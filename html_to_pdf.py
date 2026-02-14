#!/usr/bin/env python3
"""Convert HTML to PDF using WeasyPrint"""
from weasyprint import HTML, CSS
import os

try:
    print("Creating PDF from HTML...")
    
    # Convert HTML to PDF
    HTML('tariff_thesis_mobile.html').write_pdf(
        'tariff_investment_thesis_mobile.pdf',
        stylesheets=[]
    )
    
    print(f"✓ PDF created successfully!")
    print(f"  Size: {os.path.getsize('tariff_investment_thesis_mobile.pdf'):,} bytes")
    
    # Copy to OneDrive
    onedrive_path = os.path.expanduser("~/OneDrive/Trading")
    if os.path.exists(onedrive_path):
        import shutil
        shutil.copy("tariff_investment_thesis_mobile.pdf", onedrive_path)
        print(f"✓ Uploaded to OneDrive/Trading/")
    else:
        print(f"OneDrive path not found. PDF is in current directory.")
        
except Exception as e:
    print(f"Error: {e}")
    print("PDF creation failed, but HTML version is available.")
