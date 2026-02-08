#!/usr/bin/env python3
"""
Live Dashboard for Polymarket Optimization Session
Real-time monitoring while Wom is driving
"""

import json
import os
from datetime import datetime

def load_checkpoints():
    """Load all checkpoint files"""
    checkpoints = []
    for i in range(1, 5):
        filename = f"optimization_checkpoint_{i}.json"
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                checkpoints.append(json.load(f))
    return checkpoints

def generate_dashboard():
    """Generate live dashboard view"""
    checkpoints = load_checkpoints()
    
    print("=" * 70)
    print("POLYMARKET OPTIMIZATION SESSION - LIVE DASHBOARD")
    print("=" * 70)
    print(f"Session Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST")
    print(f"Wom Status: DRIVING (20-min session)")
    print("-" * 70)
    
    # Agent Stack Status
    print("\nAGENT STACK STATUS:")
    print("-" * 70)
    agents = [
        ("Strategic Orchestrator", "Decisions", "ACTIVE"),
        ("Market Scanner", "Live Data", "ACTIVE"),
        ("Data Validator", "Accuracy", "ACTIVE"),
        ("Communication Hub", "Logging", "ACTIVE"),
        ("Memory Manager", "Checkpoints", "ACTIVE")
    ]
    for name, role, status in agents:
        print(f"  [{status}] {name:25} | Role: {role:15} | Model: Kimi 2.5")
    
    # Checkpoints
    print("\n" + "=" * 70)
    print("CHECKPOINT PROGRESS")
    print("=" * 70)
    
    for i, cp in enumerate(checkpoints, 1):
        data = cp.get("data", {})
        print(f"\nCheck #{i} - {cp.get('timestamp', 'N/A')}")
        print(f"  Markets Scanned: {data.get('markets_scanned', 0):,}")
        print(f"  Extreme Opportunities: {len(data.get('extreme_opportunities', []))}")
        print(f"  High Confidence: {data.get('high_confidence_count', 0)}")
        print(f"  2026 Markets: {len(data.get('markets_2026', []))}")
        print(f"  Elon Markets: {len(data.get('elon_markets', []))}")
        print(f"  Price Movements: {len(data.get('price_movements', []))}")
    
    # Progress bar
    total_checks = 4
    completed = len(checkpoints)
    remaining = total_checks - completed
    
    print("\n" + "=" * 70)
    print("SESSION PROGRESS")
    print("=" * 70)
    print(f"Completed: {completed}/{total_checks} checks")
    print(f"Remaining: {remaining} checks")
    
    bar_length = 40
    filled = int((completed / total_checks) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    pct = (completed / total_checks) * 100
    print(f"\n[{bar}] {pct:.0f}%")
    
    # Elon Markets Summary
    if checkpoints:
        last_cp = checkpoints[-1]
        data = last_cp.get("data", {})
        elon_markets = data.get("elon_markets", [])
        
        if elon_markets:
            print("\n" + "=" * 70)
            print("ELON MUSK MARKETS DISCOVERED")
            print("=" * 70)
            for i, m in enumerate(elon_markets[:10], 1):
                question = m.get('question', 'N/A')[:60]
                print(f"{i:2}. {question}...")
    
    # Current Status
    print("\n" + "=" * 70)
    print("CURRENT STATUS")
    print("=" * 70)
    if completed < total_checks:
        print(f"Status: RUNNING - Waiting for check #{completed + 1}")
        print(f"Next check in: ~{5 - (datetime.now().minute % 5)} minutes")
    else:
        print("Status: COMPLETE - Generating final report")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    generate_dashboard()
