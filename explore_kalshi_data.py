import requests
import json
import pandas as pd
from datetime import datetime

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

def fetch_all_events():
    """Fetch all events from Kalshi API"""
    all_events = []
    cursor = None
    
    while True:
        params = {'limit': 100}
        if cursor:
            params['cursor'] = cursor
            
        response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params=params)
        
        if response.status_code != 200:
            print(f"Error fetching events: {response.status_code}")
            break
            
        data = response.json()
        events = data.get('events', [])
        all_events.extend(events)
        
        # Check for pagination
        if 'next_cursor' in data and data['next_cursor']:
            cursor = data['next_cursor']
        else:
            break
            
    return all_events

def analyze_events(events):
    """Analyze events for trading opportunities"""
    print(f"Total events: {len(events)}")
    
    # Convert to DataFrame for analysis
    df_data = []
    for event in events:
        for market in event.get('markets', []):
            df_data.append({
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
            })
    
    df = pd.DataFrame(df_data)
    
    print(f"\nTotal markets: {len(df)}")
    print(f"\nMarket status distribution:")
    print(df['status'].value_counts())
    
    print(f"\nCategory distribution:")
    print(df['event_category'].value_counts().head(10))
    
    # Filter for active markets
    active_df = df[df['status'] == 'active']
    print(f"\nActive markets: {len(active_df)}")
    
    # Analyze price ranges
    print(f"\nPrice distribution of active markets:")
    print(f"Min YES price: {active_df['yes_price'].min()}")
    print(f"Max YES price: {active_df['yes_price'].max()}")
    print(f"Mean YES price: {active_df['yes_price'].mean():.2f}")
    print(f"Median YES price: {active_df['yes_price'].median():.2f}")
    
    # Find dip opportunities (>10% drop)
    active_df['prev_week_change'] = (active_df['yes_price'] - active_df['previous_week_price']) / active_df['previous_week_price'] * 100
    dip_opportunities = active_df[active_df['prev_week_change'] < -10]
    print(f"\nDip opportunities (>10% drop from week high): {len(dip_opportunities)}")
    
    if len(dip_opportunities) > 0:
        print("\nTop 10 dip opportunities:")
        for idx, row in dip_opportunities.head(10).iterrows():
            print(f"  {row['market_title'][:50]}... - Price: {row['yes_price']}¢ (was {row['previous_week_price']}¢, drop: {row['prev_week_change']:.1f}%)")
    
    return df, active_df, dip_opportunities

def main():
    print("Fetching Kalshi data...")
    events = fetch_all_events()
    
    if events:
        df, active_df, dip_opportunities = analyze_events(events)
        
        # Save data for further analysis
        df.to_csv('kalshi_all_markets.csv', index=False)
        active_df.to_csv('kalshi_active_markets.csv', index=False)
        dip_opportunities.to_csv('kalshi_dip_opportunities.csv', index=False)
        
        print(f"\nData saved to CSV files:")
        print(f"  - kalshi_all_markets.csv ({len(df)} markets)")
        print(f"  - kalshi_active_markets.csv ({len(active_df)} markets)")
        print(f"  - kalshi_dip_opportunities.csv ({len(dip_opportunities)} markets)")
    else:
        print("No events fetched")

if __name__ == "__main__":
    main()