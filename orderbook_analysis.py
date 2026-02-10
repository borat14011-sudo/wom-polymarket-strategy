import json
import urllib.request
import urllib.error
from datetime import datetime
import time

# Fetch markets from Gamma API
def fetch_markets():
    url = "https://gamma-api.polymarket.com/markets?active=true&closed=false&archived=false&limit=200"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://polymarket.com',
        'Referer': 'https://polymarket.com/'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return []

# Fetch order book from CLOB API
def fetch_orderbook(token_id):
    url = f"https://clob.polymarket.com/book?token_id={token_id}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Origin': 'https://polymarket.com',
        'Referer': 'https://polymarket.com/'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": "No orderbook exists"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}

# Calculate spread percentage
def calculate_spread_pct(best_bid, best_ask):
    if best_bid and best_ask and best_bid > 0:
        return ((best_ask - best_bid) / ((best_bid + best_ask) / 2)) * 100
    return None

# Calculate depth from order book
def calculate_depth(orderbook, token_price):
    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])
    
    bid_depth = sum(float(bid.get("size", 0)) for bid in bids[:10])
    ask_depth = sum(float(ask.get("size", 0)) for ask in asks[:10])
    
    # Calculate depth in USD (assuming size is in USDC)
    total_depth_usd = bid_depth + ask_depth
    
    return {
        "bid_depth": round(bid_depth, 2),
        "ask_depth": round(ask_depth, 2),
        "total_depth_usd": round(total_depth_usd, 2)
    }

# Calculate volatility proxy from price changes
def calculate_volatility_proxy(market):
    # Use various time horizon price changes as volatility proxy
    changes = []
    for key in ["oneHourPriceChange", "oneDayPriceChange", "oneWeekPriceChange"]:
        val = market.get(key)
        if val is not None:
            changes.append(abs(float(val)))
    
    if changes:
        return round(sum(changes) / len(changes), 4)
    return 0

