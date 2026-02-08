# Order Book Depth Implementation Guide

**Created:** 2026-02-07  
**Purpose:** Practical guide for implementing order book depth checks using Polymarket CLOB API

---

## Quick Start

### Step 1: Test CLOB API Access

```python
import requests

# Test basic connectivity
def test_clob_api():
    """Verify CLOB API is accessible"""
    
    # Health check
    response = requests.get("https://clob.polymarket.com/markets")
    if response.status_code == 200:
        markets = response.json()
        print(f"✅ CLOB API accessible. Found {len(markets)} markets")
        return True
    else:
        print(f"❌ CLOB API error: {response.status_code}")
        return False

# Run test
if __name__ == "__main__":
    test_clob_api()
```

### Step 2: Get Order Book for a Market

```python
import requests
from typing import Dict, Optional

def get_order_book(token_id: str) -> Optional[Dict]:
    """
    Fetch order book for a specific token
    
    Args:
        token_id: Token ID from CLOB markets endpoint
        
    Returns:
        Order book data or None if error
    """
    url = f"https://clob.polymarket.com/book"
    params = {"token_id": token_id}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching order book: {e}")
        return None

# Example usage
# token_id = "29763725280755533853228704213586000655160583839125347030858041807759211842058"
# book = get_order_book(token_id)
# print(book)
```

### Step 3: Calculate Order Book Depth

```python
from typing import Dict, List, Tuple

def calculate_depth_within_range(
    order_book: Dict,
    pct_range: float = 0.05
) -> Tuple[float, float, float, float]:
    """
    Calculate order book depth within % range of mid-price
    
    Args:
        order_book: CLOB order book response
        pct_range: Percentage range (0.05 = 5%)
        
    Returns:
        (bid_depth_usd, ask_depth_usd, total_depth_usd, mid_price)
    """
    bids = order_book.get('bids', [])
    asks = order_book.get('asks', [])
    
    if not bids or not asks:
        return (0.0, 0.0, 0.0, 0.0)
    
    # Calculate mid-price
    best_bid = float(bids[0]['price'])
    best_ask = float(asks[0]['price'])
    mid_price = (best_bid + best_ask) / 2.0
    
    # Define price range
    lower_bound = mid_price * (1 - pct_range)
    upper_bound = mid_price * (1 + pct_range)
    
    # Sum bid depth (bids within range)
    bid_depth_usd = sum(
        float(bid['price']) * float(bid['size'])
        for bid in bids
        if float(bid['price']) >= lower_bound
    )
    
    # Sum ask depth (asks within range)
    ask_depth_usd = sum(
        float(ask['price']) * float(ask['size'])
        for ask in asks
        if float(ask['price']) <= upper_bound
    )
    
    total_depth_usd = bid_depth_usd + ask_depth_usd
    
    return (bid_depth_usd, ask_depth_usd, total_depth_usd, mid_price)

# Example usage
"""
book = get_order_book(token_id)
bid_depth, ask_depth, total_depth, mid = calculate_depth_within_range(book)
print(f"Bid depth: ${bid_depth:,.2f}")
print(f"Ask depth: ${ask_depth:,.2f}")
print(f"Total depth: ${total_depth:,.2f}")
print(f"Mid-price: ${mid:.4f}")
"""
```

---

## Complete Pre-Trade Check Function

