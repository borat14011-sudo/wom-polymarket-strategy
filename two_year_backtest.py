"""
TWO-YEAR HISTORICAL SIMULATION
Starting Feb 2024 → Feb 2026

Strategies Tested:
1. Buy the Dip v2.1 (10%+ drop, time-filtered)
2. Near-Certainties (90%+ true prob at <85% price)
3. Hype Fade (spike-driven, bet NO)

Uses REAL Polymarket data from 93,949 markets
"""

import json
from datetime import datetime, timedelta
from collections import defaultdict
import random

# Load real market data
print("Loading 93,949 real markets...")
with open('markets_snapshot_20260207_221914.json', encoding='utf-8') as f:
    data = json.load(f)

markets = data['markets']
print(f"Loaded {len(markets)} markets")

# Parse dates and filter to 2024-2026 window
def parse_date(d):
    if not d:
        return None
    try:
        dt = datetime.fromisoformat(d.replace('Z', '+00:00'))
        return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
    except:
        return None

# Simulation parameters
from datetime import timezone
START_DATE = datetime(2024, 2, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 2, 1, tzinfo=timezone.utc)
INITIAL_CAPITAL = 100.0  # Starting with $100
TOTAL_COSTS = 0.055  # 5.5% roundtrip (fees + slippage)

# Strategy tracking
class Portfolio:
    def __init__(self, initial):
        self.capital = initial
        self.initial = initial
        self.trades = []
        self.positions = []
        self.trade_count = 0
        self.win_count = 0
        self.max_drawdown = 0
        self.peak = initial
        
    def execute_trade(self, market, entry_price, exit_price, is_yes, strategy, date):
        """Execute a trade with transaction costs"""
        # Position sizing: 2% for short-term, 1% for medium, 0.5% for long
        size = self.capital * 0.02  # 2% per trade
        
        # Calculate P&L
        if is_yes:
            if exit_price > entry_price:
                gross_return = (exit_price - entry_price) / entry_price
            else:
                gross_return = -1  # Total loss
        else:  # Bet NO
            if exit_price < entry_price:
                gross_return = (entry_price - exit_price) / (1 - entry_price)
            else:
                gross_return = -1
        
        # Apply transaction costs
        net_return = gross_return - TOTAL_COSTS if gross_return > -1 else gross_return
        pnl = size * net_return
        
        self.capital += pnl
        self.trade_count += 1
        if pnl > 0:
            self.win_count += 1
            
        # Track drawdown
        if self.capital > self.peak:
            self.peak = self.capital
        drawdown = (self.peak - self.capital) / self.peak
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            
        self.trades.append({
            'date': date,
            'market': market.get('question', '')[:50],
            'strategy': strategy,
            'entry': entry_price,
            'exit': exit_price,
            'pnl': pnl,
            'capital': self.capital
        })
        
        return pnl

# Strategy 1: Buy the Dip v2.1
def detect_dip_opportunity(market, current_date):
    """Detect >10% price drops in suitable timeframes"""
    price_change = market.get('price_change_7d')
    if not price_change:
        return None
    
    # Check for 10%+ drop
    if price_change >= -0.10:
        return None
    
    end_date = parse_date(market.get('end_date'))
    if not end_date:
        return None
    
    # Ensure both dates are comparable
    if current_date.tzinfo is None:
        current_date = current_date.replace(tzinfo=timezone.utc)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)
    days_to_resolution = (end_date - current_date).days
    
    # Time filter: <7 days OR >30 days
    if 7 <= days_to_resolution <= 30:
        return None  # Skip efficient window
    
    if days_to_resolution < 1 or days_to_resolution > 365:
        return None
    
    # Get current price
    prices = market.get('outcome_prices')
    if not prices or len(prices) < 2:
        return None
    
    yes_price = float(prices[0]) if prices[0] else 0.5
    
    # Avoid extremes
    if yes_price < 0.08 or yes_price > 0.92:
        return None
    
    # Volume check
    volume = market.get('volume', 0)
    if volume < 10000:
        return None
    
    return {
        'entry_price': yes_price,
        'exit_price': min(yes_price * 1.15, 0.95),  # Mean reversion target
        'is_yes': True,
        'days': days_to_resolution
    }

# Strategy 2: Near-Certainties
def detect_certainty_opportunity(market, current_date):
    """Markets with >90% true probability priced at <85%"""
    question = market.get('question', '').lower()
    
    # High-certainty keywords
    certainty_signals = [
        ('spacex', 'blue origin', 0.92),  # SpaceX vs Blue Origin
        ('gta vi', 'price', 0.95),         # GTA pricing
        ('trillion', 'musk', 0.90),        # Musk trillionaire
        ('climate', '2050', 0.95),         # Climate predictions
    ]
    
    for sig1, sig2, true_prob in certainty_signals:
        if sig1 in question and sig2 in question:
            prices = market.get('outcome_prices')
            if not prices:
                return None
            yes_price = float(prices[0]) if prices[0] else 0.5
            
            # Is it underpriced?
            if yes_price < 0.85 and yes_price > 0.50:
                return {
                    'entry_price': yes_price,
                    'exit_price': true_prob,  # Exit at true probability
                    'is_yes': True,
                    'edge': true_prob - yes_price
                }
    return None

