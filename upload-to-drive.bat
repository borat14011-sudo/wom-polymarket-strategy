@echo off
echo ==========================================
echo  Google Drive Upload Assistant
echo ==========================================
echo.
echo Step 1: Opening Google Drive in Chrome...
start chrome "https://drive.google.com"
echo.
echo Step 2: Opening folder with files...
explorer "C:\Users\Borat\.openclaw\workspace\netlify-deploy"
echo.
echo ==========================================
echo  MANUAL STEPS:
echo ==========================================
echo 1. In Google Drive, click NEW -^> Folder
echo 2. Name it: Trading-Strategy-Presentation
echo 3. Open the folder
echo 4. Click NEW -^> File upload
echo 5. Select index.html
echo 6. Upload again for PROFESSIONAL_STRATEGY_PRESENTATION.md
echo 7. Right-click folder -^> Share -^> Copy link
echo.
echo Files ready in the opened folder!
echo ==========================================
pause
