"""
Quick test script for Railway deployed API
"""
import requests
import json
import sys

def test_railway_api(base_url):
    """Test the deployed API on Railway."""
    
    print(f"🧪 Testing API at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Health Check: PASSED")
            print(f"   Status: {result.get('status')}")
            print(f"   Supabase: {result.get('supabase_cache')}")
        else:
            print(f"❌ Health Check: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
        return False
    
    print()
    
    # Test 2: Generate API Key
    try:
        data = {
            "name": "Railway Test Key",
            "description": "Test key for Railway deployment"
        }
        response = requests.post(f"{base_url}/generate-api-key", json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            api_key = result.get("api_key")
            print("✅ API Key Generation: PASSED")
            print(f"   Key: {api_key[:30]}...")
        else:
            print(f"❌ API Key Generation: FAILED ({response.status_code})")
            return False
    except Exception as e:
        print(f"❌ API Key Generation: ERROR - {e}")
        return False
    
    print()
    
    # Test 3: Meal Recommendation (if we have data)
    try:
        meal_data = {
            "user_profile": {
                "age": 25,
                "gender": "male",
                "activity_level": "moderately_active",
                "diet_goal": "muscle_gain",
                "preferred_cuisines": "Persian",
                "preferred_ingredients": "Chicken",
                "allergies": "None"
            },
            "meal_type": "lunch",
            "api_key": api_key
        }
        
        response = requests.post(f"{base_url}/meal-recommendation", json=meal_data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print("✅ Meal Recommendation: PASSED")
            print(f"   Suggestions: {len(result.get('suggestions', []))}")
        elif response.status_code == 503:
            print("⚠️  Meal Recommendation: No database (expected)")
        else:
            print(f"❌ Meal Recommendation: FAILED ({response.status_code})")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Meal Recommendation: ERROR - {e}")
    
    print()
    
    # Test 4: API Documentation
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API Documentation: ACCESSIBLE")
            print(f"   URL: {base_url}/docs")
        else:
            print(f"❌ API Documentation: FAILED ({response.status_code})")
    except Exception as e:
        print(f"❌ API Documentation: ERROR - {e}")
    
    print()
    print("🎯 Test Summary:")
    print(f"   API Base URL: {base_url}")
    print(f"   API Key: {api_key}")
    print(f"   Documentation: {base_url}/docs")
    print(f"   Alternative docs: {base_url}/redoc")
    
    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_railway_api.py <API_BASE_URL>")
        print("Example: python test_railway_api.py https://myapp-production.up.railway.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    test_railway_api(base_url)
