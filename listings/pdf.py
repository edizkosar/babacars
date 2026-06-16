"""
İlan föyü (PDF) üretimi — reportlab ile.
Markasız, kurumsal görünümlü bir araç bilgi föyü oluşturur.
"""
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT

INK = colors.HexColor('#111111')
GOLD = colors.HexColor('#C9A84C')
GREY = colors.HexColor('#6B7280')
LIGHT = colors.HexColor('#F5EFE6')
LINE = colors.HexColor('#E5DDD0')


def _fmt_price(value, currency='TRY'):
    try:
        return f"{value:,.0f} {currency}".replace(',', '.')
    except Exception:
        return f"{value} {currency}"


def build_listing_pdf(listing) -> bytes:
    """Verilen ilan için PDF baytlarını döndürür."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title=listing.title, author='BabaCars',
    )

    styles = getSampleStyleSheet()
    h_brand = ParagraphStyle('brand', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=20, textColor=INK, leading=22)
    h_title = ParagraphStyle('title', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=16, textColor=INK, leading=20, spaceBefore=4)
    p_meta = ParagraphStyle('meta', parent=styles['Normal'], fontName='Helvetica',
                            fontSize=9.5, textColor=GREY, leading=14)
    p_price = ParagraphStyle('price', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=22, textColor=GOLD, alignment=TA_RIGHT, leading=24)
    p_label = ParagraphStyle('label', parent=styles['Normal'], fontName='Helvetica-Bold',
                             fontSize=8, textColor=GREY, leading=11)
    p_section = ParagraphStyle('section', parent=styles['Normal'], fontName='Helvetica-Bold',
                               fontSize=11, textColor=INK, leading=14, spaceBefore=2)
    p_body = ParagraphStyle('body', parent=styles['Normal'], fontName='Helvetica',
                            fontSize=9.5, textColor=INK, leading=15)
    p_foot = ParagraphStyle('foot', parent=styles['Normal'], fontName='Helvetica',
                            fontSize=8, textColor=GREY, alignment=TA_CENTER, leading=11)

    elems = []

    # ── Başlık satırı: marka + tarih ──
    from django.utils import timezone
    head = Table([[
        Paragraph('Baba<font color="#C9A84C">Cars</font>', h_brand),
        Paragraph(f"Föy Tarihi<br/>{timezone.now():%d.%m.%Y %H:%M}",
                  ParagraphStyle('d', parent=p_meta, alignment=TA_RIGHT)),
    ]], colWidths=[None, 45 * mm])
    head.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elems.append(head)
    elems.append(Spacer(1, 4))
    elems.append(HRFlowable(width='100%', thickness=2, color=GOLD))
    elems.append(Spacer(1, 10))

    # ── Kapak fotoğrafı ──
    cover = listing.photos.first()
    if cover:
        try:
            img = Image(cover.image.path, width=174 * mm, height=92 * mm)
            img.hAlign = 'CENTER'
            elems.append(img)
            elems.append(Spacer(1, 10))
        except Exception:
            pass

    # ── İlan tipi rozeti + başlık + fiyat ──
    tip = 'KİRALIK' if listing.listing_type == 'rental' else 'SATILIK'
    title_block = Table([[
        Paragraph(f'<font size=8 color="#C9A84C"><b>{tip}</b></font><br/>'
                  f'<font size=16><b>{listing.title}</b></font>', h_title),
        Paragraph(_fmt_price(listing.price, listing.currency)
                  + ('<br/><font size=9 color="#6B7280">/ gün</font>' if listing.listing_type == 'rental' else ''),
                  p_price),
    ]], colWidths=[None, 60 * mm])
    title_block.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elems.append(title_block)
    elems.append(Spacer(1, 4))
    elems.append(Paragraph(
        f"{listing.city}{(' / ' + listing.district) if listing.district else ''}", p_meta))
    elems.append(Spacer(1, 12))

    # ── Teknik özellikler tablosu ──
    v = getattr(listing, 'vehicle', None)
    if v:
        def row(label, value):
            return [Paragraph(label, p_label), Paragraph(str(value), p_body)]

        specs = [
            row('MARKA', v.make), row('MODEL', v.model),
            row('YIL', v.year), row('KİLOMETRE', f"{v.mileage:,} km".replace(',', '.')),
            row('YAKIT', v.get_fuel_type_display()), row('VİTES', v.get_transmission_display()),
            row('KASA TİPİ', v.get_body_type_display()), row('RENK', v.color),
        ]
        if v.engine_cc:
            specs.append(row('MOTOR HACMİ', f"{v.engine_cc} cc"))
        if v.horsepower:
            specs.append(row('GÜÇ', f"{v.horsepower} HP"))
        specs.append(row('KAPI / KOLTUK', f"{v.num_doors} / {v.num_seats}"))
        specs.append(row('HASAR KAYDI', 'Var' if v.has_damage_record else 'Yok'))

        # İki sütunlu yerleşim için satırları ikişerli grupla
        elems.append(Paragraph('Teknik Özellikler', p_section))
        elems.append(Spacer(1, 6))
        grid_data = []
        for i in range(0, len(specs), 2):
            left = specs[i]
            right = specs[i + 1] if i + 1 < len(specs) else [Paragraph('', p_label), Paragraph('', p_body)]
            grid_data.append([left[0], left[1], right[0], right[1]])

        tbl = Table(grid_data, colWidths=[28 * mm, 56 * mm, 28 * mm, 56 * mm])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, LINE),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))
        elems.append(tbl)
        elems.append(Spacer(1, 14))

    # ── Açıklama ──
    if listing.description:
        elems.append(Paragraph('Açıklama', p_section))
        elems.append(Spacer(1, 4))
        desc = listing.description.replace('\n', '<br/>')
        elems.append(Paragraph(desc, p_body))
        elems.append(Spacer(1, 12))

    # ── Satıcı kutusu ──
    seller = listing.seller
    seller_tbl = Table([[
        Paragraph('SATICI', p_label),
        Paragraph(getattr(seller, 'full_name', '') or seller.email, p_body),
    ], [
        Paragraph('İLETİŞİM', p_label),
        Paragraph(seller.phone or seller.email, p_body),
    ]], colWidths=[28 * mm, None])
    seller_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, LINE),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elems.append(seller_tbl)
    elems.append(Spacer(1, 16))

    # ── Alt bilgi ──
    elems.append(HRFlowable(width='100%', thickness=0.5, color=LINE))
    elems.append(Spacer(1, 4))
    elems.append(Paragraph(
        'Bu föy BabaCars platformu üzerinden otomatik oluşturulmuştur. '
        'Bilgiler ilan sahibinin beyanına dayanır.', p_foot))

    doc.build(elems)
    pdf = buf.getvalue()
    buf.close()
    return pdf
