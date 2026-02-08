# IMMEDIATE ACTION CHECKLIST

## DESKTOP - Phase 2 (Do This Now)

### MOVE TO ARCHIVE:
```powershell
# Grandma Animation
Move-Item "$env:USERPROFILE\Desktop\grandma-animated-v2.mp4" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\GRANDMA-REVIEWS-PAINTINGS*.mp4" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\grandma-animation-raw.mp4" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\grandma-video-improved.html" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\grandma-scenes" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\animation-scenes.txt" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"
Move-Item "$env:USERPROFILE\Desktop\VIDEO-LINK*.txt" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\01-Grandma-Animation-Project\"

# Sonris
Move-Item "$env:USERPROFILE\Desktop\sonris_pdfs" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
Move-Item "$env:USERPROFILE\Desktop\SONRIS-*.md" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
Move-Item "$env:USERPROFILE\Desktop\sonris-*.js" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
Move-Item "$env:USERPROFILE\Desktop\sonris-*.json" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
Move-Item "$env:USERPROFILE\Desktop\*SONRIS*.bat" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
Move-Item "$env:USERPROFILE\Desktop\*SONRIS*.txt" "$env:USERPROFILE\Desktop\ARCHIVE\2026-02-08-CLEANUP\02-Sonris-PDF-Extraction\"
```

### DELETE IMMEDIATELY (Safe):
```powershell
# Verification screenshots
Remove-Item "$env:USERPROFILE\Desktop\gmail-*.png"
Remove-Item "$env:USERPROFILE\Desktop\SUCCESS-CHECK.png"
Remove-Item "$env:USERPROFILE\Desktop\final-check.png"
Remove-Item "$env:USERPROFILE\Desktop\upload-verification.png"
Remove-Item "$env:USERPROFILE\Desktop\screen-verification.png"

# Upload helpers
Remove-Item "$env:USERPROFILE\Desktop\upload-*.js"
Remove-Item "$env:USERPROFILE\Desktop\upload-*.ps1"
Remove-Item "$env:USERPROFILE\Desktop\*upload*.txt"
Remove-Item "$env:USERPROFILE\Desktop\drive-*.ps1"
Remove-Item "$env:USERPROFILE\Desktop\drive-*.js"
Remove-Item "$env:USERPROFILE\Desktop\auto-upload*.js"
Remove-Item "$env:USERPROFILE\Desktop\extract-and-upload.ps1"
Remove-Item "$env:USERPROFILE\Desktop\mouse-drag-upload.ps1"

# 2Captcha
Remove-Item "$env:USERPROFILE\Desktop\2CAPTCHA-*.txt"
Remove-Item "$env:USERPROFILE\Desktop\INSTALL-2CAPTCHA.bat"
Remove-Item "$env:USERPROFILE\Desktop\2CAPTCHA-SETUP-GUIDE.txt"
Remove-Item "$env:USERPROFILE\Desktop\RUN-SONRIS-2CAPTCHA.bat"
Remove-Item "$env:USERPROFILE\Desktop\sonris-with-2captcha.js"

# Temp files
Remove-Item "$env:USERPROFILE\Desktop\WHEN-YOU-RETURN-READ-THIS.txt"
Remove-Item "$env:USERPROFILE\Desktop\EMAIL-TO-YOURSELF.txt"
Remove-Item "$env:USERPROFILE\Desktop\READY-TO-RUN.txt"
Remove-Item "$env:USERPROFILE\Desktop\ANIMATED-VIDEO-COMPLETE.txt"
Remove-Item "$env:USERPROFILE\Desktop\DRAG-TO-DRIVE-NOW.txt"
Remove-Item "$env:USERPROFILE\Desktop\CHECK-DRIVE-NOW.txt"
Remove-Item "$env:USERPROFILE\Desktop\UPLOAD-INSTAGRAM-FILES.bat"
Remove-Item "$env:USERPROFILE\Desktop\OPEN-SONRIS-FILES.bat"
Remove-Item "$env:USERPROFILE\Desktop\OPEN-BEST-6-FILES.bat"
Remove-Item "$env:USERPROFILE\Desktop\OPEN-FOR-UPLOAD.bat"
```

## WORKSPACE - Phase 3 (Do After Desktop)

### MOVE TO ARCHIVE:
```powershell
# Kimi testing files
Move-Item "C:\Users\Borat\.openclaw\workspace\KIMI_*.md" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\research-phase\"
Move-Item "C:\Users\Borat\.openclaw\workspace\kimi-*.ps1" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\research-phase\"

# Old validation reports (keep last 5 of each type)
Move-Item "C:\Users\Borat\.openclaw\workspace\*VALIDATION*.md" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\validation-reports\"
Move-Item "C:\Users\Borat\.openclaw\workspace\*BACKTEST*.md" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\validation-reports\"

# Agent reports (archive older ones)
Move-Item "C:\Users\Borat\.openclaw\workspace\AGENT*_*.md" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\research-phase\"
Move-Item "C:\Users\Borat\.openclaw\workspace\agent*_*.md" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\research-phase\"
Move-Item "C:\Users\Borat\.openclaw\workspace\agent*_*.json" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\research-phase\"

# Test scripts
Move-Item "C:\Users\Borat\.openclaw\workspace\test_*.js" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
Move-Item "C:\Users\Borat\.openclaw\workspace\test_*.py" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
Move-Item "C:\Users\Borat\.openclaw\workspace\check_*.js" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
Move-Item "C:\Users\Borat\.openclaw\workspace\check_*.py" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
Move-Item "C:\Users\Borat\.openclaw\workspace\debug_*.js" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
Move-Item "C:\Users\Borat\.openclaw\workspace\diagnose_*.js" "C:\Users\Borat\.openclaw\workspace\ARCHIVE\test-scripts\"
```

### DELETE IMMEDIATELY (Safe):
```powershell
# Cache files
Remove-Item "C:\Users\Borat\.openclaw\workspace\*.pyc" -Recurse
Remove-Item "C:\Users\Borat\.openclaw\workspace\__pycache__" -Recurse -Force

# Old status files
Remove-Item "C:\Users\Borat\.openclaw\workspace\status.json"
Remove-Item "C:\Users\Borat\.openclaw\workspace\detailed_status.json"

# Superseded memory archive
Remove-Item "C:\Users\Borat\.openclaw\workspace\MEMORY_ARCHIVE_2026-02-08.md"
```

## KEEP (DO NOT TOUCH):
- `polymarket_trading_system/` folder
- `trading-cli.py`, `api.py`, `signal-generator.py`
- `live_*.py` monitoring scripts
- `backtest_*.py` production backtests
- `polymarket_history.db`, `historical_2024.db`
- `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`
- `.git/` folder
- `memory/` folder
- `config.yaml`, `config.json`
