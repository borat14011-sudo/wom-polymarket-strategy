"""
STRATEGY 6: EXPERT FADE
Fade consensus - when price is stuck at a round number for too long, bet against
"""
import json
import numpy as np

print("[*] EXPERT FADE BACKTEST STARTING...")

data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def infer_outcome(final_price):
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'Expert Fade',
        'description': 'Fade sticky consensus prices (round numbers that persist too long)',
        'trades': [],
        'total_markets': 0,
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'returns': []
    }
    
    # Round numbers that represent "consensus"
    consensus_prices = [0.50, 0.60, 0.70, 0.75, 0.80, 0.90]
    tolerance = 0.03  # Within 3% of round number
    sticky_threshold = 5  # Stuck for 5+ periods
    
    for market in data:
        ph = market.get('price_history', [])
        if len(ph) < 20:
            continue
        
        results['total_markets'] += 1
        
        prices = [p['p'] for p in ph]
        final_price = prices[-1]
        
        if 0.1 <= final_price <= 0.9:
            continue
        
        outcome = infer_outcome(final_price)
        
        # Look for sticky consensus prices
        for i in range(10, len(prices) - 5):
            curr_price = prices[i]
            
            # Check if near a consensus price
            near_consensus = None
            for cp in consensus_prices:
                if abs(curr_price - cp) < tolerance:
                    near_consensus = cp
                    break
            
            if near_consensus is None:
                continue
            
            # Check if price has been stuck
            lookback = prices[i-sticky_threshold:i]
            if all(abs(p - near_consensus) < tolerance for p in lookback):
                entry_price = curr_price
                
                # Fade: if consensus is YES-favored (>0.5), bet NO
                if near_consensus > 0.5:
                    no_cost = 1 - entry_price
                    payout = 1 if outcome == 'NO' else 0
                    trade_return = (payout - no_cost) / no_cost if no_cost > 0 else 0
                    is_win = (outcome == 'NO')
                    bet_side = 'NO'
                else:
                    # If consensus is NO-favored, bet YES
                    payout = 1 if outcome == 'YES' else 0
                    trade_return = (payout - entry_price) / entry_price if entry_price > 0 else 0
                    is_win = (outcome == 'YES')
                    bet_side = 'YES'
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'consensus_price': near_consensus,
                    'entry_price': entry_price,
                    'bet_side': bet_side,
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

with open('backtest-results/expert_fade_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] EXPERT FADE COMPLETE")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
