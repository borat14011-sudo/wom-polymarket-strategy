"""
STRATEGY 7: WHALE TRACKING
Detect large volume moves (simulated via big price jumps) and follow them
"""
import json
import numpy as np

print("[*] WHALE TRACKING BACKTEST STARTING...")

data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def infer_outcome(final_price):
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'Whale Tracking',
        'description': 'Follow large price moves (proxy for whale activity)',
        'trades': [],
        'total_markets': 0,
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'returns': []
    }
    
    # Large move threshold (simulating whale detection)
    whale_move_threshold = 0.08  # 8% move in one period
    
    for market in data:
        ph = market.get('price_history', [])
        if len(ph) < 15:
            continue
        
        results['total_markets'] += 1
        
        prices = [p['p'] for p in ph]
        final_price = prices[-1]
        
        if 0.1 <= final_price <= 0.9:
            continue
        
        outcome = infer_outcome(final_price)
        
        # Look for whale moves
        for i in range(5, len(prices) - 5):
            prev_price = prices[i-1]
            curr_price = prices[i]
            
            if prev_price < 0.05 or prev_price > 0.95:
                continue
            
            price_change = (curr_price - prev_price) / prev_price
            
            # Detect large upward move (whale buying YES)
            if price_change > whale_move_threshold:
                entry_price = curr_price
                
                if entry_price > 0.9 or entry_price < 0.1:
                    continue
                
                # Follow whale: buy YES
                payout = 1 if outcome == 'YES' else 0
                trade_return = (payout - entry_price) / entry_price if entry_price > 0 else 0
                is_win = (outcome == 'YES')
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'whale_move': f'+{price_change*100:.1f}%',
                    'entry_price': entry_price,
                    'bet_side': 'YES (follow whale)',
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
            
            # Detect large downward move (whale selling YES / buying NO)
            elif price_change < -whale_move_threshold:
                entry_price = curr_price
                
                if entry_price > 0.9 or entry_price < 0.1:
                    continue
                
                # Follow whale: buy NO
                no_cost = 1 - entry_price
                payout = 1 if outcome == 'NO' else 0
                trade_return = (payout - no_cost) / no_cost if no_cost > 0 else 0
                is_win = (outcome == 'NO')
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'whale_move': f'{price_change*100:.1f}%',
                    'entry_price': entry_price,
                    'bet_side': 'NO (follow whale)',
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

with open('backtest-results/whale_tracking_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] WHALE TRACKING COMPLETE")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
