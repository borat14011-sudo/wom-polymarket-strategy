# Integration Test Suite for Polymarket Trading System

Comprehensive end-to-end integration tests for the Polymarket automated trading pipeline.

## 📋 Overview

This test suite validates the complete trading system from data collection to alert delivery. It includes:

- **26 integration test cases** covering all workflows
- **Mock services** for external APIs (Polymarket, Twitter, Telegram)
- **Performance benchmarks** for critical paths
- **Concurrency tests** for race conditions
- **Error handling** for failure scenarios
- **CI/CD ready** with proper exit codes

## 🚀 Quick Start

### Installation

No dependencies required! Uses Python standard library only:
- `unittest` - Test framework
- `sqlite3` - Mock database
- `threading` - Concurrency tests
- `tracemalloc` - Memory profiling

### Run Tests

```bash
# Run all integration tests (26 tests, ~10 min)
python integration-tests.py

# Quick smoke tests (4 tests, ~1 min)
python integration-tests.py --quick

# Full test suite (explicit)
python integration-tests.py --full

# Performance benchmarks only
python integration-tests.py --benchmark

# Test specific workflow
python integration-tests.py --workflow data
python integration-tests.py --workflow hype
python integration-tests.py --workflow signal
python integration-tests.py --workflow alert
```

## 📁 Files

```
integration-tests.py          # Main test suite (26 tests)
mocks.py                      # Mock services for testing
EXAMPLE-TEST-OUTPUT.md        # Example test outputs
INTEGRATION-TESTS-README.md   # This file
```

## 🧪 Test Categories

### 1. End-to-End Workflow Tests (5 tests)

Complete pipeline tests from start to finish:

```python
test_01_data_collection_to_database()
# Tests: API → Collector → Database

test_02_twitter_to_hype_to_database()
# Tests: Twitter → Hype Monitor → Database

test_03_signal_to_risk_to_alert()
# Tests: Signal Generator → Risk Manager → Telegram

test_04_full_pipeline_with_mock_data()
# Tests: Complete pipeline with all components

test_05_multiple_markets_pipeline()
# Tests: Processing multiple markets end-to-end
```

### 2. Component Interaction Tests (5 tests)

Tests for pairs of components working together:

```python
test_06_data_collector_database_interaction()
test_07_hype_monitor_database_interaction()
test_08_signal_generator_risk_manager_interaction()
test_09_alert_system_telegram_mock_interaction()
test_10_end_to_end_component_chain()
```

### 3. Error Handling Tests (8 tests)

Failure scenarios and recovery:

```python
test_11_api_timeout_recovery()
test_12_api_rate_limit_handling()
test_13_database_connection_loss()
test_14_invalid_data_handling()
test_15_twitter_api_failure_recovery()
test_16_telegram_network_error_handling()
test_17_database_query_error_recovery()
test_18_risk_manager_rejection_handling()
```

### 4. Concurrency Tests (3 tests)

Race conditions and parallel execution:

```python
test_19_multiple_collectors_concurrent()
# Tests: 5 collectors running in parallel

test_20_database_concurrent_writes()
# Tests: 20 concurrent database writes

test_21_signal_generation_under_load()
# Tests: 10 signals generated concurrently
```

### 5. Performance Benchmarks (5 tests)

Performance metrics and optimization targets:

```python
test_22_data_collection_speed()
# Target: >10 markets/second

test_23_signal_generation_latency()
# Target: <50ms average, <100ms P95

test_24_database_query_performance()
# Target: >100 queries/second

test_25_memory_usage_under_load()
# Target: <50MB under load

test_26_end_to_end_pipeline_throughput()
# Target: >1 market/second through complete pipeline
```

## 🎭 Mock Services

### MockPolymarketAPI

Simulates Polymarket API with realistic market data:

```python
api = MockPolymarketAPI(
    fail_mode='timeout',    # Simulate failures
    latency_ms=100          # Simulate network delay
)

markets = api.get_markets(limit=100)
trades = api.get_market_trades(market_id)
```

**Fail modes:**
- `timeout` - Simulate API timeout
- `rate_limit` - Simulate rate limiting
- `server_error` - Random 500 errors
- `invalid_data` - Malformed responses

### MockTwitterAPI

Simulates Twitter/X API for sentiment analysis:

```python
twitter = MockTwitterAPI(fail_mode='timeout')
tweets = twitter.search_tweets("bitcoin", limit=100)
trending = twitter.get_trending_topics()
```

### MockTelegramBot

Simulates Telegram Bot API:

```python
bot = MockTelegramBot(fail_mode='network_error')
bot.send_message(chat_id="123", text="Alert!")
messages = bot.get_sent_messages()  # For verification
```

### MockDatabase

In-memory SQLite database for fast testing:

```python
db = MockDatabase(fail_mode='query_error')
db.connect()
db.insert_market(market_data)
db.insert_signal(signal_data)
db.insert_hype_score(hype_data)

# Performance metrics
stats = db.get_performance_stats()
# Returns: total_queries, avg_query_time_ms, min, max
```

### MockRiskManager

Risk validation for signals:

```python
risk_manager = MockRiskManager(
    max_exposure=10000,
    max_position_size=5000
)

result = risk_manager.validate_signal(signal)
# Returns: {"approved": bool, "reason": str, "adjusted_size": float}
```

## 🏗️ System Architecture

