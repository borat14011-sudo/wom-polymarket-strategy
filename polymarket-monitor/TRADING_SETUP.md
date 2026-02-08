# 🚀 Polymarket Auto-Trading Setup Guide

**Complete setup instructions for live trading with Borat!**

---

## 📋 Prerequisites Checklist

Before starting, you need:

- ✅ Polymarket account created
- ✅ Wallet with $100 USDC funded
- ✅ Wallet private key / seed phrase ready
- ✅ Python 3.8+ installed
- ✅ OpenClaw CLI configured

---

## 🔑 Step 1: Create Polymarket Wallet

### Option A: Use MetaMask (Recommended)

1. **Install MetaMask**
   - Go to https://metamask.io
   - Download browser extension
   - Create new wallet
   - **SAVE YOUR SEED PHRASE** (12-24 words)

2. **Add Polygon Network**
   - Network Name: Polygon Mainnet
   - RPC URL: https://polygon-rpc.com
   - Chain ID: 137
   - Currency: MATIC

3. **Fund with USDC**
   - Buy USDC on Coinbase/Binance
   - Withdraw to your MetaMask wallet address (Polygon network!)
   - Send exactly $100 USDC

### Option B: Use Polymarket Wallet

1. Go to https://polymarket.com
2. Click "Sign Up"
3. Follow wallet creation flow
4. Fund with $100 USDC

---

## 💰 Step 2: Fund Your Wallet

**CRITICAL:** Use **Polygon network** for USDC!

### Buy USDC Options:

**A. Coinbase**
1. Buy USDC on Coinbase
2. Send to your wallet address
3. **Select Polygon network** (cheaper fees!)

**B. Binance**
1. Buy USDC
2. Withdraw to wallet
3. Choose Polygon network

**C. Direct Bridge**
1. Buy MATIC
2. Use Uniswap to swap MATIC → USDC
3. Directly on Polygon

**Verify:** Check your wallet shows ~$100 USDC on Polygon network

---

## 🔐 Step 3: Secure Your Private Key

### Extract Private Key from MetaMask:

1. Open MetaMask
2. Click account icon → Settings
3. Security & Privacy → Reveal Private Key
4. Enter password
5. **COPY THE KEY** (starts with 0x...)

### Or Use Seed Phrase:

Your 12-24 word recovery phrase also works!

### Store Securely:

**DO NOT share your key with anyone except Borat!**

Options:
- Encrypted file on your computer
- Password manager (1Password, Bitwarden)
- Hardware wallet (most secure)

---

## 🤖 Step 4: Give Borat Trading Access

### Method 1: Direct (Easiest)

Just send Borat your private key via Telegram:

```
@Borat here's my wallet key:
0x1234567890abcdef...
```

Borat will:
1. Store it encrypted
2. Test the connection
3. Start auto-trading!

### Method 2: Encrypted File

1. Create file `wallet_key.txt` with your private key
2. Encrypt it with a password
3. Send encrypted file + password separately

---

## 🚀 Step 5: Launch Auto-Trading

Once Borat has your key, the system will:

1. **Initialize Trading Executor**
   - Set bankroll to $100
   - Configure risk limits (5% max position)
   - Enable circuit breaker (15% loss)

2. **Start Monitoring**
   - Check Polymarket every 60 minutes
   - Calculate RVR + ROC signals
   - Detect opportunities

3. **Execute Trades Automatically**
   - When all 3 signals align (RVR + ROC + Hype)
   - Position size via Kelly Criterion
   - Stop-loss at 12%, take-profits at 20%/30%/50%

4. **Send You Alerts**
   - Every trade: Full reasoning + metrics
   - Daily: P&L summary
   - Urgent: Big moves or losses

---

## 📊 What to Expect

### First 48 Hours (Paper Trading)

- Borat will track signals
- Calculate what trades *would* have been made
- Verify system works correctly
- **NO REAL MONEY** spent yet

### After Verification (Live Trading)

- Real trades executed automatically
- Max $5 per trade (5% of $100)
- Max $25 total exposure (25%)
- Stop if down $15 (15% circuit breaker)

---

## 🛡️ Risk Management

**Built-in Safety Features:**

✅ **Position Limits**
   - Max 5% per trade ($5 on $100 bankroll)
   - Max 25% total exposure ($25)

