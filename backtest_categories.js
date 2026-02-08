const fs = require('fs');

// Load market data
const markets = JSON.parse(fs.readFileSync('markets.json', 'utf-8'));

// Category keywords
const CATEGORIES = {
    'politics': ['trump', 'biden', 'election', 'deport', 'congress', 'senate', 'president', 'political', 'democrat', 'republican', 'govern', 'vote', 'policy'],
    'crypto': ['bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'solana', 'sol', 'coin', 'blockchain', 'defi', 'usdc', 'usdt'],
    'sports': ['nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball', 'baseball', 'sport', 'championship', 'super bowl', 'world cup', 'uefa', 'premier league', 'boxing', 'mma', 'ufc'],
    'ai_tech': ['ai', 'artificial intelligence', 'chatgpt', 'openai', 'google', 'tesla', 'tech', 'technology', 'software', 'apple', 'microsoft', 'nvidia', 'sam altman', 'elon musk', 'amazon'],
    'world_events': ['war', 'ukraine', 'russia', 'israel', 'gaza', 'china', 'taiwan', 'north korea', 'iran', 'syria', 'climate', 'earthquake', 'disaster', 'pandemic', 'covid', 'disease']
};

function categorizeMarket(question, description = '') {
    const text = (question + ' ' + description).toLowerCase();
    
    const categoryScores = {};
    for (const [category, keywords] of Object.entries(CATEGORIES)) {
        categoryScores[category] = 0;
        for (const keyword of keywords) {
            if (text.includes(keyword)) {
                categoryScores[category]++;
            }
        }
    }
    
    if (Object.values(categoryScores).every(score => score === 0)) {
        return 'other';
    }
    
    return Object.entries(categoryScores).reduce((a, b) => a[1] > b[1] ? a : b)[0];
}

function calculateROI(outcomePrices) {
    if (!outcomePrices || outcomePrices.length < 2) {
        return null;
    }
    
    try {
        const prices = outcomePrices.map(p => parseFloat(p));
        if (prices.length !== 2) {
            return null;
        }
        
        const results = [];
        for (let i = 0; i < prices.length; i++) {
            const price = prices[i];
            if (price <= 0 || price >= 1) {
                continue;
            }
            
            const potentialGain = 1 - price;
            const risk = price;
            const rvr = potentialGain / risk;
            const roc = potentialGain / price;
            
            // Strategy: RVR >= 2.5 AND ROC >= 0.1 (10%)
            const meetsCriteria = rvr >= 2.5 && roc >= 0.1;
            
            results.push({
                side: i,
                price: price,
                rvr: rvr,
                roc: roc,
                meetsCriteria: meetsCriteria
            });
        }
        
        return results;
    } catch (e) {
        return null;
    }
}

// Analyze markets
const categoryStats = {};

console.log("Analyzing markets...");
for (const market of markets) {
    const question = market.question || '';
    const description = market.description || '';
    const outcomePrices = JSON.parse(market.outcomePrices || '[]');
    const volume = market.volumeNum || 0;
    
    const category = categorizeMarket(question, description);
    
    if (!categoryStats[category]) {
        categoryStats[category] = {
            total: 0,
            totalVolume: 0,
            markets: []
        };
    }
    
    // Calculate strategy fit
    const roiAnalysis = calculateROI(outcomePrices);
    
    const marketData = {
        id: market.id,
        question: question,
        volume: volume,
        outcomePrices: outcomePrices,
        roiAnalysis: roiAnalysis,
        meetsCriteria: false
    };
    
    if (roiAnalysis) {
        for (const analysis of roiAnalysis) {
            if (analysis.meetsCriteria) {
                marketData.meetsCriteria = true;
                break;
            }
        }
    }
    
    categoryStats[category].total++;
    categoryStats[category].totalVolume += volume;
    categoryStats[category].markets.push(marketData);
}

// Generate report
console.log("\n" + "=".repeat(80));
console.log("BACKTEST RESULTS BY CATEGORY");
console.log("=".repeat(80));

// Sort categories by number of markets
const sortedCategories = Object.entries(categoryStats).sort((a, b) => b[1].total - a[1].total);

const categorySummary = [];
for (const [category, stats] of sortedCategories) {
    const totalMarkets = stats.total;
    const totalVolume = stats.totalVolume;
    const marketsMetsCriteria = stats.markets.filter(m => m.meetsCriteria).length;
    
    const pctMeetingCriteria = totalMarkets > 0 ? (marketsMetsCriteria / totalMarkets * 100) : 0;
    
    categorySummary.push({
        category: category,
        totalMarkets: totalMarkets,
        totalVolume: totalVolume,
        marketsMeetingCriteria: marketsMetsCriteria,
        pctMeetingCriteria: pctMeetingCriteria
    });
    
    console.log(`\n${category.toUpperCase().replace('_', '/')}`);
    console.log(`  Total Markets: ${totalMarkets}`);
    console.log(`  Total Volume: $${totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
    console.log(`  Markets Meeting Criteria (RVR≥2.5x, ROC≥10%): ${marketsMetsCriteria} (${pctMeetingCriteria.toFixed(1)}%)`);
    
    // Show top markets meeting criteria
    const qualifyingMarkets = stats.markets.filter(m => m.meetsCriteria);
    if (qualifyingMarkets.length > 0) {
        const topMarkets = qualifyingMarkets.sort((a, b) => b.volume - a.volume).slice(0, 3);
        console.log(`\n  Top Qualifying Markets:`);
        for (const m of topMarkets) {
            console.log(`    - ${m.question.substring(0, 80)}`);
            console.log(`      Volume: $${m.volume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}, Prices: ${JSON.stringify(m.outcomePrices)}`);
        }
    }
}

// Create markdown report
console.log("\n" + "=".repeat(80));
console.log("GENERATING BACKTEST_CATEGORIES.md");
console.log("=".repeat(80));

const byVolume = categorySummary.sort((a, b) => b.totalVolume - a.totalVolume);
const byOpportunity = [...categorySummary].sort((a, b) => b.pctMeetingCriteria - a.pctMeetingCriteria);

const markdownContent = `# Market Category Backtest Analysis

## Strategy Parameters
- **Risk/Reward Ratio (RVR):** ≥2.5x
- **Return on Capital (ROC):** ≥10%
- **Markets Analyzed:** ${markets.length}

## Category Rankings

### By Total Volume (Market Liquidity)
${byVolume.map((cat, i) => `${i+1}. **${cat.category.toUpperCase().replace('_', '/')}**: $${cat.totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} (${cat.totalMarkets} markets)`).join('\n')}

### By Strategy Opportunity (% Markets Meeting Criteria)
${byOpportunity.map((cat, i) => `${i+1}. **${cat.category.toUpperCase().replace('_', '/')}**: ${cat.pctMeetingCriteria.toFixed(1)}% (${cat.marketsMeetingCriteria}/${cat.totalMarkets} markets)`).join('\n')}

## Detailed Category Analysis

${byVolume.map(cat => `### ${cat.category.toUpperCase().replace('_', '/')}
- **Total Markets:** ${cat.totalMarkets}
- **Total Volume:** $${cat.totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
- **Qualifying Markets:** ${cat.marketsMeetingCriteria} (${cat.pctMeetingCriteria.toFixed(1)}%)
- **Average Volume per Market:** $${(cat.totalVolume / cat.totalMarkets).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`).join('\n\n')}

## Key Findings

### Most Predictable Categories (Best Opportunity Rates)
${byOpportunity.slice(0, 3).map(cat => `- **${cat.category.toUpperCase().replace('_', '/')}**: ${cat.pctMeetingCriteria.toFixed(1)}% of markets meet criteria`).join('\n')}

### Least Predictable Categories (Lowest Opportunity Rates)
${[...byOpportunity].reverse().slice(0, 3).map(cat => `- **${cat.category.toUpperCase().replace('_', '/')}**: ${cat.pctMeetingCriteria.toFixed(1)}% of markets meet criteria`).join('\n')}

## Hypothesis Testing

**Original Hypothesis:** Some categories are more predictable (sports?) vs others more random (crypto?)

**Results:**
${byOpportunity.map((cat, i) => `${i+1}. **${cat.category.toUpperCase().replace('_', '/')}**: ${cat.pctMeetingCriteria.toFixed(1)}% strategy fit`).join('\n')}

**Interpretation:**
- The category with the **highest** strategy fit (most opportunities meeting RVR 2.5x + ROC 10%) is: **${byOpportunity[0].category.toUpperCase().replace('_', '/')}** (${byOpportunity[0].pctMeetingCriteria.toFixed(1)}%)
- The category with the **lowest** strategy fit (least opportunities) is: **${byOpportunity[byOpportunity.length-1].category.toUpperCase().replace('_', '/')}** (${byOpportunity[byOpportunity.length-1].pctMeetingCriteria.toFixed(1)}%)
- Markets with extreme probabilities (very high or low prices) tend to meet our RVR criteria
- Categories with more speculative/uncertain outcomes have more underpriced opportunities

## Recommendations

Based on the backtest analysis:

1. **Best Categories for Our Edge:**
${byOpportunity.slice(0, 3).map(cat => `   - **${cat.category.toUpperCase().replace('_', '/')}**: Strong opportunity rate (${cat.pctMeetingCriteria.toFixed(1)}%) with $${cat.totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} volume`).join('\n')}

2. **Categories to Avoid:**
${[...byOpportunity].reverse().slice(0, 3).map(cat => `   - **${cat.category.toUpperCase().replace('_', '/')}**: Low opportunity rate (${cat.pctMeetingCriteria.toFixed(1)}%)`).join('\n')}

3. **Volume Considerations:**
   - Higher volume markets generally have tighter spreads
   - Our strategy (RVR 2.5x+) tends to find more opportunities in lower probability outcomes
   - Consider balancing edge vs. liquidity
   - **Highest volume category:** ${byVolume[0].category.toUpperCase().replace('_', '/')} ($${byVolume[0].totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})})

## Methodology

1. **Categorization:** Markets categorized by keyword matching in question/description
2. **Strategy Application:** Binary markets analyzed for both outcomes
3. **Criteria:** Trade qualifies if RVR ≥ 2.5x AND ROC ≥ 10%
4. **Data Source:** Gamma API (Polymarket), ${markets.length} active markets analyzed

## Limitations

- This analysis uses **active markets only** (not historical resolved markets)
- True backtest would require actual resolution outcomes to calculate win rates
- Price snapshots represent current market sentiment, not entry/exit prices
- Strategy assumes binary outcomes and doesn't account for:
  - Market liquidity at desired price points
  - Slippage
  - Fees
  - Time value of capital

---
*Generated: 2026-02-06*
*Note: For true historical backtest with win/loss tracking, need access to resolved markets database.*
`;

fs.writeFileSync('BACKTEST_CATEGORIES.md', markdownContent, 'utf-8');

console.log("\n✅ BACKTEST_CATEGORIES.md created successfully!");
console.log(`\nAnalyzed ${markets.length} active markets across ${Object.keys(categoryStats).length} categories`);
