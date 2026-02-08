#!/usr/bin/env python3
"""
Price-Based Backtest - Use final prices as outcome proxies
Simple, fast, directional insights
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"POLYMARKET PRICE-PROXY BACKTEST")
print(f"Rule: Final price >0.90 = YES won, <0.10 = NO won")
print(f"{'='*70}\n")

# Load dataset
print("Loading dataset...")
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    dataset = json.load(f)
print(f"[OK] {len(dataset):,} markets loaded\n")

# ============================================================
# STRATEGY 1: TREND FILTER
# ============================================================
def backtest_trend_filter(markets):
    """Only buy when price is trending UP"""
    print(f"{'='*70}")
    print(f"STRATEGY 1: TREND FILTER")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 20:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome from final price
        if final_price > 0.90:
            outcome = 'Yes'
        elif final_price < 0.10:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue  # Skip ambiguous
        
        # Check each price point as potential entry
        for i in range(3, len(prices) - 5):  # Leave room for exit
            current_price = prices[i].get('p', 0)
            prev_prices = [prices[i-j].get('p', 0) for j in range(1, 4)]
            
            # Trend filter: price must be rising
            if current_price > prev_prices[0] > prev_prices[1]:
                entry_price = current_price
                
                # Simulate trade outcome
                if outcome == 'Yes':
                    pnl = final_price - entry_price
                else:
                    pnl = (1 - final_price) - (1 - entry_price)
                
                win = pnl > 0
                
                trades.append({
                    'market': market['question'][:60],
                    'entry': entry_price,
                    'exit': final_price,
                    'inferred_outcome': outcome,
                    'pnl': pnl,
                    'win': win
                })
                break  # One trade per market
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    print(f"Results:")
    print(f"  Trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print()
    
    return {
        'strategy': 'Trend Filter',
        'trades': total,
        'wins': wins,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'skipped': skipped_ambiguous
    }

# ============================================================
# STRATEGY 2: TIME HORIZON <3 DAYS
# ============================================================
def backtest_time_horizon(markets):
    """Short-term markets perform better"""
    print(f"{'='*70}")
    print(f"STRATEGY 2: TIME HORIZON <3 DAYS")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        # Calculate duration
        start = market.get('start_date')
        end = market.get('end_date')
        if not start or not end:
            continue
        
        try:
            from datetime import datetime
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).days
        except:
            continue
        
        # Filter: <3 days only
        if duration >= 3:
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 10:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome
        if final_price > 0.90:
            outcome = 'Yes'
        elif final_price < 0.10:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # Entry at midpoint
        mid_idx = len(prices) // 2
        entry_price = prices[mid_idx].get('p', 0)
        
        # Simulate
        if outcome == 'Yes':
            pnl = final_price - entry_price
        else:
            pnl = (1 - final_price) - (1 - entry_price)
        
        win = pnl > 0
        
        trades.append({
            'market': market['question'][:60],
            'duration_days': duration,
            'entry': entry_price,
            'exit': final_price,
            'pnl': pnl,
            'win': win
        })
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    print(f"Results:")
    print(f"  Trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print()
    
    return {
        'strategy': 'Time Horizon <3d',
        'trades': total,
        'wins': wins,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'skipped': skipped_ambiguous
    }

# ============================================================
# STRATEGY 3: NO-SIDE BIAS
# ============================================================
def backtest_no_side(markets):
    """Fade unlikely events"""
    print(f"{'='*70}")
    print(f"STRATEGY 3: NO-SIDE BIAS")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 10:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome
        if final_price > 0.90:
            outcome = 'Yes'
        elif final_price < 0.10:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # Entry at midpoint
        mid_idx = len(prices) // 2
        entry_price = prices[mid_idx].get('p', 0)
        
        # Filter: only bet NO when YES < 30%
        if entry_price >= 0.30:
            continue
        
        # We're betting NO (against YES)
        if outcome == 'No':
            pnl = (1 - entry_price) - (1 - final_price)
        else:
            pnl = -abs((1 - entry_price) - (1 - final_price))
        
        win = outcome == 'No'
        
        trades.append({
            'market': market['question'][:60],
            'entry_yes_price': entry_price,
            'outcome': outcome,
            'pnl': pnl,
            'win': win
        })
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    print(f"Results:")
    print(f"  Trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print()
    
    return {
        'strategy': 'NO-Side Bias',
        'trades': total,
        'wins': wins,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'skipped': skipped_ambiguous
    }

# ============================================================
# RUN ALL STRATEGIES
# ============================================================
results = []

results.append(backtest_trend_filter(dataset))
results.append(backtest_time_horizon(dataset))
results.append(backtest_no_side(dataset))

# ============================================================
# SUMMARY
# ============================================================
print(f"{'='*70}")
print(f"SUMMARY - PRICE-PROXY BACKTESTS")
print(f"{'='*70}\n")

for r in results:
    print(f"{r['strategy']:20s} | {r['trades']:>5,} trades | "
          f"{r['win_rate']:>5.1f}% win | {r['avg_pnl']:>+6.3f} avg")

print(f"\n{'='*70}\n")

# Save
output_file = OUTPUT_DIR / f"price_proxy_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'method': 'price_proxy',
        'dataset_size': len(dataset),
        'strategies': results
    }, f, indent=2)

print(f"Results saved: {output_file}")
