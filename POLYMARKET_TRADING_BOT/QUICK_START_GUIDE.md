# 🚀 Polymarket Trading Bot - Quick Start Guide

**Execute trades in under 5 minutes. No thinking required.**

---

## ✅ PRE-FLIGHT CHECKLIST (Do These First)

### 1. Check Python Version
**Copy and paste this command:**
```bash
python --version
```

**Expected output:**
```
Python 3.8.x  (or higher - 3.8, 3.9, 3.10, 3.11, 3.12 all work)
```

**If you see an error:**
- Download Python from https://python.org
- Install with "Add Python to PATH" checked ✅

---

### 2. Check Chrome is Installed
**Copy and paste this command:**

**Windows:**
```bash
dir "C:\Program Files\Google\Chrome\Application\chrome.exe" 2>nul || dir "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" 2>nul && echo Chrome FOUND || echo Chrome NOT FOUND
```

**Mac:**
```bash
ls /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome 2>/dev/null && echo "Chrome FOUND" || echo "Chrome NOT FOUND"
```

**Expected output:**
```
Chrome FOUND
```

**If Chrome is NOT found:**
- Download from https://google.com/chrome
- Install it now

---

### 3. Verify Your Polymarket Balance

1. Go to https://polymarket.com
2. Log in to your account
3. Check your balance in the top right corner
4. **You need at least $10.00 to trade**

**⚠️ IMPORTANT:** The bot will NOT trade if you have less than $10 USDC.

---

## 🛠️ STEP-BY-STEP SETUP

### Step 1: Navigate to Bot Folder
**Copy and paste:**
```bash
cd POLYMARKET_TRADING_BOT
```

**Expected output:**
```
(no output, just returns to prompt)
```

---

### Step 2: Run Setup Script
**Windows - Copy and paste:**
```bash
setup.bat
```

**Mac/Linux - Copy and paste:**
```bash
bash setup.sh
```

**Expected output:**
```
========================================
Polymarket Trading Bot - Setup
========================================

[1/4] Python found ✓

[2/4] Creating virtual environment...

[3/4] Activating virtual environment...

[4/4] Installing dependencies...

========================================
Setup Complete! ✓
========================================
```

**If setup fails:**
- Make sure you're in the POLYMARKET_TRADING_BOT folder
- Try running: `pip install -r requirements.txt` manually
- Still failing? Run: `python -m pip install --upgrade pip` then try again

---

### Step 3: Create Your Credentials File
**Copy and paste:**

**Windows:**
```bash
copy .env.example .env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

**Expected output:**
```
        1 file(s) copied.
