#!/usr/bin/env python3
"""
POLYMARKET LIVE BET FETCHER
Gets live bets, positions, and market data from Polymarket
"""

import requests
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# API Base URLs
GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"


class PolymarketLiveBets:
    """Fetch live bets and positions from Polymarket"""

    def __init__(self):
        self.session = requests.Session()
        print("[OK] Connected to Polymarket APIs")

    # ========== METHOD 1: Get All Active Markets (No Auth) ==========

    def get_active_markets(self, limit: int = 100, min_volume: float = 50000) -> List[Dict]:
        """
        Get all active markets with live prices
        Returns markets with current bid/ask prices, volume, liquidity
        """
        print(f"\n[+] Fetching {limit} active markets...")

        response = self.session.get(
            f"{GAMMA_API}/markets",
            params={
                "active": "true",
                "closed": "false",
                "limit": limit
            },
            timeout=30
        )
        response.raise_for_status()
        markets = response.json()

        # Filter by volume and add computed fields
        active_bets = []
        for market in markets:
            volume = float(market.get('volume', 0))
            if volume >= min_volume:
                best_bid = float(market.get('bestBid', 0))
                best_ask = float(market.get('bestAsk', 0))

                active_bets.append({
                    'question': market.get('question', 'Unknown'),
                    'slug': market.get('marketSlug', market.get('slug', '')),
                    'condition_id': market.get('conditionId', ''),
                    'volume': volume,
                    'liquidity': float(market.get('liquidity', 0)),
                    'best_bid': best_bid,
                    'best_ask': best_ask,
                    'spread': best_ask - best_bid if best_ask > 0 and best_bid > 0 else 1,
                    'end_date': market.get('endDate', 'Unknown'),
                    'token_ids': self._parse_token_ids(market.get('clobTokenIds', '[]')),
                    'outcome_prices': self._parse_prices(market.get('outcomePrices', '[]')),
                    'volume_24h': float(market.get('volume24hr', 0)),
                    'last_updated': market.get('updatedAt', '')
                })

        # Sort by volume
        active_bets.sort(key=lambda x: x['volume'], reverse=True)
        print(f"[OK] Found {len(active_bets)} markets with volume >= ${min_volume:,.0f}")

        return active_bets

    # ========== METHOD 2: Get User Positions (No Auth) ==========

    def get_user_positions(self, wallet_address: str) -> Dict[str, Any]:
        """
        Get all positions for a specific wallet address
        Shows what bets they currently hold
        """
        print(f"\n[+] Fetching positions for {wallet_address}...")

        response = self.session.get(
            f"{DATA_API}/positions",
            params={"user": wallet_address},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()

        positions = data.get('positions', [])
        print(f"[OK] Found {len(positions)} positions")

        return {
            'wallet': wallet_address,
            'total_positions': len(positions),
            'positions': positions
        }

    # ========== METHOD 3: Get Market Trades (No Auth) ==========

    def get_market_trades(self, condition_id: str, limit: int = 50) -> List[Dict]:
        """
        Get recent trades for a specific market
        Shows live betting activity
        """
        print(f"\n[+] Fetching trades for market {condition_id[:20]}...")

        response = self.session.get(
            f"{DATA_API}/trades",
            params={
                "market": condition_id,
                "limit": limit
            },
            timeout=30
        )
        response.raise_for_status()
        trades = response.json()

        print(f"[OK] Found {len(trades)} recent trades")

        # Format trades
        formatted_trades = []
        for trade in trades:
            formatted_trades.append({
                'trader': trade.get('trader', 'Unknown'),
                'side': trade.get('side', 'Unknown'),  # BUY or SELL
                'size': float(trade.get('size', 0)),
                'price': float(trade.get('price', 0)),
                'timestamp': trade.get('timestamp', ''),
                'transaction_hash': trade.get('transactionHash', '')
            })

        return formatted_trades

    # ========== METHOD 4: Get Live Orderbook ==========

    def get_orderbook(self, token_id: str) -> Dict[str, Any]:
        """
        Get live orderbook (bids and asks) for a token
        Shows pending orders at each price level
        """
        print(f"\n[+] Fetching orderbook for token {token_id[:30]}...")

        response = self.session.get(
            f"{CLOB_API}/book",
            params={"token_id": token_id},
            timeout=30
        )
        response.raise_for_status()
        book = response.json()

        bids = book.get('bids', [])
        asks = book.get('asks', [])

        print(f"[OK] Found {len(bids)} bids, {len(asks)} asks")

        return {
            'token_id': token_id,
            'bids': bids[:10],  # Top 10 bids
            'asks': asks[:10],  # Top 10 asks
            'best_bid': bids[0] if bids else None,
            'best_ask': asks[0] if asks else None
        }

    # ========== METHOD 5: Get Historical Prices ==========

    def get_price_history(self, condition_id: str, interval: str = "1h") -> List[Dict]:
        """
        Get historical price data for charting
        interval: 1m, 5m, 1h, 1d, max
        """
        print(f"\n[+] Fetching price history ({interval})...")

        response = self.session.get(
            f"{DATA_API}/prices",
            params={
                "market": condition_id,
                "interval": interval
            },
            timeout=30
        )
        response.raise_for_status()
        prices = response.json()

        print(f"[OK] Retrieved {len(prices)} price points")
        return prices

    # ========== Utility Methods ==========

    def _parse_token_ids(self, token_ids_str: str) -> List[str]:
        """Parse token IDs from JSON string"""
        try:
            return json.loads(token_ids_str)
        except:
            return []

    def _parse_prices(self, prices_str: str) -> List[float]:
        """Parse prices from JSON string"""
        try:
            prices = json.loads(prices_str)
            return [float(p) for p in prices]
        except:
            return []

    def find_market_by_slug(self, slug: str) -> Optional[Dict]:
        """Find a specific market by its slug"""
        response = self.session.get(
            f"{GAMMA_API}/events",
            params={"slug": slug},
            timeout=30
        )
        response.raise_for_status()
        events = response.json()

        if events and len(events) > 0:
            return events[0]
        return None


# ========== DEMO / TEST ==========

def main():
    print("=" * 70)
    print("POLYMARKET LIVE BET FETCHER")
    print("=" * 70)
    print(f"Time: {datetime.now()}")

    client = PolymarketLiveBets()

    # --- DEMO 1: Get Top Active Markets ---
    print("\n" + "=" * 70)
    print("DEMO 1: TOP 10 ACTIVE MARKETS")
    print("=" * 70)

    markets = client.get_active_markets(limit=50, min_volume=100000)

    for i, market in enumerate(markets[:10], 1):
        print(f"\n{i}. {market['question'][:70]}...")
        print(f"   Volume: ${market['volume']:,.0f} | 24h: ${market['volume_24h']:,.0f}")
        print(f"   Bid: {market['best_bid']:.3f} | Ask: {market['best_ask']:.3f} | Spread: {market['spread']:.3f}")
        if market['outcome_prices']:
            print(f"   Prices: YES {market['outcome_prices'][0]:.3f} | NO {market['outcome_prices'][1]:.3f}")
        print(f"   Link: https://polymarket.com/event/{market['slug']}")

    # --- DEMO 2: Get Specific Market Orderbook ---
    if markets:
        print("\n" + "=" * 70)
        print("DEMO 2: LIVE ORDERBOOK (Top Market)")
        print("=" * 70)

        top_market = markets[0]
        if top_market['token_ids']:
            orderbook = client.get_orderbook(top_market['token_ids'][0])

            print(f"\nMarket: {top_market['question'][:60]}...")
            print("\n[SELL ORDERS - ASKS]:")
            for ask in orderbook['asks'][:5]:
                price = float(ask['price']) if isinstance(ask['price'], str) else ask['price']
                size = float(ask['size']) if isinstance(ask['size'], str) else ask['size']
                print(f"   {price:.3f} x ${size:,.0f}")

            print("\n[BUY ORDERS - BIDS]:")
            for bid in orderbook['bids'][:5]:
                price = float(bid['price']) if isinstance(bid['price'], str) else bid['price']
                size = float(bid['size']) if isinstance(bid['size'], str) else bid['size']
                print(f"   {price:.3f} x ${size:,.0f}")

    # --- DEMO 3: Get Recent Trades ---
    if markets:
        print("\n" + "=" * 70)
        print("DEMO 3: RECENT TRADES")
        print("=" * 70)

        trades = client.get_market_trades(markets[0]['condition_id'], limit=10)

        for trade in trades[:5]:
            side_marker = ">>>" if trade['side'] == 'BUY' else "<<<"
            ts = trade['timestamp']
            ts_str = str(ts)[:16] if isinstance(ts, str) else str(ts)
            print(f"{side_marker} {trade['side']:4} {trade['price']:.3f} x ${trade['size']:,.0f} @ {ts_str}")

    # --- DEMO 4: Example User Positions ---
    print("\n" + "=" * 70)
    print("DEMO 4: USER POSITIONS (Example)")
    print("=" * 70)
    print("\nTo get positions for a specific wallet, call:")
    print("  positions = client.get_user_positions('0x...')")
    print("\nThis returns all bets that wallet is currently holding.")

    # Save results
    print("\n" + "=" * 70)
    print("SAVING RESULTS")
    print("=" * 70)

    output = {
        'timestamp': datetime.now().isoformat(),
        'top_markets': markets[:20],
        'count': len(markets)
    }

    with open('live_bets_output.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)

    print("[OK] Saved to live_bets_output.json")
    print(f"\nFound {len(markets)} active markets with significant volume")
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)


if __name__ == "__main__":
    main()
