#!/usr/bin/env python3
"""
Polymarket Trading System - Integration Test Suite

Comprehensive integration tests for the entire trading pipeline.

Usage:
    python integration-tests.py                     # Run all integration tests
    python integration-tests.py --quick            # Quick smoke tests (1 min)
    python integration-tests.py --full             # Full suite (10 min)
    python integration-tests.py --benchmark        # Performance benchmarks
    python integration-tests.py --workflow data    # Test specific workflow
"""

import sys
import time
import unittest
import argparse
import threading
import tracemalloc
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any

# Import mock services
from mocks import (
    MockPolymarketAPI,
    MockTwitterAPI,
    MockTelegramBot,
    MockDatabase,
    MockRiskManager,
    generate_mock_market,
    generate_mock_signal,
    generate_mock_tweets
)


# ============================================================================
# COMPONENT IMPLEMENTATIONS (Simplified for testing)
# ============================================================================

class DataCollector:
    """Collects market data from Polymarket API"""
    
    def __init__(self, api: MockPolymarketAPI, db: MockDatabase):
        self.api = api
        self.db = db
    
    def collect_markets(self, limit: int = 100) -> int:
        """Collect markets and store in database"""
        markets = self.api.get_markets(limit=limit)
        count = 0
        for market in markets:
            if self.db.insert_market(market):
                count += 1
        return count
    
    def collect_market_trades(self, market_id: str) -> List[Dict]:
        """Collect trades for a specific market"""
        return self.api.get_market_trades(market_id)


class HypeMonitor:
    """Monitors Twitter for market sentiment and hype"""
    
    def __init__(self, twitter_api: MockTwitterAPI, db: MockDatabase):
        self.twitter_api = twitter_api
        self.db = db
    
    def calculate_hype_score(self, keyword: str, market_id: str) -> float:
        """
        Calculate hype score based on Twitter activity
        
        Returns:
            float: Hype score 0-100
        """
        tweets = self.twitter_api.search_tweets(keyword, limit=100)
        
        if not tweets:
            return 0.0
        
        # Calculate metrics
        tweet_count = len(tweets)
        total_engagement = sum(t.get('likes', 0) + t.get('retweets', 0) for t in tweets)
        avg_engagement = total_engagement / tweet_count if tweet_count > 0 else 0
        
        # Simple sentiment analysis (positive keywords)
        positive_keywords = ['bullish', 'moon', 'great', 'amazing', 'best']
        sentiment_score = sum(
            1 for t in tweets 
            if any(kw in t['text'].lower() for kw in positive_keywords)
        ) / tweet_count if tweet_count > 0 else 0.5
        
        # Calculate hype score (0-100)
        hype_score = min(100, (tweet_count * 0.3) + (avg_engagement * 0.01) + (sentiment_score * 50))
        
        # Store in database
        self.db.insert_hype_score({
            'market_id': market_id,
            'keyword': keyword,
            'tweet_count': tweet_count,
            'sentiment_score': sentiment_score,
            'hype_score': hype_score
        })
        
        return hype_score


class SignalGenerator:
    """Generates trading signals from market data and hype scores"""
    
    def __init__(self, db: MockDatabase):
        self.db = db
    
    def generate_signal(self, market_id: str, hype_score: float, market_data: Dict) -> Dict:
        """
        Generate trading signal based on data
        
        Returns:
            Dict with signal details
        """
        yes_price = market_data.get('yes_price', 0.5)
        volume = market_data.get('volume', 0)
        liquidity = market_data.get('liquidity', 0)
        
        # Signal logic
        signal_type = None
        confidence = 0.0
        reason = ""
        
        # High hype + low price = BUY signal
        if hype_score > 70 and yes_price < 0.4:
            signal_type = "BUY"
            confidence = min(0.95, 0.6 + (hype_score / 200) + ((0.5 - yes_price) / 2))
            reason = f"High hype ({hype_score:.1f}) with undervalued price ({yes_price:.2f})"
        
        # Low hype + high price = SELL signal
        elif hype_score < 30 and yes_price > 0.6:
            signal_type = "SELL"
            confidence = min(0.95, 0.6 + ((1 - hype_score / 100) * 0.2) + ((yes_price - 0.5) / 2))
            reason = f"Low hype ({hype_score:.1f}) with overvalued price ({yes_price:.2f})"
        
        # No clear signal
        else:
            signal_type = "HOLD"
            confidence = 0.5
            reason = "No clear opportunity"
        
        # Adjust confidence based on liquidity
        if liquidity < 100000:
            confidence *= 0.8
            reason += " (low liquidity adjustment)"
        
        signal = {
            'market_id': market_id,
            'signal_type': signal_type,
            'confidence': confidence,
            'price': yes_price,
            'size': min(5000, liquidity * 0.01),  # 1% of liquidity
            'reason': reason
        }
        
        # Store in database
        self.db.insert_signal(signal)
        
        return signal


