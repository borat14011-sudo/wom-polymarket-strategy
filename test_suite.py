#!/usr/bin/env python3
"""
Comprehensive Test Suite for Polymarket Trading System

Usage:
    python test_suite.py                    # Run all tests
    python test_suite.py --module signals   # Test specific module
    python test_suite.py --coverage         # Show coverage report
    python test_suite.py --verbose          # Detailed output
"""

import unittest
import sys
import time
import math
from typing import List, Dict, Tuple
from test_helpers import (
    MockDataGenerator, MockDatabase,
    validate_price, validate_timestamp, validate_market_id
)


# ============================================================================
# SIGNAL GENERATION LOGIC
# ============================================================================

def calculate_rvr(volumes: List[float], window: int = 20) -> float:
    """
    Calculate Relative Volume Ratio
    RVR = current_volume / average_volume
    """
    if len(volumes) < window or window <= 0:
        return 1.0
    
    recent_volume = volumes[-1]
    avg_volume = sum(volumes[-window:]) / window
    
    if avg_volume == 0:
        return 1.0
    
    return recent_volume / avg_volume


def calculate_roc(prices: List[float], period: int = 14) -> float:
    """
    Calculate Rate of Change
    ROC = ((current_price - old_price) / old_price) * 100
    """
    if len(prices) < period + 1 or period <= 0:
        return 0.0
    
    current_price = prices[-1]
    old_price = prices[-period - 1]
    
    if old_price == 0:
        return 0.0
    
    return ((current_price - old_price) / old_price) * 100


def calculate_hype_score(signals: List[Dict], window_seconds: int = 3600) -> float:
    """
    Calculate hype score from social signals
    Weighted by sentiment and volume, time-decayed
    """
    if not signals:
        return 0.0
    
    current_time = time.time()
    total_score = 0.0
    total_weight = 0.0
    
    for signal in signals:
        age = current_time - signal['timestamp']
        
        # Skip signals outside window
        if age > window_seconds:
            continue
        
        # Time decay: exponential decay over window
        decay = math.exp(-age / (window_seconds / 3))
        
        # Score = sentiment * volume * decay
        score = signal['sentiment'] * signal['volume'] * decay
        total_score += score
        total_weight += decay
    
    if total_weight == 0:
        return 0.0
    
    # Normalize to 0-100 scale
    return min(100, (total_score / total_weight) * 10)


def check_signal_confirmation(
    rvr: float,
    roc: float,
    hype: float,
    rvr_threshold: float = 1.5,
    roc_threshold: float = 5.0,
    hype_threshold: float = 60.0
) -> Tuple[bool, List[str]]:
    """
    Check if all three signals confirm a trading opportunity
    Returns: (confirmed, triggered_signals)
    """
    triggered = []
    
    if rvr >= rvr_threshold:
        triggered.append('RVR')
    
    if abs(roc) >= roc_threshold:
        triggered.append('ROC')
    
    if hype >= hype_threshold:
        triggered.append('HYPE')
    
    confirmed = len(triggered) >= 3
    return confirmed, triggered


# ============================================================================
# RISK MANAGEMENT
# ============================================================================

def calculate_kelly_position_size(
    win_probability: float,
    win_loss_ratio: float,
    max_position: float = 0.25
) -> float:
    """
    Calculate position size using Kelly Criterion
    Kelly% = (win_prob * win_loss_ratio - (1 - win_prob)) / win_loss_ratio
    """
    if not (0 <= win_probability <= 1):
        return 0.0
    
    if win_loss_ratio <= 0:
        return 0.0
    
    kelly = (win_probability * win_loss_ratio - (1 - win_probability)) / win_loss_ratio
    
    # Use fractional Kelly (0.25 = quarter Kelly for safety)
    fractional_kelly = kelly * 0.25
    
    # Cap at max position
    return max(0, min(max_position, fractional_kelly))


def calculate_stop_loss(
    entry_price: float,
    volatility: float,
    multiplier: float = 2.0
) -> float:
    """
    Calculate stop loss based on volatility
    Stop = entry_price - (volatility * multiplier)
    """
    if entry_price <= 0 or volatility < 0:
        return entry_price
    
    stop_loss = entry_price - (volatility * multiplier)
    
    # Ensure stop loss is reasonable (not negative, at least 1% below entry)
    min_stop = entry_price * 0.99
    return max(0.01, min(min_stop, stop_loss))


