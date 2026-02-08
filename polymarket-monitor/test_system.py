"""
Test script to verify all components work
"""
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_database():
    """Test database initialization"""
    logger.info("Testing database...")
    try:
        from database import init_database
        init_database()
        logger.info("✅ Database test passed")
        return True
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        return False

def test_scraper():
    """Test market scraping"""
    logger.info("Testing scraper...")
    try:
        from polymarket_scraper import fetch_trending_markets
        markets = fetch_trending_markets(limit=5)
        if markets:
            logger.info(f"✅ Scraper test passed ({len(markets)} markets fetched)")
            return True
        else:
            logger.warning("⚠️  Scraper returned no markets")
            return False
    except Exception as e:
        logger.error(f"❌ Scraper test failed: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    logger.info("Testing dependencies...")
    try:
        import requests
        import schedule
        import sqlite3
        logger.info("✅ Dependencies test passed")
        return True
    except ImportError as e:
        logger.error(f"❌ Missing dependency: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("POLYMARKET MONITOR - SYSTEM TEST")
    print("=" * 60)
    print()
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Database", test_database),
        ("Scraper", test_scraper),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"Running {name} test...")
        result = test_func()
        results.append(result)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL TESTS PASSED ({passed}/{total})")
        print()
        print("System is ready! Run: python monitor_daemon.py")
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed}/{total})")
        print()
        print("Please fix the issues above before running the monitor")
        sys.exit(1)
    
    print("=" * 60)

if __name__ == "__main__":
    main()
