#!/usr/bin/env python3
"""
QUICK LIVE MARKETS 2025 - KIMI 2.5 STRATEGIC EDITION
Get current 2025 markets for Wom's trading system
"""
import requests
import json

def get_current_2025_markets():
    """Get current 2025 markets quickly"""
    print("KIMI 2.5: Getting current 2025 markets...")
    print("=" * 50)
    
    # Use CLOB API - proven to work with 1000 markets
    try:
        response = requests.get("https://clob.polymarket.com/markets?limit=1000", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            all_markets = data.get('data', [])
            
            print(f"Total markets in database: {len(all_markets)}")
            
            # Filter for 2025 and current events
            current_2025 = []
            keywords = ['2025', '2026', 'trump', 'biden', 'election', 'musk', 'tesla', 
                       'bitcoin', 'crypto', 'super bowl', 'chiefs', 'eagles', 'president']
            
            for market in all_markets:
                text = market.get('question', market.get('title', '')).lower()
                end_date = str(market.get('end_date_iso', '')).lower()
                
                # Check for 2025 or current keywords
                if '2025' in text or '2025' in end_date:
                    current_2025.append(market)
                else:
                    for keyword in keywords:
                        if keyword in text:
                            current_2025.append(market)
                            break
            
            print(f"Current 2025 markets found: {len(current_2025)}")
            print()
            
            # Show top current markets
            print("TOP CURRENT 2025 MARKETS:")
            print("-" * 40)
            
            for i, market in enumerate(current_2025[:15]):
                question = market.get('question', market.get('title', 'No question'))
                end_date = market.get('end_date_iso', 'No date')
                active = market.get('active', False)
                closed = market.get('closed', False)
                
                print(f"{i+1}. {question[:70]}...")
                print(f"   End: {end_date[:10]} | Active: {active} | Closed: {closed}")
                
                if 'tokens' in market and market['tokens']:
                    print(f"   Tokens: {len(market['tokens'])}")
                print()
            
            # Save results
            with open('LIVE_2025_MARKETS.json', 'w') as f:
                json.dump(current_2025, f, indent=2)
            
            print(f"SAVED: {len(current_2025)} current markets to LIVE_2025_MARKETS.json")
            
            # Show market categories
            categories = {}
            for market in current_2025:
                text = market.get('question', market.get('title', '')).lower()
                if 'super bowl' in text:
                    categories['super_bowl'] = categories.get('super_bowl', 0) + 1
                elif 'trump' in text or 'biden' in text:
                    categories['politics'] = categories.get('politics', 0) + 1
                elif 'musk' in text or 'tesla' in text:
                    categories['musk'] = categories.get('musk', 0) + 1
                elif 'bitcoin' in text or 'crypto' in text:
                    categories['crypto'] = categories.get('crypto', 0) + 1
                elif 'election' in text:
                    categories['election'] = categories.get('election', 0) + 1
            
            print("\nMARKET CATEGORIES:")
            for cat, count in categories.items():
                print(f"  {cat}: {count}")
            
            return current_2025
            
        else:
            print(f"API Error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"System Error: {e}")
        return []

def get_market_details(market_id):
    """Get detailed info for specific market"""
    try:
        # Try to get more details
        urls = [
            f"https://clob.polymarket.com/markets/{market_id}",
            f"https://gamma-api.polymarket.com/markets/{market_id}"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        
        return None
        
    except Exception as e:
        print(f"Detail error: {e}")
        return None

if __name__ == "__main__":
    markets = get_current_2025_markets()
    
    if markets:
        print(f"\nSUCCESS: Found {len(markets)} current 2025 markets!")
        print("System ready for live trading data!")
    else:
        print("No current markets found - checking API status...")
        
        # Quick API check
        try:
            response = requests.get("https://clob.polymarket.com/markets?limit=10", timeout=10)
            print(f"API Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Sample markets: {len(data.get('data', []))}")
        except Exception as e:
            print(f"API Check Error: {e}")