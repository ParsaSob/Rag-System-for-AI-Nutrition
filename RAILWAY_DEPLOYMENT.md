# 🚅 استقرار API روی Railway

## 📋 مراحل Deploy

### 1. آماده‌سازی پروژه
```bash
# مطمئن شوید تمام فایل‌ها آماده است:
# ✅ api_server.py
# ✅ requirements.txt  
# ✅ railway.json
# ✅ Procfile
# ✅ src/ directory با تمام فایل‌ها
```

### 2. ایجاد حساب Railway
- به [railway.app](https://railway.app) بروید
- با GitHub وارد شوید
- پروژه جدید ایجاد کنید

### 3. اتصال Repository
```bash
# اگر هنوز Git repo ندارید:
git init
git add .
git commit -m "Initial commit: Smart Nutrition API"

# Push به GitHub
git remote add origin https://github.com/username/nutrition-api.git
git push -u origin main
```

### 4. Deploy در Railway
1. **New Project** → **Deploy from GitHub repo**
2. Repository خود را انتخاب کنید
3. Railway خودکار detect می‌کند و deploy می‌کند

### 5. تنظیم Environment Variables
در Railway Dashboard → Settings → Environment:

```env
OPENAI_API_KEY=sk-your-openai-key-here
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
PORT=8000
```

## 🔗 دسترسی به API

بعد از deploy موفق:

### URL API شما:
```
https://your-app-name-production.up.railway.app
```

### Test Endpoints:
```bash
# Health Check
curl https://your-app-name-production.up.railway.app/health

# API Documentation
https://your-app-name-production.up.railway.app/docs
```

## 📱 استفاده از سایت اصلی

### JavaScript Example:
```javascript
const API_BASE = 'https://your-app-name-production.up.railway.app';
const API_KEY = 'sk-nutrition-your-api-key';

async function getMealRecommendation(userProfile, mealType) {
  try {
    const response = await fetch(`${API_BASE}/meal-recommendation`, {
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
    
    const result = await response.json();
    return result;
  } catch (error) {
    console.error('API Error:', error);
    return null;
  }
}

// استفاده
const userProfile = {
  age: 25,
  gender: "male",
  activity_level: "moderately_active",
  diet_goal: "muscle_gain",
  preferred_cuisines: "Persian",
  preferred_ingredients: "Chicken",
  allergies: "None"
};

getMealRecommendation(userProfile, "lunch")
  .then(result => {
    if (result && result.success) {
      console.log('Meal suggestions:', result.suggestions);
      // نمایش در UI
    }
  });
```

### PHP Example:
```php
<?php
$apiBase = 'https://your-app-name-production.up.railway.app';
$apiKey = 'sk-nutrition-your-api-key';

function getMealRecommendation($userProfile, $mealType) {
    global $apiBase, $apiKey;
    
    $data = [
        'user_profile' => $userProfile,
        'meal_type' => $mealType,
        'api_key' => $apiKey
    ];
    
    $options = [
        'http' => [
            'header' => "Content-type: application/json\r\n",
            'method' => 'POST',
            'content' => json_encode($data)
        ]
    ];
    
    $context = stream_context_create($options);
    $result = file_get_contents($apiBase . '/meal-recommendation', false, $context);
    
    return json_decode($result, true);
}

// استفاده
$userProfile = [
    'age' => 30,
    'gender' => 'female',
    'activity_level' => 'lightly_active',
    'diet_goal' => 'weight_loss',
    'preferred_cuisines' => 'Persian',
    'allergies' => 'None'
];

$result = getMealRecommendation($userProfile, 'dinner');
if ($result && $result['success']) {
    echo json_encode($result['suggestions']);
}
?>
```

## 🔧 تنظیمات Production

### 1. Domain سفارشی (اختیاری)
- در Railway Settings → Custom Domain
- دامنه خود را اضافه کنید

### 2. CORS Configuration
```python
# در api_server.py برای production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-website.com"],  # دامنه سایت شما
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting (اختیاری)
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/meal-recommendation")
@limiter.limit("10/minute")  # محدودیت درخواست
async def get_meal_recommendation(...):
    # ...
```

## 📊 مانیتورینگ

### Railway Metrics
- CPU Usage
- Memory Usage  
- Request Count
- Response Time

### Custom Logging
```python
import logging

# در api_server.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 🔐 امنیت Production

### 1. API Keys Management
```python
# تولید کلیدهای مجزا برای هر کلاینت
POST /generate-api-key
{
  "name": "Main Website",
  "description": "API key for main website production"
}
```

### 2. HTTPS
Railway خودکار SSL certificate ارائه می‌دهد

### 3. Environment Variables
هرگز secrets را در کد قرار ندهید - فقط در Railway Environment Variables

## 🚨 Troubleshooting

### Build Errors:
```bash
# بررسی لاگ‌های Railway در Dashboard
# مطمئن شوید requirements.txt کامل است
```

### Runtime Errors:
```bash
# بررسی logs در Railway Dashboard
# تست local با همان environment variables
```

### API Not Responding:
```bash
# بررسی health endpoint
curl https://your-app.railway.app/health

# بررسی Railway metrics
```

## 💰 هزینه

### Railway Free Tier:
- $5 اعتبار ماهانه
- مناسب برای تست و پروژه‌های کوچک

### Upgrade:
- $20/ماه Pro plan
- منابع بیشتر و پشتیبانی

## 🎯 نتیجه

بعد از deploy موفق روی Railway:

✅ **API در دسترس جهانی**  
✅ **SSL Certificate خودکار**  
✅ **Auto-scaling**  
✅ **CI/CD خودکار**  
✅ **Monitoring داخلی**  

**URL نهایی شما:**
```
https://your-project-name-production.up.railway.app
```

این URL را در سایت اصلی‌تان برای دریافت پیشنهادات غذایی استفاده کنید! 🚀
