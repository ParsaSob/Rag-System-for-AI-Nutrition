"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    MODERATELY_ACTIVE = "moderately_active"
    VERY_ACTIVE = "very_active"

class DietGoal(str, Enum):
    WEIGHT_LOSS = "weight_loss"
    WEIGHT_GAIN = "weight_gain"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"

class MealType(str, Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"

class UserProfile(BaseModel):
    age: int = Field(..., ge=1, le=120, description="User's age")
    gender: Gender = Field(..., description="User's gender")
    activity_level: ActivityLevel = Field(..., description="Activity level")
    diet_goal: DietGoal = Field(..., description="Diet goal")
    preferred_diet: Optional[str] = Field(None, description="e.g., vegan, keto, mediterranean")
    preferences: Optional[str] = Field(None, description="General dietary preferences")
    preferred_cuisines: Optional[str] = Field(None, description="Preferred cuisines")
    dispreferred_cuisines: Optional[str] = Field(None, description="Cuisines to avoid")
    preferred_ingredients: Optional[str] = Field(None, description="Preferred ingredients")
    dispreferred_ingredients: Optional[str] = Field(None, description="Ingredients to avoid")
    allergies: Optional[str] = Field(None, description="Food allergies")
    medical_conditions: Optional[str] = Field(None, description="Relevant medical conditions")

class MealRecommendationRequest(BaseModel):
    user_profile: UserProfile
    meal_type: MealType
    api_key: str = Field(..., description="API key for authentication")

class NutritionQueryRequest(BaseModel):
    question: str = Field(..., min_length=1, description="Nutrition question")
    api_key: str = Field(..., description="API key for authentication")

class Ingredient(BaseModel):
    name: str
    amount: float
    unit: str
    calories: float
    protein: float
    carbs: float
    fat: float
    macrosString: str

class MealSuggestion(BaseModel):
    mealTitle: str
    description: str
    ingredients: List[Ingredient]
    totalCalories: float
    totalProtein: float
    totalCarbs: float
    totalFat: float
    nutritionalNotes: Optional[str] = None

class MealRecommendationResponse(BaseModel):
    suggestions: List[MealSuggestion]
    success: bool = True
    message: Optional[str] = None

class NutritionQueryResponse(BaseModel):
    answer: str
    success: bool = True
    message: Optional[str] = None
    sources: Optional[List[str]] = None

class APIKeyRequest(BaseModel):
    name: str = Field(..., description="Name for the API key")
    description: Optional[str] = Field(None, description="Description of API key usage")

class APIKeyResponse(BaseModel):
    api_key: str
    name: str
    created_at: str
    success: bool = True

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str