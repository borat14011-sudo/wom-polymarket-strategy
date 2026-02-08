"""
Smart Rate Limiter for API Calls

A thread-safe rate limiting module using token bucket algorithm with adaptive
delays, exponential backoff, and comprehensive statistics tracking.

Features:
- Token bucket algorithm for burst handling
- Adaptive rate adjustment on 429 errors
- Exponential backoff (1s, 2s, 4s, 8s, 16s)
- Request queuing and statistics
- Thread-safe design
- No external dependencies

Usage Examples:

    # Decorator pattern
    from rate_limiter import RateLimiter
    
    limiter = RateLimiter("polymarket", requests_per_minute=60)
    
    @limiter.limit
    def fetch_markets():
        return requests.get("https://api.polymarket.com/markets")
    
    result = fetch_markets()  # Automatically rate limited
    
    # Manual control
    limiter.wait()  # Block until token available
    response = requests.get("https://api.polymarket.com/markets")
    if response.status_code == 200:
        limiter.record_success(latency=response.elapsed.total_seconds())
    else:
        limiter.record_failure(is_429=(response.status_code == 429))
    
    # Check statistics
    stats = limiter.get_stats()
    print(f"Total requests: {stats['total_requests']}")
    print(f"Success rate: {stats['successful_requests'] / stats['total_requests']:.2%}")
    print(f"Avg latency: {stats['average_latency_ms']:.2f}ms")
    
    # Predefined limiters
    from rate_limiter import polymarket_limiter, twitter_limiter
    
    @polymarket_limiter.limit
    def get_market_data():
        pass
    
    @twitter_limiter.limit
    def scrape_tweets():
        pass
"""

import threading
import time
from functools import wraps
from collections import deque
from typing import Optional, Callable, Any, Dict
import logging


