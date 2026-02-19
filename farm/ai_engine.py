"""
🐐 AI Engine — v6.0
Batch 2: AI-Powered Suggestions

Rule-based + simple scoring engine.
No external AI API — farm ke apne data se predictions.

Features:
1. Best Breeding Pair Suggestion
2. Sick Goat Early Detection
3. Optimal Selling Time
4. Feed Optimization Suggestion
5. Revenue Forecast (simple trend)
6. Mortality Risk Alert
"""

from datetime import date, timedelta
from django.db.models import Avg, Sum, Count

from .models import (
    Goat, BreedingRecord, HealthRecord, MilkProduction,
    WeightRecord, Sale, MarketPrice, Expense
)


# ==================== 1. BEST BREEDING PAIR ====================

def suggest_breeding_pairs(limit: int = 5):
    """
    Best mother-father pairs suggest karo.
    Score: (weight_score × 0.3) + (health_score × 0.4) + (milk_score × 0.3)

    Returns: list of (mother, father, score, reasons)
    """
    females = Goat.objects.filter(gender='F', status__in=['A', 'P'])
    males = Goat.objects.filter(gender='M', status='A')

    suggestions = []

    for female in females[:20]:  # Max 20 females check karo (performance)
        female_score = _calculate_breeding_score(female)

        for male in males[:10]:  # Max 10 males
            # Same parents nahi honay chahiye (incest check)
            if female.mother_id and female.mother_id == male.id:
                continue
            if female.father_id and female.father_id == male.id:
                continue

            male_score = _calculate_breeding_score(male)
            combined_score = round((female_score + male_score) / 2, 1)

            # Already recently bred?
            recent_breeding = BreedingRecord.objects.filter(
                mother=female, father=male,
                breeding_date__gte=date.today() - timedelta(days=200)
            ).exists()

            if recent_breeding:
                continue

            reasons = _get_breeding_reasons(female, male, female_score, male_score)

            suggestions.append({
                'mother_id': female.id,
                'mother_name': f"{female.name} ({female.tag_number})",
                'mother_breed': female.breed,
                'father_id': male.id,
                'father_name': f"{male.name} ({male.tag_number})",
                'father_breed': male.breed,
                'combined_score': combined_score,
                'mother_score': female_score,
                'father_score': male_score,
                'reasons': reasons,
            })

    return sorted(suggestions, key=lambda x: x['combined_score'], reverse=True)[:limit]


def _calculate_breeding_score(goat) -> float:
    """Goat ka breeding suitability score (0-100)."""
    score = 0

    # Weight score (0-30): Achi weight = zyada score
    avg_breed_weight = Goat.objects.filter(breed=goat.breed).aggregate(
        avg=Avg('weight'))['avg'] or goat.weight
    weight_ratio = goat.weight / max(float(avg_breed_weight), 1)
    score += min(30, weight_ratio * 20)

    # Health score (0-40): Kam treatments = zyada score
    treatment_count = goat.health_records.filter(record_type='T').count()
    health_score = max(0, 40 - treatment_count * 5)
    score += health_score

    # Age score (0-20): Optimal breeding age 1-4 years
    age_months = goat.get_age_months()
    if 12 <= age_months <= 48:
        score += 20
    elif age_months < 12:
        score += age_months / 12 * 10
    else:
        score += max(0, 20 - (age_months - 48) / 6)

    # Previous successful breeding (0-10)
    if goat.gender == 'F':
        successful = goat.breeding_as_mother.filter(status='D').count()
        score += min(10, successful * 3)
    else:
        fathered = goat.breeding_as_father.filter(status='D').count()
        score += min(10, fathered * 2)

    return round(min(100, score), 1)


def _get_breeding_reasons(female, male, f_score, m_score) -> list:
    reasons = []
    if f_score >= 70:
        reasons.append(f"{female.name} ka health score bahut acha hai ({f_score}/100)")
    if m_score >= 70:
        reasons.append(f"{male.name} genetically strong hai ({m_score}/100)")
    if female.breed != male.breed:
        reasons.append("Cross-breeding se hybrid vigor milega")
    if female.breeding_as_mother.filter(status='D').count() > 0:
        reasons.append(f"{female.name} ki previous deliveries successful rahi hain")
    return reasons or ["Standard score ke basis par suggest kiya gaya"]


# ==================== 2. SICK GOAT DETECTION ====================

