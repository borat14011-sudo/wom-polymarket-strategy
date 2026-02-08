#!/usr/bin/env python3
"""
EVENT RADAR AGENT 5/5 - Historical Pattern Extraction
Markets 80-99 Analysis
"""

import json
from datetime import datetime
from typing import Dict, List

def load_data():
    """Load the event radar inputs"""
    with open('polymarket-monitor/backtest-results/event_radar_inputs.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_market_subset(markets: List[Dict], signals: List[Dict], start_idx: int, end_idx: int) -> Dict:
    """Analyze a subset of markets for event patterns"""
    
    subset_markets = markets[start_idx:end_idx]
    subset_signals = signals[start_idx:end_idx]
    
    # Category analysis
    categories = {}
    for market in subset_markets:
        cat = market.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    # Pattern extraction
    patterns = {
        'crypto_price_predictions': [],
        'esports_totals': [],
        'player_props': [],
        'bitcoin_timing': [],
        'temperature_bets': [],
        'other': []
    }
    
    # Resolution analysis
    resolution_outcomes = {
        'YES': 0,
        'NO': 0,
        'UNCLEAR': 0
    }
    
    # Volume and price metrics
    total_volume = 0
    price_volatility_data = []
    
    for i, (market, signal) in enumerate(zip(subset_markets, subset_signals)):
        title = market['title']
        metadata = signal.get('market_metadata', {})
        
        # Extract resolution from summary
        summary = signal.get('short_summary', '')
        if 'Resolved: YES' in summary:
            resolution = 'YES'
        elif 'Resolved: NO' in summary:
            resolution = 'NO'
        else:
            resolution = 'UNCLEAR'
        
        resolution_outcomes[resolution] += 1
        
        # Volume tracking
        volume = metadata.get('volume', 0)
        total_volume += volume
        
        # Price range analysis
        price_range = metadata.get('price_range', {})
        price_min = price_range.get('min', 0)
        price_max = price_range.get('max', 0)
        volatility = price_max - price_min if price_max and price_min else 0
        price_volatility_data.append({
            'market_id': market['id'],
            'volatility': volatility,
            'volume': volume
        })
        
        # Pattern classification
        title_lower = title.lower()
        
        if 'bitcoin' in title_lower and ('up or down' in title_lower or 'above' in title_lower):
            patterns['bitcoin_timing'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
        elif 'total kills' in title_lower or 'o/u' in title_lower:
            patterns['esports_totals'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
        elif any(stat in title_lower for stat in ['points', 'rebounds', 'assists']):
            patterns['player_props'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
        elif 'temperature' in title_lower:
            patterns['temperature_bets'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
        elif any(crypto in title_lower for crypto in ['ethereum', 'solana', 'xrp']):
            patterns['crypto_price_predictions'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
        else:
            patterns['other'].append({
                'id': market['id'],
                'title': title,
                'resolution': resolution,
                'volume': volume
            })
    
    # Calculate insights
    avg_volume = total_volume / len(subset_markets) if subset_markets else 0
    avg_volatility = sum(p['volatility'] for p in price_volatility_data) / len(price_volatility_data) if price_volatility_data else 0
    
    # High volume markets
    high_volume_markets = sorted(price_volatility_data, key=lambda x: x['volume'], reverse=True)[:5]
    
    return {
        'analysis_metadata': {
            'agent': 'agent5',
            'market_range': f'{start_idx}-{end_idx-1}',
            'total_markets': len(subset_markets),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        },
        'category_distribution': categories,
        'resolution_outcomes': resolution_outcomes,
        'patterns': {k: len(v) for k, v in patterns.items()},
        'pattern_details': patterns,
        'volume_metrics': {
            'total_volume': round(total_volume, 2),
            'average_volume': round(avg_volume, 2),
            'top_volume_markets': high_volume_markets
        },
        'volatility_metrics': {
            'average_price_volatility': round(avg_volatility, 4),
            'high_volatility_count': sum(1 for p in price_volatility_data if p['volatility'] > 0.3)
        },
        'key_insights': generate_insights(patterns, resolution_outcomes, avg_volume)
    }

def generate_insights(patterns: Dict, resolutions: Dict, avg_volume: float) -> List[str]:
    """Generate key insights from the analysis"""
    insights = []
    
    # Pattern insights
    pattern_counts = {k: len(v) for k, v in patterns.items()}
    dominant_pattern = max(pattern_counts.items(), key=lambda x: x[1])
    insights.append(f"Dominant pattern: {dominant_pattern[0]} ({dominant_pattern[1]} markets)")
    
    # Resolution bias
    total_resolutions = sum(resolutions.values())
    if total_resolutions > 0:
        no_pct = (resolutions['NO'] / total_resolutions) * 100
        yes_pct = (resolutions['YES'] / total_resolutions) * 100
        insights.append(f"Resolution bias: {no_pct:.1f}% NO, {yes_pct:.1f}% YES")
    
    # Bitcoin timing analysis
    if patterns['bitcoin_timing']:
        btc_markets = patterns['bitcoin_timing']
        btc_yes = sum(1 for m in btc_markets if m['resolution'] == 'YES')
        btc_no = sum(1 for m in btc_markets if m['resolution'] == 'NO')
        insights.append(f"Bitcoin timing markets: {len(btc_markets)} total, {btc_yes} YES / {btc_no} NO")
    
    # Player props
    if patterns['player_props']:
        props = patterns['player_props']
        avg_prop_volume = sum(m['volume'] for m in props) / len(props)
        insights.append(f"Player props average volume: ${avg_prop_volume:,.0f}")
    
    # Volume insight
    insights.append(f"Average market volume: ${avg_volume:,.0f}")
    
    return insights

def main():
    print("Loading event radar data...")
    data = load_data()
    
    markets = data['markets_sample']
    signals = data['signals_batch']
    
    print(f"Total markets in dataset: {len(markets)}")
    print(f"Analyzing markets 80-99...")
    
    # Analyze markets 80-99 (indices 80 to 99 inclusive, which is 20 markets)
    analysis = analyze_market_subset(markets, signals, 80, 100)
    
    # Save results
    output_file = 'agent5_event_radar.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n[OK] Analysis complete!")
    print(f"Markets analyzed: {analysis['analysis_metadata']['total_markets']}")
    print(f"Output saved to: {output_file}")
    
    print("\nKey Insights:")
    for insight in analysis['key_insights']:
        print(f"  - {insight}")
    
    print("\nPattern Distribution:")
    for pattern, count in analysis['patterns'].items():
        print(f"  {pattern}: {count}")

if __name__ == '__main__':
    main()
