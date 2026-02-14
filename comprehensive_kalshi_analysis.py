import requests
import json
import pandas as pd
from datetime import datetime

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

def fetch_all_markets():
    """Fetch all markets from Kalshi API"""
    print("Fetching Kalshi markets...")
    
    all_markets = []
    cursor = None
    page = 1
    
    while True:
        params = {'limit': 100}
        if cursor:
            params['cursor'] = cursor
            
        response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break
            
        data = response.json()
        events = data.get('events', [])
        
        for event in events:
            for market in event.get('markets', []):
                market_data = {
                    'event_ticker': event.get('ticker'),
                    'event_title': event.get('title'),
                    'event_category': event.get('category'),
                    'market_id': market.get('id'),
                    'market_ticker': market.get('ticker_name'),
                    'market_title': market.get('title'),
                    'yes_bid': market.get('yes_bid'),  # in cents
                    'yes_ask': market.get('yes_ask'),  # in cents
                    'last_price': market.get('last_price'),  # in cents
                    'previous_day_price': market.get('previous_day_price'),  # in cents
                    'previous_week_price': market.get('previous_week_price'),  # in cents
                    'volume': market.get('volume'),
                    'dollar_volume': market.get('dollar_volume'),
                    'status': market.get('status'),
                    'close_date': market.get('close_date'),
                    'expiration_date': market.get('expiration_date'),
                    'can_close_early': market.get('can_close_early'),
                    'rulebook_variables': json.dumps(market.get('rulebook_variables', {}))
                }
                all_markets.append(market_data)
        
        print(f"Page {page}: Fetched {len(events)} events, total markets: {len(all_markets)}")
        
        # Check for pagination
        if 'next_cursor' in data and data['next_cursor']:
            cursor = data['next_cursor']
            page += 1
        else:
            break
    
    return pd.DataFrame(all_markets)

def analyze_trading_strategies(df):
    """Analyze various trading strategies"""
    
    # Filter active markets
    active_df = df[df['status'] == 'active'].copy()
    print(f"\nActive markets: {len(active_df)}")
    
    # Calculate mid price (average of bid and ask)
    active_df['mid_price'] = (active_df['yes_bid'] + active_df['yes_ask']) / 2
    
    results = {}
    
    # Strategy 1: Buy the Dip
    active_df['week_drop_pct'] = (active_df['mid_price'] - active_df['previous_week_price']) / active_df['previous_week_price'] * 100
    dip_opportunities = active_df[active_df['week_drop_pct'] < -10].sort_values('week_drop_pct')
    results['buy_the_dip'] = dip_opportunities
    
    print(f"\n1. BUY THE DIP Strategy")
    print(f"   Opportunities (>10% drop): {len(dip_opportunities)}")
    if len(dip_opportunities) > 0:
        print("   Top 5 opportunities:")
        for idx, row in dip_opportunities.head().iterrows():
            print(f"     - {row['market_title'][:50]}...")
            print(f"       Price: {row['mid_price']}¢ (was {row['previous_week_price']}¢, drop: {row['week_drop_pct']:.1f}%)")
            print(f"       Volume: ${row['dollar_volume']}, Category: {row['event_category']}")
    
    # Strategy 2: Near Certainty (high probability underpriced)
    high_prob = active_df[(active_df['mid_price'] > 70) & (active_df['mid_price'] < 90)]
    results['near_certainty'] = high_prob
    
    print(f"\n2. NEAR CERTAINTY Strategy")
    print(f"   Opportunities (70-90¢): {len(high_prob)}")
    if len(high_prob) > 0:
        print("   Top 5 opportunities:")
        for idx, row in high_prob.head().iterrows():
            print(f"     - {row['market_title'][:50]}...")
            print(f"       Price: {row['mid_price']}¢, Volume: ${row['dollar_volume']}")
    
    # Strategy 3: Longshot Fade (low probability overpriced)
    longshots = active_df[(active_df['mid_price'] < 30) & (active_df['mid_price'] > 5)]
    results['longshot_fade'] = longshots
    
    print(f"\n3. LONGSHOT FADE Strategy")
    print(f"   Opportunities (5-30¢): {len(longshots)}")
    
    # Strategy 4: Mean Reversion (prices near 50¢)
    mean_rev = active_df[(active_df['mid_price'] > 40) & (active_df['mid_price'] < 60)]
    results['mean_reversion'] = mean_rev
    
    print(f"\n4. MEAN REVERSION Strategy")
    print(f"   Opportunities (40-60¢): {len(mean_rev)}")
    
    # Strategy 5: High Volume Momentum
    high_vol = active_df[active_df['dollar_volume'] > 10000].sort_values('dollar_volume', ascending=False)
    results['high_volume'] = high_vol
    
    print(f"\n5. HIGH VOLUME MOMENTUM Strategy")
    print(f"   Opportunities (>$10k volume): {len(high_vol)}")
    
    # Strategy 6: Low Volume Inefficiency
    low_vol = active_df[(active_df['dollar_volume'] < 1000) & (active_df['dollar_volume'] > 0)]
    results['low_volume'] = low_vol
    
    print(f"\n6. LOW VOLUME INEFFICIENCY Strategy")
    print(f"   Opportunities (<$1k volume): {len(low_vol)}")
    
    # Strategy 7: Category Analysis
    print(f"\n7. CATEGORY ANALYSIS")
    category_stats = active_df.groupby('event_category').agg({
        'market_id': 'count',
        'mid_price': 'mean',
        'dollar_volume': 'sum'
    }).sort_values('market_id', ascending=False)
    
    for category, row in category_stats.head(10).iterrows():
        print(f"   {category}: {int(row['market_id'])} markets, avg price: {row['mid_price']:.1f}¢, volume: ${int(row['dollar_volume'])}")
    
    # Strategy 8: Spread Analysis (bid-ask spread as %)
    active_df['spread_pct'] = (active_df['yes_ask'] - active_df['yes_bid']) / active_df['mid_price'] * 100
    high_spread = active_df[active_df['spread_pct'] > 20].sort_values('spread_pct', ascending=False)
    results['high_spread'] = high_spread
    
    print(f"\n8. SPREAD ANALYSIS")
    print(f"   Avg spread: {active_df['spread_pct'].mean():.1f}%")
    print(f"   High spread opportunities (>20%): {len(high_spread)}")
    
    return results

def calculate_expected_value(strategy_results, df):
    """Calculate expected value for each strategy based on historical data"""
    
    # Note: This is a simplified calculation
    # In reality, we would need historical resolution data
    
    print("\n" + "="*80)
    print("EXPECTED VALUE CALCULATIONS (Simplified)")
    print("="*80)
    
    ev_calculations = {}
    
    # Buy the Dip EV
    if len(strategy_results['buy_the_dip']) > 0:
        avg_drop = strategy_results['buy_the_dip']['week_drop_pct'].mean()
        # Assuming mean reversion: price returns halfway to previous level
        expected_gain = abs(avg_drop) * 0.5  # 50% reversion
        kalshi_fee = 2.0  # % for extreme prices
        ev = expected_gain - kalshi_fee
        ev_calculations['buy_the_dip'] = ev
        print(f"\nBuy the Dip EV:")
        print(f"  Avg drop: {avg_drop:.1f}%")
        print(f"  Expected reversion: {expected_gain:.1f}% (50% of drop)")
        print(f"  Kalshi fee: {kalshi_fee:.1f}%")
        print(f"  Net EV: {ev:.1f}%")
    
    # Near Certainty EV
    if len(strategy_results['near_certainty']) > 0:
        avg_price = strategy_results['near_certainty']['mid_price'].mean()
        expected_prob = 95  # Assuming true probability is 95%
        expected_gain = (100 - avg_price) * (expected_prob/100) - (avg_price * ((100-expected_prob)/100))
        kalshi_fee = 1.5  # % for high prices
        ev = expected_gain - kalshi_fee
        ev_calculations['near_certainty'] = ev
        print(f"\nNear Certainty EV:")
        print(f"  Avg price: {avg_price:.1f}¢")
        print(f"  Assumed true probability: {expected_prob}%")
        print(f"  Expected gain: {expected_gain:.1f}%")
        print(f"  Kalshi fee: {kalshi_fee:.1f}%")
        print(f"  Net EV: {ev:.1f}%")
    
    return ev_calculations

