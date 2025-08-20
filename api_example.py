"""
Example usage of the Smart Nutrition API
"""
import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "sk-nutrition-your-api-key-here"  # Replace with your actual API key

def test_health():
    """Test API health."""
    response = requests.get(f"{API_BASE_URL}/health")
    print("🏥 Health Check:")
    print(json.dumps(response.json(), indent=2))
    print()

def generate_api_key():
    """Generate a new API key."""
    data = {
        "name": "Test Client",
        "description": "API key for testing"
    }
    response = requests.post(f"{API_BASE_URL}/generate-api-key", json=data)
    if response.status_code == 200:
        result = response.json()
        print("🔑 Generated API Key:")
        print(f"Key: {result['api_key']}")
        print("⚠️  Save this key! You'll need it for API requests.")
        return result['api_key']
    else:
        print("❌ Failed to generate API key")
        print(response.text)
        return None

def get_meal_recommendation(api_key):
    """Get a meal recommendation."""
    data = {
        "user_profile": {
            "age": 30,
            "gender": "male",
            "activity_level": "moderately_active",
            "diet_goal": "muscle_gain",
            "preferred_diet": "Mediterranean",
            "preferences": "High protein, low sugar",
            "preferred_cuisines": "Persian, Mediterranean",
            "dispreferred_cuisines": "Fast food",
            "preferred_ingredients": "Chicken, fish, vegetables",
            "dispreferred_ingredients": "Processed foods",
            "allergies": "None",
            "medical_conditions": "None"
        },
        "meal_type": "lunch",
        "api_key": api_key
    }
    
    response = requests.post(f"{API_BASE_URL}/meal-recommendation", json=data)
    
    print("🍽️ Meal Recommendation:")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    print()

def nutrition_query(api_key):
    """Ask a nutrition question."""
    data = {
        "question": "What are the calories and protein in chicken breast?",
        "api_key": api_key
    }
    
    response = requests.post(f"{API_BASE_URL}/nutrition-query", json=data)
    
    print("🥗 Nutrition Query:")
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result['answer']}")
        if result.get('sources'):
            print(f"Sources: {', '.join(result['sources'])}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    print()

def list_documents(api_key):
    """List available documents."""
    headers = {"X-API-Key": api_key}
    response = requests.get(f"{API_BASE_URL}/documents", headers=headers)
    
    print("📄 Available Documents:")
    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    print()

if __name__ == "__main__":
    print("🚀 Testing Smart Nutrition API")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Generate API key (uncomment if you need a new key)
    # new_key = generate_api_key()
    # if new_key:
    #     API_KEY = new_key
    
    if API_KEY and "your-api-key-here" not in API_KEY:
        # List documents
        list_documents(API_KEY)
        
        # Test nutrition query
        nutrition_query(API_KEY)
        
        # Test meal recommendation
        get_meal_recommendation(API_KEY)
    else:
        print("⚠️  Please set a valid API_KEY at the top of this file")
        print("💡 Uncomment the generate_api_key() call to create one")

