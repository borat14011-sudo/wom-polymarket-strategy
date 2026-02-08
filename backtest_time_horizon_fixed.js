// TIME HORIZON REAL BACKTEST - FIXED VERSION
// Validates win rate with PROPER entry/exit logic

const fs = require('fs');

console.log('🔍 Loading resolved markets data...\n');

const resolvedData = JSON.parse(fs.readFileSync('polymarket_resolved_markets.json', 'utf8').replace(/^\uFEFF/, ''));

console.log(`✅ Loaded ${resolvedData.length} resolved markets\n`);

// We'll use a simple but valid strategy:
// - Entry: Buy YES at market creation (simulated as 50% probability)
// - Exit: Market resolves
// - Win: YES wins (winner = "Yes", final_prices = "1|0")
// - Loss: NO wins (winner = "No", final_prices = "0|1")

// Time horizon estimation based on market type
function estimateTimeHorizonDays(market) {
    const title = (market.question + ' ' + market.event_title).toLowerCase();
    
    if (title.includes('election') || title.includes('senate') || title.includes('president')) {
        return 60; // Election markets created ~60 days before
    } else if (title.includes('nba') || title.includes('nfl') || title.includes('game') || title.includes('matchup')) {
        return 2; // Sports markets created ~2 days before
    } else if (title.includes('weekend') || title.includes('opening')) {
        return 7; // Weekend/event markets ~1 week
    } else {
        return 14; // Default: 2 weeks
    }
}

// Determine if we won with a YES position
function checkWin(market) {
    // If market winner is "Yes", we won
    // If market winner is "No", we lost
    return market.winner === "Yes";
}

// Analyze markets
const buckets = {
    'under3days': { wins: 0, losses: 0, markets: [] },
    '3to7days': { wins: 0, losses: 0, markets: [] },
    'over7days': { wins: 0, losses: 0, markets: [] }
};

let totalProcessed = 0;
let skipped = 0;

resolvedData.forEach(market => {
    // Skip if missing critical data
    if (!market.winner || !market.final_prices) {
        skipped++;
        return;
    }
    
    // Estimate time horizon
    const horizonDays = estimateTimeHorizonDays(market);
    
    // Determine bucket
    let bucket;
    if (horizonDays < 3) {
        bucket = 'under3days';
    } else if (horizonDays >= 3 && horizonDays <= 7) {
        bucket = '3to7days';
    } else {
        bucket = 'over7days';
    }
    
    // Check if we won (YES position)
    const won = checkWin(market);
    
    if (won) {
        buckets[bucket].wins++;
    } else {
        buckets[bucket].losses++;
    }
    
    buckets[bucket].markets.push({
        question: market.question,
        horizonDays: horizonDays,
        winner: market.winner,
        finalPrices: market.final_prices,
        won: won
    });
    
    totalProcessed++;
});

console.log(`📊 Processed ${totalProcessed} markets (skipped ${skipped})\n`);

// Calculate win rates
function calculateWinRate(bucket) {
    const total = bucket.wins + bucket.losses;
    if (total === 0) return { rate: 0, total: 0 };
    return {
        rate: (bucket.wins / total * 100).toFixed(1),
        total: total
    };
}

const results = {
    under3days: calculateWinRate(buckets.under3days),
    '3to7days': calculateWinRate(buckets['3to7days']),
    over7days: calculateWinRate(buckets.over7days)
};

// Print results
console.log('═══════════════════════════════════════════════════════════');
console.log('  TIME HORIZON REAL BACKTEST - CORRECTED');
console.log('  Strategy: Enter YES at creation, hold until resolution');
console.log('═══════════════════════════════════════════════════════════\n');

console.log('📊 RESULTS BY TIME HORIZON:\n');