def detect_sick_goats():
    """
    Early warning system for potentially sick goats.
    Indicators:
    - Weight loss > 10% in 2 weeks
    - Multiple treatments in last 30 days
    - No milk production drop > 30%
    """
    alerts = []
    today = date.today()

    for goat in Goat.objects.filter(status__in=['A', 'P']).prefetch_related(
        'weight_records', 'health_records', 'milk_records'
    ):
        risk_factors = []
        risk_level = 0  # 0=normal, 1=watch, 2=alert, 3=critical

        # --- Weight loss check ---
        recent_weights = goat.weight_records.filter(
            date__gte=today - timedelta(days=14)
        ).order_by('date')

        if recent_weights.count() >= 2:
            oldest = recent_weights.first().weight
            newest = recent_weights.last().weight
            if oldest > 0:
                loss_pct = (oldest - newest) / oldest * 100
                if loss_pct >= 15:
                    risk_factors.append(f"⚠️ {loss_pct:.1f}% weight loss in 2 weeks")
                    risk_level = max(risk_level, 3)
                elif loss_pct >= 10:
                    risk_factors.append(f"⚠️ {loss_pct:.1f}% weight loss — monitor karo")
                    risk_level = max(risk_level, 2)

        # --- Multiple treatments ---
        recent_treatments = goat.health_records.filter(
            record_type='T',
            date__gte=today - timedelta(days=30)
        ).count()

        if recent_treatments >= 3:
            risk_factors.append(f"⚠️ {recent_treatments} treatments last 30 days mein")
            risk_level = max(risk_level, 3)
        elif recent_treatments >= 2:
            risk_factors.append(f"⚠️ {recent_treatments} treatments last 30 days mein")
            risk_level = max(risk_level, 2)

        # --- Milk production drop (females only) ---
        if goat.gender == 'F':
            last_week_milk = goat.milk_records.filter(
                date__gte=today - timedelta(days=7)
            ).aggregate(total=Sum('quantity'))['total'] or 0

            prev_week_milk = goat.milk_records.filter(
                date__gte=today - timedelta(days=14),
                date__lt=today - timedelta(days=7)
            ).aggregate(total=Sum('quantity'))['total'] or 0

            if prev_week_milk > 0 and last_week_milk < prev_week_milk * 0.7:
                drop_pct = (prev_week_milk - last_week_milk) / prev_week_milk * 100
                risk_factors.append(f"⚠️ Milk production {drop_pct:.0f}% drop hua")
                risk_level = max(risk_level, 2)

        if risk_level >= 1:
            alerts.append({
                'goat_id': goat.id,
                'tag_number': goat.tag_number,
                'name': goat.name,
                'breed': goat.breed,
                'risk_level': risk_level,
                'risk_label': {1: 'Watch', 2: 'Alert', 3: 'Critical'}[risk_level],
                'risk_factors': risk_factors,
                'last_checkup': goat.health_records.filter(
                    record_type='C').order_by('-date').values_list('date', flat=True).first(),
            })

    return sorted(alerts, key=lambda x: x['risk_level'], reverse=True)


# ==================== 3. OPTIMAL SELLING TIME ====================

def suggest_sell_goats():
    """
    Kaun se goats sell karne chahiye abhi.
    Factors:
    - Age (6-18 months = prime selling age for meat)
    - Current market price vs average
    - Weight (target weight reached)
    - Farm capacity (too many goats)
    """
    suggestions = []
    today = date.today()

    # Current market price
    latest_live_price = MarketPrice.objects.filter(
        item='LIVE_GOAT'
    ).order_by('-date_recorded').values_list('price', flat=True).first()

    avg_market_price = MarketPrice.objects.filter(
        item='LIVE_GOAT'
    ).aggregate(avg=Avg('price'))['avg'] or 0

    price_favorable = (
        latest_live_price and avg_market_price and
        float(latest_live_price) > float(avg_market_price) * 1.1
    )

    for goat in Goat.objects.filter(status='A', gender='M').select_related():
        reasons = []
        score = 0
        age_months = goat.get_age_months()

        # Age check (6-18 months = prime for male meat goats)
        if 6 <= age_months <= 18:
            reasons.append(f"✅ Umar ({age_months} months) selling ke liye sahi hai")
            score += 40
        elif age_months > 24:
            reasons.append(f"⚠️ Zyada umar ({age_months} months) — value kam ho sakti hai")
            score += 20

        # Weight check (general: >25kg = good for selling)
        if goat.weight >= 25:
            reasons.append(f"✅ Weight ({goat.weight} kg) selling ke liye achha hai")
            score += 30

        # Market price favorable
        if price_favorable:
            reasons.append(f"✅ Market price avg se zyada hai (₹{latest_live_price}/unit)")
            score += 20

        # Health: recent treatments (cost-benefit)
        recent_health_cost = goat.health_records.filter(
            date__gte=today - timedelta(days=90)
        ).aggregate(total=Sum('cost'))['cost'] or 0
        if float(recent_health_cost or 0) > 1000:
            reasons.append(f"⚠️ Health cost zyada hai (₹{recent_health_cost}) — sell consider karein")
            score += 10

        if score >= 50:
            suggestions.append({
                'goat_id': goat.id,
                'tag_number': goat.tag_number,
                'name': goat.name,
                'breed': goat.breed,
                'age_months': age_months,
                'weight_kg': goat.weight,
                'score': score,
                'reasons': reasons,
                'estimated_value': round(goat.weight * float(latest_live_price or 200), 2),
            })

    return sorted(suggestions, key=lambda x: x['score'], reverse=True)


