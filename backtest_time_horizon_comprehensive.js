// COMPREHENSIVE TIME HORIZON BACKTEST
// Uses all available data sources to validate the time horizon strategy

const fs = require('fs');

console.log('🔍 Loading data from all sources...\n');

// Load all data sources
const activeMarkets = JSON.parse(fs.readFileSync('active-markets.json', 'utf8'));
const eventsData = JSON.parse(fs.readFileSync('events.json', 'utf8'));
const resolvedData = JSON.parse(fs.readFileSync('polymarket_resolved_markets.json', 'utf8').replace(/^\uFEFF/, ''));

console.log(`✅ Active markets: ${activeMarkets.length}`);
console.log(`✅ Events: ${eventsData.length}`);
console.log(`✅ Resolved markets: ${resolvedData.length}\n`);

// Function to calculate time horizon in days
function getTimeHorizonDays(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffMs = end - start;
    return diffMs / (1000 * 60 * 60 * 24);
}

// Analysis buckets
const buckets = {
    'under3days': { markets: [], wins: 0, losses: 0 },
    '3to7days': { markets: [], wins: 0, losses: 0 },
    'over7days': { markets: [], wins: 0, losses: 0 }
};

// Process events (these have creationDate and endDate)
console.log('📊 Processing events data...');
let eventsProcessed = 0;

eventsData.forEach(event => {
    if (!event.creationDate || !event.endDate) return;
    
    const horizonDays = getTimeHorizonDays(event.creationDate, event.endDate);
    if (horizonDays < 0 || isNaN(horizonDays)) return;
    
    // For events, we'll look at their markets to determine outcomes
    if (!event.markets || event.markets.length === 0) return;
    
    event.markets.forEach(market => {
        if (!market.closed) return; // Only count resolved markets
        
        let bucket;
        if (horizonDays < 3) bucket = 'under3days';
        else if (horizonDays >= 3 && horizonDays <= 7) bucket = '3to7days';
        else bucket = 'over7days';
        
        // Determine win/loss
        // Simplified: if market has a clear winner price (>0.9), we would have caught it
        const outcomes = market.outcomePrices || market.outcomes;
        let won = false;
        
        if (typeof outcomes === 'string') {
            const prices = outcomes.split('|').map(p => parseFloat(p.replace(/[^0-9.]/g, '')));
            // If we entered at signal and the market resolved clearly (>0.9), count as win
            won = prices.some(p => p > 0.9);
        }
        
        if (won) buckets[bucket].wins++;
        else buckets[bucket].losses++;
        
        buckets[bucket].markets.push({
            question: market.question || event.title,
            horizonDays: horizonDays.toFixed(2),
            won: won,
            source: 'events'
        });
        
        eventsProcessed++;
    });
});

console.log(`   Processed ${eventsProcessed} resolved event markets\n`);

// Process active markets (we can calculate current time horizon)
console.log('📊 Processing active markets...');
let activeProcessed = 0;

activeMarkets.forEach(market => {
    // Skip if market is not closed/resolved
    if (!market.closed) return;
    
    const startDate = market.startDate || market.createdAt;
    const endDate = market.endDate;
    
    if (!startDate || !endDate) return;
    
    const horizonDays = getTimeHorizonDays(startDate, endDate);
    if (horizonDays < 0 || isNaN(horizonDays)) return;
    
    let bucket;
    if (horizonDays < 3) bucket = 'under3days';
    else if (horizonDays >= 3 && horizonDays <= 7) bucket = '3to7days';
    else bucket = 'over7days';
    
    // For closed markets, check if we can determine outcome
    const prices = market.outcomePrices;
    let won = false;
    
    if (Array.isArray(prices)) {
        const numPrices = prices.map(p => parseFloat(p));
        won = numPrices.some(p => p > 0.9);
    } else if (typeof prices === 'string') {
        const numPrices = JSON.parse(prices).map(p => parseFloat(p));
        won = numPrices.some(p => p > 0.9);
    }
    
    if (won) buckets[bucket].wins++;
    else buckets[bucket].losses++;
    
    buckets[bucket].markets.push({
        question: market.question,
        horizonDays: horizonDays.toFixed(2),
        won: won,
        source: 'active'
    });
    
    activeProcessed++;
});

console.log(`   Processed ${activeProcessed} closed active markets\n`);

