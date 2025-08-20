# 🚀 Smart Nutrition API - راهنمای استقرار

## 📋 مروری کلی

این API یک سیستم RAG کامل برای تغذیه و برنامه‌ریزی وعده‌های غذایی است که شامل:
- 🔐 احراز هویت API Key
- 🍽️ پیشنهاد وعده غذایی شخصی‌سازی شده
- 🥗 پاسخ‌دهی به سوالات تغذیه‌ای
- 💾 کش هوشمند با Supabase
- 📊 پردازش دیتابیس غذایی (CSV/Excel/PDF)

## 🛠️ نصب و راه‌اندازی

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2. تنظیم متغیرهای محیط
```bash
# کلیدهای API
export OPENAI_API_KEY="sk-your-openai-key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_ANON_KEY="your-supabase-key"

# پورت سرور (اختیاری)
export PORT=8000
```

### 3. آماده‌سازی دیتابیس غذایی
- فایل‌های CSV، Excel یا PDF خود را در پوشه `data/` قرار دهید
- دیتابیس باید شامل نام غذا، کالری، پروتئین، کربوهیدرات و چربی باشد

### 4. اجرای سرور
```bash
# اجرای مستقیم
python api_server.py

# یا با uvicorn
uvicorn api_server:app --host 0.0.0.0 --port 8000 --reload
```

## 🔑 مدیریت API Key

### تولید کلید جدید
```bash
curl -X POST "http://localhost:8000/generate-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Website",
    "description": "API key for main website"
  }'
```

### لیست کلیدها
```bash
curl -X GET "http://localhost:8000/api-keys" \
  -H "X-API-Key: your-api-key"
```

## 📡 API Endpoints

### 1. پیشنهاد وعده غذایی
```http
POST /meal-recommendation
Content-Type: application/json

{
  "user_profile": {
    "age": 30,
    "gender": "male",
    "activity_level": "moderately_active",
    "diet_goal": "muscle_gain",
    "preferred_diet": "Mediterranean",
    "preferences": "High protein",
    "preferred_cuisines": "Persian, Italian",
    "dispreferred_cuisines": "Fast food",
    "preferred_ingredients": "Chicken, vegetables",
    "dispreferred_ingredients": "Processed foods",
    "allergies": "None",
    "medical_conditions": "None"
  },
  "meal_type": "lunch",
  "api_key": "sk-nutrition-..."
}
```

### 2. پرسش تغذیه‌ای
```http
POST /nutrition-query
Content-Type: application/json

{
  "question": "How many calories are in 100g chicken breast?",
  "api_key": "sk-nutrition-..."
}
```

### 3. لیست اسناد
```http
GET /documents
X-API-Key: sk-nutrition-...
```

### 4. بررسی سلامت
```http
GET /health
```

## 🌐 استقرار روی Host

### استقرار ساده
```bash
# Clone repository
git clone your-repo-url
cd nutrition-api

# نصب وابستگی‌ها
pip install -r requirements.txt

# تنظیم متغیرهای محیط
export OPENAI_API_KEY="your-key"
export SUPABASE_URL="your-url"
export SUPABASE_ANON_KEY="your-key"

# اجرای سرور در پورت 80 یا 8000
python api_server.py
```

### استقرار با Docker
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api_server.py"]
```

```bash
# ساخت و اجرا
docker build -t nutrition-api .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key" \
  -e SUPABASE_URL="your-url" \
  -e SUPABASE_ANON_KEY="your-key" \
  nutrition-api
```

### استقرار روی VPS/Cloud
```bash
# نصب در سرور
sudo apt update && sudo apt install python3-pip
pip3 install -r requirements.txt

# اجرا با PM2 (برای production)
npm install -g pm2
pm2 start api_server.py --interpreter python3 --name nutrition-api

# یا با systemd service
sudo nano /etc/systemd/system/nutrition-api.service
```

## 🔗 اتصال از سایت اصلی

### JavaScript Example
```javascript
const API_BASE = 'https://your-domain.com';
const API_KEY = 'sk-nutrition-your-key';

async function getMealRecommendation(userProfile, mealType) {
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
  
  return await response.json();
}

// استفاده
const userProfile = {
  age: 25,
  gender: "female",
  activity_level: "lightly_active",
  diet_goal: "weight_loss",
  // ... سایر فیلدها
};

getMealRecommendation(userProfile, "breakfast")
  .then(result => {
    console.log('Meal suggestion:', result);
    // نمایش در UI
  });
```

### PHP Example
```php
<?php
$apiBase = 'https://your-domain.com';
$apiKey = 'sk-nutrition-your-key';

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
?>
```

## 📊 نظارت و لاگ‌ها

### مشاهده لاگ‌ها
```bash
# اگر با PM2 اجرا کرده‌اید
pm2 logs nutrition-api

# اگر مستقیم اجرا کرده‌اید
tail -f api_server.log
```

### متریک‌های مهم
- تعداد درخواست‌های API
- زمان پاسخ‌دهی
- استفاده از کش Supabase
- خطاهای API

## 🔧 تنظیمات پیشرفته

### تنظیم CORS برای دامنه خاص
```python
# در api_server.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-website.com"],  # فقط دامنه شما
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

### محدودیت Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/meal-recommendation")
@limiter.limit("10/minute")  # محدودیت 10 درخواست در دقیقه
async def get_meal_recommendation(request: Request, ...):
    # ...
```

## 🔐 امنیت

### نکات مهم امنیتی
1. **API Key**: هرگز کلید API را در کد frontend قرار ندهید
2. **HTTPS**: همیشه از HTTPS استفاده کنید
3. **CORS**: فقط دامنه‌های مجاز را اضافه کنید
4. **Rate Limiting**: محدودیت درخواست اعمال کنید
5. **Environment Variables**: کلیدها را در متغیرهای محیط ذخیره کنید

### تولید کلید امن
```python
# در auth_service.py کلیدها به صورت امن تولید می‌شوند
# هر کلید شامل: sk-nutrition-{32-char-random-string}
```

## 🆘 عیب‌یابی

### مشکلات رایج

1. **API Key Invalid**
   - بررسی کنید کلید درست وارد شده
   - کلید جدید تولید کنید

2. **No Food Database**
   - فایل‌های CSV/Excel را در `data/` قرار دهید
   - فرمت فایل‌ها را بررسی کنید

3. **Supabase Connection Failed**
   - URL و Key را چک کنید
   - جدول `document_embeddings` ساخته شده باشد

4. **OpenAI API Error**
   - کلید OpenAI را بررسی کنید
   - اعتبار حساب را چک کنید

### تست API
```bash
# تست کامل با فایل example
python api_example.py
```

## 📞 پشتیبانی

برای مشکلات فنی:
1. لاگ‌های سرور را بررسی کنید
2. endpoint `/health` را تست کنید
3. مستندات API در `/docs` را مطالعه کنید

---

🎯 **حالا API شما آماده است! سایت اصلی‌تان می‌تواند پیشنهادات غذایی شخصی‌سازی شده دریافت کند.**

