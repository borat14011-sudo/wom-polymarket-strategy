@echo off
echo Opening workspace folder for Google Drive upload...
echo.
echo Folder: C:\Users\Borat\.openclaw\workspace
echo.
echo Instructions:
echo 1. Drag files from THIS window to Google Drive
echo 2. Follow the guide in GOOGLE-DRIVE-UPLOAD-READY.md
echo.
echo Press any key to open folder...
pause >nul
explorer "C:\Users\Borat\.openclaw\workspace"
start https://drive.google.com
echo.
echo Both File Explorer and Google Drive opened!
echo Happy uploading! - Borat 🇰🇿
pause