def calculate_take_profit(
    entry_price: float,
    stop_loss: float,
    risk_reward_ratio: float = 2.0
) -> float:
    """
    Calculate take profit based on risk/reward ratio
    Take profit = entry + (entry - stop) * ratio
    """
    if entry_price <= 0 or stop_loss < 0 or risk_reward_ratio <= 0:
        return entry_price
    
    risk = entry_price - stop_loss
    take_profit = entry_price + (risk * risk_reward_ratio)
    
    # Ensure take profit doesn't exceed 1.0 (Polymarket max)
    return min(0.99, take_profit)


def check_circuit_breaker(
    recent_losses: List[float],
    max_loss_threshold: float = 0.10,
    consecutive_losses: int = 3
) -> Tuple[bool, str]:
    """
    Check if circuit breaker should trigger
    Returns: (triggered, reason)
    """
    if not recent_losses:
        return False, ""
    
    # Check total loss
    total_loss = sum(recent_losses)
    if total_loss >= max_loss_threshold:
        return True, f"Total loss {total_loss:.2%} exceeds threshold {max_loss_threshold:.2%}"
    
    # Check consecutive losses
    if len(recent_losses) >= consecutive_losses:
        if all(loss > 0 for loss in recent_losses[-consecutive_losses:]):
            return True, f"{consecutive_losses} consecutive losses detected"
    
    return False, ""


# ============================================================================
# CORRELATION ANALYSIS
# ============================================================================

def calculate_cross_correlation(series1: List[float], series2: List[float], max_lag: int = 10) -> List[float]:
    """
    Calculate cross-correlation between two series at different lags
    Returns list of correlations for lags 0 to max_lag
    """
    if len(series1) != len(series2) or len(series1) == 0:
        return []
    
    n = len(series1)
    correlations = []
    
    # Normalize series
    mean1 = sum(series1) / n
    mean2 = sum(series2) / n
    std1 = math.sqrt(sum((x - mean1) ** 2 for x in series1) / n)
    std2 = math.sqrt(sum((x - mean2) ** 2 for x in series2) / n)
    
    if std1 == 0 or std2 == 0:
        return [0.0] * (max_lag + 1)
    
    for lag in range(max_lag + 1):
        if lag >= n:
            correlations.append(0.0)
            continue
        
        correlation = 0.0
        count = n - lag
        
        for i in range(count):
            correlation += ((series1[i] - mean1) / std1) * ((series2[i + lag] - mean2) / std2)
        
        correlation /= count
        correlations.append(correlation)
    
    return correlations


def detect_lag(correlations: List[float]) -> int:
    """
    Detect optimal lag from cross-correlation results
    Returns the lag with highest absolute correlation
    """
    if not correlations:
        return 0
    
    max_corr = 0
    best_lag = 0
    
    for i, corr in enumerate(correlations):
        if abs(corr) > abs(max_corr):
            max_corr = corr
            best_lag = i
    
    return best_lag


def granger_causality_test(series1: List[float], series2: List[float], max_lag: int = 5) -> Dict:
    """
    Simplified Granger causality test
    Tests if series1 helps predict series2
    Returns: {'lag': best_lag, 'score': prediction_improvement}
    """
    if len(series1) < max_lag + 2 or len(series2) < max_lag + 2:
        return {'lag': 0, 'score': 0.0}
    
    n = len(series1)
    
    # Calculate baseline error (prediction without series1)
    baseline_error = 0.0
    for i in range(max_lag, n - 1):
        prediction = series2[i]  # Naive: predict same as current
        actual = series2[i + 1]
        baseline_error += (prediction - actual) ** 2
    
    baseline_error /= (n - max_lag - 1)
    
    # Calculate error with series1 (simple lagged regression)
    best_lag = 0
    best_error = baseline_error
    
    for lag in range(1, max_lag + 1):
        error = 0.0
        for i in range(lag, n - 1):
            # Simple prediction: use correlation with lagged series1
            prediction = series2[i] + 0.1 * (series1[i - lag] - series1[i - lag - 1]) if i > lag else series2[i]
            actual = series2[i + 1]
            error += (prediction - actual) ** 2
        
        error /= (n - lag - 1)
        
        if error < best_error:
            best_error = error
            best_lag = lag
    
    # Score is improvement over baseline
    improvement = (baseline_error - best_error) / baseline_error if baseline_error > 0 else 0.0
    
    return {'lag': best_lag, 'score': improvement}


# ============================================================================
# TEST CASES
# ============================================================================

