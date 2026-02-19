"""
Goat Farm Management API - v5.5 (Code Quality & Feature Improvements)
Fixes applied:
  - FIX #12: JWT removed → Django Session Auth use kiya
  - FIX #3: N+1 query problem → aggregate(Sum()) use kiya
  - FIX #4: Weather API key env variable se lo
  - FIX #6: Wildcard import hataya
  - FIX #7: Separate Input/Output schemas
  - FIX #8: update mein None values properly handle kiye
  - FIX #9: Pagination sab list endpoints par lagayi
  - FIX #10: Missing DELETE endpoints add kiye
  - FIX #11: select_related/prefetch_related for performance
  - FIX #13: Sab inline function imports → top-level imports (PEP 8)
  - FIX #14: __import__('datetime') hack → proper datetime import
  - FIX #15: Mid-file 'from .models import Notification' → top-level
  - FIX #16: GoatOut.created_at → proper datetime type (no manual .isoformat())
  - FIX #17: NotificationOut.created_at → proper datetime type
  - FIX #18: PATCH endpoints add kiye (partial update support)
  - FIX #19: list_goats mein safe ordering parameter add kiya
  - FIX #20: list_health → ordered by -date (latest first)
  - FIX #21: list_milk → date_from/date_to filter + ordered by -date
"""

from ninja import NinjaAPI, Schema
from ninja.pagination import paginate, PageNumberPagination
from ninja.security import SessionAuth
from typing import List, Optional
from datetime import date, time, datetime
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.conf import settings

from .models import (
    Goat, BreedingRecord, HealthRecord, MilkProduction,
    FeedInventory, FeedConsumption, Sale, Expense, WeightRecord,
    PerformanceEvaluation, MarketPrice, WeatherRecord, FarmEvent,
    BreedingPlan, CustomReminder, AdditionalIncome, Task,
    Customer, Credit, Notification, Insurance, MortalityRecord,
    VaccinationSchedule, BudgetPlanning, ActivityLog, VetVisit,
)
from .weather_api import weather_api


# ==================== AUTHENTICATION ====================
# FIX #12: Using Django Session Auth instead of JWT
# Users login via web interface, same session works for API calls

# Single API instance — login auth=None hai, baaki sab SessionAuth se protected
api = NinjaAPI(
    title="🐐 Goat Farm Management API",
    version="5.5",
    auth=SessionAuth(),
    urls_namespace="farm_api",
    docs_url="/docs/",          # Swagger UI: /api/docs/
    openapi_url="/openapi.json",
)

# Weather router — auth=None (router-level pe set hai)
api.add_router("/weather/", weather_api)


# ==================== API ROOT ====================

@api.get("/", auth=None, tags=["Info"], summary="API root — welcome & links")
def api_root(request):
    """
    🐐 Goat Farm Management API

    Yahan se sab kuch access kar sakte hain:
    - **Swagger UI (interactive docs):** `/api/docs/`
    - **OpenAPI JSON:** `/api/openapi.json`
    - **Login:** `POST /api/auth/login/`
    - **Dashboard Stats:** `GET /api/stats/dashboard/`
    """
    return {
        "message": "🐐 Goat Farm Management API — v5.5",
        "status": "running",
        "links": {
            "swagger_ui":    "/api/docs/",
            "openapi_json":  "/api/openapi.json",
            "login":         "POST /api/auth/login/",
            "logout":        "POST /api/auth/logout/",
            "me":            "GET  /api/auth/me/",
            "dashboard":     "GET  /api/stats/dashboard/",
        },
        "quick_endpoints": {
            "goats":         "/api/goats/",
            "breeding":      "/api/breeding/",
            "health":        "/api/health/",
            "milk":          "/api/milk/",
            "sales":         "/api/sales/",
            "expenses":      "/api/expenses/",
            "weather_live":  "/api/weather/current/",
        }
    }


class LoginSchema(Schema):
    username: str
    password: str

class TokenSchema(Schema):
    access_token: str
    token_type: str
    username: str

class UserSchema(Schema):
    id: int
    username: str
    email: str
    is_staff: bool


@api.get("/auth/", auth=None, tags=["Auth"])
def auth_info(request):
    """Auth endpoints ki jankari"""
    return {
        "login":  "POST /api/auth/login/",
        "logout": "POST /api/auth/logout/",
        "me":     "GET  /api/auth/me/  (login required)",
        "docs":   "GET  /api/docs/",
    }


@api.post("/auth/login/", response={200: TokenSchema, 401: dict}, auth=None, tags=["Auth"])
def login(request, payload: LoginSchema):
    """
    Login करें — Session Auth
    Frontend ko session cookie automatically milti hai.
    """
    user = authenticate(request, username=payload.username, password=payload.password)
    if not user:
        return 401, {"detail": "Invalid username ya password. Dobara try karein."}

    auth_login(request, user)

    return 200, {
        "access_token": "session-based",
        "token_type": "session",
        "username": user.username,
    }


@api.post("/auth/logout/", auth=None, tags=["Auth"])
def logout_api(request):
    """Logout करें"""
    auth_logout(request)
    return {"detail": "Logged out successfully."}


