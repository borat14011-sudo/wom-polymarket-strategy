# Paper Trade Tracking Sheet

*Live tracking document for paper trades. Updated manually as trades progress.*

---

## Active Trades

| Trade | Entry Date | Entry Price | Size | Fees | Cost Basis | Current Price | Unrealized P&L | Realized P&L | Status |
|-------|------------|-------------|------|------|------------|---------------|----------------|--------------|--------|
| MSTR Mar 31 | Feb 8, 2025 | $0.983 | 6.10 | $0.06 | $6.06 | $0.983 | $0.00 | - | **Open** |
| MSTR Jun 30 | Feb 8, 2025 | $0.905 | 6.63 | $0.07 | $6.07 | $0.905 | $0.00 | - | **Open** |
| MSTR Dec 31 | Feb 8, 2025 | $0.835 | 9.58 | $0.08 | $8.08 | $0.835 | $0.00 | - | **Open** |

### Calculation Notes

- **Size (Contracts)**: `Position Size / (Entry Price × 100)`
- **Cost Basis**: `(Size × Entry Price × 100) + Fees`
- **Unrealized P&L**: `((Current Price - Entry Price) × Size × 100) - (Exit Fees if closed)`
- **Realized P&L**: Populated only when trade is closed

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Capital Deployed** | $20.21 |
| **Total Unrealized P&L** | $0.00 |
| **Total Realized P&L** | $0.00 |
| **Open Positions** | 3 |
| **Closed Positions** | 0 |
| **Win Rate** | 0% |

---

## IRR Tracking (Internal Rate of Return)

| Trade | Days Held | Entry | Current Value | % Return | Annualized IRR |
|-------|-----------|-------|---------------|----------|----------------|
| MSTR Mar 31 | 0 | $6.06 | $6.00 | -1.0% | N/A |
| MSTR Jun 30 | 0 | $6.07 | $6.00 | -1.2% | N/A |
| MSTR Dec 31 | 0 | $6.08 | $8.00 | -1.0% | N/A |
| **Portfolio** | - | $20.21 | $20.00 | -1.0% | N/A |

> **IRR Formula**: `((Current Value / Entry Value) ^ (365 / Days Held) - 1) × 100`
> <br>IRR is most meaningful after 30+ days held.

---

## Trade Notes

### MSTR Mar 31
- **Strategy**: Near-term momentum play
- **Thesis**: MicroStrategy's Bitcoin holdings creating leverage effect
- **Stop Loss**: $0.75 (mental)
- **Target**: $1.20
- **Notes**: 

### MSTR Jun 30
- **Strategy**: Medium-term trend
- **Thesis**: Continued institutional adoption of BTC
- **Stop Loss**: $0.70 (mental)
- **Target**: $1.35
- **Notes**: 

### MSTR Dec 31
- **Strategy**: Long-term LEAPS-style position
- **Thesis**: MSTR as Bitcoin proxy for 2025 bull run
- **Stop Loss**: $0.60 (mental)
- **Target**: $2.00+
- **Notes**: Lower delta, longer runway

---

## Update Log

| Date | Action | Notes |
|------|--------|-------|
| Feb 8, 2025 | Opened positions | Initial entry on all 3 trades |
| | | |

---

## How to Update This Sheet

### When Entering a New Trade:
1. Add row to **Active Trades** table
2. Fill Entry Date, Price, Size, Fees
3. Calculate Cost Basis: `(Size × Entry Price × 100) + Fees`
4. Set Status to "Open"

### When Updating Prices:
1. Update **Current Price** column
2. Recalculate **Unrealized P&L**: `((Current - Entry) × Size × 100)`
3. Update **IRR Tracking** table with new values

### When Closing a Trade:
1. Move row to **Closed Trades** section (create below)
2. Update with Exit Price, Exit Date
3. Calculate Realized P&L: `((Exit - Entry) × Size × 100) - Fees`
4. Change Status to "Closed"
5. Update **Summary Statistics**

---

*Last Updated: Feb 8, 2025 at 17:43 PST*
