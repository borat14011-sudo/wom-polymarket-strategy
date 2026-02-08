#!/usr/bin/env python3
"""
Market Microstructure Analyzer for Polymarket
Analyzes order book dynamics, whale activity, liquidity, and price impact
"""

import requests
import argparse
import json
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import statistics


@dataclass
class OrderBookSnapshot:
    """Snapshot of order book state"""
    timestamp: float
    bids: List[Tuple[float, float]]  # (price, size)
    asks: List[Tuple[float, float]]
    market_id: str


@dataclass
class SpreadMetrics:
    """Bid-ask spread analysis"""
    spread_abs: float
    spread_bps: float  # basis points
    mid_price: float
    best_bid: float
    best_ask: float
    bid_depth_1k: float  # depth within $1K of best bid
    ask_depth_1k: float


@dataclass
class ImbalanceMetrics:
    """Order book imbalance indicators"""
    ratio: float  # bid_value / ask_value
    net_pressure: float  # (bid - ask) / (bid + ask)
    signal: str  # "BUY_PRESSURE" | "SELL_PRESSURE" | "BALANCED"


@dataclass
class LiquidityMetrics:
    """Liquidity quality metrics"""
    score: float  # 0-100
    total_liquidity: float
    bid_liquidity: float
    ask_liquidity: float
    concentration: float  # Herfindahl index
    resilience: float  # depth beyond top level


@dataclass
class PriceImpact:
    """Price impact estimation"""
    order_size: float
    estimated_price: float
    slippage_pct: float
    slippage_abs: float
    optimal_size: float  # for <1% slippage


@dataclass
class WhaleActivity:
    """Whale detection metrics"""
    large_positions: List[Dict]
    top_10_positions: List[Dict]
    unusual_volume: bool
    smart_money_score: float  # 0-100


