"""
🐐 Goat Farm Analytics Engine — v6.0
Batch 1: Advanced Analytics & Reports

Yeh module sab analytics calculations handle karta hai:
- Monthly P&L (Profit & Loss)
- Breed-wise performance comparison
- ROI per goat
- Herd growth trends
- Top performing goats
- Feed efficiency metrics
"""

from django.db.models import Sum, Count, Avg, F, Q, Case, When, IntegerField, FloatField
from django.db.models.functions import TruncMonth, TruncYear
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    Goat, Sale, Expense, MilkProduction, HealthRecord,
    BreedingRecord, WeightRecord, FeedInventory, FeedConsumption,
    AdditionalIncome
)


# ==================== P&L (Profit & Loss) ====================

def get_monthly_pl(year: int):
    """
    Poore saal ka monthly P&L data.
    Returns: list of 12 months with income, expense, profit
    """
    months = []
    for month in range(1, 13):
        income = Sale.objects.filter(
            date__year=year, date__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        additional = AdditionalIncome.objects.filter(
            date__year=year, date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        expense = Expense.objects.filter(
            date__year=year, date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_income = float(income) + float(additional)
        total_expense = float(expense)

        months.append({
            'month': month,
            'month_name': date(year, month, 1).strftime('%b'),
            'income': round(total_income, 2),
            'expense': round(total_expense, 2),
            'profit': round(total_income - total_expense, 2),
            'is_profitable': total_income >= total_expense,
        })

    return {
        'year': year,
        'months': months,
        'total_income': round(sum(m['income'] for m in months), 2),
        'total_expense': round(sum(m['expense'] for m in months), 2),
        'total_profit': round(sum(m['profit'] for m in months), 2),
    }


def get_yearly_pl_summary(years: int = 3):
    """Last N years ka yearly summary."""
    current_year = date.today().year
    results = []
    for y in range(current_year - years + 1, current_year + 1):
        data = get_monthly_pl(y)
        results.append({
            'year': y,
            'income': data['total_income'],
            'expense': data['total_expense'],
            'profit': data['total_profit'],
        })
    return results


# ==================== Breed-wise Performance ====================

def get_breed_performance():
    """
    Har breed ka performance comparison.
    Returns: milk yield, avg weight, health cost, count per breed
    """
    breeds = Goat.objects.values('breed').annotate(
        total=Count('id'),
        active=Count(Case(When(status='A', then=1), output_field=IntegerField())),
        avg_weight=Avg('weight'),
    ).order_by('-total')

    result = []
    for b in breeds:
        breed_goat_ids = list(Goat.objects.filter(breed=b['breed']).values_list('id', flat=True))

        total_milk = MilkProduction.objects.filter(
            goat_id__in=breed_goat_ids
        ).aggregate(total=Sum('quantity'))['total'] or 0

        avg_health_cost = HealthRecord.objects.filter(
            goat_id__in=breed_goat_ids
        ).aggregate(avg=Avg('cost'))['avg'] or 0

        avg_milk_per_goat = round(float(total_milk) / max(b['total'], 1), 2)

        result.append({
            'breed': b['breed'],
            'total_goats': b['total'],
            'active_goats': b['active'],
            'avg_weight_kg': round(float(b['avg_weight'] or 0), 2),
            'total_milk_liters': round(float(total_milk), 2),
            'avg_milk_per_goat': avg_milk_per_goat,
            'avg_health_cost': round(float(avg_health_cost), 2),
        })

    return sorted(result, key=lambda x: x['avg_milk_per_goat'], reverse=True)


# ==================== ROI per Goat ====================

def get_top_goats_by_roi(limit: int = 10):
    """
    Har goat ka ROI calculate karo.
    ROI = (total revenue generated - purchase price) / purchase price × 100
    """
    goats = Goat.objects.filter(status__in=['A', 'P', 'S']).select_related('mother', 'father')
    result = []

    for goat in goats:
        # Revenue: milk sales (proportional) + direct goat sale
        milk_revenue = Sale.objects.filter(
            sale_type='M', date__gte=goat.purchase_date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        # Milk revenue approximation: goat's share = goat_milk / total_farm_milk
        goat_milk = MilkProduction.objects.filter(goat=goat).aggregate(
            total=Sum('quantity'))['total'] or 0
        total_farm_milk = MilkProduction.objects.aggregate(
            total=Sum('quantity'))['total'] or 1
        milk_share = float(goat_milk) / float(total_farm_milk)
        goat_milk_revenue = float(milk_revenue) * milk_share

        # Direct sale revenue
        direct_sale = Sale.objects.filter(
            goat=goat, sale_type='G'
        ).aggregate(total=Sum('total_amount'))['total'] or 0

        total_revenue = goat_milk_revenue + float(direct_sale)
        purchase_price = float(goat.purchase_price)

        # Health cost (investment)
        health_cost = HealthRecord.objects.filter(goat=goat).aggregate(
            total=Sum('cost'))['total'] or 0
        total_investment = purchase_price + float(health_cost)

        roi = ((total_revenue - total_investment) / max(total_investment, 1)) * 100

        result.append({
            'goat_id': goat.id,
            'tag_number': goat.tag_number,
            'name': goat.name,
            'breed': goat.breed,
            'purchase_price': purchase_price,
            'total_revenue': round(total_revenue, 2),
            'total_investment': round(total_investment, 2),
            'roi_percent': round(roi, 1),
            'milk_liters': round(float(goat_milk), 2),
        })

    return sorted(result, key=lambda x: x['roi_percent'], reverse=True)[:limit]


# ==================== Herd Growth Trend ====================

def get_herd_growth(months: int = 12):
    """
    Last N months ka herd size trend.
    Returns: births, deaths, sales, net change per month
    """
    today = date.today()
    result = []

    for i in range(months - 1, -1, -1):
        # Month calculate karo
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        births = BreedingRecord.objects.filter(
            actual_delivery_date__year=year,
            actual_delivery_date__month=month,
            status='D'
        ).aggregate(kids=Sum('number_of_kids'))['kids'] or 0

        deaths = Goat.objects.filter(
            mortality__death_date__year=year,
            mortality__death_date__month=month
        ).count()

        sales = Sale.objects.filter(
            sale_type='G', date__year=year, date__month=month
        ).count()

        purchases = Goat.objects.filter(
            purchase_date__year=year, purchase_date__month=month
        ).count()

        result.append({
            'year': year,
            'month': month,
            'month_name': date(year, month, 1).strftime('%b %Y'),
            'births': int(births),
            'deaths': deaths,
            'sales': sales,
            'purchases': purchases,
            'net_change': int(births) + purchases - deaths - sales,
        })

    return result


# ==================== Top Performing Goats ====================

def get_top_performers(category: str = 'milk', limit: int = 10):
    """
    Top goats by category: 'milk', 'weight_gain', 'health'
    """
    if category == 'milk':
        data = MilkProduction.objects.values('goat_id').annotate(
            total_milk=Sum('quantity')
        ).order_by('-total_milk')[:limit]

        result = []
        for d in data:
            try:
                goat = Goat.objects.get(pk=d['goat_id'])
                result.append({
                    'goat_id': goat.id,
                    'tag_number': goat.tag_number,
                    'name': goat.name,
                    'breed': goat.breed,
                    'value': round(float(d['total_milk']), 2),
                    'unit': 'Liters',
                })
            except Goat.DoesNotExist:
                pass
        return result

    elif category == 'weight_gain':
        result = []
        for goat in Goat.objects.filter(status__in=['A', 'P']):
            records = goat.weight_records.order_by('date')
            if records.count() >= 2:
                gain = records.last().weight - records.first().weight
                days = (records.last().date - records.first().date).days or 1
                result.append({
                    'goat_id': goat.id,
                    'tag_number': goat.tag_number,
                    'name': goat.name,
                    'breed': goat.breed,
                    'value': round(gain, 2),
                    'unit': 'kg gain',
                    'daily_gain': round(gain / days * 30, 2),  # per month
                })
        return sorted(result, key=lambda x: x['value'], reverse=True)[:limit]

    elif category == 'health':
        # Fewest health issues = best health
        result = []
        for goat in Goat.objects.filter(status__in=['A', 'P']):
            treatment_count = goat.health_records.filter(record_type='T').count()
            health_cost = goat.health_records.aggregate(total=Sum('cost'))['total'] or 0
            result.append({
                'goat_id': goat.id,
                'tag_number': goat.tag_number,
                'name': goat.name,
                'breed': goat.breed,
                'value': treatment_count,
                'unit': 'treatments',
                'total_health_cost': round(float(health_cost), 2),
            })
        return sorted(result, key=lambda x: x['value'])[:limit]

    return []


# ==================== Feed Efficiency ====================

def get_feed_efficiency():
    """
    Feed cost per liter of milk.
    Monthly breakdown.
    """
    today = date.today()
    result = []

    for i in range(5, -1, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        feed_cost = Expense.objects.filter(
            expense_type='F',
            date__year=year, date__month=month
        ).aggregate(total=Sum('amount'))['total'] or 0

        milk_produced = MilkProduction.objects.filter(
            date__year=year, date__month=month
        ).aggregate(total=Sum('quantity'))['total'] or 0

        cost_per_liter = (
            round(float(feed_cost) / float(milk_produced), 2)
            if milk_produced else None
        )

        result.append({
            'month_name': date(year, month, 1).strftime('%b %Y'),
            'feed_cost': round(float(feed_cost), 2),
            'milk_liters': round(float(milk_produced), 2),
            'cost_per_liter': cost_per_liter,
        })

    return result


# ==================== Dashboard Summary ====================

def get_analytics_summary():
    """Quick summary for analytics dashboard cards."""
    today = date.today()
    this_month = get_monthly_pl(today.year)['months'][today.month - 1]
    last_month_num = today.month - 1 or 12
    last_month_year = today.year if today.month > 1 else today.year - 1
    last_month = get_monthly_pl(last_month_year)['months'][last_month_num - 1]

    profit_change = (
        ((this_month['profit'] - last_month['profit']) / abs(last_month['profit']) * 100)
        if last_month['profit'] != 0 else 0
    )

    return {
        'this_month_profit': this_month['profit'],
        'last_month_profit': last_month['profit'],
        'profit_change_percent': round(profit_change, 1),
        'total_active_goats': Goat.objects.filter(status='A').count(),
        'total_milk_this_month': MilkProduction.objects.filter(
            date__year=today.year, date__month=today.month
        ).aggregate(total=Sum('quantity'))['total'] or 0,
    }