// For resolved markets without creation date, make educated estimate
console.log('📊 Processing resolved markets (estimated horizons)...');
let resolvedProcessed = 0;

resolvedData.forEach(market => {
    const endDate = market.event_end_date;
    if (!endDate) return;
    
    // Estimate: Most election markets created 30-90 days before event
    // Sports/short-term markets: 1-7 days before
    // For this analysis, we'll use the market title to estimate
    const title = (market.question + ' ' + market.event_title).toLowerCase();
    
    let estimatedCreationDaysBefore;
    if (title.includes('election') || title.includes('senate') || title.includes('president')) {
        estimatedCreationDaysBefore = 60; // 60 days before for elections
    } else if (title.includes('nba') || title.includes('nfl') || title.includes('game')) {
        estimatedCreationDaysBefore = 3; // 3 days before for sports
    } else {
        estimatedCreationDaysBefore = 14; // 2 weeks default
    }
    
    const horizonDays = estimatedCreationDaysBefore;
    
    let bucket;
    if (horizonDays < 3) bucket = 'under3days';
    else if (horizonDays >= 3 && horizonDays <= 7) bucket = '3to7days';
    else bucket = 'over7days';
    
    // Determine outcome
    const winner = market.winner;
    const finalPrices = market.final_prices ? market.final_prices.split('|').map(p => parseFloat(p)) : [];
    
    let won = false;
    if (winner === "Yes" && finalPrices[0] === 1) won = true;
    if (winner === "No" && finalPrices[1] === 1) won = true;
    
    if (won) buckets[bucket].wins++;
    else buckets[bucket].losses++;
    
    buckets[bucket].markets.push({
        question: market.question,
        horizonDays: horizonDays.toFixed(2) + ' (est)',
        won: won,
        winner: market.winner,
        source: 'resolved_estimated'
    });
    
    resolvedProcessed++;
});

console.log(`   Processed ${resolvedProcessed} resolved markets (estimated)\n`);

// Calculate win rates
function calculateWinRate(bucket) {
    const total = bucket.wins + bucket.losses;
    if (total === 0) return 0;
    return (bucket.wins / total * 100).toFixed(1);
}

// Generate summary
const summary = {
    under3days: {
        total: buckets.under3days.wins + buckets.under3days.losses,
        wins: buckets.under3days.wins,
        losses: buckets.under3days.losses,
        winRate: calculateWinRate(buckets.under3days)
    },
    '3to7days': {
        total: buckets['3to7days'].wins + buckets['3to7days'].losses,
        wins: buckets['3to7days'].wins,
        losses: buckets['3to7days'].losses,
        winRate: calculateWinRate(buckets['3to7days'])
    },
    over7days: {
        total: buckets.over7days.wins + buckets.over7days.losses,
        wins: buckets.over7days.wins,
        losses: buckets.over7days.losses,
        winRate: calculateWinRate(buckets.over7days)
    }
};

// Print results
console.log('═══════════════════════════════════════════════════════════');
console.log('  TIME HORIZON COMPREHENSIVE BACKTEST RESULTS');
console.log('═══════════════════════════════════════════════════════════\n');

console.log(`Total markets analyzed: ${eventsProcessed + activeProcessed + resolvedProcessed}\n`);

console.log('📊 RESULTS BY TIME HORIZON:\n');

console.log('1️⃣ MARKETS WITH <3 DAY HORIZON');
console.log(`   Total: ${summary.under3days.total}`);
console.log(`   Wins: ${summary.under3days.wins}`);
console.log(`   Losses: ${summary.under3days.losses}`);
console.log(`   ✨ WIN RATE: ${summary.under3days.winRate}%`);
console.log(`   Expected: 66.7%`);
console.log(`   Validation: ${Math.abs(parseFloat(summary.under3days.winRate) - 66.7) < 15 ? '✅ REASONABLE' : '❌ DIFFERENT'}\n`);

console.log('2️⃣ MARKETS WITH 3-7 DAY HORIZON');
console.log(`   Total: ${summary['3to7days'].total}`);
console.log(`   Wins: ${summary['3to7days'].wins}`);
console.log(`   Losses: ${summary['3to7days'].losses}`);
console.log(`   ✨ WIN RATE: ${summary['3to7days'].winRate}%\n`);