console.log('1️⃣ MARKETS WITH <3 DAY HORIZON (estimated)');
console.log(`   Total: ${results.under3days.total}`);
console.log(`   Wins: ${buckets.under3days.wins}`);
console.log(`   Losses: ${buckets.under3days.losses}`);
console.log(`   ✨ WIN RATE: ${results.under3days.rate}%`);
console.log(`   Expected: 66.7%`);
const diff3 = Math.abs(parseFloat(results.under3days.rate) - 66.7);
console.log(`   Validation: ${diff3 < 10 ? '✅ CLOSE' : diff3 < 20 ? '⚠️ MODERATE DIFF' : '❌ DIFFERENT'}\n`);

console.log('2️⃣ MARKETS WITH 3-7 DAY HORIZON (estimated)');
console.log(`   Total: ${results['3to7days'].total}`);
console.log(`   Wins: ${buckets['3to7days'].wins}`);
console.log(`   Losses: ${buckets['3to7days'].losses}`);
console.log(`   ✨ WIN RATE: ${results['3to7days'].rate}%\n`);

console.log('3️⃣ MARKETS WITH >7 DAY HORIZON (estimated)');
console.log(`   Total: ${results.over7days.total}`);
console.log(`   Wins: ${buckets.over7days.wins}`);
console.log(`   Losses: ${buckets.over7days.losses}`);
console.log(`   ✨ WIN RATE: ${results.over7days.rate}%\n`);

console.log('═══════════════════════════════════════════════════════════\n');

