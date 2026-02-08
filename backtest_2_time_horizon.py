"""
STRATEGY 2: TIME HORIZON <3 DAYS
Only trade markets with less than 3 days to resolution
"""
import json
import numpy as np
from datetime import datetime, timedelta

print("[*] TIME HORIZON <3D BACKTEST STARTING...")

# Load data
data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def parse_date(date_str):
    """Parse ISO date string"""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        return None

def infer_outcome(final_price):
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'Time Horizon <3 Days',
        'description': 'Only trade markets within 3 days of resolution - momentum tends to be clearer',
        'trades': [],
        'total_markets': 0,
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'returns': []
    }
    
    for market in data:
        ph = market.get('price_history', [])
        if len(ph) < 10:
            continue
        
        results['total_markets'] += 1
        
        end_date = parse_date(market.get('end_date', ''))
        if not end_date:
            continue
        
        prices = [p['p'] for p in ph]
        timestamps = [p['t'] for p in ph]
        final_price = prices[-1]
        
        if 0.1 <= final_price <= 0.9:
            continue
        
        outcome = infer_outcome(final_price)
        
        # Find entry points within 3 days of end
        end_timestamp = end_date.timestamp()
        three_days_before = end_timestamp - (3 * 24 * 60 * 60)
        
        for i in range(len(ph) - 2):
            t = timestamps[i]
            if t >= three_days_before and t < end_timestamp - 3600:  # At least 1 hour before end
                entry_price = prices[i]
                
                # Skip extreme prices
                if entry_price > 0.9 or entry_price < 0.1:
                    continue
                
                # Bet on the more likely side based on current price
                if entry_price > 0.5:
                    # Bet YES
                    payout = 1 if outcome == 'YES' else 0
                    cost = entry_price
                else:
                    # Bet NO (which means we profit if NO wins)
                    payout = 1 if outcome == 'NO' else 0
                    cost = 1 - entry_price
                
                trade_return = (payout - cost) / cost if cost > 0 else 0
                is_win = payout > 0
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'entry_price': entry_price,
                    'bet_side': 'YES' if entry_price > 0.5 else 'NO',
                    'outcome': outcome,
                    'return': trade_return,
                    'win': is_win
                })
                results['trades_executed'] += 1
                results['returns'].append(trade_return)
                
                if is_win:
                    results['wins'] += 1
                else:
                    results['losses'] += 1
                
                break
    
    # Calculate metrics
    if results['trades_executed'] > 0:
        results['win_rate'] = results['wins'] / results['trades_executed']
        results['avg_return'] = float(np.mean(results['returns']))
        results['total_return'] = float(sum(results['returns']))
        
        if len(results['returns']) > 1 and np.std(results['returns']) > 0:
            results['sharpe_ratio'] = float(np.mean(results['returns']) / np.std(results['returns']))
        else:
            results['sharpe_ratio'] = 0.0
        
        cumulative = np.cumsum(results['returns'])
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - running_max
        results['max_drawdown'] = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0.0
    else:
        results['win_rate'] = 0
        results['avg_return'] = 0
        results['sharpe_ratio'] = 0
        results['max_drawdown'] = 0
    
    results['returns'] = [float(r) for r in results['returns'][:100]]
    results['trades'] = results['trades'][:50]
    
    return results

results = run_backtest()

with open('backtest-results/time_horizon_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] TIME HORIZON <3D COMPLETE")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