# Strategy 3: Hype Fade
def detect_hype_fade_opportunity(market, current_date):
    """Markets that spiked on news/hype - bet NO"""
    question = market.get('question', '').lower()
    
    # Hype keywords (markets that tend to overreact)
    hype_signals = [
        'greenland', 'aliens', 'ufo', 'gold card', 'stimulus', 'purchase',
        'annex', 'martial law', 'pardon', 'resign'
    ]
    
    price_change = market.get('price_change_24h', 0) or 0
    price_change_7d = market.get('price_change_7d', 0) or 0
    
    # Look for spike (20%+ increase)
    if price_change_7d < 0.15:
        return None
    
    # Check if it matches hype signals
    if not any(sig in question for sig in hype_signals):
        return None
    
    prices = market.get('outcome_prices')
    if not prices:
        return None
    yes_price = float(prices[0]) if prices[0] else 0.5
    
    # Only bet NO on spiked markets in 20-60% range
    if yes_price < 0.20 or yes_price > 0.60:
        return None
    
    return {
        'entry_price': yes_price,
        'exit_price': yes_price * 0.6,  # Expect fade to 60% of spike
        'is_yes': False,
        'spike': price_change_7d
    }

# Run simulation
print("\n" + "="*60)
print("TWO-YEAR HISTORICAL SIMULATION")
print("Start: Feb 2024 | End: Feb 2026 | Capital: $100")
print("="*60)

portfolio = Portfolio(INITIAL_CAPITAL)

# Process markets chronologically
markets_with_dates = []
for m in markets:
    end_date = parse_date(m.get('end_date'))
    if end_date and START_DATE <= end_date <= END_DATE:
        markets_with_dates.append((end_date, m))

markets_with_dates.sort(key=lambda x: x[0])
print(f"\nMarkets in Feb 2024 - Feb 2026 window: {len(markets_with_dates)}")

# Simulate month by month
monthly_pnl = defaultdict(float)
strategy_stats = defaultdict(lambda: {'trades': 0, 'wins': 0, 'pnl': 0})

for end_date, market in markets_with_dates:
    # Simulate entry ~14 days before resolution
    entry_date = end_date - timedelta(days=14)
    # Ensure entry_date is timezone-aware
    if entry_date.tzinfo is None:
        entry_date = entry_date.replace(tzinfo=timezone.utc)
    if entry_date < START_DATE:
        continue
    
    # Check for opportunities
    opportunities = []
    
    dip = detect_dip_opportunity(market, entry_date)
    if dip:
        opportunities.append(('Buy the Dip', dip))
    
    certainty = detect_certainty_opportunity(market, entry_date)
    if certainty:
        opportunities.append(('Near-Certainty', certainty))
    
    hype = detect_hype_fade_opportunity(market, entry_date)
    if hype:
        opportunities.append(('Hype Fade', hype))
    
    for strategy, opp in opportunities:
        # Simulate trade outcome based on market resolution
        winner = market.get('outcome_winner')
        if winner is None:
            continue  # Skip unresolved
        
        # Determine actual exit price based on outcome
        if winner == 'YES':
            exit_price = 1.0 if opp['is_yes'] else 0.0
        else:
            exit_price = 0.0 if opp['is_yes'] else 1.0
        
        pnl = portfolio.execute_trade(
            market, 
            opp['entry_price'], 
            exit_price,
            opp['is_yes'],
            strategy,
            entry_date
        )
        
        month_key = entry_date.strftime('%Y-%m')
        monthly_pnl[month_key] += pnl
        
        strategy_stats[strategy]['trades'] += 1
        strategy_stats[strategy]['pnl'] += pnl
        if pnl > 0:
            strategy_stats[strategy]['wins'] += 1

# Results
print("\n" + "="*60)
print("SIMULATION RESULTS")
print("="*60)

print(f"\n[PORTFOLIO PERFORMANCE]")
print(f"  Starting Capital: ${INITIAL_CAPITAL:.2f}")
print(f"  Final Capital:    ${portfolio.capital:.2f}")
print(f"  Total Return:     {((portfolio.capital - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100:.1f}%")
print(f"  Max Drawdown:     {portfolio.max_drawdown * 100:.1f}%")
print(f"  Total Trades:     {portfolio.trade_count}")
print(f"  Win Rate:         {(portfolio.win_count / portfolio.trade_count * 100) if portfolio.trade_count else 0:.1f}%")

print(f"\n[STRATEGY BREAKDOWN]")
for strategy, stats in sorted(strategy_stats.items()):
    win_rate = (stats['wins'] / stats['trades'] * 100) if stats['trades'] else 0
    print(f"\n  {strategy}:")
    print(f"    Trades: {stats['trades']}")
    print(f"    Win Rate: {win_rate:.1f}%")
    print(f"    P&L: ${stats['pnl']:.2f}")

print(f"\n[MONTHLY P&L]")
for month in sorted(monthly_pnl.keys()):
    pnl = monthly_pnl[month]
    bar = "+" * int(abs(pnl)) if pnl > 0 else "-" * int(abs(pnl))
    print(f"  {month}: ${pnl:+.2f} {bar[:20]}")

# Save detailed results
results = {
    'simulation': {
        'start_date': START_DATE.isoformat(),
        'end_date': END_DATE.isoformat(),
        'initial_capital': INITIAL_CAPITAL,
        'final_capital': portfolio.capital,
        'total_return_pct': ((portfolio.capital - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100,
        'max_drawdown_pct': portfolio.max_drawdown * 100,
        'total_trades': portfolio.trade_count,
        'win_rate': (portfolio.win_count / portfolio.trade_count * 100) if portfolio.trade_count else 0
    },
    'strategy_breakdown': dict(strategy_stats),
    'monthly_pnl': dict(monthly_pnl),
    'trades': portfolio.trades[-100:]  # Last 100 trades
}

with open('TWO_YEAR_BACKTEST_RESULTS.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)

print(f"\n[OK] Results saved to TWO_YEAR_BACKTEST_RESULTS.json")
