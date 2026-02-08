"""
STEP 3 & 4: STRATEGY HYPOTHESES GENERATION AND BACKTESTING
Generate strategies based on discovered patterns and backtest them
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

print("="*80)
print("STEP 3: STRATEGY HYPOTHESIS GENERATION")
print("="*80)

# Load data
resolved_df = pd.read_csv('resolved_markets_enriched.csv')
backtest_df = pd.read_csv('backtest_results.csv')

# Parse backtest dates
backtest_df['entry_date'] = pd.to_datetime(backtest_df['entry_date'])
backtest_df['exit_date'] = pd.to_datetime(backtest_df['exit_date'])

strategies = []

# HYPOTHESIS 1: Fade the Base Rate (NO Bias)
# Observation: 64.4% of markets resolve NO
# Strategy: Buy NO on random markets (or better, markets with slight YES premium)
strategies.append({
    'id': 1,
    'name': 'Base Rate Fade - Always NO',
    'description': 'Buy NO on all markets, since 64.4% resolve NO overall',
    'rationale': 'Markets heavily skew toward NO resolution. Simple base rate play.',
    'expected_win_rate': 0.644,
    'logic': lambda row: 'NO',
    'min_sample': 100
})

# HYPOTHESIS 2: Volume-Based Filter
# Observation: Low volume markets (<$10K) have 11-28% YES rate (72-89% NO)
# Strategy: Buy NO on low volume markets
strategies.append({
    'id': 2,
    'name': 'Low Volume NO Fade',
    'description': 'Buy NO on markets with volume <$10K (have 72-89% NO rate)',
    'rationale': 'Low volume markets resolve NO much more often than average',
    'expected_win_rate': 0.80,
    'logic': lambda row: 'NO' if row.get('volume_num', 0) < 10000 else None,
    'min_sample': 45
})

# HYPOTHESIS 3: High Volume YES Play
# Observation: Mid-volume markets ($10K-$1M) have 42-44% YES rate
# Strategy: Buy YES on mid-volume markets
strategies.append({
    'id': 3,
    'name': 'Mid-Volume YES Play',
    'description': 'Buy YES on markets with $10K-$1M volume',
    'rationale': 'Mid-volume markets resolve YES more often than base rate',
    'expected_win_rate': 0.43,
    'logic': lambda row: 'YES' if 10000 <= row.get('volume_num', 0) <= 1000000 else None,
    'min_sample': 91
})

# HYPOTHESIS 4: Political Markets - Fade the Hype
# Observation: Trump markets have 53% YES rate, but most are low volume
# Strategy: Buy NO on Trump-related markets (sample may be biased)
strategies.append({
    'id': 4,
    'name': 'Trump Fade - Buy NO',
    'description': 'Buy NO on Trump-related markets',
    'rationale': 'Trump markets have slightly above 50% YES, but may be overhyped',
    'expected_win_rate': 0.47,
    'logic': lambda row: 'NO' if 'trump' in str(row.get('question', '')).lower() else None,
    'min_sample': 32
})

# HYPOTHESIS 5: Election Markets - Base Rate Play
# Observation: 71% of markets are election-related, 35.8% YES rate
# Strategy: Buy NO on election markets
strategies.append({
    'id': 5,
    'name': 'Election Markets NO',
    'description': 'Buy NO on election-related markets',
    'rationale': 'Election markets match overall base rate (64% NO)',
    'expected_win_rate': 0.64,
    'logic': lambda row: 'NO' if any(term in str(row.get('question', '')).lower() 
                                     for term in ['election', 'senate', 'president', 'governor', 'primary', 'ballot', 'vote']) else None,
    'min_sample': 106
})

# HYPOTHESIS 6: Price-Based Strategy (from backtest insights)
# Observation: Backtest shows 40-60% entry bucket has 57% win rate
# Strategy: Buy when entry price is in 40-60% range (close to fair)
strategies.append({
    'id': 6,
    'name': 'Fair Price Entry (40-60%)',
    'description': 'Enter when price is in 40-60% range (avoid extremes)',
    'rationale': 'Backtest shows 57% win rate in middle price range',
    'expected_win_rate': 0.57,
    'logic': lambda row: 'YES' if 0.4 <= row.get('entry_price', 0) <= 0.6 else None,
    'min_sample': 337,
    'uses_backtest': True
})

# HYPOTHESIS 7: Avoid Longshots
# Observation: Backtest shows 0-20% entry bucket has only 26% win rate
# Strategy: Avoid buying YES when price < 20% (don't chase longshots)
strategies.append({
    'id': 7,
    'name': 'Avoid Longshots (<20%)',
    'description': 'Do not buy YES when probability < 20%',
    'rationale': 'Longshots in backtest only win 26% of the time',
    'expected_win_rate': 0.50,  # By avoiding bad trades
    'logic': lambda row: 'NO' if row.get('entry_price', 0) < 0.2 else None,
    'min_sample': 654,
    'uses_backtest': True
})

# HYPOTHESIS 8: Momentum - Buy Rising Prices
# Observation: Backtest entry prices correlate with exits
# Strategy: Buy YES when entry price > 50% (follow the crowd on favorites)
strategies.append({
    'id': 8,
    'name': 'Follow Momentum (>50%)',
    'description': 'Buy YES when price > 50% (momentum play)',
    'rationale': 'Favorites in backtest have 57-69% win rates',
    'expected_win_rate': 0.60,
    'logic': lambda row: 'YES' if row.get('entry_price', 0) > 0.5 else None,
    'min_sample': 750,
    'uses_backtest': True
})

# HYPOTHESIS 9: Contrarian - Fade Favorites
# Observation: High prices might be overvalued
# Strategy: Buy NO when price > 70%
strategies.append({
    'id': 9,
    'name': 'Fade Favorites (>70%)',
    'description': 'Buy NO when YES price > 70% (contrarian)',
    'rationale': 'High prices may reflect overconfidence; backtest shows 43% win rate in 80-100% bucket',
    'expected_win_rate': 0.57,  # Buying NO when YES > 70%
    'logic': lambda row: 'NO' if row.get('entry_price', 0) > 0.7 else None,
    'min_sample': 750,
    'uses_backtest': True
})

# HYPOTHESIS 10: Combined Filter
# Low volume + election = High NO probability
strategies.append({
    'id': 10,
    'name': 'Combined: Low Volume + Election',
    'description': 'Buy NO on low volume (<$10K) election markets',
    'rationale': 'Combines two strong NO signals',
    'expected_win_rate': 0.75,
    'logic': lambda row: 'NO' if (row.get('volume_num', 0) < 10000 and 
                                   any(term in str(row.get('question', '')).lower() 
                                       for term in ['election', 'senate', 'president', 'vote'])) else None,
    'min_sample': 30
})

print("\nGenerated 10 Strategy Hypotheses:")
print("-" * 80)
for s in strategies:
    print(f"\n{s['id']}. {s['name']}")
    print(f"   Desc: {s['description']}")
    print(f"   Rationale: {s['rationale']}")
    print(f"   Expected Win Rate: {s['expected_win_rate']*100:.1f}%")
    print(f"   Min Sample: {s['min_sample']}")

print("\n" + "="*80)
print("STEP 4: BACKTESTING STRATEGIES")
print("="*80)

# Backtest each strategy
results = []

print("\nBacktesting on resolved markets (n=149) and backtest data (n=2014)...")

for strategy in strategies:
    print(f"\n{'='*60}")
    print(f"Strategy {strategy['id']}: {strategy['name']}")
    print(f"{'='*60}")
    
    # Determine which dataset to use
    if strategy.get('uses_backtest'):
        # Use backtest data
        test_data = backtest_df.copy()
        
        # Apply strategy logic
        test_data['signal'] = test_data.apply(strategy['logic'], axis=1)
        trades = test_data.dropna(subset=['signal'])
        
        if len(trades) == 0:
            print(f"  No trades generated")
            continue
            
        # Calculate P&L
        trades['won'] = trades['pnl'] > 0
        win_rate = trades['won'].mean()
        total_pnl = trades['pnl'].sum()
        avg_pnl = trades['pnl'].mean()
        
        # Apply 5% fees
        trades['pnl_after_fees'] = trades['pnl'] * 0.95
        total_pnl_after_fees = trades['pnl_after_fees'].sum()
        
        # Calculate drawdown
        trades['cumulative'] = trades['pnl'].cumsum()
        trades['running_max'] = trades['cumulative'].cummax()
        trades['drawdown'] = trades['cumulative'] - trades['running_max']
        max_drawdown = trades['drawdown'].min()
        
        # Sharpe-like metric (simplified)
        returns = trades['pnl']
        sharpe = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        print(f"  Trades: {len(trades)}")
        print(f"  Win Rate: {win_rate*100:.1f}%")
        print(f"  Total P&L (before fees): ${total_pnl:.2f}")
        print(f"  Total P&L (after 5% fees): ${total_pnl_after_fees:.2f}")
        print(f"  Avg P&L per trade: ${avg_pnl:.3f}")
        print(f"  Max Drawdown: ${max_drawdown:.2f}")
        print(f"  Sharpe-like ratio: {sharpe:.3f}")
        
        results.append({
            'id': strategy['id'],
            'name': strategy['name'],
            'trades': len(trades),
            'win_rate': win_rate,
            'pnl_before_fees': total_pnl,
            'pnl_after_fees': total_pnl_after_fees,
            'avg_pnl': avg_pnl,
            'max_drawdown': max_drawdown,
            'sharpe': sharpe,
            'data_source': 'backtest_csv'
        })
        
    else:
        # Use resolved markets data
        test_data = resolved_df.copy()
        
        # Apply strategy logic to get signal
        test_data['signal'] = test_data.apply(strategy['logic'], axis=1)
        trades = test_data.dropna(subset=['signal'])
        
        if len(trades) == 0:
            print(f"  No trades generated")
            continue
        
        # Simulate trades on resolved markets
        # Assume we buy at implied probability and hold to resolution
        trades['entry_price'] = trades['final_yes_price']
        trades['exit_price'] = trades['winner'].apply(lambda x: 1.0 if x == 'Yes' else 0.0)
        
        # Calculate P&L
        trades['pnl'] = trades.apply(lambda row: 
            row['exit_price'] - row['entry_price'] if row['signal'] == 'YES'
            else row['entry_price'] - row['exit_price'], axis=1)
        
        trades['won'] = trades['pnl'] > 0
        win_rate = trades['won'].mean()
        total_pnl = trades['pnl'].sum()
        avg_pnl = trades['pnl'].mean()
        
        # Apply 5% fees
        trades['pnl_after_fees'] = trades['pnl'] * 0.95
        total_pnl_after_fees = trades['pnl_after_fees'].sum()
        
        # Drawdown
        trades['cumulative'] = trades['pnl'].cumsum()
        trades['running_max'] = trades['cumulative'].cummax()
        trades['drawdown'] = trades['cumulative'] - trades['running_max']
        max_drawdown = trades['drawdown'].min()
        
        # Sharpe
        returns = trades['pnl']
        sharpe = returns.mean() / returns.std() if returns.std() > 0 else 0
        
        print(f"  Trades: {len(trades)}")
        print(f"  Win Rate: {win_rate*100:.1f}%")
        print(f"  Total P&L (before fees): ${total_pnl:.2f}")
        print(f"  Total P&L (after 5% fees): ${total_pnl_after_fees:.2f}")
        print(f"  Avg P&L per trade: ${avg_pnl:.3f}")
        print(f"  Max Drawdown: ${max_drawdown:.2f}")
        print(f"  Sharpe-like ratio: {sharpe:.3f}")
        
        results.append({
            'id': strategy['id'],
            'name': strategy['name'],
            'trades': len(trades),
            'win_rate': win_rate,
            'pnl_before_fees': total_pnl,
            'pnl_after_fees': total_pnl_after_fees,
            'avg_pnl': avg_pnl,
            'max_drawdown': max_drawdown,
            'sharpe': sharpe,
            'data_source': 'resolved_markets'
        })

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv('strategy_backtest_results.csv', index=False)

print("\n" + "="*80)
print("BACKTEST RESULTS SUMMARY")
print("="*80)
print(results_df.to_string(index=False))

print("\n[OK] Saved backtest results to strategy_backtest_results.csv")
