"""
API Usage Examples for Smart Nutrition API
"""
import requests
import json

# API Configuration
API_BASE_URL = "http://localhost:8000"  # Change to your deployed URL
API_KEY = "demo-key-12345"  # Use your actual API key

def test_meal_recommendation():
    """Example: Get meal recommendation"""
    
    url = f"{API_BASE_URL}/api/v1/meal-recommendation"
    
    payload = {
        "user_profile": {
            "age": 25,
            "gender": "female",
            "activity_level": "moderately_active",
            "diet_goal": "weight_loss",
            "preferred_diet": "Mediterranean",
            "preferences": "Low carb, high protein",
            "preferred_cuisines": "Persian, Mediterranean",
            "dispreferred_cuisines": "Fast food",
            "preferred_ingredients": "Chicken, vegetables, olive oil",
            "dispreferred_ingredients": "Sugar, processed foods",
            "allergies": "None",
            "medical_conditions": "None"
        },
        "meal_type": "lunch",
        "api_key": API_KEY
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("🍽️ Meal Recommendation:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

def test_nutrition_query():
    """Example: Ask nutrition question"""
    
    url = f"{API_BASE_URL}/api/v1/nutrition-query"
    
    payload = {
        "question": "How many calories are in 100g of chicken breast?",
        "api_key": API_KEY
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        print("🔍 Nutrition Query Result:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

def test_api_key_info():
    """Example: Check API key usage"""
    
    url = f"{API_BASE_URL}/api/v1/api-keys/info"
    
    params = {
        "api_key": API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        print("🔑 API Key Info:")
        print(json.dumps(result, indent=2))
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")

def test_health_check():
    """Example: Check API health"""
    
    url = f"{API_BASE_URL}/health"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        print("🏥 Health Check:")
        print(json.dumps(result, indent=2))
        
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")

# JavaScript/Frontend Example
def generate_js_example():
    """Generate JavaScript example for frontend integration"""
    
    js_code = '''
// JavaScript Example for Smart Nutrition API

const API_BASE_URL = 'http://localhost:8000';  // Your API URL
const API_KEY = 'demo-key-12345';  // Your API key

// Function to get meal recommendation
async function getMealRecommendation(userProfile, mealType) {
    const url = `${API_BASE_URL}/api/v1/meal-recommendation`;
    
    const payload = {
        user_profile: userProfile,
        meal_type: mealType,
        api_key: API_KEY
    };
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error getting meal recommendation:', error);
        throw error;
    }
}

// Example usage
const userProfile = {
    age: 30,
    gender: 'male',
    activity_level: 'moderately_active',
    diet_goal: 'muscle_gain',
    preferred_diet: 'Mediterranean',
    preferences: 'High protein, moderate carbs',
    preferred_cuisines: 'Persian, Italian',
    dispreferred_cuisines: 'Fast food',
    preferred_ingredients: 'Chicken, fish, vegetables',
    dispreferred_ingredients: 'Sugar, processed foods',
    allergies: 'None',
    medical_conditions: 'None'
};

// Get lunch recommendation
getMealRecommendation(userProfile, 'lunch')
    .then(result => {
        console.log('Meal recommendation:', result);
        // Display result in your UI
        displayMealRecommendation(result);
    })
    .catch(error => {
        console.error('Failed to get meal recommendation:', error);
    });

// Function to display meal recommendation in UI
function displayMealRecommendation(result) {
    if (result.suggestions && result.suggestions.length > 0) {
        const meal = result.suggestions[0];
        
        // Create HTML for meal display
        const mealHTML = `
            <div class="meal-recommendation">
                <h3>${meal.mealTitle}</h3>
                <p>${meal.description}</p>
                
                <div class="nutrition-summary">
                    <span>Calories: ${meal.totalCalories}</span>
                    <span>Protein: ${meal.totalProtein}g</span>
                    <span>Carbs: ${meal.totalCarbs}g</span>
                    <span>Fat: ${meal.totalFat}g</span>
                </div>
                
                <h4>Ingredients:</h4>
                <ul class="ingredients-list">
                    ${meal.ingredients.map(ingredient => `
                        <li>
                            ${ingredient.name} - ${ingredient.amount}${ingredient.unit}
                            <span class="macros">(${ingredient.macrosString})</span>
                        </li>
                    `).join('')}
                </ul>
                
                ${meal.nutritionalNotes ? `<p class="notes">${meal.nutritionalNotes}</p>` : ''}
            </div>
        `;
        
        // Insert into your page
        document.getElementById('meal-container').innerHTML = mealHTML;
    }
}
'''
    
    with open('frontend_example.js', 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print("📄 JavaScript example saved to 'frontend_example.js'")

if __name__ == "__main__":
    print("🧪 Testing Smart Nutrition API...")
    print("=" * 50)
    
    # Test all endpoints
    test_health_check()
    print("\\n" + "=" * 50)
    
    test_api_key_info()
    print("\\n" + "=" * 50)
    
    test_nutrition_query()
    print("\\n" + "=" * 50)
    
    test_meal_recommendation()
    print("\\n" + "=" * 50)
    
    generate_js_example()
    print("\\n✅ All tests completed!")

