"""
Integration test for historical price tracking system
Verifies database, scraper, and signal detector work together
"""

import sys
import logging
from datetime import datetime, timedelta

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_database():
    """Test database initialization and basic operations"""
    print("\n" + "=" * 60)
    print("TEST 1: Database Operations")
    print("=" * 60)
    
    try:
        from historical_db import HistoricalDB
        
        # Initialize test database
        db = HistoricalDB("test_history.db")
        
        # Test store snapshot
        print("✓ Database initialized")
        
        test_market_id = "test_market_123"
        now = datetime.now()
        
        # Store snapshots for last 48 hours
        snapshots = []
        for hours_ago in range(48, 0, -1):
            ts = int((now - timedelta(hours=hours_ago)).timestamp())
            price = 0.5 + (hours_ago * 0.001)  # Slight downward trend
            volume = 10000 + (hours_ago * 100)
            snapshots.append((test_market_id, price, 1 - price, volume, ts))
        
        db.store_snapshots_batch(snapshots)
        print(f"✓ Stored {len(snapshots)} test snapshots")
        
        # Test 24h lookup
        price_24h = db.get_price_24h_ago(test_market_id)
        volume_24h = db.get_volume_24h_ago(test_market_id)
        
        assert price_24h is not None, "Failed to retrieve 24h price"
        assert volume_24h is not None, "Failed to retrieve 24h volume"
        
        print(f"✓ 24h price lookup: {price_24h:.4f}")
        print(f"✓ 24h volume lookup: {volume_24h:.0f}")
        
        # Test full history
        history = db.get_price_history(test_market_id, hours=48)
        assert len(history) > 0, "Failed to retrieve price history"
        print(f"✓ Price history: {len(history)} snapshots")
        
        # Test stats
        stats = db.get_stats()
        print(f"✓ Database stats: {stats['num_markets']} markets, {stats['num_snapshots']} snapshots")
        
        print("\n✅ DATABASE TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ DATABASE TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_scraper():
    """Test scraper functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Scraper (Live API)")
    print("=" * 60)
    
    try:
        from historical_scraper import PolymarketScraper
        
        scraper = PolymarketScraper()
        print("✓ Scraper initialized")
        
        # Run test scrape (10 markets)
        num_stored = scraper.scrape_and_store(limit=10)
        
        assert num_stored > 0, "Scraper stored 0 snapshots"
        print(f"✓ Scraped and stored {num_stored} market snapshots")
        
        # Verify data is in database
        from historical_db import get_db
        db = get_db()
        stats = db.get_stats()
        
        assert stats['num_snapshots'] >= num_stored, "Snapshots not in database"
        print(f"✓ Verified snapshots in database: {stats['num_snapshots']} total")
        
        print("\n✅ SCRAPER TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ SCRAPER TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_detector():
    """Test signal detector integration"""
    print("\n" + "=" * 60)
    print("TEST 3: Signal Detector Integration")
    print("=" * 60)
    
    try:
        from signal_detector_v2 import SignalDetectorV2
        from historical_db import get_db
        
        detector = SignalDetectorV2()
        print("✓ Signal detector initialized")
        
        # Check database has data
        db = get_db()
        stats = db.get_stats()
        
        if stats['num_snapshots'] == 0:
            print("⚠️  No historical data in database yet")
            print("   Run test_scraper() first or wait 24h for production data")
            return None
        
        print(f"✓ Database has {stats['num_snapshots']} snapshots for {stats['num_markets']} markets")
        
        # Test historical data lookup
        import requests
        response = requests.get(
            "https://gamma-api.polymarket.com/markets",
            params={'limit': 5, 'active': True},
            timeout=10
        )
        
        if response.status_code == 200:
            markets = response.json()
            print(f"✓ Fetched {len(markets)} test markets from API")
            
            found_historical = 0
            for market in markets[:5]:
                market_id = market.get('id')
                hist_data = detector._get_historical_data(market_id)
                
                if hist_data and hist_data['price_24h_ago'] is not None:
                    found_historical += 1
                    print(f"✓ Found historical data for {market.get('question', 'Unknown')[:50]}")
            
            if found_historical == 0:
                print("⚠️  No historical data found for test markets")
                print("   This is normal if database is <24h old")
            else:
                print(f"✓ Historical lookup working: {found_historical}/{len(markets)} markets have data")
        
        print("\n✅ SIGNAL DETECTOR TESTS PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ SIGNAL DETECTOR TESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print("HISTORICAL PRICE TRACKING SYSTEM - INTEGRATION TESTS")
    print("=" * 60)
    
    results = {}
    
    # Test 1: Database
    results['database'] = test_database()
    
    # Test 2: Scraper (requires internet)
    results['scraper'] = test_scraper()
    
    # Test 3: Signal detector integration
    results['signal_detector'] = test_signal_detector()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else ("⚠️  SKIP" if passed is None else "❌ FAIL")
        print(f"{test_name.upper()}: {status}")
    
    all_passed = all(v is not False for v in results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("\nNext steps:")
        print("1. Setup automated scraping (see HISTORICAL_DATABASE.md)")
        print("2. Wait 24 hours for data to accumulate")
        print("3. Run signal_detector_v2.py to see real signals")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("Check errors above and review HISTORICAL_DATABASE.md")
        return 1


if __name__ == "__main__":
    sys.exit(main())
