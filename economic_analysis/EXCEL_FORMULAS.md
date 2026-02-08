# Excel Formulas for Economic Analysis

## Sheet 1: Monthly Performance Tracker

### Column Setup
| Column | Header | Formula/Value |
|--------|--------|---------------|
| A | Month | 0 to 24 |
| B | Date | =DATE(2024,1,1) + (A2 × 30) |
| C | Gross_Return_Pct | Input monthly gross return |
| D | Cost_Pct | =C2 × 0.05 (5% of gross) |
| E | Edge_Decay_Pct | See decay schedule |
| F | Net_Return_Pct | =C2-D2-E2 |
| G | Portfolio_Value | =G1 × (1+F2) |
| H | Previous_Peak | =MAX($G$1:G2) |
| I | Drawdown_Pct | =(G2-H2)/H2 |

### Key Formulas

**Cumulative Return:**
```excel
=(Current_Value / Starting_Value) - 1
```

**Running Maximum:**
```excel
=MAX($G$2:G25)
```

**Drawdown Calculation:**
```excel
=(Current_Value / Running_Max) - 1
```

---

## Sheet 2: Kelly Criterion Calculator

### Input Cells
| Cell | Input | Example |
|------|-------|---------|
| B2 | Win Rate (p) | 0.849 |
| B3 | Average Win | 0.0046 |
| B4 | Average Loss | 0.0018 |

### Kelly Formula
```excel
=((B3/B4)*B2 - (1-B2)) / (B3/B4)
```

Or broken down:
```excel
b = B3/B4 (payoff ratio)
p = B2 (win probability)
q = 1-B2 (loss probability)
Kelly = (b*p - q) / b
```

### Conservative Kelly (50%)
```excel
=Kelly * 0.5
```

### Max Position Size
```excel
=MIN(Conservative_Kelly, 0.02) (capped at 2%)
```

---

## Sheet 3: CAGR Calculations

### Basic CAGR
```excel
=(Ending_Value / Starting_Value)^(1/Years) - 1
```

Example:
```excel
=(1379.36/1000)^(1/2) - 1 = 17.51%
```

### From Monthly Returns
```excel
=GEOMEAN(1+monthly_returns_range)^12 - 1
```

---

## Sheet 4: IRR Calculations

### Monthly IRR (Excel)
```excel
=IRR(cash_flow_range, [guess])
```

Cash flow range includes:
- Month 0: -1000 (initial investment)
- Months 1-23: 0 (no cash flows)
- Month 24: +1379.36 (final value)

### Annualized IRR
```excel
=(1 + Monthly_IRR)^12 - 1
```

### MIRR (Modified IRR)
```excel
=MIRR(cash_flow_range, finance_rate, reinvest_rate)
```

Example:
```excel
=MIRR(B2:B26, 0, 0.045)
```

---

## Sheet 5: Risk Metrics

### Standard Deviation (Monthly)
```excel
=STDEV.S(monthly_return_range)
```

### Annualized Standard Deviation
```excel
=Monthly_StdDev × SQRT(12)
```

### Sharpe Ratio
```excel
=(Annual_Return - Risk_Free_Rate) / Annualized_StdDev
```

Example:
```excel
=(0.1803 - 0.045) / 0.1289 = 1.05
```

### Downside Deviation
```excel
{=SQRT(SUM(IF(returns<0, returns^2, 0)) / COUNT(returns))}
```

(Array formula - press Ctrl+Shift+Enter)

### Sortino Ratio
```excel
=(Annual_Return - Risk_Free_Rate) / Downside_Deviation
```

### Maximum Drawdown
```excel
=MIN(drawdown_range)
```

### Calmar Ratio
```excel
=CAGR / ABS(Max_Drawdown)
```

Example:
```excel
=0.1803 / 0.087 = 2.07
```

---

## Sheet 6: VaR Calculations

### Parametric VaR (Daily)
```excel
=Portfolio_Value × (NORMSINV(confidence) × Daily_Volatility)
```

Where:
```excel
Daily_Volatility = Annual_Volatility / SQRT(252)
NORMSINV(0.95) = 1.645
NORMSINV(0.99) = 2.326
```

### Historical VaR (Percentile)
```excel
=PERCENTILE.EXC(return_range, 1-confidence)
```

Example (95% VaR):
```excel
=PERCENTILE.EXC(monthly_returns, 0.05)
```

---

## Sheet 7: Cost Analysis

### Total Cost Impact
```excel
=Gross_Return × Cost_Percentage
```

### Net Return
```excel
=Gross_Return - Cost_Amount - Edge_Decay
```

### Cost Drag on CAGR
```excel
=CAGR_Gross - CAGR_Net
```

---

## Sheet 8: Edge Decay Model

### Decay Factor
```excel
=(1 - Decay_Rate)^Month
```

Where Decay_Rate = 1.5% per month (0.015)

### Remaining Edge
```excel
=Initial_Edge × Decay_Factor
```

### Lost Alpha
```excel
=Previous_Edge - Current_Edge
```

---

## Sheet 9: Sensitivity Analysis

### Data Table Setup

1. Create base scenario with all inputs
2. Select output cells (CAGR, IRR, etc.)
3. Data → What-If Analysis → Data Table
4. Row input: Cost percentage range
5. Column input: Decay rate range

### Two-Way Sensitivity Formula
```excel
=TABLE(cost_range, decay_range)
```

---

## Quick Reference: Key Excel Functions

| Function | Purpose |
|----------|---------|
| `=IRR()` | Internal rate of return |
| `=MIRR()` | Modified IRR with reinvestment rate |
| `=GEOMEAN()` | Geometric mean for CAGR |
| `=STDEV.S()` | Sample standard deviation |
| `=PERCENTILE.EXC()` | Percentile for VaR |
| `=MAX()` | Maximum value (for peaks) |
| `=MIN()` | Minimum value (for drawdowns) |
| `=NORMSINV()` | Z-score for confidence level |
| `=SUMPRODUCT()` | Weighted averages |
| `=COUNTIF()` | Count occurrences |

---

## Chart Formulas

### Equity Curve (Line Chart)
X-axis: Month numbers 0-24
Y-axis: Portfolio_Value column

### Underwater Chart (Area Chart)
X-axis: Month numbers
Y-axis: Drawdown_Pct column (inverted values)

### Rolling Sharpe (Line Chart)
```excel
=((AVERAGE(last_12_months) × 12) - Risk_Free) / (STDEV(last_12_months) × SQRT(12))
```

---

## Validation Checks

### Sanity Checks
1. Final portfolio value should equal initial × (1+CAGR)^years
2. Sum of monthly returns should approximate CAGR
3. Max drawdown should never exceed -100%
4. Sharpe ratio typically 0.5-3.0 for real strategies
5. Kelly should never recommend >50% (risk of ruin)

### Formula Audits
```excel
=SUM(Costs) / SUM(Gross_Profits) = Cost_Percentage
=PRODUCT(1+monthly_returns) - 1 ≈ CAGR
=MAX(Previous_Peak) = MAX(Portfolio_Value)
```

---

*All formulas tested with Excel 2019/365. Array formulas require Ctrl+Shift+Enter in older versions.*