// Generate detailed markdown report
const markdown = `# TIME HORIZON REAL BACKTEST RESULTS

**Analysis Date:** ${new Date().toISOString()}

## Executive Summary

This backtest validates the time horizon strategy using **${totalProcessed} real resolved Polymarket markets**. We tested the claim that markets with shorter time horizons (<3 days) have a 66.7% win rate.

### ⚠️ Important Caveats

1. **Time Horizons are ESTIMATED** - Actual market creation dates not available
   - Election markets: assumed 60 days before event
   - Sports markets: assumed 2 days before event
   - Other markets: assumed 14 days before event

2. **Simple Strategy** - Enter YES at market creation, hold until resolution
   - This is NOT a sophisticated signal-based strategy
   - Real trading would use momentum, volume, ROC signals
   - Results show baseline probabilities, not actual trading performance

## Methodology

- **Data:** ${totalProcessed} resolved Polymarket markets (${skipped} skipped due to incomplete data)
- **Entry Strategy:** Buy YES at market creation (simulated)
- **Exit:** Hold until market resolves
- **Win Condition:** Market resolves YES

## Results

### 📊 Win Rates by Time Horizon

| Time Horizon | Total Markets | Wins | Losses | Win Rate | vs Expected |
|-------------|---------------|------|--------|----------|-------------|
| **< 3 days** | ${results.under3days.total} | ${buckets.under3days.wins} | ${buckets.under3days.losses} | **${results.under3days.rate}%** | 66.7% expected |
| **3-7 days** | ${results['3to7days'].total} | ${buckets['3to7days'].wins} | ${buckets['3to7days'].losses} | **${results['3to7days'].rate}%** | - |
| **> 7 days** | ${results.over7days.total} | ${buckets.over7days.wins} | ${buckets.over7days.losses} | **${results.over7days.rate}%** | - |

### 🎯 Validation of 66.7% Claim

**Claim:** Markets with <3 day horizon have 66.7% win rate

**Actual Result:** ${results.under3days.rate}%

**Difference:** ${diff3.toFixed(1)}%

**Status:** ${
  diff3 < 10 
    ? '✅ **VALIDATED** - Within 10% of expected' 
    : diff3 < 20
    ? '⚠️ **PARTIALLY VALIDATED** - Within 20% of expected'
    : '❌ **NOT VALIDATED** - >20% difference'}

## Analysis

### Short-Term Markets (<3 days)
- **Win Rate:** ${results.under3days.rate}%
- **Sample:** ${results.under3days.total} markets (mostly sports)
- **Interpretation:** ${
  parseFloat(results.under3days.rate) > 55
    ? 'Positive edge - markets slightly favor YES outcomes'
    : parseFloat(results.under3days.rate) < 45
    ? 'Negative edge - markets slightly favor NO outcomes'
    : 'Neutral - approximately 50/50 outcomes'}

### Medium-Term Markets (3-7 days)
- **Win Rate:** ${results['3to7days'].rate}%  
- **Sample:** ${results['3to7days'].total} markets
- **Interpretation:** ${
  parseFloat(results['3to7days'].rate) > 60
    ? 'Strong positive edge'
    : parseFloat(results['3to7days'].rate) > 45
    ? 'Slight positive edge or neutral'
    : 'Negative edge'}

### Long-Term Markets (>7 days)
- **Win Rate:** ${results.over7days.rate}%
- **Sample:** ${results.over7days.total} markets (mostly elections)
- **Interpretation:** ${
  parseFloat(results.over7days.rate) > 55
    ? 'Positive edge - election markets tend toward YES outcomes in our sample'
    : 'Approximately balanced outcomes'}

## Sample Markets by Category

### Short-Term (<3 days) - Top 10

${buckets.under3days.markets.slice(0, 10).map((m, i) => 
`${i+1}. **${m.question}**
   - Estimated horizon: ${m.horizonDays} days
   - Winner: ${m.winner}
   - Final prices: ${m.finalPrices}
   - Our result: ${m.won ? '✅ WIN' : '❌ LOSS'}`
).join('\n\n')}

### Medium-Term (3-7 days) - Top 10

${buckets['3to7days'].markets.slice(0, Math.min(10, buckets['3to7days'].markets.length)).map((m, i) => 
`${i+1}. **${m.question}**
   - Estimated horizon: ${m.horizonDays} days
   - Winner: ${m.winner}
   - Final prices: ${m.finalPrices}
   - Our result: ${m.won ? '✅ WIN' : '❌ LOSS'}`
).join('\n\n')}

### Long-Term (>7 days) - Top 10

${buckets.over7days.markets.slice(0, 10).map((m, i) => 
`${i+1}. **${m.question}**
   - Estimated horizon: ${m.horizonDays} days
   - Winner: ${m.winner}
   - Final prices: ${m.finalPrices}
   - Our result: ${m.won ? '✅ WIN' : '❌ LOSS'}`
).join('\n\n')}

## Key Findings

### 1. The 66.7% Claim

${diff3 < 10 
  ? `✅ **Validated** - Short-term markets show ${results.under3days.rate}% win rate, close to claimed 66.7%`
  : diff3 < 20
  ? `⚠️ **Partially Validated** - ${results.under3days.rate}% is within reasonable variance of 66.7%`
  : `❌ **Not Validated** - ${results.under3days.rate}% differs significantly from 66.7%`}

### 2. Time Horizon Correlation

${parseFloat(results.under3days.rate) > parseFloat(results.over7days.rate)
  ? '✅ Short-term markets outperform long-term (supports time horizon hypothesis)'
  : '❌ Long-term markets outperform short-term (contradicts time horizon hypothesis)'}

### 3. Data Quality Issues

⚠️ **Critical Limitations:**
- Market creation dates are ESTIMATED, not actual
- Sample size for <3 day markets is small (${results.under3days.total})
- Strategy is overly simplified (just buy YES)
- No account for entry timing, price, liquidity

## Strategic Implications

${parseFloat(results.under3days.rate) > 60 
  ? `### ✅ Time Horizon Strategy Shows Promise

1. Short-term markets have ${results.under3days.rate}% win rate
2. This suggests YES outcomes are more likely in short-duration markets
3. **Recommendation:** Focus on short-term markets with proper entry signals`
  : `### ⚠️ Results Inconclusive

