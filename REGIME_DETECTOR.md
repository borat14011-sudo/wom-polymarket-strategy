# Market Regime Detection System for Polymarket

## Overview

This document describes a comprehensive market regime detection system designed specifically for Polymarket prediction markets. The system automatically classifies market conditions across multiple dimensions and dynamically selects optimal trading strategies based on the detected regime.

## Key Characteristics of Polymarket

- **Binary/Categorical Outcomes**: Markets resolve to Yes/No or multiple discrete outcomes
- **Time-Decaying**: Prices converge to 0 or 1 as resolution approaches
- **Event-Driven**: News and external events cause sharp price movements
- **Liquidity Constraints**: Variable liquidity across markets
- **Implied Probability**: Prices represent probability estimates (0-1 range)

---

## 1. Volatility Regime Classification

### 1.1 Volatility Metrics for Prediction Markets

Unlike traditional markets, Polymarket volatility is measured differently:

```python
# Key volatility measures for prediction markets
volatility_metrics = {
    'price_volatility': 'Standard deviation of price changes',
    'implied_volatility': 'Derived from price movements relative to time',
    'range_volatility': 'High-low range normalized by price level',
    'velocity': 'Rate of price change (momentum)',
    'acceleration': 'Second derivative of price changes'
}
```

### 1.2 Realized Volatility Calculation

For prediction markets, we use modified volatility calculations:

```
Realized Volatility = sqrt(sum(log_returns^2) * 252)

Where log_returns for binary markets:
- If price > 0.5: log_return = log(price / previous_price)
- If price <= 0.5: Use adjusted log-odds: log(p/(1-p))
```

### 1.3 Volatility Regime Thresholds

| Regime | Annualized Volatility | Characteristics |
|--------|----------------------|-----------------|
| Low | < 30% | Stable prices, low uncertainty |
| Medium | 30% - 80% | Normal market conditions |
| High | > 80% | High uncertainty, event-driven moves |
| Extreme | > 150% | Crisis/regime change, major news |

### 1.4 Volatility Regime Detection Algorithm

Uses Hidden Markov Models (HMM) and regime-switching models:

- **State Identification**: Low, Medium, High volatility states
- **Transition Probabilities**: Markov chain for regime persistence
- **Duration Modeling**: Expected time in each regime

---

## 2. Market Sentiment Regime Detection

### 2.1 Sentiment Indicators for Prediction Markets

```python
sentiment_indicators = {
    'price_momentum': 'Trend direction and strength',
    'order_flow_imbalance': 'Buy vs sell pressure',
    'skewness': 'Asymmetry in return distribution',
    'market_breadth': 'Number of advancing vs declining markets',
    'funding_premium': 'Cost of carry implied in prices',
    'social_sentiment': 'External sentiment from news/social'
}
```

### 2.2 Sentiment Regime Classification

| Regime | Characteristics | Price Behavior |
|--------|----------------|----------------|
| Bullish | Strong upward momentum, positive skew | Prices trending toward resolution |
| Bearish | Strong downward momentum, negative skew | Prices moving away from resolution |
| Neutral | Mean-reverting, low momentum | Range-bound oscillation |
| Uncertain | High volatility, no clear direction | Choppy, unpredictable |
| Euphoric | Extreme optimism, parabolic moves | Unsustainable price levels |
| Panic | Extreme pessimism, capitulation | Sharp downward spikes |

### 2.3 Sentiment Score Construction

Composite sentiment index combining multiple factors:

```
Sentiment Score = w1*Momentum + w2*Flow + w3*Skew + w4*Breadth

Normalized to [-1, 1] range:
-1 = Extreme Bearish
 0 = Neutral
+1 = Extreme Bullish
```

---

## 3. Volume Regime Analysis

### 3.1 Volume Metrics

```python
volume_metrics = {
    'absolute_volume': 'Total USD volume traded',
    'relative_volume': 'Volume vs historical average',
    'volume_trend': 'Direction of volume changes',
    'volume_volatility': 'Variability in volume',
    'dollar_volume': 'Volume * price (liquidity proxy)',
    'trade_size_distribution': 'Distribution of trade sizes',
    'buy_sell_ratio': 'Aggressive buy vs sell volume'
}
```

### 3.2 Volume Regime Classification

