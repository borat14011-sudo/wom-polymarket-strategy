@echo off
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
echo 4. Navigate to: C:\Users\Borat\OneDrive\Trading
echo 5. File name: Polymarket_Investment_Presentation.pdf
echo 6. Click Save again
echo.
echo Press any key to open browser...
pause >nul

REM Open HTML in default browser
start "" "C:\Users\Borat\.openclaw\workspace\Polymarket_Investment_Presentation.html"

echo.
echo Browser should now be open with the presentation.
echo.
echo REMEMBER: Press Ctrl+P to save as PDF!
echo.
echo Press any key to exit...
pause >nul
