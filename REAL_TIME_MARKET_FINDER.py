#!/usr/bin/env python3
"""
REAL-TIME MARKET FINDER - KIMI 2.5 EMERGENCY EDITION
Find actual current trading markets on Polymarket
"""
import requests
import json
from datetime import datetime

def find_real_time_markets():
    """Find actual current trading markets"""
    print("KIMI 2.5 EMERGENCY: Finding real-time markets...")
    print("=" * 60)
    
    try:
        # Get markets from multiple sources
        sources = [
            ("CLOB API", "https://clob.polymarket.com/markets?limit=1000"),
            ("Gamma API", "https://gamma-api.polymarket.com/markets"),
        ]
        
        all_current_markets = []
        
        for source_name, url in sources:
            print(f"Checking {source_name}...")
            
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if source_name == "CLOB API":
                        markets = data.get('data', [])
                    else:
                        markets = data if isinstance(data, list) else []
                    
                    print(f"  Markets found: {len(markets)}")
                    
                    # Find current/active markets
                    current_markets = []
                    
                    for market in markets:
                        # Check market status
                        active = market.get('active', False)
                        closed = market.get('closed', False)
                        accepting_orders = market.get('accepting_orders', False)
                        
                        # Check end date
                        end_date = str(market.get('end_date_iso', ''))
                        
                        # Consider current if: active, not closed, accepting orders, and recent end date
                        is_current = False
                        
                        if active and not closed and accepting_orders:
                            is_current = True
                        
                        # Also check if end date is in future
                        if end_date:
                            try:
                                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                                if end_dt > datetime.now(datetime.timezone.utc):
                                    is_current = True
                            except:
                                pass
                        
                        if is_current:
                            current_markets.append(market)
                    
                    print(f"  Current markets: {len(current_markets)}")
                    all_current_markets.extend(current_markets)
                    
                    # Show some examples
                    if current_markets:
                        print(f"  Sample current markets:")
                        for i, market in enumerate(current_markets[:3]):
                            question = market.get('question', market.get('title', 'No question'))
                            end_date = market.get('end_date_iso', 'No date')
                            print(f"    {i+1}. {question[:60]}...")
                            print(f"       Ends: {end_date[:10]}")
                    
                else:
                    print(f"  Error: {response.status_code}")
                    
            except Exception as e:
                print(f"  Error: {e}")
            
            print()
        
        # Remove duplicates and analyze
        unique_markets = []
        seen_questions = set()
        
        for market in all_current_markets:
            question = market.get('question', market.get('title', ''))
            if question and question not in seen_questions:
                seen_questions.add(question)
                unique_markets.append(market)
        
        print(f"UNIQUE CURRENT MARKETS: {len(unique_markets)}")
        print("=" * 60)
        
        if unique_markets:
            # Show detailed analysis
            for i, market in enumerate(unique_markets[:20]):
                question = market.get('question', market.get('title', 'No question'))
                end_date = market.get('end_date_iso', 'No date')
                active = market.get('active', False)
                accepting = market.get('accepting_orders', False)
                
                print(f"{i+1}. {question[:80]}...")
                print(f"   End: {end_date[:10]} | Active: {active} | Accepting: {accepting}")
                
                if 'tokens' in market and market['tokens']:
                    print(f"   Tokens: {len(market['tokens'])}")
                print()
            
            # Save results
            with open('REAL_CURRENT_MARKETS.json', 'w') as f:
                json.dump(unique_markets, f, indent=2)
            
            print(f"SAVED: {len(unique_markets)} current markets to REAL_CURRENT_MARKETS.json")
            
            # Category analysis
            categories = {}
            for market in unique_markets:
                text = market.get('question', market.get('title', '')).lower()
                
                if any(word in text for word in ['super bowl', 'chiefs', 'eagles', 'mahomes', 'hurts']):
                    categories['super_bowl'] = categories.get('super_bowl', 0) + 1
                elif any(word in text for word in ['trump', 'biden', 'election', 'president']):
                    categories['politics'] = categories.get('politics', 0) + 1
                elif any(word in text for word in ['musk', 'tesla']):
                    categories['musk'] = categories.get('musk', 0) + 1
                elif any(word in text for word in ['bitcoin', 'crypto']):
                    categories['crypto'] = categories.get('crypto', 0) + 1
                else:
                    categories['other'] = categories.get('other', 0) + 1
            
            print("\nMARKET CATEGORIES:")
            for cat, count in categories.items():
                print(f"  {cat.replace('_', ' ').title()}: {count}")
            
            return unique_markets
        else:
            print("No current markets found!")
            
            # Debug: Show what years/dates we actually have
            print("\nDEBUG: Analyzing available dates...")
            
            all_dates = []
            for source_name, url in sources:
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        markets = data.get('data', []) if source_name == "CLOB API" else (data if isinstance(data, list) else [])
                        
                        for market in markets[:50]:  # Sample first 50
                            end_date = market.get('end_date_iso', '')
                            if end_date:
                                all_dates.append(end_date[:10])
                except:
                    continue
            
            if all_dates:
                print(f"Sample end dates found: {sorted(all_dates)[:10]}")
                years = [date[:4] for date in all_dates if len(date) >= 4]
                year_counts = {}
                for year in years:
                    year_counts[year] = year_counts.get(year, 0) + 1
                print(f"Years distribution: {year_counts}")
            
            return []
            
    except Exception as e:
        print(f"Critical system error: {e}")
        return []

if __name__ == "__main__":
    markets = find_real_time_markets()
    
    if markets:
        print(f"\nSUCCESS: {len(markets)} REAL CURRENT MARKETS FOUND!")
        print("✅ Live market data extraction successful!")
        print("✅ Ready for Wom's trading system integration!")
        
        # Show trading readiness
        tradeable = [m for m in markets if m.get('accepting_orders', False) and m.get('active', False)]
        print(f"\nTRADING READY: {len(tradeable)} markets accepting orders")
        
        # Next steps
        print(f"\nIMMEDIATE NEXT STEPS:")
        print(f"1. Get live prices for {len(markets)} markets")
        print(f"2. Set up price monitoring system")
        print(f"3. Deploy automated trading signals")
        print(f"4. Execute on validated strategies")
        
    else:
        print("No real-time markets found - investigating API structure...")
        
        # Final investigation
        print("\nINVESTIGATING API STRUCTURE...")
        try:
            response = requests.get("https://clob.polymarket.com/markets?limit=5", timeout=10)
            if response.status_code == 200:
                data = response.json()
                markets = data.get('data', [])
                
                print("Sample market structure:")
                if markets:
                    market = markets[0]
                    print(f"Available keys: {list(market.keys())}")
                    
                    # Show sample data
                    for key, value in market.items():
                        if isinstance(value, (str, int, float, bool)):
                            print(f"  {key}: {value}")
                        elif isinstance(value, list) and len(value) > 0:
                            print(f"  {key}: [list with {len(value)} items]")
                        elif isinstance(value, dict):
                            print(f"  {key}: {dict} with keys: {list(value.keys())}")
        except Exception as e:
            print(f"Investigation error: {e}")