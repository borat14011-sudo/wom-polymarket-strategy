import requests
import json
import pandas as pd
from datetime import datetime

api_key = '14a525cf-42d7-4746-8e36-30a8d9c17c96'
headers = {
    'Authorization': f'Bearer {api_key}',
    'Accept': 'application/json'
}

def fetch_kalshi_markets():
    """Fetch Kalshi markets and filter for prediction markets (not sports)"""
    print("Fetching Kalshi markets...")
    
    all_markets = []
    response = requests.get('https://api.elections.kalshi.com/v1/events', headers=headers, params={'limit': 100})
    data = response.json()
    
    for event in data.get('events', []):
        category = event.get('category', '')
        
        # Skip sports markets
        if category == 'Sports':
            continue
            
        for market in event.get('markets', []):
            if market.get('status') == 'active':
                market_data = {
                    'event_category': category,
                    'market_ticker': market.get('ticker_name'),
                    'market_title': market.get('title'),
                    'yes_bid': market.get('yes_bid'),
                    'yes_ask': market.get('yes_ask'),
                    'last_price': market.get('last_price'),
                    'previous_week_price': market.get('previous_week_price'),
                    'volume': market.get('volume'),
                    'dollar_volume': market.get('dollar_volume'),
                    'close_date': market.get('close_date'),
                    'can_close_early': market.get('can_close_early')
                }
                all_markets.append(market_data)
    
    return pd.DataFrame(all_markets)

def calculate_expected_value(row, strategy):
    """Calculate expected value based on strategy"""
    mid_price = (row['yes_bid'] + row['yes_ask']) / 2
    
    if strategy == 'buy_the_dip':
        if pd.isna(row['previous_week_price']) or row['previous_week_price'] == 0:
            return None
            
        drop_pct = (mid_price - row['previous_week_price']) / row['previous_week_price'] * 100
        
        # Only consider drops > 10%
        if drop_pct > -10:
            return None
            
        # Expected value calculation for Buy the Dip
        # Assumption: 50% mean reversion of the drop
        expected_reversion = abs(drop_pct) * 0.5
        
        # Kalshi fee adjustment based on price
        if mid_price < 26 or mid_price > 74:
            fee = 2.0  # Kalshi advantage zone
        else:
            fee = 4.0  # Polymarket would be better, but using Kalshi
        
        ev = expected_reversion - fee
        
        return {
            'strategy': 'Buy the Dip',
            'market': row['market_title'],
            'ticker': row['market_ticker'],
            'price': mid_price,
            'previous_price': row['previous_week_price'],
            'drop_pct': drop_pct,
            'volume': row['dollar_volume'],
            'category': row['event_category'],
            'expected_value': ev,
            'reasoning': f"Price dropped {abs(drop_pct):.1f}% from {row['previous_week_price']}¢. Expected 50% mean reversion ({expected_reversion:.1f}%) minus {fee}% fees."
        }
    
    elif strategy == 'near_certainty':
        # Look for high probability markets (70-90¢) that might be underpriced
        if mid_price < 70 or mid_price > 90:
            return None
            
        # Assume true probability is 5-10% higher than market price
        assumed_true_prob = min(95, mid_price + 10)
        
        # Expected value calculation
        win_prob = assumed_true_prob / 100
        lose_prob = 1 - win_prob
        potential_gain = 100 - mid_price
        potential_loss = mid_price
        
        expected_gain = (win_prob * potential_gain) - (lose_prob * potential_loss)
        
        # Fee adjustment
        if mid_price > 74:
            fee = 1.5  # Kalshi advantage for high prices
        else:
            fee = 4.0
            
        ev = expected_gain - fee
        
        return {
            'strategy': 'Near Certainty',
            'market': row['market_title'],
            'ticker': row['market_ticker'],
            'price': mid_price,
            'volume': row['dollar_volume'],
            'category': row['event_category'],
            'expected_value': ev,
            'reasoning': f"Market at {mid_price}¢ but true probability estimated at {assumed_true_prob}%. Expected gain: {expected_gain:.1f}% minus {fee}% fees."
        }
    
    elif strategy == 'hype_fade':
        # Look for markets that spiked recently (from previous research)
        if pd.isna(row['previous_week_price']) or row['previous_week_price'] == 0:
            return None
            
        spike_pct = (mid_price - row['previous_week_price']) / row['previous_week_price'] * 100
        
        # Look for spikes > 100%
        if spike_pct < 100:
            return None
            
        # Expected fade of 50% of the spike
        expected_fade = spike_pct * 0.5
        
        # For hype fade, we would bet NO (sell YES)
        # Simplified EV: expected fade minus fees
        fee = 2.0 if (mid_price < 26 or mid_price > 74) else 4.0
        ev = expected_fade - fee
        
        return {
            'strategy': 'Hype Fade',
            'market': row['market_title'],
            'ticker': row['market_ticker'],
            'price': mid_price,
            'previous_price': row['previous_week_price'],
            'spike_pct': spike_pct,
            'volume': row['dollar_volume'],
            'category': row['event_category'],
            'expected_value': ev,
            'reasoning': f"Price spiked {spike_pct:.1f}% from {row['previous_week_price']}¢. Expected 50% fade ({expected_fade:.1f}%) minus {fee}% fees. Bet NO."
        }
    
    return None