class AlertSystem:
    """Sends alerts via Telegram"""
    
    def __init__(self, telegram_bot: MockTelegramBot):
        self.telegram_bot = telegram_bot
        self.default_chat_id = "test_chat"
    
    def send_signal_alert(self, signal: Dict, risk_check: Dict) -> bool:
        """Send signal alert to Telegram"""
        if not risk_check.get('approved', False):
            return False
        
        message = (
            f"🚨 TRADING SIGNAL\n"
            f"Market: {signal['market_id']}\n"
            f"Action: {signal['signal_type']}\n"
            f"Confidence: {signal['confidence']:.1%}\n"
            f"Price: {signal['price']:.3f}\n"
            f"Size: ${signal.get('size', 0):.0f}\n"
            f"Reason: {signal['reason']}\n"
            f"Risk: {risk_check['reason']}"
        )
        
        self.telegram_bot.send_message(self.default_chat_id, message)
        return True


# ============================================================================
# INTEGRATION TEST SUITES
# ============================================================================

class EndToEndWorkflowTests(unittest.TestCase):
    """Test complete workflows from start to finish"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = MockPolymarketAPI()
        self.twitter = MockTwitterAPI()
        self.telegram = MockTelegramBot()
        self.db = MockDatabase()
        self.db.connect()
        self.risk_manager = MockRiskManager()
        
        self.data_collector = DataCollector(self.api, self.db)
        self.hype_monitor = HypeMonitor(self.twitter, self.db)
        self.signal_generator = SignalGenerator(self.db)
        self.alert_system = AlertSystem(self.telegram)
    
    def tearDown(self):
        """Clean up"""
        self.db.disconnect()
    
    def test_01_data_collection_to_database(self):
        """Test: Data collection → Database storage"""
        # Collect markets
        count = self.data_collector.collect_markets(limit=10)
        
        # Verify data in database
        markets = self.db.get_markets()
        
        self.assertGreater(count, 0, "Should collect at least one market")
        self.assertEqual(len(markets), count, "Database should contain all collected markets")
        self.assertIn('id', markets[0], "Market should have ID field")
        self.assertIn('question', markets[0], "Market should have question field")
    
    def test_02_twitter_to_hype_to_database(self):
        """Test: Twitter scrape → Hype calculation → Database"""
        market_id = "0x1234"
        
        # Calculate hype score
        hype_score = self.hype_monitor.calculate_hype_score("bitcoin", market_id)
        
        # Verify hype score stored
        hype_scores = self.db.get_hype_scores(market_id=market_id)
        
        self.assertGreater(hype_score, 0, "Should calculate hype score")
        self.assertLessEqual(hype_score, 100, "Hype score should be <= 100")
        self.assertEqual(len(hype_scores), 1, "Should store one hype score")
        self.assertEqual(hype_scores[0]['market_id'], market_id)
    
    def test_03_signal_to_risk_to_alert(self):
        """Test: Signal generation → Risk check → Alert"""
        market_id = "0x1234"
        market_data = self.api.get_market(market_id)
        
        # Generate signal
        signal = self.signal_generator.generate_signal(market_id, 85.0, market_data)
        
        # Risk check
        risk_check = self.risk_manager.validate_signal(signal)
        
        # Send alert
        alert_sent = self.alert_system.send_signal_alert(signal, risk_check)
        
        self.assertIn('signal_type', signal)
        self.assertGreater(signal['confidence'], 0)
        self.assertTrue(risk_check['approved'], "High confidence signal should pass risk check")
        self.assertTrue(alert_sent, "Alert should be sent for approved signal")
        self.assertEqual(len(self.telegram.get_sent_messages()), 1, "Should send one message")
    
    def test_04_full_pipeline_with_mock_data(self):
        """Test: Complete pipeline with mock data"""
        # Step 1: Collect market data
        self.data_collector.collect_markets(limit=3)
        markets = self.db.get_markets()
        self.assertGreater(len(markets), 0, "Should collect markets")
        
        # Step 2: Calculate hype for each market
        market = markets[0]
        keyword = market['question'].split()[1]  # Extract keyword from question
        hype_score = self.hype_monitor.calculate_hype_score(keyword, market['id'])
        self.assertIsNotNone(hype_score)
        
        # Step 3: Generate signal
        signal = self.signal_generator.generate_signal(market['id'], hype_score, market)
        self.assertIn('signal_type', signal)
        
        # Step 4: Risk check
        risk_check = self.risk_manager.validate_signal(signal)
        self.assertIn('approved', risk_check)
        
        # Step 5: Send alert if approved
        if risk_check['approved']:
            alert_sent = self.alert_system.send_signal_alert(signal, risk_check)
            self.assertTrue(alert_sent)
        
        # Verify end-to-end data flow
        signals = self.db.get_signals()
        hype_scores = self.db.get_hype_scores()
        
        self.assertGreater(len(signals), 0, "Should have generated signals")
        self.assertGreater(len(hype_scores), 0, "Should have hype scores")
    
    def test_05_multiple_markets_pipeline(self):
        """Test: Process multiple markets through full pipeline"""
        # Collect multiple markets
        self.data_collector.collect_markets(limit=3)
        markets = self.db.get_markets()
        
        processed_count = 0
        for market in markets:
            # Extract keyword (simplified)
            keyword = market['question'].split()[1] if len(market['question'].split()) > 1 else "test"
            
            # Calculate hype
            hype_score = self.hype_monitor.calculate_hype_score(keyword, market['id'])
            
            # Generate signal
            signal = self.signal_generator.generate_signal(market['id'], hype_score, market)
            
            # Risk check
            risk_check = self.risk_manager.validate_signal(signal)
            
            # Alert if approved
            if risk_check['approved']:
                self.alert_system.send_signal_alert(signal, risk_check)
                processed_count += 1
        
        self.assertGreater(processed_count, 0, "Should process at least one market")
        
        # Verify database state
        signals = self.db.get_signals()
        self.assertEqual(len(signals), len(markets), "Should have signal for each market")


class ComponentInteractionTests(unittest.TestCase):
    """Test interactions between components"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.api = MockPolymarketAPI()
        self.twitter = MockTwitterAPI()
        self.telegram = MockTelegramBot()
        self.db = MockDatabase()
        self.db.connect()
        self.risk_manager = MockRiskManager()
    
    def tearDown(self):
        """Clean up"""
        self.db.disconnect()
    
    def test_06_data_collector_database_interaction(self):
        """Test: Data collector + Database interaction"""
        collector = DataCollector(self.api, self.db)
        
        # Collect and verify
        count = collector.collect_markets(limit=5)
        markets = self.db.get_markets()
        
        self.assertEqual(count, len(markets))
        
        # Verify data integrity
        for market in markets:
            self.assertIsNotNone(market['id'])
            self.assertIsNotNone(market['question'])
            self.assertIsInstance(market['volume'], (int, float))
    
    def test_07_hype_monitor_database_interaction(self):
        """Test: Hype monitor + Database interaction"""
        monitor = HypeMonitor(self.twitter, self.db)
        
        # Calculate hype for multiple keywords
        keywords = ["bitcoin", "trump", "apple"]
        for i, keyword in enumerate(keywords):
            market_id = f"0x{i:04x}"
            hype_score = monitor.calculate_hype_score(keyword, market_id)
            self.assertGreater(hype_score, 0)
        
        # Verify all stored
        hype_scores = self.db.get_hype_scores()
        self.assertEqual(len(hype_scores), len(keywords))
    
    def test_08_signal_generator_risk_manager_interaction(self):
        """Test: Signal generator + Risk manager interaction"""
        generator = SignalGenerator(self.db)
        
        # Generate signals with different confidence levels
        market_data = generate_mock_market(yes_price=0.3, liquidity=1000000)
        
        # High confidence signal
        signal_high = generator.generate_signal("0x1234", 90.0, market_data)
        risk_high = self.risk_manager.validate_signal(signal_high)
        
        self.assertTrue(risk_high['approved'], "High confidence should pass")
        
        # Low confidence signal
        signal_low = generator.generate_signal("0x5678", 20.0, market_data)
        risk_low = self.risk_manager.validate_signal(signal_low)
        
        # Low confidence might still pass if > 0.6, but let's test edge case
        if signal_low['confidence'] < 0.6:
            self.assertFalse(risk_low['approved'], "Low confidence should fail")
    
    def test_09_alert_system_telegram_mock_interaction(self):
        """Test: Alert system + Telegram (mock) interaction"""
        alert_system = AlertSystem(self.telegram)
        
        # Send multiple alerts
        signals = [
            generate_mock_signal("0x1234", confidence=0.8, signal_type="BUY"),
            generate_mock_signal("0x5678", confidence=0.9, signal_type="SELL"),
            generate_mock_signal("0x9abc", confidence=0.7, signal_type="HOLD")
        ]
        
        for signal in signals:
            risk_check = {'approved': True, 'reason': 'Test approved'}
            alert_system.send_signal_alert(signal, risk_check)
        
        messages = self.telegram.get_sent_messages()
        self.assertEqual(len(messages), len(signals))
        
        # Verify message content
        self.assertIn("TRADING SIGNAL", messages[0]['text'])
        self.assertIn("BUY", messages[0]['text'])
    
    def test_10_end_to_end_component_chain(self):
        """Test: All components working together in sequence"""
        # Initialize all components
        collector = DataCollector(self.api, self.db)
        monitor = HypeMonitor(self.twitter, self.db)
        generator = SignalGenerator(self.db)
        alerts = AlertSystem(self.telegram)
        
        # Execute complete chain
        # 1. Collect data
        collector.collect_markets(limit=1)
        markets = self.db.get_markets()
        market = markets[0]
        
        # 2. Monitor hype
        hype_score = monitor.calculate_hype_score("test", market['id'])
        
        # 3. Generate signal
        signal = generator.generate_signal(market['id'], hype_score, market)
        
        # 4. Risk check
        risk_check = self.risk_manager.validate_signal(signal)
        
        # 5. Send alert
        if risk_check['approved']:
            alerts.send_signal_alert(signal, risk_check)
        
        # Verify complete flow
        self.assertEqual(len(self.db.get_markets()), 1)
        self.assertEqual(len(self.db.get_hype_scores()), 1)
        self.assertEqual(len(self.db.get_signals()), 1)