class TestSignalGeneration(unittest.TestCase):
    """Test signal generation logic"""
    
    def test_rvr_calculation_normal(self):
        """Test RVR with normal volume data"""
        volumes = [100] * 19 + [200]  # Last volume is 2x average
        rvr = calculate_rvr(volumes, window=20)
        self.assertAlmostEqual(rvr, 2.0, places=2)
    
    def test_rvr_calculation_low_volume(self):
        """Test RVR with below-average volume"""
        volumes = [100] * 19 + [50]  # Last volume is 0.5x average
        rvr = calculate_rvr(volumes, window=20)
        self.assertAlmostEqual(rvr, 0.5, places=2)
    
    def test_rvr_insufficient_data(self):
        """Test RVR returns 1.0 when insufficient data"""
        volumes = [100] * 10
        rvr = calculate_rvr(volumes, window=20)
        self.assertEqual(rvr, 1.0)
    
    def test_rvr_zero_average_volume(self):
        """Test RVR handles zero average volume"""
        volumes = [0] * 20
        rvr = calculate_rvr(volumes, window=20)
        self.assertEqual(rvr, 1.0)
    
    def test_roc_positive_change(self):
        """Test ROC with positive price change"""
        prices = [0.5] * 10 + [0.55]  # 10% increase
        roc = calculate_roc(prices, period=10)
        self.assertAlmostEqual(roc, 10.0, places=1)
    
    def test_roc_negative_change(self):
        """Test ROC with negative price change"""
        prices = [0.5] * 10 + [0.45]  # 10% decrease
        roc = calculate_roc(prices, period=10)
        self.assertAlmostEqual(roc, -10.0, places=1)
    
    def test_roc_no_change(self):
        """Test ROC with no price change"""
        prices = [0.5] * 20
        roc = calculate_roc(prices, period=10)
        self.assertEqual(roc, 0.0)
    
    def test_roc_insufficient_data(self):
        """Test ROC returns 0 when insufficient data"""
        prices = [0.5] * 5
        roc = calculate_roc(prices, period=10)
        self.assertEqual(roc, 0.0)
    
    def test_hype_score_high_sentiment(self):
        """Test hype score with high sentiment signals"""
        signals = [
            {'timestamp': time.time() - 300, 'sentiment': 0.9, 'volume': 50},
            {'timestamp': time.time() - 600, 'sentiment': 0.8, 'volume': 40},
            {'timestamp': time.time() - 900, 'sentiment': 0.85, 'volume': 45}
        ]
        hype = calculate_hype_score(signals, window_seconds=3600)
        self.assertGreater(hype, 30)  # Should be significant
    
    def test_hype_score_low_sentiment(self):
        """Test hype score with low sentiment signals"""
        signals = [
            {'timestamp': time.time() - 300, 'sentiment': 0.2, 'volume': 10},
            {'timestamp': time.time() - 600, 'sentiment': 0.1, 'volume': 5}
        ]
        hype = calculate_hype_score(signals, window_seconds=3600)
        self.assertLess(hype, 20)  # Should be low
    
    def test_hype_score_empty_signals(self):
        """Test hype score with no signals"""
        hype = calculate_hype_score([], window_seconds=3600)
        self.assertEqual(hype, 0.0)
    
    def test_hype_score_time_decay(self):
        """Test hype score applies time decay"""
        old_signal = {'timestamp': time.time() - 3000, 'sentiment': 0.8, 'volume': 50}
        recent_signal = {'timestamp': time.time() - 100, 'sentiment': 0.8, 'volume': 50}
        
        hype_old = calculate_hype_score([old_signal], window_seconds=3600)
        hype_recent = calculate_hype_score([recent_signal], window_seconds=3600)
        
        self.assertGreater(hype_recent, hype_old)  # Recent should score higher
    
    def test_signal_confirmation_all_triggered(self):
        """Test signal confirmation when all signals trigger"""
        confirmed, triggered = check_signal_confirmation(
            rvr=2.0, roc=6.0, hype=70.0,
            rvr_threshold=1.5, roc_threshold=5.0, hype_threshold=60.0
        )
        self.assertTrue(confirmed)
        self.assertEqual(len(triggered), 3)
        self.assertIn('RVR', triggered)
        self.assertIn('ROC', triggered)
        self.assertIn('HYPE', triggered)
    
    def test_signal_confirmation_partial(self):
        """Test signal confirmation with only 2 signals"""
        confirmed, triggered = check_signal_confirmation(
            rvr=2.0, roc=3.0, hype=70.0,  # ROC below threshold
            rvr_threshold=1.5, roc_threshold=5.0, hype_threshold=60.0
        )
        self.assertFalse(confirmed)
        self.assertEqual(len(triggered), 2)
    
    def test_signal_confirmation_negative_roc(self):
        """Test signal confirmation handles negative ROC"""
        confirmed, triggered = check_signal_confirmation(
            rvr=2.0, roc=-6.0, hype=70.0,  # Negative ROC still triggers
            rvr_threshold=1.5, roc_threshold=5.0, hype_threshold=60.0
        )
        self.assertTrue(confirmed)


