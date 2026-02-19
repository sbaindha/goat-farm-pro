"""
🐐 Goat Farm Invoice Generator — v6.0
Batch 1: Auto Invoice & Receipt Generator

ReportLab se professional PDF invoices generate karta hai.
Features:
- Sale invoice with GST
- Payment receipt for credits
- Auto invoice numbering (INV-2026-001)
- Farm letterhead (name, address, GST)
- WhatsApp-shareable download link
"""

import io
import os
from datetime import date, datetime
from django.conf import settings
from django.http import HttpResponse

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm, cm
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable, Image
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ==================== COLORS ====================
GREEN_DARK = HexColor('#1B5E20') if REPORTLAB_AVAILABLE else None
GREEN = HexColor('#2E7D32') if REPORTLAB_AVAILABLE else None
GREEN_LIGHT = HexColor('#E8F5E9') if REPORTLAB_AVAILABLE else None
GRAY = HexColor('#424242') if REPORTLAB_AVAILABLE else None
GRAY_LIGHT = HexColor('#F5F5F5') if REPORTLAB_AVAILABLE else None
AMBER = HexColor('#F57F17') if REPORTLAB_AVAILABLE else None


# ==================== GST RATES ====================
GST_RATES = {
    'G': 0.0,   # Live goat — 0% GST (exempted)
    'M': 5.0,   # Milk — 5% GST
    'MN': 0.0,  # Manure — 0% GST
    'O': 18.0,  # Other services — 18% GST
}
GST_DESCRIPTIONS = {
    'G': 'Live Animal (GST Exempt)',
    'M': 'Milk Products (GST @5%)',
    'MN': 'Agricultural Product (GST Exempt)',
    'O': 'Services (GST @18%)',
}


# ==================== INVOICE NUMBER ====================
def get_next_invoice_number():
    """Auto-increment invoice number: INV-2026-001"""
    from .models import Sale
    year = date.today().year
    # Count this year's invoices
    count = Sale.objects.filter(
        date__year=year,
        invoice_number__isnull=False
    ).count()
    return f"INV-{year}-{str(count + 1).zfill(3)}"


# ==================== FARM SETTINGS ====================
def get_farm_settings():
    """Farm ka naam aur details — settings.py ya default."""
    return {
        'name': getattr(settings, 'FARM_NAME', 'My Goat Farm'),
        'address': getattr(settings, 'FARM_ADDRESS', 'Village, District, State - PIN'),
        'phone': getattr(settings, 'FARM_PHONE', '+91 98765 43210'),
        'email': getattr(settings, 'FARM_EMAIL', 'farm@example.com'),
        'gst_number': getattr(settings, 'FARM_GST', 'GST Registration Number'),
        'bank_name': getattr(settings, 'FARM_BANK_NAME', 'Bank Name'),
        'account_number': getattr(settings, 'FARM_ACCOUNT_NO', 'Account Number'),
        'ifsc': getattr(settings, 'FARM_IFSC', 'IFSC Code'),
    }