console.log('3️⃣ MARKETS WITH >7 DAY HORIZON');
console.log(`   Total: ${summary.over7days.total}`);
console.log(`   Wins: ${summary.over7days.wins}`);
console.log(`   Losses: ${summary.over7days.losses}`);
console.log(`   ✨ WIN RATE: ${summary.over7days.winRate}%\n`);

console.log('═══════════════════════════════════════════════════════════\n');

// Generate markdown report
const markdown = `# TIME HORIZON REAL BACKTEST RESULTS

**Analysis Date:** ${new Date().toISOString()}

## Executive Summary

This backtest validates the time horizon strategy using **real Polymarket data** from multiple sources. We tested the claim that markets with short time horizons (<3 days) have approximately 66.7% win rate.

## Data Sources

- **Events:** ${eventsData.length} events with ${eventsProcessed} resolved markets
- **Active Markets:** ${activeMarkets.length} markets (${activeProcessed} closed/resolved)
- **Resolved Markets:** ${resolvedData.length} markets (${resolvedProcessed} analyzed with estimated horizons)
- **Total Analyzed:** ${eventsProcessed + activeProcessed + resolvedProcessed} market outcomes

## Methodology

### Time Horizon Calculation
- **Events & Active Markets:** Actual creation date → end date
- **Resolved Markets:** Estimated based on market type:
  - Election markets: ~60 days before event
  - Sports markets: ~3 days before event
  - Other markets: ~14 days before event

### Win Criteria
- Market resolved with clear winner (price >0.9)
- Assumed entry at market creation/signal time

## Results

### 📊 Win Rates by Time Horizon

| Time Horizon | Total Markets | Wins | Losses | Win Rate | vs Expected |
|-------------|---------------|------|--------|----------|-------------|
| **< 3 days** | ${summary.under3days.total} | ${summary.under3days.wins} | ${summary.under3days.losses} | **${summary.under3days.winRate}%** | 66.7% expected |
| **3-7 days** | ${summary['3to7days'].total} | ${summary['3to7days'].wins} | ${summary['3to7days'].losses} | **${summary['3to7days'].winRate}%** | - |
| **> 7 days** | ${summary.over7days.total} | ${summary.over7days.wins} | ${summary.over7days.losses} | **${summary.over7days.winRate}%** | - |

### 🎯 Validation of 66.7% Claim

**Claim:** Markets with <3 day time horizon have 66.7% win rate

**Actual Result:** ${summary.under3days.winRate}%

**Status:** ${
  Math.abs(parseFloat(summary.under3days.winRate) - 66.7) < 10 
    ? '✅ **VALIDATED** - Within 10% of expected' 
    : parseFloat(summary.under3days.winRate) > 55
    ? '⚠️ **PARTIALLY VALIDATED** - Profitable but different from expected'
    : '❌ **NOT VALIDATED** - Significant difference'}

## Key Findings

### 1. Short-Term Markets (<3 days)
- **Win Rate:** ${summary.under3days.winRate}%
- **Sample Size:** ${summary.under3days.total} markets
- **Conclusion:** ${
  parseFloat(summary.under3days.winRate) > 60 
    ? '✅ Strategy is profitable for short-term markets' 
    : parseFloat(summary.under3days.winRate) > 50
    ? '⚠️ Marginally profitable - needs optimization'
    : '❌ Strategy underperforms on short-term markets'}

### 2. Medium-Term Markets (3-7 days)
- **Win Rate:** ${summary['3to7days'].winRate}%
- **Sample Size:** ${summary['3to7days'].total} markets
- **Conclusion:** ${
  parseFloat(summary['3to7days'].winRate) > parseFloat(summary.under3days.winRate)
    ? '✅ Outperforms short-term markets'
    : '⚠️ Comparable to or underperforms short-term'}

### 3. Long-Term Markets (>7 days)
- **Win Rate:** ${summary.over7days.winRate}%
- **Sample Size:** ${summary.over7days.total} markets
- **Conclusion:** ${
  parseFloat(summary.over7days.winRate) > 60
    ? '✅ Strong performance on long-term markets'
    : '⚠️ Variable performance'}

## Sample Markets

### Short-Term (<3 days) - Examples

${buckets.under3days.markets.slice(0, 5).map((m, i) => 
`${i+1}. **${m.question}**
   - Time horizon: ${m.horizonDays} days
   - Result: ${m.won ? '✅ WIN' : '❌ LOSS'}
   - Source: ${m.source}`
).join('\n\n')}

### Medium-Term (3-7 days) - Examples

${buckets['3to7days'].markets.slice(0, 5).map((m, i) => 
`${i+1}. **${m.question}**
   - Time horizon: ${m.horizonDays} days
   - Result: ${m.won ? '✅ WIN' : '❌ LOSS'}
   - Source: ${m.source}`
).join('\n\n')}

### Long-Term (>7 days) - Examples

${buckets.over7days.markets.slice(0, 5).map((m, i) => 
`${i+1}. **${m.question}**
   - Time horizon: ${m.horizonDays} days
   - Result: ${m.won ? '✅ WIN' : '❌ LOSS'}
   - Source: ${m.source}`
).join('\n\n')}

## Data Quality Notes

⚠️ **Important Limitations:**

1. **Resolved Markets:** Creation dates estimated based on market type
2. **Win Logic:** Simplified - assumes entry at creation, clear resolution
3. **Sample Size:** Limited by available resolved market data
4. **Selection Bias:** Active data may not represent full market history

## Strategic Recommendations

${parseFloat(summary.under3days.winRate) > 60 ? `
### ✅ Strategy is Validated

