# BACKTEST_CORRELATION.md
## Correlation Strategy for Prediction Markets

**Strategy**: Identify markets that move together and use correlations to hedge risk or amplify gains through simultaneous positions.

---

## 📊 Core Concept

**Positive Correlation**: Markets that move in the same direction
- **Double Down**: Bet YES on both to amplify gains when correlation is strong
- **Risk**: If wrong, lose on both positions

**Negative Correlation**: Markets that move in opposite directions  
- **Hedge**: Bet YES on one, NO on the other to reduce risk
- **Lower returns but safer**

**Independent Markets**: No correlation
- **Diversify**: Spread risk across unrelated events

---

## 🔗 Known Market Correlations

### **Geopolitics + Commodities**

#### **Iran Strike → Oil Prices** ⭐ Strong Positive
- **Correlation**: Military action in Middle East → Supply disruption fears → Oil spike
- **Strategy**: 
  - YES on "Iran strike by [date]" + YES on "Oil >$85 by [date]"
  - Risk multiplier: If strike happens, both hit
  - Hedge option: YES Iran strike + NO on "Oil stays <$80"
- **Historical**: 2020 Soleimani assassination → Oil jumped $5
- **Timing**: Oil markets react within 24-48 hours

#### **Russia-Ukraine Escalation → Oil/Gas Prices** Strong Positive
- **Strategy**: Escalation news → Energy prices up
- **Also correlates with**: European natural gas prices, wheat prices

#### **Middle East Conflict → Defense Stocks** Moderate Positive
- Less direct but measurable correlation

---

### **Politics - Party Dynamics**

#### **Trump Legal Issues → GOP Primary Odds** Complex
- **2023-2024 Pattern**: 
  - Indictments → Trump support INCREASED in primary
  - BUT decreased in general election odds
- **Strategy**: 
  - YES Trump indictment + YES Trump primary win (positive correlation)
  - YES Trump indictment + NO Trump general election (negative correlation)
- **Hedge Play**: Can profit whether indictments help or hurt him overall

#### **Biden Health News → Democrat Nominee Markets** Strong
- Any major health scare → Other Democrat odds rise
- **Strategy**: Monitor Biden health + have positions on Harris, Newsom ready

#### **Debate Performance → Polling Markets** Strong (but fast-moving)
- Debate winner markets correlate with 7-day polling bump markets
- **Timing critical**: Need to enter before debate or immediately after

---

### **Crypto Markets - High Correlation Cluster**

#### **Bitcoin → Altcoins** Very Strong Positive (0.7-0.9 correlation)
- **Strategy**: 
  - YES Bitcoin >$100k + YES Ethereum >$5k (amplify)
  - When BTC moves, alts follow but with higher volatility
- **Leverage**: Altcoin bets are often cheaper with bigger multipliers

#### **Bitcoin → Crypto Regulation** Moderate Negative
- Harsh regulation news → Prices drop
- **Hedge**: YES Bitcoin >$X + NO on "Major crypto regulation by [date]"

#### **Stock Market → Crypto** Moderate Positive (risk-on asset)
- **Bull market**: Both rise together
- **Recession fears**: Both fall
- **Strategy**: YES "S&P 500 >X" + YES "BTC >$Y"

---

### **Economy - Inflation Cluster**

#### **CPI Report → Fed Rate Hike** Strong Positive
- High inflation → Fed raises rates
- **Strategy**: YES "CPI >X%" + YES "Fed hikes to Y%"

#### **Fed Rate Hike → Stock Market** Moderate Negative
- Rate hikes → Market dips (usually)
- **Hedge**: YES Fed hike + NO on "S&P 500 >X"

#### **Unemployment → Recession** Strong Positive
- Unemployment spike → Recession odds rise
- **Leading indicator**: Watch unemployment markets for recession plays

---

### **Tech/AI Markets**

#### **OpenAI/Anthropic Releases → AI Capability Markets** Strong
- Major model release → "AGI by [date]" odds shift
- **Strategy**: Watch for announcement leaks, position before public release

#### **AI Regulation → Big Tech Stock Markets** Moderate Negative
- Harsh AI rules → Tech valuations drop

---

## 🎯 Backtesting Methodology

### **Data Collection**
1. **Historical Market Pairs**: Pull resolution data for correlated markets
2. **Time Windows**: Measure correlation over 7-day, 30-day, 90-day windows
3. **Event Timing**: Track how quickly second market reacts to first

### **Correlation Calculation**
```
Correlation Score = (Markets moving together) / (Total observations)
- Strong: >0.7
- Moderate: 0.4-0.7  
- Weak: 0.2-0.4
- None: <0.2
```

### **Strategy Testing**
For each correlated pair:
1. **Entry Logic**: When to enter both positions
2. **Position Sizing**: Equal weight vs. weighted by confidence
3. **Exit Strategy**: Take profits on one? Hold both?
4. **Risk Assessment**: What if correlation breaks?

### **Performance Metrics**
- **Win Rate**: % of times both positions profit
- **Correlation Stability**: Does it hold over time?
- **Arbitrage Opportunities**: Market mispricing the correlation?

---

## 💰 Example Trade Scenarios

### **Scenario 1: Iran Strike Play** (Geopolitical + Commodities)
**Setup**:
- Iran strike odds: 30% → 45% (rising tension)
- Oil >$85 odds: 25% (currently at $78/barrel)