class TestRiskManagement(unittest.TestCase):
    """Test risk management functions"""
    
    def test_kelly_criterion_positive_edge(self):
        """Test Kelly position sizing with positive edge"""
        position = calculate_kelly_position_size(
            win_probability=0.6,
            win_loss_ratio=2.0,
            max_position=0.25
        )
        self.assertGreater(position, 0)
        self.assertLessEqual(position, 0.25)
    
    def test_kelly_criterion_no_edge(self):
        """Test Kelly returns 0 with no edge"""
        position = calculate_kelly_position_size(
            win_probability=0.5,
            win_loss_ratio=1.0,
            max_position=0.25
        )
        self.assertAlmostEqual(position, 0.0, places=2)
    
    def test_kelly_criterion_invalid_probability(self):
        """Test Kelly handles invalid probability"""
        position = calculate_kelly_position_size(
            win_probability=1.5,  # Invalid
            win_loss_ratio=2.0,
            max_position=0.25
        )
        self.assertEqual(position, 0.0)
    
    def test_kelly_criterion_negative_ratio(self):
        """Test Kelly handles negative win/loss ratio"""
        position = calculate_kelly_position_size(
            win_probability=0.6,
            win_loss_ratio=-1.0,  # Invalid
            max_position=0.25
        )
        self.assertEqual(position, 0.0)
    
    def test_kelly_criterion_respects_max(self):
        """Test Kelly respects maximum position size"""
        position = calculate_kelly_position_size(
            win_probability=0.9,  # Very high edge
            win_loss_ratio=5.0,
            max_position=0.10  # Low max
        )
        self.assertLessEqual(position, 0.10)
    
    def test_stop_loss_calculation(self):
        """Test stop loss calculation"""
        stop = calculate_stop_loss(
            entry_price=0.50,
            volatility=0.05,
            multiplier=2.0
        )
        expected = 0.50 - (0.05 * 2.0)
        self.assertAlmostEqual(stop, expected, places=2)
    
    def test_stop_loss_minimum_gap(self):
        """Test stop loss maintains minimum gap"""
        stop = calculate_stop_loss(
            entry_price=0.50,
            volatility=0.001,  # Very low volatility
            multiplier=2.0
        )
        self.assertLessEqual(stop, 0.50 * 0.99)  # At least 1% below
    
    def test_stop_loss_not_negative(self):
        """Test stop loss never goes negative"""
        stop = calculate_stop_loss(
            entry_price=0.10,
            volatility=0.20,  # High volatility
            multiplier=2.0
        )
        self.assertGreaterEqual(stop, 0.01)
    
    def test_take_profit_calculation(self):
        """Test take profit with 2:1 risk/reward"""
        take_profit = calculate_take_profit(
            entry_price=0.50,
            stop_loss=0.45,
            risk_reward_ratio=2.0
        )
        expected = 0.50 + (0.50 - 0.45) * 2.0
        self.assertAlmostEqual(take_profit, expected, places=2)
    
    def test_take_profit_max_cap(self):
        """Test take profit doesn't exceed 0.99"""
        take_profit = calculate_take_profit(
            entry_price=0.90,
            stop_loss=0.80,
            risk_reward_ratio=3.0
        )
        self.assertLessEqual(take_profit, 0.99)
    
    def test_take_profit_invalid_inputs(self):
        """Test take profit handles invalid inputs"""
        take_profit = calculate_take_profit(
            entry_price=-0.50,  # Invalid
            stop_loss=0.45,
            risk_reward_ratio=2.0
        )
        self.assertEqual(take_profit, -0.50)  # Returns entry price
    
    def test_circuit_breaker_total_loss(self):
        """Test circuit breaker triggers on total loss"""
        losses = [0.03, 0.04, 0.05]  # Total 12% loss
        triggered, reason = check_circuit_breaker(
            recent_losses=losses,
            max_loss_threshold=0.10,
            consecutive_losses=3
        )
        self.assertTrue(triggered)
        self.assertIn("Total loss", reason)
    
    def test_circuit_breaker_consecutive_losses(self):
        """Test circuit breaker triggers on consecutive losses"""
        losses = [0.02, 0.02, 0.02]  # 3 consecutive losses, 6% total
        triggered, reason = check_circuit_breaker(
            recent_losses=losses,
            max_loss_threshold=0.10,
            consecutive_losses=3
        )
        self.assertTrue(triggered)
        self.assertIn("consecutive", reason)
    
    def test_circuit_breaker_no_trigger(self):
        """Test circuit breaker doesn't trigger prematurely"""
        losses = [0.02, 0.01]  # Small losses
        triggered, reason = check_circuit_breaker(
            recent_losses=losses,
            max_loss_threshold=0.10,
            consecutive_losses=3
        )
        self.assertFalse(triggered)
    
    def test_circuit_breaker_mixed_results(self):
        """Test circuit breaker with wins and losses"""
        losses = [0.02, -0.01, 0.02]  # Win in middle (negative loss)
        triggered, reason = check_circuit_breaker(
            recent_losses=losses,
            max_loss_threshold=0.10,
            consecutive_losses=3
        )
        self.assertFalse(triggered)


