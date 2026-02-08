# Smart Rate Limiter - Usage Guide

## 🚀 Quick Start

```python
from rate_limiter import polymarket_limiter, twitter_limiter

# Decorator pattern (recommended)
@polymarket_limiter.limit
def fetch_markets():
    response = requests.get("https://api.polymarket.com/markets")
    return response.json()

markets = fetch_markets()  # Automatically rate limited!
```

## 📦 Features

✅ **Token bucket algorithm** - Smooth rate limiting with burst support  
✅ **Adaptive delays** - Automatically slows down on 429 errors, recovers gradually  
✅ **Exponential backoff** - Retries failed requests: 1s → 2s → 4s → 8s → 16s  
✅ **Statistics tracking** - Monitor request counts, latency, rate limit hits  
✅ **Thread-safe** - Use across multiple threads safely  
✅ **Zero dependencies** - Pure Python standard library  

## 🎯 Usage Patterns

### Pattern 1: Decorator (Best for most cases)

```python
from rate_limiter import RateLimiter

limiter = RateLimiter("my_api", requests_per_minute=60)

@limiter.limit
def call_api(endpoint):
    return requests.get(f"https://api.example.com/{endpoint}")

# Automatically rate limited + retry on failure
result = call_api("data")
```

### Pattern 2: Manual Control (Fine-grained)

```python
limiter.wait()  # Block until rate limit allows

response = requests.get("https://api.example.com/data")

if response.status_code == 200:
    limiter.record_success(latency=response.elapsed.total_seconds())
elif response.status_code == 429:
    limiter.record_failure(is_429=True)
else:
    limiter.record_failure()
```

### Pattern 3: Predefined Limiters

```python
from rate_limiter import polymarket_limiter, twitter_limiter

@polymarket_limiter.limit  # 60 req/min
def get_polymarket_data():
    pass

@twitter_limiter.limit  # 30 req/min (conservative)
def scrape_tweets():
    pass
```

## 📊 Statistics

```python
stats = limiter.get_stats()

print(f"Total requests: {stats['total_requests']}")
print(f"Success rate: {stats['successful_requests'] / stats['total_requests']:.1%}")
print(f"Avg latency: {stats['average_latency_ms']:.2f}ms")
print(f"Rate limit hits: {stats['rate_limit_hits']}")
print(f"Current rate: {stats['adaptive_multiplier']:.0%} of normal")
```

Example output:
```
Total requests: 150
Success rate: 98.7%
Avg latency: 245.32ms
Rate limit hits: 2
Current rate: 50% of normal
```

## 🧠 Adaptive Rate Limiting

The limiter automatically adjusts to API health:

1. **Normal operation**: 100% of configured rate (e.g., 60 req/min)
2. **After 429 error**: Immediately drops to 50% (30 req/min)
3. **Recovery**: After 60s without 429s, gradually increases back to 100% (10% every 10s)

This prevents hammering rate-limited APIs and speeds recovery.

## 🔄 Exponential Backoff

On request failure, automatic retry with delays:

| Attempt | Delay |
|---------|-------|
| 1       | 1s    |
| 2       | 2s    |
| 3       | 4s    |
| 4       | 8s    |
| 5       | 16s   |
| 6+      | Give up (raise exception) |

## 🛠️ Advanced Usage

### Custom Rate Limits

```python
# Conservative rate for fragile API
gentle_limiter = RateLimiter("fragile_api", requests_per_minute=10)

# Aggressive rate for robust API
fast_limiter = RateLimiter("robust_api", requests_per_minute=300)
```

### Timeout on Wait

```python
# Don't wait forever
if limiter.wait(timeout=5.0):  # Wait max 5 seconds
    response = requests.get(url)
else:
    print("Rate limit timeout, skipping request")
```

### Reset Statistics

```python
limiter.reset_stats()  # Clear counters (doesn't affect rate limiting state)
```

### Multiple APIs in Same Code

```python
poly_limiter = RateLimiter("polymarket", requests_per_minute=60)
twitter_limiter = RateLimiter("twitter", requests_per_minute=30)
coingecko_limiter = RateLimiter("coingecko", requests_per_minute=50)

@poly_limiter.limit
def fetch_poly():
    pass

@twitter_limiter.limit
def fetch_twitter():
    pass

@coingecko_limiter.limit
def fetch_prices():
    pass
```

## 🧪 Testing

Run the test suite:

```bash
python test_rate_limiter.py
```

Or run the demo built into the module:

```bash
python rate-limiter.py
```

## 🔒 Thread Safety

All methods are thread-safe. Use the same limiter across multiple threads:

```python
import threading

limiter = RateLimiter("shared", requests_per_minute=60)

def worker(thread_id):
    for i in range(10):
        limiter.wait()
        print(f"Thread {thread_id}, request {i}")
        limiter.record_success()

threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
for t in threads:
    t.start()
for t in threads:
    t.join()

print(limiter.get_stats())  # All requests tracked correctly
```

## 💡 Best Practices

1. **Use predefined limiters** when possible (`polymarket_limiter`, `twitter_limiter`)
2. **Be conservative** with external APIs - start low, increase if stable
3. **Monitor statistics** - Check `rate_limit_hits` to tune limits
4. **Prefer decorator pattern** - Cleaner code, automatic retry
5. **Log adaptive changes** - Set up logging to see rate adjustments:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔧 Integration Example

```python
# trading_bot.py
from rate_limiter import polymarket_limiter, twitter_limiter
import requests

@polymarket_limiter.limit
def get_market_prices(market_id):
    """Fetch current market prices"""
    response = requests.get(
        f"https://api.polymarket.com/markets/{market_id}/prices"
    )
    response.raise_for_status()
    return response.json()

@twitter_limiter.limit
def get_trending_topics():
    """Scrape trending topics"""
    # snscrape or twitter API call here
    pass

# Main trading loop
while True:
    try:
        prices = get_market_prices("some-market-id")
        trends = get_trending_topics()
        
        # Trading logic here
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Check stats periodically
    if iteration % 100 == 0:
        stats = polymarket_limiter.get_stats()
        print(f"Polymarket: {stats['successful_requests']}/{stats['total_requests']} success")
```

## 📈 Performance

- **Overhead**: ~0.1ms per `wait()` call (negligible)
- **Memory**: O(1) - fixed size buffers (last 100 latencies)
- **CPU**: Minimal - simple math, no busy-waiting

Great success! 🎉
