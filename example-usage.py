#!/usr/bin/env python3
"""
Example usage of Market Microstructure Analyzer
Demonstrates integration patterns for professional traders
"""

from market_microstructure import MarketAnalyzer
import time


def example_basic_analysis():
    """Basic market analysis"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Market Analysis")
    print("="*70)
    
    # Replace with actual Polymarket token ID
    # Example: "21742633143463906290569050155826241533067272736897614950488156847949938836455"
    market_id = "YOUR_TOKEN_ID_HERE"
    
    analyzer = MarketAnalyzer(market_id)
    
    # Get current spread
    spread = analyzer.get_spread()
    print(f"\nCurrent spread: {spread.spread_bps:.1f} bps")
    print(f"Mid price: ${spread.mid_price:.4f}")
    
    # Check liquidity
    liquidity = analyzer.get_liquidity_metrics()
    print(f"\nLiquidity score: {liquidity.score:.1f}/100")
    print(f"Total liquidity: ${liquidity.total_liquidity:,.0f}")
    
    # Estimate price impact
    impact = analyzer.estimate_impact(1000)
    print(f"\nPrice impact for $1K order:")
    print(f"  Slippage: {impact.slippage_pct:.2f}%")
    print(f"  Optimal size: ${impact.optimal_size:,.0f}")


def example_whale_tracker():
    """Track whale activity"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Whale Activity Tracker")
    print("="*70)
    
    market_id = "YOUR_TOKEN_ID_HERE"
    analyzer = MarketAnalyzer(market_id)
    
    whales = analyzer.detect_whales()
    
    print(f"\n🐋 Found {len(whales.large_positions)} large positions (>$10K)")
    print(f"Smart money score: {whales.smart_money_score:.1f}/100")
    
    if whales.unusual_volume:
        print("⚠️  ALERT: Unusual whale activity detected!")
    
    print("\nTop 5 positions:")
    for i, pos in enumerate(whales.top_10_positions[:5], 1):
        side_emoji = "🟢" if pos['side'] == 'BID' else "🔴"
        print(f"  {i}. {side_emoji} {pos['side']}: ${pos['value']:>10,.0f} @ ${pos['price']:.4f}")


def example_trading_signals():
    """Generate trading signals"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Trading Signal Generator")
    print("="*70)
    
    market_id = "YOUR_TOKEN_ID_HERE"
    analyzer = MarketAnalyzer(market_id)
    
    # Get multiple metrics
    spread = analyzer.get_spread()
    imbalance = analyzer.get_imbalance()
    liquidity = analyzer.get_liquidity_metrics()
    flow = analyzer.analyze_flow()
    
    print("\n📊 Market Conditions:")
    print(f"  Spread: {spread.spread_bps:.1f} bps")
    print(f"  Liquidity: {liquidity.score:.1f}/100")
    print(f"  Flow: {flow['momentum']}")
    print(f"  Pressure: {imbalance.signal}")
    
    # Generate signal
    print("\n🎯 Trading Signal:")
    
    if liquidity.score < 40:
        print("  ⚠️  AVOID - Low liquidity, high slippage risk")
    elif spread.spread_bps > 100:
        print("  ⚠️  WAIT - Spread too wide, poor execution quality")
    elif imbalance.signal == "BUY_PRESSURE" and flow['momentum'] == "BULLISH":
        print("  ✅ BULLISH - Strong buying pressure, consider long position")
        print(f"     Confidence: {flow['flow_strength']:.0f}/100")
    elif imbalance.signal == "SELL_PRESSURE" and flow['momentum'] == "BEARISH":
        print("  ✅ BEARISH - Strong selling pressure, consider short position")
        print(f"     Confidence: {flow['flow_strength']:.0f}/100")
    else:
        print("  ⏸️  NEUTRAL - No clear signal, wait for better setup")


def example_order_optimizer():
    """Optimize order execution"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Smart Order Execution")
    print("="*70)
    
    market_id = "YOUR_TOKEN_ID_HERE"
    analyzer = MarketAnalyzer(market_id)
    
    # Want to buy $10,000 worth
    target_size = 10000
    
    print(f"\nTarget order size: ${target_size:,.0f}")
    
    # Analyze impact
    impact = analyzer.estimate_impact(target_size)
    
    print(f"\nSingle order execution:")
    print(f"  Expected price: ${impact.estimated_price:.4f}")
    print(f"  Slippage: {impact.slippage_pct:.2f}%")
    
    if impact.slippage_pct > 1.0:
        # Calculate optimal split
        optimal = impact.optimal_size
        num_chunks = int(target_size / optimal) + 1
        chunk_size = target_size / num_chunks
        
        print(f"\n💡 Recommendation: SPLIT ORDER")
        print(f"  Optimal chunk size: ${optimal:,.0f}")
        print(f"  Suggested split: {num_chunks} orders of ${chunk_size:,.0f}")
        print(f"  Expected slippage reduction: {impact.slippage_pct - 1.0:.2f}%")
    else:
        print(f"\n✅ Single order execution is optimal")