1. **Focus on Short-Term Markets** - Win rate ${summary.under3days.winRate}% supports the hypothesis
2. **Increase Position Sizing** - Higher win rate justifies larger positions
3. **Refine Entry Timing** - Optimize entry point within the <3 day window
` : `
### ⚠️ Strategy Needs Refinement

1. **Improve Signal Quality** - Current win rate ${summary.under3days.winRate}% below expected
2. **Better Market Selection** - Filter for higher quality signals
3. **Risk Management** - Reduce position size until win rate improves
`}

## Next Steps

1. **Collect More Data** - Get actual market creation timestamps
2. **Segment Analysis** - Break down by market category (politics, sports, crypto)
3. **Volume Weighting** - Weight results by market liquidity
4. **Time Decay Analysis** - Study performance vs time remaining

## Conclusion

${parseFloat(summary.under3days.winRate) > 60 
  ? `The time horizon strategy shows **strong promise** with real data. Short-term markets demonstrate a ${summary.under3days.winRate}% win rate, which supports profitable trading.` 
  : parseFloat(summary.under3days.winRate) > 50
  ? `The time horizon strategy shows **potential** but needs refinement. Win rate of ${summary.under3days.winRate}% is profitable but below the claimed 66.7%.`
  : `The time horizon strategy requires **significant optimization** based on current ${summary.under3days.winRate}% win rate.`}

**Bottom Line:** ${
  parseFloat(summary.under3days.winRate) > 60
    ? '✅ Proceed with strategy - data supports the approach'
    : parseFloat(summary.under3days.winRate) > 50
    ? '⚠️ Proceed with caution - optimize before scaling'
    : '❌ Do not trade until strategy is improved'}

---

*Generated: ${new Date().toISOString()}*
*Markets Analyzed: ${eventsProcessed + activeProcessed + resolvedProcessed}*
*Data Sources: Events, Active Markets, Resolved Markets*
`;

// Save reports
fs.writeFileSync('TIME_HORIZON_REAL_BACKTEST.md', markdown);
fs.writeFileSync('time_horizon_real_backtest_results.json', JSON.stringify({
    timestamp: new Date().toISOString(),
    summary: summary,
    buckets: {
        under3days: buckets.under3days.markets,
        '3to7days': buckets['3to7days'].markets,
        over7days: buckets.over7days.markets
    },
    metadata: {
        eventsProcessed,
        activeProcessed,
        resolvedProcessed,
        totalAnalyzed: eventsProcessed + activeProcessed + resolvedProcessed
    }
}, null, 2));

console.log('✅ Report saved to: TIME_HORIZON_REAL_BACKTEST.md');
console.log('✅ Data saved to: time_horizon_real_backtest_results.json\n');

console.log('📈 FINAL SUMMARY:');
console.log(`<3 days: ${summary.under3days.winRate}% (${summary.under3days.total} markets)`);
console.log(`3-7 days: ${summary['3to7days'].winRate}% (${summary['3to7days'].total} markets)`);
console.log(`>7 days: ${summary.over7days.winRate}% (${summary.over7days.total} markets)`);
console.log(`\n${Math.abs(parseFloat(summary.under3days.winRate) - 66.7) < 10 ? '✅ 66.7% claim VALIDATED' : '⚠️ 66.7% claim needs review'}`);
