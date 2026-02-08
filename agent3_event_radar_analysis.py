#!/usr/bin/env python3
"""
Event Radar Agent 3 - Historical Pattern Extraction
Analyzes markets 40-59 from event_radar_inputs.json
"""

import json
from datetime import datetime
from collections import defaultdict

# Read input data
with open('polymarket-monitor/backtest-results/event_radar_inputs.json', 'r') as f:
    data = json.load(f)

markets_sample = data['markets_sample']
signals_batch = data['signals_batch']

# Extract markets 40-59 (20 markets)
target_markets = markets_sample[40:60]
target_market_ids = {m['id'] for m in target_markets}

# Extract corresponding signals
target_signals = [s for s in signals_batch if s['signal_id'].replace('M-', '') in target_market_ids]

print(f"Processing markets 40-59: {len(target_markets)} markets")
print(f"Found {len(target_signals)} corresponding signals")

# EVENT RADAR ANALYSIS
# Extract historical patterns from markets 40-59

def extract_resolution_outcome(signal):
    """Extract resolution from summary text"""
    summary = signal.get('short_summary', '')
    if 'Resolved: YES' in summary or 'Final: 1.00' in summary:
        return 'YES'
    elif 'Resolved: NO' in summary or 'Final: 0.00' in summary:
        return 'NO'
    elif 'Resolved: UNCLEAR' in summary or 'Final: 0.5' in summary:
        return 'UNCLEAR'
    else:
        # Extract final price
        if 'Final:' in summary:
            final_val = float(summary.split('Final:')[1].strip().rstrip(']'))
            if final_val >= 0.75:
                return 'YES'
            elif final_val <= 0.25:
                return 'NO'
            else:
                return 'UNCLEAR'
    return 'UNKNOWN'

def categorize_market(title):
    """Categorize market by type"""
    title_lower = title.lower()
    
    if 'bitcoin' in title_lower or 'ethereum' in title_lower or 'crypto' in title_lower or 'solana' in title_lower or 'xrp' in title_lower:
        return 'CRYPTO'
    elif any(sport in title_lower for sport in ['o/u', 'over/under', 'spread', 'total', 'kills', 'points', 'rebounds', 'assists']):
        return 'SPORTS_PROP'
    elif any(game in title_lower for game in ['counter-strike', 'dota', 'lol:', 'call of duty']):
        return 'ESPORTS'
    elif 'temperature' in title_lower or 'weather' in title_lower:
        return 'WEATHER'
    elif 'vs.' in title or 'vs' in title_lower:
        return 'MATCHUP'
    elif 'will' in title_lower and ('close' in title_lower or 'price' in title_lower):
        return 'PRICE_PREDICTION'
    else:
        return 'OTHER'

# Build analysis
analysis = {
    'agent_id': 3,
    'market_range': '40-59',
    'total_markets': len(target_markets),
    'total_signals': len(target_signals),
    'patterns': {},
    'category_breakdown': defaultdict(int),
    'resolution_stats': defaultdict(int),
    'volume_analysis': {
        'total_volume': 0,
        'avg_volume': 0,
        'high_volume_markets': [],
        'low_volume_markets': []
    },
    'price_patterns': {
        'tight_range_markets': [],  # max-min < 0.2
        'wide_swing_markets': [],   # max-min > 0.7
        'decisive_markets': []      # final near 0 or 1
    },
    'markets_analyzed': []
}

# Process each signal
for signal in target_signals:
    market_id = signal['signal_id'].replace('M-', '')
    
    # Find corresponding market
    market = next((m for m in target_markets if m['id'] == market_id), None)
    if not market:
        continue
    
    title = signal['headline_text']
    category = categorize_market(title)
    resolution = extract_resolution_outcome(signal)
    
    metadata = signal.get('market_metadata', {})
    volume = metadata.get('volume', 0)
    price_range = metadata.get('price_range', {})
    min_price = price_range.get('min', 0)
    max_price = price_range.get('max', 1)
    price_volatility = max_price - min_price
    
    # Extract final price from summary
    summary = signal.get('short_summary', '')
    final_price = 0.5
    if 'Final:' in summary:
        try:
            final_str = summary.split('Final:')[1].strip().rstrip(']').strip()
            final_price = float(final_str)
        except:
            pass
    
    # Update stats
    analysis['category_breakdown'][category] += 1
    analysis['resolution_stats'][resolution] += 1
    analysis['volume_analysis']['total_volume'] += volume
    
    # Track volume extremes
    if volume > 3000000:
        analysis['volume_analysis']['high_volume_markets'].append({
            'id': market_id,
            'title': title,
            'volume': volume
        })
    elif volume < 150000:
        analysis['volume_analysis']['low_volume_markets'].append({
            'id': market_id,
            'title': title,
            'volume': volume
        })
    
    # Price pattern analysis
    if price_volatility < 0.2:
        analysis['price_patterns']['tight_range_markets'].append({
            'id': market_id,
            'title': title,
            'range': f"{min_price:.2f}-{max_price:.2f}",
            'volatility': price_volatility
        })
    
    if price_volatility > 0.7:
        analysis['price_patterns']['wide_swing_markets'].append({
            'id': market_id,
            'title': title,
            'range': f"{min_price:.2f}-{max_price:.2f}",
            'volatility': price_volatility
        })
    
    if final_price <= 0.1 or final_price >= 0.9:
        analysis['price_patterns']['decisive_markets'].append({
            'id': market_id,
            'title': title,
            'final_price': final_price,
            'resolution': resolution
        })
    
    # Store market analysis
    analysis['markets_analyzed'].append({
        'id': market_id,
        'title': title,
        'category': category,
        'resolution': resolution,
        'volume': volume,
        'price_volatility': price_volatility,
        'final_price': final_price,
        'close_time': market.get('close_time_utc', '')
    })

