"""
FRESH START - Polymarket Data Analysis
Discover REAL strategies from ACTUAL data
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

# 1. Resolved markets (has outcomes)
with open('polymarket_resolved_markets.json', 'r', encoding='utf-8-sig') as f:
    resolved_raw = json.load(f)
resolved_df = pd.DataFrame(resolved_raw)
print(f"[OK] Resolved markets: {len(resolved_df):,}")

# 2. Full markets snapshot
with open('markets_snapshot_20260207_221914.json', 'r', encoding='utf-8') as f:
    snapshot = json.load(f)
snapshot_df = pd.DataFrame(snapshot['markets'])
print(f"[OK] Markets snapshot: {len(snapshot_df):,}")

# 3. Previous backtest results
backtest_df = pd.read_csv('backtest_results.csv')
print(f"[OK] Backtest trades: {len(backtest_df):,}")

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

# Overall base rate
yes_count = (resolved_df['winner'] == 'Yes').sum()
total_resolved = len(resolved_df)
base_rate_yes = yes_count / total_resolved * 100

print(f"\nOverall Base Rate:")
print(f"  Total resolved markets: {total_resolved:,}")
print(f"  YES winners: {yes_count:,} ({base_rate_yes:.1f}%)")
print(f"  NO winners: {total_resolved - yes_count:,} ({100-base_rate_yes:.1f}%)")

print("\n" + "="*80)
print("STEP 1B: VOLUME DISTRIBUTION")
print("="*80)

volume_stats = resolved_df['volume_num'].describe(percentiles=[.1, .25, .5, .75, .9, .95, .99])
print(f"\nVolume Distribution (Resolved Markets):")
print(volume_stats)

# Categorize by volume
resolved_df['volume_category'] = pd.cut(
    resolved_df['volume_num'], 
    bins=[0, 1000, 10000, 100000, 1000000, float('inf')],
    labels=['<$1K', '$1K-$10K', '$10K-$100K', '$100K-$1M', '>$1M']
)

volume_yes_rates = resolved_df.groupby('volume_category').agg({
    'winner_binary': ['count', 'mean']
}).round(3)
print(f"\nYES rates by volume category:")
print(volume_yes_rates)

print("\n" + "="*80)
print("STEP 2A: QUESTION PATTERN ANALYSIS")
print("="*80)

# Pattern: Questions starting with "Will"
will_pattern = resolved_df['question'].str.startswith('Will', case=False, na=False)
will_yes_rate = resolved_df[will_pattern]['winner_binary'].mean() * 100
will_count = will_pattern.sum()

print(f"\nQuestions starting with 'Will':")
print(f"  Count: {will_count:,} ({will_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {will_yes_rate:.1f}%")
print(f"  NO rate: {100-will_yes_rate:.1f}%")

# Pattern: Celebrity mentions
celebrity_terms = ['trump', 'biden', 'musk', 'kanye', 'kim kardashian', 'taylor swift', 'elon', 'celebrity']
celebrity_pattern = resolved_df['question'].str.lower().str.contains('|'.join(celebrity_terms), na=False)
celeb_yes_rate = resolved_df[celebrity_pattern]['winner_binary'].mean() * 100
celeb_count = celebrity_pattern.sum()

print(f"\nQuestions mentioning celebrities/politicians:")
print(f"  Count: {celeb_count:,} ({celeb_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {celeb_yes_rate:.1f}%")
print(f"  NO rate: {100-celeb_yes_rate:.1f}%")

# Pattern: Crypto mentions
crypto_terms = ['bitcoin', 'ethereum', 'crypto', 'btc', 'eth', 'blockchain', 'cryptocurrency']
crypto_pattern = resolved_df['question'].str.lower().str.contains('|'.join(crypto_terms), na=False)
crypto_yes_rate = resolved_df[crypto_pattern]['winner_binary'].mean() * 100
crypto_count = crypto_pattern.sum()

print(f"\nQuestions about crypto:")
print(f"  Count: {crypto_count:,} ({crypto_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {crypto_yes_rate:.1f}%")
print(f"  NO rate: {100-crypto_yes_rate:.1f}%")

# Pattern: Tech companies
tech_terms = ['apple', 'google', 'microsoft', 'amazon', 'meta', 'facebook', 'tesla', 'nvidia', 'netflix']
tech_pattern = resolved_df['question'].str.lower().str.contains('|'.join(tech_terms), na=False)
tech_yes_rate = resolved_df[tech_pattern]['winner_binary'].mean() * 100
tech_count = tech_pattern.sum()

print(f"\nQuestions about tech companies:")
print(f"  Count: {tech_count:,} ({tech_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {tech_yes_rate:.1f}%")
print(f"  NO rate: {100-tech_yes_rate:.1f}%")

# Pattern: Election mentions
election_terms = ['election', 'vote', 'senate', 'president', 'governor', 'primary', 'ballot']
election_pattern = resolved_df['question'].str.lower().str.contains('|'.join(election_terms), na=False)
election_yes_rate = resolved_df[election_pattern]['winner_binary'].mean() * 100
election_count = election_pattern.sum()

print(f"\nQuestions about elections:")
print(f"  Count: {election_count:,} ({election_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {election_yes_rate:.1f}%")
print(f"  NO rate: {100-election_yes_rate:.1f}%")

# Pattern: Sports
sports_terms = ['super bowl', 'nba', 'nfl', 'mlb', 'world cup', 'olympics', 'championship', 'playoff']
sports_pattern = resolved_df['question'].str.lower().str.contains('|'.join(sports_terms), na=False)
sports_yes_rate = resolved_df[sports_pattern]['winner_binary'].mean() * 100
sports_count = sports_pattern.sum()

print(f"\nQuestions about sports:")
print(f"  Count: {sports_count:,} ({sports_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {sports_yes_rate:.1f}%")
print(f"  NO rate: {100-sports_yes_rate:.1f}%")

# Pattern: Date-specific questions
date_pattern = resolved_df['question'].str.contains(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December|\d{4})\b', case=False, na=False, regex=True)
date_yes_rate = resolved_df[date_pattern]['winner_binary'].mean() * 100
date_count = date_pattern.sum()

print(f"\nQuestions with specific dates/years:")
print(f"  Count: {date_count:,} ({date_count/total_resolved*100:.1f}% of total)")
print(f"  YES rate: {date_yes_rate:.1f}%")
print(f"  NO rate: {100-date_yes_rate:.1f}%")

print("\n" + "="*80)
print("STEP 2B: PRICE/OUTCOME ANALYSIS")
print("="*80)

# Clean final prices for analysis
resolved_df['final_yes_price'] = pd.to_numeric(resolved_df['final_yes_price'], errors='coerce')
resolved_df = resolved_df.dropna(subset=['final_yes_price'])

# Bin by final price (implied probability)
resolved_df['price_bin'] = pd.cut(
    resolved_df['final_yes_price'],
    bins=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    labels=['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
)

price_analysis = resolved_df.groupby('price_bin').agg({
    'winner_binary': ['count', 'mean'],
    'final_yes_price': 'mean'
}).round(3)
price_analysis.columns = ['Count', 'Actual_Yes_Rate', 'Avg_Implied_Prob']
price_analysis['Calibration_Error'] = (price_analysis['Actual_Yes_Rate'] - price_analysis['Avg_Implied_Prob']).round(3)

print(f"\nCalibration Analysis (Final Price vs Actual Outcome):")
print(price_analysis)

# Calculate edge by price bucket
print(f"\nEdge Analysis:")
print("  Negative error = Market overpriced YES (favorites lose more than expected)")
print("  Positive error = Market underpriced YES (underdogs win more than expected)")

# Specific analysis: Heavy favorites (>80% implied prob)
favorites = resolved_df[resolved_df['final_yes_price'] > 0.8]
fav_yes_rate = favorites['winner_binary'].mean() * 100
fav_avg_price = favorites['final_yes_price'].mean() * 100
print(f"\nHeavy Favorites (>80% implied probability):")
print(f"  Count: {len(favorites):,}")
print(f"  Average implied YES prob: {fav_avg_price:.1f}%")
print(f"  Actual YES rate: {fav_yes_rate:.1f}%")
print(f"  Edge: {fav_yes_rate - fav_avg_price:.1f}% (negative = favorites underperform)")

# Longshots (<20% implied prob)
longshots = resolved_df[resolved_df['final_yes_price'] < 0.2]
long_yes_rate = longshots['winner_binary'].mean() * 100
long_avg_price = longshots['final_yes_price'].mean() * 100
print(f"\nLongshots (<20% implied probability):")
print(f"  Count: {len(longshots):,}")
print(f"  Average implied YES prob: {long_avg_price:.1f}%")
print(f"  Actual YES rate: {long_yes_rate:.1f}%")
print(f"  Edge: {long_yes_rate - long_avg_price:.1f}% (positive = longshots overperform)")

print("\n" + "="*80)
print("STEP 2C: MARKET DURATION ANALYSIS")
print("="*80)

# Parse dates
try:
    resolved_df['event_end_date'] = pd.to_datetime(resolved_df['event_end_date'], errors='coerce')
    # Use created_time as proxy for start (when available)
    resolved_df['created_time'] = pd.to_datetime(resolved_df['created_time'], errors='coerce')
    resolved_df['duration_days'] = (resolved_df['event_end_date'] - resolved_df['created_time']).dt.days
    
    # Categorize by duration
    resolved_df['duration_category'] = pd.cut(
        resolved_df['duration_days'],
        bins=[-float('inf'), 7, 30, 90, 365, float('inf')],
        labels=['<1 week', '1-4 weeks', '1-3 months', '3-12 months', '>1 year']
    )
    
    duration_analysis = resolved_df.groupby('duration_category').agg({
        'winner_binary': ['count', 'mean'],
        'volume_num': 'median'
    }).round(3)
    print(f"\nYES rates by market duration:")
    print(duration_analysis)
except Exception as e:
    print(f"  Could not analyze duration: {e}")

print("\n" + "="*80)
print("STEP 2D: TIME PATTERNS")
print("="*80)

try:
    resolved_df['end_hour'] = resolved_df['event_end_date'].dt.hour
    resolved_df['end_dayofweek'] = resolved_df['event_end_date'].dt.dayofweek
    
    print(f"\nResolution by hour of day:")
    hour_analysis = resolved_df.groupby('end_hour')['winner_binary'].agg(['count', 'mean']).round(3)
    hour_analysis = hour_analysis[hour_analysis['count'] >= 10]  # Filter low sample
    print(hour_analysis)
    
    print(f"\nResolution by day of week (0=Monday):")
    dow_analysis = resolved_df.groupby('end_dayofweek')['winner_binary'].agg(['count', 'mean']).round(3)
    print(dow_analysis)
except Exception as e:
    print(f"  Could not analyze time patterns: {e}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE - Saving results...")
print("="*80)

# Save intermediate results
resolved_df.to_csv('resolved_markets_enriched.csv', index=False)
print(f"\n[OK] Saved enriched resolved markets to resolved_markets_enriched.csv")

# Print key findings for next step
print("\n" + "="*80)
print("KEY PATTERNS DISCOVERED:")
print("="*80)
print(f"1. Base rate heavily skewed toward NO: {100-base_rate_yes:.1f}% vs {base_rate_yes:.1f}%")
print(f"2. 'Will' questions: {will_yes_rate:.1f}% YES rate (n={will_count})")
print(f"3. Celebrity/Trump questions: {celeb_yes_rate:.1f}% YES rate (n={celeb_count})")
print(f"4. Election questions: {election_yes_rate:.1f}% YES rate (n={election_count})")
print(f"5. Crypto questions: {crypto_yes_rate:.1f}% YES rate (n={crypto_count})")
print(f"6. Favorites (>80%) win {fav_yes_rate:.1f}% vs {fav_avg_price:.1f}% implied")
print(f"7. Longshots (<20%) win {long_yes_rate:.1f}% vs {long_avg_price:.1f}% implied")