@api.get("/auth/me/", response=UserSchema, tags=["Auth"])
def me(request):
    """Apni profile dekhein"""
    return {
        "id": request.auth.id,
        "username": request.auth.username,
        "email": request.auth.email,
        "is_staff": request.auth.is_staff,
    }


# ==================== SCHEMAS (Input / Output alag) ====================

# --- Goat ---
class GoatIn(Schema):
    tag_number: str
    name: str
    breed: str
    gender: str
    color: str
    date_of_birth: date
    weight: float
    purchase_date: date
    purchase_price: float
    status: str = 'A'
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    notes: Optional[str] = ''  # FIX: notes field add kiya (model mein tha, schema mein missing tha)

# FIX: GoatPatch — PATCH ke liye alag schema, sab fields Optional hain
class GoatPatch(Schema):
    tag_number: Optional[str] = None
    name: Optional[str] = None
    breed: Optional[str] = None
    gender: Optional[str] = None
    color: Optional[str] = None
    date_of_birth: Optional[date] = None
    weight: Optional[float] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    status: Optional[str] = None
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    notes: Optional[str] = None

class GoatOut(Schema):
    id: int
    tag_number: str
    name: str
    breed: str
    gender: str
    color: str
    date_of_birth: date
    weight: float
    purchase_date: date
    purchase_price: float
    status: str
    mother_id: Optional[int] = None
    father_id: Optional[int] = None
    notes: str = ''  # FIX: notes field GoatOut mein bhi add kiya
    age_months: int
    age_years: int
    created_at: datetime

    @staticmethod
    def resolve_age_months(obj):
        return obj.get_age_months()

    @staticmethod
    def resolve_age_years(obj):
        return obj.get_age_years()

# --- Breeding ---
class BreedingIn(Schema):
    mother_id: int
    father_id: int
    breeding_date: date
    # Auto-calculated as breeding_date + 150 days if not provided
    expected_delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    status: str = 'P'
    number_of_kids: Optional[int] = None
    notes: Optional[str] = ''

class BreedingOut(Schema):
    id: int
    mother_id: int
    father_id: int
    breeding_date: date
    expected_delivery_date: date
    actual_delivery_date: Optional[date] = None
    status: str
    number_of_kids: Optional[int] = None
    notes: str

# --- Health ---
class HealthIn(Schema):
    goat_id: int
    record_type: str
    date: date
    description: str
    medicine_used: Optional[str] = ''
    dosage: Optional[str] = ''
    cost: float
    veterinarian: Optional[str] = ''
    next_due_date: Optional[date] = None

class HealthOut(Schema):
    id: int
    goat_id: int
    record_type: str
    date: date
    description: str
    medicine_used: str
    dosage: str
    cost: float
    veterinarian: str
    next_due_date: Optional[date] = None

# --- Milk ---
class MilkIn(Schema):
    goat_id: int
    date: date
    session: str
    quantity: float
    fat_percentage: Optional[float] = None

class MilkOut(Schema):
    id: int
    goat_id: int
    date: date
    session: str
    quantity: float
    fat_percentage: Optional[float] = None

# --- Sale ---
class SaleIn(Schema):
    sale_type: str
    goat_id: Optional[int] = None
    date: date
    quantity: float
    unit: str
    price_per_unit: float
    # total_amount is auto-calculated in model's save() as quantity × price_per_unit
    total_amount: Optional[float] = None
    buyer_name: str
    buyer_contact: Optional[str] = ''
    payment_status: str = 'P'

class SaleOut(Schema):
    id: int
    sale_type: str
    goat_id: Optional[int] = None
    date: date
    quantity: float
    unit: str
    price_per_unit: float
    total_amount: float
    buyer_name: str
    buyer_contact: str
    payment_status: str

# --- Expense ---
class ExpenseIn(Schema):
    date: date
    expense_type: str
    description: str
    amount: float
    paid_to: str
    payment_method: str = 'C'

class ExpenseOut(Schema):
    id: int
    date: date
    expense_type: str
    description: str
    amount: float
    paid_to: str
    payment_method: str

# --- Weight ---
class WeightIn(Schema):
    goat_id: int
    date: date
    weight: float

class WeightOut(Schema):
    id: int
    goat_id: int
    date: date
    weight: float

# --- Performance ---
class PerformanceIn(Schema):
    goat_id: int
    evaluation_date: date
    weight_score: int
    milk_production_score: int
    health_score: int
    breeding_score: int
    overall_category: str
    total_score: int
    percentage: float
    notes: Optional[str] = ''

class PerformanceOut(Schema):
    id: int
    goat_id: int
    evaluation_date: date
    weight_score: int
    milk_production_score: int
    health_score: int
    breeding_score: int
    overall_category: str
    total_score: int
    percentage: float
    notes: str

# --- Market Price ---
class MarketPriceIn(Schema):
    item: str
    quality: str
    market: str
    location: str
    price: float
    unit: str
    date_recorded: date

class MarketPriceOut(Schema):
    id: int
    item: str
    quality: str
    market: str
    location: str
    price: float
    unit: str
    date_recorded: date