```
(or on Mac/Linux, no output means success)

---

### Step 4: Add Your Credentials
**Copy and paste:**

**Windows (Notepad):**
```bash
notepad .env
```

**Mac (TextEdit):**
```bash
open -e .env
```

**Edit the file to look like this:**
```env
# Polymarket Credentials
POLYMARKET_EMAIL=your_actual_email@gmail.com
POLYMARKET_PASSWORD=your_actual_password
```

**Replace:**
- `your_actual_email@gmail.com` → Your real Polymarket email
- `your_actual_password` → Your real Polymarket password

**Save the file and close the editor.**

**⚠️ CRITICAL:** Never share your `.env` file with anyone!

---

## 🎯 RUN THE BOT

### First Test Run (Safe Mode - No Browser Window)
**Copy and paste:**
```bash
python trading_bot.py
```

**What you will see:**
```
2024-02-08 18:30:01 - INFO - Starting Polymarket Trading Bot
2024-02-08 18:30:01 - INFO - Target Market: MicroStrategy 500K BTC Dec 31
2024-02-08 18:30:01 - INFO - Trade Action: BUY_NO
2024-02-08 18:30:01 - INFO - Target Price: $0.835 (83.5¢)
2024-02-08 18:30:01 - INFO - Position Size: $8.00
2024-02-08 18:30:05 - INFO - Browser initialized
2024-02-08 18:30:08 - INFO - Logging in to Polymarket...
2024-02-08 18:30:12 - INFO - Login successful
2024-02-08 18:30:15 - INFO - Current balance: $X.XX USDC
2024-02-08 18:30:18 - INFO - Searching for market: MicroStrategy 500K BTC Dec 31
2024-02-08 18:30:22 - INFO - Market found, navigating...
2024-02-08 18:30:25 - INFO - Current NO price: 0.842
2024-02-08 18:30:25 - INFO - Target price: 0.835
2024-02-08 18:30:25 - INFO - Price difference: 0.007 (outside tolerance)
2024-02-08 18:30:25 - INFO - Trade NOT executed - price not within tolerance
2024-02-08 18:30:25 - INFO - Bot execution completed
```

**✅ This is SUCCESS** - The bot is working correctly!

---

### See the Browser (Debug Mode)
**Edit your `.env` file and add this line:**
```env
HEADLESS=false
```

Then run again:
```bash
python trading_bot.py
```

A Chrome window will open so you can watch what happens.

---

## 🛡️ SAFETY CHECKS

### How to Stop the Bot
**Press:** `Ctrl + C` (in the terminal window)

**Or close the terminal window.**

---

### What If It Fails?

| Error | Solution |
|-------|----------|
| "Python not found" | Install Python from python.org |
| "Chrome not found" | Install Chrome from google.com/chrome |
| "Login failed" | Check email/password in `.env` file |
| "Insufficient balance" | Deposit more USDC to Polymarket |
| "Market not found" | Check market name is exact |
| "Price outside tolerance" | Wait for price to move closer to target |
| Browser stays blank | Check internet connection |

---

### How to Verify Position Was Opened

1. Go to https://polymarket.com/portfolio
2. Log in if needed
3. Look for "MicroStrategy 500K BTC Dec 31"
4. You should see your position listed
5. Check the "NO" position shows your trade amount

---

## ✅ POST-TRADE VERIFICATION

### Check Polymarket Portfolio

1. **Go to:** https://polymarket.com/portfolio
2. **Look for:** Your trade in the "Positions" section
3. **Verify:**
   - Market name matches
   - Side (YES/NO) is correct
   - Amount matches your position size
   - Entry price is shown

---

### Confirm Order Details

**In your terminal, you should see:**
```
2024-02-08 18:35:15 - INFO - Trade executed successfully!
2024-02-08 18:35:15 - INFO - Order: BUY NO $8.00 at 0.835
2024-02-08 18:35:15 - INFO - Transaction confirmed
```

---

### Log Your Trade

**Create a tracking file:**

**Windows:**
```bash
notepad trades.txt
```

**Mac/Linux:**
```bash
touch trades.txt && open trades.txt
```

**Log each trade like this:**
```
=== TRADE LOG ===
Date: 2024-02-08
Market: MicroStrategy 500K BTC Dec 31
Action: BUY NO
Amount: $8.00
Entry Price: 83.5¢
Target Exit: 90.0¢ (adjust as needed)
Status: OPEN
=================
```

---

## 📊 CURRENT STRATEGY CONFIGURATION

| Setting | Value |
|---------|-------|
| Market | MicroStrategy 500K BTC Dec 31 |
| Action | BUY NO |
| Target Price | 83.5¢ (0.835) |
| Position Size | $8.00 |
| Price Tolerance | ±0.5¢ |
| Min Balance | $10.00 |

---

## 🔄 CHANGE STRATEGY (Optional)

**To change what the bot trades, edit `.env`:**

```env
TARGET_MARKET=Different Market Name
TRADE_ACTION=BUY_YES
TARGET_PRICE=0.450
POSITION_SIZE=25.00
```

**Then run the bot again.**

---

## 🆘 EMERGENCY CONTACTS

- **Polymarket Support:** https://polymarket.com/support
- **Check Logs:** Look in `POLYMARKET_TRADING_BOT/logs/` folder
- **Last Log File:** Most recent file named `trading_bot_YYYYMMDD_HHMMSS.log`

---

## ⚠️ FINAL WARNINGS

1. **Never trade more than you can afford to lose**
2. **Always verify the trade executed correctly**
3. **Keep your `.env` file secret**
4. **Test with small amounts first**
5. **Monitor your positions regularly**

---

## 🎉 YOU'RE READY!

**Run the bot:**
```bash
python trading_bot.py
```

**Good luck! 🚀**
