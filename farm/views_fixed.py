from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from .models import *
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta

@require_http_methods(["GET"])
def dashboard(request):
    """Professional Dashboard - मुख्य डैशबोर्ड"""
    return render(request, 'farm/professional_dashboard.html')

@require_http_methods(["GET"])
def weather_dashboard(request):
    """Weather Dashboard - मौसम डैशबोर्ड"""
    return render(request, 'farm/weather_dashboard.html')

@require_http_methods(["GET"])
def goats_list(request):
    """Goats Management - बकरियां प्रबंधन"""
    return render(request, 'farm/goats_management.html')

@require_http_methods(["GET"])
def breeding_list(request):
    """Breeding Records - प्रजनन रिकॉर्ड"""
    return render(request, 'farm/breeding_management.html')

@require_http_methods(["GET"])
def health_list(request):
    """Health Records - स्वास्थ्य रिकॉर्ड"""
    return render(request, 'farm/health_management.html')

@require_http_methods(["GET"])
def milk_list(request):
    """Milk Production - दूध उत्पादन"""
    return render(request, 'farm/milk_management.html')

@require_http_methods(["GET"])
def sales_list(request):
    """Sales Management - बिक्रय प्रबंधन"""
    return render(request, 'farm/sales_management.html')

@require_http_methods(["GET"])
def expenses_list(request):
    """Expenses Management - खर्च प्रबंधन"""
    return render(request, 'farm/expenses_management.html')

@require_http_methods(["GET"])
def api_docs(request):
    """API Documentation - API डॉक्यूमेंटेशन"""
    api_endpoints = [
        {
            'name': 'Goats',
            'endpoints': [
                'GET /api/goats/ - List all goats',
                'POST /api/goats/ - Create new goat',
                'GET /api/goats/{id}/ - Get goat details',
                'PUT /api/goats/{id}/ - Update goat',
                'DELETE /api/goats/{id}/ - Delete goat',
            ]
        },
        {
            'name': 'Breeding Records',
            'endpoints': [
                'GET /api/breeding/ - List breeding records',
                'POST /api/breeding/ - Create breeding record',
                'GET /api/breeding/{id}/ - Get breeding details',
                'PUT /api/breeding/{id}/ - Update breeding',
            ]
        },
        {
            'name': 'Health Records',
            'endpoints': [
                'GET /api/health/ - List health records',
                'POST /api/health/ - Create health record',
                'GET /api/health/{id}/ - Get health details',
            ]
        },
        {
            'name': 'Milk Production',
            'endpoints': [
                'GET /api/milk/ - List milk records',
                'POST /api/milk/ - Create milk record',
                'GET /api/milk/{id}/ - Get milk details',
            ]
        },
        {
            'name': 'Sales',
            'endpoints': [
                'GET /api/sales/ - List sales',
                'POST /api/sales/ - Create sale',
                'GET /api/sales/{id}/ - Get sale details',
            ]
        },
        {
            'name': 'Expenses',
            'endpoints': [
                'GET /api/expenses/ - List expenses',
                'POST /api/expenses/ - Create expense',
                'GET /api/expenses/{id}/ - Get expense details',
            ]
        },
        {
            'name': 'Statistics',
            'endpoints': [
                'GET /api/stats/dashboard/ - Dashboard statistics',
                'GET /api/stats/monthly-income/?year=2026&month=2 - Monthly income',
                'GET /api/stats/monthly-expense/?year=2026&month=2 - Monthly expense',
            ]
        },
    ]
    
    context = {
        'api_endpoints': api_endpoints,
        'total_endpoints': sum(len(e['endpoints']) for e in api_endpoints)
    }
    
    return render(request, 'farm/api_docs.html', context)