class PolymarketCLOB:
    """Interface to Polymarket CLOB API"""
    
    BASE_URL = "https://clob.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MarketMicrostructureAnalyzer/1.0'
        })
    
    def get_order_book(self, token_id: str) -> Dict:
        """Fetch order book for a token"""
        url = f"{self.BASE_URL}/book"
        params = {"token_id": token_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch order book: {e}")
    
    def get_market_info(self, condition_id: str) -> Dict:
        """Get market information"""
        url = f"{self.BASE_URL}/markets/{condition_id}"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {}
    
    def get_trades(self, market_id: str, limit: int = 100) -> List[Dict]:
        """Fetch recent trades"""
        url = f"{self.BASE_URL}/trades"
        params = {"market": market_id, "limit": limit}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return []
    
    def get_prices(self, token_id: str) -> Dict:
        """Get current price info"""
        url = f"{self.BASE_URL}/price"
        params = {"token_id": token_id}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {}


class MarketAnalyzer:
    """Main market microstructure analyzer"""
    
    def __init__(self, token_id: str):
        self.token_id = token_id
        self.clob = PolymarketCLOB()
        self.order_book_history: List[OrderBookSnapshot] = []
        self.max_history = 100
    
    def _parse_order_book(self, book_data: Dict) -> OrderBookSnapshot:
        """Parse order book response into snapshot"""
        bids = []
        asks = []
        
        if 'bids' in book_data:
            for order in book_data['bids']:
                price = float(order.get('price', 0))
                size = float(order.get('size', 0))
                if price > 0 and size > 0:
                    bids.append((price, size))
        
        if 'asks' in book_data:
            for order in book_data['asks']:
                price = float(order.get('price', 0))
                size = float(order.get('size', 0))
                if price > 0 and size > 0:
                    asks.append((price, size))
        
        # Sort bids descending, asks ascending
        bids.sort(reverse=True, key=lambda x: x[0])
        asks.sort(key=lambda x: x[0])
        
        return OrderBookSnapshot(
            timestamp=time.time(),
            bids=bids,
            asks=asks,
            market_id=self.token_id
        )
    
    def refresh_order_book(self) -> OrderBookSnapshot:
        """Fetch and store latest order book"""
        book_data = self.clob.get_order_book(self.token_id)
        snapshot = self._parse_order_book(book_data)
        
        self.order_book_history.append(snapshot)
        if len(self.order_book_history) > self.max_history:
            self.order_book_history.pop(0)
        
        return snapshot
    
    def get_current_snapshot(self) -> OrderBookSnapshot:
        """Get latest snapshot (refresh if none)"""
        if not self.order_book_history:
            return self.refresh_order_book()
        return self.order_book_history[-1]
    
    def get_spread(self) -> SpreadMetrics:
        """Calculate bid-ask spread metrics"""
        snapshot = self.get_current_snapshot()
        
        if not snapshot.bids or not snapshot.asks:
            return SpreadMetrics(0, 0, 0, 0, 0, 0, 0)
        
        best_bid = snapshot.bids[0][0]
        best_ask = snapshot.asks[0][0]
        
        spread_abs = best_ask - best_bid
        mid_price = (best_bid + best_ask) / 2
        spread_bps = (spread_abs / mid_price) * 10000 if mid_price > 0 else 0
        
        # Calculate depth within $1K
        bid_depth = sum(size for price, size in snapshot.bids if price * size <= 1000)
        ask_depth = sum(size for price, size in snapshot.asks if price * size <= 1000)
        
        return SpreadMetrics(
            spread_abs=spread_abs,
            spread_bps=spread_bps,
            mid_price=mid_price,
            best_bid=best_bid,
            best_ask=best_ask,
            bid_depth_1k=bid_depth,
            ask_depth_1k=ask_depth
        )
    
    def get_depth_profile(self, levels: int = 10) -> Dict:
        """Analyze order book depth at multiple levels"""
        snapshot = self.get_current_snapshot()
        
        depth = {
            'bids': [],
            'asks': [],
            'cumulative_bids': [],
            'cumulative_asks': []
        }
        
        cumulative_bid_value = 0
        for i, (price, size) in enumerate(snapshot.bids[:levels]):
            value = price * size
            cumulative_bid_value += value
            depth['bids'].append({
                'level': i,
                'price': price,
                'size': size,
                'value': value
            })
            depth['cumulative_bids'].append(cumulative_bid_value)
        
        cumulative_ask_value = 0
        for i, (price, size) in enumerate(snapshot.asks[:levels]):
            value = price * size
            cumulative_ask_value += value
            depth['asks'].append({
                'level': i,
                'price': price,
                'size': size,
                'value': value
            })
            depth['cumulative_asks'].append(cumulative_ask_value)
        
        return depth
    
    def get_imbalance(self) -> ImbalanceMetrics:
        """Calculate order book imbalance"""
        snapshot = self.get_current_snapshot()
        
        # Calculate value in top N levels
        levels = 5
        bid_value = sum(p * s for p, s in snapshot.bids[:levels])
        ask_value = sum(p * s for p, s in snapshot.asks[:levels])
        
        total_value = bid_value + ask_value
        if total_value == 0:
            return ImbalanceMetrics(1.0, 0, "BALANCED")
        
        ratio = bid_value / ask_value if ask_value > 0 else float('inf')
        net_pressure = (bid_value - ask_value) / total_value
        
        if net_pressure > 0.2:
            signal = "BUY_PRESSURE"
        elif net_pressure < -0.2:
            signal = "SELL_PRESSURE"
        else:
            signal = "BALANCED"
        
        return ImbalanceMetrics(
            ratio=ratio,
            net_pressure=net_pressure,
            signal=signal
        )
    
    def estimate_impact(self, order_size_usd: float, side: str = "buy") -> PriceImpact:
        """Estimate price impact for a given order size"""
        snapshot = self.get_current_snapshot()
        spread = self.get_spread()
        
        if side.lower() == "buy":
            orders = snapshot.asks
            reference_price = spread.best_ask
        else:
            orders = snapshot.bids
            reference_price = spread.best_bid
        
        remaining = order_size_usd
        filled_quantity = 0
        total_cost = 0
        
        for price, size in orders:
            order_value = price * size
            
            if remaining <= order_value:
                # Partially fill this level
                filled_qty = remaining / price
                filled_quantity += filled_qty
                total_cost += remaining
                break
            else:
                # Fully consume this level
                filled_quantity += size
                total_cost += order_value
                remaining -= order_value
        
        if filled_quantity == 0:
            return PriceImpact(order_size_usd, 0, 0, 0, 0)
        
        avg_price = total_cost / filled_quantity
        slippage_abs = abs(avg_price - reference_price)
        slippage_pct = (slippage_abs / reference_price) * 100 if reference_price > 0 else 0
        
        # Calculate optimal order size for <1% slippage
        optimal_size = 0
        cumulative = 0
        for price, size in orders:
            slippage = abs(price - reference_price) / reference_price * 100
            if slippage > 1.0:
                break
            optimal_size += price * size
            cumulative += size
        
        return PriceImpact(
            order_size=order_size_usd,
            estimated_price=avg_price,
            slippage_pct=slippage_pct,
            slippage_abs=slippage_abs,
            optimal_size=optimal_size
        )
    
    def get_liquidity_metrics(self) -> LiquidityMetrics:
        """Calculate comprehensive liquidity metrics"""
        snapshot = self.get_current_snapshot()
        
        # Total liquidity
        bid_liquidity = sum(p * s for p, s in snapshot.bids)
        ask_liquidity = sum(p * s for p, s in snapshot.asks)
        total_liquidity = bid_liquidity + ask_liquidity
        
        # Concentration (Herfindahl index)
        if total_liquidity > 0:
            all_values = [p * s for p, s in snapshot.bids + snapshot.asks]
            concentration = sum((v / total_liquidity) ** 2 for v in all_values)
        else:
            concentration = 1.0
        
        # Resilience (depth beyond top level)
        if len(snapshot.bids) > 1 and len(snapshot.asks) > 1:
            top_level = snapshot.bids[0][0] * snapshot.bids[0][1] + snapshot.asks[0][0] * snapshot.asks[0][1]
            deep_liquidity = total_liquidity - top_level
            resilience = deep_liquidity / total_liquidity if total_liquidity > 0 else 0
        else:
            resilience = 0
        
        # Liquidity score (0-100)
        spread = self.get_spread()
        spread_score = max(0, 100 - spread.spread_bps / 10)  # Lower spread = higher score
        depth_score = min(100, (total_liquidity / 10000) * 100)  # More liquidity = higher score
        concentration_score = max(0, (1 - concentration) * 100)  # Less concentration = higher score
        resilience_score = resilience * 100
        
        liquidity_score = (spread_score * 0.3 + depth_score * 0.3 + 
                          concentration_score * 0.2 + resilience_score * 0.2)
        
        return LiquidityMetrics(
            score=liquidity_score,
            total_liquidity=total_liquidity,
            bid_liquidity=bid_liquidity,
            ask_liquidity=ask_liquidity,
            concentration=concentration,
            resilience=resilience
        )
    
    def detect_whales(self) -> WhaleActivity:
        """Detect whale activity and large positions"""
        snapshot = self.get_current_snapshot()
        
        # Find large orders (>$10K)
        large_positions = []
        for price, size in snapshot.bids:
            value = price * size
            if value > 10000:
                large_positions.append({
                    'side': 'BID',
                    'price': price,
                    'size': size,
                    'value': value
                })
        
        for price, size in snapshot.asks:
            value = price * size
            if value > 10000:
                large_positions.append({
                    'side': 'ASK',
                    'price': price,
                    'size': size,
                    'value': value
                })
        
        # Sort by value
        large_positions.sort(key=lambda x: x['value'], reverse=True)
        
        # Top 10 positions
        top_10 = large_positions[:10]
        
        # Unusual volume detection
        total_value = sum(p * s for p, s in snapshot.bids + snapshot.asks)
        whale_value = sum(pos['value'] for pos in large_positions)
        whale_concentration = whale_value / total_value if total_value > 0 else 0
        unusual_volume = whale_concentration > 0.5  # Whales control >50% of book
        
        # Smart money score (based on position sizing, spread positioning)
        smart_money_score = 0
        spread = self.get_spread()
        
        for pos in top_10:
            # Positions closer to mid price = smarter
            distance_from_mid = abs(pos['price'] - spread.mid_price) / spread.mid_price
            position_score = max(0, 100 - distance_from_mid * 100)
            smart_money_score += position_score
        
        if top_10:
            smart_money_score = smart_money_score / len(top_10)
        
        return WhaleActivity(
            large_positions=large_positions,
            top_10_positions=top_10,
            unusual_volume=unusual_volume,
            smart_money_score=smart_money_score
        )
    
    def analyze_flow(self, timeframe_minutes: int = 60) -> Dict:
        """Analyze order flow and momentum"""
        # This would require historical trade data
        # For now, use order book imbalance as proxy
        
        imbalance = self.get_imbalance()
        spread = self.get_spread()
        
        # Momentum based on imbalance
        momentum = "BULLISH" if imbalance.net_pressure > 0.1 else "BEARISH" if imbalance.net_pressure < -0.1 else "NEUTRAL"
        
        # Reversal signals
        reversal_signals = []
        if imbalance.net_pressure > 0.5:
            reversal_signals.append("OVERBOUGHT - Potential sell pressure")
        elif imbalance.net_pressure < -0.5:
            reversal_signals.append("OVERSOLD - Potential buy pressure")
        
        if spread.spread_bps > 100:
            reversal_signals.append("WIDE SPREAD - Low confidence / volatility")
        
        return {
            'momentum': momentum,
            'net_pressure': imbalance.net_pressure,
            'signal': imbalance.signal,
            'reversal_signals': reversal_signals,
            'flow_strength': abs(imbalance.net_pressure) * 100
        }
    
    def get_time_weighted_spread(self, duration_minutes: int = 60) -> float:
        """Calculate time-weighted average spread"""
        if len(self.order_book_history) < 2:
            return self.get_spread().spread_bps
        
        cutoff_time = time.time() - (duration_minutes * 60)
        recent_snapshots = [s for s in self.order_book_history if s.timestamp > cutoff_time]
        
        if not recent_snapshots:
            return self.get_spread().spread_bps
        
        spreads = []
        for snapshot in recent_snapshots:
            if snapshot.bids and snapshot.asks:
                best_bid = snapshot.bids[0][0]
                best_ask = snapshot.asks[0][0]
                mid = (best_bid + best_ask) / 2
                spread_bps = ((best_ask - best_bid) / mid) * 10000 if mid > 0 else 0
                spreads.append(spread_bps)
        
        return statistics.mean(spreads) if spreads else 0
    
    def get_best_trading_times(self) -> Dict:
        """Analyze historical spreads to find best trading times"""
        if len(self.order_book_history) < 10:
            return {
                'status': 'insufficient_data',
                'message': 'Need more historical data'
            }
        
        # Group by hour
        spreads_by_hour = defaultdict(list)
        
        for snapshot in self.order_book_history:
            if snapshot.bids and snapshot.asks:
                hour = datetime.fromtimestamp(snapshot.timestamp).hour
                best_bid = snapshot.bids[0][0]
                best_ask = snapshot.asks[0][0]
                mid = (best_bid + best_ask) / 2
                spread_bps = ((best_ask - best_bid) / mid) * 10000 if mid > 0 else 0
                spreads_by_hour[hour].append(spread_bps)
        
        # Calculate average spread per hour
        avg_spreads = {
            hour: statistics.mean(spreads)
            for hour, spreads in spreads_by_hour.items()
        }
        
        if not avg_spreads:
            return {'status': 'no_data'}
        
        best_hour = min(avg_spreads, key=avg_spreads.get)
        worst_hour = max(avg_spreads, key=avg_spreads.get)
        
        return {
            'best_hour': best_hour,
            'best_spread_bps': avg_spreads[best_hour],
            'worst_hour': worst_hour,
            'worst_spread_bps': avg_spreads[worst_hour],
            'all_hours': avg_spreads
        }
    
    def full_analysis(self) -> Dict:
        """Run complete market microstructure analysis"""
        self.refresh_order_book()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'market_id': self.token_id,
            'spread': asdict(self.get_spread()),
            'imbalance': asdict(self.get_imbalance()),
            'liquidity': asdict(self.get_liquidity_metrics()),
            'depth_profile': self.get_depth_profile(),
            'price_impact_1k': asdict(self.estimate_impact(1000, 'buy')),
            'price_impact_5k': asdict(self.estimate_impact(5000, 'buy')),
            'whales': asdict(self.detect_whales()),
            'flow': self.analyze_flow(),
            'time_weighted_spread_1h': self.get_time_weighted_spread(60)
        }