# --- Weather ---
class WeatherIn(Schema):
    date: date
    min_temperature: float
    max_temperature: float
    avg_temperature: float
    humidity: float
    rainfall: float = 0.0
    weather_condition: str
    impact_notes: Optional[str] = ''

class WeatherOut(Schema):
    id: int
    date: date
    min_temperature: float
    max_temperature: float
    avg_temperature: float
    humidity: float
    rainfall: float
    weather_condition: str
    impact_notes: str

# --- Breeding Plan ---
class BreedingPlanIn(Schema):
    title: str
    description: str
    target_breedings: int
    target_births: int
    target_breeds: str
    budget: float
    start_date: date
    end_date: date
    status: str = 'PLANNING'
    strategy_notes: Optional[str] = ''

class BreedingPlanOut(Schema):
    id: int
    title: str
    description: str
    target_breedings: int
    target_births: int
    target_breeds: str
    budget: float
    actual_spent: float
    status: str
    actual_breedings: int
    actual_births: int
    success_rate: float
    achievement_percentage: float
    start_date: date
    end_date: date
    strategy_notes: str

# --- Farm Event ---
class FarmEventIn(Schema):
    title: str
    event_type: str
    date: date
    location: str
    description: str
    attendees: Optional[str] = ''
    cost: float = 0.0
    is_milestone: bool = False

class FarmEventOut(Schema):
    id: int
    title: str
    event_type: str
    date: date
    location: str
    description: str
    attendees: str
    cost: float
    is_milestone: bool

# --- Reminder ---
class ReminderIn(Schema):
    title: str
    description: str
    reminder_type: str
    scheduled_time: time
    goat_id: Optional[int] = None
    is_active: bool = True

class ReminderOut(Schema):
    id: int
    title: str
    description: str
    reminder_type: str
    scheduled_time: time
    goat_id: Optional[int] = None
    is_active: bool


# ==================== GOAT ENDPOINTS ====================

@api.get("/goats/", response=List[GoatOut], tags=["Goats"])
@paginate(PageNumberPagination)
def list_goats(request, search: str = None, status: str = None, breed: str = None, ordering: str = "-created_at"):
    """सभी बकरियों की सूची — ordering: tag_number, name, -created_at, date_of_birth"""
    qs = Goat.objects.select_related('mother', 'father')
    
    if search:
        qs = qs.filter(Q(tag_number__icontains=search) | Q(name__icontains=search))
    if status:
        qs = qs.filter(status=status)
    if breed:
        qs = qs.filter(breed=breed)

    # Safe ordering — sirf allowed fields
    allowed_orderings = {
        "tag_number", "-tag_number", "name", "-name",
        "date_of_birth", "-date_of_birth", "created_at", "-created_at", "weight", "-weight"
    }
    if ordering in allowed_orderings:
        qs = qs.order_by(ordering)
    else:
        qs = qs.order_by("-created_at")
    
    return qs

@api.post("/goats/", response=GoatOut, tags=["Goats"])
def create_goat(request, payload: GoatIn):
    """नई बकरी जोड़ें"""
    return Goat.objects.create(**payload.dict())

@api.get("/goats/{goat_id}/", response=GoatOut, tags=["Goats"])
def get_goat(request, goat_id: int):
    """बकरी की विस्तृत जानकारी"""
    return get_object_or_404(Goat, id=goat_id)

