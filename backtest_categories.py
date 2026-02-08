import json
import re
from collections import defaultdict

# Load market data
with open('markets.json', 'r', encoding='utf-8') as f:
    markets = json.load(f)

# Category keywords
CATEGORIES = {
    'politics': ['trump', 'biden', 'election', 'deport', 'congress', 'senate', 'president', 'political', 'democrat', 'republican', 'govern', 'vote', 'policy'],
    'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'crypto', 'coin', 'blockchain', 'defi', 'usdc', 'usdt'],
    'sports': ['nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball', 'sport', 'championship', 'super bowl', 'world cup', 'uefa', 'premier league', 'boxing', 'mma', 'ufc'],
    'ai_tech': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'google', 'tesla', 'tech', 'technology', 'software', 'apple', 'microsoft', 'nvidia', 'sam altman', 'elon musk', 'amazon'],
    'world_events': ['war', 'ukraine', 'russia', 'israel', 'gaza', 'china', 'taiwan', 'north korea', 'iran', 'syria', 'climate', 'earthquake', 'disaster', 'pandemic', 'covid', 'disease']
}

def categorize_market(question, description=''):
    """Categorize a market based on its question and description."""
    text = (question + ' ' + description).lower()
    
    # Check each category
    category_scores = defaultdict(int)
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in text:
                category_scores[category] += 1
    
    if not category_scores:
        return 'other'
    
    # Return category with highest score
    return max(category_scores.items(), key=lambda x: x[1])[0]

def calculate_roi(outcome_prices, volume):
    """
    Calculate potential ROI for a market.
    outcome_prices: list of price strings like ["0.054", "0.946"]
    
    RVR 2.5x + ROC 10% strategy:
    - Risk/Reward Ratio of at least 2.5x
    - Return on Capital of at least 10%
    """
    if not outcome_prices or len(outcome_prices) < 2:
        return None, None
    
    try:
        prices = [float(p) for p in outcome_prices]
        if len(prices) != 2:
            return None, None
        
        # For binary markets, analyze both sides
        # If price is 0.3, potential gain is 0.7 (if it resolves to Yes)
        # RVR = potential_gain / risk = (1 - price) / price
        
        results = []
        for i, price in enumerate(prices):
            if price <= 0 or price >= 1:
                continue
            
            potential_gain = 1 - price
            risk = price
            rvr = potential_gain / risk if risk > 0 else 0
            roc = (potential_gain / price) if price > 0 else 0
            
            # Strategy: RVR >= 2.5 AND ROC >= 0.1 (10%)
            meets_criteria = rvr >= 2.5 and roc >= 0.1
            
            results.append({
                'side': i,
                'price': price,
                'rvr': rvr,
                'roc': roc,
                'meets_criteria': meets_criteria
            })
        
        return results
    except (ValueError, TypeError):
        return None

# Analyze markets
category_stats = defaultdict(lambda: {
    'total': 0,
    'total_volume': 0,
    'markets': []
})

print("Analyzing markets...")
for market in markets:
    question = market.get('question', '')
    description = market.get('description', '')
    outcome_prices = json.loads(market.get('outcomePrices', '[]'))
    volume = market.get('volumeNum', 0)
    
    category = categorize_market(question, description)
    
    # Calculate strategy fit
    roi_analysis = calculate_roi(outcome_prices, volume)
    
    market_data = {
        'id': market.get('id'),
        'question': question,
        'volume': volume,
        'outcome_prices': outcome_prices,
        'roi_analysis': roi_analysis,
        'meets_criteria': False
    }
    
    if roi_analysis:
        for analysis in roi_analysis:
            if analysis.get('meets_criteria'):
                market_data['meets_criteria'] = True
                break
    
    category_stats[category]['total'] += 1
    category_stats[category]['total_volume'] += volume
    category_stats[category]['markets'].append(market_data)

# Generate report
print("\n" + "="*80)
print("BACKTEST RESULTS BY CATEGORY")
print("="*80)

# Sort categories by number of markets
sorted_categories = sorted(category_stats.items(), key=lambda x: x[1]['total'], reverse=True)

category_summary = []
for category, stats in sorted_categories:
    total_markets = stats['total']
    total_volume = stats['total_volume']
    markets_meeting_criteria = sum(1 for m in stats['markets'] if m['meets_criteria'])
    
    pct_meeting_criteria = (markets_meeting_criteria / total_markets * 100) if total_markets > 0 else 0
    
    category_summary.append({
        'category': category,
        'total_markets': total_markets,
        'total_volume': total_volume,
        'markets_meeting_criteria': markets_meeting_criteria,
        'pct_meeting_criteria': pct_meeting_criteria
    })
    
    print(f"\n{category.upper().replace('_', '/')}")
    print(f"  Total Markets: {total_markets}")
    print(f"  Total Volume: ${total_volume:,.2f}")
    print(f"  Markets Meeting Criteria (RVR≥2.5x, ROC≥10%): {markets_meeting_criteria} ({pct_meeting_criteria:.1f}%)")
    
    # Show top markets meeting criteria
    qualifying_markets = [m for m in stats['markets'] if m['meets_criteria']]
    if qualifying_markets:
        # Sort by volume
        top_markets = sorted(qualifying_markets, key=lambda x: x['volume'], reverse=True)[:3]
        print(f"\n  Top Qualifying Markets:")
        for m in top_markets:
            print(f"    - {m['question'][:80]}")
            print(f"      Volume: ${m['volume']:,.2f}, Prices: {m['outcome_prices']}")

