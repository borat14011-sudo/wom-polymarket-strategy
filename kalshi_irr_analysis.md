# 🚨 KALSHI IRR ANALYSIS - CRITICAL FINDING 🚨

**Analysis Date:** Feb 12, 2026
**Analyst:** IRR Specialist

---

## ⚠️ CRITICAL PROBLEM: NO SHORT-TERM MARKETS IN DATASET

After analyzing **11,196 lines** of `kalshi_markets_raw.json`, I have a critical finding:

### **The dataset contains ZERO active markets resolving within 90 days.**

All markets in this data fall into two categories:
1. **Already finalized** (close dates in 2025)
2. **Multi-year resolution** (2027-2099)

---

## What the Data Actually Contains

| Category | Example | Close Date | Status |
|----------|---------|------------|--------|
| Supervolcano | Before Jan 1, 2050 | 2050 | Active |
| Mars colonization | Before 2050 | 2050 | Active |
| Global warming 2°C | Before 2050 | 2050 | Active |
| Pope selection | 2070 | 2070 | Active |
| Elon on Mars | 2099 | 2099 | Active |
| Next James Bond | 2030 | 2030 | Active |
| Nuclear fusion | 2030 | 2030 | Active |
| Canadian election | May 2025 | **FINALIZED** | Closed |
| Pope (resolved) | May 2025 | **FINALIZED** | Closed |

---

## IRR Analysis of Available "Dip Candidates"

Wom was 100% RIGHT. These long-term markets are **GARBAGE** for returns. Here's the math:

### Supervolcano Before 2050 (KXERUPTSUPER-0-50JAN01)
- **YES Price:** 13¢ (bid) / 19¢ (ask)
- **If NO wins:** Profit = 13¢ on 87¢ = 14.9% gross
- **Time to resolution:** ~24 years
- **IRR:** (1.149)^(1/24) - 1 = **0.58% annually**
- **Verdict:** 🗑️ WORSE THAN A SAVINGS ACCOUNT

### Mars Colonization Before 2050 (KXCOLONIZEMARS-50)
- **NO Price:** 80¢ (100 - 20)
- **If NO wins:** Profit = 20¢ on 80¢ = 25% gross
- **Time to resolution:** ~24 years
- **IRR:** (1.25)^(1/24) - 1 = **0.93% annually**
- **Verdict:** 🗑️ STILL TERRIBLE

### Global Warming 2°C Before 2050 (KXWARMING-50)
- **YES at 78¢**
- **If YES wins:** Profit = 22¢ on 78¢ = 28.2% gross
- **Time to resolution:** ~24 years
- **IRR:** (1.282)^(1/24) - 1 = **1.04% annually**
- **Verdict:** 🗑️ A BOND DOES BETTER

### Earthquake in Japan Before 2030 (KXEARTHQUAKEJAPAN-30)
- **YES at 45¢ (dip candidate)**
- **If YES wins:** Profit = 55¢ on 45¢ = 122% gross
- **Time:** ~4 years
- **IRR:** (2.22)^(1/4) - 1 = **22% annually**
- **Verdict:** ✅ BETTER but still 4 year lock-up with binary risk

### EV Market Share >30% by 2030 (EVSHARE-30JAN-30)
- **YES at 45¢ (dip candidate)**
- **If YES wins:** Profit = 55¢ on 45¢ = 122% gross
- **Time:** ~4 years
- **IRR:** (2.22)^(1/4) - 1 = **22% annually**
- **Verdict:** ✅ DECENT but requires conviction on EV adoption

---

## 📊 IRR vs Resolution Time (Available Markets)

| Market | Price | Gross % | Years | IRR (Annual) | Verdict |
|--------|-------|---------|-------|--------------|---------|
| Supervolcano NO | 87¢→100¢ | 14.9% | 24 | **0.58%** | 🗑️ |
| Mars Colonize NO | 80¢→100¢ | 25% | 24 | **0.93%** | 🗑️ |
| 2°C Warming YES | 78¢→100¢ | 28.2% | 24 | **1.04%** | 🗑️ |
| Nuclear Fusion YES | 47¢→100¢ | 113% | 4 | **20.8%** | ⚠️ |
| Japan Earthquake YES | 45¢→100¢ | 122% | 4 | **22.2%** | ⚠️ |
| EV Share >30% YES | 45¢→100¢ | 122% | 4 | **22.2%** | ⚠️ |
| Callum Turner Bond YES | 39¢→100¢ | 156% | 4 | **26.5%** | ⚠️ |
| Data Center YES | 64¢→100¢ | 56% | 4 | **11.8%** | ⚠️ |

---

## 🎯 WHAT'S MISSING (SHORT-TERM GOLDMINES)

The dataset **DOES NOT CONTAIN** the high-IRR, fast-resolution markets like:

| Market Type | Resolution | Typical IRR if Correct |
|-------------|------------|----------------------|
| Fed Rate Decision | 1-2 weeks | 500-2000%+ annualized |
| CPI Release | ~1 week | 500-2000%+ annualized |
| GDP Release | ~1 week | 500-2000%+ annualized |
| NBA/NFL Games | 1-3 days | 1000-5000%+ annualized |
| Weekly Political Events | 1-4 weeks | 200-1000%+ annualized |

**Example:** A 50/50 bet that resolves in 1 week
- Win $1 on $1 bet = 100% in 1 week
- Annualized: (2.0)^52 - 1 = **ASTRONOMICAL**
- Even with 55% win rate, fast turnover crushes slow markets

---

## 🔴 CONCLUSION

### The Dataset is USELESS for Short-Term IRR Trading

**Current data characteristics:**
- ❌ Zero markets resolving within 90 days
- ❌ All active markets are 4-24+ years out
- ❌ Missing Fed, CPI, GDP, sports, and short-term political markets

**Recommendation:**
1. **Pull fresh Kalshi data** with filters for:
   - Close date within 90 days
   - Active status only
   - Categories: Economics, Fed, Sports, Politics (short-term)
   
2. **Focus on capital velocity**, not gross returns
   - 10% in 1 week >>> 100% in 10 years
   
3. **The real money** is in:
   - FOMC meeting outcomes (8 per year)
   - Monthly CPI/employment data
   - Quarterly GDP releases
   - Daily/weekly sports

---

## 📢 FINAL VERDICT

**Wom was RIGHT.**

These 2050 markets are traps for naive investors who see "87% profit potential" without understanding time value of money.

**0.58% annual IRR on a supervolcano bet is embarrassing.**

A 4% Treasury bond beats every single 2050 market in this dataset.

---

*Need fresh short-term market data to provide actionable trading recommendations.*
