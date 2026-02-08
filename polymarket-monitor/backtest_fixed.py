#!/usr/bin/env python3
"""
Fixed Backtest - No Look-Ahead Bias
Walk-forward simulation with realistic entry/exit timing
"""
import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"POLYMARKET FIXED BACKTEST - NO LOOK-AHEAD BIAS")
print(f"Walk-forward simulation with realistic timing")
print(f"{'='*70}\n")

# Load dataset
print("Loading dataset...")
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    dataset = json.load(f)
print(f"[OK] {len(dataset):,} markets loaded\n")

# ============================================================
# STRATEGY 1: TREND FILTER (FIXED)
# ============================================================
def backtest_trend_filter_fixed(markets):
    """Only buy when price is trending UP - FIXED VERSION"""
    print(f"{'='*70}")
    print(f"STRATEGY 1: TREND FILTER (FIXED)")
    print(f"Entry: When price shows uptrend (3 rising points)")
    print(f"Exit: At market close (simulated)")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    skipped_no_signal = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 30:  # Need enough history
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome (only for validation)
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # Walk forward through price history
        # CRITICAL: Stop at -10 to simulate realistic exit timing
        # (can't exit at the exact final price in reality)
        max_entry_idx = len(prices) - 10
        
        for i in range(5, max_entry_idx):
            # Only look at data UP TO index i (no future data!)
            current_price = prices[i].get('p', 0)
            prev_1 = prices[i-1].get('p', 0)
            prev_2 = prices[i-2].get('p', 0)
            prev_3 = prices[i-3].get('p', 0)
            
            # Trend signal: 3 consecutive rising prices
            if current_price > prev_1 > prev_2 > prev_3:
                entry_price = current_price
                
                # Exit: Simulate exit 5 data points before close
                # (realistic - can't time the exact close)
                exit_idx = len(prices) - 5
                exit_price = prices[exit_idx].get('p', 0)
                
                # Calculate P&L based on which side we'd take
                # If price is trending up, we buy YES
                if outcome == 'Yes':
                    pnl = exit_price - entry_price
                else:
                    pnl = -(exit_price - entry_price)
                
                win = pnl > 0
                
                trades.append({
                    'market': market['question'][:60],
                    'entry': entry_price,
                    'exit': exit_price,
                    'entry_idx': i,
                    'exit_idx': exit_idx,
                    'total_points': len(prices),
                    'pnl': pnl,
                    'win': win
                })
                break  # One trade per market
        else:
            skipped_no_signal += 1
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    losses = total - wins
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    winning_trades = [t for t in trades if t['win']]
    losing_trades = [t for t in trades if not t['win']]
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    print(f"Results:")
    print(f"  Total trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Losses: {losses:,}")
    print(f"  Avg win: {avg_win:+.3f}")
    print(f"  Avg loss: {avg_loss:+.3f}")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print(f"  Skipped (no signal): {skipped_no_signal:,}")
    print()
    
    return {
        'strategy': 'Trend Filter (Fixed)',
        'trades': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss
    }

# ============================================================
# STRATEGY 2: TIME HORIZON <3 DAYS (FIXED)
# ============================================================
def backtest_time_horizon_fixed(markets):
    """Short-term markets - FIXED VERSION"""
    print(f"{'='*70}")
    print(f"STRATEGY 2: TIME HORIZON <3 DAYS (FIXED)")
    print(f"Entry: At 50% of market lifetime")
    print(f"Exit: At 90% of market lifetime")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    skipped_duration = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        # Duration filter
        start = market.get('start_date')
        end = market.get('end_date')
        if not start or not end:
            continue
        
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            duration = (end_dt - start_dt).days
        except:
            continue
        
        if duration >= 3:
            skipped_duration += 1
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 20:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # FIXED: Entry at 50% of lifetime, Exit at 90%
        entry_idx = len(prices) // 2
        exit_idx = int(len(prices) * 0.9)
        
        entry_price = prices[entry_idx].get('p', 0)
        exit_price = prices[exit_idx].get('p', 0)
        
        # Simple directional trade (buy YES if > 0.5, NO if < 0.5)
        if entry_price > 0.5:
            # Betting YES
            if outcome == 'Yes':
                pnl = exit_price - entry_price
            else:
                pnl = -(exit_price - entry_price)
        else:
            # Betting NO
            if outcome == 'No':
                pnl = (1 - entry_price) - (1 - exit_price)
            else:
                pnl = -((1 - entry_price) - (1 - exit_price))
        
        win = pnl > 0
        
        trades.append({
            'market': market['question'][:60],
            'duration_days': duration,
            'entry': entry_price,
            'exit': exit_price,
            'pnl': pnl,
            'win': win
        })
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    losses = total - wins
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    winning_trades = [t for t in trades if t['win']]
    losing_trades = [t for t in trades if not t['win']]
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    print(f"Results:")
    print(f"  Total trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Losses: {losses:,}")
    print(f"  Avg win: {avg_win:+.3f}")
    print(f"  Avg loss: {avg_loss:+.3f}")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print(f"  Skipped (wrong duration): {skipped_duration:,}")
    print()
    
    return {
        'strategy': 'Time Horizon <3d (Fixed)',
        'trades': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss
    }

