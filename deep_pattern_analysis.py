import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('backtest_results.csv')
df['win'] = df['roi'] > 0
df['price_move'] = abs(df['exit_price'] - df['entry_price'])
df['distance_from_05'] = abs(df['entry_price'] - 0.5)

print('=== TRADEABLE VS UNTRADEABLE MARKETS ===\n')

# Define "good" markets: high win rate, decent sample size
market_stats = df.groupby('market_id').agg({
    'win': 'mean',
    'roi': ['mean', 'std', 'count'],
    'price_move': 'mean',
    'entry_price': 'mean'
}).reset_index()
market_stats.columns = ['market_id', 'win_rate', 'avg_roi', 'roi_std', 'trade_count', 'avg_move', 'avg_price']

# Markets with multiple trades (more data points)
multi_trade_markets = market_stats[market_stats['trade_count'] >= 2]
print(f'Markets with 2+ strategy attempts: {len(multi_trade_markets)}')
print(f'  Avg win rate: {multi_trade_markets["win_rate"].mean()*100:.1f}%')
print(f'  Win rate std: {multi_trade_markets["win_rate"].std()*100:.1f}pp')
print()

# Top predictable markets (high win rate, multiple trades)
predictable = multi_trade_markets.nlargest(20, 'win_rate')
print('TOP 20 MOST PREDICTABLE MARKETS:')
print(f'  Avg win rate: {predictable["win_rate"].mean()*100:.1f}%')
print(f'  Avg price at entry: {predictable["avg_price"].mean():.3f}')
print(f'  Avg price movement: {predictable["avg_move"].mean():.3f}')
print(f'  Avg distance from 0.5: {abs(predictable["avg_price"] - 0.5).mean():.3f}')
print()

# Bottom unpredictable markets
unpredictable = multi_trade_markets.nsmallest(20, 'win_rate')
print('BOTTOM 20 LEAST PREDICTABLE MARKETS:')
print(f'  Avg win rate: {unpredictable["win_rate"].mean()*100:.1f}%')
print(f'  Avg price at entry: {unpredictable["avg_price"].mean():.3f}')
print(f'  Avg price movement: {unpredictable["avg_move"].mean():.3f}')
print(f'  Avg distance from 0.5: {abs(unpredictable["avg_price"] - 0.5).mean():.3f}')
print()

print('=== VOLATILITY/VOLUME RELATIONSHIPS ===\n')

# Proxy for volume: number of strategy signals triggered
# Proxy for volatility: price movement magnitude
df['volatility_bucket'] = pd.qcut(df['price_move'], q=4, labels=['Low Vol', 'Med-Low Vol', 'Med-High Vol', 'High Vol'])

print('Win Rate by Volatility:')
for bucket in ['Low Vol', 'Med-Low Vol', 'Med-High Vol', 'High Vol']:
    subset = df[df['volatility_bucket'] == bucket]
    print(f'{bucket:15s}: {subset["win"].mean()*100:5.1f}% win rate, {subset["roi"].mean():6.3f} avg ROI ({len(subset)} trades)')
print()

print('=== STRATEGY-SPECIFIC FAILURE MODES ===\n')

# Identify losing streaks by strategy
for strategy in sorted(df['strategy'].unique()):
    subset = df[df['strategy'] == strategy].copy()
    subset = subset.sort_values('entry_date').reset_index(drop=True)
    subset['loss'] = subset['roi'] < 0
    
    # Find longest losing streak
    max_streak = 0
    current_streak = 0
    for is_loss in subset['loss']:
        if is_loss:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0
    
    # Identify patterns in losses
    losses = subset[subset['loss']]
    
    print(f'{strategy}:')
    print(f'  Max losing streak: {max_streak} trades')
    if len(losses) > 0:
        print(f'  Avg loss entry price: {losses["entry_price"].mean():.3f}')
        print(f'  Loss price move: {losses["price_move"].mean():.3f}')
        print(f'  % losses near extremes (<0.2 or >0.8): {((losses["entry_price"]<0.2) | (losses["entry_price"]>0.8)).mean()*100:.1f}%')
    print()

