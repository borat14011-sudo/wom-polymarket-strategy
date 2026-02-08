#!/usr/bin/env python3
"""
CURRENT MARKETS EXTRACTOR - KIMI 2.5 STRATEGIC
Get truly current markets (2024-2025) from Polymarket
"""
import requests
import json
from datetime import datetime

def extract_current_markets():
    """Extract current markets with proper filtering"""
    print("KIMI 2.5: Extracting current markets...")
    print("=" * 50)
    
    try:
        # Get CLOB markets
        response = requests.get("https://clob.polymarket.com/markets?limit=1000", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            all_markets = data.get('data', [])
            
            print(f"Total markets available: {len(all_markets)}")
            
            # Filter for truly current markets
            current_markets = []
            current_year = datetime.now().year
            
            for market in all_markets:
                question = market.get('question', market.get('title', ''))
                if not question:
                    continue
                    
                text = question.lower()
                end_date = str(market.get('end_date_iso', ''))
                
                # Check if market is current (2024-2026)
                is_current = False
                
                # Check end date year
                if end_date and ('2024' in end_date or '2025' in end_date or '2026' in end_date):
                    is_current = True
                
                # Check for current events in question
                current_keywords = [
                    'trump 2024', 'biden 2024', 'election 2024', 'election 2025',
                    'musk', 'tesla', 'bitcoin 2024', 'bitcoin 2025', 'crypto 2024',
                    'super bowl 2025', 'super bowl lix', 'chiefs', 'eagles',
                    'patrick mahomes', 'jalen hurts', 'president 2024', 'president 2025'
                ]
                
                for keyword in current_keywords:
                    if keyword in text:
                        is_current = True
                        break
                
                # Check if market is active and not closed
                active = market.get('active', False)
                closed = market.get('closed', False)
                accepting_orders = market.get('accepting_orders', False)
                
                if is_current and active and not closed and accepting_orders:
                    current_markets.append(market)
            
            print(f"Active current markets: {len(current_markets)}")
            
            # Show detailed current markets
            print("\nACTIVE CURRENT MARKETS:")
            print("=" * 60)
            
            for i, market in enumerate(current_markets[:20]):
                question = market.get('question', market.get('title', 'No question'))
                end_date = market.get('end_date_iso', 'No date')
                active = market.get('active', False)
                accepting = market.get('accepting_orders', False)
                
                # Parse date
                try:
                    if end_date and end_date != 'No date':
                        parsed_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        days_until = (parsed_date - datetime.now(timezone.utc)).days
                        time_status = f"{days_until} days" if days_until > 0 else "EXPIRED"
                    else:
                        time_status = "No date"
                except:
                    time_status = "Invalid date"
                
                print(f"{i+1}. {question[:80]}...")
                print(f"   Ends: {end_date[:10]} ({time_status})")
                print(f"   Status: Active={active} | Accepting Orders={accepting}")
                
                if 'tokens' in market and market['tokens']:
                    print(f"   Tokens: {len(market['tokens'])}")
                    # Show token details
                    for token in market['tokens'][:2]:
                        token_id = token.get('token_id', 'No ID')
                        outcome = token.get('outcome', 'No outcome')
                        print(f"     - {outcome[:30]}... ({token_id[:20]}...)")
                
                print()
            
            # Save current markets
            with open('CURRENT_ACTIVE_MARKETS.json', 'w') as f:
                json.dump(current_markets, f, indent=2)
            
            print(f"SAVED: {len(current_markets)} active current markets")
            
            # Summary by category
            categories = {}
            for market in current_markets:
                text = market.get('question', market.get('title', '')).lower()
                if 'super bowl' in text or 'chiefs' in text or 'eagles' in text:
                    categories['super_bowl'] = categories.get('super_bowl', 0) + 1
                elif 'trump' in text or 'biden' in text or 'election' in text:
                    categories['politics_election'] = categories.get('politics_election', 0) + 1
                elif 'musk' in text or 'tesla' in text:
                    categories['musk_tesla'] = categories.get('musk_tesla', 0) + 1
                elif 'bitcoin' in text or 'crypto' in text:
                    categories['crypto'] = categories.get('crypto', 0) + 1
                else:
                    categories['other'] = categories.get('other', 0) + 1
            
            print("\nMARKET BREAKDOWN:")
            for cat, count in categories.items():
                print(f"  {cat.replace('_', ' ').title()}: {count}")
            
            return current_markets
            
        else:
            print(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"System Error: {e}")
        return []

if __name__ == "__main__":
    markets = extract_current_markets()
    
    if markets:
        print(f"\nSUCCESS: {len(markets)} ACTIVE CURRENT MARKETS FOUND!")
        print("✅ Live market data system is operational!")
        print("✅ Ready for real-time trading monitoring!")
        
        # Show next steps
        print(f"\nNEXT STEPS:")
        print(f"1. Monitor these {len(markets)} active markets")
        print(f"2. Extract live prices for trading signals")
        print(f"3. Set up automated position tracking")
        print(f"4. Deploy capital on validated strategies")
    else:
        print("No current markets found")
        
        # Debug: show what years we have
        try:
            response = requests.get("https://clob.polymarket.com/markets?limit=100", timeout=10)
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', [])
                
                years_found = set()
                for market in markets:
                    end_date = str(market.get('end_date_iso', ''))
                    if end_date:
                        for year in ['2023', '2024', '2025', '2026']:
                            if year in end_date:
                                years_found.add(year)
                                break
                
                print(f"Years found in database: {sorted(years_found)}")
        except Exception as e:
            print(f"Debug error: {e}")