# Calculate averages
if target_signals:
    analysis['volume_analysis']['avg_volume'] = analysis['volume_analysis']['total_volume'] / len(target_signals)

# Convert defaultdicts to regular dicts for JSON serialization
analysis['category_breakdown'] = dict(analysis['category_breakdown'])
analysis['resolution_stats'] = dict(analysis['resolution_stats'])

# Pattern extraction
patterns_found = []

# Pattern 1: Category dominance
dominant_category = max(analysis['category_breakdown'].items(), key=lambda x: x[1])
if dominant_category[1] > len(target_markets) * 0.3:
    patterns_found.append({
        'pattern_type': 'CATEGORY_DOMINANCE',
        'description': f'{dominant_category[0]} markets dominate this batch ({dominant_category[1]}/{len(target_markets)})',
        'strength': dominant_category[1] / len(target_markets)
    })

# Pattern 2: Resolution bias
yes_count = analysis['resolution_stats'].get('YES', 0)
no_count = analysis['resolution_stats'].get('NO', 0)
total_resolved = yes_count + no_count
if total_resolved > 0:
    yes_rate = yes_count / total_resolved
    if yes_rate > 0.65 or yes_rate < 0.35:
        patterns_found.append({
            'pattern_type': 'RESOLUTION_BIAS',
            'description': f'Significant bias toward {"YES" if yes_rate > 0.5 else "NO"} outcomes ({yes_rate:.1%} YES rate)',
            'yes_rate': yes_rate
        })

# Pattern 3: Volume concentration
high_volume_count = len(analysis['volume_analysis']['high_volume_markets'])
if high_volume_count > 3:
    patterns_found.append({
        'pattern_type': 'HIGH_VOLUME_CONCENTRATION',
        'description': f'{high_volume_count} markets with >3M volume indicate high trader interest',
        'count': high_volume_count
    })

# Pattern 4: Price stability
tight_range_count = len(analysis['price_patterns']['tight_range_markets'])
if tight_range_count > len(target_markets) * 0.3:
    patterns_found.append({
        'pattern_type': 'PRICE_STABILITY',
        'description': f'{tight_range_count} markets with tight price ranges (<0.2 volatility) suggest high confidence',
        'count': tight_range_count
    })

# Pattern 5: Decisive resolutions
decisive_count = len(analysis['price_patterns']['decisive_markets'])
if decisive_count > len(target_markets) * 0.5:
    patterns_found.append({
        'pattern_type': 'DECISIVE_RESOLUTIONS',
        'description': f'{decisive_count} markets resolved decisively (final price <0.1 or >0.9)',
        'count': decisive_count,
        'rate': decisive_count / len(target_markets)
    })

analysis['patterns'] = patterns_found

# Write output
output_file = 'agent3_event_radar.json'
with open(output_file, 'w') as f:
    json.dump(analysis, f, indent=2)

print(f"\n[OK] Analysis complete!")
print(f"Categories found: {list(analysis['category_breakdown'].keys())}")
print(f"Patterns detected: {len(patterns_found)}")
print(f"Total volume: ${analysis['volume_analysis']['total_volume']:,.0f}")
print(f"Output written to: {output_file}")

# Print pattern summary
if patterns_found:
    print("\nKEY PATTERNS DETECTED:")
    for i, pattern in enumerate(patterns_found, 1):
        print(f"  {i}. {pattern['pattern_type']}: {pattern['description']}")
else:
    print("\n[WARNING] No strong patterns detected in this batch")