```python
from typing import Dict, Optional
from dataclasses import dataclass

@dataclass
class DepthCheckResult:
    """Result of order book depth check"""
    approved: bool
    reason: str
    total_depth: float
    bid_depth: float
    ask_depth: float
    imbalance_ratio: float
    spread_pct: float
    mid_price: float

def check_order_book_depth(
    token_id: str,
    min_depth_usd: float = 10000,
    max_imbalance: float = 0.7,
    max_spread_pct: float = 0.02,
    pct_range: float = 0.05
) -> Optional[DepthCheckResult]:
    """
    Complete pre-trade order book depth check
    
    Args:
        token_id: CLOB token ID for the market outcome
        min_depth_usd: Minimum liquidity required (default $10k)
        max_imbalance: Maximum order book imbalance (default 0.7 = 70/30)
        max_spread_pct: Maximum allowed spread (default 2%)
        pct_range: Price range for depth calculation (default 5%)
        
    Returns:
        DepthCheckResult or None if API error
    """
    # Fetch order book
    book = get_order_book(token_id)
    if not book:
        return None
    
    bids = book.get('bids', [])
    asks = book.get('asks', [])
    
    # Check if order book exists
    if not bids or not asks:
        return DepthCheckResult(
            approved=False,
            reason="No order book (insufficient liquidity)",
            total_depth=0,
            bid_depth=0,
            ask_depth=0,
            imbalance_ratio=0,
            spread_pct=0,
            mid_price=0
        )
    
    # Calculate mid-price and spread
    best_bid = float(bids[0]['price'])
    best_ask = float(asks[0]['price'])
    mid_price = (best_bid + best_ask) / 2.0
    spread_pct = (best_ask - best_bid) / mid_price if mid_price > 0 else 1.0
    
    # Check spread
    if spread_pct > max_spread_pct:
        return DepthCheckResult(
            approved=False,
            reason=f"Spread too wide: {spread_pct*100:.2f}% > {max_spread_pct*100:.0f}%",
            total_depth=0,
            bid_depth=0,
            ask_depth=0,
            imbalance_ratio=0,
            spread_pct=spread_pct,
            mid_price=mid_price
        )
    
    # Calculate depth within range
    bid_depth, ask_depth, total_depth, _ = calculate_depth_within_range(book, pct_range)
    
    # Check minimum depth
    if total_depth < min_depth_usd:
        return DepthCheckResult(
            approved=False,
            reason=f"Insufficient depth: ${total_depth:,.0f} < ${min_depth_usd:,.0f}",
            total_depth=total_depth,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            imbalance_ratio=bid_depth / total_depth if total_depth > 0 else 0.5,
            spread_pct=spread_pct,
            mid_price=mid_price
        )
    
    # Calculate imbalance
    imbalance_ratio = bid_depth / total_depth if total_depth > 0 else 0.5
    
    # Check imbalance
    if imbalance_ratio > max_imbalance or imbalance_ratio < (1 - max_imbalance):
        return DepthCheckResult(
            approved=False,
            reason=f"Order book imbalance: {imbalance_ratio*100:.0f}/{(1-imbalance_ratio)*100:.0f}",
            total_depth=total_depth,
            bid_depth=bid_depth,
            ask_depth=ask_depth,
            imbalance_ratio=imbalance_ratio,
            spread_pct=spread_pct,
            mid_price=mid_price
        )
    
    # All checks passed
    return DepthCheckResult(
        approved=True,
        reason="Order book depth sufficient",
        total_depth=total_depth,
        bid_depth=bid_depth,
        ask_depth=ask_depth,
        imbalance_ratio=imbalance_ratio,
        spread_pct=spread_pct,
        mid_price=mid_price
    )

# Example usage
"""
result = check_order_book_depth(token_id)
if result and result.approved:
    print("✅ Trade approved")
    print(f"   Depth: ${result.total_depth:,.2f}")
    print(f"   Spread: {result.spread_pct*100:.2f}%")
else:
    print(f"❌ Trade rejected: {result.reason if result else 'API error'}")
"""
```

---

## Getting Token IDs from Market Info

```python
def get_market_token_ids(condition_id: str) -> Optional[List[str]]:
    """
    Get token IDs for a market using Gamma API
    
    Args:
        condition_id: Market condition ID from Gamma API
        
    Returns:
        List of token IDs [yes_token, no_token] or None
    """
    # First get market details from Gamma
    gamma_url = f"https://gamma-api.polymarket.com/markets"
    
    try:
        response = requests.get(gamma_url, params={"id": condition_id})
        response.raise_for_status()
        markets = response.json()
        
        if not markets:
            return None
            
        market = markets[0]
        token_ids = market.get('clobTokenIds', [])
        
        return token_ids if len(token_ids) == 2 else None
        
    except Exception as e:
        print(f"Error fetching market token IDs: {e}")
        return None

# Example: Get token IDs for a market
"""
condition_id = "0x3bed62b0b7e3eb52c1f0d8a5d11edad1f74989038fc1cae2889cdbe96a248dfe"
token_ids = get_market_token_ids(condition_id)
if token_ids:
    yes_token, no_token = token_ids
    print(f"YES token: {yes_token}")
    print(f"NO token: {no_token}")
"""
```

---

## Integration with Trading System

