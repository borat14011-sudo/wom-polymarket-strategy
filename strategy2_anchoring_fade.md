# Strategy 2: Anchoring Breakout Fade (ABF)

## Behavioral Framework
**Core Hypothesis**: Prices in prediction markets cluster around psychological anchors (round numbers like 0.25, 0.50, 0.75), creating temporary resistance/support. When prices break these levels due to minor news, they often overshoot and then revert to the anchor zone.

**Psychological Basis**:
- **Anchoring Bias**: Traders mentally anchor to round numbers as reference points
- **Disposition Effect**: Traders reluctant to realize losses, causing clustering
- **Round Number Heuristic**: Cognitive ease of processing round numbers

**Market Mechanism**:
1. Prices gravitate to nearest round number (anchor)
2. Minor news causes temporary breakout
3. Market overreacts due to anchor break "significance"
4. Prices mean-revert back to anchor zone
5. Fade the breakout for profit

## Event Detection Requirements

### Anchor Identification:
1. **Primary Anchors**: 0.10, 0.25, 0.33, 0.50, 0.66, 0.75, 0.90
2. **Secondary Anchors**: 0.05 increments (0.05, 0.15, ..., 0.95)
3. **Dynamic Anchors**: Recent high/low prices, opening prices

### Breakout Detection:
```
IF (price has spent >12h within 2% of anchor)
AND (price breaks >5% away from anchor within 6h)
AND (breakout volume < 3x average)  // Minor news, not major
THEN trigger_fade_signal
```

### News Significance Filter:
- **Major News Exclusion**: If >10 news articles in past 6h about topic
- **Social Media Exclusion**: If Twitter mentions >2σ above average
- **Volume Exclusion**: If trading volume >5x daily average

## Trading Logic

### Entry Conditions:
1. **Direction**: Fade the breakout (bet opposite direction)
2. **Timing**: Enter within 2 hours of breakout confirmation
3. **Position Size**: 1-2% of capital ($0.10-$0.20)
4. **Price Level**: Enter when price is 4-8% beyond anchor

### Exit Conditions:
1. **Target**: Return to anchor zone (within 2% of anchor)
2. **Stop Loss**: 8% beyond entry (total 12-16% from anchor)
3. **Time Limit**: 48 hours maximum hold
4. **Partial Exit**: 50% at 4% profit, remainder at anchor return

## Expected Performance Metrics

### Win Rate Target: 55-60%
- Anchors provide strong psychological support/resistance

### Average Return per Trade: 6% (gross)
- Net return after fees: 2% (6% - 4% fees)
- Lower than ADA due to smaller moves

### Position Frequency: 3-5 trades per week
- Many markets cluster at anchors

### Annualized Return Estimate:
```
Assuming: 4 trades/week * 52 weeks = 208 trades
Average net return: 2% per trade
Capital per trade: 1.5% avg ($0.15)
Compound return: ~55% annual (conservative)
```

### Risk Metrics:
- Max drawdown: 10-15%
- Sharpe ratio: 1.0-1.3
- Win/Loss ratio: 1.5-1.8

## Implementation Requirements

### Data Sources:
1. **Polymarket API**: Real-time price feeds
2. **News Sentiment API**: Minor vs. major news classification
3. **Volume Analytics**: Breakout volume analysis

### Technical Infrastructure:
1. **Anchor Detection Engine**: Identify price clustering patterns
2. **Breakout Classifier**: Distinguish minor vs. major breakouts
3. **Real-time Monitoring**: Track all markets for anchor proximity
4. **Backtesting Suite**: Test on historical anchor behaviors

### Key Parameters to Optimize:
1. **Anchor sensitivity**: How close to round number defines "at anchor"?
2. **Breakout threshold**: What % move constitutes a breakout?
3. **News significance threshold**: How to filter major vs. minor news?
4. **Exit strategy**: Fixed target vs. dynamic return to anchor

### Validation Steps:
1. **Historical analysis**: Study anchor behavior in 2,600+ resolved markets
2. **Clustering quantification**: Measure price time at various anchors
3. **Breakout reversion rate**: Statistical significance testing
4. **Paper trading**: 30-day simulation with live data

## Unique Advantages
1. **High-frequency opportunities**: Many anchors across many markets
2. **Clear signals**: Breakouts are objectively measurable
3. **Psychological robustness**: Anchoring bias is well-documented
4. **Low data requirements**: Primarily price data needed

## Potential Risks
1. **Structural breakouts**: When anchor breaks due to fundamental change
2. **Liquidity gaps**: Thin markets may not respect anchors
3. **Multiple anchors**: Conflicting anchor zones
4. **Market evolution**: Anchoring effects may weaken over time

## Mitigations
1. **Fundamental filters**: Exclude markets with imminent resolutions
2. **Liquidity requirements**: Minimum $1,000 daily volume
3. **Anchor hierarchy**: Weight primary anchors more heavily
4. **Adaptive thresholds**: Adjust based on recent market behavior

## Special Considerations for Polymarket
1. **Binary nature**: Anchors may be stronger in binary markets
2. **Resolution proximity**: Avoid markets resolving within 7 days
3. **Fee impact**: 4% round-trip requires careful entry/exit timing
4. **Slippage management**: Use limit orders near anchor zones