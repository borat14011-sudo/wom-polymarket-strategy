import json
import statistics
from datetime import datetime

# Analyze the pairs trading results for patterns
print("=== SYSTEMATIC PATTERN ANALYSIS ===\n")

# Load pairs trading data
with open('backtest-results/pairs_trading_results.json', 'r') as f:
    pairs_data = json.load(f)

trades = pairs_data['trades']

# Categorize trades by type
categories = {
    'sports': [],
    'crypto': [],
    'politics': [],
    'weather': [],
    'other': []
}

for trade in trades:
    question = trade['question'].lower()
    if 'tennis' in question or 'basketball' in question or 'sports' in question or 'match' in question:
        categories['sports'].append(trade)
    elif 'bitcoin' in question or 'ethereum' in question or 'crypto' in question:
        categories['crypto'].append(trade)
    elif 'trump' in question or 'biden' in question or 'election' in question:
        categories['politics'].append(trade)
    elif 'temperature' in question or 'weather' in question:
        categories['weather'].append(trade)
    else:
        categories['other'].append(trade)

print("=== CATEGORY PERFORMANCE ===")
for category, trades_list in categories.items():
    if trades_list:
        wins = sum(1 for t in trades_list if t['win'])
        total = len(trades_list)
        returns = [t['return'] for t in trades_list]
        avg_return = statistics.mean(returns) if returns else 0
        
        print(f"{category.upper()}: {wins}/{total} wins ({wins/total:.1%}), avg return: {avg_return:.2%}")

# Analyze favorite-longshot bias
print("\n=== FAVORITE-LONGSHOT BIAS ANALYSIS ===")
# Group by probability ranges
prob_ranges = {
    '0-10%': [],
    '10-30%': [],
    '30-50%': [],
    '50-70%': [],
    '70-90%': [],
    '90-100%': []
}

for trade in trades:
    total_prob = trade['total_prob']
    if total_prob <= 10:
        prob_ranges['0-10%'].append(trade)
    elif total_prob <= 30:
        prob_ranges['10-30%'].append(trade)
    elif total_prob <= 50:
        prob_ranges['30-50%'].append(trade)
    elif total_prob <= 70:
        prob_ranges['50-70%'].append(trade)
    elif total_prob <= 90:
        prob_ranges['70-90%'].append(trade)
    else:
        prob_ranges['90-100%'].append(trade)

print("Probability Range Analysis:")
for range_name, trades_list in prob_ranges.items():
    if trades_list:
        wins = sum(1 for t in trades_list if t['win'])
        total = len(trades_list)
        win_rate = wins / total if total > 0 else 0
        
        # Calculate expected vs actual
        if '-' in range_name:
            low, high = map(float, range_name.replace('%', '').split('-'))
            expected_prob = (low + high) / 200  # Convert to probability
        else:
            expected_prob = 0.95  # For 90-100% range
        
        print(f"{range_name}: {wins}/{total} ({win_rate:.1%}) vs expected {expected_prob:.1%}")

# Analyze time-based patterns from market regime report
print("\n=== MARKET REGIME ANALYSIS ===")
with open('polymarket-backtest/MARKET_REGIME_REPORT.json', 'r') as f:
    regime_data = json.load(f)

strategies = regime_data['strategies']

print("Best performing strategies:")
for strategy in strategies:
    if strategy['recommendation'].startswith('🚀'):
        print(f"{strategy['name']}: {strategy['overallMetrics']['winRate']:.1%} win rate, {strategy['overallMetrics']['avgReturn']:.2%} avg return")

print("\nWorst performing strategies:")
for strategy in strategies:
    if strategy['recommendation'].startswith('❌'):
        print(f"{strategy['name']}: {strategy['overallMetrics']['winRate']:.1%} win rate, {strategy['overallMetrics']['avgReturn']:.2%} avg return")

# Analyze specific edge opportunities
print("\n=== SPECIFIC EDGE OPPORTUNITIES ===")

# 1. News reversion strategy performs well in high volatility
news_reversion = next(s for s in strategies if s['name'] == 'News Reversion')
high_vol_perf = news_reversion['regimePerformance']['High Volatility (VIX >30 or large price swings)']
print(f"1. News Reversion in High Volatility: {high_vol_perf['winRate']:.1%} win rate, {high_vol_perf['avgReturn']:.2%} avg return")

# 2. NO-Side bias in low volume markets
no_side_bias = next(s for s in strategies if s['name'] == 'NO-Side Bias')
low_vol_perf = no_side_bias['regimePerformance']['Low Volume (<$100K daily)']
print(f"2. NO-Side Bias in Low Volume: {low_vol_perf['winRate']:.1%} win rate, {low_vol_perf['avgReturn']:.2%} avg return")

# 3. Time horizon <3d in crypto bull markets
time_horizon = next(s for s in strategies if s['name'] == 'Time Horizon <3d')
crypto_bull_perf = time_horizon['regimePerformance']['Bull Crypto (BTC >20% YTD)']
print(f"3. Time Horizon <3d in Crypto Bull: {crypto_bull_perf['winRate']:.1%} win rate, {crypto_bull_perf['avgReturn']:.2%} avg return")

# Calculate expected value after 4% transaction costs
print("\n=== EXPECTED VALUE AFTER 4% TRANSACTION COSTS ===")
transaction_cost = 0.04

for strategy in strategies:
    win_rate = strategy['overallMetrics']['winRate']
    avg_win_return = 1.0  # Assuming 1:1 payout for simplicity
    avg_loss_return = -1.0
    
    # Adjust for transaction costs
    effective_win_return = avg_win_return * (1 - transaction_cost)
    effective_loss_return = avg_loss_return * (1 + transaction_cost)
    
    expected_value = (win_rate * effective_win_return) + ((1 - win_rate) * effective_loss_return)
    
    print(f"{strategy['name']}: EV = {expected_value:.3f} (raw: {strategy['overallMetrics']['avgReturn']:.3f})")