class RateLimiter:
    """
    Thread-safe rate limiter using token bucket algorithm.
    
    Tokens are added at a constant rate (requests_per_minute / 60).
    Each request consumes one token. Supports bursts up to max bucket size.
    
    Args:
        name: Identifier for this limiter (for logging/stats)
        requests_per_minute: Maximum sustained request rate
    """
    
    def __init__(self, name: str, requests_per_minute: int = 60):
        self.name = name
        self.requests_per_minute = requests_per_minute
        self.tokens_per_second = requests_per_minute / 60.0
        
        # Token bucket state
        self.max_tokens = float(requests_per_minute)  # Allow full minute burst
        self.tokens = self.max_tokens
        self.last_update = time.time()
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Statistics
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.rate_limit_hits = 0
        self.latencies = deque(maxlen=100)  # Keep last 100 for average
        
        # Adaptive rate control
        self.adaptive_multiplier = 1.0  # Multiplier for token refill rate
        self.last_429_time = 0.0
        self.recovery_start_time = 0.0
        
        # Logging
        self.logger = logging.getLogger(f"RateLimiter.{name}")
    
    def _refill_tokens(self):
        """Refill token bucket based on elapsed time and adaptive multiplier."""
        now = time.time()
        elapsed = now - self.last_update
        
        # Calculate tokens to add (adjusted by adaptive multiplier)
        tokens_to_add = elapsed * self.tokens_per_second * self.adaptive_multiplier
        self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
        self.last_update = now
    
    def _adjust_rate(self, got_429: bool = False):
        """
        Adjust rate based on API health signals.
        
        On 429: Slow down to 50% of normal rate
        Recovery: After 60s without 429, gradually increase back to 100%
        """
        now = time.time()
        
        if got_429:
            self.rate_limit_hits += 1
            self.last_429_time = now
            self.recovery_start_time = 0.0
            
            # Immediate slowdown to 50%
            old_multiplier = self.adaptive_multiplier
            self.adaptive_multiplier = 0.5
            
            self.logger.warning(
                f"Rate limit hit! Slowing down: {old_multiplier:.2f} -> {self.adaptive_multiplier:.2f}"
            )
        else:
            # Gradual recovery after 60 seconds of healthy requests
            time_since_429 = now - self.last_429_time
            
            if time_since_429 > 60 and self.adaptive_multiplier < 1.0:
                if self.recovery_start_time == 0.0:
                    self.recovery_start_time = now
                
                # Recover 10% every 10 seconds
                recovery_elapsed = now - self.recovery_start_time
                recovery_steps = int(recovery_elapsed / 10)
                target_multiplier = min(1.0, 0.5 + (recovery_steps * 0.1))
                
                if target_multiplier > self.adaptive_multiplier:
                    old_multiplier = self.adaptive_multiplier
                    self.adaptive_multiplier = target_multiplier
                    self.logger.info(
                        f"Rate recovering: {old_multiplier:.2f} -> {self.adaptive_multiplier:.2f}"
                    )
    
    def wait(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until a token is available (blocks until ready).
        
        Args:
            timeout: Maximum seconds to wait. None = wait forever.
        
        Returns:
            True if token acquired, False if timeout reached
        """
        start_time = time.time()
        
        with self.lock:
            while True:
                self._refill_tokens()
                
                # Token available?
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    self.total_requests += 1
                    return True
                
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        self.logger.warning(f"Wait timeout after {elapsed:.2f}s")
                        return False
                
                # Calculate optimal wait time
                tokens_needed = 1.0 - self.tokens
                wait_time = tokens_needed / (self.tokens_per_second * self.adaptive_multiplier)
                wait_time = min(wait_time, 1.0)  # Cap at 1s to check conditions regularly
                
                # Release lock during sleep (allow other threads)
                self.lock.release()
                try:
                    time.sleep(wait_time)
                finally:
                    self.lock.acquire()
    
    def record_success(self, latency: Optional[float] = None):
        """
        Record a successful request.
        
        Args:
            latency: Request latency in seconds (optional)
        """
        with self.lock:
            self.successful_requests += 1
            if latency is not None:
                self.latencies.append(latency)
            self._adjust_rate(got_429=False)
    
    def record_failure(self, is_429: bool = False):
        """
        Record a failed request.
        
        Args:
            is_429: True if failure was due to rate limiting (HTTP 429)
        """
        with self.lock:
            self.failed_requests += 1
            if is_429:
                self._adjust_rate(got_429=True)
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with exponential backoff on failure.
        
        Retry delays: 1s, 2s, 4s, 8s, 16s (max 5 retries)
        Automatically detects 429 errors from HTTP response objects.
        
        Args:
            func: Function to execute
            *args, **kwargs: Arguments to pass to function
        
        Returns:
            Function result
        
        Raises:
            Exception: If all retries exhausted
        """
        max_retries = 5
        backoff_delays = [1, 2, 4, 8, 16]
        
        for attempt in range(max_retries + 1):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                latency = time.time() - start_time
                
                # Check for rate limit response (common HTTP pattern)
                is_429 = False
                if hasattr(result, 'status_code'):
                    if result.status_code == 429:
                        is_429 = True
                    elif result.status_code >= 400:
                        # Other error, but not rate limit
                        self.record_failure(is_429=False)
                        if attempt < max_retries:
                            delay = backoff_delays[attempt]
                            self.logger.warning(
                                f"HTTP {result.status_code}, retrying in {delay}s "
                                f"(attempt {attempt + 1}/{max_retries + 1})"
                            )
                            time.sleep(delay)
                            continue
                        else:
                            raise Exception(
                                f"Max retries exceeded: HTTP {result.status_code}"
                            )
                
                if is_429:
                    self.record_failure(is_429=True)
                    if attempt < max_retries:
                        delay = backoff_delays[attempt]
                        self.logger.warning(
                            f"Got 429, backing off {delay}s "
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Max retries exceeded after 429 errors")
                
                # Success!
                self.record_success(latency)
                return result
                
            except Exception as e:
                # Non-HTTP exception
                self.record_failure(is_429=False)
                
                if attempt < max_retries:
                    delay = backoff_delays[attempt]
                    self.logger.warning(
                        f"Exception {type(e).__name__}: {e}, retrying in {delay}s "
                        f"(attempt {attempt + 1}/{max_retries + 1})"
                    )
                    time.sleep(delay)
                else:
                    self.logger.error(f"Max retries exceeded: {e}")
                    raise
    
    def limit(self, func: Callable) -> Callable:
        """
        Decorator to rate limit a function with automatic retry.
        
        Usage:
            @limiter.limit
            def fetch_data():
                return requests.get(url)
        
        The decorated function will:
        1. Wait for rate limit token
        2. Execute the function
        3. Retry with exponential backoff on failure
        4. Record statistics
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait()
            return self.retry_with_backoff(func, *args, **kwargs)
        
        return wrapper
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current statistics.
        
        Returns:
            Dict with keys:
                - name: Limiter name
                - total_requests: Total requests attempted
                - successful_requests: Successful requests
                - failed_requests: Failed requests
                - rate_limit_hits: Number of 429 errors
                - average_latency_ms: Average latency in milliseconds
                - current_tokens: Current tokens in bucket
                - adaptive_multiplier: Current rate adjustment (1.0 = normal)
                - requests_per_minute: Configured rate limit
        """
        with self.lock:
            avg_latency = (
                sum(self.latencies) / len(self.latencies) 
                if self.latencies else 0.0
            )
            
            return {
                "name": self.name,
                "total_requests": self.total_requests,
                "successful_requests": self.successful_requests,
                "failed_requests": self.failed_requests,
                "rate_limit_hits": self.rate_limit_hits,
                "average_latency_ms": avg_latency * 1000,
                "current_tokens": self.tokens,
                "adaptive_multiplier": self.adaptive_multiplier,
                "requests_per_minute": self.requests_per_minute,
            }
    
    def reset_stats(self):
        """Reset all statistics counters (does not affect rate limiting state)."""
        with self.lock:
            self.total_requests = 0
            self.successful_requests = 0
            self.failed_requests = 0
            self.rate_limit_hits = 0
            self.latencies.clear()
    
    def __repr__(self):
        stats = self.get_stats()
        return (
            f"RateLimiter(name='{self.name}', "
            f"rpm={self.requests_per_minute}, "
            f"tokens={stats['current_tokens']:.1f}, "
            f"multiplier={stats['adaptive_multiplier']:.2f}, "
            f"requests={stats['total_requests']})"
        )


# Predefined limiters for common APIs
polymarket_limiter = RateLimiter("polymarket", requests_per_minute=60)
twitter_limiter = RateLimiter("twitter", requests_per_minute=30)


if __name__ == "__main__":
    # Demo / test
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Rate Limiter Demo")
    print("=" * 60)
    
    # Create a test limiter (10 requests/minute for quick demo)
    limiter = RateLimiter("demo", requests_per_minute=10)
    
    # Simulate some requests
    print(f"\nSimulating {15} rapid requests (limit: 10/min)...\n")
    
    for i in range(15):
        start = time.time()
        limiter.wait()
        elapsed = time.time() - start
        
        # Simulate request
        time.sleep(0.05)  # 50ms simulated latency
        limiter.record_success(latency=0.05)
        
        print(f"Request {i+1:2d} - waited {elapsed:.3f}s - {limiter.tokens:.2f} tokens remaining")
    
    # Show statistics
    print("\n" + "=" * 60)
    print("Statistics:")
    print("=" * 60)
    stats = limiter.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key:25s}: {value:.2f}")
        else:
            print(f"  {key:25s}: {value}")
    
    print("\n" + "=" * 60)
    print("Demo complete. Import this module to use in your project.")
    print("=" * 60)
