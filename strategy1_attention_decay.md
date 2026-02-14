# Strategy 1: Attention Decay Arbitrage (ADA)

## Behavioral Framework
**Core Hypothesis**: Attention to prediction market events follows a predictable decay curve (exponential), but market prices adjust linearly, creating mean-reversion opportunities after attention spikes.

**Psychological Basis**:
- **Availability Heuristic**: Recent dramatic events are overweighted in probability estimates
- **Recency Bias**: Traders focus on what's most salient, not what's most probable
- **Attention Fatigue**: Sustained focus on any single event is cognitively expensive

**Market Mechanism**:
1. Breaking news or event causes attention spike
2. Prices move dramatically (often overshooting)
3. Attention decays exponentially over 24-72 hours
4. Prices slowly mean-revert as attention fades
5. Gap between attention decay and price adjustment creates arbitrage

## Event Detection Requirements

### Input Signals:
1. **Social Media Volume**: Twitter/X mentions, Reddit posts about market topic
2. **News Mentions**: Count of news articles referencing event
3. **Google Trends**: Search volume for related keywords
4. **Market Metrics**: Trading volume spike (>5x daily average)
5. **Price Movement**: >15% move within 24h window

### Detection Algorithm:
```
IF (social_volume > 2σ above 7d avg) 
AND (price_move > 15%)
AND (time_since_spike > 24h)  // Avoid catching initial move
THEN trigger_strategy
```

### Attention Decay Model:
```
Attention(t) = A * e^(-λt)
Where:
A = initial attention magnitude
λ = decay constant (empirically ~0.5/day for news events)
t = time since peak attention
```

## Trading Logic

### Entry Conditions:
1. **Timing**: 24-48 hours after attention peak
2. **Position**: Bet AGAINST the direction of initial spike
   - If spike drove prices UP, take NO position
   - If spike drove prices DOWN, take YES position
3. **Size**: 1-2% of capital ($0.10-$0.20)
4. **Price Filter**: Only if move exceeded 20% (ensures overshoot)

### Exit Conditions:
1. **Time-based**: Hold for 3-7 days (attention decay completion)
2. **Profit Target**: 8-12% gain (net of fees)
3. **Stop Loss**: 6% loss (prevents catastrophic failures)
4. **Attention Normalization**: When social volume returns to baseline

## Expected Performance Metrics

### Win Rate Target: 60-65%
- Based on mean-reversion tendency in overshoot scenarios

### Average Return per Trade: 8% (gross)
- Net return after fees: 4% (8% - 4% fees)

### Position Frequency: 2-4 trades per week
- Given 200 active markets and attention spikes

### Annualized Return Estimate:
```
Assuming: 3 trades/week * 52 weeks = 156 trades
Average net return: 4% per trade
Capital per trade: 1.5% avg ($0.15)
Compound return: ~85% annual (conservative)
```

### Risk Metrics:
- Max drawdown: 15-20%
- Sharpe ratio: 1.2-1.5
- Win/Loss ratio: 1.8-2.0

## Implementation Requirements

### Data Sources:
1. **Twitter API** for mention tracking
2. **Google Trends API** for search volume
3. **News API** (NewsAPI.org, GDELT)
4. **Polymarket API** for price/volume data

### Technical Infrastructure:
1. **Real-time monitoring**: Webhook-based alert system
2. **Attention scoring engine**: Calculate attention scores for all markets
3. **Backtesting framework**: Test on 2,600+ resolved markets
4. **Execution bot**: Automate trade entry/exit via Polymarket API

### Key Parameters to Optimize:
1. **Attention spike threshold**: What constitutes a significant spike?
2. **Entry delay**: Optimal time after spike (24h, 36h, 48h?)
3. **Position sizing**: Based on spike magnitude
4. **Exit timing**: Fixed period vs. attention normalization

### Validation Steps:
1. **Historical analysis**: Apply to 2,600 resolved markets
2. **Paper trading**: 30-day simulation
3. **Small-scale live**: $1-2 capital initially
4. **Full deployment**: After positive validation

## Unique Advantages
1. **Behavioral edge**: Explores systematic cognitive bias
2. **Scalable**: Works across all market types
3. **Data-rich**: Multiple independent signals
4. **Automation-friendly**: Clear trigger conditions

## Potential Risks
1. **Structural breaks**: Events that truly change probabilities
2. **Liquidity issues**: Slippage in small markets
3. **Model decay**: Attention patterns may change over time
4. **API costs**: Data acquisition expenses

## Mitigations
1. **Exclude major structural events** (elections, major announcements)
2. **Minimum liquidity filter**: $500+ volume in past 24h
3. **Regular model retraining**: Weekly parameter updates
4. **Cost management**: Use free tier APIs where possible