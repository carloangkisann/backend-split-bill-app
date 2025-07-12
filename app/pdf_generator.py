from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from app.models import PersonSplitResult, ItemAssignment, Item
from typing import List
import io

def generate_split_pdf(
    results: List[PersonSplitResult],
    items: List[Item],
    session_id: str,
    total_payment: int,
    handling_fee: int,
    other_fee: int,
    discount: int,
    discount_plus: int
) -> bytes:
    buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    total_style = ParagraphStyle(name="TotalStyle", textColor=colors.red, fontSize=10)
    bold_style = ParagraphStyle(name="BoldStyle", fontSize=10, fontName="Helvetica-Bold")
    elements = []

    elements.append(Paragraph("Split Bill Summary", styles['Title']))
    elements.append(Paragraph(f"Session ID: {session_id}", styles['Normal']))
    elements.append(Spacer(1, 10))

    subtotal_sum = sum(p.total for p in results)
    total_discount = discount + discount_plus
    final_total = total_payment

    for person in results:
        elements.append(Paragraph(f"<b>{person.name}</b>", styles['Heading3']))
        table_data = [["Nama Item", "Qty", "Unit Price", "Subtotal (Rp)"]]
        subtotal = 0

        for item_assignment in person.items:
            index = item_assignment.item_index
            quantity = item_assignment.quantity
            item = items[index]
            item_subtotal = quantity * item.unit_price
            subtotal += item_subtotal
            table_data.append([
                item.name,
                str(quantity),
                f"Rp{item.unit_price:,}",
                f"Rp{item_subtotal:,}"
            ])

        prop_ratio = subtotal / subtotal_sum if subtotal_sum > 0 else 0
        handling_share = round(prop_ratio * handling_fee)
        other_share = round(prop_ratio * other_fee)
        discount_share = round(prop_ratio * total_discount)
        final_payment = subtotal + handling_share + other_share - discount_share

        table_data.append([
            Paragraph("<b>Biaya Penanganan</b>", bold_style), "", "", f"Rp{handling_share:,}"
        ])
        table_data.append([
            Paragraph("<b>Biaya Lainnya</b>", bold_style), "", "", f"Rp{other_share:,}"
        ])
        table_data.append([
            Paragraph("<b>Diskon Proporsional</b>", bold_style), "", "",
            Paragraph(f"<b>-Rp{discount_share:,}</b>", styles["Normal"])
        ])
        table_data.append([
            Paragraph("<b>Total Bayar</b>", bold_style), "", "",
            Paragraph(f"<b>Rp{final_payment:,}</b>", total_style)
        ])

        table = Table(table_data, hAlign='LEFT', colWidths=[230, 40, 80, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Total Biaya Penanganan: Rp{handling_fee:,}</b>", styles['Normal']))
    elements.append(Paragraph(f"<b>Total Biaya Lainnya: Rp{other_fee:,}</b>", styles['Normal']))
    elements.append(Paragraph(f"<b>Total Diskon: Rp{total_discount:,}</b>", styles['Normal']))
    elements.append(Spacer(1, 15))
    elements.append(Paragraph(f"<b>Total Pembayaran Akhir: Rp{total_payment:,}</b>", styles['Title']))

    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes