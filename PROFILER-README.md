# Performance Profiler for Polymarket Trading System

A lightweight, production-ready performance monitoring module for tracking system resources, timing metrics, and detecting bottlenecks.

## 🚀 Quick Start

```bash
# Quick 1-minute profile with demo
python performance-profiler.py

# Extended 10-minute profile
python performance-profiler.py --extended

# Continuous monitoring (Ctrl+C to stop)
python performance-profiler.py --monitor

# Generate HTML report
python performance-profiler.py --report perf.html --duration 60
```

## 📊 Features

### 1. Resource Monitoring
- CPU usage per component
- Memory usage (RSS, VMS)
- Disk I/O (reads/writes in MB/s)
- Network usage (send/receive in MB/s)
- Thread count

### 2. Timing Metrics
- Mean, median, min, max
- Percentiles: P50, P95, P99
- Standard deviation
- Operation counts
- Total time spent

### 3. Bottleneck Detection
- Automatically identifies slow operations (>500ms)
- Flags high CPU usage (>80%)
- Detects high memory usage (>1GB)
- Provides optimization suggestions

### 4. Trend Analysis
- Tracks metrics over time
- Detects performance degradation
- Alerts on anomalies (3x baseline)
- Compares recent vs historical data

### 5. Multiple Output Formats
- **Console**: Formatted summary with colors
- **JSON**: Machine-readable metrics export
- **HTML**: Interactive report with charts (Plotly.js)

## 🔧 Integration Examples

### Context Manager (Recommended)

```python
from performance_profiler import Profiler

with Profiler("data-collector", "fetch_markets"):
    markets = fetch_polymarket_data()
    process_markets(markets)
```

### Decorator

```python
from performance_profiler import profile

@profile("signal-generator", "analyze_market")
def analyze_market(market_data):
    indicators = calculate_indicators(market_data)
    return generate_signals(indicators)
```

### Manual Timing

```python
from performance_profiler import get_collector
import time

collector = get_collector()

start = time.time()
result = expensive_operation()
duration = time.time() - start

collector.record_timing("api", "polymarket_query", duration, metadata={
    "market_id": "12345",
    "success": True
})
```

### Background Monitoring

```python
from performance_profiler import BackgroundMonitor, get_collector

collector = get_collector()
monitor = BackgroundMonitor(collector, interval=2.0)

monitor.start()  # Start background monitoring

try:
    run_trading_bot()  # Your application
finally:
    monitor.stop()
    collector.generate_html_report("performance.html")
```

## 📋 CLI Options

```bash
# Duration modes
python performance-profiler.py                  # 1-minute quick check
python performance-profiler.py --extended       # 10-minute profile
python performance-profiler.py --duration 30    # Custom 30 seconds
python performance-profiler.py --monitor        # Continuous (Ctrl+C to stop)

# Output options
python performance-profiler.py --report perf.html     # HTML report
python performance-profiler.py --json metrics.json    # JSON export

# Other options
python performance-profiler.py --demo           # Run demo workload
python performance-profiler.py --interval 0.5   # Sample every 0.5s (default: 1.0)
python performance-profiler.py --component data-collector  # Filter component
```

## 📈 Output Examples

### Console Summary

```
================================================================================
⚡ PERFORMANCE PROFILE SUMMARY
================================================================================

📅 Duration: 60.2 seconds
🕐 Started: 2026-02-06 05:54:32

📊 RESOURCE USAGE
--------------------------------------------------------------------------------
  CPU:     18.5% avg  |  2.3% min  |  45.2% max
  Memory:  87.3 MB avg  |  85.1 MB min  |  92.7 MB max
  Threads: 8 avg  |  8 min  |  9 max
  Disk I/O: ↓0.15 MB/s  |  ↑0.08 MB/s
  Network:  ↓2.34 MB/s  |  ↑0.87 MB/s

⏱️  TIMING STATISTICS
--------------------------------------------------------------------------------
Component:Operation                          Count       Mean        P95        P99
--------------------------------------------------------------------------------
api:call                                       123     248.7ms    389.2ms    395.6ms
signal-generator:analyze_market                 45     201.3ms    287.5ms    298.1ms
data-collector:fetch_markets                   500      98.2ms    147.3ms    149.8ms
database:query                                 234      28.3ms     47.1ms     48.9ms

🔍 BOTTLENECKS DETECTED
--------------------------------------------------------------------------------
1. [slow_operation]
   Operation api:call is slow (avg 0.25s). Consider optimization.

✅ No performance degradation detected
```

### JSON Export

```json
{
  "start_time": 1707231272.5,
  "duration": 60.2,
  "timing_stats": {
    "api:call": {
      "count": 123,
      "mean": 0.2487,
      "median": 0.2401,
      "p95": 0.3892,
      "p99": 0.3956,
      "max": 0.4123
    }
  },
  "resource_stats": {
    "cpu_percent": {
      "mean": 18.5,
      "max": 45.2
    }
  },
  "bottlenecks": [...],
  "anomalies": [...]
}
```

