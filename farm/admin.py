from django.contrib import admin

# FIX #1: Use specific imports instead of wildcard (PEP 8 compliance)
from .models import (
    Goat, BreedingRecord, HealthRecord, MilkProduction,
    FeedInventory, FeedConsumption, Sale, Expense, WeightRecord,
    Task, Customer, Credit, Notification, Insurance, MortalityRecord,
    AdditionalIncome, ActivityLog, VetVisit, VaccinationSchedule,
    BudgetPlanning, PerformanceEvaluation, CustomReminder, Document,
    PhotoGallery, WeatherRecord, MarketPrice, FarmEvent, BreedingPlan
)



@admin.register(Goat)
class GoatAdmin(admin.ModelAdmin):
    list_display = ['tag_number', 'name', 'breed', 'gender', 'status', 'date_of_birth']
    list_filter = ['breed', 'gender', 'status', 'created_at']
    search_fields = ['tag_number', 'name']
    fieldsets = (
        ('Basic Info', {'fields': ('tag_number', 'name', 'breed', 'gender', 'color')}),
        ('Birth & Age', {'fields': ('date_of_birth',)}),
        # FIX #1: 'photo_url' → 'photo' (ImageField se match karta hai)
        ('Physical', {'fields': ('weight', 'photo')}),
        ('Purchase', {'fields': ('purchase_date', 'purchase_price')}),
        ('Lineage', {'fields': ('mother', 'father')}),
        ('Status', {'fields': ('status',)}),
    )

@admin.register(BreedingRecord)
class BreedingRecordAdmin(admin.ModelAdmin):
    list_display = ['mother', 'father', 'breeding_date', 'expected_delivery_date', 'status']
    list_filter = ['status', 'breeding_date']
    search_fields = ['mother__name', 'father__name']

@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['goat', 'record_type', 'date', 'cost']
    list_filter = ['record_type', 'date']
    search_fields = ['goat__name']

@admin.register(MilkProduction)
class MilkProductionAdmin(admin.ModelAdmin):
    list_display = ['goat', 'date', 'session', 'quantity']
    list_filter = ['date', 'session']
    search_fields = ['goat__name']

@admin.register(FeedInventory)
class FeedInventoryAdmin(admin.ModelAdmin):
    list_display = ['feed_name', 'feed_type', 'quantity', 'unit', 'unit_price']
    list_filter = ['feed_type']
    search_fields = ['feed_name']

@admin.register(FeedConsumption)
class FeedConsumptionAdmin(admin.ModelAdmin):
    list_display = ['feed', 'date', 'quantity_consumed']
    list_filter = ['date']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['sale_type', 'date', 'quantity', 'total_amount', 'payment_status']
    list_filter = ['sale_type', 'date', 'payment_status']
    search_fields = ['buyer_name']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['date', 'expense_type', 'amount', 'paid_to']
    list_filter = ['expense_type', 'date']
    search_fields = ['paid_to']

@admin.register(WeightRecord)
class WeightRecordAdmin(admin.ModelAdmin):
    list_display = ['goat', 'date', 'weight']
    list_filter = ['date']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority', 'due_date']
    list_filter = ['status', 'priority']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'contact', 'email']
    search_fields = ['name', 'contact']

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ['customer', 'amount', 'date_issued', 'paid_amount', 'status']
    list_filter = ['status']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_read', 'created_at']
    list_filter = ['is_read']

@admin.register(Insurance)
class InsuranceAdmin(admin.ModelAdmin):
    list_display = ['goat', 'provider', 'coverage_amount', 'start_date', 'end_date']

@admin.register(MortalityRecord)
class MortalityRecordAdmin(admin.ModelAdmin):
    list_display = ['goat', 'death_date', 'cause']
    list_filter = ['death_date']

@admin.register(AdditionalIncome)
class AdditionalIncomeAdmin(admin.ModelAdmin):
    list_display = ['source', 'amount', 'date']

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'user', 'timestamp']
    list_filter = ['timestamp']
    readonly_fields = ['timestamp']

@admin.register(VetVisit)
class VetVisitAdmin(admin.ModelAdmin):
    list_display = ['date', 'vet_name', 'contact', 'cost']

@admin.register(VaccinationSchedule)
class VaccinationScheduleAdmin(admin.ModelAdmin):
    list_display = ['goat', 'vaccine_name', 'due_date', 'completed']
    list_filter = ['completed']

@admin.register(BudgetPlanning)
class BudgetPlanningAdmin(admin.ModelAdmin):
    list_display = ['category', 'planned_amount', 'actual_amount', 'month']

@admin.register(PerformanceEvaluation)
class PerformanceEvaluationAdmin(admin.ModelAdmin):
    list_display = ['goat', 'total_score', 'percentage', 'overall_category']

@admin.register(CustomReminder)
class CustomReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'reminder_type', 'is_active', 'scheduled_time']
    list_filter = ['reminder_type', 'is_active']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'expiry_date', 'goat']
    list_filter = ['document_type']

@admin.register(PhotoGallery)
class PhotoGalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'date_taken', 'featured']
    list_filter = ['category', 'featured']

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'avg_temperature', 'humidity', 'rainfall']

@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['item', 'quality', 'market', 'price', 'date_recorded']
    list_filter = ['item', 'quality']

@admin.register(FarmEvent)
class FarmEventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'location', 'cost']
    list_filter = ['event_type', 'is_milestone']

@admin.register(BreedingPlan)
class BreedingPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'budget', 'actual_spent', 'start_date']
    list_filter = ['status']