# ==================== MAIN PDF GENERATOR ====================
def generate_sale_invoice_pdf(sale) -> bytes:
    """
    Sale object se PDF invoice generate karo.
    Returns: PDF bytes

    Usage:
        pdf_bytes = generate_sale_invoice_pdf(sale)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="invoice_{sale.invoice_number}.pdf"'
        return response
    """
    if not REPORTLAB_AVAILABLE:
        raise ImportError("ReportLab install nahi hai. Run: pip install reportlab")

    farm = get_farm_settings()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm
    )

    styles = getSampleStyleSheet()
    elements = []

    # ===== HEADER: Farm Name + Invoice Title =====
    header_data = [
        [
            Paragraph(f"<b><font size='18' color='#1B5E20'>🐐 {farm['name']}</font></b>", styles['Normal']),
            Paragraph(f"<b><font size='16' color='#2E7D32'>TAX INVOICE</font></b>", styles['Normal']),
        ],
        [
            Paragraph(f"<font size='9' color='#424242'>{farm['address']}</font>", styles['Normal']),
            Paragraph(f"<font size='9' color='#424242'>Invoice No: <b>{sale.invoice_number or 'N/A'}</b></font>", styles['Normal']),
        ],
        [
            Paragraph(f"<font size='9' color='#424242'>📞 {farm['phone']} | ✉ {farm['email']}</font>", styles['Normal']),
            Paragraph(f"<font size='9' color='#424242'>Date: <b>{sale.date.strftime('%d %B %Y')}</b></font>", styles['Normal']),
        ],
        [
            Paragraph(f"<font size='9' color='#424242'>GSTIN: {farm['gst_number']}</font>", styles['Normal']),
            Paragraph(f"<font size='9' color='#424242'>Due Date: <b>{sale.date.strftime('%d %B %Y')}</b></font>", styles['Normal']),
        ],
    ]

    header_table = Table(header_data, colWidths=[110*mm, 65*mm])
    header_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, -1), (-1, -1), 1, GREEN_DARK),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 8*mm))

    # ===== BILL TO =====
    bill_data = [
        [
            Paragraph("<b><font size='10' color='#1B5E20'>BILL TO:</font></b>", styles['Normal']),
            Paragraph("<b><font size='10' color='#1B5E20'>PAYMENT INFO:</font></b>", styles['Normal']),
        ],
        [
            Paragraph(f"<b>{sale.buyer_name}</b>", styles['Normal']),
            Paragraph(f"Bank: {farm['bank_name']}", styles['Normal']),
        ],
        [
            Paragraph(f"📞 {sale.buyer_contact or 'N/A'}", styles['Normal']),
            Paragraph(f"A/C: {farm['account_number']}", styles['Normal']),
        ],
        [
            Paragraph(f"Payment: <b>{sale.get_payment_status_display()}</b>", styles['Normal']),
            Paragraph(f"IFSC: {farm['ifsc']}", styles['Normal']),
        ],
    ]

    bill_table = Table(bill_data, colWidths=[87.5*mm, 87.5*mm])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN_LIGHT),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, GRAY),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, GRAY),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 6*mm))

    # ===== ITEMS TABLE =====
    gst_rate = GST_RATES.get(sale.sale_type, 0)
    gst_desc = GST_DESCRIPTIONS.get(sale.sale_type, '')
    base_amount = round(float(sale.total_amount) / (1 + gst_rate / 100), 2) if gst_rate > 0 else float(sale.total_amount)
    gst_amount = round(float(sale.total_amount) - base_amount, 2)

    item_name = f"{sale.get_sale_type_display()}"
    if sale.goat:
        item_name += f" — {sale.goat.name} ({sale.goat.tag_number})"

    item_header = ['#', 'Description', 'Qty', 'Unit', 'Rate (₹)', 'Amount (₹)']
    item_rows = [
        ['1', item_name, str(sale.quantity), sale.unit,
         f"₹{sale.price_per_unit:,.2f}", f"₹{base_amount:,.2f}"],
    ]

    items_data = [item_header] + item_rows + [
        ['', '', '', '', 'Sub Total:', f"₹{base_amount:,.2f}"],
        ['', '', '', '', f'GST ({gst_rate:.0f}%):', f"₹{gst_amount:,.2f}"],
        ['', '', '', '', '<b>TOTAL:</b>', f"<b>₹{sale.total_amount:,.2f}</b>"],
    ]

    # Convert last rows to Paragraph for bold
    for i in range(len(item_rows) + 1, len(items_data)):
        items_data[i][4] = Paragraph(items_data[i][4], styles['Normal'])
        items_data[i][5] = Paragraph(items_data[i][5], styles['Normal'])

    items_table = Table(items_data, colWidths=[10*mm, 65*mm, 20*mm, 20*mm, 30*mm, 30*mm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), GREEN_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, len(item_rows)), [white, GRAY_LIGHT]),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, len(item_rows)), 0.5, GRAY),
        ('LINEABOVE', (4, len(item_rows) + 1), (-1, -1), 0.5, GRAY),
        ('BACKGROUND', (0, -1), (-1, -1), GREEN_LIGHT),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 6*mm))

    # ===== GST NOTE =====
    if gst_desc:
        elements.append(Paragraph(
            f"<i><font size='8' color='#666666'>* {gst_desc}</font></i>",
            styles['Normal']
        ))
        elements.append(Spacer(1, 4*mm))

    # ===== AMOUNT IN WORDS =====
    elements.append(Paragraph(
        f"<b>Amount in Words:</b> <i>{amount_to_words(float(sale.total_amount))} Rupees Only</i>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 10*mm))

    # ===== SIGNATURE =====
    sig_data = [
        [
            Paragraph("<font size='9' color='#424242'>Terms & Conditions:\n• Payment due on delivery\n• All disputes subject to local jurisdiction\n• Thank you for your business!</font>", styles['Normal']),
            Paragraph(f"<b>For {farm['name']}</b>", styles['Normal']),
        ],
        [
            '',
            Paragraph("<br/><br/><br/>_________________________<br/>Authorized Signatory", styles['Normal']),
        ]
    ]
    sig_table = Table(sig_data, colWidths=[100*mm, 75*mm])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(sig_table)
    elements.append(HRFlowable(width="100%", thickness=1, color=GREEN_DARK))
    elements.append(Spacer(1, 3*mm))
    elements.append(Paragraph(
        f"<font size='8' color='#666666'>Generated by Goat Farm Management System v6.0 | {datetime.now().strftime('%d %b %Y %H:%M')}</font>",
        ParagraphStyle('footer', parent=styles['Normal'], alignment=TA_CENTER)
    ))

    doc.build(elements)
    return buffer.getvalue()


# ==================== AMOUNT IN WORDS ====================
def amount_to_words(amount: float) -> str:
    """Simple amount to words converter."""
    ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
            'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen',
            'Seventeen', 'Eighteen', 'Nineteen']
    tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

    def convert_below_100(n):
        if n < 20:
            return ones[n]
        return tens[n // 10] + (f' {ones[n % 10]}' if n % 10 else '')

    def convert_below_1000(n):
        if n < 100:
            return convert_below_100(n)
        return ones[n // 100] + ' Hundred' + (f' {convert_below_100(n % 100)}' if n % 100 else '')

    n = int(amount)
    if n == 0:
        return 'Zero'
    if n >= 10000000:
        return convert_below_1000(n // 10000000) + ' Crore ' + amount_to_words(n % 10000000)
    if n >= 100000:
        return convert_below_1000(n // 100000) + ' Lakh ' + amount_to_words(n % 100000)
    if n >= 1000:
        return convert_below_1000(n // 1000) + ' Thousand ' + amount_to_words(n % 1000)
    return convert_below_1000(n)


# ==================== HTTP RESPONSE HELPER ====================
def invoice_pdf_response(sale):
    """Direct HTTP response return karo."""
    pdf_bytes = generate_sale_invoice_pdf(sale)
    filename = f"invoice_{sale.invoice_number or sale.id}.pdf"
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response
