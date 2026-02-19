# 📋 CHANGELOG — Goat Farm Management System

## v5.7-IMPROVED (2026-02-18)

### 🐛 Bug Fixes

**farm/api.py**
- FIX: `PATCH /api/goats/{id}/` — `if value is not None` check galat tha; notes ya mother_id jaisi fields intentionally None/blank ho sakti hain. Check hataya — `exclude_unset=True` hi kaafi hai.
- FIX: `POST /api/milk/` — `unique_together (goat, date, session)` violation par Django cryptic IntegrityError deta tha. Ab pehle check hota hai aur 409 status ke saath clear Hindi+English error message deta hai.
- FIX: `GET /api/expenses/` — koi ordering nahi thi, response random order mein aata tha. Ab `-date` (latest first) ordering add ki.
- FIX: `GET /api/stats/dashboard/` — 5 alag `Goat.objects.*().count()` queries thi → ek hi `aggregate()` mein Case/When se sab counts. DB round-trips 5 se 1 hua.

**farm/models.py**
- FIX: `BreedingRecord.clean()` — `self.mother.gender` / `self.father.gender` access se implicit DB queries hoti thi (related object lazy load). Ab `values_list('gender', flat=True)` se sirf gender field fetch hota hai — efficient.
- FIX: `FeedConsumption.save()` — edit pe inventory update nahi hoti thi; sirf naye records pe deduction tha. Ab edit pe purana quantity fetch karke difference adjust hota hai. Zyada consume karne par `ValidationError` bhi uthti hai.
- FIX: `VaccinationSchedule.save()` — `completed=True` karne par `completion_date` manually set karna padta tha, bhool jane par blank rahti. Ab auto `date.today()` set hota hai. `completed=False` karne par `completion_date` clear ho jaati hai.
- FIX: `Credit.save()` — status manually set karna padta tha aur out-of-sync ho jaata tha. Ab `paid_amount` ke basis par `Pending/Partial/Paid/Overdue` auto-set hota hai. `Written_Off` manual rahega.

---

## v5.6-FIXED (2026-02-18)

### 🐛 Bug Fixes

**API Schema Fixes (farm/api.py)**
- FIX: `GoatIn` schema mein `notes` field missing tha → add kiya.
- FIX: `GoatOut` schema mein `notes` field missing tha → add kiya.
- FIX: `PATCH /api/goats/{id}/` endpoint mein `GoatIn` use ho raha tha. Naya `GoatPatch` schema banaya jisme sab fields `Optional` hain.
- FIX: `POST /api/breeding/` mein `expected_delivery_date=None` directly `.objects.create()` mein ja raha tha. Ab None values filter ho jaati hain.

**Security Fixes (farm/backup_views.py)**
- FIX: `restore_json_backup` par `@csrf_exempt` tha — hataya. Frontend Django ka `X-CSRFToken` cookie header bheje.
- FIX: Restore endpoint par koi staff/admin check nahi tha. Ab `is_staff` check add kiya.

**Security Fix (farm/weather_service.py)**
- FIX: `WEATHER_API_KEY` ka fallback ek real hardcoded API key tha. Ab empty string fallback hai jo demo mode activate karta hai.

**Model Fix (farm/models.py)**
- FIX: `FeedConsumption.save()` mein negative inventory possible tha. Ab save se pehle check hota hai.

---

## v5.5-IMPROVED (2026-02-18)

### 🎨 UI & UX Improvements

- Bilingual toggle, Dark/Light theme, improved base template, dashboard live stats, Indian goat breeds added, Goat `notes` field added.

---

## v5.5 (Previous)

- Fixed CORS, JWT → Session Auth, pagination, N+1 fixes, PATCH endpoints, Swagger UI.

---

## v6.0-BATCH1 (2026-02-18) — New Feature Modules

### 🆕 New Python Modules Added