def example_market_monitor():
    """Real-time market monitoring"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Real-Time Market Monitor")
    print("="*70)
    print("\nMonitoring for 2 minutes (updates every 10s)...")
    print("Press Ctrl+C to stop\n")
    
    market_id = "YOUR_TOKEN_ID_HERE"
    analyzer = MarketAnalyzer(market_id)
    
    try:
        for i in range(12):  # 2 minutes
            analyzer.refresh_order_book()
            
            spread = analyzer.get_spread()
            imbalance = analyzer.get_imbalance()
            liquidity = analyzer.get_liquidity_metrics()
            
            timestamp = time.strftime("%H:%M:%S")
            
            print(f"[{timestamp}] "
                  f"Spread: {spread.spread_bps:>5.1f}bps | "
                  f"Liq: {liquidity.score:>4.1f} | "
                  f"Pressure: {imbalance.net_pressure:>+6.1%} | "
                  f"Signal: {imbalance.signal}")
            
            # Alert on significant changes
            if liquidity.score < 30:
                print("         ⚠️  ALERT: Liquidity dropped significantly!")
            
            if abs(imbalance.net_pressure) > 0.5:
                print("         ⚠️  ALERT: Extreme order book imbalance!")
            
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def example_multi_market_scanner():
    """Scan multiple markets for opportunities"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Multi-Market Scanner")
    print("="*70)
    
    # List of markets to monitor
    markets = [
        "MARKET_1_TOKEN_ID",
        "MARKET_2_TOKEN_ID", 
        "MARKET_3_TOKEN_ID"
    ]
    
    print("\nScanning markets for trading opportunities...\n")
    
    opportunities = []
    
    for market_id in markets:
        try:
            analyzer = MarketAnalyzer(market_id)
            
            spread = analyzer.get_spread()
            imbalance = analyzer.get_imbalance()
            liquidity = analyzer.get_liquidity_metrics()
            
            # Score the opportunity
            score = 0
            
            # Good liquidity
            if liquidity.score > 70:
                score += 30
            
            # Tight spread
            if spread.spread_bps < 50:
                score += 25
            
            # Strong directional signal
            if abs(imbalance.net_pressure) > 0.2:
                score += 25
            
            # High total liquidity
            if liquidity.total_liquidity > 50000:
                score += 20
            
            if score > 60:
                opportunities.append({
                    'market_id': market_id,
                    'score': score,
                    'spread': spread.spread_bps,
                    'liquidity': liquidity.score,
                    'signal': imbalance.signal,
                    'pressure': imbalance.net_pressure
                })
        
        except Exception as e:
            print(f"  ⚠️  Error analyzing {market_id[:16]}...: {e}")
    
    # Sort by score
    opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    if opportunities:
        print("🎯 Top Trading Opportunities:\n")
        for i, opp in enumerate(opportunities[:5], 1):
            print(f"{i}. Market: {opp['market_id'][:16]}...")
            print(f"   Score: {opp['score']}/100")
            print(f"   Spread: {opp['spread']:.1f}bps | Liquidity: {opp['liquidity']:.1f}")
            print(f"   Signal: {opp['signal']} ({opp['pressure']:+.1%})")
            print()
    else:
        print("No opportunities found matching criteria.")


