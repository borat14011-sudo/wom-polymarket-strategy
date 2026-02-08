"""
FRESH START - Polymarket Data Analysis
Discover REAL strategies from ACTUAL data
Working with: 149 resolved markets + 2,014 backtest trades
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import re
from collections import Counter

print("="*80)
print("STEP 1: DATA EXPLORATION")
print("="*80)

# Load all data files
print("\nLoading data files...")

# 1. Resolved markets (has outcomes) - 149 markets
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    resolved_raw = json.load(f)
resolved_df = pd.DataFrame(resolved_raw)
print(f"[OK] Resolved markets with outcomes: {len(resolved_df)}")

# 2. Full markets snapshot - 93,949 markets
with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    snapshot = json.load(f)
snapshot_df = pd.DataFrame(snapshot['markets'])
print(f"[OK] Markets snapshot: {len(snapshot_df):,}")

# 3. Previous backtest results - 2,014 trades
backtest_df = pd.read_csv('backtest_results.csv')
print(f"[OK] Backtest trades: {len(backtest_df):,}")
print(f"[OK] Unique markets in backtest: {backtest_df['market_id'].nunique()}")

print("\n" + "="*80)
print("STEP 1A: BASE RATE ANALYSIS")
print("="*80)

# Clean and prepare resolved data
resolved_df['winner_binary'] = resolved_df['winner'].apply(lambda x: 1 if str(x).lower() == 'yes' else 0)
resolved_df['volume_num'] = pd.to_numeric(resolved_df['volume_num'], errors='coerce')

# Parse final prices to get YES price
def get_yes_price(final_prices):
    if pd.isna(final_prices):
        return None
    parts = str(final_prices).split('|')
    if len(parts) >= 1:
        try:
            return float(parts[0])
        except:
            return None
    return None

resolved_df['final_yes_price'] = resolved_df['final_prices'].apply(get_yes_price)
resolved_df['final_yes_price'] = pd.to_numeric(resolved_df['final_yes_price'], errors='coerce')

# Overall base rate
yes_count = (resolved_df['winner'] == 'Yes').sum()
total_resolved = len(resolved_df)
base_rate_yes = yes_count / total_resolved * 100

print(f"\nOverall Base Rate (n={total_resolved}):")
print(f"  YES winners: {yes_count} ({base_rate_yes:.1f}%)")
print(f"  NO winners: {total_resolved - yes_count} ({100-base_rate_yes:.1f}%)")
print(f"  *** Markets heavily skew toward NO resolution ***")

print("\n" + "="*80)
print("STEP 1B: VOLUME DISTRIBUTION")
print("="*80)

volume_stats = resolved_df['volume_num'].describe(percentiles=[.1, .25, .5, .75, .9, .95, .99])
print(f"\nVolume Distribution (Resolved Markets):")
for k, v in volume_stats.items():
    print(f"  {k}: ${v:,.0f}")

# Categorize by volume
resolved_df['volume_category'] = pd.cut(
    resolved_df['volume_num'], 
    bins=[0, 1000, 10000, 100000, 1000000, float('inf')],
    labels=['<$1K', '$1K-$10K', '$10K-$100K', '$100K-$1M', '>$1M']
)

print(f"\nYES rates by volume category:")
volume_analysis = resolved_df.groupby('volume_category', observed=False).agg({
    'winner_binary': ['count', 'mean']
})
volume_analysis.columns = ['Count', 'YES_Rate']
for idx, row in volume_analysis.iterrows():
    print(f"  {idx}: {row['Count']:.0f} markets, {row['YES_Rate']*100:.1f}% YES")

print("\n" + "="*80)
print("STEP 2A: QUESTION PATTERN ANALYSIS")
print("="*80)

def analyze_pattern(df, pattern_name, condition):
    """Helper to analyze a pattern"""
    subset = df[condition]
    count = len(subset)
    if count == 0:
        return None
    yes_rate = subset['winner_binary'].mean() * 100
    avg_volume = subset['volume_num'].mean()
    return {
        'name': pattern_name,
        'count': count,
        'pct_of_total': count / len(df) * 100,
        'yes_rate': yes_rate,
        'no_rate': 100 - yes_rate,
        'avg_volume': avg_volume
    }

patterns = []

# Pattern: Questions starting with "Will"
will_mask = resolved_df['question'].str.lower().str.startswith('will', na=False)
patterns.append(analyze_pattern(resolved_df, "Starts with 'Will'", will_mask))

# Pattern: Celebrity/politician mentions
celeb_terms = ['trump', 'biden', 'musk', 'kanye', 'kardashian', 'taylor swift', 'elon']
celeb_mask = resolved_df['question'].str.lower().str.contains('|'.join(celeb_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Celebrity/Politician mentions", celeb_mask))

# Pattern: Trump specifically
trump_mask = resolved_df['question'].str.lower().str.contains('trump', na=False)
patterns.append(analyze_pattern(resolved_df, "Trump mentions", trump_mask))

# Pattern: Biden specifically
biden_mask = resolved_df['question'].str.lower().str.contains('biden', na=False)
patterns.append(analyze_pattern(resolved_df, "Biden mentions", biden_mask))

# Pattern: Crypto mentions
crypto_terms = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'blockchain']
crypto_mask = resolved_df['question'].str.lower().str.contains('|'.join(crypto_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Crypto mentions", crypto_mask))

# Pattern: Tech companies
tech_terms = ['apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook', 'tesla', 'nvidia']
tech_mask = resolved_df['question'].str.lower().str.contains('|'.join(tech_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Tech company mentions", tech_mask))

# Pattern: Election mentions
election_terms = ['election', 'senate', 'president', 'governor', 'primary', 'ballot', 'vote']
election_mask = resolved_df['question'].str.lower().str.contains('|'.join(election_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Election-related", election_mask))

# Pattern: Sports
sports_terms = ['super bowl', 'nba', 'nfl', 'mlb', 'world cup', 'olympics', 'championship']
sports_mask = resolved_df['question'].str.lower().str.contains('|'.join(sports_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Sports-related", sports_mask))

# Pattern: Date-specific (has month name or year)
date_mask = resolved_df['question'].str.contains(r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|20\d\d)\b', case=False, na=False, regex=True)
patterns.append(analyze_pattern(resolved_df, "Has specific date/year", date_mask))

# Pattern: Financial/business
finance_terms = ['stock', 'price', 'market', 'etf', 'ipo', 'merger', 'acquisition', 'revenue']
finance_mask = resolved_df['question'].str.lower().str.contains('|'.join(finance_terms), na=False)
patterns.append(analyze_pattern(resolved_df, "Financial/Business", finance_mask))

print("\nPattern Analysis Results:")
print("-" * 80)
for p in patterns:
    if p:
        print(f"\n{p['name']}:")
        print(f"  Count: {p['count']} ({p['pct_of_total']:.1f}% of total)")
        print(f"  YES rate: {p['yes_rate']:.1f}% | NO rate: {p['no_rate']:.1f}%")
        print(f"  Avg volume: ${p['avg_volume']:,.0f}")

print("\n" + "="*80)
print("STEP 2B: PRICE/OUTCOME ANALYSIS (CALIBRATION)")
print("="*80)

# Filter out rows with missing prices
price_df = resolved_df.dropna(subset=['final_yes_price'])

# Bin by final price (implied probability)
price_df['price_bin'] = pd.cut(
    price_df['final_yes_price'],
    bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
)

print("\nCalibration Analysis (Final Price vs Actual Outcome):")
print("-" * 80)
print(f"{'Price Bin':<10} {'Count':>6} {'Avg ImpProb':>12} {'Actual Yes%':>12} {'Error':>10}")
print("-" * 80)

for bin_name in price_df['price_bin'].cat.categories:
    subset = price_df[price_df['price_bin'] == bin_name]
    if len(subset) == 0:
        continue
    count = len(subset)
    avg_implied = subset['final_yes_price'].mean() * 100
    actual_yes = subset['winner_binary'].mean() * 100
    error = actual_yes - avg_implied
    print(f"{bin_name:<10} {count:>6} {avg_implied:>11.1f}% {actual_yes:>11.1f}% {error:>+9.1f}%")

# Specific analysis: Heavy favorites (>80% implied prob)
print("\n" + "-" * 80)
favorites = price_df[price_df['final_yes_price'] > 0.8]
if len(favorites) > 0:
    fav_yes_rate = favorites['winner_binary'].mean() * 100
    fav_avg_price = favorites['final_yes_price'].mean() * 100
    print(f"\nHeavy Favorites (>80% implied probability, n={len(favorites)}):")
    print(f"  Average implied YES prob: {fav_avg_price:.1f}%")
    print(f"  Actual YES rate: {fav_yes_rate:.1f}%")
    print(f"  Edge: {fav_yes_rate - fav_avg_price:+.1f}% (negative = favorites underperform)")

# Longshots (<20% implied prob)
longshots = price_df[price_df['final_yes_price'] < 0.2]
if len(longshots) > 0:
    long_yes_rate = longshots['winner_binary'].mean() * 100
    long_avg_price = longshots['final_yes_price'].mean() * 100
    print(f"\nLongshots (<20% implied probability, n={len(longshots)}):")
    print(f"  Average implied YES prob: {long_avg_price:.1f}%")
    print(f"  Actual YES rate: {long_yes_rate:.1f}%")
    print(f"  Edge: {long_yes_rate - long_avg_price:+.1f}% (positive = longshots overperform)")

# Middle range (20-80%)
middle = price_df[(price_df['final_yes_price'] >= 0.2) & (price_df['final_yes_price'] <= 0.8)]
if len(middle) > 0:
    mid_yes_rate = middle['winner_binary'].mean() * 100
    mid_avg_price = middle['final_yes_price'].mean() * 100
    print(f"\nMiddle Range (20-80% implied probability, n={len(middle)}):")
    print(f"  Average implied YES prob: {mid_avg_price:.1f}%")
    print(f"  Actual YES rate: {mid_yes_rate:.1f}%")
    print(f"  Edge: {mid_yes_rate - mid_avg_price:+.1f}%")

print("\n" + "="*80)
print("STEP 2C: BACKTEST RESULTS ANALYSIS")
print("="*80)

# Analyze the existing backtest results
backtest_df['won'] = backtest_df['pnl'] > 0
backtest_df['entry_price_bucket'] = pd.cut(
    backtest_df['entry_price'],
    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
    labels=['0-20%', '20-40%', '40-60%', '60-80%', '80-100%']
)

print(f"\nOverall Backtest Performance:")
print(f"  Total trades: {len(backtest_df)}")
print(f"  Win rate: {backtest_df['won'].mean()*100:.1f}%")
print(f"  Total P&L: ${backtest_df['pnl'].sum():.2f}")
print(f"  Avg P&L per trade: ${backtest_df['pnl'].mean():.3f}")
print(f"  Avg ROI: {backtest_df['roi'].mean()*100:.1f}%")

# Performance by entry price bucket
print(f"\nPerformance by Entry Price Bucket:")
bt_analysis = backtest_df.groupby('entry_price_bucket', observed=False).agg({
    'pnl': ['count', 'mean', 'sum'],
    'won': 'mean',
    'roi': 'mean'
})
bt_analysis.columns = ['Count', 'Avg_PnL', 'Total_PnL', 'Win_Rate', 'Avg_ROI']
print(bt_analysis.round(3))

# Calculate P&L with 5% fees
backtest_df['pnl_after_fees'] = backtest_df['pnl'] * 0.95  # 5% fee
print(f"\nWith 5% fees applied:")
print(f"  Total P&L before fees: ${backtest_df['pnl'].sum():.2f}")
print(f"  Total P&L after fees: ${backtest_df['pnl_after_fees'].sum():.2f}")
print(f"  Fee impact: ${backtest_df['pnl'].sum() - backtest_df['pnl_after_fees'].sum():.2f}")

print("\n" + "="*80)
print("STEP 2D: MARKET DURATION ANALYSIS")
print("="*80)

try:
    resolved_df['event_end_date'] = pd.to_datetime(resolved_df['event_end_date'], errors='coerce')
    resolved_df['created_time'] = pd.to_datetime(resolved_df['created_time'], errors='coerce')
    resolved_df['duration_days'] = (resolved_df['event_end_date'] - resolved_df['created_time']).dt.days
    
    # Remove negative durations (data errors)
    valid_durations = resolved_df[resolved_df['duration_days'] >= 0]
    
    # Categorize by duration
    valid_durations['duration_category'] = pd.cut(
        valid_durations['duration_days'],
        bins=[0, 7, 30, 90, 365, float('inf')],
        labels=['<1 week', '1-4 weeks', '1-3 months', '3-12 months', '>1 year']
    )
    
    print(f"\nYES rates by market duration:")
    dur_analysis = valid_durations.groupby('duration_category', observed=False).agg({
        'winner_binary': ['count', 'mean'],
        'volume_num': 'median'
    })
    dur_analysis.columns = ['Count', 'YES_Rate', 'Median_Volume']
    for idx, row in dur_analysis.iterrows():
        print(f"  {idx}: {row['Count']:.0f} markets, {row['YES_Rate']*100:.1f}% YES, ${row['Median_Volume']:,.0f} median vol")
except Exception as e:
    print(f"  Could not analyze duration: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)

# Save enriched data
resolved_df.to_csv('resolved_markets_enriched.csv', index=False)
print(f"\n[OK] Saved enriched resolved markets to resolved_markets_enriched.csv")

# Print summary for next step
print("\n" + "="*80)
print("KEY PATTERNS DISCOVERED:")
print("="*80)
print(f"1. Base rate heavily skewed toward NO: {100-base_rate_yes:.1f}% vs {base_rate_yes:.1f}% (n={total_resolved})")
for p in patterns:
    if p and p['count'] >= 5:
        print(f"2. {p['name']}: {p['yes_rate']:.1f}% YES rate (n={p['count']})")
print(f"3. Backtest shows {backtest_df['won'].mean()*100:.1f}% win rate on {len(backtest_df)} trades")
print(f"4. Fees (5%) reduce P&L from ${backtest_df['pnl'].sum():.2f} to ${backtest_df['pnl_after_fees'].sum():.2f}")
