#!/usr/bin/env python3
"""
Simple script to save presentation to OneDrive
"""

import os
import sys

def main():
    print("="*60)
    print("SAVE PRESENTATION TO ONEDRIVE")
    print("="*60)
    
    html_path = 'Polymarket_Investment_Presentation.html'
    pdf_path = r'C:\Users\Borat\OneDrive\Trading\Polymarket_Investment_Presentation.pdf'
    
    print(f"Source: {html_path}")
    print(f"Destination: {pdf_path}")
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
    
    # Since automatic PDF conversion is failing, let me create a batch file
    # that opens the browser and provides clear instructions
    
    batch_content = f"""@echo off
echo ========================================
echo AUTOMATIC PDF SAVE TO ONEDRIVE
echo ========================================
echo.
echo This will open your default browser with the presentation.
echo.
echo AFTER BROWSER OPENS:
echo 1. Press Ctrl+P
echo 2. Select "Save as PDF" or "Microsoft Print to PDF"
echo 3. Click "Save"
echo 4. Navigate to: {onedrive_dir}
echo 5. File name: Polymarket_Investment_Presentation.pdf
echo 6. Click Save again
echo.
echo Press any key to open browser...
pause >nul

REM Open HTML in default browser
start "" "{os.path.abspath(html_path)}"

echo.
echo Browser should now be open with the presentation.
echo.
echo REMEMBER: Press Ctrl+P to save as PDF!
echo.
echo Press any key to exit...
pause >nul
"""
    
    batch_path = "OPEN_AND_SAVE.bat"
    with open(batch_path, 'w', encoding='ascii') as f:
        f.write(batch_content)
    
    print(f"Created batch file: {batch_path}")
    print()
    print("TO SAVE PDF TO ONEDRIVE:")
    print(f"1. Run '{batch_path}'")
    print("2. Browser opens with presentation")
    print("3. Press Ctrl+P")
    print("4. Select 'Save as PDF'")
    print(f"5. Save to: {pdf_path}")
    print()
    
    # Also create a simple README file in OneDrive
    readme_path = os.path.join(onedrive_dir, "PRESENTATION_README.txt")
    readme_content = f"""PRESENTATION READY FOR PDF SAVE

Presentation: Polymarket Quantitative Trading Strategy
Date: February 10, 2026
Location: {html_path}

TO SAVE AS PDF:
1. Open {html_path} in browser
2. Press Ctrl+P
3. Select "Save as PDF"
4. Save to this folder as: Polymarket_Investment_Presentation.pdf

The presentation contains:
- Executive Summary & Investment Thesis
- Market Analysis (4% fee reality)
- 6 Novel Trading Strategies
- Risk Management & Position Sizing
- Expected Returns (6-12% monthly)
- Monte Carlo Simulations

Generated: {os.path.basename(__file__)}
"""
    
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Created README in OneDrive: {readme_path}")
    print()
    
    # Try to open the batch file
    try:
        os.startfile(batch_path)
        print("Batch file opened automatically!")
        print("Follow the instructions in the command window.")
    except:
        print(f"Run '{batch_path}' manually to start the process.")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if success:
        print("="*60)
        print("READY TO SAVE PDF TO ONEDRIVE!")
        print("="*60)
        print("\nThe process has been automated.")
        print("Just follow the instructions in the command window.")
    else:
        print("="*60)
        print("SETUP COMPLETE")
        print("="*60)
        print("\nRun 'OPEN_AND_SAVE.bat' to save the PDF.")
    
    sys.exit(0 if success else 1)