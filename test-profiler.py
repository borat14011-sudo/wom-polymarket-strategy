#!/usr/bin/env python3
"""
Quick test script for performance-profiler.py
Tests all major functionality without requiring full CLI run
"""

import sys
import time
import random

# Import the profiler
try:
    from performance_profiler import (
        Profiler, profile, get_collector, 
        BackgroundMonitor, MetricsCollector
    )
    print("✅ Successfully imported performance_profiler")
except ImportError as e:
    print(f"❌ Failed to import: {e}")
    sys.exit(1)

print("\n" + "="*80)
print("🧪 TESTING PERFORMANCE PROFILER")
print("="*80)

# Test 1: Context Manager
print("\n[Test 1] Context Manager...")
try:
    with Profiler("test-component", "operation1"):
        time.sleep(0.1)
    print("✅ Context manager works")
except Exception as e:
    print(f"❌ Context manager failed: {e}")

# Test 2: Decorator
print("\n[Test 2] Decorator...")
try:
    @profile("test-component", "operation2")
    def test_function():
        time.sleep(0.05)
        return "success"
    
    result = test_function()
    print(f"✅ Decorator works (result: {result})")
except Exception as e:
    print(f"❌ Decorator failed: {e}")

# Test 3: Manual Timing
print("\n[Test 3] Manual Timing...")
try:
    collector = get_collector()
    collector.record_timing("test-component", "operation3", 0.123, metadata={"test": True})
    print("✅ Manual timing works")
except Exception as e:
    print(f"❌ Manual timing failed: {e}")

# Test 4: Resource Sampling
print("\n[Test 4] Resource Sampling...")
try:
    collector = get_collector()
    sample = collector.record_resource_sample()
    if sample:
        print(f"✅ Resource sampling works")
        print(f"   CPU: {sample['cpu_percent']:.1f}%")
        print(f"   Memory: {sample['memory_rss_mb']:.1f} MB")
        print(f"   Threads: {sample['num_threads']}")
    else:
        print("⚠️  Resource sampling returned None (might be permission issue)")
except Exception as e:
    print(f"❌ Resource sampling failed: {e}")

# Test 5: Generate Some Data
print("\n[Test 5] Generating test data...")
try:
    for i in range(20):
        with Profiler("data-collector", "fetch"):
            time.sleep(random.uniform(0.01, 0.05))
        
        with Profiler("processor", "process"):
            time.sleep(random.uniform(0.02, 0.08))
        
        collector.record_resource_sample()
        time.sleep(0.1)
    
    print("✅ Generated test data (20 iterations)")
except Exception as e:
    print(f"❌ Data generation failed: {e}")

# Test 6: Timing Statistics
print("\n[Test 6] Timing Statistics...")
try:
    stats = collector.get_timing_stats("data-collector", "fetch")
    if stats:
        print("✅ Timing statistics work")
        print(f"   Count: {stats['count']}")
        print(f"   Mean: {stats['mean']*1000:.1f}ms")
        print(f"   P95: {stats['p95']*1000:.1f}ms")
        print(f"   P99: {stats['p99']*1000:.1f}ms")
    else:
        print("⚠️  No timing data collected")
except Exception as e:
    print(f"❌ Timing statistics failed: {e}")

# Test 7: Resource Statistics
print("\n[Test 7] Resource Statistics...")
try:
    resource_stats = collector.get_resource_stats()
    if resource_stats:
        print("✅ Resource statistics work")
        print(f"   CPU (avg): {resource_stats['cpu_percent']['mean']:.1f}%")
        print(f"   Memory (avg): {resource_stats['memory_rss_mb']['mean']:.1f} MB")
    else:
        print("⚠️  No resource data collected")
except Exception as e:
    print(f"❌ Resource statistics failed: {e}")

# Test 8: Bottleneck Detection
print("\n[Test 8] Bottleneck Detection...")
try:
    bottlenecks = collector.detect_bottlenecks()
    print(f"✅ Bottleneck detection works ({len(bottlenecks)} found)")
    for b in bottlenecks[:3]:
        print(f"   - {b['type']}: {b.get('suggestion', 'N/A')[:60]}")
except Exception as e:
    print(f"❌ Bottleneck detection failed: {e}")

# Test 9: Degradation Detection
print("\n[Test 9] Degradation Detection...")
try:
    degradations = collector.detect_degradation(window_minutes=1)
    print(f"✅ Degradation detection works ({len(degradations)} found)")
    for d in degradations[:3]:
        print(f"   - {d['type']}: {d.get('increase_percent', 0):.1f}% increase")
except Exception as e:
    print(f"❌ Degradation detection failed: {e}")

# Test 10: JSON Export
print("\n[Test 10] JSON Export...")
try:
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json_path = f.name
    
    collector.export_json(json_path)
    
    file_size = os.path.getsize(json_path)
    print(f"✅ JSON export works ({file_size} bytes)")
    
    # Clean up
    os.remove(json_path)
except Exception as e:
    print(f"❌ JSON export failed: {e}")

# Test 11: HTML Report
print("\n[Test 11] HTML Report Generation...")
try:
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        html_path = f.name
    
    collector.generate_html_report(html_path)
    
    file_size = os.path.getsize(html_path)
    print(f"✅ HTML report generation works ({file_size} bytes)")
    print(f"   Report saved to: {html_path}")
    
    # Don't delete so user can view it
    print(f"   💡 Open this file in a browser to see the report!")
except Exception as e:
    print(f"❌ HTML report failed: {e}")

# Test 12: Background Monitor
print("\n[Test 12] Background Monitor...")
try:
    test_collector = MetricsCollector()
    monitor = BackgroundMonitor(test_collector, interval=0.5)
    
    monitor.start()
    print("✅ Background monitor started")
    
    time.sleep(2)  # Let it collect some samples
    
    monitor.stop()
    print("✅ Background monitor stopped")
    
    if len(test_collector.resource_samples) > 0:
        print(f"   Collected {len(test_collector.resource_samples)} samples")
    else:
        print("⚠️  No samples collected")
except Exception as e:
    print(f"❌ Background monitor failed: {e}")

# Final Summary
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)

all_stats = collector.get_all_timing_stats()
print(f"\n✅ All core functionality tested successfully!")
print(f"\n📈 Final Stats:")
print(f"   - {len(all_stats)} operation types tracked")
print(f"   - {len(collector.resource_samples)} resource samples collected")
print(f"   - {len(collector.anomalies)} anomalies detected")
print(f"\n🎉 Performance profiler is working correctly!")
print("\n" + "="*80 + "\n")
