from django.urls import path
from . import views, excel_views


from .views import (
    download_goats_excel,
    download_breeding_excel,
    download_health_excel,
    download_milk_excel,
    download_sales_excel,
    download_expenses_excel,
    download_all_data,
)

# Backup & enhanced Excel views
from .backup_views import (
    backup_page,
    download_json_backup,
    download_zip_backup,
    restore_json_backup,
    download_complete_excel,
    download_excel_goats,
    download_excel_breeding,
    download_excel_health,
    download_excel_milk,
    download_excel_sales,
    download_excel_expenses,
    download_excel_weight,
    download_excel_tasks,
    download_excel_vaccination,
    download_excel_insurance,
    download_excel_customers,
    download_excel_feed,
    download_excel_mortality,
    backup_stats_api,
)

"""
Updated farm/urls.py with Admin Excel Routes
"""


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
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard pages (login required)
    path('', views.dashboard, name='dashboard'),
    path('weather/', views.weather_dashboard, name='weather'),
    path('goats/', views.goats_list, name='goats'),
    path('breeding/', views.breeding_list, name='breeding'),
    path('health/', views.health_list, name='health'),
    path('milk/', views.milk_list, name='milk'),
    path('sales/', views.sales_list, name='sales'),
    path('expenses/', views.expenses_list, name='expenses'),
    path('api-docs/', views.api_docs, name='api_docs'),     # purana — redirect karta hai
    path('api-help/', views.api_help, name='api_help'),     # naya interactive help page

    # Excel import/export
    path('excel/', excel_views.excel_import_page, name='excel_import'),
    path('excel/import/goats/', excel_views.import_goats_from_excel, name='import_goats'),
    path('excel/import/milk/', excel_views.import_milk_from_excel, name='import_milk'),
    path('excel/import/sales/', excel_views.import_sales_from_excel, name='import_sales'),
    path('excel/import/health/', excel_views.import_health_from_excel, name='import_health'),
    path('excel/import/expenses/', excel_views.import_expenses_from_excel, name='import_expenses'),

    # Excel template downloads
    path('excel/template/goats/', excel_views.download_goats_template, name='template_goats'),
    path('excel/template/milk/', excel_views.download_milk_template, name='template_milk'),
    path('excel/template/sales/', excel_views.download_sales_template, name='template_sales'),
    path('excel/template/health/', excel_views.download_health_template, name='template_health'),
    path('excel/template/expenses/', excel_views.download_expenses_template, name='template_expenses'),
    
    path('download/goats/', download_goats_excel, name='download_goats'),
    path('download/breeding/', download_breeding_excel, name='download_breeding'),
    path('download/health/', download_health_excel, name='download_health'),
    path('download/milk/', download_milk_excel, name='download_milk'),
    path('download/sales/', download_sales_excel, name='download_sales'),
    path('download/expenses/', download_expenses_excel, name='download_expenses'),
    path('download/all/', download_all_data, name='download_all'),

    
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
    # ==================== BACKUP & EXCEL DOWNLOAD URLS ====================

    # ==================== v6.0 NEW PAGES ====================
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('ai/', views.ai_dashboard, name='ai_dashboard'),
    path('invoices/', views.invoice_management, name='invoices'),
    path('qr/', views.qr_management, name='qr_management'),
    path('goat/scan/<str:tag_number>/', views.goat_scan_page, name='goat_scan'),

    # Backup page
    path('backup/', backup_page, name='backup'),

    # Full backup downloads
    path('backup/download/json/', download_json_backup, name='backup_json'),
    path('backup/download/zip/',  download_zip_backup,  name='backup_zip'),
    path('backup/download/excel/', download_complete_excel, name='backup_excel_complete'),

    # Restore
    path('backup/restore/', restore_json_backup, name='backup_restore'),

    # Stats API (for backup page live counts)
    path('backup/stats/', backup_stats_api, name='backup_stats'),

    # Individual Excel downloads (new enhanced versions)
    path('backup/excel/goats/',       download_excel_goats,       name='excel_goats'),
    path('backup/excel/breeding/',    download_excel_breeding,    name='excel_breeding'),
    path('backup/excel/health/',      download_excel_health,      name='excel_health'),
    path('backup/excel/milk/',        download_excel_milk,        name='excel_milk'),
    path('backup/excel/sales/',       download_excel_sales,       name='excel_sales'),
    path('backup/excel/expenses/',    download_excel_expenses,    name='excel_expenses'),
    path('backup/excel/weight/',      download_excel_weight,      name='excel_weight'),
    path('backup/excel/tasks/',       download_excel_tasks,       name='excel_tasks'),
    path('backup/excel/vaccination/', download_excel_vaccination, name='excel_vaccination'),
    path('backup/excel/insurance/',   download_excel_insurance,   name='excel_insurance'),
    path('backup/excel/customers/',   download_excel_customers,   name='excel_customers'),
    path('backup/excel/feed/',        download_excel_feed,        name='excel_feed'),
    path('backup/excel/mortality/',   download_excel_mortality,   name='excel_mortality'),
]


