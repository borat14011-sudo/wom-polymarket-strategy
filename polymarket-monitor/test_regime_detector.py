"""
Test script for market regime detector.
Run this to verify the detector is working correctly.
"""

from market_regime_detector import MarketRegimeDetector, MarketRegime, is_tradeable, check_regime


def test_basic_functionality():
    """Test basic detector functionality"""
    print("="*60)
    print("Testing Market Regime Detector")
    print("="*60 + "\n")
    
    detector = MarketRegimeDetector()
    
    # Test 1: Get summary
    print("📊 Test 1: Market Summary")
    print("-"*60)
    summary = detector.get_market_summary()
    print(summary)
    print()
    
    # Test 2: Individual coin checks
    print("\n📈 Test 2: Individual Coin Analysis")
    print("-"*60)
    for coin in ["BTC", "ETH", "SOL"]:
        try:
            data = detector.get_regime_data(coin)
            print(f"\n{coin}:")
            print(f"  Regime: {data.regime.value}")
            print(f"  Price: ${data.current_price:,.2f}")
            print(f"  Changes: 7d={data.price_change_7d:+.1f}%, 14d={data.price_change_14d:+.1f}%, 30d={data.price_change_30d:+.1f}%")
            print(f"  30-day Avg: ${data.avg_price_30d:,.2f}")
            print(f"  Tradeable for FADE_BULL: {'✅ YES' if detector.is_tradeable_regime(coin) else '🚫 NO'}")
        except Exception as e:
            print(f"\n{coin}: ❌ Error - {e}")
    
    # Test 3: Quick convenience functions
    print("\n\n🔧 Test 3: Convenience Functions")
    print("-"*60)
    for coin in ["BTC", "ETH", "SOL"]:
        try:
            regime = check_regime(coin)
            tradeable = is_tradeable(coin)
            print(f"{coin}: {regime.value} - Tradeable: {tradeable}")
        except Exception as e:
            print(f"{coin}: Error - {e}")
    
    # Test 4: Cache verification
    print("\n\n⚡ Test 4: Cache Performance")
    print("-"*60)
    import time
    
    start = time.time()
    detector.get_all_regimes()
    first_call = time.time() - start
    
    start = time.time()
    detector.get_all_regimes()
    cached_call = time.time() - start
    
    print(f"First call: {first_call:.2f}s")
    print(f"Cached call: {cached_call:.2f}s")
    print(f"Speedup: {first_call/cached_call:.1f}x faster")
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)


if __name__ == "__main__":
    test_basic_functionality()