def main():
    print("FINDING TOP 10 KALSHI PREDICTION MARKET BETS")
    print("="*80)
    
    # Fetch markets
    df = fetch_kalshi_markets()
    print(f"Found {len(df)} active prediction markets (excluding sports)")
    
    # Calculate EV for all strategies
    all_opportunities = []
    
    for idx, row in df.iterrows():
        # Try each strategy
        for strategy in ['buy_the_dip', 'near_certainty', 'hype_fade']:
            opportunity = calculate_expected_value(row, strategy)
            if opportunity and opportunity['expected_value'] > 5:  # Minimum 5% EV
                all_opportunities.append(opportunity)
    
    # Sort by expected value
    all_opportunities.sort(key=lambda x: x['expected_value'], reverse=True)
    
    # Take top 10
    top_10 = all_opportunities[:10]
    
    print(f"\nTOP 10 KALSHI PREDICTION MARKET BETS")
    print("="*80)
    
    for i, trade in enumerate(top_10):
        print(f"\n{i+1}. {trade['strategy']}: {trade['market'][:70]}...")
        print(f"   Ticker: {trade['ticker']}")
        print(f"   Category: {trade['category']}")
        print(f"   Current Price: {trade['price']:.1f}¢")
        print(f"   Volume: ${trade['volume']}")
        
        if 'drop_pct' in trade:
            print(f"   Drop: {trade['drop_pct']:.1f}% (from {trade['previous_price']}¢)")
        elif 'spike_pct' in trade:
            print(f"   Spike: {trade['spike_pct']:.1f}% (from {trade['previous_price']}¢)")
            
        print(f"   Expected Value: {trade['expected_value']:.1f}%")
        print(f"   Reasoning: {trade['reasoning']}")
    
    # Save results
    with open('top_10_kalshi_bets.json', 'w') as f:
        json.dump(top_10, f, indent=2)
    
    print(f"\nResults saved to top_10_kalshi_bets.json")
    
    # Generate summary table
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    print("\nRanked by Expected Value:")
    print(f"{'Rank':<5} {'Strategy':<15} {'EV':<8} {'Price':<8} {'Category':<20}")
    print("-" * 60)
    
    for i, trade in enumerate(top_10):
        print(f"{i+1:<5} {trade['strategy']:<15} {trade['expected_value']:<8.1f} {trade['price']:<8.1f} {trade['category']:<20}")
    
    # Risk parameters
    print("\nRISK PARAMETERS:")
    print("1. Position Sizing: 0.5-2% of bankroll per trade (1/3 Kelly)")
    print("2. Stop Loss: -25% from entry price")
    print("3. Max Portfolio Exposure: 15% in Kalshi markets")
    print("4. Platform Selection: Use Kalshi for prices <26¢ or >74¢, else Polymarket")
    print("5. Time Filter: Avoid 7-30 day markets (most efficient)")
    
    # Execution plan
    print("\nEXECUTION PLAN:")
    print("1. Start with 2 highest EV trades")
    print("2. Monitor for 24 hours before adding more positions")
    print("3. Scale in over 2-3 days for high conviction trades")
    print("4. Take profit at 50% of expected move")
    print("5. Review weekly performance")

if __name__ == "__main__":
    main()