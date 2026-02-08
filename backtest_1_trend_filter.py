"""
STRATEGY 1: TREND FILTER
Only buy when price is trending UP (using simple moving average crossover)
"""
import json
import numpy as np
from datetime import datetime

print("[*] TREND FILTER BACKTEST STARTING...")

# Load data
data = json.load(open(r'C:\Users\Borat\.openclaw\workspace\polymarket-monitor\historical-data-scraper\data\backtest_dataset_v1.json'))

def calculate_sma(prices, window):
    """Simple Moving Average"""
    if len(prices) < window:
        return None
    return sum(prices[-window:]) / window

def infer_outcome(final_price):
    """Infer outcome from final price: YES if >0.5, NO if <0.5"""
    return 'YES' if final_price > 0.5 else 'NO'

def run_backtest():
    results = {
        'strategy': 'Trend Filter',
        'description': 'Buy when short-term MA crosses above long-term MA (uptrend signal)',
        'trades': [],
        'total_markets': 0,
        'trades_executed': 0,
        'wins': 0,
        'losses': 0,
        'total_return': 0,
        'returns': []
    }
    
    short_window = 5  # 5-period short MA
    long_window = 15  # 15-period long MA
    
    for market in data:
        ph = market.get('price_history', [])
        if len(ph) < long_window + 5:  # Need enough data
            continue
            
        results['total_markets'] += 1
        prices = [p['p'] for p in ph]
        final_price = prices[-1]
        
        # Need clear outcome for backtesting
        if 0.1 <= final_price <= 0.9:
            continue
        
        outcome = infer_outcome(final_price)
        
        # Check for entry signals throughout the price history
        for i in range(long_window, len(prices) - 5):  # Leave room for exit
            short_ma = calculate_sma(prices[:i], short_window)
            long_ma = calculate_sma(prices[:i], long_window)
            prev_short_ma = calculate_sma(prices[:i-1], short_window)
            prev_long_ma = calculate_sma(prices[:i-1], long_window)
            
            if short_ma is None or long_ma is None:
                continue
            if prev_short_ma is None or prev_long_ma is None:
                continue
            
            # Bullish crossover: short MA crosses above long MA
            if prev_short_ma <= prev_long_ma and short_ma > long_ma:
                entry_price = prices[i]
                
                # Skip if price already too high or too low
                if entry_price > 0.85 or entry_price < 0.15:
                    continue
                
                # We buy YES side
                exit_price = final_price if outcome == 'YES' else 0
                trade_return = (exit_price - entry_price) / entry_price if entry_price > 0 else 0
                
                is_win = (outcome == 'YES')
                
                results['trades'].append({
                    'market_id': market.get('market_id'),
                    'question': market.get('question', '')[:50],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
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
                
                break  # One trade per market
    
    # Calculate metrics
    if results['trades_executed'] > 0:
        results['win_rate'] = results['wins'] / results['trades_executed']
        results['avg_return'] = np.mean(results['returns'])
        results['total_return'] = sum(results['returns'])
        
        # Sharpe ratio (simplified, assuming risk-free rate = 0)
        if len(results['returns']) > 1 and np.std(results['returns']) > 0:
            results['sharpe_ratio'] = np.mean(results['returns']) / np.std(results['returns'])
        else:
            results['sharpe_ratio'] = 0
        
        # Max drawdown
        cumulative = np.cumsum(results['returns'])
        running_max = np.maximum.accumulate(cumulative)
        drawdowns = cumulative - running_max
        results['max_drawdown'] = float(np.min(drawdowns)) if len(drawdowns) > 0 else 0
    else:
        results['win_rate'] = 0
        results['avg_return'] = 0
        results['sharpe_ratio'] = 0
        results['max_drawdown'] = 0
    
    # Clean up for JSON
    results['returns'] = [float(r) for r in results['returns'][:100]]  # Keep first 100 for reference
    results['trades'] = results['trades'][:50]  # Keep first 50 trades for reference
    
    return results

results = run_backtest()

# Save results
with open('backtest-results/trend_filter_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"[OK] TREND FILTER COMPLETE")
print(f"   Trades: {results['trades_executed']}")
print(f"   Win Rate: {results['win_rate']*100:.1f}%")
print(f"   Avg Return: {results['avg_return']*100:.1f}%")
print(f"   Sharpe: {results['sharpe_ratio']:.2f}")
print(f"   Max DD: {results['max_drawdown']*100:.1f}%")