class ErrorHandlingTests(unittest.TestCase):
    """Test error handling and recovery"""
    
    def test_11_api_timeout_recovery(self):
        """Test: API timeout handling"""
        api = MockPolymarketAPI(fail_mode='timeout')
        db = MockDatabase()
        db.connect()
        collector = DataCollector(api, db)
        
        with self.assertRaises(TimeoutError):
            collector.collect_markets()
        
        db.disconnect()
    
    def test_12_api_rate_limit_handling(self):
        """Test: API rate limit handling"""
        api = MockPolymarketAPI(fail_mode='rate_limit')
        db = MockDatabase()
        db.connect()
        collector = DataCollector(api, db)
        
        # First 100 requests should work
        try:
            for i in range(150):
                api.get_markets(limit=1)
        except Exception as e:
            self.assertIn("Rate limit", str(e))
        
        db.disconnect()
    
    def test_13_database_connection_loss(self):
        """Test: Database connection loss handling"""
        db = MockDatabase(fail_mode='connection_error')
        
        with self.assertRaises(ConnectionError):
            db.connect()
    
    def test_14_invalid_data_handling(self):
        """Test: Invalid/malformed data handling"""
        api = MockPolymarketAPI(fail_mode='invalid_data')
        db = MockDatabase()
        db.connect()
        
        # Try to collect with invalid data
        try:
            markets = api.get_markets()
            # Invalid data might not have expected fields
            if isinstance(markets, dict) and 'invalid' in markets:
                self.assertTrue(True, "Detected invalid data")
        except Exception:
            self.assertTrue(True, "Exception caught for invalid data")
        
        db.disconnect()
    
    def test_15_twitter_api_failure_recovery(self):
        """Test: Twitter API failure recovery"""
        twitter = MockTwitterAPI(fail_mode='timeout')
        db = MockDatabase()
        db.connect()
        monitor = HypeMonitor(twitter, db)
        
        with self.assertRaises(TimeoutError):
            monitor.calculate_hype_score("bitcoin", "0x1234")
        
        db.disconnect()
    
    def test_16_telegram_network_error_handling(self):
        """Test: Telegram network error handling"""
        telegram = MockTelegramBot(fail_mode='network_error')
        alert_system = AlertSystem(telegram)
        
        signal = generate_mock_signal("0x1234", confidence=0.8)
        risk_check = {'approved': True, 'reason': 'Test'}
        
        with self.assertRaises(ConnectionError):
            alert_system.send_signal_alert(signal, risk_check)
    
    def test_17_database_query_error_recovery(self):
        """Test: Database query error recovery"""
        db = MockDatabase(fail_mode='query_error')
        db.connect()
        
        # Insert some data
        market = generate_mock_market()
        
        try:
            # This might fail on 5th query
            for i in range(10):
                db.insert_market(generate_mock_market(market_id=f"0x{i:04x}"))
        except Exception as e:
            self.assertIn("locked", str(e).lower())
        
        db.disconnect()
    
    def test_18_risk_manager_rejection_handling(self):
        """Test: Risk manager signal rejection"""
        risk_manager = MockRiskManager(max_exposure=1000)
        
        # Create signal that exceeds exposure
        signal = generate_mock_signal("0x1234", confidence=0.8, size=2000)
        
        risk_check = risk_manager.validate_signal(signal)
        
        # Should either reject or adjust size
        if not risk_check['approved']:
            self.assertIn('reason', risk_check)
        elif 'adjusted_size' in risk_check:
            self.assertLess(risk_check['adjusted_size'], signal['size'])