@api.put("/goats/{goat_id}/", response=GoatOut, tags=["Goats"])
def update_goat(request, goat_id: int, payload: GoatIn):
    """बकरी की जानकारी अपडेट करें (full update)"""
    goat = get_object_or_404(Goat, id=goat_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(goat, attr, value)
    goat.save()
    return goat

@api.patch("/goats/{goat_id}/", response=GoatOut, tags=["Goats"])
def partial_update_goat(request, goat_id: int, payload: GoatPatch):
    """बकरी की जानकारी आंशिक रूप से अपडेट करें (partial update — sirf jo fields bhejo)"""
    goat = get_object_or_404(Goat, id=goat_id)
    # FIX: 'if value is not None' check hataya — notes ya mother_id jaisi fields
    # intentionally None/blank ho sakti hain. exclude_unset=True kaafi hai.
    for attr, value in payload.dict(exclude_unset=True).items():
        setattr(goat, attr, value)
    goat.save()
    return goat

@api.delete("/goats/{goat_id}/", tags=["Goats"])
def delete_goat(request, goat_id: int):
    """बकरी रिकॉर्ड हटाएं"""
    goat = get_object_or_404(Goat, id=goat_id)
    goat.delete()
    return {"deleted": True, "id": goat_id}


# ==================== BREEDING ENDPOINTS ====================

@api.get("/breeding/", response=List[BreedingOut], tags=["Breeding"])
@paginate(PageNumberPagination)
def list_breeding(request, status: str = None):
    qs = BreedingRecord.objects.select_related('mother', 'father')
    if status:
        qs = qs.filter(status=status)
    return qs

@api.post("/breeding/", response=BreedingOut, tags=["Breeding"])
def create_breeding(request, payload: BreedingIn):
    # FIX: expected_delivery_date None ho to model.save() auto-calculate karega (breeding_date + 150 days)
    # payload.dict() se None values nikaalo taaki model field validation fail na ho
    data = {k: v for k, v in payload.dict().items() if v is not None}
    return BreedingRecord.objects.create(**data)

@api.get("/breeding/{record_id}/", response=BreedingOut, tags=["Breeding"])
def get_breeding(request, record_id: int):
    return get_object_or_404(BreedingRecord, id=record_id)

@api.put("/breeding/{record_id}/", response=BreedingOut, tags=["Breeding"])
def update_breeding(request, record_id: int, payload: BreedingIn):
    record = get_object_or_404(BreedingRecord, id=record_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(record, attr, value)
    record.save()
    return record

@api.delete("/breeding/{record_id}/", tags=["Breeding"])
def delete_breeding(request, record_id: int):
    record = get_object_or_404(BreedingRecord, id=record_id)
    record.delete()
    return {"deleted": True, "id": record_id}


# ==================== HEALTH ENDPOINTS ====================

@api.get("/health/", response=List[HealthOut], tags=["Health"])
@paginate(PageNumberPagination)
def list_health(request, goat_id: int = None, record_type: str = None):
    qs = HealthRecord.objects.select_related('goat').order_by('-date')
    if goat_id:
        qs = qs.filter(goat_id=goat_id)
    if record_type:
        qs = qs.filter(record_type=record_type)
    return qs

@api.post("/health/", response=HealthOut, tags=["Health"])
def create_health(request, payload: HealthIn):
    return HealthRecord.objects.create(**payload.dict())

@api.get("/health/{record_id}/", response=HealthOut, tags=["Health"])
def get_health(request, record_id: int):
    return get_object_or_404(HealthRecord, id=record_id)

@api.put("/health/{record_id}/", response=HealthOut, tags=["Health"])
def update_health(request, record_id: int, payload: HealthIn):
    record = get_object_or_404(HealthRecord, id=record_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(record, attr, value)
    record.save()
    return record

@api.delete("/health/{record_id}/", tags=["Health"])
def delete_health(request, record_id: int):
    record = get_object_or_404(HealthRecord, id=record_id)
    record.delete()
    return {"deleted": True, "id": record_id}


# ==================== MILK ENDPOINTS ====================

@api.get("/milk/", response=List[MilkOut], tags=["Milk"])
@paginate(PageNumberPagination)
def list_milk(request, goat_id: int = None, date_from: date = None, date_to: date = None):
    qs = MilkProduction.objects.select_related('goat').order_by('-date')
    if goat_id:
        qs = qs.filter(goat_id=goat_id)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs

@api.post("/milk/", response={200: MilkOut, 409: dict}, tags=["Milk"])
def create_milk(request, payload: MilkIn):
    """दूध उत्पादन रिकॉर्ड जोड़ें — ek goat, ek date, ek session pe sirf ek record"""    # FIX: unique_together (goat, date, session) violation ke liye clear error
    if MilkProduction.objects.filter(
        goat_id=payload.goat_id, date=payload.date, session=payload.session
    ).exists():
        return 409, {"detail": f"Is goat ka {payload.date} date aur {payload.session} session ka record pehle se hai. Edit karne ke liye PUT use karein."}
    return 200, MilkProduction.objects.create(**payload.dict())

@api.get("/milk/{record_id}/", response=MilkOut, tags=["Milk"])
def get_milk(request, record_id: int):
    return get_object_or_404(MilkProduction, id=record_id)

@api.put("/milk/{record_id}/", response=MilkOut, tags=["Milk"])
def update_milk(request, record_id: int, payload: MilkIn):
    record = get_object_or_404(MilkProduction, id=record_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(record, attr, value)
    record.save()
    return record

@api.delete("/milk/{record_id}/", tags=["Milk"])
def delete_milk(request, record_id: int):
    record = get_object_or_404(MilkProduction, id=record_id)
    record.delete()
    return {"deleted": True, "id": record_id}


# ==================== SALES ENDPOINTS ====================

@api.get("/sales/", response=List[SaleOut], tags=["Sales"])
@paginate(PageNumberPagination)
def list_sales(request, goat_id: int = None, payment_status: str = None):
    qs = Sale.objects.select_related('goat')
    if goat_id:
        qs = qs.filter(goat_id=goat_id)
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    return qs

@api.post("/sales/", response=SaleOut, tags=["Sales"])
def create_sale(request, payload: SaleIn):
    return Sale.objects.create(**payload.dict())

@api.get("/sales/{sale_id}/", response=SaleOut, tags=["Sales"])
def get_sale(request, sale_id: int):
    return get_object_or_404(Sale, id=sale_id)

@api.put("/sales/{sale_id}/", response=SaleOut, tags=["Sales"])
def update_sale(request, sale_id: int, payload: SaleIn):
    sale = get_object_or_404(Sale, id=sale_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(sale, attr, value)
    sale.save()
    return sale

@api.delete("/sales/{sale_id}/", tags=["Sales"])
def delete_sale(request, sale_id: int):
    """बिक्रय रिकॉर्ड हटाएं"""
    sale = get_object_or_404(Sale, id=sale_id)
    sale.delete()
    return {"deleted": True, "id": sale_id}


# ==================== EXPENSE ENDPOINTS ====================

@api.get("/expenses/", response=List[ExpenseOut], tags=["Expenses"])
@paginate(PageNumberPagination)
def list_expenses(request, expense_type: str = None, date_from: date = None, date_to: date = None):
    qs = Expense.objects.order_by('-date')  # FIX: latest first ordering add kiya
    if expense_type:
        qs = qs.filter(expense_type=expense_type)
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs

@api.post("/expenses/", response=ExpenseOut, tags=["Expenses"])
def create_expense(request, payload: ExpenseIn):
    return Expense.objects.create(**payload.dict())

@api.get("/expenses/{expense_id}/", response=ExpenseOut, tags=["Expenses"])
def get_expense(request, expense_id: int):
    return get_object_or_404(Expense, id=expense_id)

@api.put("/expenses/{expense_id}/", response=ExpenseOut, tags=["Expenses"])
def update_expense(request, expense_id: int, payload: ExpenseIn):
    expense = get_object_or_404(Expense, id=expense_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(expense, attr, value)
    expense.save()
    return expense

@api.delete("/expenses/{expense_id}/", tags=["Expenses"])
def delete_expense(request, expense_id: int):
    """खर्च रिकॉर्ड हटाएं"""
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    return {"deleted": True, "id": expense_id}


# ==================== WEIGHT ENDPOINTS ====================

@api.get("/weight/", response=List[WeightOut], tags=["Weight"])
@paginate(PageNumberPagination)
def list_weight(request, goat_id: int = None):
    qs = WeightRecord.objects.select_related('goat')
    if goat_id:
        qs = qs.filter(goat_id=goat_id)
    return qs

@api.post("/weight/", response=WeightOut, tags=["Weight"])
def create_weight(request, payload: WeightIn):
    return WeightRecord.objects.create(**payload.dict())

@api.get("/weight/{record_id}/", response=WeightOut, tags=["Weight"])
def get_weight(request, record_id: int):
    return get_object_or_404(WeightRecord, id=record_id)

@api.put("/weight/{record_id}/", response=WeightOut, tags=["Weight"])
def update_weight(request, record_id: int, payload: WeightIn):
    record = get_object_or_404(WeightRecord, id=record_id)
    for attr, value in payload.dict(exclude_unset=False).items():
        setattr(record, attr, value)
    record.save()
    return record

@api.delete("/weight/{record_id}/", tags=["Weight"])
def delete_weight(request, record_id: int):
    record = get_object_or_404(WeightRecord, id=record_id)
    record.delete()
    return {"deleted": True, "id": record_id}


# ==================== PERFORMANCE ENDPOINTS ====================

@api.get("/performance/", response=List[PerformanceOut], tags=["Performance"])
@paginate(PageNumberPagination)
def list_performance(request, goat_id: int = None):
    qs = PerformanceEvaluation.objects.select_related('goat')
    if goat_id:
        qs = qs.filter(goat_id=goat_id)
    return qs

@api.post("/performance/", response=PerformanceOut, tags=["Performance"])
def create_performance(request, payload: PerformanceIn):
    return PerformanceEvaluation.objects.create(**payload.dict())

@api.get("/performance/{record_id}/", response=PerformanceOut, tags=["Performance"])
def get_performance(request, record_id: int):
    return get_object_or_404(PerformanceEvaluation, id=record_id)

@api.delete("/performance/{record_id}/", tags=["Performance"])
def delete_performance(request, record_id: int):
    record = get_object_or_404(PerformanceEvaluation, id=record_id)
    record.delete()
    return {"deleted": True, "id": record_id}


# ==================== MARKET PRICE ENDPOINTS ====================

@api.get("/market-prices/", response=List[MarketPriceOut], tags=["Market"])
@paginate(PageNumberPagination)
def list_prices(request, item: str = None):
    qs = MarketPrice.objects.all()
    if item:
        qs = qs.filter(item=item)
    return qs

@api.post("/market-prices/", response=MarketPriceOut, tags=["Market"])
def create_price(request, payload: MarketPriceIn):
    return MarketPrice.objects.create(**payload.dict())

@api.get("/market-prices/{price_id}/", response=MarketPriceOut, tags=["Market"])
def get_price(request, price_id: int):
    return get_object_or_404(MarketPrice, id=price_id)

@api.delete("/market-prices/{price_id}/", tags=["Market"])
def delete_price(request, price_id: int):
    record = get_object_or_404(MarketPrice, id=price_id)
    record.delete()
    return {"deleted": True, "id": price_id}


# ==================== WEATHER RECORDS ENDPOINTS ====================
# NOTE: /weather/ prefix is reserved for live weather router (weather_api)
# Stored WeatherRecord CRUD is at /weather-records/

@api.get("/weather-records/", response=List[WeatherOut], tags=["Weather Records"])
@paginate(PageNumberPagination)
def list_weather(request, date_from: date = None, date_to: date = None):
    """Database mein store kiye hue historical weather records"""
    qs = WeatherRecord.objects.all()
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)
    return qs

@api.post("/weather-records/", response=WeatherOut, tags=["Weather Records"])
def create_weather(request, payload: WeatherIn):
    """Naya weather record store karo"""
    return WeatherRecord.objects.create(**payload.dict())


# ==================== BREEDING PLAN ENDPOINTS ====================

@api.get("/breeding-plans/", response=List[BreedingPlanOut], tags=["Breeding Plans"])
@paginate(PageNumberPagination)
def list_plans(request, status: str = None):
    qs = BreedingPlan.objects.all()
    if status:
        qs = qs.filter(status=status)
    return qs

@api.post("/breeding-plans/", response=BreedingPlanOut, tags=["Breeding Plans"])
def create_plan(request, payload: BreedingPlanIn):
    return BreedingPlan.objects.create(**payload.dict())


# ==================== FARM EVENTS ENDPOINTS ====================

@api.get("/events/", response=List[FarmEventOut], tags=["Events"])
@paginate(PageNumberPagination)
def list_events(request, event_type: str = None):
    qs = FarmEvent.objects.all()
    if event_type:
        qs = qs.filter(event_type=event_type)
    return qs

@api.post("/events/", response=FarmEventOut, tags=["Events"])
def create_event(request, payload: FarmEventIn):
    return FarmEvent.objects.create(**payload.dict())


# ==================== REMINDERS ENDPOINTS ====================

@api.get("/reminders/", response=List[ReminderOut], tags=["Reminders"])
@paginate(PageNumberPagination)
def list_reminders(request, is_active: bool = True):
    return CustomReminder.objects.filter(is_active=is_active)

@api.post("/reminders/", response=ReminderOut, tags=["Reminders"])
def create_reminder(request, payload: ReminderIn):
    return CustomReminder.objects.create(**payload.dict())


# ==================== STATS ENDPOINTS ====================

@api.get("/stats/dashboard/", tags=["Stats"])
def get_dashboard_stats(request):
    """
    FIX #3: N+1 query problem fix —
    aggregate(Sum()) use kiya, sab records loop mein nahi chalate
    """
    today = date.today()

    total_milk = MilkProduction.objects.aggregate(
        total=Sum('quantity')
    )['total'] or 0

    total_revenue = Sale.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or 0

    # This month stats
    this_month_revenue = Sale.objects.filter(
        date__year=today.year, date__month=today.month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    this_month_expenses = Expense.objects.filter(
        date__year=today.year, date__month=today.month
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Upcoming: due vaccinations and deliveries
    upcoming_vaccinations = VaccinationSchedule.objects.filter(
        due_date__gte=today, completed=False
    ).count()

    upcoming_deliveries = BreedingRecord.objects.filter(
        expected_delivery_date__gte=today, status__in=['P', 'C']
    ).count()

    overdue_tasks = Task.objects.filter(
        due_date__lt=today, status__in=['P', 'IP']
    ).count()

    # FIX: 5 alag Goat queries → ek hi query mein sab counts (DB round-trips reduce)
    from django.db.models import Case, When, IntegerField
    goat_stats = Goat.objects.aggregate(
        total=Count('id'),
        active=Count(Case(When(status='A', then=1), output_field=IntegerField())),
        pregnant=Count(Case(When(status='P', then=1), output_field=IntegerField())),
        sold=Count(Case(When(status='S', then=1), output_field=IntegerField())),
        dead=Count(Case(When(status='D', then=1), output_field=IntegerField())),
    )

    return {
        # Goat counts — single optimized query
        "total_goats": goat_stats['total'],
        "active_goats": goat_stats['active'],
        "pregnant_goats": goat_stats['pregnant'],
        "sold_goats": goat_stats['sold'],
        "dead_goats": goat_stats['dead'],
        # Sales & expenses
        "total_sales_count": Sale.objects.count(),
        "total_expenses_count": Expense.objects.count(),
        "total_milk_production_liters": round(total_milk, 2),
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_profit": round(total_revenue - total_expenses, 2),
        # This month
        "this_month_revenue": round(this_month_revenue, 2),
        "this_month_expenses": round(this_month_expenses, 2),
        "this_month_profit": round(this_month_revenue - this_month_expenses, 2),
        # Alerts
        "upcoming_vaccinations": upcoming_vaccinations,
        "upcoming_deliveries": upcoming_deliveries,
        "overdue_tasks": overdue_tasks,
        "unpaid_sales": Sale.objects.filter(payment_status='UP').count(),
    }

@api.get("/stats/monthly-income/", tags=["Stats"])
def get_monthly_income(request, year: int, month: int):
    """मासिक आय — aggregate use kiya"""
    income = Sale.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    additional = AdditionalIncome.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    return {
        "year": year,
        "month": month,
        "sales_income": round(income, 2),
        "additional_income": round(additional, 2),
        "total": round(income + additional, 2),
    }

@api.get("/stats/monthly-expense/", tags=["Stats"])
def get_monthly_expense(request, year: int, month: int):
    """मासिक खर्च — aggregate use kiya"""
    total = Expense.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    return {
        "year": year,
        "month": month,
        "expense": round(total, 2),
    }

@api.get("/stats/profit-loss/", tags=["Stats"])
def get_profit_loss(request, year: int, month: int):
    """Monthly Profit/Loss statement"""
    income = Sale.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    additional = AdditionalIncome.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    expense = Expense.objects.filter(
        date__year=year, date__month=month
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = income + additional
    profit = total_income - expense

    return {
        "year": year,
        "month": month,
        "total_income": round(total_income, 2),
        "total_expense": round(expense, 2),
        "net_profit": round(profit, 2),
        "is_profitable": profit >= 0,
    }


# ==================== GOAT STATS ENDPOINT ====================

@api.get("/goats/{goat_id}/stats/", tags=["Goats"])
def get_goat_stats(request, goat_id: int):
    """Ek bkari ki poori performance summary"""
    goat = get_object_or_404(Goat, id=goat_id)

    total_milk = goat.milk_records.aggregate(total=Sum('quantity'))['total'] or 0
    total_health_cost = goat.health_records.aggregate(total=Sum('cost'))['total'] or 0

    latest_weight = goat.weight_records.first()
    weight_records_count = goat.weight_records.count()

    # Weight gain: latest vs earliest
    weight_gain = None
    if weight_records_count >= 2:
        earliest = goat.weight_records.last()
        if latest_weight and earliest:
            weight_gain = round(latest_weight.weight - earliest.weight, 2)

    return {
        "goat_id": goat.id,
        "tag_number": goat.tag_number,
        "name": goat.name,
        "age_months": goat.get_age_months(),
        "age_years": goat.get_age_years(),
        "current_weight": latest_weight.weight if latest_weight else goat.weight,
        "weight_gain_kg": weight_gain,
        "total_milk_liters": round(total_milk, 2),
        "health_records_count": goat.health_records.count(),
        "total_health_cost": round(total_health_cost, 2),
        "breeding_count": goat.breeding_as_mother.count() + goat.breeding_as_father.count(),
        "kids_count": goat.kids_as_mother.count() + goat.kids_as_father.count(),
        "is_insured": goat.insurance.exists(),
        "has_overdue_vaccination": goat.vaccination_schedule.filter(
            due_date__lt=date.today(),
            completed=False
        ).exists(),
    }


# ==================== NOTIFICATIONS ENDPOINTS ====================

class NotificationOut(Schema):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime

@api.get("/notifications/", response=List[NotificationOut], tags=["Notifications"])
@paginate(PageNumberPagination)
def list_notifications(request, unread_only: bool = False):
    """सूचनाएं — unread_only=true से सिर्फ न पढ़ी हुई"""
    qs = Notification.objects.all()
    if unread_only:
        qs = qs.filter(is_read=False)
    return qs

@api.post("/notifications/{notif_id}/mark-read/", tags=["Notifications"])
def mark_notification_read(request, notif_id: int):
    """Notification को पढ़ा हुआ mark करें"""
    notif = get_object_or_404(Notification, id=notif_id)
    notif.is_read = True
    notif.save()
    return {"marked_read": True, "id": notif_id}

@api.post("/notifications/mark-all-read/", tags=["Notifications"])
def mark_all_read(request):
    """सभी notifications को पढ़ा हुआ mark करें"""
    count = Notification.objects.filter(is_read=False).update(is_read=True)
    return {"marked_read": count}


# ==================== ANALYTICS ENDPOINTS (v6.0 Batch 1) ====================

@api.get("/analytics/pl-chart/", tags=["Analytics v6"])
def get_pl_chart(request, year: int = None):
    """Monthly Profit & Loss chart data."""
    from .analytics import get_monthly_pl
    if not year:
        from datetime import date
        year = date.today().year
    return get_monthly_pl(year)

@api.get("/analytics/yearly-summary/", tags=["Analytics v6"])
def get_yearly_summary(request, years: int = 3):
    """Last N years ka yearly P&L summary."""
    from .analytics import get_yearly_pl_summary
    return get_yearly_pl_summary(years)

@api.get("/analytics/breed-performance/", tags=["Analytics v6"])
def get_breed_performance(request):
    """Har breed ka performance comparison."""
    from .analytics import get_breed_performance
    return get_breed_performance()

@api.get("/analytics/top-goats/", tags=["Analytics v6"])
def get_top_goats(request, category: str = "milk", limit: int = 10):
    """Top goats by category: milk, weight_gain, health."""
    from .analytics import get_top_performers
    return get_top_performers(category, limit)

@api.get("/analytics/roi/", tags=["Analytics v6"])
def get_roi_analysis(request, limit: int = 10):
    """Top goats by ROI (Return on Investment)."""
    from .analytics import get_top_goats_by_roi
    return get_top_goats_by_roi(limit)

@api.get("/analytics/herd-growth/", tags=["Analytics v6"])
def get_herd_growth(request, months: int = 12):
    """Herd size trend — last N months."""
    from .analytics import get_herd_growth
    return get_herd_growth(months)

@api.get("/analytics/feed-efficiency/", tags=["Analytics v6"])
def get_feed_efficiency(request):
    """Feed cost per liter of milk — last 6 months."""
    from .analytics import get_feed_efficiency
    return get_feed_efficiency()

@api.get("/analytics/summary/", tags=["Analytics v6"])
def get_analytics_summary(request):
    """Quick analytics summary for dashboard cards."""
    from .analytics import get_analytics_summary
    return get_analytics_summary()


# ==================== AI ENGINE ENDPOINTS (v6.0 Batch 2) ====================

@api.get("/ai/breeding-suggestions/", tags=["AI Engine v6"])
def get_breeding_suggestions(request, limit: int = 5):
    """AI: Best breeding pairs suggest karo."""
    from .ai_engine import suggest_breeding_pairs
    return suggest_breeding_pairs(limit)

@api.get("/ai/sick-detection/", tags=["AI Engine v6"])
def get_sick_goat_alerts(request):
    """AI: Potentially sick goats detect karo."""
    from .ai_engine import detect_sick_goats
    return detect_sick_goats()

@api.get("/ai/sell-suggestions/", tags=["AI Engine v6"])
def get_sell_suggestions(request):
    """AI: Kaun se goats sell karne chahiye abhi."""
    from .ai_engine import suggest_sell_goats
    return suggest_sell_goats()

@api.get("/ai/feed-optimization/", tags=["AI Engine v6"])
def get_feed_optimization(request):
    """AI: Daily feed requirement per category."""
    from .ai_engine import get_feed_optimization
    return get_feed_optimization()

@api.get("/ai/revenue-forecast/", tags=["AI Engine v6"])
def get_revenue_forecast(request, months_ahead: int = 3):
    """AI: Agle N months ka revenue forecast."""
    from .ai_engine import forecast_revenue
    return forecast_revenue(months_ahead)


# ==================== INVOICE ENDPOINTS (v6.0 Batch 1) ====================

@api.get("/invoices/{sale_id}/pdf/", auth=None, tags=["Invoices v6"])
def download_invoice_pdf(request, sale_id: int):
    """Sale ka PDF invoice download karo."""
    from .invoice import invoice_pdf_response, REPORTLAB_AVAILABLE
    from django.http import JsonResponse
    
    sale = get_object_or_404(Sale, id=sale_id)
    
    if not REPORTLAB_AVAILABLE:
        return {"error": "ReportLab install nahi hai. Run: pip install reportlab"}
    
    return invoice_pdf_response(sale)


# ==================== QR CODE ENDPOINTS (v6.0 Batch 2) ====================

@api.get("/goats/{goat_id}/qr-code/", auth=None, tags=["QR Code v6"])
def get_goat_qr(request, goat_id: int):
    """Goat ka QR code PNG image download karo."""
    from .qr_utils import generate_qr_code, QR_AVAILABLE
    from django.http import HttpResponse
    
    if not QR_AVAILABLE:
        return {"error": "qrcode install nahi hai. Run: pip install qrcode[pil]"}
    
    goat = get_object_or_404(Goat, id=goat_id)
    base_url = request.build_absolute_uri('/').rstrip('/')
    qr_bytes = generate_qr_code(goat.tag_number, base_url)
    
    response = HttpResponse(qr_bytes, content_type='image/png')
    response['Content-Disposition'] = f'inline; filename="qr_{goat.tag_number}.png"'
    return response

@api.get("/goats/qr-batch-pdf/", tags=["QR Code v6"])
def get_batch_qr_pdf(request):
    """Sab active goats ke QR codes ek PDF mein."""
    from .qr_utils import generate_batch_qr_pdf, QR_AVAILABLE
    from django.http import HttpResponse
    
    if not QR_AVAILABLE:
        return {"error": "qrcode install nahi hai. Run: pip install qrcode[pil]"}
    
    goats = Goat.objects.filter(status__in=['A', 'P']).order_by('tag_number')
    base_url = request.build_absolute_uri('/').rstrip('/')
    pdf_bytes = generate_batch_qr_pdf(list(goats), base_url)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="goat_qr_tags.pdf"'
    return response


# ==================== NOTIFICATION ENDPOINTS (v6.0 Batch 2) ====================

@api.post("/notifications/send-vaccination-reminders/", tags=["Alerts v6"])
def trigger_vaccination_reminders(request, days_ahead: int = 3):
    """Vaccination due reminders bhejo (WhatsApp)."""
    from .notifications import send_vaccination_reminders
    results = send_vaccination_reminders(days_ahead)
    return {"sent": len(results), "results": results}

@api.post("/notifications/send-delivery-reminders/", tags=["Alerts v6"])
def trigger_delivery_reminders(request, days_ahead: int = 2):
    """Expected delivery reminders bhejo."""
    from .notifications import send_delivery_reminders
    results = send_delivery_reminders(days_ahead)
    return {"sent": len(results), "results": results}

@api.post("/notifications/send-payment-reminders/", tags=["Alerts v6"])
def trigger_payment_reminders(request):
    """Overdue payment reminders customers ko bhejo."""
    from .notifications import send_overdue_payment_reminders
    results = send_overdue_payment_reminders()
    return {"sent": len(results), "results": results}

@api.get("/notifications/daily-summary/", tags=["Alerts v6"])
def get_daily_summary(request):
    """Daily farm summary."""
    from .notifications import send_daily_summary
    return send_daily_summary()