class TestDataValidation(unittest.TestCase):
    """Test data validation functions"""
    
    def test_validate_price_valid_range(self):
        """Test price validation with valid prices"""
        self.assertTrue(validate_price(0.0))
        self.assertTrue(validate_price(0.5))
        self.assertTrue(validate_price(1.0))
    
    def test_validate_price_invalid_negative(self):
        """Test price validation rejects negative"""
        self.assertFalse(validate_price(-0.1))
    
    def test_validate_price_invalid_above_one(self):
        """Test price validation rejects > 1.0"""
        self.assertFalse(validate_price(1.1))
    
    def test_validate_price_edge_cases(self):
        """Test price validation edge cases"""
        self.assertTrue(validate_price(0.0001))
        self.assertTrue(validate_price(0.9999))
    
    def test_validate_timestamp_current(self):
        """Test timestamp validation with current time"""
        now = time.time()
        self.assertTrue(validate_timestamp(now))
    
    def test_validate_timestamp_recent_past(self):
        """Test timestamp validation with recent past"""
        one_day_ago = time.time() - (24 * 3600)
        self.assertTrue(validate_timestamp(one_day_ago))
    
    def test_validate_timestamp_near_future(self):
        """Test timestamp validation with near future"""
        one_day_ahead = time.time() + (24 * 3600)
        self.assertTrue(validate_timestamp(one_day_ahead))
    
    def test_validate_timestamp_too_old(self):
        """Test timestamp validation rejects ancient timestamps"""
        two_years_ago = time.time() - (2 * 365 * 24 * 3600)
        self.assertFalse(validate_timestamp(two_years_ago))
    
    def test_validate_timestamp_too_future(self):
        """Test timestamp validation rejects far future"""
        two_years_ahead = time.time() + (2 * 365 * 24 * 3600)
        self.assertFalse(validate_timestamp(two_years_ahead))
    
    def test_validate_market_id_valid(self):
        """Test market ID validation with valid IDs"""
        self.assertTrue(validate_market_id("market_12345"))
        self.assertTrue(validate_market_id("btc-usd-2024"))
        self.assertTrue(validate_market_id("event.123"))
    
    def test_validate_market_id_too_short(self):
        """Test market ID validation rejects short IDs"""
        self.assertFalse(validate_market_id("abc"))
    
    def test_validate_market_id_too_long(self):
        """Test market ID validation rejects long IDs"""
        long_id = "a" * 101
        self.assertFalse(validate_market_id(long_id))
    
    def test_validate_market_id_invalid_chars(self):
        """Test market ID validation rejects invalid characters"""
        self.assertFalse(validate_market_id("market@123"))
        self.assertFalse(validate_market_id("market 123"))
    
    def test_validate_market_id_not_string(self):
        """Test market ID validation rejects non-strings"""
        self.assertFalse(validate_market_id(12345))
        self.assertFalse(validate_market_id(None))


