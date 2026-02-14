import requests
import json
import pandas as pd
from datetime import datetime

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

def fetch_market_data():
    """Fetch and analyze Kalshi market data"""
    print("Fetching Kalshi market data...")
    
    all_markets = []
    events_response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 100})
    events_data = events_response.json()
    
    for event in events_data.get('events', []):
        for market in event.get('markets', []):
            market_data = {
                'event_id': event.get('id'),
                'event_title': event.get('title'),
                'event_category': event.get('category'),
                'market_id': market.get('id'),
                'market_ticker': market.get('ticker'),
                'market_title': market.get('title'),
                'yes_price': market.get('yes_price'),
                'no_price': market.get('no_price'),
                'volume': market.get('volume'),
                'status': market.get('status'),
                'close_date': market.get('close_date'),
                'previous_day_price': market.get('previous_day_price'),
                'previous_week_price': market.get('previous_week_price'),
                'created_time': market.get('created_time')
            }
            all_markets.append(market_data)
    
    return pd.DataFrame(all_markets)

def analyze_strategies(df):
    """Analyze different trading strategies"""
    
    # Filter active markets
    active_df = df[df['status'] == 'active'].copy()
    print(f"Active markets: {len(active_df)}")
    
    # Strategy 1: Buy the Dip (already checked)
    active_df['week_drop_pct'] = (active_df['yes_price'] - active_df['previous_week_price']) / active_df['previous_week_price'] * 100
    dip_opportunities = active_df[active_df['week_drop_pct'] < -10]
    print(f"\n1. Buy the Dip opportunities (>10% drop): {len(dip_opportunities)}")
    
    # Strategy 2: Near Certainty (high probability underpriced)
    high_prob = active_df[(active_df['yes_price'] > 70) & (active_df['yes_price'] < 90)]
    print(f"\n2. Near Certainty opportunities (70-90¢): {len(high_prob)}")
    
    # Strategy 3: Longshots (low probability overpriced)
    longshots = active_df[(active_df['yes_price'] < 30) & (active_df['yes_price'] > 5)]
    print(f"\n3. Longshot opportunities (5-30¢): {len(longshots)}")
    
    # Strategy 4: Mean reversion candidates (prices near 50¢)
    mean_reversion = active_df[(active_df['yes_price'] > 40) & (active_df['yes_price'] < 60)]
    print(f"\n4. Mean reversion candidates (40-60¢): {len(mean_reversion)}")
    
    # Strategy 5: High volume momentum
    high_volume = active_df[active_df['volume'] > 10000].sort_values('volume', ascending=False)
    print(f"\n5. High volume markets (>$10k): {len(high_volume)}")
    
    # Strategy 6: Low volume inefficiency
    low_volume = active_df[(active_df['volume'] < 1000) & (active_df['volume'] > 0)]
    print(f"\n6. Low volume inefficiency markets (<$1k): {len(low_volume)}")
    
    # Strategy 7: Category analysis
    print(f"\n7. Category distribution:")
    category_counts = active_df['event_category'].value_counts()
    for category, count in category_counts.head(10).items():
        print(f"   {category}: {count} markets")
    
    # Strategy 8: Time to expiration analysis
    # Parse close dates
    try:
        active_df['close_date_parsed'] = pd.to_datetime(active_df['close_date'])
        active_df['days_to_close'] = (active_df['close_date_parsed'] - pd.Timestamp.now()).dt.days
        
        short_term = active_df[active_df['days_to_close'] < 7]
        medium_term = active_df[(active_df['days_to_close'] >= 7) & (active_df['days_to_close'] < 30)]
        long_term = active_df[active_df['days_to_close'] >= 30]
        
        print(f"\n8. Time to expiration:")
        print(f"   Short-term (<7 days): {len(short_term)}")
        print(f"   Medium-term (7-30 days): {len(medium_term)}")
        print(f"   Long-term (>30 days): {len(long_term)}")
    except:
        print(f"\n8. Time to expiration: Could not parse dates")
    
    return {
        'dip_opportunities': dip_opportunities,
        'near_certainty': high_prob,
        'longshots': longshots,
        'mean_reversion': mean_reversion,
        'high_volume': high_volume,
        'low_volume': low_volume,
        'short_term': short_term if 'short_term' in locals() else None,
        'medium_term': medium_term if 'medium_term' in locals() else None,
        'long_term': long_term if 'long_term' in locals() else None
    }

def main():
    df = fetch_market_data()
    print(f"Total markets fetched: {len(df)}")
    
    strategies = analyze_strategies(df)
    
    # Save detailed analysis
    with open('kalshi_strategy_analysis.json', 'w') as f:
        analysis = {
            'summary': {
                'total_markets': len(df),
                'active_markets': len(df[df['status'] == 'active']),
                'inactive_markets': len(df[df['status'] != 'active'])
            },
            'strategies': {
                'buy_the_dip': len(strategies['dip_opportunities']),
                'near_certainty': len(strategies['near_certainty']),
                'longshots': len(strategies['longshots']),
                'mean_reversion': len(strategies['mean_reversion']),
                'high_volume': len(strategies['high_volume']),
                'low_volume': len(strategies['low_volume'])
            }
        }
        json.dump(analysis, f, indent=2)
    
    print(f"\nAnalysis saved to kalshi_strategy_analysis.json")

if __name__ == "__main__":
    main()