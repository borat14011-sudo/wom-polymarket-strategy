import json
import requests
from datetime import datetime, timezone
import math

def fetch_markets():
    """Fetch active markets from Polymarket API"""
    url = "https://gamma-api.polymarket.com/markets?limit=100&closed=false"
    response = requests.get(url)
    return response.json()

def calculate_days_until_resolution(end_date_str):
    """Calculate days until resolution"""
    if not end_date_str:
        return None
    
    try:
        # Parse the date string (format: "2025-12-31T12:00:00Z")
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        
        # Calculate difference in days
        delta = end_date - now
        return max(0, delta.days)
    except Exception as e:
        print(f"Error parsing date {end_date_str}: {e}")
        return None

def calculate_expected_value(yes_price, no_price, days_until_resolution, true_probability=0.5):
    """
    Calculate expected value after 4% transaction costs + 1% slippage
    Assuming we're buying YES shares
    """
    # Use mid-price for calculation
    mid_price = yes_price
    
    # Apply 1% slippage (worst-case execution)
    execution_price = mid_price * 1.01 if mid_price < 0.5 else mid_price * 0.99
    
    # Calculate payout if correct (1 - execution_price after costs)
    # Entry cost: 2% fee, Exit cost: 2% fee
    gross_payout = 1 - execution_price
    net_payout = gross_payout * 0.98 * 0.98  # Apply both entry and exit fees
    
    # Calculate expected value
    expected_value = (true_probability * net_payout) - ((1 - true_probability) * execution_price * 1.02)
    
    # Annualize if we have days until resolution
    if days_until_resolution and days_until_resolution > 0:
        annualized = ((1 + expected_value) ** (365 / days_until_resolution)) - 1
    else:
        annualized = None
    
    return {
        'expected_value': expected_value * 100,  # as percentage
        'annualized': annualized * 100 if annualized else None,
        'execution_price': execution_price,
        'net_payout': net_payout
    }

def analyze_markets(markets):
    """Analyze markets for opportunities"""
    opportunities = []
    
    for market in markets:
        try:
            # Extract basic info
            question = market.get('question', '')
            
            # Parse outcomePrices which is a string like "["0.0545", "0.9455"]"
            outcome_prices_str = market.get('outcomePrices', '["0", "0"]')
            try:
                # Remove brackets and quotes, then split
                outcome_prices = outcome_prices_str.strip('[]"').replace('"', '').split(',')
                yes_price = float(outcome_prices[0].strip())
                no_price = float(outcome_prices[1].strip())
            except:
                # Fallback to bestBid/bestAsk if available
                yes_price = market.get('bestBid', 0.5)
                no_price = 1 - yes_price
            volume_24hr = market.get('volume24hr', 0)
            liquidity = market.get('liquidityNum', 0)
            end_date = market.get('endDate')
            
            # Calculate days until resolution
            days_until_resolution = calculate_days_until_resolution(end_date)
            
            # Skip if no end date
            if days_until_resolution is None:
                continue
            
            # Filter criteria
            # 1. Price between 8% and 92%
            if not (0.08 <= yes_price <= 0.92):
                continue
                
            # 2. Volume > $1000/day
            if volume_24hr < 1000:
                continue
            
            # Calculate expected value (assuming true probability = market price for now)
            # In reality, we'd need to estimate true probability based on research
            ev_data = calculate_expected_value(yes_price, no_price, days_until_resolution, yes_price)
            
            # 3. Expected value > 3% after costs
            if ev_data['expected_value'] <= 3:
                continue
            
            # 4. Clear resolution criteria (check description)
            description = market.get('description', '')
            resolution_source = market.get('resolutionSource', '')
            has_clear_criteria = bool(resolution_source) or 'resolve' in description.lower() or 'source' in description.lower()
            
            if not has_clear_criteria:
                continue
            
            # Calculate position size using Kelly Criterion
            # Simplified: edge / odds
            edge = ev_data['expected_value'] / 100
            odds = (1 / yes_price) - 1
            kelly_fraction = edge / odds if odds > 0 else 0
            
            # Cap at 25% of capital (from memory)
            position_size_pct = min(kelly_fraction * 100, 25)
            
            opportunities.append({
                'question': question,
                'yes_price': yes_price * 100,
                'no_price': no_price * 100,
                'volume_24hr': volume_24hr,
                'liquidity': liquidity,
                'days_until_resolution': days_until_resolution,
                'expected_value': ev_data['expected_value'],
                'annualized_return': ev_data['annualized'],
                'position_size_pct': position_size_pct,
                'market_id': market.get('id'),
                'slug': market.get('slug')
            })
            
        except Exception as e:
            print(f"Error analyzing market {market.get('id')}: {e}")
            continue
    
    # Sort by expected value (descending)
    opportunities.sort(key=lambda x: x['expected_value'], reverse=True)
    
    return opportunities[:10]  # Top 10

def main():
    print("Fetching Polymarket data...")
    markets = fetch_markets()
    
    print(f"Found {len(markets)} active markets")
    
    opportunities = analyze_markets(markets)
    
    print(f"\nFound {len(opportunities)} opportunities meeting criteria")
    
    # Generate report
    report = "# Polymarket Opportunity Scan Report\n"
    report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    report += f"Markets analyzed: {len(markets)}\n"
    report += f"Opportunities found: {len(opportunities)}\n\n"
    
    if opportunities:
        report += "## Top 10 Opportunities (Ranked by Expected Value)\n\n"
        
        for i, opp in enumerate(opportunities, 1):
            report += f"### {i}. {opp['question']}\n"
            report += f"- **Market ID:** {opp['market_id']}\n"
            report += f"- **YES Price:** {opp['yes_price']:.1f}% | NO Price: {opp['no_price']:.1f}%\n"
            report += f"- **24h Volume:** ${opp['volume_24hr']:,.0f}\n"
            report += f"- **Liquidity:** ${opp['liquidity']:,.0f}\n"
            report += f"- **Days to Resolution:** {opp['days_until_resolution']}\n"
            report += f"- **Expected Value (after costs):** {opp['expected_value']:.1f}%\n"
            if opp['annualized_return']:
                report += f"- **Annualized Return:** {opp['annualized_return']:.1f}%\n"
            report += f"- **Recommended Position Size:** {opp['position_size_pct']:.1f}% of capital\n"
            report += f"- **Market URL:** https://polymarket.com/event/{opp['slug']}\n\n"
    else:
        report += "## No opportunities found meeting all criteria\n"
        report += "Consider relaxing filters or checking different markets.\n"
    
    # Save report
    with open('current_opportunities_scan.md', 'w') as f:
        f.write(report)
    
    print(f"\nReport saved to current_opportunities_scan.md")
    
    # Also print summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    if opportunities:
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. {opp['question'][:60]}...")
            print(f"   YES: {opp['yes_price']:.1f}% | EV: {opp['expected_value']:.1f}% | Size: {opp['position_size_pct']:.1f}%")
    else:
        print("No opportunities found")

if __name__ == "__main__":
    main()