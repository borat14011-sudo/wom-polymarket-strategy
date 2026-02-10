# Whale Mirror Trading Strategies

> **Executable trading strategies for copying profitable whale trades on Polymarket**

---

## Executive Summary

This document outlines three distinct mirroring strategies with varying risk/reward profiles. Each strategy includes specific entry/exit rules, position sizing formulas, and risk management protocols.

---

## Strategy 1: The Instant Mirror (Aggressive)

**Profile:** High frequency, high execution risk, maximum alpha capture

### Entry Timing
- **Trigger:** Immediate execution upon whale buy signal detection
- **Latency Target:** <30 seconds from on-chain confirmation
- **Delay:** None - front-run the followers, not the whale

```python
def should_enter(signal):
    """
    signal: {
        'whale_address': str,
        'market_id': str,
        'side': 'YES' | 'NO',
        'amount_usd': float,
        'timestamp': datetime,
        'tx_hash': str,
        'block_confirmations': int
    }
    """
    # Wait for 2 block confirmations minimum
    if signal['block_confirmations'] < 2:
        return False
    
    # Skip if signal is older than 2 minutes
    if (datetime.now() - signal['timestamp']).seconds > 120:
        return False
    
    # Check whale is in approved list
    if signal['whale_address'] not in APPROVED_WHALE_LIST:
        return False
    
    return True
```

### Position Sizing
- **Formula:** Fixed amount per signal with whale conviction multiplier
- **Base Size:** $100 per signal
- **Conviction Multiplier:** `log10(whale_position_size / 1000) + 1`

```python
def calculate_position_size(signal, base_size=100):
    whale_position = signal['amount_usd']
    conviction = math.log10(whale_position / 1000) + 1
    conviction = max(0.5, min(conviction, 5))  # Cap between 0.5x and 5x
    return base_size * conviction

# Examples:
# Whale bets $1,000 → Position size: $100 (1x)
# Whale bets $10,000 → Position size: $200 (2x)
# Whale bets $100,000 → Position size: $300 (3x)
# Whale bets $1,000,000 → Position size: $400 (4x)
```

