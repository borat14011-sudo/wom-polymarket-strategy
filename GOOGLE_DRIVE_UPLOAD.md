# Upload to Google Drive - Quick Guide

## Method 1: Drag & Drop (Easiest)

1. Open **Chrome** and go to https://drive.google.com
2. Make sure you're logged in as **Borat14011@gmail.com**
3. Click **"New" → "Folder"** and name it: `Trading-Strategy-Presentation`
4. Open the folder
5. Drag these files from File Explorer:

```
C:\Users\Borat\.openclaw\workspace\netlify-deploy\index.html
C:\Users\Borat\.openclaw\workspace\PROFESSIONAL_STRATEGY_PRESENTATION.md
```

6. Right-click folder → **"Share"** → Copy link

## Method 2: Google Drive Desktop App

If you have Google Drive installed:

1. Open **Google Drive** folder on your computer
2. Create folder: `Trading-Strategy-Presentation`
3. Copy files from:
   ```
   C:\Users\Borat\.openclaw\workspace\netlify-deploy\index.html
   C:\Users\Borat\.openclaw\workspace\PROFESSIONAL_STRATEGY_PRESENTATION.md
   ```
4. Files sync automatically
5. Right-click folder in Google Drive → **"Share"**

## Method 3: Use Python (If you have gdown)

```bash
pip install gdown google-auth-oauthlib
python upload-to-drive.py
```

## Files to Upload

| File | Location | Description |
|------|----------|-------------|
| index.html | `netlify-deploy\index.html` | Web presentation (open in browser) |
| PROFESSIONAL_STRATEGY_PRESENTATION.md | Root workspace | Markdown source |

## Quick Access

**Folder path:** `C:\Users\Borat\.openclaw\workspace\netlify-deploy`

**Zip version:** `C:\Users\Borat\.openclaw\workspace\netlify-deploy.zip`

---

## Sharing Settings

When sharing, use these settings:
- **Anyone with the link can view**
- **Viewer** permissions (not editor)

This gives you a shareable link like:
`https://drive.google.com/drive/folders/xxxxx`
