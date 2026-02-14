#!/usr/bin/env python3
"""
Automatically save HTML presentation as PDF to OneDrive
"""

import os
import subprocess
import sys
import time

def main():
    # Paths
    html_path = 'Polymarket_Investment_Presentation.html'
    pdf_path = r'C:\Users\Borat\OneDrive\Trading\Polymarket_Investment_Presentation.pdf'
    
    print("="*60)
    print("AUTOMATIC PDF SAVE TO ONEDRIVE")
    print("="*60)
    print(f"HTML: {html_path}")
    print(f"PDF: {pdf_path}")
    print()
    
    # Check if HTML exists
    if not os.path.exists(html_path):
        print("ERROR: HTML file not found")
        return False
    
    # Create OneDrive Trading folder if needed
    onedrive_dir = os.path.dirname(pdf_path)
    if not os.path.exists(onedrive_dir):
        os.makedirs(onedrive_dir)
        print(f"Created directory: {onedrive_dir}")
    
    # Try different methods
    methods = [
        ("Chrome", "chrome.exe"),
        ("Edge", "msedge.exe"),
        ("Brave", "brave.exe")
    ]
    
    for browser_name, browser_exe in methods:
        print(f"\nTrying {browser_name}...")
        
        # Check if browser is installed
        try:
            # Try to find browser path
            result = subprocess.run(['where', browser_exe], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"  {browser_name} not found in PATH")
                continue
                
            browser_path = result.stdout.strip().split('\n')[0]
            print(f"  Found: {browser_path}")
            
            # Prepare command
            html_abs = os.path.abspath(html_path).replace('\\', '/')
            url = f'file:///{html_abs}'
            
            cmd = [
                browser_path,
                '--headless',
                '--disable-gpu',
                f'--print-to-pdf={pdf_path}',
                url
            ]
            
            print(f"  Running: {' '.join(cmd[:3])} ...")
            
            # Run browser
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # Check if PDF was created
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"\n✅ SUCCESS! PDF created with {browser_name}")
                print(f"   Location: {pdf_path}")
                print(f"   Size: {size:,} bytes")
                return True
            else:
                print(f"  ❌ {browser_name} failed to create PDF")
                
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ {browser_name} timed out")
        except Exception as e:
            print(f"  ❌ {browser_name} error: {e}")
    
    # If all browsers fail, try a fallback
    print("\n" + "="*60)
    print("FALLBACK METHOD: Creating simple text-based PDF")
    print("="*60)
    
    try:
        # Create a simple text PDF using reportlab if available
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Paragraph
            
            print("Using reportlab to create PDF...")
            
            # Read HTML content
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract text content (simple extraction)
            import re
            # Remove HTML tags
            text_content = re.sub(r'<[^>]+>', ' ', html_content)
            # Remove multiple spaces
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Create PDF
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Add title
            title = Paragraph("Polymarket Quantitative Trading Strategy<br/>Investment Presentation", styles['Title'])
            story.append(title)
            
            # Add date
            date_text = Paragraph("February 10, 2026", styles['Normal'])
            story.append(date_text)
            
            story.append(Paragraph("<br/><br/>", styles['Normal']))
            
            # Add content (truncated for demo)
            lines = text_content.split('. ')
            for i, line in enumerate(lines[:50]):  # First 50 sentences
                if line.strip():
                    story.append(Paragraph(line.strip() + '.', styles['Normal']))
            
            doc.build(story)
            
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"\n✅ Created simple PDF with reportlab")
                print(f"   Location: {pdf_path}")
                print(f"   Size: {size:,} bytes")
                print(f"   Note: This is a text-only version")
                return True
                
        except ImportError:
            print("reportlab not available, creating text file instead...")
            
            # Create a simple text file as fallback
            txt_path = pdf_path.replace('.pdf', '.txt')
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple HTML to text conversion
            import re
            text = re.sub(r'<[^>]+>', ' ', content)
            text = re.sub(r'\s+', ' ', text).strip()
            
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write("POLYMARKET QUANTITATIVE TRADING STRATEGY\n")
                f.write("Investment Presentation\n")
                f.write("February 10, 2026\n")
                f.write("="*60 + "\n\n")
                f.write(text[:5000] + "...\n\n")
                f.write("[Full presentation available in HTML format]")
            
            print(f"\n⚠️ Created text file instead of PDF")
            print(f"   Location: {txt_path}")
            print(f"   For full presentation, open: {html_path}")
            
    except Exception as e:
        print(f"\n❌ All methods failed: {e}")
    
    return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("✅ PDF SAVED TO ONEDRIVE SUCCESSFULLY!")
        print("="*60)
        print("\nLocation: C:\\Users\\Borat\\OneDrive\\Trading\\Polymarket_Investment_Presentation.pdf")
        print("\nYou can now access it from:")
        print("1. File Explorer: OneDrive\\Trading\\")
        print("2. OneDrive web: https://onedrive.live.com")
        print("3. OneDrive mobile app")
    else:
        print("\n" + "="*60)
        print("❌ COULD NOT CREATE PDF AUTOMATICALLY")
        print("="*60)
        print("\nManual method required:")
        print("1. Open 'Polymarket_Investment_Presentation.html' in browser")
        print("2. Press Ctrl+P")
        print("3. Select 'Save as PDF'")
        print("4. Save to: OneDrive\\Trading\\")
        
    sys.exit(0 if success else 1)