# Create markdown report
print("\n" + "="*80)
print("GENERATING BACKTEST_CATEGORIES.md")
print("="*80)

markdown_content = """# Market Category Backtest Analysis

## Strategy Parameters
- **Risk/Reward Ratio (RVR):** ≥2.5x
- **Return on Capital (ROC):** ≥10%
- **Markets Analyzed:** {}

## Category Rankings

### By Total Volume (Market Liquidity)
{}

### By Strategy Opportunity (% Markets Meeting Criteria)
{}

## Detailed Category Analysis

{}

## Key Findings

### Most Predictable Categories
{}

### Least Predictable Categories  
{}

## Recommendations

Based on the backtest analysis:

1. **Best Categories for Our Edge:**
{}

2. **Categories to Avoid:**
{}

3. **Volume Considerations:**
   - Higher volume markets generally have tighter spreads
   - Our strategy (RVR 2.5x+) tends to find more opportunities in lower probability outcomes
   - Consider balancing edge vs. liquidity

## Methodology

1. **Categorization:** Markets categorized by keyword matching in question/description
2. **Strategy Application:** Binary markets analyzed for both outcomes
3. **Criteria:** Trade qualifies if RVR ≥ 2.5x AND ROC ≥ 10%
4. **Data Source:** Gamma API (Polymarket), {} active markets analyzed

---
*Generated: 2026-02-06*
*Note: This is a snapshot analysis of currently active markets. For true historical backtest, resolved markets data needed.*
""".format(
    len(markets),
    # By volume
    '\n'.join([f"{i+1}. **{cat['category'].upper().replace('_', '/')}**: ${cat['total_volume']:,.2f} ({cat['total_markets']} markets)" 
               for i, cat in enumerate(sorted(category_summary, key=lambda x: x['total_volume'], reverse=True))]),
    # By opportunity
    '\n'.join([f"{i+1}. **{cat['category'].upper().replace('_', '/')}**: {cat['pct_meeting_criteria']:.1f}% ({cat['markets_meeting_criteria']}/{cat['total_markets']} markets)" 
               for i, cat in enumerate(sorted(category_summary, key=lambda x: x['pct_meeting_criteria'], reverse=True))]),
    # Detailed analysis
    '\n\n'.join([
        f"### {cat['category'].upper().replace('_', '/')}\n"
        f"- **Total Markets:** {cat['total_markets']}\n"
        f"- **Total Volume:** ${cat['total_volume']:,.2f}\n"
        f"- **Qualifying Markets:** {cat['markets_meeting_criteria']} ({cat['pct_meeting_criteria']:.1f}%)\n"
        f"- **Average Volume per Market:** ${cat['total_volume']/cat['total_markets'] if cat['total_markets'] > 0 else 0:,.2f}\n"
        for cat in sorted(category_summary, key=lambda x: x['total_volume'], reverse=True)
    ]),
    # Most predictable
    '\n'.join([f"- **{cat['category'].upper().replace('_', '/')}**: {cat['pct_meeting_criteria']:.1f}% of markets meet criteria" 
               for cat in sorted(category_summary, key=lambda x: x['pct_meeting_criteria'], reverse=True)[:3]]),
    # Least predictable
    '\n'.join([f"- **{cat['category'].upper().replace('_', '/')}**: {cat['pct_meeting_criteria']:.1f}% of markets meet criteria" 
               for cat in sorted(category_summary, key=lambda x: x['pct_meeting_criteria'])[:3]]),
    # Best categories
    '\n'.join([f"   - **{cat['category'].upper().replace('_', '/')}**: Strong opportunity rate ({cat['pct_meeting_criteria']:.1f}%) with ${cat['total_volume']:,.2f} volume" 
               for cat in sorted(category_summary, key=lambda x: x['pct_meeting_criteria'], reverse=True)[:3]]),
    # Worst categories
    '\n'.join([f"   - **{cat['category'].upper().replace('_', '/')}**: Low opportunity rate ({cat['pct_meeting_criteria']:.1f}%)" 
               for cat in sorted(category_summary, key=lambda x: x['pct_meeting_criteria'])[:3]]),
    len(markets)
)

with open('BACKTEST_CATEGORIES.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("\n✅ BACKTEST_CATEGORIES.md created successfully!")
print(f"\nAnalyzed {len(markets)} active markets across {len(category_stats)} categories")