**farm/analytics.py** — Advanced Analytics Engine
- `get_monthly_pl(year)` — Monthly P&L data for Chart.js
- `get_yearly_pl_summary(years)` — Multi-year comparison
- `get_breed_performance()` — Breed-wise milk, weight, health comparison
- `get_top_goats_by_roi(limit)` — ROI per goat (revenue vs investment)
- `get_herd_growth(months)` — Births, deaths, sales trend
- `get_top_performers(category, limit)` — Top goats by milk/weight/health
- `get_feed_efficiency()` — Feed cost per liter of milk

**farm/invoice.py** — PDF Invoice Generator (requires: pip install reportlab)
- `generate_sale_invoice_pdf(sale)` — Professional PDF with GST
- Auto GST rates: Live Goat 0%, Milk 5%, Services 18%
- Amount in words (Hindi-style: Lakh, Crore)
- Farm letterhead (configurable via settings.py or .env)
- Auto invoice numbering: INV-2026-001, 002...

**farm/ai_engine.py** — AI-Powered Suggestion Engine
- `suggest_breeding_pairs(limit)` — Best mother-father pairs (score-based)
- `detect_sick_goats()` — Early warning: weight loss, treatments, milk drop
- `suggest_sell_goats()` — Optimal selling time (age + market price + weight)
- `get_feed_optimization()` — Daily feed requirement per goat category
- `forecast_revenue(months_ahead)` — Simple trend-based revenue forecast

**farm/qr_utils.py** — QR Code Generator (requires: pip install qrcode[pil])
- `generate_qr_code(tag, base_url)` — Per-goat QR code PNG
- `generate_goat_tag_image(goat, base_url)` — Ear tag style image
- `generate_batch_qr_pdf(goats, base_url)` — All goats QR codes in one PDF

**farm/notifications.py** — WhatsApp Alert System (requires: pip install twilio)
- `send_vaccination_reminders(days_ahead)` — Upcoming vaccination alerts
- `send_delivery_reminders(days_ahead)` — Expected delivery warnings
- `send_overdue_payment_reminders()` — Customer payment reminders
- `send_low_feed_alerts(threshold_days)` — Low stock warnings
- `send_daily_summary()` — Morning farm summary

### 🔌 New API Endpoints Added (farm/api.py)

Analytics (7 endpoints):
- GET /api/analytics/pl-chart/?year=2026
- GET /api/analytics/yearly-summary/?years=3
- GET /api/analytics/breed-performance/
- GET /api/analytics/top-goats/?category=milk&limit=10
- GET /api/analytics/roi/?limit=10
- GET /api/analytics/herd-growth/?months=12
- GET /api/analytics/feed-efficiency/
- GET /api/analytics/summary/

AI Engine (5 endpoints):
- GET /api/ai/breeding-suggestions/?limit=5
- GET /api/ai/sick-detection/
- GET /api/ai/sell-suggestions/
- GET /api/ai/feed-optimization/
- GET /api/ai/revenue-forecast/?months_ahead=3

Invoice (1 endpoint):
- GET /api/invoices/{sale_id}/pdf/

QR Code (2 endpoints):
- GET /api/goats/{id}/qr-code/
- GET /api/goats/qr-batch-pdf/

Notifications (4 endpoints):
- POST /api/notifications/send-vaccination-reminders/
- POST /api/notifications/send-delivery-reminders/
- POST /api/notifications/send-payment-reminders/
- GET /api/notifications/daily-summary/

### 📦 New Dependencies (requirements.txt)
- reportlab>=4.0.0 (Invoice PDF)
- qrcode[pil]>=7.4.2 (QR Codes)
- twilio>=8.0.0 (WhatsApp)
- numpy>=1.24.0 (AI calculations)

### ⚙️ New Settings (.env.example)
- FARM_NAME, FARM_ADDRESS, FARM_PHONE, FARM_EMAIL, FARM_GST
- FARM_BANK_NAME, FARM_ACCOUNT_NO, FARM_IFSC
- TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM
- FARM_OWNER_PHONE

### 📋 Roadmap Document
- Feature_Roadmap_v6.docx — Complete 12-module, 3-batch implementation plan
- 60+ features documented with priorities and timelines
