# Polymarket Data Samples - Real Examples

## 📊 Sample Market Data

### Example 1: Michigan Senate Election (High Volume)

**Question**: Will a Democrat win Michigan US Senate Election?

```
Event: Michigan Senate Election Winner
Market ID: 255448
Outcomes: Yes | No
Final Prices: 1 | 0
Winner: Yes ✓
Volume: $394,971.30
Resolved: 2024-11-05
```

**Interpretation**: 
- Final price of "1" for YES means YES shares paid out $1.00
- Final price of "0" for NO means NO shares were worthless
- Market correctly predicted Democratic victory
- $395k in trading volume shows high interest

---

### Example 2: Jake Paul vs Mike Tyson (Highest Volume)

**Question**: Will Mike Tyson win his boxing match against Jake Paul?

```
Event: Jake Paul vs. Mike Tyson: Who will win?
Market ID: 255474
Outcomes: Yes | No
Final Prices: 0 | 1
Winner: No ✓
Volume: $32,399,877.16
Resolved: 2024-11-16
```

**Interpretation**:
- Mike Tyson did NOT win (Jake Paul won)
- Highest volume market in dataset ($32M+)
- Final NO price of 1 = NO shares paid $1.00
- Major sporting event generated massive interest

---

### Example 3: Presidential Primary

**Question**: Will Arizona be Trump's worst state on March 19?

```
Event: Trump's worst state on March 19?
Market ID: 255447
Outcomes: Yes | No
Final Prices: 1 | 0
Winner: Yes ✓
Volume: $16,201.25
Resolved: 2024-03-19
```

**Interpretation**:
- Arizona was indeed Trump's worst state
- Lower volume ($16k) for niche political question
- Market resolved correctly

---

## 🎯 Binary Outcome Patterns

### YES Winners (Final Prices: 1 | 0)
```csv
"Will a Democrat win Michigan US Senate Election?","Yes|No","1|0","Yes",$394,971
"Will Arizona be Trump's worst state?","Yes|No","1|0","Yes",$16,201
"Will Florida be Trump's best state?","Yes|No","1|0","Yes",$1,564
```

### NO Winners (Final Prices: 0 | 1)
```csv
"Will a Republican win Michigan US Senate Election?","Yes|No","0|1","No",$684,107
"Will Florida be Trump's worst state?","Yes|No","0|1","No",$65,403
"Will Mike Tyson win?","Yes|No","0|1","No",$32,399,877
```

---

## 💰 Volume Distribution Examples

### High Volume (>$1M)
```
1. Mike Tyson vs Jake Paul (No winner)     $32,399,877
2. Jake Paul wins (Yes winner)             $15,917,754
3. No official winner (No winner)          $14,968,970
4. Virginia Presidential (No, Other)       $10,128,418
5. Virginia Presidential (No, Republican)  $5,686,644
```

### Medium Volume ($100k-$1M)
```
1. Michigan Senate (No, Republican)        $684,107
2. Michigan Senate (No, Other)             $676,897
3. Michigan Senate (Yes, Democrat)         $394,971
```

### Low Volume (<$100k)
```
1. Florida worst state? (No)               $65,403
2. Arizona worst state? (Yes)              $16,201
3. Kansas worst state? (No)                $16,049
```

---

## 📅 Timeline Examples

### March 2024 Markets
- Trump state performance predictions
- Super Tuesday primaries
- Political primaries

### November 2024 Markets
- Presidential election
- Senate races
- Mike Tyson vs Jake Paul fight

### Complete Date Range
- **Earliest**: March 1, 2024
- **Latest**: December 30, 2024
- **Span**: 304 days

---

## 🔍 Multi-Outcome Market Example

**Event**: Senegal Presidential Election Winner

