# 🐐 Goat Farm Management System v5.5 — Django Ninja

## द्विभाषी फार्म प्रबंधन सिस्टम | Bilingual Farm Management System

एक **production-ready** Django Ninja REST API-based goat farm management system — हिंदी + English bilingual interface के साथ।  
A **production-ready** goat farm management system with full Hindi + English bilingual support.

---

## ✨ Improvements in This Version (v5.5 Improved)

### 🎨 UI Improvements
- **Bilingual Interface** — Click `हिं / EN` button to instantly switch between Hindi and English
- **Dark / Light Theme** — Click 🌙/☀️ to toggle themes, preference saved in localStorage
- **Modern Sidebar** — Clean navigation with all sections organized
- **CSS Variable System** — Consistent design tokens across all pages
- **Indian Goat Breeds Added** — Sirohi, Barbari, Jamunapari, Beetal, Osmanabadi, Marwari, etc.

### 🏗️ Code Improvements
- **Unified base.html** — All templates now extend `farm/base.html` with proper CSS variables
- **Dashboard with Real Data** — Dashboard now passes proper context from database
- **Notes field added** to Goat model for additional information
- **helper methods** added: `is_male()`, `is_female()` on Goat model

### 🌐 API (Existing — unchanged)
- 100+ REST endpoints via Django Ninja
- Session-based authentication (no JWT needed)
- Pagination on all list endpoints
- Full CRUD with PATCH support

---

## 🚀 Quick Start (5 मिनट में / in 5 minutes)

### Step 1: Dependencies Install करें
```bash
cd goat_farm
pip install -r requirements.txt
```

### Step 2: Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 3: Admin User बनाएं
```bash
python manage.py createsuperuser
```

### Step 4: Server चलाएं
```bash
python manage.py runserver
```

### Step 5: Browser में खोलें
| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000/ | Dashboard (login required) |
| http://127.0.0.1:8000/goats/ | Goat management |
| http://127.0.0.1:8000/health/ | Health records |
| http://127.0.0.1:8000/milk/ | Milk production |
| http://127.0.0.1:8000/sales/ | Sales management |
| http://127.0.0.1:8000/expenses/ | Expenses |
| http://127.0.0.1:8000/api/docs/ | Swagger API UI |
| http://127.0.0.1:8000/admin/ | Django Admin |

---

## 📊 Features

✅ **30+ Database Models** — Complete farm management  
✅ **100+ REST API Endpoints** — Mobile apps, desktop clients  
✅ **Bilingual Interface** — हिंदी + English, switch instantly  
✅ **Dark / Light Theme** — User preference saved  
✅ **Indian Goat Breeds** — Sirohi, Barbari, Jamunapari, Beetal, etc.  
✅ **Dashboard with Live Data** — Real statistics from database  
✅ **Excel Import/Export** — Bulk data operations  
✅ **JSON/ZIP Backup** — Complete data backup & restore  
✅ **Weather Integration** — Farm weather tracking  
✅ **Responsive Design** — Mobile, tablet, desktop  

---

## 🇮🇳 Supported Indian Goat Breeds (भारतीय नस्लें)

| नस्ल / Breed | Region / क्षेत्र |
|---|---|
| Sirohi (सिरोही) | Rajasthan |
| Barbari (बरबरी) | UP, Rajasthan |
| Jamunapari (जमुनापारी) | UP, MP |
| Beetal (बीटल) | Punjab, Haryana |
| Osmanabadi (उस्मानाबादी) | Maharashtra |
| Marwari (मारवाड़ी) | Rajasthan |
| Kutchi (कच्छी) | Gujarat |
| Zalawadi (झालावाड़ी) | Gujarat |

---

## 🔧 Tech Stack

- **Backend:** Django 5.x + Django Ninja (REST API)
- **Database:** SQLite (development) / PostgreSQL (production)
- **Frontend:** Vanilla HTML/CSS/JS — no frontend framework needed
- **Auth:** Django Session Authentication
- **Cache:** File-based cache (Django built-in)
- **Excel:** openpyxl

---

## 📄 Environment Variables (.env)

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com
WEATHER_API_KEY=your-openweathermap-key
```

---

## 📜 License

Open Source · Free to Use · © 2026

🐐 **Jai Goat Farm!** 🐐