def print_analysis(analysis: Dict):
    """Pretty print analysis results"""
    print("\n" + "="*70)
    print(f"MARKET MICROSTRUCTURE ANALYSIS - {analysis['timestamp']}")
    print(f"Market ID: {analysis['market_id']}")
    print("="*70)
    
    # Spread
    spread = analysis['spread']
    print(f"\n📊 SPREAD METRICS:")
    print(f"  Mid Price: ${spread['mid_price']:.4f}")
    print(f"  Spread: ${spread['spread_abs']:.4f} ({spread['spread_bps']:.1f} bps)")
    print(f"  Best Bid: ${spread['best_bid']:.4f}")
    print(f"  Best Ask: ${spread['best_ask']:.4f}")
    
    # Imbalance
    imbalance = analysis['imbalance']
    print(f"\n⚖️  ORDER BOOK IMBALANCE:")
    print(f"  Signal: {imbalance['signal']}")
    print(f"  Net Pressure: {imbalance['net_pressure']:+.2%}")
    print(f"  Bid/Ask Ratio: {imbalance['ratio']:.2f}")
    
    # Liquidity
    liquidity = analysis['liquidity']
    print(f"\n💧 LIQUIDITY METRICS:")
    print(f"  Liquidity Score: {liquidity['score']:.1f}/100")
    print(f"  Total Liquidity: ${liquidity['total_liquidity']:,.0f}")
    print(f"  Bid Liquidity: ${liquidity['bid_liquidity']:,.0f}")
    print(f"  Ask Liquidity: ${liquidity['ask_liquidity']:,.0f}")
    print(f"  Resilience: {liquidity['resilience']:.1%}")
    
    # Price Impact
    impact_1k = analysis['price_impact_1k']
    print(f"\n💥 PRICE IMPACT (for $1K order):")
    print(f"  Estimated Price: ${impact_1k['estimated_price']:.4f}")
    print(f"  Slippage: {impact_1k['slippage_pct']:.2f}%")
    print(f"  Optimal Order Size (<1% slippage): ${impact_1k['optimal_size']:,.0f}")
    
    # Whales
    whales = analysis['whales']
    print(f"\n🐋 WHALE ACTIVITY:")
    print(f"  Large Positions (>$10K): {len(whales['large_positions'])}")
    print(f"  Smart Money Score: {whales['smart_money_score']:.1f}/100")
    print(f"  Unusual Volume: {'⚠️  YES' if whales['unusual_volume'] else 'No'}")
    
    if whales['top_10_positions']:
        print(f"\n  Top 3 Positions:")
        for i, pos in enumerate(whales['top_10_positions'][:3], 1):
            print(f"    {i}. {pos['side']}: ${pos['value']:,.0f} @ ${pos['price']:.4f}")
    
    # Flow
    flow = analysis['flow']
    print(f"\n🌊 FLOW ANALYSIS:")
    print(f"  Momentum: {flow['momentum']}")
    print(f"  Flow Strength: {flow['flow_strength']:.1f}/100")
    if flow['reversal_signals']:
        print(f"  ⚠️  Reversal Signals:")
        for signal in flow['reversal_signals']:
            print(f"    - {signal}")
    
    # Trading recommendation
    print(f"\n💡 TRADING INSIGHT:")
    if liquidity['score'] < 30:
        print(f"  ⚠️  LOW LIQUIDITY - High slippage risk, use limit orders")
    elif liquidity['score'] > 70:
        print(f"  ✅ GOOD LIQUIDITY - Favorable trading conditions")
    
    if spread['spread_bps'] > 50:
        print(f"  ⚠️  WIDE SPREAD - Consider waiting for tighter markets")
    
    if imbalance['signal'] == "BUY_PRESSURE":
        print(f"  📈 Strong buying pressure - Price may move up")
    elif imbalance['signal'] == "SELL_PRESSURE":
        print(f"  📉 Strong selling pressure - Price may move down")
    
    print("\n" + "="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Market Microstructure Analyzer for Polymarket',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python market-microstructure.py --market TOKEN_ID
  python market-microstructure.py --market TOKEN_ID --whales
  python market-microstructure.py --market TOKEN_ID --liquidity
  python market-microstructure.py --market TOKEN_ID --impact 5000
  python market-microstructure.py --market TOKEN_ID --monitor 60
        """
    )
    
    parser.add_argument('--market', type=str, help='Market token ID to analyze')
    parser.add_argument('--whales', action='store_true', help='Show whale activity')
    parser.add_argument('--liquidity', action='store_true', help='Show liquidity report')
    parser.add_argument('--impact', type=float, help='Estimate price impact for USD amount')
    parser.add_argument('--flow', action='store_true', help='Show flow analysis')
    parser.add_argument('--monitor', type=int, help='Monitor mode (refresh every N seconds)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.market:
        parser.print_help()
        print("\n⚠️  Error: --market TOKEN_ID is required")
        return 1
    
    try:
        analyzer = MarketAnalyzer(args.market)
        
        # Monitor mode
        if args.monitor:
            print(f"📡 Monitoring market {args.market} (refresh every {args.monitor}s)")
            print("Press Ctrl+C to stop\n")
            
            while True:
                analysis = analyzer.full_analysis()
                
                if args.json:
                    print(json.dumps(analysis, indent=2))
                else:
                    print_analysis(analysis)
                
                time.sleep(args.monitor)
        
        # Single analysis
        else:
            if args.whales:
                whales = analyzer.detect_whales()
                if args.json:
                    print(json.dumps(asdict(whales), indent=2))
                else:
                    print("\n🐋 WHALE ACTIVITY REPORT\n")
                    print(f"Large Positions (>$10K): {len(whales.large_positions)}")
                    print(f"Smart Money Score: {whales.smart_money_score:.1f}/100")
                    print(f"Unusual Volume: {whales.unusual_volume}\n")
                    
                    print("Top 10 Positions:")
                    for i, pos in enumerate(whales.top_10_positions, 1):
                        print(f"{i:2d}. {pos['side']:3s} ${pos['value']:>10,.0f} @ ${pos['price']:.4f}")
            
            elif args.liquidity:
                liquidity = analyzer.get_liquidity_metrics()
                if args.json:
                    print(json.dumps(asdict(liquidity), indent=2))
                else:
                    print("\n💧 LIQUIDITY REPORT\n")
                    print(f"Liquidity Score: {liquidity.score:.1f}/100")
                    print(f"Total Liquidity: ${liquidity.total_liquidity:,.0f}")
                    print(f"  Bid Side: ${liquidity.bid_liquidity:,.0f}")
                    print(f"  Ask Side: ${liquidity.ask_liquidity:,.0f}")
                    print(f"Concentration: {liquidity.concentration:.3f} (lower = better)")
                    print(f"Resilience: {liquidity.resilience:.1%}")
            
            elif args.impact:
                impact = analyzer.estimate_impact(args.impact, 'buy')
                if args.json:
                    print(json.dumps(asdict(impact), indent=2))
                else:
                    print(f"\n💥 PRICE IMPACT ANALYSIS (${args.impact:,.0f} order)\n")
                    print(f"Estimated Fill Price: ${impact.estimated_price:.4f}")
                    print(f"Slippage: {impact.slippage_pct:.2f}% (${impact.slippage_abs:.4f})")
                    print(f"Optimal Size (<1% slippage): ${impact.optimal_size:,.0f}")
            
            elif args.flow:
                flow = analyzer.analyze_flow()
                if args.json:
                    print(json.dumps(flow, indent=2))
                else:
                    print("\n🌊 FLOW ANALYSIS\n")
                    print(f"Momentum: {flow['momentum']}")
                    print(f"Net Pressure: {flow['net_pressure']:+.2%}")
                    print(f"Signal: {flow['signal']}")
                    print(f"Flow Strength: {flow['flow_strength']:.1f}/100")
                    
                    if flow['reversal_signals']:
                        print("\n⚠️  Reversal Signals:")
                        for signal in flow['reversal_signals']:
                            print(f"  - {signal}")
            
            else:
                # Full analysis
                analysis = analyzer.full_analysis()
                
                if args.json:
                    print(json.dumps(analysis, indent=2))
                else:
                    print_analysis(analysis)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n👋 Stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