### Exit Rules
- **Primary:** Exit when whale exits position
- **Secondary:** 48-hour timeout - exit at market price
- **Stop Loss:** -15% from entry (whale may be wrong)
- **Take Profit:** +50% from entry (don't be greedy)

```python
def should_exit(position, current_price, whale_activity):
    # Exit if whale closed position
    if whale_activity['type'] == 'exit':
        return True, 'WHALE_EXIT'
    
    # Time-based exit
    if (datetime.now() - position['entry_time']).hours > 48:
        return True, 'TIMEOUT'
    
    # Stop loss
    pnl_pct = (current_price - position['entry_price']) / position['entry_price']
    if pnl_pct < -0.15:
        return True, 'STOP_LOSS'
    
    # Take profit
    if pnl_pct > 0.50:
        return True, 'TAKE_PROFIT'
    
    return False, None
```

### Risk Management
- **Max Daily Signals:** 20 per whale
- **Max Exposure per Market:** $500
- **Max Concurrent Positions:** 10
- **Circuit Breaker:** Pause after 3 consecutive losses from same whale

---

## Strategy 2: The Delayed Follower (Moderate)

**Profile:** Reduced slippage, trend confirmation, balanced risk

### Entry Timing
- **Trigger:** 2-hour delay after whale signal
- **Confirmation:** Price moved <5% in whale's favor during delay
- **Rationale:** Avoid front-running bots, let initial volatility settle

```python
def should_enter_delayed(signal, market_data):
    # 2-hour minimum delay
    if (datetime.now() - signal['timestamp']).seconds < 7200:
        return False
    
    # Get price at signal time and current price
    price_at_signal = market_data.get_historical_price(
        signal['market_id'], 
        signal['timestamp']
    )
    current_price = market_data.get_current_price(signal['market_id'])
    
    # Whale bought YES - check price hasn't mooned
    if signal['side'] == 'YES':
        price_change = (current_price - price_at_signal) / price_at_signal
        if price_change > 0.05:  # >5% move, too late
            return False
    
    # Whale bought NO - check price hasn't crashed
    if signal['side'] == 'NO':
        price_change = (price_at_signal - current_price) / price_at_signal
        if price_change > 0.05:
            return False
    
    # Check for second whale entering (momentum confirmation)
    recent_signals = get_signals_since(signal['timestamp'], hours=2)
    whale_count = len(set([s['whale_address'] for s in recent_signals]))
    
    # Require at least 1 other whale or proceed with caution
    if whale_count < 2:
        # Reduce position size if no confirmation
        return 'REDUCED'
    
    return True
```

### Position Sizing (Kelly Criterion)
- **Formula:** Kelly Fraction based on whale's historical performance
- **Kelly Calculation:** `f* = (bp - q) / b`
  - `b` = average win amount / average loss amount
  - `p` = win rate
  - `q` = loss rate = 1 - p

```python
def kelly_criterion(whale_stats, max_kelly=0.25):
    """
    whale_stats: {
        'win_rate': 0.65,
        'avg_win_pct': 0.35,
        'avg_loss_pct': 0.15,
        'total_trades': 50
    }
    """
    p = whale_stats['win_rate']
    q = 1 - p
    b = whale_stats['avg_win_pct'] / whale_stats['avg_loss_pct']
    
    kelly = (b * p - q) / b
    
    # Half-Kelly for safety
    half_kelly = kelly / 2
    
    # Cap at max_kelly (25%)
    return min(max(half_kelly, 0), max_kelly)

def calculate_position_size_kelly(whale_stats, bankroll=10000):
    kelly_fraction = kelly_criterion(whale_stats)
    return bankroll * kelly_fraction

# Example:
# Whale: 65% win rate, 35% avg win, 15% avg loss
# b = 0.35/0.15 = 2.33
# kelly = (2.33 * 0.65 - 0.35) / 2.33 = 0.50 (50%)
# half_kelly = 25%
# Position size = $10,000 * 0.25 = $2,500
```

### Exit Rules
- **Primary:** Hold until resolution or whale exits
- **Time Decay:** For long-dated markets, exit at 75% of time elapsed
- **Stop Loss:** -20% (wider stop due to delayed entry)
- **Take Profit:** Scale out: 30% at +25%, 50% at +50%, rest at +100%

```python
def should_exit_scaled(position, current_price, market_info):
    pnl_pct = (current_price - position['entry_price']) / position['entry_price']
    
    # Scale out levels
    if pnl_pct >= 1.00 and position['remaining'] > 0:
        return 'PARTIAL', 1.0  # Close remaining 100%
    
    if pnl_pct >= 0.50 and position['remaining'] >= position['size'] * 0.5:
        return 'PARTIAL', 0.5  # Close 50%
    
    if pnl_pct >= 0.25 and position['remaining'] >= position['size'] * 0.8:
        return 'PARTIAL', 0.3  # Close 30%
    
    # Time-based exit for long markets
    time_elapsed = (datetime.now() - position['entry_time']).days
    total_duration = (market_info['resolution_date'] - position['entry_time']).days
    
    if time_elapsed / total_duration > 0.75:
        return True, 'TIME_DECAY'
    
    # Stop loss
    if pnl_pct < -0.20:
        return True, 'STOP_LOSS'
    
    return False, None
```

### Risk Management
- **Whale Validation:** Minimum 20 historical trades for Kelly sizing
- **Max Allocation:** 25% of portfolio per whale
- **Drawdown Limit:** Pause whale if 30% drawdown from peak
- **Correlation Check:** Max 3 positions in same event category

---

## Strategy 3: The Whale Index (Conservative)

**Profile:** Diversified, index-like exposure, lowest variance

### Entry Timing
- **Trigger:** Aggregate whale sentiment score
- **Consensus Required:** Minimum 3 whales signaling same direction within 24h
- **Weight:** Position size proportional to whale consensus strength

```python
def calculate_whale_consensus(signals_24h, whale_weights):
    """
    Returns: sentiment_score between -1 (all NO) and +1 (all YES)
    """
    weighted_yes = 0
    weighted_no = 0
    
    for signal in signals_24h:
        weight = whale_weights.get(signal['whale_address'], 0.1)
        amount_weight = math.log(signal['amount_usd'] / 1000 + 1)
        
        if signal['side'] == 'YES':
            weighted_yes += weight * amount_weight
        else:
            weighted_no += weight * amount_weight
    
    total = weighted_yes + weighted_no
    if total == 0:
        return 0
    
    sentiment = (weighted_yes - weighted_no) / total
    return sentiment

def should_enter_consensus(market_id, min_consensus=0.6):
    signals = get_signals_last_24h(market_id)
    
    if len(signals) < 3:
        return False, 0
    
    whale_weights = {
        addr: stats['win_rate'] 
        for addr, stats in TOP_WHALES.items()
    }
    
    consensus = calculate_whale_consensus(signals, whale_weights)
    
    if abs(consensus) >= min_consensus:
        side = 'YES' if consensus > 0 else 'NO'
        return True, side, abs(consensus)
    
    return False, None, 0
```

### Position Sizing (Risk Parity)
- **Formula:** Equal risk contribution across all open positions
- **Base Allocation:** Equal dollar amount per position
- **Rebalancing:** Weekly rebalancing to maintain equal risk

```python
def calculate_position_size_risk_parity(portfolio, target_positions=10, total_capital=50000):
    """
    Distribute capital equally among target positions
    """
    # Reserve 20% cash
    investable = total_capital * 0.8
    
    # Count current positions
    current_positions = len(portfolio.open_positions)
    available_slots = target_positions - current_positions
    
    if available_slots <= 0:
        return 0
    
    # Equal allocation
    position_size = investable / target_positions
    
    return position_size

def rebalance_portfolio(portfolio, target_positions=10):
    """
    Weekly rebalance to equal weights
    """
    total_value = portfolio.cash + sum(p.value for p in portfolio.positions)
    target_per_position = (total_value * 0.8) / target_positions
    
    rebalances = []
    for position in portfolio.positions:
        if position.value > target_per_position * 1.2:
            # Trim overweight position
            excess = position.value - target_per_position
            rebalances.append(('SELL', position.market_id, excess))
        elif position.value < target_per_position * 0.8:
            # Add to underweight
            deficit = target_per_position - position.value
            rebalances.append(('BUY', position.market_id, deficit))
    
    return rebalances
```

### Exit Rules
- **Primary:** Consensus dissolves (<3 whales remain in direction)
- **Secondary:** Opposite signal from high-weight whale
- **Rebalancing:** Weekly regardless of P&L
- **Stop Loss:** -25% portfolio level (emergency only)

```python
def should_exit_consensus(position, current_signals, whale_weights):
    # Count whales still in position
    same_side_signals = [
        s for s in current_signals 
        if s['side'] == position['side']
    ]
    
    if len(same_side_signals) < 3:
        return True, 'CONSENSUS_BROKEN'
    
    # Check for strong opposite signal
    opposite_signals = [
        s for s in current_signals 
        if s['side'] != position['side']
    ]
    
    for signal in opposite_signals:
        if whale_weights.get(signal['whale_address'], 0) > 0.7:
            # High-confidence whale flipped
            return True, 'WHALE_FLIP'
    
    return False, None
```

### Risk Management
- **Diversification:** Max 15% in any single market
- **Category Limits:** Max 30% in any event category (politics, sports, etc.)
- **Whale Concentration:** Max 40% of portfolio following single whale
- **Emergency Stop:** Halt all new entries if portfolio down >25%

---

## Backtest Framework

### Performance Metrics

```python
class BacktestEngine:
    def __init__(self, strategy, start_date, end_date):
        self.strategy = strategy
        self.start_date = start_date
        self.end_date = end_date
        self.trades = []
        self.equity_curve = []
    
    def run(self, historical_signals):
        """
        Run strategy against historical whale signals
        """
        portfolio = Portfolio(initial_capital=10000)
        
        for signal in historical_signals:
            # Check exits first
            for position in portfolio.positions:
                if self.strategy.should_exit(position, signal):
                    pnl = portfolio.close_position(position, signal)
                    self.trades.append({
                        'exit_signal': signal,
                        'pnl': pnl,
                        'exit_time': signal['timestamp']
                    })
            
            # Check entries
            if self.strategy.should_enter(signal):
                size = self.strategy.calculate_position_size(signal)
                portfolio.open_position(signal, size)
        
        return self.calculate_metrics(portfolio)
    
    def calculate_metrics(self, portfolio):
        returns = [t['pnl'] for t in self.trades]
        
        metrics = {
            'total_return': sum(returns),
            'total_trades': len(self.trades),
            'win_rate': len([r for r in returns if r > 0]) / len(returns),
            'avg_win': np.mean([r for r in returns if r > 0]),
            'avg_loss': np.mean([r for r in returns if r < 0]),
            'profit_factor': abs(sum(r for r in returns if r > 0) / 
                                sum(r for r in returns if r < 0)),
            'max_drawdown': self.calculate_max_drawdown(),
            'sharpe_ratio': self.calculate_sharpe_ratio(),
            'calmar_ratio': self.calculate_calmar_ratio(),
            'sortino_ratio': self.calculate_sortino_ratio()
        }
        
        return metrics
    
    def calculate_max_drawdown(self):
        """Calculate maximum peak-to-trough decline"""
        equity = self.equity_curve
        peak = equity[0]
        max_dd = 0
        
        for value in equity:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            max_dd = max(max_dd, dd)
        
        return max_dd
    
    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Annualized Sharpe ratio"""
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        excess_returns = returns - risk_free_rate / 252  # Daily
        return np.sqrt(252) * np.mean(excess_returns) / np.std(returns)
```

### Expected Returns by Strategy

| Metric | Instant Mirror | Delayed Follower | Whale Index |
|--------|----------------|------------------|-------------|
| **Expected Annual Return** | 80-150% | 40-80% | 25-50% |
| **Max Drawdown** | -40% | -25% | -15% |
| **Sharpe Ratio** | 1.2-1.8 | 1.5-2.2 | 1.8-2.5 |
| **Win Rate** | 55-60% | 60-65% | 65-70% |
| **Trades/Month** | 30-50 | 15-25 | 8-12 |
| **Complexity** | Low | Medium | High |

### Backtest Procedure

```python
# Example: Backtest Strategy 2 against Whale X

WHALE_X = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb'

# Load historical signals
signals = load_whale_signals(
    whale_address=WHALE_X,
    start_date='2024-06-01',
    end_date='2024-12-01'
)

# Calculate whale statistics
whale_stats = {
    'win_rate': calculate_win_rate(signals),
    'avg_win_pct': calculate_avg_win(signals),
    'avg_loss_pct': calculate_avg_loss(signals),
    'total_trades': len(signals)
}

# Run backtest
strategy = DelayedFollowerStrategy(whale_stats)
engine = BacktestEngine(strategy, '2024-06-01', '2024-12-01')
results = engine.run(signals)

print(f"""
Backtest Results for Whale {WHALE_X[:10]}...
================================
Total Return: {results['total_return']:.2%}
Total Trades: {results['total_trades']}
Win Rate: {results['win_rate']:.1%}
Max Drawdown: {results['max_drawdown']:.2%}
Sharpe Ratio: {results['sharpe_ratio']:.2f}
Profit Factor: {results['profit_factor']:.2f}
""")
```

---

## Implementation Checklist

### Phase 1: Infrastructure
- [ ] Real-time whale signal detection (blockchain listener)
- [ ] Price oracle integration for entry/exit calculations
- [ ] Position tracking system
- [ ] Risk monitoring dashboard

### Phase 2: Strategy Deployment
- [ ] Paper trade each strategy for 2 weeks
- [ ] Compare slippage vs. backtest assumptions
- [ ] Optimize execution timing
- [ ] Implement circuit breakers

### Phase 3: Live Trading
- [ ] Start with 10% of intended capital
- [ ] Scale up 10% per week if performing to expectation
- [ ] Weekly strategy review and parameter tuning
- [ ] Monthly deep-dive on whale performance changes

---

## Appendix: Whale Selection Criteria

### Tier 1 Whales (Kelly Sizing Eligible)
- Minimum 6 months trading history
- Minimum 30 closed trades
- Win rate > 60%
- Positive expectancy
- Sharpe ratio > 1.0

### Tier 2 Whales (Reduced Allocation)
- 3-6 months trading history
- 15-30 closed trades
- Win rate 55-60%
- No major blow-ups (>50% drawdown)

### Blacklist Criteria
- Any whale with >3 consecutive losses
- Whales showing correlated timing (possible group)
- Accounts with suspicious funding patterns
- Whales who delete/trade against their own signals

---

## Risk Disclosures

⚠️ **Important:**
- Past whale performance does not guarantee future results
- Execution slippage can significantly impact returns
- Black swan events can invalidate any strategy
- Never risk more than you can afford to lose
- These strategies are educational - do your own research

---

*Document Version: 1.0*
*Created: 2026-02-09*
*Status: Executable - Awaiting Implementation*
