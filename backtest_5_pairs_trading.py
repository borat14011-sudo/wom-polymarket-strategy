"""
STRATEGY 5: PAIRS TRADING
Find markets in same event and exploit price discrepancies
"""
import json
import numpy as np
from collections import defaultdict

print("[*] PAIRS TRADING BACKTEST STARTING...")

data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def infer_outcome(final_price):
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'Pairs Trading',
        'description': 'Exploit price discrepancies between related markets in same event',
        'trades': [],
        'total_markets': 0,
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'returns': []
    }
    
    # Group markets by event_id
    events = defaultdict(list)
    for market in data:
        event_id = market.get('event_id')
        if event_id:
            events[event_id].append(market)
    
    results['total_events'] = len(events)
    results['events_with_multiple_markets'] = sum(1 for e in events.values() if len(e) > 1)
    
    # For each event with multiple markets
    for event_id, markets in events.items():
        if len(markets) < 2:
            continue
        
        results['total_markets'] += len(markets)
        
        # Check if prices sum to roughly 1 (mutually exclusive outcomes)
        valid_markets = [m for m in markets if len(m.get('price_history', [])) >= 10]
        if len(valid_markets) < 2:
            continue
        
        # Get mid-point prices for all markets
        mid_prices = []
        for m in valid_markets:
            ph = m.get('price_history', [])
            mid_idx = len(ph) // 2
            mid_prices.append(ph[mid_idx]['p'])
        
        total_prob = sum(mid_prices)
        
        # Look for arbitrage: if total > 1.05, market is mispriced
        if total_prob > 1.05:
            # Sell the overpriced combination - but simplified: 
            # Just short the most overpriced one
            max_idx = np.argmax(mid_prices)
            market = valid_markets[max_idx]
            
            ph = market.get('price_history', [])
            mid_idx = len(ph) // 2
            entry_price = ph[mid_idx]['p']
            final_price = ph[-1]['p']
            
            if 0.1 <= final_price <= 0.9:
                continue
            
            outcome = infer_outcome(final_price)
            
            # Short YES (bet NO) on overpriced market
            no_cost = 1 - entry_price
            payout = 1 if outcome == 'NO' else 0
            trade_return = (payout - no_cost) / no_cost if no_cost > 0 else 0
            is_win = (outcome == 'NO')
            
            results['trades'].append({
                'event_id': event_id,
                'market_id': market.get('market_id'),
                'question': market.get('question', '')[:50],
                'total_prob': total_prob,
                'entry_price': entry_price,
                'bet_side': 'NO (fade overpriced)',
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
        
        # If total < 0.95, buy the underpriced combination
        elif total_prob < 0.95:
            # Buy the most underpriced one
            min_idx = np.argmin(mid_prices)
            market = valid_markets[min_idx]
            
            ph = market.get('price_history', [])
            mid_idx = len(ph) // 2
            entry_price = ph[mid_idx]['p']
            final_price = ph[-1]['p']
            
            if 0.1 <= final_price <= 0.9:
                continue
            
            outcome = infer_outcome(final_price)
            
            # Buy YES on underpriced market
            payout = 1 if outcome == 'YES' else 0
            trade_return = (payout - entry_price) / entry_price if entry_price > 0 else 0
            is_win = (outcome == 'YES')
            
            results['trades'].append({
                'event_id': event_id,
                'market_id': market.get('market_id'),
                'question': market.get('question', '')[:50],
                'total_prob': total_prob,
                'entry_price': entry_price,
                'bet_side': 'YES (buy underpriced)',
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

with open('backtest-results/pairs_trading_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] PAIRS TRADING COMPLETE")
print(f"   Events analyzed: {results.get('total_events', 0)}")
print(f"   Multi-market events: {results.get('events_with_multiple_markets', 0)}")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