1. Win rate of ${results.under3days.rate}% does not strongly support the hypothesis
2. Small sample size (${results.under3days.total} markets) limits confidence
3. **Recommendation:** Collect more data before implementing strategy`}

## What's Missing

To properly validate the 66.7% claim, we need:

1. **Actual Market Creation Timestamps** - not estimates
2. **Entry Price Data** - not just "buy YES"
3. **Signal-Based Entry** - momentum, ROC, volume triggers
4. **Position Sizing** - Kelly criterion or fixed fraction
5. **More Data** - especially for <3 day markets

## Recommendations

### If Implementing Time Horizon Strategy:

1. **Collect Live Data** - Start tracking markets from creation to resolution
2. **Test Entry Signals** - Don't just buy at creation, wait for signals
3. **Category Analysis** - Sports vs politics vs crypto may differ
4. **Volume Filter** - Only trade high-liquidity markets
5. **Backtest with Price Data** - Use CLOB data for realistic entry/exit prices

### For This Dataset:

${results.under3days.total < 10
  ? '❌ Sample size too small for <3 day markets - collect more data'
  : results.under3days.total < 30
  ? '⚠️ Limited sample size - findings are preliminary'
  : '✅ Reasonable sample size - findings have moderate confidence'}

## Conclusion

**Bottom Line:** ${
  diff3 < 10 && parseFloat(results.under3days.rate) > 60
    ? '✅ Data supports time horizon hypothesis - short-term markets show profitable characteristics'
    : diff3 < 20 && results.under3days.total > 20
    ? '⚠️ Weak support for hypothesis - more data needed'
    : '❌ Insufficient evidence to validate 66.7% claim with current data'}

${parseFloat(results.under3days.rate) > 55
  ? '**Proceed with strategy** but start small and collect live data to validate assumptions.'
  : '**Do not implement** until you have actual market creation timestamps and better entry signals.'}

---

*Generated: ${new Date().toISOString()}*  
*Markets Analyzed: ${totalProcessed}*  
*Strategy: Simple YES entry at creation*  
*Time Horizons: ESTIMATED (see caveats)*
`;

// Save report
fs.writeFileSync('TIME_HORIZON_REAL_BACKTEST.md', markdown);
console.log('✅ Report saved to: TIME_HORIZON_REAL_BACKTEST.md\n');

// Save JSON data
const jsonOutput = {
    timestamp: new Date().toISOString(),
    metadata: {
        totalProcessed,
        skipped,
        strategy: 'Buy YES at creation, hold to resolution',
        dataSource: 'polymarket_resolved_markets.json',
        caveats: 'Time horizons are ESTIMATED based on market type'
    },
    results: {
        under3days: {
            winRate: results.under3days.rate,
            total: results.under3days.total,
            wins: buckets.under3days.wins,
            losses: buckets.under3days.losses,
            markets: buckets.under3days.markets
        },
        '3to7days': {
            winRate: results['3to7days'].rate,
            total: results['3to7days'].total,
            wins: buckets['3to7days'].wins,
            losses: buckets['3to7days'].losses,
            markets: buckets['3to7days'].markets
        },
        over7days: {
            winRate: results.over7days.rate,
            total: results.over7days.total,
            wins: buckets.over7days.wins,
            losses: buckets.over7days.losses,
            markets: buckets.over7days.markets
        }
    }
};

fs.writeFileSync('time_horizon_real_backtest_results.json', JSON.stringify(jsonOutput, null, 2));
console.log('✅ Data saved to: time_horizon_real_backtest_results.json\n');

console.log('📈 SUMMARY:');
console.log(`<3 days: ${results.under3days.rate}% (${results.under3days.total} markets) - ${diff3 < 10 ? 'CLOSE TO 66.7%' : 'DIFFERS FROM 66.7%'}`);
console.log(`3-7 days: ${results['3to7days'].rate}% (${results['3to7days'].total} markets)`);
console.log(`>7 days: ${results.over7days.rate}% (${results.over7days.total} markets)`);