```
Market 1: Bassirou Diomaye Faye wins?
  Outcomes: Yes | No
  Final Prices: 1 | 0
  Winner: Yes ✓
  Volume: $25,952.20

Market 2: Amadou Ba wins?
  Outcomes: Yes | No
  Final Prices: 0 | 1
  Winner: No ✓
  Volume: $24,130.20

Market 3: Khalifa Sall wins?
  Outcomes: Yes | No
  Final Prices: 0 | 1
  Winner: No ✓
  Volume: $7,016.84
```

**Interpretation**:
- 8 candidates had individual YES/NO markets
- Bassirou Diomaye Faye won (only YES winner)
- All other candidates correctly resolved to NO
- Total event volume: ~$79k across all markets

---

## 📈 Data Quality Indicators

### ✅ Complete Markets (All Fields Present)
```csv
event_id,event_title,market_id,question,outcomes,final_prices,winner,volume_usd
903799,"Michigan Senate Election",255448,"Will a Democrat win?","Yes|No","1|0","Yes",394971.30
```

### ⚠️ Minimal Volume Markets
```csv
event_id,event_title,market_id,question,outcomes,final_prices,winner,volume_usd
903792,"Senegal Election",255434,"Will Aly Ngouille Ndiaye win?","Yes|No","0|1","No",0
```
*Note: 3/149 markets have zero volume but still have valid outcomes*

---

## 🎲 Outcome Statistics from Sample

### Presidential Elections (Sample: 10 markets)
- Democrat wins: 3 ✓
- Republican wins: 3 ✓
- Other party wins: 0 ✓
- Other doesn't win: 4 ✓

### Sports Events (Sample: 3 markets)
- Jake Paul wins: 1 ✓
- Mike Tyson wins: 0 ✓
- No official winner: 0 ✓

### Political Primaries (Sample: 15 markets)
- Trump wins state: 10 ✓
- Specific state outcomes: 5 ✓

---

## 💡 How to Use This Data

### 1. Load a Sample Market
```python
import pandas as pd

df = pd.read_csv('polymarket_resolved_markets.csv')

# Get Michigan Senate market
michigan = df[df['market_id'] == '255448'].iloc[0]

print(f"Question: {michigan['question']}")
print(f"Winner: {michigan['winner']}")
print(f"Volume: ${michigan['volume_usd']:,.2f}")
```

### 2. Analyze Outcome Accuracy
```python
# Parse final prices
df['yes_price'] = df['final_prices'].str.split('|').str[0].astype(float)
df['no_price'] = df['final_prices'].str.split('|').str[1].astype(float)

# Check if YES won
df['yes_won'] = df['winner'] == 'Yes'

# Verify prices match outcomes
df['price_matches'] = (
    ((df['yes_won']) & (df['yes_price'] >= 0.95)) |
    ((~df['yes_won']) & (df['no_price'] >= 0.95))
)

print(f"Price-outcome consistency: {df['price_matches'].sum()}/{len(df)}")
```

### 3. Volume Analysis
```python
# Top 10 by volume
top_markets = df.nlargest(10, 'volume_usd')[['question', 'winner', 'volume_usd']]
print(top_markets)

# Average volume
print(f"Average volume: ${df['volume_usd'].astype(float).mean():,.2f}")
```

---

## 🏆 Data Validation Summary

✅ **All markets resolved**: 149/149  
✅ **Winners determined**: 149/149 (100%)  
✅ **Final prices consistent**: 149/149 (100%)  
✅ **Volume data**: 146/149 (98%)  
✅ **Date data**: 149/149 (100%)  
✅ **Token IDs**: 149/149 (100%)  

**Conclusion**: High-quality, backtest-ready dataset

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| Total Markets | 149 |
| YES Winners | 53 (35.6%) |
| NO Winners | 96 (64.4%) |
| Avg Volume | $746,521 |
| Max Volume | $32.4M |
| Min Volume | $0 |
| Date Range | 304 days |
| Unique Events | 33 |

---

*All data verified from Polymarket Gamma API*  
*Final outcomes are real, not simulated*  
*Ready for backtesting and analysis*