def main():
    print("Fetching markets...")
    markets = fetch_markets()
    
    if not markets:
        print("Failed to fetch markets")
        return
    
    # Sort by volume (descending) and get top 20
    markets_sorted = sorted(markets, key=lambda x: float(x.get("volumeNum", 0)), reverse=True)
    top_20 = markets_sorted[:20]
    
    print(f"Found {len(top_20)} top markets by volume")
    
    analysis_results = []
    
    for idx, market in enumerate(top_20):
        print(f"\n[{idx+1}/20] Processing: {market.get('question', 'Unknown')[:50]}...")
        
        # Parse token IDs
        try:
            token_ids = json.loads(market.get("clobTokenIds", "[]"))
        except:
            token_ids = []
        
        if not token_ids:
            print("  No token IDs found")
            continue
        
        # Get market data
        volume = float(market.get("volumeNum", 0))
        liquidity = float(market.get("liquidityNum", 0))
        best_bid = market.get("bestBid")
        best_ask = market.get("bestAsk")
        spread = market.get("spread")
        
        # Calculate spread percentage
        spread_pct = None
        if best_bid and best_ask:
            spread_pct = calculate_spread_pct(float(best_bid), float(best_ask))
        
        # Calculate volatility proxy
        volatility = calculate_volatility_proxy(market)
        
        # Fetch order books for both tokens (Yes/No outcomes)
        orderbooks = []
        total_depth = {"bid_depth": 0, "ask_depth": 0, "total_depth_usd": 0}
        
        for token_id in token_ids[:2]:  # Usually Yes and No tokens
            print(f"  Fetching orderbook for token {str(token_id)[:20]}...")
            ob = fetch_orderbook(str(token_id))
            orderbooks.append({
                "token_id": str(token_id),
                "orderbook": ob
            })
            
            if "error" not in ob:
                depth = calculate_depth(ob, 0.5)  # Assume midpoint price
                total_depth["bid_depth"] += depth["bid_depth"]
                total_depth["ask_depth"] += depth["ask_depth"]
                total_depth["total_depth_usd"] += depth["total_depth_usd"]
            
            time.sleep(0.2)  # Rate limiting
        
        # Prepare market analysis
        market_analysis = {
            "market_id": market.get("id"),
            "condition_id": market.get("conditionId"),
            "question": market.get("question"),
            "slug": market.get("slug"),
            "volume_usd": round(volume, 2),
            "liquidity_usd": round(liquidity, 2),
            "spread": spread,
            "spread_pct": round(spread_pct, 4) if spread_pct else None,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "bid_depth": total_depth["bid_depth"],
            "ask_depth": total_depth["ask_depth"],
            "total_depth_usd": total_depth["total_depth_usd"],
            "volatility_proxy": volatility,
            "one_day_price_change": market.get("oneDayPriceChange"),
            "one_week_price_change": market.get("oneWeekPriceChange"),
            "outcome_prices": market.get("outcomePrices"),
            "token_ids": token_ids,
            "orderbooks_fetched": len([ob for ob in orderbooks if "error" not in ob.get("orderbook", {})]),
            "timestamp": datetime.now().isoformat()
        }
        
        analysis_results.append(market_analysis)
        spread_str = f"{spread_pct:.2f}%" if spread_pct else "N/A"
        print(f"  [OK] Volume: ${volume:,.0f}, Spread: {spread_str}, Depth: ${total_depth['total_depth_usd']:,.0f}")
    
    # Calculate summary stats
    valid_spreads = [m["spread_pct"] for m in analysis_results if m["spread_pct"] is not None]
    valid_depths = [m["total_depth_usd"] for m in analysis_results if m["total_depth_usd"] > 0]
    
    # Identify most liquid (by volume)
    most_liquid = sorted(analysis_results, key=lambda x: x["volume_usd"], reverse=True)[:5]
    
    # Identify widest spreads (arbitrage opportunity)
    widest_spreads = sorted([m for m in analysis_results if m["spread_pct"] is not None], 
                           key=lambda x: x["spread_pct"], reverse=True)[:5]
    
    summary = {
        "most_liquid_markets": [
            {"market_id": m["market_id"], "question": m["question"][:80], "volume_usd": m["volume_usd"]} 
            for m in most_liquid
        ],
        "widest_spreads_arbitrage_opportunity": [
            {"market_id": m["market_id"], "question": m["question"][:80], "spread_pct": m["spread_pct"], "volume_usd": m["volume_usd"]} 
            for m in widest_spreads
        ],
        "average_spread_pct": round(sum(valid_spreads) / len(valid_spreads), 4) if valid_spreads else None,
        "average_depth_usd": round(sum(valid_depths) / len(valid_depths), 2) if valid_depths else 0,
        "total_volume_analyzed": round(sum(m["volume_usd"] for m in analysis_results), 2),
        "markets_analyzed": len(analysis_results),
        "timestamp": datetime.now().isoformat()
    }
    
    # Save results
    final_output = {
        "summary": summary,
        "market_analysis": analysis_results
    }
    
    with open("orderbook_analysis.json", "w") as f:
        json.dump(final_output, f, indent=2)
    
    print(f"\n{'='*60}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"Markets analyzed: {len(analysis_results)}")
    print(f"Total volume: ${summary['total_volume_analyzed']:,.2f}")
    print(f"Average spread: {summary['average_spread_pct']:.2f}%" if summary['average_spread_pct'] else "Average spread: N/A")
    print(f"Average depth: ${summary['average_depth_usd']:,.2f}")
    print(f"\nMost liquid market: {most_liquid[0]['question'][:60] if most_liquid else 'N/A'}...")
    if widest_spreads:
        print(f"Widest spread: {widest_spreads[0]['question'][:60]}... ({widest_spreads[0]['spread_pct']:.2f}%)")
    else:
        print("Widest spread: N/A")
    print(f"\nResults saved to orderbook_analysis.json")

if __name__ == "__main__":
    main()
