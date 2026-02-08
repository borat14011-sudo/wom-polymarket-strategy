# 🐍 Python Setup for Windows - Complete Guide

**Issue:** Monitoring system can't run because Python isn't properly installed or in PATH.

**Goal:** Get Python working so cron jobs can check Polymarket prices automatically.

---

## 🔍 Step 1: Check If Python Is Already Installed

Open **Command Prompt** (not PowerShell) and run:

```cmd
python --version
```

**Possible outcomes:**

### ✅ If you see: `Python 3.11.x` or `Python 3.12.x`
→ Python IS installed, but not in PATH. **Skip to Step 3.**

### ❌ If you see: "Python was not found" or opens Microsoft Store
→ Python is NOT installed. **Continue to Step 2.**

---

## 📥 Step 2: Install Python (If Needed)

### Option A: Official Python Installer (RECOMMENDED)

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.12.x" (latest stable)

2. **Run Installer:**
   - ✅ **CRITICAL:** Check "Add python.exe to PATH" (bottom of installer)
   - Click "Install Now"
   - Wait 2-3 minutes

3. **Verify Installation:**
   ```cmd
   python --version
   pip --version
   ```
   
   Should show Python 3.12.x and pip 23.x

### Option B: winget (If You Prefer Command Line)

```cmd
winget install Python.Python.3.12
```

Then restart Command Prompt and verify:
```cmd
python --version
```

---

## 🛤️ Step 3: Fix PATH (If Python Installed But Not Found)

If `python --version` doesn't work but you know Python is installed:

### Find Python Location:

1. **Open File Explorer**
2. Check these locations:
   ```
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\
   C:\Program Files\Python312\
   C:\Python312\
   ```

3. **Look for `python.exe`** in one of these folders.

### Add to PATH:

1. **Open System Environment Variables:**
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter
   - Click "Advanced" tab
   - Click "Environment Variables"

2. **Edit PATH:**
   - Under "User variables", find `Path`
   - Click "Edit"
   - Click "New"
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\`
   - Click "New" again
   - Add: `C:\Users\YourName\AppData\Local\Programs\Python\Python312\Scripts\`
   - Click "OK" on all windows

3. **Restart Command Prompt** and test:
   ```cmd
   python --version
   ```

---

## 📦 Step 4: Install Required Packages

Once Python works, install the packages needed for monitoring:

```cmd
pip install requests
pip install beautifulsoup4
pip install python-dotenv
```

**Verify:**
```cmd
python -c "import requests; print('Requests installed!')"
```

Should print: `Requests installed!`

---

## 🔧 Step 5: Test Polymarket API Script

Let's test if the monitoring script can run:

1. **Navigate to workspace:**
   ```cmd
   cd C:\Users\Borat\.openclaw\workspace\polymarket-monitor
   ```

2. **Run test:**
   ```cmd
   python api_monitor.py
   ```

**Expected Output:**
```
==========================================
POLYMARKET API MONITOR
==========================================
Timestamp: 2026-02-07 09:20:00 CST

IRAN MARKETS FOUND: 3

Market #1: US strikes Iran by February 13?
  YES: 6.5% | NO: 93.5%
  Volume 24h: $805,000
  End Date: 2026-02-13

PAPER POSITION STATUS:
Entry: 12% @ Feb 6, 1:00 PM CST
Current: 6.5%
P/L: -$1.93 (-46%)
```

### If you see errors:

**"No module named 'requests'"**
→ Run: `pip install requests`

**"File not found"**
→ The script may not exist yet. I can create it for you.

**"SyntaxError"**
→ Wrong Python version. Need 3.11+

---

## 🤖 Step 6: Enable Automated Monitoring

Once the script works manually, we need to make it run automatically via OpenClaw cron.

**Option A: OpenClaw Native (Preferred)**

OpenClaw should auto-detect Python in PATH after restart:

```cmd
openclaw gateway restart
```

Wait 30 seconds, then check if cron jobs start working.

**Option B: Manual Cron Job (If Option A Fails)**

If cron still can't find Python, we may need to:
1. Update OpenClaw config with explicit Python path
2. Or use Windows Task Scheduler instead

---

## 🧪 Step 7: Verify Everything Works

### Test 1: Python from Command Prompt
```cmd
python --version
```
✅ Should show: `Python 3.12.x`

### Test 2: Import Required Packages
```cmd
python -c "import requests; import json; print('All packages OK!')"
```
✅ Should print: `All packages OK!`

### Test 3: Run Monitoring Script
```cmd
cd C:\Users\Borat\.openclaw\workspace\polymarket-monitor
python api_monitor.py
```
✅ Should show market data

### Test 4: OpenClaw Cron Access
```cmd
openclaw status
```
✅ Check if cron jobs show "Running" (not "Error")

---

## 🚨 Common Issues & Fixes

### Issue 1: "python is not recognized"
**Fix:** Python not in PATH. Go back to Step 3.

### Issue 2: "Microsoft Store opens when I type python"
**Fix:** Disable Windows alias:
1. Settings → Apps → App execution aliases
2. Turn OFF "App Installer" for python.exe
3. Restart Command Prompt

### Issue 3: "Permission denied"
**Fix:** Run Command Prompt as Administrator:
1. Right-click Command Prompt
2. "Run as administrator"
3. Try again

### Issue 4: "No module named 'requests'"
**Fix:** Install packages:
```cmd
pip install requests beautifulsoup4 python-dotenv
```

### Issue 5: Cron jobs still failing after Python installed
**Fix:** Restart OpenClaw gateway:
```cmd
openclaw gateway restart
```

---

## 🎯 Quick Success Test

**Run this one command to test everything:**

```cmd
python -c "import requests; r = requests.get('https://clob.polymarket.com/markets'); print('SUCCESS!' if r.status_code == 200 else 'FAILED')"
```

**Expected:** `SUCCESS!`

If that works, Python is ready for monitoring!

---

## 📞 What to Tell Me

After you run through these steps, tell me:

1. ✅ or ❌ **Python installed?** (`python --version` output)
2. ✅ or ❌ **Packages installed?** (did `pip install` work?)
3. ✅ or ❌ **API test worked?** (test command output)
4. ✅ or ❌ **Any errors?** (paste error messages)

Then I can either:
- Create the monitoring script (if it doesn't exist)
- Fix cron configuration (if Python works but cron doesn't)
- Troubleshoot specific errors

---

## 🚀 Once Working...

You'll get automatic Polymarket price checks every 5 minutes via Telegram:

```
📊 5-MIN POLYMARKET CHECK (9:25 AM CST)

Paper Position: Iran Feb 13
Entry: 12% @ Feb 6
Current: 6.3%
P/L: -$2.01 (-48%)

New Opportunities: None detected
Next Check: 9:30 AM CST
```

**Let's get Python working first, then monitoring will handle the rest!** 🇰🇿
