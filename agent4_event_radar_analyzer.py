#!/usr/bin/env python3
"""
Event Radar Agent 4 - Historical Pattern Extraction
Markets 60-79 Analysis
"""

import json
from datetime import datetime
from typing import Dict, List, Any

def load_inputs():
    """Load event radar inputs"""
    with open('polymarket-monitor/backtest-results/event_radar_inputs.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_market_patterns(markets: List[Dict], signals: List[Dict]) -> Dict:
    """Analyze event radar patterns for markets 60-79"""
    
    # Extract markets 60-79
    subset_markets = markets[60:80]
    subset_signals = signals[60:80]
    
    patterns = {
        "agent_id": "agent4",
        "market_range": "60-79",
        "total_markets": len(subset_markets),
        "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
        "market_patterns": [],
        "aggregate_insights": {
            "category_distribution": {},
            "resolution_patterns": {},
            "volatility_insights": {},
            "temporal_patterns": {}
        }
    }
    
    # Analyze each market
    for i, (market, signal) in enumerate(zip(subset_markets, subset_signals), start=60):
        
        metadata = signal.get('market_metadata', {})
        price_range = metadata.get('price_range', {})
        
        # Calculate key metrics
        price_volatility = price_range.get('max', 0) - price_range.get('min', 0)
        
        # Determine resolution category
        resolution_text = market.get('resolution_criteria_summary', '')
        if 'YES' in resolution_text or 'Final: 1.00' in resolution_text:
            resolution = 'YES'
        elif 'NO' in resolution_text or 'Final: 0.00' in resolution_text:
            resolution = 'NO'
        elif 'UNCLEAR' in resolution_text:
            resolution = 'UNCLEAR'
        else:
            resolution = 'UNKNOWN'
        
        # Extract category from title
        title = market.get('title', '')
        category = categorize_market(title)
        
        # Calculate market duration
        start_date = metadata.get('start_date', '')
        end_date = metadata.get('end_date', '')
        duration_hours = calculate_duration_hours(start_date, end_date)
        
        market_pattern = {
            "market_index": i,
            "market_id": market.get('id'),
            "title": title,
            "category": category,
            "resolution": resolution,
            "volume": metadata.get('volume', 0),
            "price_volatility": round(price_volatility, 4),
            "price_min": price_range.get('min', 0),
            "price_max": price_range.get('max', 0),
            "duration_hours": duration_hours,
            "event_radar_signals": extract_event_signals(title, signal, metadata)
        }
        
        patterns["market_patterns"].append(market_pattern)
        
        # Aggregate insights
        patterns["aggregate_insights"]["category_distribution"][category] = \
            patterns["aggregate_insights"]["category_distribution"].get(category, 0) + 1
        patterns["aggregate_insights"]["resolution_patterns"][resolution] = \
            patterns["aggregate_insights"]["resolution_patterns"].get(resolution, 0) + 1
    
    # Calculate aggregate metrics
    calculate_aggregate_insights(patterns)
    
    return patterns

def categorize_market(title: str) -> str:
    """Categorize market based on title"""
    title_lower = title.lower()
    
    if 'bitcoin' in title_lower or 'btc' in title_lower or 'crypto' in title_lower or 'ethereum' in title_lower or 'solana' in title_lower or 'xrp' in title_lower:
        return 'crypto'
    elif 'kills' in title_lower or 'game' in title_lower or 'esports' in title_lower or 'counter-strike' in title_lower or 'lol:' in title_lower or 'dota' in title_lower:
        return 'esports'
    elif 'points' in title_lower or 'rebounds' in title_lower or 'assists' in title_lower or 'o/u' in title_lower or 'spread' in title_lower:
        return 'sports_props'
    elif 'temperature' in title_lower or 'weather' in title_lower:
        return 'weather'
    elif 'stock' in title_lower or 'amazon' in title_lower or 'netflix' in title_lower or 'amzn' in title_lower or 'nflx' in title_lower:
        return 'stocks'
    elif 'tennis' in title_lower or 'set' in title_lower or 'match' in title_lower:
        return 'tennis'
    elif 'vs' in title_lower or 'vs.' in title_lower:
        return 'head_to_head'
    else:
        return 'other'

def extract_event_signals(title: str, signal: Dict, metadata: Dict) -> Dict:
    """Extract event radar signals from market data"""
    
    signals = {
        "high_urgency": False,
        "short_duration": False,
        "high_volatility": False,
        "predictable_outcome": False,
        "time_sensitive": False,
        "event_type": None
    }
    
    # Detect time-sensitive markets
    if 'up or down' in title.lower():
        signals["time_sensitive"] = True
        signals["event_type"] = "micro_timeframe"
        signals["high_urgency"] = True
    
    # Detect short-duration events
    price_range = metadata.get('price_range', {})
    volatility = price_range.get('max', 0) - price_range.get('min', 0)
    
    if volatility > 0.8:
        signals["high_volatility"] = True
    
    if volatility < 0.1:
        signals["predictable_outcome"] = True
    
    # Detect sports props
    if 'o/u' in title.lower() or 'over/under' in title.lower():
        signals["event_type"] = "sports_prop"
    
    # Detect esports
    if 'kills' in title.lower() and 'game' in title.lower():
        signals["event_type"] = "esports"
        signals["short_duration"] = True
    
    return signals

def calculate_duration_hours(start_date: str, end_date: str) -> float:
    """Calculate duration in hours between two dates"""
    try:
        if not start_date or not end_date:
            return 0
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        duration = (end - start).total_seconds() / 3600
        return round(duration, 2)
    except:
        return 0

def calculate_aggregate_insights(patterns: Dict):
    """Calculate aggregate insights"""
    markets = patterns["market_patterns"]
    
    if not markets:
        return
    
    # Volume statistics
    volumes = [m["volume"] for m in markets]
    volatilities = [m["price_volatility"] for m in markets]
    durations = [m["duration_hours"] for m in markets if m["duration_hours"] > 0]
    
    patterns["aggregate_insights"]["volatility_insights"] = {
        "avg_volatility": round(sum(volatilities) / len(volatilities), 4) if volatilities else 0,
        "max_volatility": round(max(volatilities), 4) if volatilities else 0,
        "min_volatility": round(min(volatilities), 4) if volatilities else 0,
        "high_volatility_count": sum(1 for v in volatilities if v > 0.5)
    }
    
    patterns["aggregate_insights"]["temporal_patterns"] = {
        "avg_duration_hours": round(sum(durations) / len(durations), 2) if durations else 0,
        "max_duration_hours": round(max(durations), 2) if durations else 0,
        "min_duration_hours": round(min(durations), 2) if durations else 0,
        "short_duration_count": sum(1 for d in durations if d < 24)
    }
    
    patterns["aggregate_insights"]["volume_insights"] = {
        "avg_volume": round(sum(volumes) / len(volumes), 2) if volumes else 0,
        "total_volume": round(sum(volumes), 2),
        "high_volume_count": sum(1 for v in volumes if v > 1000000)
    }
    
    # Event signal aggregation
    event_signals = {
        "high_urgency": 0,
        "short_duration": 0,
        "high_volatility": 0,
        "predictable_outcome": 0,
        "time_sensitive": 0
    }
    
    for m in markets:
        signals = m.get("event_radar_signals", {})
        for key in event_signals:
            if signals.get(key):
                event_signals[key] += 1
    
    patterns["aggregate_insights"]["event_signal_summary"] = event_signals

def main():
    print(">> Event Radar Agent 4 - Starting Analysis")
    print("Markets: 60-79")
    
    # Load data
    data = load_inputs()
    markets = data.get('markets_sample', [])
    signals = data.get('signals_batch', [])
    
    print(f"[OK] Loaded {len(markets)} total markets")
    print(f"[OK] Analyzing subset: markets 60-79 (20 markets)")
    
    # Analyze patterns
    results = analyze_market_patterns(markets, signals)
    
    # Save results
    output_file = 'agent4_event_radar.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n[COMPLETE] Analysis Complete!")
    print(f"[OUTPUT] {output_file}")
    print(f"\nKey Findings:")
    print(f"  - Total Markets Analyzed: {results['total_markets']}")
    print(f"  - Category Distribution: {results['aggregate_insights']['category_distribution']}")
    print(f"  - Resolution Patterns: {results['aggregate_insights']['resolution_patterns']}")
    print(f"  - Avg Volatility: {results['aggregate_insights']['volatility_insights']['avg_volatility']}")
    print(f"  - Avg Duration: {results['aggregate_insights']['temporal_patterns']['avg_duration_hours']} hours")

if __name__ == "__main__":
    main()
