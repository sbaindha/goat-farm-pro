import pandas as pd
from datetime import datetime
from django.db import transaction
from .models import Goat, MilkProduction, Sale, HealthRecord, Expense
import io

class ExcelImportError(Exception):
    """Custom exception for Excel import errors"""
    pass

class ExcelImporter:
    """Handle Excel file imports for various models"""

    @staticmethod
    def import_goats(file):
        """
        Import Goats from Excel file
        Expected columns: tag_number, name, breed, gender, color, date_of_birth, 
                        weight, purchase_date, purchase_price, status
        """
        try:
            df = pd.read_excel(file)
            df = df.fillna('')
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        goat = Goat.objects.create(
                            tag_number=str(row['tag_number']).strip(),
                            name=str(row['name']).strip(),
                            breed=str(row['breed']).strip(),
                            gender=str(row['gender']).strip(),
                            color=str(row['color']).strip(),
                            date_of_birth=pd.to_datetime(row['date_of_birth']).date(),
                            weight=float(row['weight']),
                            purchase_date=pd.to_datetime(row['purchase_date']).date(),
                            purchase_price=float(row['purchase_price']),
                            status=str(row.get('status', 'A')).strip()
                        )
                        results['success'] += 1
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: {str(e)}")

            return results

        except Exception as e:
            raise ExcelImportError(f"Error importing goats: {str(e)}")

    @staticmethod
    def import_milk_production(file):
        """
        Import Milk Production records from Excel
        Expected columns: goat_tag, date, session, quantity, fat_percentage
        """
        try:
            df = pd.read_excel(file)
            df = df.fillna('')
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        goat = Goat.objects.get(tag_number=str(row['goat_tag']).strip())
                        
                        MilkProduction.objects.create(
                            goat=goat,
                            date=pd.to_datetime(row['date']).date(),
                            session=str(row['session']).strip().upper()[0],  # M or E
                            quantity=float(row['quantity']),
                            fat_percentage=float(row.get('fat_percentage', 0)) or None
                        )
                        results['success'] += 1
                    except Goat.DoesNotExist:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: Goat '{row['goat_tag']}' not found")
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: {str(e)}")

            return results

        except Exception as e:
            raise ExcelImportError(f"Error importing milk production: {str(e)}")

    @staticmethod
    def import_sales(file):
        """
        Import Sales records from Excel
        Expected columns: sale_type, date, quantity, unit, price_per_unit, 
                        total_amount, buyer_name, buyer_contact, payment_status
        """
        try:
            df = pd.read_excel(file)
            df = df.fillna('')
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        goat_id = None
                        if row.get('goat_tag'):
                            try:
                                goat = Goat.objects.get(tag_number=str(row['goat_tag']).strip())
                                goat_id = goat.id
                            except Goat.DoesNotExist:
                                pass

                        Sale.objects.create(
                            sale_type=str(row['sale_type']).strip(),
                            goat_id=goat_id,
                            date=pd.to_datetime(row['date']).date(),
                            quantity=float(row['quantity']),
                            unit=str(row['unit']).strip(),
                            price_per_unit=float(row['price_per_unit']),
                            total_amount=float(row['total_amount']),
                            buyer_name=str(row['buyer_name']).strip(),
                            buyer_contact=str(row.get('buyer_contact', '')).strip(),
                            payment_status=str(row.get('payment_status', 'P')).strip()
                        )
                        results['success'] += 1
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: {str(e)}")

            return results

        except Exception as e:
            raise ExcelImportError(f"Error importing sales: {str(e)}")

    @staticmethod
    def import_health_records(file):
        """
        Import Health Records from Excel
        Expected columns: goat_tag, record_type, date, description, 
                        medicine_used, dosage, cost, veterinarian, next_due_date
        """
        try:
            df = pd.read_excel(file)
            df = df.fillna('')
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        goat = Goat.objects.get(tag_number=str(row['goat_tag']).strip())
                        
                        next_due = None
                        if row.get('next_due_date'):
                            next_due = pd.to_datetime(row['next_due_date']).date()
                        
                        HealthRecord.objects.create(
                            goat=goat,
                            record_type=str(row['record_type']).strip()[0].upper(),
                            date=pd.to_datetime(row['date']).date(),
                            description=str(row['description']).strip(),
                            medicine_used=str(row.get('medicine_used', '')).strip(),
                            dosage=str(row.get('dosage', '')).strip(),
                            cost=float(row.get('cost', 0)),
                            veterinarian=str(row.get('veterinarian', '')).strip(),
                            next_due_date=next_due
                        )
                        results['success'] += 1
                    except Goat.DoesNotExist:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: Goat '{row['goat_tag']}' not found")
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: {str(e)}")

            return results

        except Exception as e:
            raise ExcelImportError(f"Error importing health records: {str(e)}")

    @staticmethod
    def import_expenses(file):
        """
        Import Expense records from Excel
        Expected columns: date, expense_type, description, amount, paid_to, payment_method
        """
        try:
            df = pd.read_excel(file)
            df = df.fillna('')
            
            results = {
                'success': 0,
                'failed': 0,
                'errors': []
            }

            with transaction.atomic():
                for idx, row in df.iterrows():
                    try:
                        Expense.objects.create(
                            date=pd.to_datetime(row['date']).date(),
                            expense_type=str(row['expense_type']).strip()[0].upper(),
                            description=str(row['description']).strip(),
                            amount=float(row['amount']),
                            paid_to=str(row['paid_to']).strip(),
                            payment_method=str(row.get('payment_method', 'C')).strip()[0].upper()
                        )
                        results['success'] += 1
                    except Exception as e:
                        results['failed'] += 1
                        results['errors'].append(f"Row {idx + 2}: {str(e)}")

            return results

        except Exception as e:
            raise ExcelImportError(f"Error importing expenses: {str(e)}")