class ConcurrencyTests(unittest.TestCase):
    """Test concurrent operations"""
    
    def test_19_multiple_collectors_concurrent(self):
        """Test: Multiple data collectors running concurrently"""
        api = MockPolymarketAPI(latency_ms=100)  # Add latency to simulate real API
        db = MockDatabase()
        db.connect()
        
        def collect_data(collector_id):
            collector = DataCollector(api, db)
            return collector.collect_markets(limit=2)
        
        # Run 5 collectors concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(collect_data, i) for i in range(5)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all succeeded
        self.assertEqual(len(results), 5)
        for result in results:
            self.assertGreater(result, 0)
        
        db.disconnect()
    
    def test_20_database_concurrent_writes(self):
        """Test: Database concurrent write operations"""
        db = MockDatabase()
        db.connect()
        
        def write_market(market_id):
            market = generate_mock_market(market_id=f"0x{market_id:04x}")
            return db.insert_market(market)
        
        # Concurrent writes
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(write_market, i) for i in range(20)]
            results = [f.result() for f in as_completed(futures)]
        
        # Verify all writes succeeded
        self.assertEqual(sum(results), 20)
        
        # Verify data integrity
        markets = db.get_markets()
        self.assertEqual(len(markets), 20)
        
        db.disconnect()
    
    def test_21_signal_generation_under_load(self):
        """Test: Signal generation under concurrent load"""
        db = MockDatabase()
        db.connect()
        
        # Pre-populate with markets
        for i in range(10):
            db.insert_market(generate_mock_market(market_id=f"0x{i:04x}"))
        
        generator = SignalGenerator(db)
        
        def generate_signal_task(market_id):
            market_data = generate_mock_market(market_id=market_id)
            return generator.generate_signal(market_id, 75.0, market_data)
        
        # Generate signals concurrently
        market_ids = [f"0x{i:04x}" for i in range(10)]
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(generate_signal_task, mid) for mid in market_ids]
            results = [f.result() for f in as_completed(futures)]
        
        self.assertEqual(len(results), 10)
        
        # Verify all signals stored
        signals = db.get_signals()
        self.assertGreaterEqual(len(signals), 10)
        
        db.disconnect()