| Regime | Relative Volume | Interpretation |
|--------|----------------|----------------|
| Low | < 50% of avg | Low interest, potential illiquidity |
| Normal | 50% - 150% of avg | Standard trading activity |
| Elevated | 150% - 300% of avg | Increased interest, potential breakout |
| Spike | > 300% of avg | News event, high conviction |
| Exhaustion | Spike followed by decline | Trend may be ending |

### 3.3 Volume-Price Relationship

Key patterns to detect:

- **Confirming Volume**: Volume increases with price trend (healthy)
- **Divergent Volume**: Volume decreases while price trends (weak)
- **Volume Climax**: Extreme volume spike (potential reversal)
- **Dry Up**: Volume collapse after trend (consolidation)

---

## 4. Correlation Regime Shifts

### 4.1 Correlation Analysis

In prediction markets, correlations matter between:

```python
correlation_types = {
    'cross_market': 'Correlation between different prediction markets',
    'cross_asset': 'Correlation with crypto/traditional assets',
    'cross_category': 'Politics vs Sports vs Crypto markets',
    'temporal': 'Correlation with past price behavior'
}
```

### 4.2 Correlation Regime States

| Regime | Correlation Level | Characteristics |
|--------|------------------|-----------------|
| Independent | < 0.3 | Markets move independently |
| Moderate | 0.3 - 0.7 | Some common factors driving prices |
| High | 0.7 - 0.9 | Strong common driver (macro event) |
| Crisis | > 0.9 | "Risk-on/Risk-off" behavior |
| Negative | < -0.3 | Hedging relationships active |

### 4.3 Dynamic Correlation Tracking

Uses rolling window correlations with:

- **Adaptive Windows**: Shorter windows for fast changes
- **Regime-Dependent**: Different correlation structures per regime
- **Lead-Lag**: Identifying which markets lead/lag

---

## 5. Strategy Performance by Regime

### 5.1 Strategy Database

| Strategy | Best Regime | Worst Regime | Description |
|----------|-------------|--------------|-------------|
| Momentum | High vol + Trend | Low vol + Range | Follow price trends |
| Mean Reversion | Low vol + Range | High vol + Trend | Fade extreme moves |
| Event Arbitrage | High vol + Uncertainty | Low vol + Stable | Trade around events |
| Liquidity Provision | Low vol + Normal vol | High vol + Spike | Market making |
| Time Decay | Any (time-dependent) | Pre-resolution | Exploit theta decay |
| Volatility | High vol transitions | Low vol stable | Trade volatility changes |
| Sentiment | Trending sentiment | Choppy/neutral | Follow sentiment signals |

### 5.2 Performance Metrics by Regime

Track for each strategy:

```python
regime_performance = {
    'sharpe_ratio': 'Risk-adjusted returns',
    'win_rate': 'Percentage of profitable trades',
    'profit_factor': 'Gross profit / gross loss',
    'max_drawdown': 'Peak to trough decline',
    'calmar_ratio': 'Return / max drawdown',
    'omega_ratio': 'Upside/downside potential',
    'regime_persistence': 'How long regime lasts'
}
```

### 5.3 Strategy Selection Matrix

```
                    Volatility Regime
                    Low    Medium    High
                   ┌──────┬────────┬──────┐
Sentiment Bullish │ MR   │ Mom    │ Mom  │
         Neutral  │ MR   │ Liq    │ Vol  │
         Bearish  │ MR   │ Mom    │ Mom  │
                   └──────┴────────┴──────┘

MR = Mean Reversion, Mom = Momentum, Liq = Liquidity Provision, Vol = Volatility
```

---

## 6. System Architecture

### 6.1 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA INPUTS                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Prices  │ │  Volume  │ │  Orders  │ │  Events  │       │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘       │
└───────┼────────────┼────────────┼────────────┼─────────────┘
        │            │            │            │
        └────────────┴────────────┴────────────┘
                       │
        ┌──────────────┴──────────────┐
        │    FEATURE ENGINEERING      │
        │  - Volatility measures      │
        │  - Sentiment indicators     │
        │  - Volume analytics         │
        │  - Correlation matrices     │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │    REGIME CLASSIFICATION    │
        │  - HMM State Detection      │
        │  - Ensemble Classifier      │
        │  - Regime Transition Model  │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │    STRATEGY SELECTOR        │
        │  - Performance Lookup       │
        │  - Risk Budget Allocation   │
        │  - Strategy Weighting       │
        └──────────────┬──────────────┘
                       │
        ┌──────────────┴──────────────┐
        │    EXECUTION ENGINE         │
        │  - Position Sizing          │
        │  - Risk Management          │
        │  - Order Execution          │
        └─────────────────────────────┘
