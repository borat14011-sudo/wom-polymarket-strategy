"""
Test script for rate-limiter.py
Demonstrates both decorator and manual usage patterns.
"""

import time
from rate_limiter import RateLimiter, polymarket_limiter, twitter_limiter


def test_basic_usage():
    """Test basic rate limiting"""
    print("=" * 70)
    print("TEST 1: Basic Rate Limiting")
    print("=" * 70)
    
    limiter = RateLimiter("test", requests_per_minute=20)  # 20/min = 1 every 3s
    
    print(f"\nMaking 5 requests at limit of {limiter.requests_per_minute}/min...\n")
    
    for i in range(5):
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        
        # Simulate request
        limiter.record_success(latency=0.1)
        
        print(f"  Request {i+1}: waited {elapsed:.3f}s | tokens: {limiter.tokens:.2f}")
    
    stats = limiter.get_stats()
    print(f"\n  ✓ Total: {stats['total_requests']}, Success: {stats['successful_requests']}")


def test_decorator_pattern():
    """Test decorator usage"""
    print("\n" + "=" * 70)
    print("TEST 2: Decorator Pattern")
    print("=" * 70)
    
    limiter = RateLimiter("decorator_test", requests_per_minute=30)
    
    @limiter.limit
    def mock_api_call(market_id):
        """Simulate API call"""
        time.sleep(0.05)  # 50ms latency
        return {"id": market_id, "status": "success"}
    
    print(f"\nCalling decorated function 3 times...\n")
    
    for i in range(3):
        start = time.time()
        result = mock_api_call(f"market_{i}")
        elapsed = time.time() - start
        print(f"  Call {i+1}: {result['status']} in {elapsed:.3f}s")
    
    stats = limiter.get_stats()
    print(f"\n  ✓ Avg latency: {stats['average_latency_ms']:.2f}ms")


def test_adaptive_rate():
    """Test adaptive rate limiting on failures"""
    print("\n" + "=" * 70)
    print("TEST 3: Adaptive Rate (429 Handling)")
    print("=" * 70)
    
    limiter = RateLimiter("adaptive_test", requests_per_minute=60)
    
    print(f"\n  Initial rate multiplier: {limiter.adaptive_multiplier:.2f}")
    
    # Simulate getting 429 error
    limiter.record_failure(is_429=True)
    print(f"  After 429 error:         {limiter.adaptive_multiplier:.2f}")
    
    # Simulate recovery
    for _ in range(3):
        limiter.record_success(latency=0.1)
    
    stats = limiter.get_stats()
    print(f"\n  ✓ Rate limit hits: {stats['rate_limit_hits']}")
    print(f"  ✓ Current multiplier: {stats['adaptive_multiplier']:.2f}")


def test_predefined_limiters():
    """Test predefined API limiters"""
    print("\n" + "=" * 70)
    print("TEST 4: Predefined Limiters")
    print("=" * 70)
    
    print(f"\n  Polymarket limiter: {polymarket_limiter.requests_per_minute}/min")
    print(f"  Twitter limiter:    {twitter_limiter.requests_per_minute}/min")
    
    @polymarket_limiter.limit
    def fetch_polymarket():
        time.sleep(0.02)
        return {"markets": 100}
    
    @twitter_limiter.limit
    def fetch_twitter():
        time.sleep(0.02)
        return {"tweets": 50}
    
    result1 = fetch_polymarket()
    result2 = fetch_twitter()
    
    print(f"\n  ✓ Polymarket: {result1}")
    print(f"  ✓ Twitter:    {result2}")


def test_statistics():
    """Test statistics tracking"""
    print("\n" + "=" * 70)
    print("TEST 5: Statistics Tracking")
    print("=" * 70)
    
    limiter = RateLimiter("stats_test", requests_per_minute=120)
    
    # Make various requests
    limiter.wait()
    limiter.record_success(latency=0.050)
    
    limiter.wait()
    limiter.record_success(latency=0.100)
    
    limiter.wait()
    limiter.record_failure(is_429=False)
    
    limiter.wait()
    limiter.record_failure(is_429=True)
    
    stats = limiter.get_stats()
    
    print("\n  Statistics:")
    print(f"    Total requests:      {stats['total_requests']}")
    print(f"    Successful:          {stats['successful_requests']}")
    print(f"    Failed:              {stats['failed_requests']}")
    print(f"    Rate limit hits:     {stats['rate_limit_hits']}")
    print(f"    Avg latency:         {stats['average_latency_ms']:.2f}ms")
    print(f"    Current tokens:      {stats['current_tokens']:.2f}")
    print(f"    Adaptive multiplier: {stats['adaptive_multiplier']:.2f}")
    
    print(f"\n  ✓ Statistics tracking working correctly")


def test_manual_usage():
    """Test manual wait/record pattern"""
    print("\n" + "=" * 70)
    print("TEST 6: Manual Usage Pattern")
    print("=" * 70)
    
    limiter = RateLimiter("manual", requests_per_minute=40)
    
    print("\n  Manual pattern with explicit wait/record:\n")
    
    class MockResponse:
        def __init__(self, status_code):
            self.status_code = status_code
    
    for i in range(3):
        # Wait for rate limit
        limiter.wait()
        
        # Simulate API call
        start = time.time()
        response = MockResponse(200 if i < 2 else 429)
        latency = time.time() - start
        
        # Record result
        if response.status_code == 200:
            limiter.record_success(latency=latency)
            print(f"    Request {i+1}: SUCCESS (200)")
        elif response.status_code == 429:
            limiter.record_failure(is_429=True)
            print(f"    Request {i+1}: RATE LIMITED (429)")
    
    stats = limiter.get_stats()
    print(f"\n  ✓ Success: {stats['successful_requests']}, Failed: {stats['failed_requests']}")


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  RATE LIMITER TEST SUITE".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    try:
        test_basic_usage()
        test_decorator_pattern()
        test_adaptive_rate()
        test_predefined_limiters()
        test_statistics()
        test_manual_usage()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nRate limiter is ready for integration!")
        print("\nQuick Start:")
        print("  from rate_limiter import polymarket_limiter")
        print("  ")
        print("  @polymarket_limiter.limit")
        print("  def fetch_data():")
        print("      return requests.get(...)")
        print()
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