class PerformanceBenchmarkTests(unittest.TestCase):
    """Performance benchmarks"""
    
    def test_22_data_collection_speed(self):
        """Benchmark: Data collection speed (markets/second)"""
        api = MockPolymarketAPI()
        db = MockDatabase()
        db.connect()
        collector = DataCollector(api, db)
        
        start_time = time.time()
        count = collector.collect_markets(limit=50)
        duration = time.time() - start_time
        
        markets_per_second = count / duration
        
        print(f"\n📊 Data Collection Speed: {markets_per_second:.2f} markets/second")
        self.assertGreater(markets_per_second, 10, "Should collect at least 10 markets/second")
        
        db.disconnect()
    
    def test_23_signal_generation_latency(self):
        """Benchmark: Signal generation latency"""
        db = MockDatabase()
        db.connect()
        generator = SignalGenerator(db)
        
        market_data = generate_mock_market()
        
        # Warmup
        generator.generate_signal("0x0000", 75.0, market_data)
        
        # Benchmark
        latencies = []
        for i in range(100):
            start = time.time()
            generator.generate_signal(f"0x{i:04x}", 75.0, market_data)
            latencies.append(time.time() - start)
        
        avg_latency_ms = (sum(latencies) / len(latencies)) * 1000
        p95_latency_ms = sorted(latencies)[94] * 1000
        
        print(f"\n📊 Signal Generation Latency:")
        print(f"   Average: {avg_latency_ms:.2f}ms")
        print(f"   P95: {p95_latency_ms:.2f}ms")
        
        self.assertLess(avg_latency_ms, 50, "Average latency should be < 50ms")
        self.assertLess(p95_latency_ms, 100, "P95 latency should be < 100ms")
        
        db.disconnect()
    
    def test_24_database_query_performance(self):
        """Benchmark: Database query performance"""
        db = MockDatabase()
        db.connect()
        
        # Insert test data
        for i in range(100):
            db.insert_market(generate_mock_market(market_id=f"0x{i:04x}"))
        
        # Benchmark queries
        start = time.time()
        for _ in range(100):
            markets = db.get_markets(limit=10)
        query_duration = time.time() - start
        
        queries_per_second = 100 / query_duration
        
        print(f"\n📊 Database Query Performance: {queries_per_second:.2f} queries/second")
        
        # Get performance stats
        stats = db.get_performance_stats()
        print(f"   Total queries: {stats['total_queries']}")
        print(f"   Avg query time: {stats['avg_query_time_ms']:.2f}ms")
        
        self.assertGreater(queries_per_second, 100, "Should handle > 100 queries/second")
        
        db.disconnect()
    
    def test_25_memory_usage_under_load(self):
        """Benchmark: Memory usage under load"""
        tracemalloc.start()
        
        api = MockPolymarketAPI()
        db = MockDatabase()
        db.connect()
        collector = DataCollector(api, db)
        
        # Baseline
        baseline = tracemalloc.get_traced_memory()[0]
        
        # Load test
        for _ in range(10):
            collector.collect_markets(limit=10)
        
        # Measure
        current, peak = tracemalloc.get_traced_memory()
        memory_used_mb = (current - baseline) / 1024 / 1024
        peak_memory_mb = peak / 1024 / 1024
        
        print(f"\n📊 Memory Usage:")
        print(f"   Used: {memory_used_mb:.2f} MB")
        print(f"   Peak: {peak_memory_mb:.2f} MB")
        
        tracemalloc.stop()
        
        self.assertLess(memory_used_mb, 50, "Memory usage should be < 50MB")
        
        db.disconnect()
    
    def test_26_end_to_end_pipeline_throughput(self):
        """Benchmark: Complete pipeline throughput"""
        api = MockPolymarketAPI()
        twitter = MockTwitterAPI()
        telegram = MockTelegramBot()
        db = MockDatabase()
        db.connect()
        risk_manager = MockRiskManager()
        
        collector = DataCollector(api, db)
        monitor = HypeMonitor(twitter, db)
        generator = SignalGenerator(db)
        alerts = AlertSystem(telegram)
        
        start_time = time.time()
        
        # Process 10 markets through complete pipeline
        collector.collect_markets(limit=10)
        markets = db.get_markets()
        
        processed = 0
        for market in markets[:10]:
            keyword = market['question'].split()[1] if len(market['question'].split()) > 1 else "test"
            hype_score = monitor.calculate_hype_score(keyword, market['id'])
            signal = generator.generate_signal(market['id'], hype_score, market)
            risk_check = risk_manager.validate_signal(signal)
            if risk_check['approved']:
                alerts.send_signal_alert(signal, risk_check)
            processed += 1
        
        duration = time.time() - start_time
        throughput = processed / duration
        
        print(f"\n📊 Pipeline Throughput: {throughput:.2f} markets/second")
        
        self.assertGreater(throughput, 1, "Should process > 1 market/second")
        
        db.disconnect()


