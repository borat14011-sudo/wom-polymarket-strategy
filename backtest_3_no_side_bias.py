"""
STRATEGY 3: NO-SIDE BIAS
Fade unlikely events - bet NO on markets with high YES prices that seem overvalued
"""
import json
import numpy as np

print("[*] NO-SIDE BIAS BACKTEST STARTING...")

data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def infer_outcome(final_price):
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'NO-Side Bias',
        'description': 'Bet NO on overpriced YES markets (contrarian fade strategy)',
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
        
        prices = [p['p'] for p in ph]
        final_price = prices[-1]
        
        if 0.1 <= final_price <= 0.9:
            continue
        
        outcome = infer_outcome(final_price)
        
        # Look for overpriced YES opportunities (price 0.6-0.85 range)
        # These are "likely" events priced in, but not certainties
        for i in range(5, len(prices) - 3):
            entry_price = prices[i]
            
            # Target: YES priced at 60-85% (seems likely but might be wrong)
            if 0.60 <= entry_price <= 0.85:
                # Bet NO - we pay (1 - entry_price) and win 1 if NO, else 0
                no_cost = 1 - entry_price  # Cost to buy NO
                payout = 1 if outcome == 'NO' else 0
                
                trade_return = (payout - no_cost) / no_cost if no_cost > 0 else 0
                is_win = (outcome == 'NO')
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'yes_price': entry_price,
                    'no_cost': no_cost,
                    'bet_side': 'NO',
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

with open('backtest-results/no_side_bias_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] NO-SIDE BIAS COMPLETE")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
