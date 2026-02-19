"""
🐐 QR Code Utility — v6.0
Batch 2: QR Code per Goat (Tag Scanning)

Features:
- Per-goat QR code generate karo
- Batch PDF with all goats' QR codes
- Ear tag print template
"""

import io
import os

try:
    import qrcode
    from qrcode.image.pil import PilImage
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


def generate_qr_code(goat_tag: str, base_url: str = "http://localhost:8000") -> bytes:
    """
    Ek goat ka QR code generate karo.
    Returns: PNG image bytes

    QR code content: {base_url}/goat/scan/{tag_number}/
    """
    if not QR_AVAILABLE:
        raise ImportError("qrcode install nahi hai. Run: pip install qrcode[pil]")

    scan_url = f"{base_url}/goat/scan/{goat_tag}/"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(scan_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1B5E20", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return buffer.getvalue()


def generate_goat_tag_image(goat, base_url: str = "http://localhost:8000") -> bytes:
    """
    Ear tag style image: QR code + goat info
    Returns: PNG bytes (5cm × 5cm at 150dpi = ~295px × 295px)
    """
    if not QR_AVAILABLE or not PIL_AVAILABLE:
        raise ImportError("qrcode aur Pillow dono install karein.")

    # QR code banana
    qr_bytes = generate_qr_code(goat.tag_number, base_url)
    qr_img = Image.open(io.BytesIO(qr_bytes)).resize((180, 180))

    # Canvas
    canvas = Image.new('RGB', (300, 320), 'white')
    draw = ImageDraw.Draw(canvas)

    # Green header bar
    draw.rectangle([0, 0, 300, 40], fill='#1B5E20')

    # Farm name in header (basic font)
    draw.text((10, 10), "GOAT FARM", fill='white')

    # QR code paste karo
    canvas.paste(qr_img, (60, 50))

    # Goat info below QR
    draw.text((10, 240), f"Tag: {goat.tag_number}", fill='#1B5E20')
    draw.text((10, 260), f"Name: {goat.name}", fill='#424242')
    draw.text((10, 280), f"Breed: {goat.breed}", fill='#424242')
    draw.text((10, 300), f"Gender: {'Male' if goat.gender == 'M' else 'Female'}", fill='#424242')

    # Border
    draw.rectangle([0, 0, 299, 319], outline='#1B5E20', width=3)

    buffer = io.BytesIO()
    canvas.save(buffer, format='PNG', dpi=(150, 150))
    return buffer.getvalue()


def generate_batch_qr_pdf(goats, base_url: str = "http://localhost:8000") -> bytes:
    """
    Sab goats ke QR codes ek PDF mein.
    Uses ReportLab for PDF generation.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import mm, cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableRow, Image as RLImage, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.colors import HexColor
        import reportlab
    except ImportError:
        raise ImportError("ReportLab install karein: pip install reportlab")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=10*mm, leftMargin=10*mm,
                            topMargin=15*mm, bottomMargin=10*mm)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(
        "<b><font size='14' color='#1B5E20'>🐐 Goat QR Code Tags — Print Sheet</font></b>",
        styles['Normal']
    ))
    elements.append(Spacer(1, 5*mm))

    # 4 QR codes per row
    row_data = []
    current_row = []

    for goat in goats:
        try:
            qr_bytes = generate_qr_code(goat.tag_number, base_url)
            qr_buf = io.BytesIO(qr_bytes)
            qr_img = RLImage(qr_buf, width=40*mm, height=40*mm)

            cell_para = [
                qr_img,
                Paragraph(f"<b>{goat.tag_number}</b>", styles['Normal']),
                Paragraph(f"{goat.name}", styles['Normal']),
                Paragraph(f"{goat.breed}", styles['Normal']),
            ]
            current_row.append(cell_para)

            if len(current_row) == 4:
                row_data.append(current_row)
                current_row = []
        except Exception:
            pass

    if current_row:
        # Pad empty cells
        while len(current_row) < 4:
            current_row.append([''])
        row_data.append(current_row)

    if row_data:
        from reportlab.platypus import Table as RLTable
        from reportlab.platypus import TableStyle
        from reportlab.lib.colors import white

        table = RLTable(row_data, colWidths=[45*mm, 45*mm, 45*mm, 45*mm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(table)

    doc.build(elements)
    return buffer.getvalue()