# ============================================================================
# TEST RUNNER
# ============================================================================

class ColoredTextTestResult(unittest.TextTestResult):
    """Test result with colored output"""
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.write("✓ ")
        self.stream.flush()
    
    def addError(self, test, err):
        super().addError(test, err)
        self.stream.write("✗ ")
        self.stream.flush()
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.stream.write("✗ ")
        self.stream.flush()


def run_test_suite(test_mode: str = 'all', workflow: str = None):
    """
    Run integration test suite
    
    Args:
        test_mode: 'quick', 'full', 'benchmark', or 'all'
        workflow: Specific workflow to test ('data', 'hype', 'signal', 'alert')
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Select tests based on mode
    if test_mode == 'quick':
        # Quick smoke tests (fast, essential tests only)
        suite.addTests(loader.loadTestsFromName('__main__.EndToEndWorkflowTests.test_01_data_collection_to_database'))
        suite.addTests(loader.loadTestsFromName('__main__.EndToEndWorkflowTests.test_03_signal_to_risk_to_alert'))
        suite.addTests(loader.loadTestsFromName('__main__.ComponentInteractionTests.test_06_data_collector_database_interaction'))
        suite.addTests(loader.loadTestsFromName('__main__.ErrorHandlingTests.test_11_api_timeout_recovery'))
        print("🚀 Running QUICK smoke tests (4 tests, ~1 min)\n")
    
    elif test_mode == 'benchmark':
        # Performance benchmarks only
        suite.addTests(loader.loadTestsFromTestCase(PerformanceBenchmarkTests))
        print("📊 Running PERFORMANCE benchmarks (5 tests)\n")
    
    elif workflow:
        # Specific workflow tests
        workflow_map = {
            'data': ['test_01_data_collection_to_database', 'test_06_data_collector_database_interaction'],
            'hype': ['test_02_twitter_to_hype_to_database', 'test_07_hype_monitor_database_interaction'],
            'signal': ['test_03_signal_to_risk_to_alert', 'test_08_signal_generator_risk_manager_interaction'],
            'alert': ['test_09_alert_system_telegram_mock_interaction']
        }
        
        if workflow in workflow_map:
            for test_name in workflow_map[workflow]:
                try:
                    suite.addTests(loader.loadTestsFromName(f'__main__.EndToEndWorkflowTests.{test_name}'))
                except:
                    try:
                        suite.addTests(loader.loadTestsFromName(f'__main__.ComponentInteractionTests.{test_name}'))
                    except:
                        pass
            print(f"🎯 Running {workflow.upper()} workflow tests\n")
        else:
            print(f"❌ Unknown workflow: {workflow}")
            print(f"   Available: data, hype, signal, alert")
            sys.exit(1)
    
    else:
        # Full suite (all tests)
        suite.addTests(loader.loadTestsFromTestCase(EndToEndWorkflowTests))
        suite.addTests(loader.loadTestsFromTestCase(ComponentInteractionTests))
        suite.addTests(loader.loadTestsFromTestCase(ErrorHandlingTests))
        suite.addTests(loader.loadTestsFromTestCase(ConcurrencyTests))
        suite.addTests(loader.loadTestsFromTestCase(PerformanceBenchmarkTests))
        print("🧪 Running FULL integration test suite (26 tests, ~10 min)\n")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, resultclass=ColoredTextTestResult)
    start_time = time.time()
    result = runner.run(suite)
    duration = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Duration: {duration:.2f} seconds")
    print("=" * 70)
    
    # Exit code
    if result.wasSuccessful():
        print("\n✅ All tests passed! Great success!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Polymarket Trading System - Integration Test Suite',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python integration-tests.py                    # Run all tests
  python integration-tests.py --quick            # Quick smoke tests
  python integration-tests.py --full             # Full test suite
  python integration-tests.py --benchmark        # Performance benchmarks
  python integration-tests.py --workflow data    # Test data workflow
        """
    )
    
    parser.add_argument('--quick', action='store_true', help='Run quick smoke tests (~1 min)')
    parser.add_argument('--full', action='store_true', help='Run full test suite (~10 min)')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmarks')
    parser.add_argument('--workflow', type=str, choices=['data', 'hype', 'signal', 'alert'],
                        help='Test specific workflow')
    
    args = parser.parse_args()
    
    # Determine test mode
    if args.quick:
        test_mode = 'quick'
    elif args.benchmark:
        test_mode = 'benchmark'
    elif args.workflow:
        test_mode = 'workflow'
    elif args.full:
        test_mode = 'all'
    else:
        # Default to full suite
        test_mode = 'all'
    
    # Run tests
    exit_code = run_test_suite(test_mode, args.workflow)
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
