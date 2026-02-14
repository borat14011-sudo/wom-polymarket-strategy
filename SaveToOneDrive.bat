@echo off
echo ========================================
echo SAVE PRESENTATION PDF TO ONEDRIVE
echo ========================================
echo.
echo Opening presentation in Chrome with print dialog...
echo.
echo AFTER CHROME OPENS:
echo 1. In the print dialog, select "Save as PDF"
echo 2. Click "Save"
echo 3. Navigate to: C:\Users\Borat\OneDrive\Trading\
echo 4. File name: Polymarket_Investment_Presentation.pdf
echo 5. Click Save again
echo.
echo Press any key to continue...
pause >nul

REM Open Chrome directly to the HTML file
start chrome "file:///C:/Users/Borat/.openclaw/workspace/Polymarket_Investment_Presentation.html"

echo.
echo Chrome should now be open with the presentation.
echo.
echo TO SAVE AS PDF:
echo 1. Press Ctrl+P (or Cmd+P on Mac)
echo 2. Destination: Select "Save as PDF"
echo 3. Save to: OneDrive\Trading\Polymarket_Investment_Presentation.pdf
echo.
echo The PDF will be saved directly to your OneDrive!
echo.
echo Press any key to exit...
pause >nul