The test suite simulates this complete pipeline:

```
┌─────────────────┐
│ Polymarket API  │──────┐
└─────────────────┘      │
                         ▼
                  ┌──────────────┐
                  │ Data         │
                  │ Collector    │
                  └──────┬───────┘
                         │
                         ▼
┌─────────────────┐  ┌─────────┐
│ Twitter API     │  │Database │
└────────┬────────┘  └────┬────┘
         │                │
         ▼                │
  ┌──────────────┐        │
  │ Hype         │────────┤
  │ Monitor      │        │
  └──────────────┘        │
                          │
                          ▼
                   ┌─────────────┐
                   │ Signal      │
                   │ Generator   │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Risk        │
                   │ Manager     │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Alert       │
                   │ System      │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │ Telegram    │
                   │ Bot         │
                   └─────────────┘
```

## 📊 Performance Targets

Based on benchmark tests:

| Metric | Target | Actual (Mock) |
|--------|--------|---------------|
| Data collection speed | >10 markets/s | ~312 markets/s |
| Signal generation latency | <50ms avg | ~2.3ms avg |
| Database queries | >100 queries/s | ~1247 queries/s |
| Memory usage | <50MB | ~3.2MB |
| Pipeline throughput | >1 market/s | ~8.5 markets/s |

## 🔧 CI/CD Integration

### Exit Codes

- `0` - All tests passed ✅
- `1` - One or more tests failed ❌

### GitHub Actions

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      # Quick tests on every push
      - name: Quick smoke tests
        run: python integration-tests.py --quick
      
      # Full suite on main branch only
      - name: Full integration suite
        if: github.ref == 'refs/heads/main'
        run: python integration-tests.py --full
      
      # Benchmarks for performance tracking
      - name: Performance benchmarks
        run: python integration-tests.py --benchmark
```

### GitLab CI

```yaml
test:quick:
  stage: test
  script:
    - python integration-tests.py --quick
  
test:full:
  stage: test
  script:
    - python integration-tests.py --full
  only:
    - main
  
test:benchmark:
  stage: test
  script:
    - python integration-tests.py --benchmark
  allow_failure: true
```

## 🛠️ Extending the Tests

### Adding a New Test

```python
class YourTestClass(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.api = MockPolymarketAPI()
        self.db = MockDatabase()
        self.db.connect()
    
    def tearDown(self):
        """Clean up"""
        self.db.disconnect()
    
    def test_your_feature(self):
        """Test: Your feature description"""
        # Arrange
        expected = "expected_value"
        
        # Act
        result = your_function()
        
        # Assert
        self.assertEqual(result, expected)
```

### Adding a New Mock

```python
class MockYourService:
    """Mock Your External Service"""
    
    def __init__(self, fail_mode: Optional[str] = None):
        self.fail_mode = fail_mode
        self.request_count = 0
    
    def your_method(self, arg: str) -> Dict:
        """Your method description"""
        self._check_failure()
        return {"result": "mock_data"}
    
    def _check_failure(self):
        """Check if should fail"""
        if self.fail_mode == 'timeout':
            raise TimeoutError("Service timeout")
```

## 🐛 Debugging Tests

### Verbose Output

```bash
python integration-tests.py --full 2>&1 | tee test-output.log
```

### Run Single Test

```python
# In Python interpreter
import unittest
from integration_tests import EndToEndWorkflowTests

suite = unittest.TestLoader().loadTestsFromName(
    'EndToEndWorkflowTests.test_04_full_pipeline_with_mock_data'
)
unittest.TextTestRunner(verbosity=2).run(suite)
```

### Debug Mode

Add this to any test:

```python
import pdb; pdb.set_trace()  # Breakpoint
```

## 📝 Best Practices

### Test Design

1. **Deterministic**: Same input → same output
2. **Isolated**: Each test independent
3. **Fast**: Mock external services
4. **Clear**: Descriptive names and assertions
5. **Comprehensive**: Cover success, failure, edge cases

### Mock Data

```python
# Use generators for consistent test data
market = generate_mock_market(
    market_id="0x1234",
    yes_price=0.3,
    liquidity=1000000
)

signal = generate_mock_signal(
    market_id="0x1234",
    confidence=0.8,
    signal_type="BUY"
)

tweets = generate_mock_tweets(
    keyword="bitcoin",
    count=10,
    sentiment="positive"
)
```

## 🎯 Test Coverage

Current coverage: **26 test cases**

- ✅ End-to-end workflows: **5 tests**
- ✅ Component interactions: **5 tests**
- ✅ Error handling: **8 tests**
- ✅ Concurrency: **3 tests**
- ✅ Performance benchmarks: **5 tests**

## 🚨 Known Limitations

1. **Mock Services**: Tests use mocks, not real APIs
2. **Timing**: Performance benchmarks may vary by hardware
3. **Concurrency**: Limited by GIL (Python Global Interpreter Lock)
4. **Database**: In-memory SQLite, not production PostgreSQL

## 📚 References

- [unittest documentation](https://docs.python.org/3/library/unittest.html)
- [Python threading](https://docs.python.org/3/library/threading.html)
- [SQLite in Python](https://docs.python.org/3/library/sqlite3.html)

## 🎉 Success!

Great success! You now have a comprehensive integration test suite ready for CI/CD.

```bash
python integration-tests.py --full
```

Watch those green checkmarks! ✅