# ==================== 4. FEED OPTIMIZATION ====================

def get_feed_optimization():
    """
    Daily feed requirement suggest karo goat categories ke basis par.
    
    Standard requirements (approximate):
    - Adult female (>1yr): 3-4% body weight per day
    - Adult male: 2-3% body weight per day
    - Kids (<6 months): 5% body weight per day
    - Pregnant: +20% extra
    """
    today = date.today()
    recommendations = []

    categories = [
        {'label': 'Adult Females (Active)', 'filter': {'gender': 'F', 'status': 'A'}, 'pct': 0.035},
        {'label': 'Pregnant Females', 'filter': {'gender': 'F', 'status': 'P'}, 'pct': 0.042},
        {'label': 'Adult Males', 'filter': {'gender': 'M', 'status': 'A'}, 'pct': 0.025},
    ]

    for cat in categories:
        goats = Goat.objects.filter(**cat['filter'])
        count = goats.count()
        if count == 0:
            continue

        avg_weight = goats.aggregate(avg=Avg('weight'))['avg'] or 30
        daily_feed_per_goat = round(float(avg_weight) * cat['pct'], 2)
        total_daily = round(daily_feed_per_goat * count, 2)

        recommendations.append({
            'category': cat['label'],
            'count': count,
            'avg_weight_kg': round(float(avg_weight), 1),
            'daily_feed_per_goat_kg': daily_feed_per_goat,
            'total_daily_feed_kg': total_daily,
            'monthly_feed_kg': round(total_daily * 30, 1),
        })

    return recommendations


# ==================== 5. REVENUE FORECAST ====================

def forecast_revenue(months_ahead: int = 3):
    """
    Simple linear trend se agle months ka revenue forecast.
    Last 6 months ka average growth rate use karta hai.
    """
    today = date.today()
    monthly_revenues = []

    for i in range(6, 0, -1):
        year = today.year
        month = today.month - i
        while month <= 0:
            month += 12
            year -= 1

        revenue = Sale.objects.filter(
            date__year=year, date__month=month
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        monthly_revenues.append(float(revenue))

    if len(monthly_revenues) < 2:
        return []

    # Average growth rate
    growth_rates = []
    for i in range(1, len(monthly_revenues)):
        if monthly_revenues[i - 1] > 0:
            rate = (monthly_revenues[i] - monthly_revenues[i - 1]) / monthly_revenues[i - 1]
            growth_rates.append(rate)

    avg_growth = sum(growth_rates) / max(len(growth_rates), 1) if growth_rates else 0.05
    # Cap growth rate between -20% and +30%
    avg_growth = max(-0.20, min(0.30, avg_growth))

    last_revenue = monthly_revenues[-1] if monthly_revenues else 0
    forecasts = []

    for i in range(1, months_ahead + 1):
        year = today.year
        month = today.month + i
        while month > 12:
            month -= 12
            year += 1

        projected = round(last_revenue * ((1 + avg_growth) ** i), 2)
        forecasts.append({
            'month_name': date(year, month, 1).strftime('%B %Y'),
            'projected_revenue': projected,
            'growth_rate_pct': round(avg_growth * 100, 1),
            'confidence': 'High' if i == 1 else 'Medium' if i == 2 else 'Low',
        })

    return forecasts