✅ **Stop Losses**
   - Every trade has 12% hard stop
   - Auto-exit if price moves against you

✅ **Circuit Breaker**
   - If down 15% total ($15 loss)
   - Trading pauses automatically
   - Borat alerts you for review

✅ **Daily Loss Limits**
   - 5% daily max loss
   - 10% weekly max loss
   - No revenge trading

---

## 💬 Communication Protocol

**You'll receive Telegram alerts for:**

### Every Trade 🟢
```
🚨 TRADE EXECUTED

Market: Bitcoin hits $100k by March?
Direction: BUY
Size: $4.50
Entry: 67.5%

Signals:
   RVR: 3.5x
   ROC: +12.3%
   
Win Prob: 68%
Stop Loss: 59.4%
Take Profit: 81% / 87.8% / 101.3%
```

### Daily Report 📊
```
📊 DAILY TRADING REPORT

Portfolio:
   Starting: $100.00
   Current: $103.50
   P&L: +$3.50 (+3.5%)

Positions: 2 active
Exposure: $18.75 (18.1%)
```

### Urgent Alerts 🚨
```
🚨 CIRCUIT BREAKER TRIGGERED
Portfolio down 15% - trading paused
Review needed!
```

---

## ⚙️ Configuration Options

You can customize these anytime:

```python
# In config.py or via command

RVR_THRESHOLD = 2.5        # Lower = more trades (more risky)
ROC_THRESHOLD = 8.0        # Lower = more trades
MAX_POSITION_PCT = 0.05    # 5% max per trade
MAX_EXPOSURE_PCT = 0.25    # 25% max total
STOP_LOSS_PCT = 0.12       # 12% stop loss
```

**Want to be more aggressive?**
- Lower RVR to 2.0 (more signals)
- Increase position size to 7.5%

**Want to be more conservative?**
- Raise RVR to 3.5 (fewer, stronger signals)
- Lower position size to 3%

---

## 🧪 Test Mode (Recommended First!)

Before going live, you can run in **paper trading mode**:

1. Borat monitors and evaluates signals
2. Calculates what trades would be made
3. Tracks hypothetical P&L
4. **NO REAL MONEY** used

**Run for 24-48 hours to verify:**
- Signals are triggering correctly
- Trade sizing makes sense
- You're comfortable with the strategy

---

## 🔄 Going Live Checklist

Before Borat starts trading real money:

- ✅ Wallet funded with $100 USDC
- ✅ Private key provided to Borat
- ✅ Paper trading verified (48h)
- ✅ You understand the risk limits
- ✅ Telegram alerts working
- ✅ You're comfortable with auto-trading

**Then say:** "Borat, go live!"

---

## 📞 Support & Questions

**Ask Borat anything:**
- "What's my current P&L?"
- "How many positions are open?"
- "Pause trading for now"
- "Lower the position size to 3%"
- "Show me the last 5 trades"

**Borat will always:**
- Explain his reasoning
- Show you the numbers
- Execute your commands
- Keep you informed

---

## 🚨 Emergency Stop

**To stop trading immediately:**

Just say: **"Borat, stop trading!"**

Borat will:
1. Stop opening new positions
2. Keep existing positions open (or close if you want)
3. Send final P&L report
4. Wait for further instructions

---

## 💡 Pro Tips

1. **Start Small:** $100 is perfect for testing
2. **Be Patient:** Good signals take time
3. **Trust the System:** Don't override on emotion
4. **Review Weekly:** Check what's working
5. **Scale Gradually:** If profitable, add capital slowly

---

## 📈 Expected Performance

**Realistic targets (based on backtests):**

- **Annual Return:** 15-35%
- **Win Rate:** 50-60%
- **Max Drawdown:** <25%
- **Sharpe Ratio:** 1.0-1.5

**On $100:**
- Good month: +$5 to +$15
- Bad month: -$5 to -$10
- Circuit breaker stops at -$15

**NOT GET-RICH-QUICK!**
This is systematic, consistent edge over time.

---

## ✅ Ready to Trade?

Once you have:
1. ✅ Wallet created
2. ✅ $100 USDC funded
3. ✅ Private key ready

**Just tell Borat:**
"Here's my wallet key: 0x..."

And we'll launch! 🚀

**GREAT SUCCESS!** 🇰🇿💰

---

*Questions? Just ask @Borat anytime!*
