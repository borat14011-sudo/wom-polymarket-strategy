#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Statistical pattern analysis for Polymarket backtest data"""

import json
import sys
from datetime import datetime
from collections import defaultdict
import re

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

def load_data():
    """Load the backtest dataset"""
    with open('historical-data-scraper/data/backtest_dataset_v1.json', 'r') as f:
        return json.load(f)

def categorize_market(question):
    """Extract category from question text"""
    q_lower = question.lower()
    
    # Category patterns
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
    elif any(word in q_lower for word in ['will', 'happen', 'occur', 'event', 'announce']):
        return 'events'
    else:
        return 'other'

def analyze_dataset():
    """Main analysis function"""
    data = load_data()
    
    print("=" * 80)
    print("POLYMARKET BACKTEST PATTERN ANALYSIS")
    print("=" * 80)
    print()
    
    print(f"📊 Total records: {len(data):,}")
    print()
    
    # Check resolved vs unresolved
    resolved = [m for m in data if m.get('closed') and m.get('outcome') is not None]
    unresolved = [m for m in data if not m.get('closed') or m.get('outcome') is None]
    
    print(f"✅ Resolved markets: {len(resolved):,}")
    print(f"⏳ Unresolved markets: {len(unresolved):,}")
    print()
    
    if len(resolved) == 0:
        print("🚨 CRITICAL ISSUE: No resolved markets found!")
        print("   Cannot perform backtest analysis without outcomes.")
        print()
        print("   Analyzing data structure instead...")
        print()
        
        # Analyze what we have
        analyze_structure(data)
        return
    
    # If we have resolved markets, do full analysis
    print(f"Proceeding with analysis of {len(resolved)} resolved markets...")
    # ... rest of analysis

def analyze_structure(data):
    """Analyze the structure of unresolved data"""
    
    print("=" * 80)
    print("DATA STRUCTURE ANALYSIS (No Outcomes Available)")
    print("=" * 80)
    print()
    
    # Category distribution
    print("📁 CATEGORY DISTRIBUTION")
    print("-" * 80)
    categories = defaultdict(int)
    for m in data:
        cat = categorize_market(m.get('question', ''))
        categories[cat] += 1
    
    total = sum(categories.values())
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) * 100
        print(f"  {cat:15s}: {count:6,} markets ({pct:5.1f}%)")
    print()
    
    # Volume analysis
    print("💰 VOLUME ANALYSIS")
    print("-" * 80)
    volumes = [m.get('volume', 0) for m in data]
    volumes_sorted = sorted(volumes, reverse=True)
    
    print(f"  Total volume: ${sum(volumes):,.0f}")
    print(f"  Mean volume: ${sum(volumes)/len(volumes):,.0f}")
    print(f"  Median volume: ${volumes_sorted[len(volumes)//2]:,.0f}")
    print(f"  Top 10% avg: ${sum(volumes_sorted[:len(volumes)//10])/(len(volumes)//10):,.0f}")
    print(f"  Bottom 50% avg: ${sum(volumes_sorted[len(volumes)//2:])/(len(volumes)//2):,.0f}")
    print()
    
    # Price range analysis
    print("💵 PRICE DISTRIBUTION")
    print("-" * 80)
    price_ranges = {
        '0.00-0.10': 0,
        '0.10-0.30': 0,
        '0.30-0.50': 0,
        '0.50-0.70': 0,
        '0.70-0.90': 0,
        '0.90-1.00': 0
    }
    
    for m in data:
        if m.get('price_history'):
            latest_price = m['price_history'][-1]['p']
            if latest_price < 0.10:
                price_ranges['0.00-0.10'] += 1
            elif latest_price < 0.30:
                price_ranges['0.10-0.30'] += 1
            elif latest_price < 0.50:
                price_ranges['0.30-0.50'] += 1
            elif latest_price < 0.70:
                price_ranges['0.50-0.70'] += 1
            elif latest_price < 0.90:
                price_ranges['0.70-0.90'] += 1
            else:
                price_ranges['0.90-1.00'] += 1
    
    total_with_prices = sum(price_ranges.values())
    for range_name, count in price_ranges.items():
        pct = (count / total_with_prices * 100) if total_with_prices > 0 else 0
        print(f"  {range_name}: {count:6,} markets ({pct:5.1f}%)")
    print()
    
    # Time-based analysis
    print("⏰ TEMPORAL PATTERNS")
    print("-" * 80)
    
    hours = defaultdict(int)
    days_of_week = defaultdict(int)
    
    for m in data:
        if m.get('price_history'):
            for price_point in m['price_history']:
                dt = datetime.fromtimestamp(price_point['t'])
                hours[dt.hour] += 1
                days_of_week[dt.strftime('%A')] += 1
    
    print("  Trading activity by hour (UTC):")
    for hour in range(24):
        count = hours.get(hour, 0)
        bar = '█' * (count // (max(hours.values()) // 50)) if hours.values() else ''
        print(f"    {hour:02d}:00 - {count:8,} {bar}")
    
    print()
    print("  Trading activity by day of week:")
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in day_order:
        count = days_of_week.get(day, 0)
        total_activity = sum(days_of_week.values())
        pct = (count / total_activity * 100) if total_activity > 0 else 0
        print(f"    {day:9s}: {count:10,} ({pct:5.1f}%)")
    
    print()
    print("=" * 80)
    print("⚠️  LIMITATION: Cannot calculate win rates, edge, or EV without outcomes")
    print("=" * 80)

if __name__ == '__main__':
    analyze_dataset()
