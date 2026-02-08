"""
Signal Detector V2.0 - Kaizen Backtest Improvements
Implements all Phase 1 filters from 8-agent parallel backtest (Feb 6, 2026)

Key Improvements:
1. Trend filter: Only enter if price UP from 24h ago (win rate 48% → 67%)
2. Time horizon: Only markets closing <3 days (win rate 33% → 66.7%)
3. NO-side bias: Bet NO on unlikely events <15% prob (82% win rate)
4. ROC upgrade: 15% / 24h (win rate 57% → 65.6%)
5. Category filter: Politics/crypto only (93.5% & 87.5% strategy fit)

V2.1 Update (Feb 7, 2026):
6. Order book depth filter: >$10K liquidity (forward testing - unproven)
"""

import requests
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)

class SignalDetectorV2:
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.clob_api = "https://clob.polymarket.com"
        self.depth_threshold = 10000  # $10K minimum order book depth
        self.depth_log_file = "orderbook_depth_log.jsonl"  # Forward testing log
        
    def _get_orderbook_depth(self, token_id):
        """
        Fetch order book depth from Polymarket CLOB API
        
        Args:
            token_id: Token ID for YES or NO side
            
        Returns:
            dict with total_depth, bid_depth, ask_depth, spread
        """
        try:
            response = requests.get(
                f"{self.clob_api}/book",
                params={'token_id': token_id},
                timeout=5
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch orderbook for {token_id}: {response.status_code}")
                return None
            
            book = response.json()
            
            # Calculate bid depth (total $ on buy side)
            bids = book.get('bids', [])
            bid_depth = sum(float(bid.get('size', 0)) for bid in bids)
            
            # Calculate ask depth (total $ on sell side)
            asks = book.get('asks', [])
            ask_depth = sum(float(ask.get('size', 0)) for ask in asks)
            
            # Total liquidity
            total_depth = bid_depth + ask_depth
            
            # Spread (best ask - best bid)
            best_bid = float(bids[0]['price']) if bids else 0
            best_ask = float(asks[0]['price']) if asks else 1
            spread = best_ask - best_bid
            
            return {
                'total_depth': total_depth,
                'bid_depth': bid_depth,
                'ask_depth': ask_depth,
                'spread': spread,
                'best_bid': best_bid,
                'best_ask': best_ask
            }
            
        except Exception as e:
            logger.error(f"Error fetching orderbook depth: {e}")
            return None
    
    def _log_depth_measurement(self, market_id, title, depth_data, passed_filter, signal_data=None):
        """
        Log order book depth for forward testing analysis
        
        Logs to JSONL file for later analysis: Does thin market filtering actually work?
        """
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'market_id': market_id,
                'title': title,
                'depth_data': depth_data,
                'passed_depth_filter': passed_filter,
                'depth_threshold': self.depth_threshold
            }
            
            if signal_data:
                log_entry['signal'] = signal_data
            
            with open(self.depth_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
            logger.debug(f"📝 Logged depth measurement for {title[:40]}")
            
        except Exception as e:
            logger.error(f"Error logging depth: {e}")
    
    def detect_signals(self, markets_data):
        """
        Detect trading signals with V2.1 filters (includes order book depth)
        
        Args:
            markets_data: List of market dicts from Polymarket gamma API
            
        Returns:
            List of signal dicts with entry side (YES/NO), market info, reasoning
        """
        signals = []
        
        for market in markets_data:
            signal = self._analyze_market(market)
            if signal:
                signals.append(signal)
                
        return signals
    
    def _analyze_market(self, market):
        """Analyze single market for entry signal"""
        
        try:
            # Extract market data
            market_id = market.get('id')
            title = market.get('question', 'Unknown')
            current_price = float(market.get('outcomePrices', ['0'])[0])  # YES price
            volume_24h = float(market.get('volume24hr', 0))
            end_date_str = market.get('endDate')
            category = market.get('category', '').lower()
            
            # Parse end date
            if not end_date_str:
                return None
            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
            days_to_resolution = (end_date - datetime.now()).days
            
            # FILTER 1: TIME HORIZON (<3 days only)
            if days_to_resolution >= 3:
                logger.debug(f"❌ {title[:50]} - Too far out ({days_to_resolution}d)")
                return None
            
            # FILTER 2: CATEGORY (Politics or Crypto only)
            valid_categories = ['politics', 'crypto', 'cryptocurrency']
            if not any(cat in category for cat in valid_categories):
                logger.debug(f"❌ {title[:50]} - Wrong category ({category})")
                return None
            
            # Get historical data for trend & ROC
            hist_data = self._get_historical_data(market_id)
            if not hist_data:
                return None
            
            price_24h_ago = hist_data.get('price_24h_ago')
            volume_24h_ago = hist_data.get('volume_24h_ago', volume_24h)
            price_24h_change_pct = ((current_price - price_24h_ago) / price_24h_ago * 100) if price_24h_ago else 0
            
            # FILTER 3: TREND FILTER (price must be UP from 24h ago)
            if current_price <= price_24h_ago:
                logger.debug(f"❌ {title[:50]} - Falling price ({current_price:.1%} < {price_24h_ago:.1%})")
                return None
            
            # FILTER 4: ROC SIGNAL (15% momentum over 24h)
            if abs(price_24h_change_pct) < 15:
                logger.debug(f"❌ {title[:50]} - Weak momentum ({price_24h_change_pct:.1f}%)")
                return None
            
            # FILTER 5: RVR SIGNAL (2.5x volume spike)
            rvr_ratio = volume_24h / volume_24h_ago if volume_24h_ago > 0 else 0
            if rvr_ratio < 2.5:
                logger.debug(f"❌ {title[:50]} - Low RVR ({rvr_ratio:.1f}x)")
                return None
            
            # DETERMINE SIDE: NO if probability <15%, else YES
            side = "NO" if current_price < 0.15 else "YES"
            
            # Calculate effective entry price (for NO, it's 1 - current_price)
            entry_price = (1 - current_price) if side == "NO" else current_price
            
            # FILTER 6: ORDER BOOK DEPTH (>$10K liquidity)
            # Get token ID for the side we're trading
            clob_token_ids = market.get('clobTokenIds', [])
            if len(clob_token_ids) < 2:
                logger.warning(f"⚠️ {title[:50]} - No token IDs available")
                return None
            
            # Token index: 0 = YES, 1 = NO
            token_index = 1 if side == "NO" else 0
            token_id = clob_token_ids[token_index]
            
            # Fetch order book depth
            depth_data = self._get_orderbook_depth(token_id)
            
            if not depth_data:
                logger.warning(f"⚠️ {title[:50]} - Failed to fetch order book")
                # Log as unknown depth
                self._log_depth_measurement(market_id, title, None, False)
                return None
            
            total_depth = depth_data['total_depth']
            
            # Log depth measurement (for forward testing analysis)
            passed_depth_filter = total_depth >= self.depth_threshold
            
            if not passed_depth_filter:
                logger.debug(f"❌ {title[:50]} - Thin market (${total_depth:,.0f} < ${self.depth_threshold:,.0f})")
                self._log_depth_measurement(market_id, title, depth_data, False)
                return None
            
            logger.info(f"✅ {title[:50]} - Deep market (${total_depth:,.0f})")
            self._log_depth_measurement(market_id, title, depth_data, True)
            
            # Build signal
            signal = {
                'market_id': market_id,
                'title': title,
                'side': side,
                'entry_price': entry_price,
                'current_yes_price': current_price,
                'current_no_price': 1 - current_price,
                'rvr_ratio': rvr_ratio,
                'roc_24h_pct': price_24h_change_pct,
                'days_to_resolution': days_to_resolution,
                'category': category,
                'volume_24h': volume_24h,
                'orderbook_depth': total_depth,
                'orderbook_spread': depth_data['spread'],
                'orderbook_bid_depth': depth_data['bid_depth'],
                'orderbook_ask_depth': depth_data['ask_depth'],
                'reasoning': self._build_reasoning(
                    title, side, current_price, rvr_ratio, 
                    price_24h_change_pct, days_to_resolution, category,
                    total_depth, depth_data['spread']
                ),
                'filters_passed': {
                    'time_horizon': True,
                    'category': True,
                    'trend': True,
                    'roc': True,
                    'rvr': True,
                    'orderbook_depth': True
                }
            }
            
            # Log successful signal with depth data
            self._log_depth_measurement(market_id, title, depth_data, True, signal_data=signal)
            
            logger.info(f"✅ SIGNAL: {side} on {title[:60]} @ {entry_price:.1%}")
            return signal
            
        except Exception as e:
            logger.error(f"Error analyzing market: {e}")
            return None
    
    def _get_historical_data(self, market_id):
        """
        Get 24h historical data for trend filter & ROC calculation
        
        Queries the historical price database built by historical_scraper.py
        """
        try:
            from historical_db import get_db
            
            # Query historical database
            db = get_db()
            hist_data = db.get_historical_data(market_id)
            
            if hist_data and hist_data['price_24h_ago'] is not None:
                logger.debug(f"📊 Found historical data for {market_id}")
                return hist_data
            else:
                logger.debug(f"⚠️ No historical data for {market_id} - skipping market")
                return None
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def _build_reasoning(self, title, side, price, rvr, roc, days, category, depth, spread):
        """Build human-readable reasoning for signal"""
        
        reasoning = f"""
🎯 SIGNAL DETECTED: {side} on {title[:60]}

📊 Entry Analysis:
• Side: {side} @ {price:.1%}
• Category: {category.upper()} ✅ (93%+ strategy fit)
• Resolution: {days} days ✅ (<3d = 66.7% win rate)

📈 Momentum Signals:
• RVR: {rvr:.1f}x ✅ (volume spike >2.5x)
• ROC: {roc:+.1f}% over 24h ✅ (>15% threshold)
• Trend: UP ✅ (no falling knife)

💧 Liquidity Check:
• Order book depth: ${depth:,.0f} ✅ (>${self.depth_threshold:,.0f} threshold)
• Spread: {spread:.1%} (tighter = better execution)
• Status: DEEP MARKET (low manipulation risk)

💡 Strategy Rationale:
"""
        
        if side == "NO":
            reasoning += f"""• Probability {price:.1%} is UNLIKELY (<15%)
• Base rate neglect: retail panic pushing price too high
• Betting NO = fade the hype (82% backtest win rate)
• Expect mean reversion as fear subsides
"""
        else:
            reasoning += f"""• Strong momentum: {roc:+.1f}% gain in 24h
• Volume spike: {rvr:.1f}x confirms conviction
• Trend filter passed: price rising, not falling
• Riding momentum to resolution in {days}d
"""
        
        reasoning += f"""
🎲 Risk Management:
• Stop-loss: 12% (hard stop)
• Take-profits: 25% @ +20%, 50% @ +30%, runner @ +50%
• Position size: Quarter Kelly (6.25% of bankroll)

🧠 V2.1 Filters Applied:
✅ Time horizon (<3d)
✅ Category (politics/crypto)
✅ Trend (price UP from 24h ago)
✅ ROC (15% / 24h momentum)
✅ RVR (2.5x volume spike)
✅ NO-side bias (if prob <15%)
✅ Order book depth (>${self.depth_threshold/1000:.0f}K - FORWARD TESTING)

Expected edge: 60-70% win rate based on Kaizen backtests.
Note: Depth filter is unproven - collecting data for 2-4 weeks validation.
"""
        
        return reasoning.strip()


# Utility function for integration with existing system
def get_signals_v2():
    """
    Drop-in replacement for existing signal detection
    
    Returns:
        List of trading signals with V2.0 filters applied
    """
    try:
        # Fetch active markets from Polymarket gamma API
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={'limit': 100, 'active': True},
            timeout=10
        )
        
        if response.status_code != 200:
            logger.error(f"Failed to fetch markets: {response.status_code}")
            return []
        
        markets = response.json()
        
        # Run V2.0 signal detection
        detector = SignalDetectorV2()
        signals = detector.detect_signals(markets)
        
        logger.info(f"Scanned {len(markets)} markets, found {len(signals)} V2.0 signals")
        return signals
        
    except Exception as e:
        logger.error(f"Error in get_signals_v2: {e}")
        return []


if __name__ == "__main__":
    # Test the detector
    logging.basicConfig(level=logging.INFO)
    
    print("🔬 Testing Signal Detector V2.0...")
    print("=" * 60)
    
    signals = get_signals_v2()
    
    if signals:
        print(f"\n✅ Found {len(signals)} signals:\n")
        for i, sig in enumerate(signals, 1):
            print(f"{i}. {sig['side']} on {sig['title'][:60]}")
            print(f"   Entry: {sig['entry_price']:.1%} | RVR: {sig['rvr_ratio']:.1f}x | ROC: {sig['roc_24h_pct']:+.1f}%")
            print(f"   Days: {sig['days_to_resolution']}d | Category: {sig['category']}")
            print()
    else:
        print("\n⚠️ No signals found (all markets filtered out by V2.0 criteria)")
        print("\nThis is NORMAL - V2.0 filters are strict:")
        print("• <3 days to resolution")
        print("• Politics/crypto only")
        print("• Price UP from 24h ago")
        print("• 15% ROC over 24h")
        print("• 2.5x RVR spike")
