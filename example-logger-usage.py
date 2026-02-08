#!/usr/bin/env python3
"""
Example usage of the Advanced Logging System

Demonstrates various logging scenarios for the Polymarket trading system.
"""

import time
import random
from advanced_logger import get_logger


def simulate_data_collector():
    """Simulate a data collection component."""
    logger = get_logger("data-collector")
    
    print("=== Data Collector Example ===")
    
    # Basic info logging
    logger.info("Starting market data collection")
    
    # Logging with metrics
    start = time.time()
    time.sleep(0.1)  # Simulate API call
    latency_ms = (time.time() - start) * 1000
    
    markets_count = random.randint(10, 20)
    logger.info("Fetched markets", metrics={
        "markets": markets_count,
        "latency_ms": latency_ms
    })
    
    # Debug logging
    logger.debug("Processing market data", metrics={"markets_processed": 5})
    
    # Warning
    logger.warning("Rate limit approaching", metrics={"requests_remaining": 10})
    
    print("✓ Data collector logs written\n")


def simulate_strategy_engine():
    """Simulate a trading strategy component."""
    logger = get_logger("strategy-engine")
    
    print("=== Strategy Engine Example ===")
    
    logger.info("Strategy engine initialized")
    
    # Simulate some trades
    for i in range(3):
        logger.info(f"Evaluating trade opportunity {i+1}", metrics={
            "confidence": random.uniform(0.6, 0.95),
            "expected_return": random.uniform(0.05, 0.15)
        })
    
    # Simulate a successful trade
    logger.info("Trade executed", metrics={
        "market": "CRYPTO-BTC-100K",
        "side": "YES",
        "amount": 100.0,
        "price": 0.65
    })
    
    print("✓ Strategy engine logs written\n")


def simulate_database_operations():
    """Simulate database operations with performance tracking."""
    logger = get_logger("database")
    
    print("=== Database Operations Example ===")
    
    # Simulate queries with latency tracking
    operations = [
        ("SELECT markets", 45.2),
        ("INSERT trade", 23.1),
        ("UPDATE position", 12.8),
        ("SELECT portfolio", 89.5)
    ]
    
    for operation, latency in operations:
        logger.info(f"Database query: {operation}", metrics={
            "latency_ms": latency,
            "rows": random.randint(1, 100)
        })
    
    print("✓ Database logs written\n")


def simulate_error_handling():
    """Simulate error scenarios."""
    logger = get_logger("api-client")
    
    print("=== Error Handling Example ===")
    
    # Simulate an API error
    try:
        raise ConnectionError("Failed to connect to Polymarket API")
    except Exception as e:
        logger.error("API connection failed", exception=e, metrics={
            "retry_count": 3,
            "timeout_ms": 5000
        })
    
    # Critical error
    try:
        raise ValueError("Invalid market ID format")
    except Exception as e:
        logger.critical("Critical validation error", exception=e)
    
    print("✓ Error logs written\n")


def simulate_performance_monitoring():
    """Simulate system performance monitoring."""
    logger = get_logger("monitor")
    
    print("=== Performance Monitoring Example ===")
    
    # Memory usage (simulated)
    memory_values = [125.5, 128.3, 142.1, 138.9]
    
    for memory_mb in memory_values:
        logger.info("System health check", metrics={
            "memory_mb": memory_mb,
            "cpu_percent": random.uniform(10, 40),
            "active_threads": random.randint(5, 15)
        })
        time.sleep(0.05)
    
    print("✓ Performance logs written\n")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("  Advanced Logger - Example Usage")
    print("="*60 + "\n")
    
    # Run all simulations
    simulate_data_collector()
    simulate_strategy_engine()
    simulate_database_operations()
    simulate_error_handling()
    simulate_performance_monitoring()
    
    print("="*60)
    print("All example logs written to logs/polymarket.log")
    print("="*60)
    print("\nTry these commands:")
    print("  python advanced-logger.py --summary")
    print("  python advanced-logger.py --search 'ERROR'")
    print("  python advanced-logger.py --component 'data-collector'")
    print("  python advanced-logger.py --search 'API' --last 1h")
    print()


if __name__ == '__main__':
    main()