### HTML Report

The HTML report includes:
- Interactive time-series charts (CPU, memory over time)
- Sortable tables with all timing statistics
- Color-coded bottleneck warnings
- Performance degradation alerts
- Anomaly timeline

## 🎯 Use Cases

### 1. Daily Health Check
Run once per day to verify system performance:
```bash
python performance-profiler.py --duration 60 --report daily-$(date +%Y%m%d).html
```

### 2. Production Monitoring
Continuous monitoring with periodic JSON exports:
```bash
python performance-profiler.py --monitor --json production-metrics.json
```

### 3. Optimization Testing
Compare performance before/after changes:
```bash
# Before
python performance-profiler.py --duration 300 --report before.html

# Make changes...

# After
python performance-profiler.py --duration 300 --report after.html
```

### 4. Component Profiling
Profile specific components in your code:
```python
@profile("data-collector")
def main_collection_loop():
    while True:
        fetch_markets()
        fetch_prices()
        time.sleep(60)
```

## 🔍 Bottleneck Detection

The profiler automatically detects:

| Type | Threshold | Action |
|------|-----------|--------|
| Slow operation | Mean > 500ms | Suggests optimization |
| High CPU | Average > 80% | Suggests scaling/optimization |
| High memory | Average > 1GB | Suggests memory leak check |
| CPU degradation | 50%+ increase | Alerts on trend |
| Memory degradation | 30%+ increase | Alerts on trend |
| Anomalies | 3x baseline | Flags unusual spikes |

## 📊 Metrics Dictionary

### Timing Metrics
- **Count**: Number of times operation was executed
- **Mean**: Average duration
- **Median (P50)**: 50th percentile (middle value)
- **P95**: 95th percentile (95% of calls faster than this)
- **P99**: 99th percentile (99% of calls faster than this)
- **Max**: Slowest execution time

### Resource Metrics
- **CPU %**: Process CPU usage (can exceed 100% on multi-core)
- **RSS**: Resident Set Size (actual RAM used)
- **VMS**: Virtual Memory Size (total allocated)
- **Disk I/O**: Read/write rates in MB/s
- **Network I/O**: Send/receive rates in MB/s

## ⚙️ Configuration

### Sampling Interval
```bash
python performance-profiler.py --interval 0.5  # Sample every 0.5 seconds
```

Lower interval = more granular data, higher overhead
Higher interval = less overhead, might miss spikes

**Recommended**: 1.0s for production, 0.5s for debugging

### History Size
```python
from performance_profiler import MetricsCollector

collector = MetricsCollector(max_history=50000)  # Keep 50k samples
```

## 💾 Storage & Performance

- **Memory footprint**: ~1MB per 1000 samples
- **CPU overhead**: < 1% with 1s interval
- **Disk I/O**: Minimal (only on report generation)

The profiler is designed to be lightweight and suitable for continuous production monitoring.

## 🛠️ Troubleshooting

### High Memory Usage
If the profiler itself uses too much memory, reduce history:
```python
collector = MetricsCollector(max_history=5000)
```

### Missing Metrics
If disk I/O or other metrics are missing:
- Check if `psutil` has necessary permissions
- Some metrics require elevated privileges on Windows

### Inaccurate Timing
For more accurate timing in tight loops:
```python
import time
start = time.perf_counter()  # More precise than time.time()
# ... operation ...
duration = time.perf_counter() - start
```

## 📚 API Reference

### Profiler(component, operation, collector)
Context manager for profiling code blocks.

### @profile(component, operation)
Decorator for profiling functions.

### get_collector()
Get the global MetricsCollector instance.

### MetricsCollector
Main class for collecting and analyzing metrics.

**Methods:**
- `record_timing(component, operation, duration, metadata)`
- `record_resource_sample()`
- `get_timing_stats(component, operation)`
- `get_resource_stats()`
- `detect_bottlenecks()`
- `detect_degradation(window_minutes=5)`
- `export_json(filepath)`
- `generate_html_report(filepath)`

### BackgroundMonitor(collector, interval)
Background thread for continuous resource monitoring.

**Methods:**
- `start()` - Start monitoring
- `stop()` - Stop monitoring

## 🎉 Great Success!

This profiler gives you full visibility into your Polymarket trading system's performance. Use it to:

- ✅ Monitor production systems
- ✅ Identify bottlenecks
- ✅ Optimize slow operations
- ✅ Detect performance regressions
- ✅ Track resource usage over time
- ✅ Generate reports for stakeholders

**Questions?** Check `PROFILER-DEMO-OUTPUT.md` for detailed examples.
