"""
🐐 Notification Engine — v6.0
Batch 2: WhatsApp/SMS Alerts

Features:
- WhatsApp message via Twilio
- Vaccination due reminders
- Delivery expected alerts
- Overdue payment reminders
- Low feed stock alerts
- Daily farm summary

Setup in .env:
    TWILIO_ACCOUNT_SID=your_sid
    TWILIO_AUTH_TOKEN=your_token
    TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
    FARM_OWNER_PHONE=+919876543210
"""

import os
import logging
from datetime import date, timedelta
from django.conf import settings
from django.db.models import Sum

logger = logging.getLogger(__name__)


# ==================== TWILIO SETUP ====================

def _get_twilio_client():
    """Twilio client return karo — not available hai to None."""
    try:
        from twilio.rest import Client
        sid = os.environ.get('TWILIO_ACCOUNT_SID', '')
        token = os.environ.get('TWILIO_AUTH_TOKEN', '')
        if sid and token:
            return Client(sid, token)
    except ImportError:
        logger.warning("Twilio install nahi hai. pip install twilio")
    return None


def _send_whatsapp(to_phone: str, message: str) -> dict:
    """
    WhatsApp message bhejo.
    Returns: {'success': True/False, 'sid': '...', 'error': '...'}
    """
    client = _get_twilio_client()
    if not client:
        logger.info(f"[DEMO] WhatsApp to {to_phone}: {message[:100]}...")
        return {'success': False, 'error': 'Twilio not configured — demo mode', 'demo': True}

    from_number = os.environ.get('TWILIO_WHATSAPP_FROM', 'whatsapp:+14155238886')
    to_number = f"whatsapp:{to_phone}" if not to_phone.startswith('whatsapp:') else to_phone

    try:
        msg = client.messages.create(body=message, from_=from_number, to=to_number)
        logger.info(f"WhatsApp sent to {to_phone}: SID={msg.sid}")
        return {'success': True, 'sid': msg.sid}
    except Exception as e:
        logger.error(f"WhatsApp failed to {to_phone}: {e}")
        return {'success': False, 'error': str(e)}


def _log_notification(title: str, message: str, sent_to: str = ''):
    """Notification log karo database mein."""
    from .models import Notification
    Notification.objects.create(
        title=title,
        message=f"[Auto] {message}" + (f" | Sent to: {sent_to}" if sent_to else "")
    )


# ==================== REMINDER FUNCTIONS ====================

def send_vaccination_reminders(days_ahead: int = 3) -> list:
    """
    Upcoming vaccination dues ke liye reminders bhejo.
    Default: agle 3 din mein due vaccinations.
    """
    from .models import VaccinationSchedule

    owner_phone = os.environ.get('FARM_OWNER_PHONE', '')
    cutoff = date.today() + timedelta(days=days_ahead)

    due_vaccinations = VaccinationSchedule.objects.filter(
        due_date__lte=cutoff,
        due_date__gte=date.today(),
        completed=False
    ).select_related('goat')

    results = []
    for vacc in due_vaccinations:
        days_left = (vacc.due_date - date.today()).days
        message = (
            f"🐐 *Goat Farm Alert*\n\n"
            f"💉 *Vaccination Due {'Today' if days_left == 0 else f'in {days_left} days'}!*\n\n"
            f"Goat: *{vacc.goat.name}* ({vacc.goat.tag_number})\n"
            f"Vaccine: *{vacc.vaccine_name}*\n"
            f"Due Date: *{vacc.due_date.strftime('%d %B %Y')}*\n\n"
            f"Please schedule the vaccination immediately."
        )

        result = {'vaccination_id': vacc.id, 'goat': vacc.goat.name, 'vaccine': vacc.vaccine_name}
        if owner_phone:
            result['whatsapp'] = _send_whatsapp(owner_phone, message)

        _log_notification(
            f"Vaccination Due: {vacc.goat.name} — {vacc.vaccine_name}",
            message
        )
        results.append(result)

    logger.info(f"Sent {len(results)} vaccination reminders")
    return results


def send_delivery_reminders(days_ahead: int = 2) -> list:
    """Upcoming expected deliveries ke liye alerts."""
    from .models import BreedingRecord

    owner_phone = os.environ.get('FARM_OWNER_PHONE', '')
    cutoff = date.today() + timedelta(days=days_ahead)

    upcoming = BreedingRecord.objects.filter(
        expected_delivery_date__lte=cutoff,
        expected_delivery_date__gte=date.today(),
        status__in=['P', 'C']
    ).select_related('mother', 'father')

    results = []
    for breeding in upcoming:
        days_left = (breeding.expected_delivery_date - date.today()).days
        message = (
            f"🐐 *Goat Farm Alert*\n\n"
            f"🍼 *Delivery Expected {'Today' if days_left == 0 else f'in {days_left} days'}!*\n\n"
            f"Mother: *{breeding.mother.name}* ({breeding.mother.tag_number})\n"
            f"Father: *{breeding.father.name}* ({breeding.father.tag_number})\n"
            f"Expected Date: *{breeding.expected_delivery_date.strftime('%d %B %Y')}*\n\n"
            f"Please prepare a clean birthing area and monitor closely."
        )

        result = {'breeding_id': breeding.id, 'mother': breeding.mother.name}
        if owner_phone:
            result['whatsapp'] = _send_whatsapp(owner_phone, message)

        _log_notification(f"Delivery Expected: {breeding.mother.name}", message)
        results.append(result)

    return results


