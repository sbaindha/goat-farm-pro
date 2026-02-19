from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .excel_utils import ExcelImporter, ExcelExporter, ExcelImportError
import json

@require_http_methods(["GET"])
def excel_import_page(request):
    """Excel Import Page - डेटा import करने का page"""
    return render(request, 'farm/excel_import.html')

@require_http_methods(["POST"])
def import_goats_from_excel(request):
    """Import Goats from Excel"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        results = ExcelImporter.import_goats(file)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully imported {results['success']} goats",
            'data': results
        })
    except ExcelImportError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def import_milk_from_excel(request):
    """Import Milk Production records from Excel"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        results = ExcelImporter.import_milk_production(file)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully imported {results['success']} milk records",
            'data': results
        })
    except ExcelImportError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def import_sales_from_excel(request):
    """Import Sales records from Excel"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        results = ExcelImporter.import_sales(file)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully imported {results['success']} sales records",
            'data': results
        })
    except ExcelImportError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def import_health_from_excel(request):
    """Import Health records from Excel"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        results = ExcelImporter.import_health_records(file)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully imported {results['success']} health records",
            'data': results
        })
    except ExcelImportError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

@require_http_methods(["POST"])
def import_expenses_from_excel(request):
    """Import Expense records from Excel"""
    try:
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
        
        file = request.FILES['file']
        results = ExcelImporter.import_expenses(file)
        
        return JsonResponse({
            'success': True,
            'message': f"Successfully imported {results['success']} expense records",
            'data': results
        })
    except ExcelImportError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Error: {str(e)}'}, status=500)

# DOWNLOAD TEMPLATES

@require_http_methods(["GET"])
def download_goats_template(request):
    """Download Goats Excel template"""
    try:
        excel_file = ExcelExporter.export_goats_template()
        response = HttpResponse(excel_file.getvalue(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Goats_Template.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def download_milk_template(request):
    """Download Milk Production Excel template"""
    try:
        excel_file = ExcelExporter.export_milk_template()
        response = HttpResponse(excel_file.getvalue(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Milk_Template.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def download_sales_template(request):
    """Download Sales Excel template"""
    try:
        excel_file = ExcelExporter.export_sales_template()
        response = HttpResponse(excel_file.getvalue(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Sales_Template.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def download_health_template(request):
    """Download Health Records Excel template"""
    try:
        excel_file = ExcelExporter.export_health_template()
        response = HttpResponse(excel_file.getvalue(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Health_Template.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["GET"])
def download_expenses_template(request):
    """Download Expenses Excel template"""
    try:
        excel_file = ExcelExporter.export_expenses_template()
        response = HttpResponse(excel_file.getvalue(), 
                              content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Expenses_Template.xlsx"'
        return response
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