print('=== INEFFICIENCY IDENTIFICATION ===\n')

# Look for market conditions that consistently offer edges
print('Price Range Inefficiencies:')
price_buckets = pd.cut(df['entry_price'], bins=[0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
for bucket in price_buckets.unique().dropna():
    subset = df[df['entry_price'].apply(lambda x: x in bucket)]
    if len(subset) > 50:  # Only report if decent sample
        sharpe_proxy = subset['roi'].mean() / subset['roi'].std() if subset['roi'].std() > 0 else 0
        print(f'{bucket}: {subset["win"].mean()*100:.1f}% WR, {sharpe_proxy:.2f} Sharpe proxy ({len(subset)} trades)')
print()

print('=== TIME-BASED PATTERNS ===\n')

# Convert dates
df['entry_date'] = pd.to_datetime(df['entry_date'])
df['hour'] = df['entry_date'].dt.hour
df['day_of_week'] = df['entry_date'].dt.dayofweek  # 0=Monday, 6=Sunday

print('Win Rate by Day of Week:')
for day in range(7):
    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
    subset = df[df['day_of_week'] == day]
    if len(subset) > 20:
        print(f'{day_name:10s}: {subset["win"].mean()*100:5.1f}% WR ({len(subset)} trades)')
print()

print('Win Rate by Hour of Day (if >20 trades):')
for hour in sorted(df['hour'].unique()):
    subset = df[df['hour'] == hour]
    if len(subset) >= 20:
        print(f'Hour {hour:02d}: {subset["win"].mean()*100:5.1f}% WR ({len(subset)} trades)')
print()

print('=== MARKET TAXONOMY ===\n')

# Categorize markets based on characteristics
df['market_type'] = 'Unknown'

# High certainty (near 0 or 1)
df.loc[(df['entry_price'] < 0.2) | (df['entry_price'] > 0.8), 'market_type'] = 'High Certainty'

# Uncertain (near 0.5)
df.loc[(df['entry_price'] >= 0.4) & (df['entry_price'] <= 0.6), 'market_type'] = 'Uncertain'

# Moderate
df.loc[((df['entry_price'] >= 0.2) & (df['entry_price'] < 0.4)) | 
       ((df['entry_price'] > 0.6) & (df['entry_price'] <= 0.8)), 'market_type'] = 'Moderate Certainty'

print('Market Type Performance:')
for mtype in ['High Certainty', 'Moderate Certainty', 'Uncertain']:
    subset = df[df['market_type'] == mtype]
    print(f'\n{mtype}:')
    print(f'  Trades: {len(subset)}')
    print(f'  Win Rate: {subset["win"].mean()*100:.1f}%')
    print(f'  Avg ROI: {subset["roi"].mean():.3f}')
    print(f'  Avg Price Move: {subset["price_move"].mean():.3f}')
    print(f'  Sharpe Proxy: {subset["roi"].mean() / subset["roi"].std() if subset["roi"].std() > 0 else 0:.2f}')

print('\n=== FINAL ACTIONABLE INSIGHTS ===\n')

# What makes a market tradeable?
print('CHARACTERISTICS OF PROFITABLE MARKETS:')
winners = df[df['roi'] > 0.2]  # Strong winners
print(f'Entry price: {winners["entry_price"].mean():.3f} ± {winners["entry_price"].std():.3f}')
print(f'Distance from 0.5: {winners["distance_from_05"].mean():.3f}')
print(f'Avg price move: {winners["price_move"].mean():.3f}')
print()

print('CHARACTERISTICS OF LOSING MARKETS:')
losers = df[df['roi'] < -0.5]
print(f'Entry price: {losers["entry_price"].mean():.3f} ± {losers["entry_price"].std():.3f}')
print(f'Distance from 0.5: {losers["distance_from_05"].mean():.3f}')
print(f'Avg price move: {losers["price_move"].mean():.3f}')
