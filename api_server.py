"""
FastAPI server for nutrition and meal recommendation API
"""
from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import asyncio
import json
import os
from typing import Dict, Any, Optional
import uvicorn

from src.api_models import *
from src.auth_service import auth_service
from src.document_processor import DocumentProcessor
from src.chains import ChainService
from src.meal_prompt_template import MEAL_RECOMMENDATION_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="🍽️ Smart Nutrition API",
    description="AI-powered nutrition and meal planning API with Supabase caching",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Global services
document_processor = DocumentProcessor()
chain_service = ChainService()

def verify_api_key(api_key: str = Header(..., alias="X-API-Key")) -> str:
    """Dependency to verify API key from header."""
    if not auth_service.validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return api_key

def verify_api_key_body(api_key: str) -> str:
    """Verify API key from request body."""
    if not auth_service.validate_api_key(api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    return api_key

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "🍽️ Smart Nutrition API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "supabase_cache": document_processor.supabase_service.is_available(),
        "documents_loaded": len(document_processor.chunks) > 0
    }

@app.post("/generate-api-key", response_model=APIKeyResponse)
async def generate_api_key(request: APIKeyRequest):
    """Generate a new API key."""
    try:
        api_key = auth_service.generate_api_key(
            name=request.name,
            description=request.description
        )
        
        return APIKeyResponse(
            api_key=api_key,
            name=request.name,
            created_at=auth_service.get_key_info(api_key)["created_at"]
        )
    except Exception as e:
        logger.error(f"Error generating API key: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate API key"
        )

@app.get("/api-keys")
async def list_api_keys(api_key: str = Depends(verify_api_key)):
    """List all API keys (admin endpoint)."""
    return {
        "api_keys": auth_service.list_api_keys(),
        "total": len(auth_service.api_keys)
    }

@app.post("/meal-recommendation", response_model=MealRecommendationResponse)
async def get_meal_recommendation(request: MealRecommendationRequest):
    """Get personalized meal recommendation."""
    try:
        # Verify API key
        verify_api_key_body(request.api_key)
        
        # Get available documents
        from src.config import DOCUMENTS
        if not DOCUMENTS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No food database available. Please upload food data."
            )
        
        # Process all available documents to get food context
        all_context = []
        for doc_name in DOCUMENTS.keys():
            try:
                chunks = document_processor.get_chunks(doc_name)
                # Get top relevant chunks for meal planning
                relevant_chunks = document_processor.get_most_relevant_chunks(
                    f"ingredients food nutrition {request.meal_type.value} {request.user_profile.preferred_cuisines}",
                    doc_name,
                    top_k=10
                )
                for chunk_data in relevant_chunks:
                    all_context.append(f"From {doc_name}:\n{chunk_data['chunk']}")
            except Exception as e:
                logger.warning(f"Error processing document {doc_name}: {e}")
                continue
        
        if not all_context:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Could not load food database context"
            )
        
        # Build the meal recommendation prompt
        prompt = MEAL_RECOMMENDATION_TEMPLATE.format(
            age=request.user_profile.age,
            gender=request.user_profile.gender.value,
            activity_level=request.user_profile.activity_level.value,
            diet_goal=request.user_profile.diet_goal.value,
            preferred_diet=request.user_profile.preferred_diet or "No specific diet",
            preferences=request.user_profile.preferences or "None specified",
            preferred_cuisines=request.user_profile.preferred_cuisines or "No preference",
            dispreferred_cuisines=request.user_profile.dispreferred_cuisines or "None",
            preferred_ingredients=request.user_profile.preferred_ingredients or "No preference",
            dispreferred_ingredients=request.user_profile.dispreferred_ingredients or "None",
            allergies=request.user_profile.allergies or "None",
            medical_conditions=request.user_profile.medical_conditions or "None",
            meal_type=request.meal_type.value,
            context="\n\n".join(all_context[:20])  # Limit context size
        )
        
        # Get QA chain and generate response
        qa_chain = chain_service.get_qa_chain()
        
        try:
            response = qa_chain.run(
                context="\n\n".join(all_context[:20]),
                question=prompt
            )
            
            # Try to parse JSON response
            try:
                json_response = json.loads(response)
                return MealRecommendationResponse(**json_response)
            except json.JSONDecodeError:
                # If not valid JSON, try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_response = json.loads(json_match.group())
                    return MealRecommendationResponse(**json_response)
                else:
                    return MealRecommendationResponse(
                        suggestions=[],
                        success=False,
                        message="Could not generate valid meal recommendation. Please try again."
                    )
                    
        except Exception as e:
            logger.error(f"Error generating meal recommendation: {e}")
            return MealRecommendationResponse(
                suggestions=[],
                success=False,
                message=f"Error generating recommendation: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in meal recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/nutrition-query", response_model=NutritionQueryResponse)
async def nutrition_query(request: NutritionQueryRequest):
    """Answer nutrition questions using the food database."""
    try:
        # Verify API key
        verify_api_key_body(request.api_key)
        
        # Get available documents
        from src.config import DOCUMENTS
        if not DOCUMENTS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="No food database available"
            )
        
        # Get relevant context for the question
        all_search_results = []
        for doc_name in DOCUMENTS.keys():
            try:
                results = document_processor.get_most_relevant_chunks(
                    request.question,
                    doc_name,
                    top_k=5
                )
                for result in results:
                    result["document"] = doc_name
                all_search_results.extend(results)
            except Exception as e:
                logger.warning(f"Error searching document {doc_name}: {e}")
                continue
        
        if not all_search_results:
            return NutritionQueryResponse(
                answer="I don't have enough information in the database to answer your question.",
                success=False,
                message="No relevant information found"
            )
        
        # Sort by relevance and prepare context
        all_search_results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        context_chunks = []
        for result in all_search_results[:10]:  # Top 10 results
            context_chunks.append(f"From {result['document']}:\n{result['chunk']}")
        
        context = "\n\n".join(context_chunks)
        
        # Get QA chain and generate response
        qa_chain = chain_service.get_qa_chain()
        
        response = qa_chain.run(
            context=context,
            question=request.question
        )
        
        # Extract sources
        sources = list(set([result['document'] for result in all_search_results[:5]]))
        
        return NutritionQueryResponse(
            answer=response,
            sources=sources
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in nutrition query: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/documents")
async def list_documents(api_key: str = Depends(verify_api_key)):
    """List available food database documents."""
    from src.config import DOCUMENTS
    return {
        "documents": list(DOCUMENTS.keys()),
        "total": len(DOCUMENTS)
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            message="API request failed"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            message="An unexpected error occurred"
        ).dict()
    )

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    
    print("🚀 Starting Smart Nutrition API Server...")
    print(f"📖 API Documentation: http://localhost:{port}/docs")
    print(f"🔄 Alternative docs: http://localhost:{port}/redoc")
    
    # Check if running in production (Railway sets RAILWAY_ENVIRONMENT)
    is_production = os.getenv("RAILWAY_ENVIRONMENT") is not None
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=not is_production,  # No reload in production
        log_level="info"
    )