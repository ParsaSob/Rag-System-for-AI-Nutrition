# 🍽️ Smart Nutrition API Documentation

## Overview

The Smart Nutrition API provides AI-powered meal recommendations and nutrition information based on your food database. It uses RAG (Retrieval-Augmented Generation) technology to give personalized suggestions.

## Base URL
```
http://your-domain.com:8000
```

## Authentication

All endpoints require an API key. Include it in your request body:
```json
{
  "api_key": "your-api-key-here"
}
```

### Demo API Keys
- `demo-key-12345` (1,000 requests limit)
- `nutrition-api-67890` (5,000 requests limit)

## Endpoints

### 1. Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "services": {
    "document_processor": true,
    "chain_service": true,
    "supabase": true
  }
}
```

### 2. Meal Recommendation
```http
POST /api/v1/meal-recommendation
```

**Request Body:**
```json
{
  "user_profile": {
    "age": 25,
    "gender": "female",
    "activity_level": "moderately_active",
    "diet_goal": "weight_loss",
    "preferred_diet": "Mediterranean",
    "preferences": "Low carb, high protein",
    "preferred_cuisines": "Persian, Mediterranean",
    "dispreferred_cuisines": "Fast food",
    "preferred_ingredients": "Chicken, vegetables",
    "dispreferred_ingredients": "Sugar, processed foods",
    "allergies": "None",
    "medical_conditions": "None"
  },
  "meal_type": "lunch",
  "api_key": "demo-key-12345"
}
```

**Field Descriptions:**

| Field | Type | Required | Options |
|-------|------|----------|---------|
| age | integer | Yes | 1-120 |
| gender | string | Yes | male, female |
| activity_level | string | Yes | sedentary, lightly_active, moderately_active, very_active |
| diet_goal | string | Yes | weight_loss, weight_gain, muscle_gain, maintenance |
| meal_type | string | Yes | breakfast, lunch, dinner, snack |
| preferred_diet | string | No | Any diet type (vegan, keto, etc.) |
| preferences | string | No | General food preferences |
| preferred_cuisines | string | No | Comma-separated cuisines |
| dispreferred_cuisines | string | No | Cuisines to avoid |
| preferred_ingredients | string | No | Ingredients to include |
| dispreferred_ingredients | string | No | Ingredients to avoid |
| allergies | string | No | Food allergies |
| medical_conditions | string | No | Health conditions |

**Response:**
```json
{
  "suggestions": [
    {
      "mealTitle": "Mediterranean Grilled Chicken Bowl",
      "description": "High-protein, low-carb meal perfect for weight loss",
      "ingredients": [
        {
          "name": "Chicken Breast",
          "amount": 150,
          "unit": "g",
          "calories": 165,
          "protein": 31,
          "carbs": 0,
          "fat": 3.6,
          "macrosString": "165 cal, 31g protein, 0g carbs, 3.6g fat"
        }
      ],
      "totalCalories": 350,
      "totalProtein": 45,
      "totalCarbs": 15,
      "totalFat": 12,
      "nutritionalNotes": "Balanced macros supporting weight loss goals"
    }
  ],
  "status": "success"
}
```

### 3. Nutrition Query
```http
POST /api/v1/nutrition-query
```

**Request Body:**
```json
{
  "question": "How many calories are in 100g of chicken breast?",
  "api_key": "demo-key-12345"
}
```

**Response:**
```json
{
  "answer": "According to the food database, 100g of chicken breast contains approximately 165 calories, with 31g protein, 0g carbohydrates, and 3.6g fat.",
  "sources": ["Food Database: data_base"],
  "status": "success"
}
```

### 4. API Key Information
```http
GET /api/v1/api-keys/info?api_key=your-key
```

**Response:**
```json
{
  "name": "Demo API Key",
  "requests_used": 45,
  "requests_limit": 1000,
  "usage_percentage": 4.5
}
```

## Rate Limits

- **60 requests per minute** per API key
- **Daily limits** based on your API key tier

## Error Responses

All errors follow this format:
```json
{
  "status": "error",
  "message": "Error description",
  "code": 400
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| 401 | Invalid or inactive API key |
| 429 | Rate limit exceeded |
| 503 | Service unavailable (no database) |
| 500 | Internal server error |

## Frontend Integration Examples

### JavaScript/React
```javascript
const API_BASE_URL = 'http://your-domain.com:8000';
const API_KEY = 'your-api-key';

async function getMealRecommendation(userProfile, mealType) {
  const response = await fetch(`${API_BASE_URL}/api/v1/meal-recommendation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_profile: userProfile,
      meal_type: mealType,
      api_key: API_KEY
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return await response.json();
}
```

### Python
```python
import requests

API_BASE_URL = 'http://your-domain.com:8000'
API_KEY = 'your-api-key'

def get_meal_recommendation(user_profile, meal_type):
    url = f"{API_BASE_URL}/api/v1/meal-recommendation"
    payload = {
        "user_profile": user_profile,
        "meal_type": meal_type,
        "api_key": API_KEY
    }
    
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()
```

### PHP
```php
<?php
$api_base_url = 'http://your-domain.com:8000';
$api_key = 'your-api-key';

function getMealRecommendation($userProfile, $mealType) {
    global $api_base_url, $api_key;
    
    $url = $api_base_url . '/api/v1/meal-recommendation';
    $data = [
        'user_profile' => $userProfile,
        'meal_type' => $mealType,
        'api_key' => $api_key
    ];
    
    $options = [
        'http' => [
            'header' => "Content-type: application/json\r\n",
            'method' => 'POST',
            'content' => json_encode($data)
        ]
    ];
    
    $context = stream_context_create($options);
    $result = file_get_contents($url, false, $context);
    
    return json_decode($result, true);
}
?>
```

## Deployment

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export SUPABASE_URL="your-supabase-url"  # Optional
export SUPABASE_ANON_KEY="your-supabase-key"  # Optional

# Start API server
python start_api.py
```

### Production Deployment
```bash
# Start with production settings
python start_api.py --host 0.0.0.0 --port 8000 --no-reload
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "start_api.py", "--host", "0.0.0.0", "--port", "8000", "--no-reload"]
```

## Best Practices

1. **Store API keys securely** - Never expose them in frontend code
2. **Handle rate limits** - Implement retry logic with exponential backoff
3. **Cache responses** - Cache meal recommendations to reduce API calls
4. **Validate inputs** - Check user profile data before sending
5. **Handle errors gracefully** - Always check response status

## Support

- **Documentation**: `/docs` endpoint for interactive API docs
- **Alternative docs**: `/redoc` endpoint
- **Health monitoring**: `/health` endpoint

## Changelog

### v1.0.0
- Initial release
- Meal recommendation endpoint
- Nutrition query endpoint
- API key authentication
- Rate limiting
- Comprehensive documentation