def main():
    print("KALSHI TRADING STRATEGY ITERATION")
    print("="*80)
    
    # Fetch data
    df = fetch_all_markets()
    print(f"\nTotal markets fetched: {len(df)}")
    
    # Analyze strategies
    strategy_results = analyze_trading_strategies(df)
    
    # Calculate expected values
    ev_calculations = calculate_expected_value(strategy_results, df)
    
    # Save results
    with open('kalshi_strategy_iteration_results.json', 'w') as f:
        results = {
            'summary': {
                'total_markets': len(df),
                'active_markets': len(df[df['status'] == 'active']),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'strategy_counts': {
                'buy_the_dip': len(strategy_results['buy_the_dip']),
                'near_certainty': len(strategy_results['near_certainty']),
                'longshot_fade': len(strategy_results['longshot_fade']),
                'mean_reversion': len(strategy_results['mean_reversion']),
                'high_volume': len(strategy_results['high_volume']),
                'low_volume': len(strategy_results['low_volume']),
                'high_spread': len(strategy_results['high_spread'])
            },
            'expected_values': ev_calculations
        }
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to kalshi_strategy_iteration_results.json")
    
    # Generate top 10 trades
    print("\n" + "="*80)
    print("TOP 10 TRADES BY EXPECTED VALUE")
    print("="*80)
    
    top_trades = []
    
    # Combine opportunities from different strategies
    for idx, row in strategy_results['buy_the_dip'].head(20).iterrows():
        ev = abs(row['week_drop_pct']) * 0.5 - 2.0  # Simplified EV calculation
        top_trades.append({
            'strategy': 'Buy the Dip',
            'market': row['market_title'],
            'ticker': row['market_ticker'],
            'price': row['mid_price'],
            'previous_price': row['previous_week_price'],
            'drop_pct': row['week_drop_pct'],
            'volume': row['dollar_volume'],
            'category': row['event_category'],
            'ev': ev
        })
    
    for idx, row in strategy_results['near_certainty'].head(20).iterrows():
        ev = (100 - row['mid_price']) * 0.95 - (row['mid_price'] * 0.05) - 1.5
        top_trades.append({
            'strategy': 'Near Certainty',
            'market': row['market_title'],
            'ticker': row['market_ticker'],
            'price': row['mid_price'],
            'volume': row['dollar_volume'],
            'category': row['event_category'],
            'ev': ev
        })
    
    # Sort by EV and take top 10
    top_trades.sort(key=lambda x: x['ev'], reverse=True)
    
    for i, trade in enumerate(top_trades[:10]):
        print(f"\n{i+1}. {trade['strategy']}: {trade['market'][:60]}...")
        print(f"   Ticker: {trade['ticker']}")
        print(f"   Price: {trade['price']}¢, Volume: ${trade['volume']}")
        print(f"   Category: {trade['category']}")
        if 'drop_pct' in trade:
            print(f"   Drop: {trade['drop_pct']:.1f}% (from {trade['previous_price']}¢)")
        print(f"   Expected Value: {trade['ev']:.1f}%")
    
    # Save top trades
    with open('kalshi_top_10_trades.json', 'w') as f:
        json.dump(top_trades[:10], f, indent=2)
    
    print(f"\nTop 10 trades saved to kalshi_top_10_trades.json")

if __name__ == "__main__":
    main()