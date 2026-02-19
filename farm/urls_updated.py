"""
Updated farm/urls.py with Admin Excel Routes
"""

from django.urls import path
from . import views

# Import admin excel views
from .admin_excel_views import (
    admin_download_goats_excel,
    admin_download_breeding_excel,
    admin_download_health_excel,
    admin_download_milk_excel,
    admin_download_sales_excel,
    admin_download_expenses_excel,
    admin_download_all_data,
    admin_excel_import,
    admin_excel_page,
)

urlpatterns = [
    # ==================== EXISTING URLS ====================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('weather/', views.weather_dashboard, name='weather'),
    path('goats/', views.goats_list, name='goats'),
    path('breeding/', views.breeding_list, name='breeding'),
    path('health/', views.health_list, name='health'),
    path('milk/', views.milk_list, name='milk'),
    path('sales/', views.sales_list, name='sales'),
    path('expenses/', views.expenses_list, name='expenses'),
    path('api-docs/', views.api_docs, name='api_docs'),
    
    # ==================== ADMIN EXCEL URLS (NEW) ====================
    
    # Main admin page
    path('admin/excel/', admin_excel_page, name='admin_excel_page'),
    
    # Downloads
    path('admin/download/goats/', admin_download_goats_excel, name='admin_download_goats'),
    path('admin/download/breeding/', admin_download_breeding_excel, name='admin_download_breeding'),
    path('admin/download/health/', admin_download_health_excel, name='admin_download_health'),
    path('admin/download/milk/', admin_download_milk_excel, name='admin_download_milk'),
    path('admin/download/sales/', admin_download_sales_excel, name='admin_download_sales'),
    path('admin/download/expenses/', admin_download_expenses_excel, name='admin_download_expenses'),
    path('admin/download/all/', admin_download_all_data, name='admin_download_all'),
    
    # Upload/Import
    path('admin/import/', admin_excel_import, name='admin_excel_import'),
]