**Position**:
- $100 YES on Iran strike at 45% 
- $100 YES on Oil >$85 at 25%

**Outcomes**:
- ✅ **Strike happens + Oil spikes**: Win both (~$350 profit)
- ⚠️ **Strike happens + Oil stays flat**: Win one, lose one (~$50 profit)
- ❌ **No strike**: Lose both ($200 loss)

**Risk/Reward**: High risk, high reward. Best when you have edge on strike odds.

---

### **Scenario 2: Crypto Bull Hedge** (Amplify gains)
**Setup**:
- BTC >$100k by Dec: 40%
- ETH >$5k by Dec: 35%
- (Strong positive correlation)

**Position**:
- $150 YES BTC >$100k at 40%
- $100 YES ETH >$5k at 35%

**Logic**: If Bitcoin runs, Ethereum almost always follows. Amplify the play.

**Hedge Addition**: 
- $50 NO on "Major crypto regulation by Dec" at 20%
- If regulation kills the run, you recover some losses

---

### **Scenario 3: Trump Paradox** (Political hedge)
**Setup**:
- Trump indictment: 70% (likely)
- Trump wins primary: 55%
- Trump wins general: 42%

**Position** (exploit the divergence):
- $100 YES Trump indictment at 70%
- $100 YES Trump primary at 55%
- $100 NO Trump general at 42% (inverse)

**Logic**: Indictments boost primary, hurt general. Profit from the paradox.

---

### **Scenario 4: Fed + Stocks** (Economic hedge)
**Setup**:
- Fed hikes to 5.5%: 60%
- S&P 500 drops below 4000: 35%

**Position**:
- $100 YES Fed hikes at 60%
- $100 YES S&P <4000 at 35%

**Logic**: Rate hikes pressure stocks. If Fed stays aggressive, market suffers. Hedge against Fed pivot hopes.

---

## 🚨 Correlation Traps (What to Avoid)

### **False Correlations**
- **Narrative-driven, not data-driven**: Just because media links them doesn't mean they move together
- **Example**: "Taylor Swift dating → NFL ratings" (weak actual correlation)

### **Lagging Correlations**
- **Time delay problem**: Market A moves, Market B takes days/weeks
- **Risk**: First market already priced in by time you enter second

### **Broken Correlations**
- **Historical ≠ Future**: 2022 stocks + crypto both dropped. 2023 they diverged.
- **Regime changes**: Fed policy shifts can break decades-old correlations

### **Liquidity Risk**
- **Thin markets**: Correlated market might not have enough volume to enter/exit
- **Spread costs**: Bid-ask spread eats profits on smaller markets

---

## 📈 Action Plan for Live Trading

### **1. Market Monitoring**
- **Daily scan**: Check odds on correlated market pairs
- **Divergence alerts**: When correlation spreads widen (opportunity)
- **News monitoring**: Trigger events that activate correlations

### **2. Position Entry Checklist**
Before entering correlated positions:
- [ ] Verify correlation is currently active (check recent movements)
- [ ] Both markets have sufficient liquidity
- [ ] Timing makes sense (not already priced in)
- [ ] Risk tolerance allows for losing both positions
- [ ] Exit strategy defined

### **3. Portfolio Exposure**
- **Max 30% in correlated pairs**: Don't overconcentrate
- **Track correlation exposure**: Know your total downside if correlations break
- **Hedge key positions**: Use negative correlations to protect winners

---

## 🔍 Where to Find Correlation Data

### **Primary Sources**
1. **Polymarket Historical Data**: Download resolution outcomes
2. **News Impact Analysis**: Track how headlines move multiple markets
3. **Traditional Markets**: Oil, stocks, crypto prices as reference

### **Tools Needed**
- **Spreadsheet**: Track pairs, outcomes, timing
- **Correlation Calculator**: Measure strength over time windows
- **Alert System**: Notify when correlated markets diverge

### **Backtesting Workflow**
1. Identify potential correlation (theory/observation)
2. Pull 20+ historical examples
3. Calculate win rate if you'd bet both
4. Measure timing lag
5. Test across different market conditions
6. Validate before live trading

---

## 📝 Next Steps

### **Immediate Actions**
1. **Build correlation matrix**: List top 20 market pairs to track
2. **Historical analysis**: Pull past 6 months of data on known pairs
3. **Live monitoring**: Set up alerts for correlation divergences
4. **Paper trade**: Test strategies for 30 days before real money

### **Long-term Research**
- **Machine learning**: Can we predict correlation strength?
- **Cross-platform**: Do correlations hold across Polymarket, Kalshi, Manifold?
- **Seasonal patterns**: Do certain correlations strengthen at specific times?

---

## 🎓 Key Takeaways

✅ **Positive correlations = amplify gains** (or losses)  
✅ **Negative correlations = hedge risk**  
✅ **Time your entries** - correlation must still be active  
✅ **Size appropriately** - double exposure = double risk  
✅ **Validate with data** - don't trust narrative alone  
✅ **Monitor for breaks** - correlations change over time  

**The edge**: Markets often misprice correlations. When oil/Iran markets diverge but correlation is strong, there's alpha.

---

**Last Updated**: 2026-02-06  
**Status**: Framework complete, ready for live backtesting  
**Next**: Begin data collection on top 10 correlation pairs