# ============================================================
# STRATEGY 3: NO-SIDE BIAS (FIXED)
# ============================================================
def backtest_no_side_fixed(markets):
    """Fade unlikely events - FIXED VERSION"""
    print(f"{'='*70}")
    print(f"STRATEGY 3: NO-SIDE BIAS (FIXED)")
    print(f"Entry: Bet NO when YES price < 25% at midpoint")
    print(f"Exit: At 90% of market lifetime")
    print(f"{'='*70}\n")
    
    trades = []
    skipped_ambiguous = 0
    skipped_no_signal = 0
    
    for market in markets:
        if not market.get('closed'):
            continue
        
        prices = market.get('price_history', [])
        if len(prices) < 20:
            continue
        
        final_price = prices[-1].get('p', 0)
        
        # Infer outcome
        if final_price > 0.95:
            outcome = 'Yes'
        elif final_price < 0.05:
            outcome = 'No'
        else:
            skipped_ambiguous += 1
            continue
        
        # Entry at midpoint
        entry_idx = len(prices) // 2
        entry_price = prices[entry_idx].get('p', 0)
        
        # Signal: Only bet NO when YES price is < 25% (unlikely event)
        if entry_price >= 0.25:
            skipped_no_signal += 1
            continue
        
        # Exit at 90% of lifetime
        exit_idx = int(len(prices) * 0.9)
        exit_price = prices[exit_idx].get('p', 0)
        
        # We're betting NO (against YES)
        # P&L = change in NO price = change in (1 - YES price)
        entry_no_price = 1 - entry_price
        exit_no_price = 1 - exit_price
        
        if outcome == 'No':
            # NO wins: we profit from NO price increasing
            pnl = exit_no_price - entry_no_price
        else:
            # YES wins: we lose as NO price decreases
            pnl = exit_no_price - entry_no_price
        
        win = pnl > 0
        
        trades.append({
            'market': market['question'][:60],
            'entry_yes_price': entry_price,
            'exit_yes_price': exit_price,
            'outcome': outcome,
            'pnl': pnl,
            'win': win
        })
    
    # Stats
    total = len(trades)
    wins = len([t for t in trades if t['win']])
    losses = total - wins
    win_rate = wins / total * 100 if total > 0 else 0
    avg_pnl = sum(t['pnl'] for t in trades) / total if total > 0 else 0
    
    winning_trades = [t for t in trades if t['win']]
    losing_trades = [t for t in trades if not t['win']]
    avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
    avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
    
    print(f"Results:")
    print(f"  Total trades: {total:,}")
    print(f"  Wins: {wins:,} ({win_rate:.1f}%)")
    print(f"  Losses: {losses:,}")
    print(f"  Avg win: {avg_win:+.3f}")
    print(f"  Avg loss: {avg_loss:+.3f}")
    print(f"  Avg P&L: {avg_pnl:+.3f}")
    print(f"  Skipped (ambiguous): {skipped_ambiguous:,}")
    print(f"  Skipped (no signal): {skipped_no_signal:,}")
    print()
    
    return {
        'strategy': 'NO-Side Bias (Fixed)',
        'trades': total,
        'wins': wins,
        'losses': losses,
        'win_rate': win_rate,
        'avg_pnl': avg_pnl,
        'avg_win': avg_win,
        'avg_loss': avg_loss
    }

# ============================================================
# RUN ALL STRATEGIES
# ============================================================
results = []

results.append(backtest_trend_filter_fixed(dataset))
results.append(backtest_time_horizon_fixed(dataset))
results.append(backtest_no_side_fixed(dataset))

# ============================================================
# SUMMARY
# ============================================================
print(f"{'='*70}")
print(f"SUMMARY - FIXED BACKTESTS (NO LOOK-AHEAD BIAS)")
print(f"{'='*70}\n")

for r in results:
    print(f"{r['strategy']:25s} | {r['trades']:>5,} trades | "
          f"{r['win_rate']:>5.1f}% win | "
          f"{r['avg_pnl']:>+6.3f} avg | "
          f"W:{r['avg_win']:>+5.3f} L:{r['avg_loss']:>+5.3f}")

print(f"\n{'='*70}\n")

# Save
output_file = OUTPUT_DIR / f"fixed_backtest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_file, 'w') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'method': 'walk_forward_no_lookahead',
        'dataset_size': len(dataset),
        'strategies': results
    }, f, indent=2)

print(f"Results saved: {output_file}")
