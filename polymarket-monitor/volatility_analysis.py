#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Volatility and price movement analysis"""

import json
import sys
import math
from datetime import datetime
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

def load_data():
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        return json.load(f)

def calculate_volatility(price_history):
    """Calculate price volatility (standard deviation of returns)"""
    if len(price_history) < 2:
        return 0
    
    prices = [p['p'] for p in price_history]
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
    
    if not returns:
        return 0
    
    mean_ret = sum(returns) / len(returns)
    variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
    return math.sqrt(variance)

def price_range(price_history):
    """Calculate price range (max - min)"""
    if not price_history:
        return 0
    prices = [p['p'] for p in price_history]
    return max(prices) - min(prices)

def categorize_market(question):
    q_lower = question.lower()
    if any(word in q_lower for word in ['nfl', 'nba', 'soccer', 'football', 'baseball', 'hockey', 'sport', 'game', 'match', 'player', 'team']):
        return 'sports'
    elif any(word in q_lower for word in ['election', 'president', 'senate', 'congress', 'vote', 'poll', 'trump', 'biden', 'republican', 'democrat', 'political']):
        return 'politics'
    elif any(word in q_lower for word in ['bitcoin', 'eth', 'crypto', 'btc', 'blockchain', 'token', 'coin']):
        return 'crypto'
    elif any(word in q_lower for word in ['stock', 'market', 'price', 'dow', 'nasdaq', 's&p', 'fed', 'interest rate', 'inflation']):
        return 'finance'
    elif any(word in q_lower for word in ['elon', 'musk', 'tweet', 'twitter', 'post', 'social media']):
        return 'social_media'
    else:
        return 'other'

def main():
    data = load_data()
    
    print("=" * 80)
    print("VOLATILITY & PRICE MOVEMENT ANALYSIS")
    print("=" * 80)
    print()
    
    # Analyze volatility by category
    category_stats = defaultdict(lambda: {'volatilities': [], 'ranges': [], 'volumes': []})
    
    for m in data:
        if not m.get('price_history') or len(m['price_history']) < 10:
            continue
        
        cat = categorize_market(m.get('question', ''))
        vol = calculate_volatility(m['price_history'])
        rng = price_range(m['price_history'])
        volume = m.get('volume', 0)
        
        category_stats[cat]['volatilities'].append(vol)
        category_stats[cat]['ranges'].append(rng)
        category_stats[cat]['volumes'].append(volume)
    
    print("📊 VOLATILITY BY CATEGORY")
    print("-" * 80)
    print(f"{'Category':<15} {'Avg Vol':<12} {'Avg Range':<12} {'Sample Size':<12} {'Avg Volume':<15}")
    print("-" * 80)
    
    for cat in sorted(category_stats.keys()):
        stats = category_stats[cat]
        if not stats['volatilities']:
            continue
        
        avg_vol = sum(stats['volatilities']) / len(stats['volatilities'])
        avg_range = sum(stats['ranges']) / len(stats['ranges'])
        avg_volume = sum(stats['volumes']) / len(stats['volumes'])
        sample_size = len(stats['volatilities'])
        
        print(f"{cat:<15} {avg_vol:<12.4f} {avg_range:<12.4f} {sample_size:<12,} ${avg_volume:<14,.0f}")
    
    print()
    
    # Analyze extreme price zones
    print("🎯 EXTREME PRICE ZONE ANALYSIS")
    print("-" * 80)
    
    extreme_low = []  # < 0.05
    extreme_high = []  # > 0.95
    mid_range = []  # 0.40-0.60
    
    for m in data:
        if not m.get('price_history'):
            continue
        
        latest_price = m['price_history'][-1]['p']
        vol = calculate_volatility(m['price_history'])
        
        if latest_price < 0.05:
            extreme_low.append({'vol': vol, 'price': latest_price, 'volume': m.get('volume', 0)})
        elif latest_price > 0.95:
            extreme_high.append({'vol': vol, 'price': latest_price, 'volume': m.get('volume', 0)})
        elif 0.40 <= latest_price <= 0.60:
            mid_range.append({'vol': vol, 'price': latest_price, 'volume': m.get('volume', 0)})
    
    print(f"\nExtreme Low (<0.05): {len(extreme_low):,} markets")
    if extreme_low:
        avg_vol = sum(m['vol'] for m in extreme_low) / len(extreme_low)
        avg_volume = sum(m['volume'] for m in extreme_low) / len(extreme_low)
        print(f"  Avg volatility: {avg_vol:.4f}")
        print(f"  Avg volume: ${avg_volume:,.0f}")
    
    print(f"\nExtreme High (>0.95): {len(extreme_high):,} markets")
    if extreme_high:
        avg_vol = sum(m['vol'] for m in extreme_high) / len(extreme_high)
        avg_volume = sum(m['volume'] for m in extreme_high) / len(extreme_high)
        print(f"  Avg volatility: {avg_vol:.4f}")
        print(f"  Avg volume: ${avg_volume:,.0f}")
    
    print(f"\nMid-range (0.40-0.60): {len(mid_range):,} markets")
    if mid_range:
        avg_vol = sum(m['vol'] for m in mid_range) / len(mid_range)
        avg_volume = sum(m['volume'] for m in mid_range) / len(mid_range)
        print(f"  Avg volatility: {avg_vol:.4f}")
        print(f"  Avg volume: ${avg_volume:,.0f}")
    
    print()
    
    # High volume vs low volume volatility
    print("💵 VOLUME TIER ANALYSIS")
    print("-" * 80)
    
    markets_with_vol = []
    for m in data:
        if m.get('price_history') and len(m['price_history']) >= 10:
            vol = calculate_volatility(m['price_history'])
            volume = m.get('volume', 0)
            markets_with_vol.append({'vol': vol, 'volume': volume})
    
    # Sort by volume
    markets_with_vol.sort(key=lambda x: x['volume'], reverse=True)
    
    top_10_pct = markets_with_vol[:len(markets_with_vol)//10]
    bottom_50_pct = markets_with_vol[len(markets_with_vol)//2:]
    
    if top_10_pct:
        avg_vol_high = sum(m['vol'] for m in top_10_pct) / len(top_10_pct)
        avg_volume_high = sum(m['volume'] for m in top_10_pct) / len(top_10_pct)
        print(f"Top 10% by volume ({len(top_10_pct):,} markets):")
        print(f"  Avg volatility: {avg_vol_high:.4f}")
        print(f"  Avg volume: ${avg_volume_high:,.0f}")
    
    if bottom_50_pct:
        avg_vol_low = sum(m['vol'] for m in bottom_50_pct) / len(bottom_50_pct)
        avg_volume_low = sum(m['volume'] for m in bottom_50_pct) / len(bottom_50_pct)
        print(f"\nBottom 50% by volume ({len(bottom_50_pct):,} markets):")
        print(f"  Avg volatility: {avg_vol_low:.4f}")
        print(f"  Avg volume: ${avg_volume_low:,.0f}")
    
    print()
    print("=" * 80)

if __name__ == '__main__':
    main()
