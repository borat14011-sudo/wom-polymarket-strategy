#!/usr/bin/env python3
"""
Create HTML version of the presentation that can be saved as PDF from browser
"""

import os
import markdown
from datetime import datetime

def create_html_presentation():
    """Create HTML version of the presentation"""
    
    input_file = "Polymarket_Investment_Presentation.md"
    output_file = "Polymarket_Investment_Presentation.html"
    
    if not os.path.exists(input_file):
        print(f"[ERROR] Input file not found: {input_file}")
        return False
    
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convert markdown to HTML
    print("Converting markdown to HTML...")
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    # Create full HTML document with print-friendly styling
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket Quantitative Trading Strategy - Investment Presentation</title>
    <style>
        @media print {{
            @page {{
                size: A4;
                margin: 1.5cm;
            }}
            body {{
                font-size: 12pt;
                line-height: 1.4;
            }}
            h1 {{ font-size: 24pt; }}
            h2 {{ font-size: 18pt; }}
            h3 {{ font-size: 14pt; }}
            .no-print {{ display: none; }}
            .page-break {{ page-break-after: always; }}
        }}
        
        @media screen {{
            body {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .content {{
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
            }}
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        .header {{
            text-align: center;
            padding: 30px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin: 0;
            padding: 0;
        }}
        
        .header h2 {{
            font-size: 1.5em;
            margin: 10px 0 0 0;
            font-weight: 300;
        }}
        
        .header .date {{
            font-size: 1.1em;
            margin-top: 15px;
            opacity: 0.9;
        }}
        
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        h1 {{ border-bottom: 3px solid #3498db; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 3px rgba(0,0,0,0.1);
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
            padding: 12px 15px;
            text-align: left;
        }}
        
        td {{
            padding: 10px 15px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        
        tr:hover {{
            background-color: #f1f8ff;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
        }}
        
        pre {{
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        .highlight {{
            background-color: #fff3cd;
            padding: 15px;
            border-left: 4px solid #ffc107;
            margin: 20px 0;
            border-radius: 0 5px 5px 0;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            font-size: 0.9em;
            color: #7f8c8d;
            border-top: 1px solid #ecf0f1;
        }}
        
        .print-button {{
            position: fixed;
            top: 20px;
            right: 20px;
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            z-index: 1000;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }}
        
        .print-button:hover {{
            background-color: #2980b9;
        }}
        
        .watermark {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            opacity: 0.1;
            font-size: 48px;
            color: #3498db;
            pointer-events: none;
            z-index: -1;
        }}
    </style>
</head>
<body>
    <button class="print-button no-print" onclick="window.print()">🖨️ Print/Save as PDF</button>
    
    <div class="content">
        <div class="header">
            <h1>Polymarket Quantitative Trading Strategy</h1>
            <h2>Investment Presentation</h2>
            <div class="date">February 10, 2026</div>
        </div>
        
        {html_content}
        
        <div class="footer">
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Confidential:</strong> For Investor Use Only</p>
            <p>OpenClaw AI Assistant | Quantitative Trading Research</p>
        </div>
    </div>
    
    <div class="watermark">CONFIDENTIAL</div>
    
    <script>
        // Add page breaks for printing
        document.addEventListener('DOMContentLoaded', function() {{
            const h2Elements = document.querySelectorAll('h2');
            h2Elements.forEach((h2, index) => {{
                if (index > 0) {{
                    const pageBreak = document.createElement('div');
                    pageBreak.className = 'page-break';
                    h2.parentNode.insertBefore(pageBreak, h2);
                }}
            }});
        }});
    </script>
</body>
</html>"""
    
    # Write HTML file
    print(f"Writing HTML to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)
    
    print(f"[SUCCESS] HTML presentation created: {output_file}")
    print(f"File size: {os.path.getsize(output_file):,} bytes")
    
    # Create instructions file
    instructions = f"""# INSTRUCTIONS TO SAVE AS PDF

## Presentation File:
- **HTML File:** {output_file}
- **Source:** Polymarket_Investment_Presentation.md
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Steps to Save as PDF:

### Method 1: Browser Print to PDF
1. Open `{output_file}` in Chrome/Edge/Firefox
2. Press `Ctrl+P` (Windows) or `Cmd+P` (Mac)
3. Select "Save as PDF" as destination
4. Click "Save"
5. Save to: `OneDrive/Trading/Polymarket_Investment_Presentation.pdf`

### Method 2: Use Print Button
1. Open `{output_file}` in browser
2. Click the "🖨️ Print/Save as PDF" button (top-right)
3. Select "Save as PDF"
4. Save to OneDrive

## OneDrive Path Recommendation:
```
OneDrive/Trading/Polymarket_Investment_Presentation.pdf
```

## Presentation Contents:
- Executive Summary & Investment Thesis
- Market Analysis & Fee Structure
- 6 Novel Trading Strategies
- Risk Management & Position Sizing
- Expected Returns & Monte Carlo Simulations
- Implementation Plan

## Notes:
- This is the "hardcore presentation" requested on Feb 13, 2026
- Contains quantitative analysis of Polymarket trading strategies
- Includes fee-aware edge calculations and risk management
"""
    
    with open("SAVE_TO_ONEDRIVE_INSTRUCTIONS.txt", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print(f"Instructions saved to: SAVE_TO_ONEDRIVE_INSTRUCTIONS.txt")
    
    return True

def main():
    print("="*60)
    print("CREATE PRESENTATION FOR ONEDRIVE")
    print("="*60)
    
    success = create_html_presentation()
    
    if success:
        print("\n" + "="*60)
        print("PRESENTATION READY FOR ONEDRIVE")
        print("="*60)
        print("\nNext steps:")
        print("1. Open 'Polymarket_Investment_Presentation.html' in browser")
        print("2. Click the 'Print/Save as PDF' button (top-right)")
        print("3. Save as PDF to: OneDrive/Trading/")
        print("4. File name: Polymarket_Investment_Presentation.pdf")
        print("\nOr follow instructions in: SAVE_TO_ONEDRIVE_INSTRUCTIONS.txt")
    else:
        print("\n[ERROR] Failed to create presentation")

if __name__ == "__main__":
    main()