```python
from typing import Optional

class OrderBookFilter:
    """Order book depth filter for trading decisions"""
    
    def __init__(
        self,
        min_depth_usd: float = 10000,
        max_imbalance: float = 0.7,
        max_spread_pct: float = 0.02,
        pct_range: float = 0.05
    ):
        self.min_depth_usd = min_depth_usd
        self.max_imbalance = max_imbalance
        self.max_spread_pct = max_spread_pct
        self.pct_range = pct_range
        
    def should_trade(self, market_condition_id: str, side: str = "YES") -> bool:
        """
        Check if market meets order book depth requirements
        
        Args:
            market_condition_id: Gamma API condition ID
            side: "YES" or "NO" outcome to trade
            
        Returns:
            True if should trade, False otherwise
        """
        # Get token IDs
        token_ids = get_market_token_ids(market_condition_id)
        if not token_ids:
            print(f"⚠️  Could not get token IDs for {market_condition_id}")
            return False
        
        # Select appropriate token (YES=0, NO=1)
        token_id = token_ids[0] if side == "YES" else token_ids[1]
        
        # Check order book depth
        result = check_order_book_depth(
            token_id,
            min_depth_usd=self.min_depth_usd,
            max_imbalance=self.max_imbalance,
            max_spread_pct=self.max_spread_pct,
            pct_range=self.pct_range
        )
        
        if not result:
            print(f"⚠️  Could not fetch order book for {market_condition_id}")
            return False
        
        if result.approved:
            print(f"✅ {market_condition_id[:10]}... - Depth: ${result.total_depth:,.0f}, "
                  f"Spread: {result.spread_pct*100:.2f}%")
        else:
            print(f"❌ {market_condition_id[:10]}... - {result.reason}")
        
        return result.approved

# Example usage in trading loop
"""
filter = OrderBookFilter(min_depth_usd=10000)

# Check if should trade
if filter.should_trade(condition_id, side="YES"):
    # Proceed with trade
    place_trade(condition_id, side="YES", amount=100)
else:
    # Skip this market
    print("Skipping due to insufficient depth")
"""
```

---

## Data Logging for Backtesting

```python
import json
from datetime import datetime

class DepthDataLogger:
    """Log order book depth data for backtesting"""
    
    def __init__(self, log_file: str = "order_book_depth_log.json"):
        self.log_file = log_file
        
    def log_depth_check(
        self,
        market_id: str,
        market_question: str,
        token_id: str,
        result: DepthCheckResult,
        trade_decision: str
    ):
        """
        Log order book depth check for analysis
        
        Args:
            market_id: Market condition ID
            market_question: Market question/title
            token_id: CLOB token ID checked
            result: DepthCheckResult from check
            trade_decision: "TRADE" or "SKIP"
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "market_id": market_id,
            "market_question": market_question,
            "token_id": token_id,
            "approved": result.approved,
            "reason": result.reason,
            "total_depth_usd": result.total_depth,
            "bid_depth_usd": result.bid_depth,
            "ask_depth_usd": result.ask_depth,
            "imbalance_ratio": result.imbalance_ratio,
            "spread_pct": result.spread_pct,
            "mid_price": result.mid_price,
            "trade_decision": trade_decision
        }
        
        # Append to log file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"Error logging depth data: {e}")

# Example usage
"""
logger = DepthDataLogger()

result = check_order_book_depth(token_id)
decision = "TRADE" if result.approved else "SKIP"

logger.log_depth_check(
    market_id=condition_id,
    market_question="Will X happen by Y?",
    token_id=token_id,
    result=result,
    trade_decision=decision
)
"""
```

---

## Historical Depth Analysis (Future)

```python
import json
from collections import defaultdict

def analyze_depth_outcomes(log_file: str = "order_book_depth_log.json"):
    """
    Analyze historical outcomes of trades vs depth
    
    Args:
        log_file: Path to depth log file
        
    Note: Requires adding trade outcomes to log entries
    """
    thin_markets = []  # depth < $10k
    deep_markets = []  # depth >= $10k
    
    with open(log_file, 'r') as f:
        for line in f:
            entry = json.loads(line)
            
            # Skip if no outcome data (for future implementation)
            if 'outcome' not in entry:
                continue
                
            if entry['total_depth_usd'] < 10000:
                thin_markets.append(entry)
            else:
                deep_markets.append(entry)
    
    # Calculate statistics
    def calc_stats(markets):
        if not markets:
            return {"count": 0, "win_rate": 0, "avg_profit": 0}
            
        wins = sum(1 for m in markets if m.get('outcome') == 'WIN')
        profits = [m.get('profit', 0) for m in markets]
        
        return {
            "count": len(markets),
            "win_rate": wins / len(markets),
            "avg_profit": sum(profits) / len(profits)
        }
    
    thin_stats = calc_stats(thin_markets)
    deep_stats = calc_stats(deep_markets)
    
    print("=== Order Book Depth Analysis ===")
    print(f"\nThin Markets (< $10k depth):")
    print(f"  Trades: {thin_stats['count']}")
    print(f"  Win Rate: {thin_stats['win_rate']*100:.1f}%")
    print(f"  Avg Profit: ${thin_stats['avg_profit']:.2f}")
    
    print(f"\nDeep Markets (>= $10k depth):")
    print(f"  Trades: {deep_stats['count']}")
    print(f"  Win Rate: {deep_stats['win_rate']*100:.1f}%")
    print(f"  Avg Profit: ${deep_stats['avg_profit']:.2f}")

# Future: Run this after collecting trade outcomes
# analyze_depth_outcomes()
```