class ExcelExporter:
    """Handle Excel file exports for various models"""

    @staticmethod
    def export_goats_template():
        """Export empty Goat template"""
        data = {
            'tag_number': ['G001', 'G002'],
            'name': ['Laila', 'Nisha'],
            'breed': ['Saanen', 'Alpine'],
            'gender': ['F', 'F'],
            'color': ['White', 'Brown'],
            'date_of_birth': ['2024-01-15', '2023-06-20'],
            'weight': [45.5, 42.0],
            'purchase_date': ['2024-01-15', '2023-06-20'],
            'purchase_price': [5000, 4500],
            'status': ['A', 'A']
        }
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Goats')
        output.seek(0)
        return output

    @staticmethod
    def export_milk_template():
        """Export empty Milk Production template"""
        data = {
            'goat_tag': ['G001', 'G001'],
            'date': ['2026-02-17', '2026-02-17'],
            'session': ['M', 'E'],
            'quantity': [2.5, 2.0],
            'fat_percentage': [4.2, 4.0]
        }
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Milk')
        output.seek(0)
        return output

    @staticmethod
    def export_sales_template():
        """Export empty Sales template"""
        data = {
            'sale_type': ['M', 'G'],
            'goat_tag': ['G001', 'G002'],
            'date': ['2026-02-17', '2026-02-17'],
            'quantity': [100, 1],
            'unit': ['Liter', 'Animal'],
            'price_per_unit': [150, 5000],
            'total_amount': [15000, 5000],
            'buyer_name': ['Dairy Co', 'Buyer'],
            'buyer_contact': ['9876543210', '9876543210'],
            'payment_status': ['P', 'P']
        }
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Sales')
        output.seek(0)
        return output

    @staticmethod
    def export_health_template():
        """Export empty Health Records template"""
        data = {
            'goat_tag': ['G001', 'G002'],
            'record_type': ['V', 'D'],
            'date': ['2026-02-17', '2026-02-17'],
            'description': ['FMD Vaccination', 'Deworming'],
            'medicine_used': ['FMD Vaccine', 'Albendazole'],
            'dosage': ['1 ml', '50 ml'],
            'cost': [200, 150],
            'veterinarian': ['Dr. Sharma', 'Dr. Patel'],
            'next_due_date': ['2026-05-17', '2026-05-17']
        }
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Health')
        output.seek(0)
        return output

    @staticmethod
    def export_expenses_template():
        """Export empty Expenses template"""
        data = {
            'date': ['2026-02-17', '2026-02-17'],
            'expense_type': ['F', 'M'],
            'description': ['Feed purchase', 'Medicine'],
            'amount': [5000, 1000],
            'paid_to': ['Supplier', 'Vet'],
            'payment_method': ['C', 'B']
        }
        df = pd.DataFrame(data)
        output = io.BytesIO()
        df.to_excel(output, index=False, sheet_name='Expenses')
        output.seek(0)
        return output
