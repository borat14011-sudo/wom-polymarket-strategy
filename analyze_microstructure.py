import pandas as pd
import numpy as np

# Load backtest results
df = pd.read_csv('backtest_results.csv')

print('=== PRICE MOVEMENT ANALYSIS ===\n')

# 1. Entry price distribution
print('Entry Price Distribution:')
print(df['entry_price'].describe())
print('\nPrice ranges:')
near_extremes = ((df['entry_price'] < 0.2) | (df['entry_price'] > 0.8)).sum()
mid_range = ((df['entry_price'] >= 0.3) & (df['entry_price'] <= 0.7)).sum()
close_range = ((df['entry_price'] >= 0.4) & (df['entry_price'] <= 0.6)).sum()
print(f'Near extremes (<0.2 or >0.8): {near_extremes} trades ({near_extremes/len(df)*100:.1f}%)')
print(f'Mid-range (0.3-0.7): {mid_range} trades ({mid_range/len(df)*100:.1f}%)')
print(f'Close (0.4-0.6): {close_range} trades ({close_range/len(df)*100:.1f}%)\n')

# 2. Win rate by entry price region
print('Win Rate by Entry Price Region:')
df['price_region'] = pd.cut(df['entry_price'], bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0], 
                             labels=['0-0.2', '0.2-0.4', '0.4-0.6', '0.6-0.8', '0.8-1.0'])
df['win'] = df['roi'] > 0
for region in sorted(df['price_region'].dropna().unique()):
    subset = df[df['price_region'] == region]
    wr = subset['win'].mean() * 100
    count = len(subset)
    avg_roi = subset['roi'].mean()
    print(f'{region}: {wr:.1f}% win rate, avg ROI: {avg_roi:.3f} ({count} trades)')
print()

# 3. ROI by strategy
print('=== STRATEGY PERFORMANCE ===\n')
for strategy in sorted(df['strategy'].unique()):
    subset = df[df['strategy'] == strategy]
    wins = subset['win'].sum()
    losses = len(subset) - wins
    avg_win_roi = subset[subset['win']]['roi'].mean() if wins > 0 else 0
    avg_loss_roi = subset[~subset['win']]['roi'].mean() if losses > 0 else 0
    
    print(f'{strategy}:')
    print(f'  Trades: {len(subset)} ({wins}W / {losses}L)')
    print(f'  Win Rate: {subset["win"].mean()*100:.1f}%')
    print(f'  Avg ROI: {subset["roi"].mean():.3f}')
    print(f'  Avg Win: {avg_win_roi:.3f} | Avg Loss: {avg_loss_roi:.3f}')
    print(f'  Best: {subset["roi"].max():.3f} | Worst: {subset["roi"].min():.3f}')
    print()

print('=== PRICE MOVEMENT PATTERNS ===\n')

# 4. Price movement magnitude
df['price_move'] = abs(df['exit_price'] - df['entry_price'])
print('Absolute Price Movement:')
print(df['price_move'].describe())
print()

# 5. Directional bias
df['move_direction'] = np.where(df['exit_price'] > df['entry_price'], 'UP', 'DOWN')
print('Directional Patterns:')
print(df['move_direction'].value_counts())
print(f'\nWin rate when price went UP: {df[df["move_direction"]=="UP"]["win"].mean()*100:.1f}%')
print(f'Win rate when price went DOWN: {df[df["move_direction"]=="DOWN"]["win"].mean()*100:.1f}%')
print()

# 6. Large moves analysis
large_moves = df[df['price_move'] > 0.3]
print(f'Large Moves (>30 cent change): {len(large_moves)} trades ({len(large_moves)/len(df)*100:.1f}%)')
print(f'Large move win rate: {large_moves["win"].mean()*100:.1f}%')
print(f'Small move (<10 cent) win rate: {df[df["price_move"]<0.1]["win"].mean()*100:.1f}%')
print()

# 7. Volatility proxy analysis
print('=== MARKET BEHAVIOR BY PRICE LEVEL ===\n')
# Markets near 0.5 are most uncertain, near 0/1 are more certain
df['distance_from_05'] = abs(df['entry_price'] - 0.5)
print('Uncertainty (distance from 0.5):')
for threshold in [0.1, 0.2, 0.3]:
    uncertain = df[df['distance_from_05'] <= threshold]
    certain = df[df['distance_from_05'] > threshold]
    print(f'\nMarkets within {threshold:.1f} of 0.5 (UNCERTAIN):')
    print(f'  Count: {len(uncertain)} trades')
    print(f'  Win rate: {uncertain["win"].mean()*100:.1f}%')
    print(f'  Avg price move: {uncertain["price_move"].mean():.3f}')
    print(f'Markets >  {threshold:.1f} from 0.5 (CERTAIN):')
    print(f'  Count: {len(certain)} trades')
    print(f'  Win rate: {certain["win"].mean()*100:.1f}%')
    print(f'  Avg price move: {certain["price_move"].mean():.3f}')

print('\n=== COMMON FAILURE MODES ===\n')

# 8. Identifying pump & dumps (sharp price move followed by reversal)
# Look for trades that lost money despite price moving in the right direction initially
df['price_direction'] = np.where(df['exit_price'] > df['entry_price'], 'UP', 'DOWN')
df['position_direction'] = np.where(df['outcome'] == 'YES', 'LONG', 'SHORT')

print('Position vs Price Direction:')
# If we went LONG (bought YES) and price went DOWN, we lost on fundamentals
# If we went LONG and price went UP but still lost, that's a reversal/pump&dump
went_long = df[df['outcome'] == 'YES']
went_short = df[df['outcome'] == 'NO']

print(f'\nLONG positions:')
long_up = went_long[went_long['price_direction'] == 'UP']
long_down = went_long[went_long['price_direction'] == 'DOWN']
print(f'  Price went UP: {len(long_up)} trades, {long_up["win"].mean()*100:.1f}% win rate')
print(f'  Price went DOWN: {len(long_down)} trades, {long_down["win"].mean()*100:.1f}% win rate')

print(f'\nSHORT positions:')
short_up = went_short[went_short['price_direction'] == 'UP']
short_down = went_short[went_short['price_direction'] == 'DOWN']
print(f'  Price went UP: {len(short_up)} trades, {short_up["win"].mean()*100:.1f}% win rate')
print(f'  Price went DOWN: {len(short_down)} trades, {short_down["win"].mean()*100:.1f}% win rate')

# 9. ROI distribution
print('\n=== ROI DISTRIBUTION ===\n')
print(df['roi'].describe())
print(f'\nTotal losers (ROI = -1.0): {(df["roi"] == -1.0).sum()} trades')
print(f'Partial winners (0 < ROI < 0.5): {((df["roi"] > 0) & (df["roi"] < 0.5)).sum()} trades')
print(f'Strong winners (ROI > 0.5): {(df["roi"] > 0.5).sum()} trades')