---

## Testing Checklist

### Phase 1: API Connectivity
- [ ] Test CLOB API health check
- [ ] Fetch sample market list
- [ ] Get order book for active market
- [ ] Parse order book structure

### Phase 2: Depth Calculation
- [ ] Calculate bid depth within 5%
- [ ] Calculate ask depth within 5%
- [ ] Verify total depth calculation
- [ ] Test edge cases (empty book, single order, etc.)

### Phase 3: Decision Logic
- [ ] Test minimum depth threshold ($10k)
- [ ] Test imbalance detection (70/30 ratio)
- [ ] Test spread filter (2%)
- [ ] Verify approval/rejection logic

### Phase 4: Integration
- [ ] Integrate with market discovery (Gamma API)
- [ ] Map condition IDs to token IDs
- [ ] Handle both YES and NO sides
- [ ] Log depth checks for analysis

### Phase 5: Data Collection
- [ ] Set up depth logging
- [ ] Collect 50+ samples
- [ ] Track trade outcomes (manual for now)
- [ ] Analyze thin vs deep performance

---

## Quick Test Script

```python
#!/usr/bin/env python3
"""
Quick test of order book depth filter
Run this to verify everything works
"""

import requests

def quick_test():
    print("🔍 Testing Order Book Depth Filter\n")
    
    # Step 1: Get an active market
    print("1. Fetching active markets...")
    markets_resp = requests.get("https://clob.polymarket.com/markets")
    if markets_resp.status_code != 200:
        print("❌ Failed to fetch markets")
        return
    
    markets = markets_resp.json()
    print(f"✅ Found {len(markets)} markets\n")
    
    # Step 2: Pick first market and get order book
    if not markets:
        print("❌ No markets available")
        return
        
    test_market = markets[0]
    token_id = test_market.get('tokens', [{}])[0].get('token_id')
    
    if not token_id:
        print("❌ Could not extract token ID")
        return
    
    print(f"2. Testing market token: {token_id[:20]}...")
    
    # Step 3: Get order book
    book_resp = requests.get(f"https://clob.polymarket.com/book?token_id={token_id}")
    if book_resp.status_code != 200:
        print(f"❌ Failed to fetch order book: {book_resp.status_code}")
        return
    
    book = book_resp.json()
    bids = book.get('bids', [])
    asks = book.get('asks', [])
    
    print(f"✅ Order book loaded:")
    print(f"   Bids: {len(bids)}")
    print(f"   Asks: {len(asks)}")
    
    if bids and asks:
        print(f"   Best Bid: {bids[0]['price']}")
        print(f"   Best Ask: {asks[0]['price']}")
    
    print("\n✅ All systems operational!")

if __name__ == "__main__":
    quick_test()
```

Save as `test_depth_filter.py` and run:
```bash
python test_depth_filter.py
```

---

## Next Steps

1. **Run quick test** to verify API access
2. **Implement depth filter** in your trading system
3. **Start logging** depth checks immediately
4. **Collect 50+ samples** over 1-2 weeks
5. **Analyze outcomes** - did thin markets perform worse?
6. **Tune thresholds** based on data ($10k might be too high/low)
7. **Backtest** on historical trades if outcome data available

---

## Common Issues & Solutions

### Issue: "No order book found"
**Cause:** Token ID is invalid or market has no liquidity  
**Solution:** Verify token ID from Gamma API, check if market is active

### Issue: API rate limiting
**Cause:** Too many requests in short time  
**Solution:** Add delays between requests (0.5-1 second), implement exponential backoff

### Issue: Token ID not mapping to condition ID
**Cause:** Using wrong API or wrong ID type  
**Solution:** Use Gamma API to get `clobTokenIds` array from market object

### Issue: Depth calculation seems wrong
**Cause:** Price range too narrow/wide, or price format misunderstood  
**Solution:** Verify prices are 0-1 range (probabilities), check percentage range calculation

---

## API Reference Quick Links

- **CLOB Docs:** https://docs.polymarket.com/developers/CLOB/introduction
- **Gamma Docs:** https://docs.polymarket.com/developers/gamma-markets-api/overview
- **Order Book Endpoint:** `GET https://clob.polymarket.com/book?token_id={ID}`
- **Markets Endpoint:** `GET https://gamma-api.polymarket.com/markets`

---

**Last Updated:** 2026-02-07  
**Status:** Ready for implementation  
**Estimated Setup Time:** 1-2 hours
