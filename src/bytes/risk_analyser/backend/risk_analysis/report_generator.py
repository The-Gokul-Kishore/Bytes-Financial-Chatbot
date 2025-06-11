from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os

def generate_pdf_report(filename, extracted, quantitative, qualitative):
    output_path = os.path.join("uploads", "Risk_Report.pdf")
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "📄 Risk Analysis Report")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Company File: {filename}")

    # Section: Quantitative Risk
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 120, "📊 Quantitative Risk Overview:")
    c.setFont("Helvetica", 12)
    c.drawString(70, height - 140, f"Risk Score: {quantitative.get('score', 'N/A')}")
    c.drawString(70, height - 160, f"Risk Level: {quantitative.get('level', 'N/A')}")

    # Section: Qualitative Risk
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "🧠 Qualitative Analysis Summary:")
    text = c.beginText(70, height - 220)
    text.setFont("Helvetica", 11)
    for line in qualitative.split('\n'):
        text.textLine(line.strip())
    c.drawText(text)

    # Section: KPI Table
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 340, "📌 Key Financial Indicators:")

    kpis = extracted.get('kpis', {})
    data = [["Metric", "Value"]]
    for k, v in kpis.items():
        data.append([k.replace("_", " ").title(), str(v)])

    table = Table(data, colWidths=[200, 200])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold')
    ]))

    table.wrapOn(c, 50, height - 500)
    table.drawOn(c, 50, height - 500)

    c.save()
    return output_path