class TestDatabaseOperations(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up mock database for each test"""
        self.db = MockDatabase()
    
    def test_insert_single_record(self):
        """Test inserting a single record"""
        data = {'market_id': 'test_123', 'price': 0.5, 'timestamp': time.time()}
        result = self.db.insert('prices', data)
        self.assertTrue(result)
        self.assertEqual(len(self.db.tables['prices']), 1)
    
    def test_insert_invalid_table(self):
        """Test insert into non-existent table fails"""
        data = {'test': 'data'}
        result = self.db.insert('invalid_table', data)
        self.assertFalse(result)
    
    def test_batch_insert(self):
        """Test batch insert multiple records"""
        data_list = [
            {'market_id': f'test_{i}', 'price': 0.5 + i * 0.1}
            for i in range(10)
        ]
        count = self.db.batch_insert('prices', data_list)
        self.assertEqual(count, 10)
        self.assertEqual(len(self.db.tables['prices']), 10)
    
    def test_query_all_records(self):
        """Test querying all records"""
        for i in range(5):
            self.db.insert('prices', {'market_id': f'test_{i}', 'price': 0.5})
        
        results = self.db.query('prices')
        self.assertEqual(len(results), 5)
    
    def test_query_with_conditions(self):
        """Test querying with conditions"""
        self.db.insert('prices', {'market_id': 'test_1', 'price': 0.5})
        self.db.insert('prices', {'market_id': 'test_2', 'price': 0.6})
        self.db.insert('prices', {'market_id': 'test_1', 'price': 0.7})
        
        results = self.db.query('prices', {'market_id': 'test_1'})
        self.assertEqual(len(results), 2)
        self.assertTrue(all(r['market_id'] == 'test_1' for r in results))
    
    def test_query_empty_table(self):
        """Test querying empty table"""
        results = self.db.query('prices')
        self.assertEqual(results, [])
    
    def test_update_records(self):
        """Test updating records"""
        self.db.insert('prices', {'market_id': 'test_1', 'price': 0.5})
        self.db.insert('prices', {'market_id': 'test_1', 'price': 0.6})
        
        count = self.db.update('prices', {'market_id': 'test_1'}, {'price': 0.7})
        self.assertEqual(count, 2)
        
        results = self.db.query('prices', {'market_id': 'test_1'})
        self.assertTrue(all(r['price'] == 0.7 for r in results))
    
    def test_update_no_matches(self):
        """Test update with no matching records"""
        self.db.insert('prices', {'market_id': 'test_1', 'price': 0.5})
        
        count = self.db.update('prices', {'market_id': 'test_2'}, {'price': 0.7})
        self.assertEqual(count, 0)
    
    def test_create_index(self):
        """Test creating an index"""
        result = self.db.create_index('prices', 'market_id')
        self.assertTrue(result)
        self.assertTrue(self.db.has_index('prices', 'market_id'))
    
    def test_has_index_nonexistent(self):
        """Test checking for non-existent index"""
        self.assertFalse(self.db.has_index('prices', 'timestamp'))
    
    def test_clear_database(self):
        """Test clearing all data"""
        self.db.insert('prices', {'test': 'data'})
        self.db.create_index('prices', 'test')
        
        self.db.clear()
        
        self.assertEqual(len(self.db.tables['prices']), 0)
        self.assertEqual(len(self.db.indexes), 0)


class TestCorrelationAnalysis(unittest.TestCase):
    """Test correlation analysis functions"""
    
    def test_cross_correlation_perfect_correlation(self):
        """Test cross-correlation with perfectly correlated series"""
        series1 = [1, 2, 3, 4, 5]
        series2 = [1, 2, 3, 4, 5]
        
        correlations = calculate_cross_correlation(series1, series2, max_lag=2)
        self.assertAlmostEqual(correlations[0], 1.0, places=1)
    
    def test_cross_correlation_negative_correlation(self):
        """Test cross-correlation with negatively correlated series"""
        series1 = [1, 2, 3, 4, 5]
        series2 = [5, 4, 3, 2, 1]
        
        correlations = calculate_cross_correlation(series1, series2, max_lag=2)
        self.assertLess(correlations[0], -0.5)
    
    def test_cross_correlation_no_correlation(self):
        """Test cross-correlation with uncorrelated series"""
        series1 = [1, 2, 1, 2, 1]
        series2 = [3, 3, 3, 3, 3]  # Constant series
        
        correlations = calculate_cross_correlation(series1, series2, max_lag=2)
        self.assertAlmostEqual(correlations[0], 0.0, places=1)
    
    def test_cross_correlation_with_lag(self):
        """Test cross-correlation detects lagged relationship"""
        series1 = [1, 2, 3, 4, 5, 6, 7]
        series2 = [0, 0, 1, 2, 3, 4, 5]  # Lagged by 2
        
        correlations = calculate_cross_correlation(series1, series2, max_lag=3)
        
        # Correlation should be higher at lag 2
        self.assertGreater(abs(correlations[2]), abs(correlations[0]))
    
    def test_cross_correlation_empty_series(self):
        """Test cross-correlation handles empty series"""
        correlations = calculate_cross_correlation([], [], max_lag=2)
        self.assertEqual(correlations, [])
    
    def test_cross_correlation_mismatched_length(self):
        """Test cross-correlation handles mismatched lengths"""
        series1 = [1, 2, 3]
        series2 = [1, 2]
        
        correlations = calculate_cross_correlation(series1, series2, max_lag=2)
        self.assertEqual(correlations, [])
    
    def test_detect_lag_finds_peak(self):
        """Test lag detection finds peak correlation"""
        correlations = [0.2, 0.3, 0.8, 0.4, 0.1]
        lag = detect_lag(correlations)
        self.assertEqual(lag, 2)
    
    def test_detect_lag_negative_correlation(self):
        """Test lag detection handles negative correlations"""
        correlations = [0.2, -0.8, 0.3, 0.1]
        lag = detect_lag(correlations)
        self.assertEqual(lag, 1)  # Highest absolute value
    
    def test_detect_lag_empty_list(self):
        """Test lag detection handles empty list"""
        lag = detect_lag([])
        self.assertEqual(lag, 0)
    
    def test_granger_causality_basic(self):
        """Test Granger causality test basic functionality"""
        series1 = list(range(20))
        series2 = [x + random.uniform(-0.5, 0.5) for x in range(20)]
        
        result = granger_causality_test(series1, series2, max_lag=3)
        
        self.assertIn('lag', result)
        self.assertIn('score', result)
        self.assertGreaterEqual(result['lag'], 0)
        self.assertLessEqual(result['lag'], 3)
    
    def test_granger_causality_insufficient_data(self):
        """Test Granger causality with insufficient data"""
        series1 = [1, 2, 3]
        series2 = [4, 5, 6]
        
        result = granger_causality_test(series1, series2, max_lag=5)
        self.assertEqual(result['lag'], 0)
        self.assertEqual(result['score'], 0.0)
    
    def test_granger_causality_score_range(self):
        """Test Granger causality score is reasonable"""
        series1 = list(range(50))
        series2 = list(range(50))
        
        result = granger_causality_test(series1, series2, max_lag=5)
        
        # Score should be between -1 and 1 (improvement ratio)
        self.assertGreaterEqual(result['score'], -1.0)
        self.assertLessEqual(result['score'], 1.0)


class TestMockDataGenerators(unittest.TestCase):
    """Test mock data generators"""
    
    def test_generate_price_series_length(self):
        """Test price series generates correct length"""
        gen = MockDataGenerator()
        prices = gen.generate_price_series(length=50)
        self.assertEqual(len(prices), 50)
    
    def test_generate_price_series_range(self):
        """Test price series stays in valid range"""
        gen = MockDataGenerator()
        prices = gen.generate_price_series(length=100, volatility=0.1)
        
        for timestamp, price in prices:
            self.assertGreaterEqual(price, 0.01)
            self.assertLessEqual(price, 0.99)
    
    def test_generate_price_series_trend(self):
        """Test price series respects trend"""
        gen = MockDataGenerator()
        prices_up = gen.generate_price_series(length=100, start_price=0.5, trend=1.0)
        prices_down = gen.generate_price_series(length=100, start_price=0.5, trend=-1.0)
        
        # Uptrend should end higher than downtrend
        self.assertGreater(prices_up[-1][1], prices_down[-1][1])
    
    def test_generate_volume_series_positive(self):
        """Test volume series generates positive volumes"""
        gen = MockDataGenerator()
        volumes = gen.generate_volume_series(length=50)
        
        for timestamp, volume in volumes:
            self.assertGreater(volume, 0)
    
    def test_generate_hype_signals_count(self):
        """Test hype signals generates correct count"""
        gen = MockDataGenerator()
        signals = gen.generate_hype_signals(length=30)
        self.assertEqual(len(signals), 30)
    
    def test_generate_hype_signals_intensity(self):
        """Test hype signals respects intensity"""
        gen = MockDataGenerator()
        signals_low = gen.generate_hype_signals(length=50, intensity='low')
        signals_high = gen.generate_hype_signals(length=50, intensity='high')
        
        avg_sentiment_low = sum(s['sentiment'] for s in signals_low) / len(signals_low)
        avg_sentiment_high = sum(s['sentiment'] for s in signals_high) / len(signals_high)
        
        self.assertGreater(avg_sentiment_high, avg_sentiment_low)
    
    def test_generate_tweets_count(self):
        """Test tweets generator creates correct count"""
        gen = MockDataGenerator()
        tweets = gen.generate_tweets(count=25)
        self.assertEqual(len(tweets), 25)
    
    def test_generate_tweets_contains_keyword(self):
        """Test tweets contain market keyword"""
        gen = MockDataGenerator()
        tweets = gen.generate_tweets(count=10, market_keyword='ETH')
        
        for tweet in tweets:
            self.assertIn('ETH', tweet['text'])
    
    def test_generate_market_data_format(self):
        """Test market data has correct format"""
        gen = MockDataGenerator()
        market = gen.generate_market_data()
        
        self.assertIn('market_id', market)
        self.assertIn('question', market)
        self.assertIn('volume', market)
        self.assertIn('liquidity', market)
    
    def test_generate_correlation_data_length(self):
        """Test correlation data generates correct length"""
        gen = MockDataGenerator()
        series1, series2 = gen.generate_correlation_data(length=100)
        
        self.assertEqual(len(series1), 100)
        self.assertEqual(len(series2), 100)
    
    def test_generate_correlation_data_correlation(self):
        """Test correlation data has expected correlation"""
        gen = MockDataGenerator()
        series1, series2 = gen.generate_correlation_data(length=100, correlation=0.9, lag=0)
        
        # Calculate simple correlation
        mean1 = sum(series1) / len(series1)
        mean2 = sum(series2) / len(series2)
        
        covariance = sum((series1[i] - mean1) * (series2[i] - mean2) for i in range(len(series1)))
        std1 = math.sqrt(sum((x - mean1) ** 2 for x in series1))
        std2 = math.sqrt(sum((x - mean2) ** 2 for x in series2))
        
        correlation = covariance / (std1 * std2) if std1 > 0 and std2 > 0 else 0
        
        self.assertGreater(abs(correlation), 0.5)  # Should be reasonably correlated


# ============================================================================
# CLI INTERFACE
# ============================================================================

def print_summary():
    """Print test summary"""
    print("\n" + "="*70)
    print("POLYMARKET TRADING SYSTEM - TEST SUITE SUMMARY")
    print("="*70)
    print("\nTest Coverage:")
    print("  ✓ Signal Generation (RVR, ROC, Hype Score, Confirmation)")
    print("  ✓ Risk Management (Kelly, Stop Loss, Take Profit, Circuit Breaker)")
    print("  ✓ Data Validation (Price, Timestamp, Market ID)")
    print("  ✓ Database Operations (Insert, Query, Update, Indexes)")
    print("  ✓ Correlation Analysis (Cross-Correlation, Lag Detection, Granger)")
    print("  ✓ Mock Data Generators (Prices, Volumes, Signals, Tweets)")
    print("\nTotal Test Cases: 50+")
    print("="*70 + "\n")


def run_tests(module=None, verbose=False):
    """Run test suite with optional module filter"""
    
    # Map module names to test classes
    module_map = {
        'signals': TestSignalGeneration,
        'risk': TestRiskManagement,
        'validation': TestDataValidation,
        'database': TestDatabaseOperations,
        'correlation': TestCorrelationAnalysis,
        'mocks': TestMockDataGenerators
    }
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if module and module in module_map:
        # Load specific module
        suite.addTests(loader.loadTestsFromTestCase(module_map[module]))
        print(f"\n▶ Running tests for module: {module}\n")
    else:
        # Load all tests
        for test_class in module_map.values():
            suite.addTests(loader.loadTestsFromTestCase(test_class))
        print("\n▶ Running all tests\n")
    
    # Run tests
    verbosity = 2 if verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*70}\n")
    
    return result.wasSuccessful()


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive Test Suite for Polymarket Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_suite.py                    # Run all tests
  python test_suite.py --module signals   # Test signal generation only
  python test_suite.py --verbose          # Detailed output
  python test_suite.py --coverage         # Show coverage summary
        """
    )
    
    parser.add_argument(
        '--module',
        choices=['signals', 'risk', 'validation', 'database', 'correlation', 'mocks'],
        help='Run tests for specific module only'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose test output'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Show test coverage summary'
    )
    
    args = parser.parse_args()
    
    if args.coverage:
        print_summary()
        return 0
    
    # Run tests
    success = run_tests(module=args.module, verbose=args.verbose)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
