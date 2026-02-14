import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load backtest results
df = pd.read_csv('../backtest_results.csv')
print("Backtest Results Analysis")
print("========================")
print(f"Total trades: {len(df)}")
print(f"Strategies: {df['strategy'].unique()}")

# Convert dates
df['entry_date'] = pd.to_datetime(df['entry_date'])
df['exit_date'] = pd.to_datetime(df['exit_date'])
df['holding_days'] = (df['exit_date'] - df['entry_date']).dt.total_seconds() / (24*3600)

# Compute fee-adjusted returns
# Assume 2% entry fee, 2% exit fee
# If buying at price p, cost = p * (1 + 0.02)
# If selling at price q (resolution), proceeds = q * (1 - 0.02)
# ROI = (proceeds - cost) / cost
# Simplified: ROI_raw = (exit_price - entry_price) / entry_price
# Adjusted ROI = ((exit_price*(1-0.02)) - (entry_price*(1+0.02))) / (entry_price*(1+0.02))
df['roi_raw'] = df['pnl'] / df['entry_price']
df['roi_adj'] = ((df['exit_price']*(0.98)) - (df['entry_price']*(1.02))) / (df['entry_price']*(1.02))

# Summary statistics
print("\n=== Performance Summary ===")
print(f"Win rate: {(df['pnl'] > 0).mean():.2%}")
print(f"Average ROI (raw): {df['roi_raw'].mean():.2%}")
print(f"Average ROI (adjusted): {df['roi_adj'].mean():.2%}")
print(f"Median ROI (raw): {df['roi_raw'].median():.2%}")
print(f"Sharpe ratio (annualized): assuming zero risk-free rate")
# Compute daily returns approximation
# For each trade, daily return = (1+roi)^(1/holding_days) - 1
df['daily_return'] = np.where(df['holding_days'] > 0, 
                               (1 + df['roi_adj']) ** (1/df['holding_days']) - 1,
                               0)
# Annualized sharpe = mean(daily_return) / std(daily_return) * sqrt(252)
if df['daily_return'].std() > 0:
    sharpe = df['daily_return'].mean() / df['daily_return'].std() * np.sqrt(252)
    print(f"Sharpe ratio (approx): {sharpe:.3f}")
else:
    print("Sharpe ratio: undefined (zero volatility)")

# Max drawdown simulation
# Assume sequential trades with equal capital allocation
df_sorted = df.sort_values('entry_date').reset_index()
df_sorted['cumulative'] = (1 + df_sorted['roi_adj']).cumprod()
df_sorted['peak'] = df_sorted['cumulative'].cummax()
df_sorted['drawdown'] = (df_sorted['cumulative'] - df_sorted['peak']) / df_sorted['peak']
max_dd = df_sorted['drawdown'].min()
print(f"Max drawdown: {max_dd:.2%}")

# Plot cumulative returns
plt.figure(figsize=(10,6))
plt.plot(df_sorted['entry_date'], df_sorted['cumulative'], label='Cumulative Return')
plt.plot(df_sorted['entry_date'], df_sorted['peak'], label='Peak', linestyle='--')
plt.fill_between(df_sorted['entry_date'], df_sorted['cumulative'], df_sorted['peak'], 
                 where=df_sorted['cumulative'] < df_sorted['peak'], color='red', alpha=0.3)
plt.xlabel('Date')
plt.ylabel('Cumulative Return (multiplicative)')
plt.title('Backtest Performance - Trend Filter Strategy')
plt.legend()
plt.grid(True)
plt.savefig('../backtesting_system/trend_filter_performance.png')
print("\nSaved performance plot to trend_filter_performance.png")

# Analyze by market type? We don't have market categories. 
# Let's examine distribution of returns
print("\n=== Return Distribution ===")
print(df['roi_adj'].describe())

# Check for outliers
print(f"\nNumber of extreme wins (ROI > 100%): {(df['roi_adj'] > 1).sum()}")
print(f"Number of total losses (ROI = -100%): {(df['roi_adj'] <= -1).sum()}")

# Examine relationship between entry price and ROI
print("\n=== Entry Price vs ROI ===")
corr = df['entry_price'].corr(df['roi_adj'])
print(f"Correlation between entry price and ROI: {corr:.3f}")

# Save detailed analysis to CSV
df_sorted.to_csv('../backtesting_system/backtest_analysis.csv', index=False)
print("\nDetailed analysis saved to backtest_analysis.csv")