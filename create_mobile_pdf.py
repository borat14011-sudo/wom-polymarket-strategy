#!/usr/bin/env python3
"""
Generate mobile-friendly PDF from Tariff Investment Thesis
Optimized for phone reading
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def create_pdf():
    # Create PDF optimized for mobile (taller format)
    doc = SimpleDocTemplate(
        "tariff_investment_thesis_mobile.pdf",
        pagesize=(360, 640),  # Mobile portrait size
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )
    
    # Container for elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'MobileTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        leading=20
    )
    
    heading_style = ParagraphStyle(
        'MobileHeading',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=8,
        spaceBefore=12,
        leading=16
    )
    
    subheading_style = ParagraphStyle(
        'MobileSubheading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#444444'),
        spaceAfter=6,
        spaceBefore=8,
        leading=14
    )
    
    body_style = ParagraphStyle(
        'MobileBody',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        spaceAfter=8
    )
    
    highlight_style = ParagraphStyle(
        'MobileHighlight',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#d9534f'),
        spaceAfter=8
    )
    
    # Title
    elements.append(Paragraph("TARIFF REVENUE", title_style))
    elements.append(Paragraph("$200-500B Investment Thesis", title_style))
    elements.append(Spacer(1, 8))
    
    # Quick Stats Box
    stats_data = [
        ['BET', 'YES at 11%'],
        ['INVESTMENT', '$2.50'],
        ['EXPECTED RETURN', '15.4% (17 days)'],
        ['ANNUALIZED', '2,051%'],
        ['RESOLUTION', 'Feb 27, 2026'],
    ]
    
    stats_table = Table(stats_data, colWidths=[130, 170])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 12))
    
    # Executive Summary
    elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))
    elements.append(Paragraph(
        "Market prices 11% chance of $200-500B tariff revenue. "
        "True probability is ~35% due to already-announced tariffs effective March 12. "
        "This creates a 24 percentage point edge.",
        body_style
    ))
    elements.append(Spacer(1, 8))
    
    # The Bet Section
    elements.append(Paragraph("THE BET", heading_style))
    elements.append(Paragraph(
        "The market is using linear extrapolation from January data ($100B annualized). "
        "It ignores the March 12 tariff implementation that was already announced.",
        body_style
    ))
    elements.append(Spacer(1, 4))
    
    elements.append(Paragraph("Why 35% is realistic:", subheading_style))
    bullet_points = [
        "• Current: $100B/year run rate",
        "• + Steel/aluminum tariffs: +$35B",
        "• + Reciprocal tariffs: +$80B",
        "• + China escalation: +$50B",
        "= $265B potential revenue"
    ]
    for point in bullet_points:
        elements.append(Paragraph(point, body_style))
    elements.append(Spacer(1, 8))
    
    # Math Section
    elements.append(Paragraph("THE MATH", heading_style))
    elements.append(Paragraph("Expected Value Calculation:", subheading_style))
    
    math_text = """
    <b>If Win (35% prob):</b> +624% return<br/>
    <b>If Lose (65% prob):</b> -97% return<br/>
    <b>Expected Value:</b> (0.35 × 6.24) + (0.65 × -0.97) = <b>+15.4%</b>
    """
    elements.append(Paragraph(math_text, body_style))
    elements.append(Spacer(1, 8))
    
    # Risk Section
    elements.append(Paragraph("KEY RISKS", heading_style))
    risks = [
        ("Trade Deal", "25%", "Trump announces deal before Feb 27"),
        ("Delay", "20%", "Implementation pushed past March 12"),
        ("Dispute", "10%", "Revenue calculation disagreement"),
    ]
    
    for risk, prob, desc in risks:
        elements.append(Paragraph(f"<b>{risk}</b> ({prob}): {desc}", body_style))
    elements.append(Spacer(1, 8))
    
    # Bottom Line
    elements.append(Paragraph("BOTTOM LINE", heading_style))
    elements.append(Paragraph(
        "This is a highly asymmetric opportunity. Market sees 11% chance, "
        "but policy trajectory suggests 35%+. Rapid 17-day resolution means "
        "fast capital turnover. Best risk-adjusted opportunity in current market.",
        highlight_style
    ))
    elements.append(Spacer(1, 12))
    
    # Footer
    elements.append(Paragraph("—", ParagraphStyle('center', alignment=TA_CENTER)))
    elements.append(Paragraph(
        "Analysis: Feb 10, 2026 | Full thesis in OneDrive/Trading/",
        ParagraphStyle('footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(elements)
    print("✓ PDF created: tariff_investment_thesis_mobile.pdf")
    print(f"  Size: {os.path.getsize('tariff_investment_thesis_mobile.pdf'):,} bytes")
    return True

if __name__ == "__main__":
    import os
    try:
        success = create_pdf()
        if success:
            # Copy to OneDrive
            onedrive_path = os.path.expanduser("~/OneDrive/Trading")
            if os.path.exists(onedrive_path):
                import shutil
                shutil.copy("tariff_investment_thesis_mobile.pdf", onedrive_path)
                print(f"✓ Uploaded to OneDrive/Trading/")
    except ImportError as e:
        print(f"Missing library: {e}")
        print("Install with: pip install reportlab")