def send_overdue_payment_reminders() -> list:
    """Overdue credit customers ko reminder bhejo."""
    from .models import Credit

    results = []
    overdue_credits = Credit.objects.filter(
        status__in=['Pending', 'Partial', 'Overdue'],
        due_date__lt=date.today()
    ).select_related('customer')

    for credit in overdue_credits:
        customer_phone = credit.customer.contact
        days_overdue = (date.today() - credit.due_date).days

        message = (
            f"🐐 *Goat Farm — Payment Reminder*\n\n"
            f"Namaskar {credit.customer.name} ji,\n\n"
            f"Aapka payment due hai:\n"
            f"Total Amount: *₹{credit.amount:,.0f}*\n"
            f"Paid: ₹{credit.paid_amount:,.0f}\n"
            f"*Remaining: ₹{credit.remaining_amount():,.0f}*\n\n"
            f"Due Date: {credit.due_date.strftime('%d %B %Y')} (*{days_overdue} days overdue*)\n\n"
            f"Kripya jald se jald payment karein.\n"
            f"Dhanyawad! 🙏"
        )

        result = {'credit_id': credit.id, 'customer': credit.customer.name,
                  'remaining': credit.remaining_amount()}

        if customer_phone:
            result['whatsapp'] = _send_whatsapp(customer_phone, message)

        _log_notification(f"Payment Reminder: {credit.customer.name}", message, customer_phone)
        results.append(result)

    return results


def send_low_feed_alerts(threshold_days: int = 7) -> list:
    """Low feed stock alerts — N din ka stock bache to alert."""
    from .models import FeedInventory

    owner_phone = os.environ.get('FARM_OWNER_PHONE', '')
    results = []

    # Daily feed consumption (last 7 days average)
    from .models import FeedConsumption
    from django.db.models import Avg

    for feed in FeedInventory.objects.all():
        # Average daily consumption
        avg_daily = FeedConsumption.objects.filter(
            feed=feed,
            date__gte=date.today() - timedelta(days=7)
        ).aggregate(avg=Avg('quantity_consumed'))['avg'] or 0

        if avg_daily > 0:
            days_remaining = feed.quantity / float(avg_daily)
        else:
            days_remaining = 999  # Unknown

        if days_remaining <= threshold_days:
            message = (
                f"🐐 *Goat Farm Alert*\n\n"
                f"🌾 *Low Feed Stock Warning!*\n\n"
                f"Feed: *{feed.feed_name}*\n"
                f"Current Stock: *{feed.quantity} {feed.unit}*\n"
                f"Estimated Days Remaining: *{int(days_remaining)} days*\n\n"
                f"Kripya jald reorder karein!"
            )

            result = {
                'feed_id': feed.id,
                'feed_name': feed.feed_name,
                'quantity': feed.quantity,
                'days_remaining': round(days_remaining, 1)
            }
            if owner_phone:
                result['whatsapp'] = _send_whatsapp(owner_phone, message)

            _log_notification(f"Low Feed: {feed.feed_name}", message)
            results.append(result)

    return results


def send_daily_summary() -> dict:
    """Farm owner ko daily morning summary bhejo."""
    from .models import (Goat, MilkProduction, Sale, BreedingRecord,
                         VaccinationSchedule, Task)

    owner_phone = os.environ.get('FARM_OWNER_PHONE', '')
    today = date.today()

    total_milk = MilkProduction.objects.filter(date=today).aggregate(
        total=Sum('quantity'))['total'] or 0

    today_sales = Sale.objects.filter(date=today).aggregate(
        total=Sum('total_amount'))['total'] or 0

    upcoming_deliveries = BreedingRecord.objects.filter(
        expected_delivery_date=today, status__in=['P', 'C']
    ).count()

    due_vaccinations = VaccinationSchedule.objects.filter(
        due_date=today, completed=False
    ).count()

    pending_tasks = Task.objects.filter(status='P', due_date=today).count()

    message = (
        f"🌅 *Good Morning! Farm Daily Summary*\n"
        f"📅 {today.strftime('%d %B %Y, %A')}\n\n"
        f"🐐 Total Goats: *{Goat.objects.filter(status__in=['A', 'P']).count()}*\n"
        f"🍼 Milk Today: *{total_milk:.1f} Liters*\n"
        f"💰 Sales Today: *₹{float(today_sales):,.0f}*\n\n"
        f"⚠️ *Action Required:*\n"
        f"🍼 Deliveries Today: {upcoming_deliveries}\n"
        f"💉 Vaccinations Due: {due_vaccinations}\n"
        f"📋 Pending Tasks: {pending_tasks}\n\n"
        f"Have a productive day! 🌾"
    )

    result = {
        'summary': {
            'total_milk': float(total_milk),
            'today_sales': float(today_sales),
            'upcoming_deliveries': upcoming_deliveries,
            'due_vaccinations': due_vaccinations,
        }
    }

    if owner_phone:
        result['whatsapp'] = _send_whatsapp(owner_phone, message)

    _log_notification("Daily Farm Summary", message)
    return result
