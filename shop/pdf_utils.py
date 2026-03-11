"""
Generate a specification PDF for a product (descriptive document with details).
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT

from django.core.files import File
from .models import Product


def build_product_specification_pdf(product: Product) -> io.BytesIO:
    """Build a PDF with product name, description, specifications and other details. Returns a BytesIO buffer."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ProductTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        spaceBefore=14,
        spaceAfter=6,
    )
    body_style = styles['Normal']

    story = []

    # Title
    story.append(Paragraph(product.name, title_style))
    story.append(Spacer(1, 0.5*cm))

    # Summary table: Category, Price, Stock, Supplier, Delivery
    summary_data = [
        ['Category', product.category.name],
        ['Price', f'€{product.price}'],
        ['Stock', str(product.stock)],
    ]
    if product.supplier:
        summary_data.append(['Supplier', product.supplier.name])
    if product.delivery_method:
        summary_data.append(['Delivery', f"{product.delivery_method.name} (€{product.delivery_method.cost})"])
    t = Table(summary_data, colWidths=[4*cm, 12*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.8*cm))

    # Description
    story.append(Paragraph('<b>Description</b>', heading_style))
    desc_text = product.description.replace('\n', '<br/>')
    story.append(Paragraph(desc_text, body_style))
    story.append(Spacer(1, 0.5*cm))

    # Specifications / technical details
    story.append(Paragraph('<b>Specifications / Technical details</b>', heading_style))
    spec_text = product.specifications.replace('\n', '<br/>')
    story.append(Paragraph(spec_text, body_style))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_and_attach_pdf(product: Product) -> bool:
    """
    Generate a specification PDF for the product and set it as descriptive_pdf.
    Returns True if successful.
    """
    buffer = build_product_specification_pdf(product)
    filename = f"specifications-{product.slug}.pdf"
    product.descriptive_pdf.save(filename, File(buffer), save=True)
    return True
