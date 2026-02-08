#!/usr/bin/env python3
"""
Performance Profiler for Polymarket Trading System

Monitors system resources, tracks timing metrics, detects bottlenecks,
and generates comprehensive performance reports.
"""

import psutil
import time
import json
import argparse
import sys
import os
import statistics
from datetime import datetime, timedelta
from collections import defaultdict, deque
from contextlib import contextmanager
from functools import wraps
from typing import Dict, List, Optional, Any, Callable
import threading
import signal


class MetricsCollector:
    """Collects and stores performance metrics"""
    
    def __init__(self, max_history: int = 10000):
        self.max_history = max_history
        self.timings = defaultdict(lambda: deque(maxlen=max_history))
        self.resource_samples = deque(maxlen=max_history)
        self.component_resources = defaultdict(lambda: deque(maxlen=max_history))
        self.anomalies = []
        self.start_time = time.time()
        self.process = psutil.Process()
        
        # Baseline metrics for anomaly detection
        self.baselines = {
            'cpu_percent': None,
            'memory_mb': None,
            'disk_read_mb': None,
            'disk_write_mb': None,
        }
        
    def record_timing(self, component: str, operation: str, duration: float, metadata: Optional[Dict] = None):
        """Record a timing metric"""
        timestamp = time.time()
        record = {
            'timestamp': timestamp,
            'duration': duration,
            'metadata': metadata or {}
        }
        key = f"{component}:{operation}"
        self.timings[key].append(record)
        
    def record_resource_sample(self):
        """Record current resource usage"""
        try:
            # CPU
            cpu_percent = self.process.cpu_percent(interval=0.1)
            
            # Memory
            mem_info = self.process.memory_info()
            memory_rss_mb = mem_info.rss / (1024 * 1024)
            memory_vms_mb = mem_info.vms / (1024 * 1024)
            
            # Disk I/O
            io_counters = self.process.io_counters() if hasattr(self.process, 'io_counters') else None
            disk_read_mb = io_counters.read_bytes / (1024 * 1024) if io_counters else 0
            disk_write_mb = io_counters.write_bytes / (1024 * 1024) if io_counters else 0
            
            # Network I/O (system-wide)
            net_io = psutil.net_io_counters()
            net_sent_mb = net_io.bytes_sent / (1024 * 1024)
            net_recv_mb = net_io.bytes_recv / (1024 * 1024)
            
            sample = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_rss_mb': memory_rss_mb,
                'memory_vms_mb': memory_vms_mb,
                'disk_read_mb': disk_read_mb,
                'disk_write_mb': disk_write_mb,
                'net_sent_mb': net_sent_mb,
                'net_recv_mb': net_recv_mb,
                'num_threads': self.process.num_threads(),
            }
            
            self.resource_samples.append(sample)
            self._check_anomalies(sample)
            
            return sample
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
            
    def _check_anomalies(self, sample: Dict):
        """Check for anomalous resource usage"""
        # Update baselines if not set
        if len(self.resource_samples) < 10:
            return
            
        if self.baselines['cpu_percent'] is None:
            recent = list(self.resource_samples)[-100:]
            self.baselines['cpu_percent'] = statistics.mean([s['cpu_percent'] for s in recent])
            self.baselines['memory_mb'] = statistics.mean([s['memory_rss_mb'] for s in recent])
            
        # Check for anomalies (3x baseline)
        if sample['cpu_percent'] > self.baselines['cpu_percent'] * 3 and sample['cpu_percent'] > 50:
            self.anomalies.append({
                'timestamp': sample['timestamp'],
                'type': 'high_cpu',
                'value': sample['cpu_percent'],
                'baseline': self.baselines['cpu_percent']
            })
            
        if sample['memory_rss_mb'] > self.baselines['memory_mb'] * 2:
            self.anomalies.append({
                'timestamp': sample['timestamp'],
                'type': 'high_memory',
                'value': sample['memory_rss_mb'],
                'baseline': self.baselines['memory_mb']
            })
    
    def get_timing_stats(self, component: str, operation: str) -> Dict:
        """Calculate timing statistics for a component/operation"""
        key = f"{component}:{operation}"
        timings = self.timings.get(key, deque())
        
        if not timings:
            return None
            
        durations = [t['duration'] for t in timings]
        
        return {
            'count': len(durations),
            'total': sum(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'min': min(durations),
            'max': max(durations),
            'stdev': statistics.stdev(durations) if len(durations) > 1 else 0,
            'p50': self._percentile(durations, 50),
            'p95': self._percentile(durations, 95),
            'p99': self._percentile(durations, 99),
        }
    
    def get_all_timing_stats(self) -> Dict:
        """Get timing stats for all components/operations"""
        stats = {}
        for key in self.timings.keys():
            component, operation = key.split(':', 1)
            stats[key] = self.get_timing_stats(component, operation)
        return stats
    
    def get_resource_stats(self) -> Dict:
        """Calculate resource usage statistics"""
        if not self.resource_samples:
            return None
            
        samples = list(self.resource_samples)
        
        stats = {
            'cpu_percent': self._calc_stats([s['cpu_percent'] for s in samples]),
            'memory_rss_mb': self._calc_stats([s['memory_rss_mb'] for s in samples]),
            'memory_vms_mb': self._calc_stats([s['memory_vms_mb'] for s in samples]),
            'num_threads': self._calc_stats([s['num_threads'] for s in samples]),
        }
        
        # Calculate disk I/O rate (MB/s)
        if len(samples) > 1:
            first, last = samples[0], samples[-1]
            duration = last['timestamp'] - first['timestamp']
            if duration > 0:
                stats['disk_read_rate_mb_s'] = (last['disk_read_mb'] - first['disk_read_mb']) / duration
                stats['disk_write_rate_mb_s'] = (last['disk_write_mb'] - first['disk_write_mb']) / duration
                stats['net_sent_rate_mb_s'] = (last['net_sent_mb'] - first['net_sent_mb']) / duration
                stats['net_recv_rate_mb_s'] = (last['net_recv_mb'] - first['net_recv_mb']) / duration
        
        return stats
    
    def _calc_stats(self, values: List[float]) -> Dict:
        """Calculate statistics for a list of values"""
        if not values:
            return None
        return {
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'min': min(values),
            'max': max(values),
            'stdev': statistics.stdev(values) if len(values) > 1 else 0,
        }
    
    def _percentile(self, values: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def detect_bottlenecks(self) -> List[Dict]:
        """Detect performance bottlenecks"""
        bottlenecks = []
        
        # Check timing bottlenecks (slowest operations)
        timing_stats = self.get_all_timing_stats()
        if timing_stats:
            sorted_by_mean = sorted(timing_stats.items(), key=lambda x: x[1]['mean'], reverse=True)
            for key, stats in sorted_by_mean[:5]:  # Top 5 slowest
                if stats['mean'] > 0.5:  # Slower than 500ms
                    bottlenecks.append({
                        'type': 'slow_operation',
                        'component_operation': key,
                        'mean_duration': stats['mean'],
                        'p99_duration': stats['p99'],
                        'count': stats['count'],
                        'suggestion': f"Operation {key} is slow (avg {stats['mean']:.2f}s). Consider optimization."
                    })
        
        # Check resource bottlenecks
        resource_stats = self.get_resource_stats()
        if resource_stats:
            if resource_stats['cpu_percent']['mean'] > 80:
                bottlenecks.append({
                    'type': 'high_cpu',
                    'value': resource_stats['cpu_percent']['mean'],
                    'suggestion': 'High CPU usage detected. Consider optimization or scaling.'
                })
            
            if resource_stats['memory_rss_mb']['mean'] > 1000:  # > 1GB
                bottlenecks.append({
                    'type': 'high_memory',
                    'value': resource_stats['memory_rss_mb']['mean'],
                    'suggestion': 'High memory usage detected. Check for memory leaks or optimize data structures.'
                })
        
        return bottlenecks
    
    def detect_degradation(self, window_minutes: int = 5) -> List[Dict]:
        """Detect performance degradation over time"""
        degradations = []
        
        if len(self.resource_samples) < 100:
            return degradations
        
        cutoff_time = time.time() - (window_minutes * 60)
        recent_samples = [s for s in self.resource_samples if s['timestamp'] > cutoff_time]
        older_samples = [s for s in self.resource_samples if s['timestamp'] <= cutoff_time]
        
        if not recent_samples or not older_samples:
            return degradations
        
        # Compare recent vs older metrics
        recent_cpu = statistics.mean([s['cpu_percent'] for s in recent_samples])
        older_cpu = statistics.mean([s['cpu_percent'] for s in older_samples])
        
        if recent_cpu > older_cpu * 1.5 and recent_cpu > 30:  # 50% increase
            degradations.append({
                'type': 'cpu_degradation',
                'recent': recent_cpu,
                'baseline': older_cpu,
                'increase_percent': ((recent_cpu - older_cpu) / older_cpu * 100)
            })
        
        recent_mem = statistics.mean([s['memory_rss_mb'] for s in recent_samples])
        older_mem = statistics.mean([s['memory_rss_mb'] for s in older_samples])
        
        if recent_mem > older_mem * 1.3:  # 30% increase
            degradations.append({
                'type': 'memory_degradation',
                'recent': recent_mem,
                'baseline': older_mem,
                'increase_percent': ((recent_mem - older_mem) / older_mem * 100)
            })
        
        return degradations
    
    def export_json(self, filepath: str):
        """Export metrics to JSON file"""
        data = {
            'start_time': self.start_time,
            'duration': time.time() - self.start_time,
            'timing_stats': self.get_all_timing_stats(),
            'resource_stats': self.get_resource_stats(),
            'bottlenecks': self.detect_bottlenecks(),
            'degradations': self.detect_degradation(),
            'anomalies': self.anomalies[-100:],  # Last 100 anomalies
            'resource_samples': list(self.resource_samples)[-1000:],  # Last 1000 samples
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def generate_html_report(self, filepath: str):
        """Generate HTML report with charts"""
        timing_stats = self.get_all_timing_stats()
        resource_stats = self.get_resource_stats()
        bottlenecks = self.detect_bottlenecks()
        degradations = self.detect_degradation()
        
        # Prepare data for charts
        resource_samples = list(self.resource_samples)
        timestamps = [s['timestamp'] - self.start_time for s in resource_samples]
        cpu_data = [s['cpu_percent'] for s in resource_samples]
        memory_data = [s['memory_rss_mb'] for s in resource_samples]
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Performance Profile Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; padding: 10px 15px; background: #f9f9f9; border-left: 4px solid #4CAF50; }}
        .metric-label {{ font-size: 12px; color: #777; text-transform: uppercase; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .metric-unit {{ font-size: 14px; color: #999; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; font-weight: bold; }}
        tr:hover {{ background: #f5f5f5; }}
        .bottleneck {{ background: #fff3cd; padding: 15px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        .degradation {{ background: #f8d7da; padding: 15px; margin: 10px 0; border-left: 4px solid #dc3545; }}
        .chart {{ margin: 20px 0; }}
        .timestamp {{ color: #999; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ Performance Profile Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p class="timestamp">Duration: {time.time() - self.start_time:.1f} seconds</p>
        
        <h2>📊 Resource Usage Summary</h2>
        <div>
            <div class="metric">
                <div class="metric-label">CPU Usage (avg)</div>
                <div class="metric-value">{resource_stats['cpu_percent']['mean']:.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric">
                <div class="metric-label">Memory (avg)</div>
                <div class="metric-value">{resource_stats['memory_rss_mb']['mean']:.1f}<span class="metric-unit">MB</span></div>
            </div>
            <div class="metric">
                <div class="metric-label">Threads</div>
                <div class="metric-value">{resource_stats['num_threads']['mean']:.0f}</div>
            </div>
        </div>
        
        <div class="chart" id="cpu-chart"></div>
        <div class="chart" id="memory-chart"></div>
        
        <h2>⏱️ Timing Statistics</h2>
        <table>
            <thead>
                <tr>
                    <th>Component:Operation</th>
                    <th>Count</th>
                    <th>Mean</th>
                    <th>Median</th>
                    <th>P95</th>
                    <th>P99</th>
                    <th>Max</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for key, stats in sorted(timing_stats.items(), key=lambda x: x[1]['mean'], reverse=True):
            html += f"""
                <tr>
                    <td><strong>{key}</strong></td>
                    <td>{stats['count']}</td>
                    <td>{stats['mean']*1000:.1f}ms</td>
                    <td>{stats['median']*1000:.1f}ms</td>
                    <td>{stats['p95']*1000:.1f}ms</td>
                    <td>{stats['p99']*1000:.1f}ms</td>
                    <td>{stats['max']*1000:.1f}ms</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>🔍 Bottlenecks Detected</h2>
"""
        
        if bottlenecks:
            for b in bottlenecks:
                html += f"""
        <div class="bottleneck">
            <strong>{b['type'].replace('_', ' ').title()}</strong><br>
            {b.get('suggestion', 'No suggestion available')}
        </div>
"""
        else:
            html += "<p>✅ No significant bottlenecks detected.</p>"
        
        html += """
        <h2>📉 Performance Degradation</h2>
"""
        
        if degradations:
            for d in degradations:
                html += f"""
        <div class="degradation">
            <strong>{d['type'].replace('_', ' ').title()}</strong><br>
            Increased by {d['increase_percent']:.1f}% (from {d['baseline']:.1f} to {d['recent']:.1f})
        </div>
"""
        else:
            html += "<p>✅ No performance degradation detected.</p>"
        
        html += f"""
    </div>
    
    <script>
        // CPU Chart
        var cpuTrace = {{
            x: {timestamps},
            y: {cpu_data},
            type: 'scatter',
            mode: 'lines',
            name: 'CPU %',
            line: {{color: '#FF6B6B', width: 2}}
        }};
        var cpuLayout = {{
            title: 'CPU Usage Over Time',
            xaxis: {{title: 'Time (seconds)'}},
            yaxis: {{title: 'CPU %'}},
            margin: {{t: 40, r: 20, b: 40, l: 50}}
        }};
        Plotly.newPlot('cpu-chart', [cpuTrace], cpuLayout);
        
        // Memory Chart
        var memTrace = {{
            x: {timestamps},
            y: {memory_data},
            type: 'scatter',
            mode: 'lines',
            name: 'Memory MB',
            line: {{color: '#4ECDC4', width: 2}}
        }};
        var memLayout = {{
            title: 'Memory Usage Over Time',
            xaxis: {{title: 'Time (seconds)'}},
            yaxis: {{title: 'Memory (MB)'}},
            margin: {{t: 40, r: 20, b: 40, l: 50}}
        }};
        Plotly.newPlot('memory-chart', [memTrace], memLayout);
    </script>
</body>
</html>
"""
        
        with open(filepath, 'w') as f:
            f.write(html)


# Global collector instance
_global_collector = None

def get_collector() -> MetricsCollector:
    """Get or create the global metrics collector"""
    global _global_collector
    if _global_collector is None:
        _global_collector = MetricsCollector()
    return _global_collector


class Profiler:
    """Context manager for profiling code blocks"""
    
    def __init__(self, component: str, operation: str = "execution", collector: Optional[MetricsCollector] = None):
        self.component = component
        self.operation = operation
        self.collector = collector or get_collector()
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        metadata = {'success': exc_type is None}
        if exc_type:
            metadata['error'] = str(exc_val)
        self.collector.record_timing(self.component, self.operation, duration, metadata)


def profile(component: str, operation: Optional[str] = None):
    """Decorator for profiling functions"""
    def decorator(func: Callable) -> Callable:
        op_name = operation or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            with Profiler(component, op_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


class BackgroundMonitor:
    """Background thread for continuous monitoring"""
    
    def __init__(self, collector: MetricsCollector, interval: float = 1.0):
        self.collector = collector
        self.interval = interval
        self.running = False
        self.thread = None
        
    def start(self):
        """Start background monitoring"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop background monitoring"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            self.collector.record_resource_sample()
            time.sleep(self.interval)


def print_summary(collector: MetricsCollector):
    """Print a console summary of metrics"""
    print("\n" + "="*80)
    print("⚡ PERFORMANCE PROFILE SUMMARY")
    print("="*80)
    
    duration = time.time() - collector.start_time
    print(f"\n📅 Duration: {duration:.1f} seconds")
    print(f"🕐 Started: {datetime.fromtimestamp(collector.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Resource stats
    resource_stats = collector.get_resource_stats()
    if resource_stats:
        print("\n📊 RESOURCE USAGE")
        print("-" * 80)
        cpu = resource_stats['cpu_percent']
        print(f"  CPU:     {cpu['mean']:.1f}% avg  |  {cpu['min']:.1f}% min  |  {cpu['max']:.1f}% max")
        
        mem = resource_stats['memory_rss_mb']
        print(f"  Memory:  {mem['mean']:.1f} MB avg  |  {mem['min']:.1f} MB min  |  {mem['max']:.1f} MB max")
        
        threads = resource_stats['num_threads']
        print(f"  Threads: {threads['mean']:.0f} avg  |  {threads['min']:.0f} min  |  {threads['max']:.0f} max")
        
        if 'disk_read_rate_mb_s' in resource_stats:
            print(f"  Disk I/O: ↓{resource_stats['disk_read_rate_mb_s']:.2f} MB/s  |  ↑{resource_stats['disk_write_rate_mb_s']:.2f} MB/s")
            print(f"  Network:  ↓{resource_stats['net_recv_rate_mb_s']:.2f} MB/s  |  ↑{resource_stats['net_sent_rate_mb_s']:.2f} MB/s")
    
    # Timing stats
    timing_stats = collector.get_all_timing_stats()
    if timing_stats:
        print("\n⏱️  TIMING STATISTICS")
        print("-" * 80)
        print(f"{'Component:Operation':<40} {'Count':>8} {'Mean':>10} {'P95':>10} {'P99':>10}")
        print("-" * 80)
        
        for key, stats in sorted(timing_stats.items(), key=lambda x: x[1]['mean'], reverse=True)[:10]:
            print(f"{key:<40} {stats['count']:>8} {stats['mean']*1000:>9.1f}ms {stats['p95']*1000:>9.1f}ms {stats['p99']*1000:>9.1f}ms")
    
    # Bottlenecks
    bottlenecks = collector.detect_bottlenecks()
    if bottlenecks:
        print("\n🔍 BOTTLENECKS DETECTED")
        print("-" * 80)
        for i, b in enumerate(bottlenecks, 1):
            print(f"{i}. [{b['type']}]")
            print(f"   {b.get('suggestion', 'No suggestion')}")
    else:
        print("\n✅ No significant bottlenecks detected")
    
    # Degradation
    degradations = collector.detect_degradation()
    if degradations:
        print("\n📉 PERFORMANCE DEGRADATION")
        print("-" * 80)
        for i, d in enumerate(degradations, 1):
            print(f"{i}. [{d['type']}] Increased by {d['increase_percent']:.1f}%")
            print(f"   Baseline: {d['baseline']:.2f} → Recent: {d['recent']:.2f}")
    else:
        print("\n✅ No performance degradation detected")
    
    # Anomalies
    if collector.anomalies:
        print(f"\n⚠️  {len(collector.anomalies)} anomalies detected (showing last 5)")
        print("-" * 80)
        for anomaly in collector.anomalies[-5:]:
            ts = datetime.fromtimestamp(anomaly['timestamp']).strftime('%H:%M:%S')
            print(f"  [{ts}] {anomaly['type']}: {anomaly['value']:.1f} (baseline: {anomaly['baseline']:.1f})")
    
    print("\n" + "="*80 + "\n")


def simulate_workload():
    """Simulate a workload for demonstration"""
    import random
    
    print("🚀 Simulating Polymarket trading system workload...")
    
    @profile("data-collector", "fetch_markets")
    def fetch_markets():
        time.sleep(random.uniform(0.05, 0.15))
        
    @profile("data-collector", "fetch_prices")
    def fetch_prices():
        time.sleep(random.uniform(0.02, 0.08))
        
    @profile("signal-generator", "analyze_market")
    def analyze_market():
        time.sleep(random.uniform(0.1, 0.3))
        
    @profile("signal-generator", "calculate_signals")
    def calculate_signals():
        time.sleep(random.uniform(0.05, 0.2))
        
    @profile("database", "query")
    def db_query():
        time.sleep(random.uniform(0.01, 0.05))
        
    @profile("api", "call")
    def api_call():
        time.sleep(random.uniform(0.1, 0.4))
    
    # Simulate operations
    for i in range(50):
        fetch_markets()
        fetch_prices()
        
        if i % 5 == 0:
            analyze_market()
            calculate_signals()
        
        if i % 3 == 0:
            db_query()
            api_call()
        
        time.sleep(0.1)


def main():
    parser = argparse.ArgumentParser(
        description="Performance Profiler for Polymarket Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python performance-profiler.py                    # Quick 1-min check with demo
  python performance-profiler.py --extended         # 10-min profile
  python performance-profiler.py --monitor          # Continuous (Ctrl+C to stop)
  python performance-profiler.py --report perf.html # Generate HTML report
  python performance-profiler.py --component data-collector --duration 30
  python performance-profiler.py --json metrics.json
        """
    )
    
    parser.add_argument('--extended', action='store_true', help='Extended profile (10 minutes)')
    parser.add_argument('--monitor', action='store_true', help='Continuous background monitoring')
    parser.add_argument('--duration', type=int, help='Custom duration in seconds')
    parser.add_argument('--component', type=str, help='Filter by component name')
    parser.add_argument('--report', type=str, help='Generate HTML report to file')
    parser.add_argument('--json', type=str, help='Export metrics to JSON file')
    parser.add_argument('--demo', action='store_true', help='Run demo workload simulation')
    parser.add_argument('--interval', type=float, default=1.0, help='Sampling interval (seconds)')
    
    args = parser.parse_args()
    
    # Determine duration
    if args.monitor:
        duration = None  # Continuous
    elif args.extended:
        duration = 600  # 10 minutes
    elif args.duration:
        duration = args.duration
    else:
        duration = 60  # Default 1 minute
    
    # Create collector
    collector = get_collector()
    monitor = BackgroundMonitor(collector, interval=args.interval)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n🛑 Stopping profiler...")
        monitor.stop()
        print_summary(collector)
        
        if args.report:
            print(f"📝 Generating HTML report: {args.report}")
            collector.generate_html_report(args.report)
            print(f"✅ Report saved to {args.report}")
        
        if args.json:
            print(f"💾 Exporting metrics to: {args.json}")
            collector.export_json(args.json)
            print(f"✅ Metrics exported to {args.json}")
        
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start monitoring
    print(f"🔍 Starting performance profiler...")
    if duration:
        print(f"⏱️  Duration: {duration} seconds")
    else:
        print(f"⏱️  Duration: Continuous (press Ctrl+C to stop)")
    print(f"📊 Sampling interval: {args.interval}s")
    
    monitor.start()
    
    # Run demo workload if requested
    if args.demo or (not args.monitor and not args.component):
        simulate_workload()
    
    # Wait for duration or indefinitely
    if duration:
        try:
            for i in range(duration):
                time.sleep(1)
                if (i + 1) % 10 == 0:
                    print(f"  ⏳ {i + 1}/{duration} seconds elapsed...")
        except KeyboardInterrupt:
            pass
    else:
        print("  Press Ctrl+C to stop and generate report...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    
    # Stop monitoring and generate report
    monitor.stop()
    print_summary(collector)
    
    if args.report:
        print(f"\n📝 Generating HTML report: {args.report}")
        collector.generate_html_report(args.report)
        print(f"✅ Report saved to {args.report}")
    
    if args.json:
        print(f"\n💾 Exporting metrics to: {args.json}")
        collector.export_json(args.json)
        print(f"✅ Metrics exported to {args.json}")


if __name__ == '__main__':
    main()
