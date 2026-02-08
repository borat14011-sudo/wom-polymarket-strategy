#!/usr/bin/env python3
"""
Tier 2: Event Radar for Historical Backtesting

Adapts the Event Radar prompt to extract event patterns from historical markets.
Uses 5 Sonnet agents on 100 markets to build event taxonomy.
"""
import json
from pathlib import Path

DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")
OUTPUT_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"TIER 2: EVENT RADAR - HISTORICAL ANALYSIS")
print(f"Adapting Event Radar for backtest pattern extraction")
print(f"{'='*70}\n")

# Load markets
print("Loading historical markets...")
with open(DATA_DIR / "backtest_dataset_v1.json") as f:
    all_markets = json.load(f)

# Filter to closed markets with outcomes (need ground truth)
closed_with_outcomes = [
    m for m in all_markets 
    if m.get('closed') and len(m.get('price_history', [])) > 20
]

print(f"Total markets: {len(all_markets):,}")
print(f"Closed with price data: {len(closed_with_outcomes):,}")

# Select 100 diverse markets for test
import random
random.seed(42)
test_markets = random.sample(
    closed_with_outcomes, 
    min(100, len(closed_with_outcomes))
)

print(f"Selected for analysis: {len(test_markets)}\n")

# Prepare data for agents
# Convert markets into "signal snippets" format Event Radar expects
signals_batch = []
for i, m in enumerate(test_markets):
    # Extract key info
    question = m.get('question', '')
    prices = m.get('price_history', [])
    final_price = prices[-1].get('p', 0) if prices else 0
    
    # Infer outcome from final price
    if final_price > 0.90:
        outcome = 'YES'
    elif final_price < 0.10:
        outcome = 'NO'
    else:
        outcome = 'UNCLEAR'
    
    # Create signal snippet
    signals_batch.append({
        "signal_id": f"M-{m.get('market_id', i)}",
        "timestamp_utc": m.get('end_date', ''),
        "source_type": "polymarket_historical",
        "headline_text": question,
        "short_summary": f"{question} [Resolved: {outcome}, Final: {final_price:.2f}]",
        "market_metadata": {
            "volume": m.get('volume', 0),
            "start_date": m.get('start_date', ''),
            "end_date": m.get('end_date', ''),
            "price_range": {
                "min": min(p.get('p', 0) for p in prices) if prices else 0,
                "max": max(p.get('p', 0) for p in prices) if prices else 0
            }
        }
    })

# Create markets_sample for Event Radar
markets_sample = [
    {
        "id": m.get('market_id', i),
        "title": m.get('question', ''),
        "resolution_criteria_summary": f"Market resolved at {final_price:.2f}",
        "category": "historical",
        "close_time_utc": m.get('end_date', '')
    }
    for i, m in enumerate(test_markets)
]

# Save inputs
with open(OUTPUT_DIR / "event_radar_inputs.json", 'w') as f:
    json.dump({
        "markets_sample": markets_sample[:100],
        "signals_batch": signals_batch[:100]
    }, f, indent=2)

print(f"[READY] Prepared {len(signals_batch)} market signals for Event Radar")
print(f"[READY] Saved inputs to: {OUTPUT_DIR / 'event_radar_inputs.json'}")
print(f"\n{'='*70}")
print(f"Next: Deploy 5 Sonnet agents with Event Radar prompt")
print(f"{'='*70}\n")