```

### 6.2 Configuration Parameters

```yaml
regime_detection:
  volatility:
    lookback_window: 20
    regime_thresholds: [0.3, 0.8]  # Low/Medium/High
    smoothing_factor: 0.1
  
  sentiment:
    momentum_lookback: 10
    sentiment_window: 5
    threshold: 0.3
  
  volume:
    baseline_window: 30
    spike_threshold: 3.0
  
  correlation:
    rolling_window: 20
    min_observations: 10
  
strategy_allocation:
  max_strategies_active: 3
  min_confidence_threshold: 0.6
  rebalance_frequency: '1H'
  risk_budget_per_regime:
    low_volatility: 0.15
    medium_volatility: 0.25
    high_volatility: 0.10
```

---

## 7. Implementation

See `regime_detector.py` for full implementation including:

- `RegimeDetector` class - Main detection engine
- `VolatilityRegimeClassifier` - Volatility state identification
- `SentimentAnalyzer` - Market sentiment calculation
- `VolumeAnalyzer` - Volume regime detection
- `CorrelationMonitor` - Cross-market correlation tracking
- `StrategySelector` - Dynamic strategy allocation
- `TransitionDetector` - Regime change identification

---

## 8. Monitoring and Alerts

### 8.1 Regime Change Alerts

Trigger notifications when:
- Volatility regime shifts (especially to High/Extreme)
- Sentiment regime changes direction
- Volume spikes (> 3x normal)
- Correlation regime enters Crisis mode
- Multiple regimes change simultaneously

### 8.2 Performance Monitoring

Track in real-time:
- Current regime classification with confidence
- Active strategies and their weights
- Strategy performance vs. regime expectations
- False positive/negative regime detection rates

---

## 9. Risk Management

### 9.1 Regime-Based Risk Limits

| Regime | Max Position | Leverage | Stop Distance |
|--------|-------------|----------|---------------|
| Low Vol | 20% | 2x | 3% |
| Medium Vol | 15% | 1.5x | 5% |
| High Vol | 10% | 1x | 8% |
| Extreme | 5% | 1x | 10% |

### 9.2 Drawdown Protection

- Reduce exposure when entering high volatility regimes
- Close momentum strategies when sentiment reverses
- Increase cash allocation during uncertain regimes
- Dynamic position sizing based on regime persistence

---

## 10. Backtesting and Validation

### 10.1 Regime Identification Accuracy

- Historical regime labeling
- Confusion matrix for regime predictions
- Transition prediction accuracy
- False regime change rate

### 10.2 Strategy Performance Validation

- Out-of-sample performance by regime
- Walk-forward analysis
- Regime-conditional Sharpe ratios
- Drawdown analysis per regime

---

## Appendix A: Mathematical Formulations

### A.1 Hidden Markov Model for Regime Detection

```
States: S = {Low, Medium, High} volatility

Transition Matrix P:
    ┌                    ┐
    │ p11  p12  p13      │
P = │ p21  p22  p23      │
    │ p31  p32  p33      │
    └                    ┘

Emission probabilities based on observed volatility

Forward algorithm for state inference:
α_t(i) = P(o_1, ..., o_t, q_t = S_i | λ)
```

### A.2 Regime-Switching GARCH

```
r_t = μ_{s_t} + ε_t
ε_t = σ_{s_t,t} * z_t
σ²_{s_t,t} = ω_{s_t} + α_{s_t}*ε²_{t-1} + β_{s_t}*σ²_{t-1}

Where s_t ∈ {1, 2, ..., K} regime states
```

---

## References

1. Hamilton, J.D. (1989). "A New Approach to the Economic Analysis of Nonstationary Time Series"
2. Ang, A. & Bekaert, G. (2002). "International Asset Allocation with Regime Shifts"
3. Kritzman, M. et al. (2012). "Regime Shifts: Implications for Dynamic Strategies"
4. Polymarket Documentation: https://docs.polymarket.com

---

*Last Updated: 2025-02-08*
*Version: 1.0*