def example_risk_management():
    """Risk assessment for position sizing"""
    print("\n" + "="*70)
    print("EXAMPLE 7: Risk Management & Position Sizing")
    print("="*70)
    
    market_id = "YOUR_TOKEN_ID_HERE"
    analyzer = MarketAnalyzer(market_id)
    
    # Account parameters
    account_size = 100000  # $100K
    max_risk_per_trade = 0.02  # 2%
    max_position_size = account_size * max_risk_per_trade
    
    print(f"\nAccount size: ${account_size:,.0f}")
    print(f"Max risk per trade: {max_risk_per_trade:.1%} (${max_position_size:,.0f})")
    
    # Analyze market conditions
    liquidity = analyzer.get_liquidity_metrics()
    impact = analyzer.estimate_impact(max_position_size)
    spread = analyzer.get_spread()
    
    print(f"\nMarket Analysis:")
    print(f"  Liquidity score: {liquidity.score:.1f}/100")
    print(f"  Total liquidity: ${liquidity.total_liquidity:,.0f}")
    print(f"  Current spread: {spread.spread_bps:.1f}bps")
    
    # Calculate safe position size
    safe_size = min(
        max_position_size,
        liquidity.total_liquidity * 0.1,  # Max 10% of total liquidity
        impact.optimal_size  # Stay within 1% slippage
    )
    
    print(f"\n💡 Recommended Position Size: ${safe_size:,.0f}")
    print(f"   Reasoning:")
    
    if safe_size == max_position_size:
        print(f"   - Within risk limits")
    else:
        print(f"   - Reduced from ${max_position_size:,.0f} due to:")
        
        if safe_size == liquidity.total_liquidity * 0.1:
            print(f"     * Liquidity constraints (10% rule)")
        
        if safe_size == impact.optimal_size:
            print(f"     * Slippage constraints (<1% rule)")
    
    # Expected costs
    expected_cost = (spread.spread_abs / 2) * (safe_size / spread.mid_price)
    print(f"\n💰 Expected Transaction Costs:")
    print(f"   Half-spread cost: ${expected_cost:.2f}")
    print(f"   As % of position: {(expected_cost / safe_size * 100):.3f}%")


def main():
    """Run all examples"""
    print("\n" + "="*70)
    print("MARKET MICROSTRUCTURE ANALYZER - EXAMPLE USAGE")
    print("="*70)
    print("\nNOTE: Replace 'YOUR_TOKEN_ID_HERE' with actual Polymarket token IDs")
    print("      to run these examples with real data.")
    print("\n" + "="*70)
    
    examples = [
        ("Basic Analysis", example_basic_analysis),
        ("Whale Tracker", example_whale_tracker),
        ("Trading Signals", example_trading_signals),
        ("Order Optimizer", example_order_optimizer),
        ("Market Monitor", example_market_monitor),
        ("Multi-Market Scanner", example_multi_market_scanner),
        ("Risk Management", example_risk_management)
    ]
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\nTo run a specific example, edit this file and call the function directly.")
    print("Example: python example-usage.py")
    
    # Uncomment to run specific examples:
    # example_basic_analysis()
    # example_whale_tracker()
    # example_trading_signals()
    # example_order_optimizer()
    # example_market_monitor()
    # example_multi_market_scanner()
    # example_risk_management()


if __name__ == '__main__':
    main()
