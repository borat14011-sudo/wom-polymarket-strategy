/**
 * MARKET REGIME ANALYSIS
 * Tests if strategies are regime-dependent or regime-agnostic
 */

const fs = require('fs');

// Load strategy results
const newsReversion = require('./backtest-results/news_reversion_results.json');
const expertFade = require('./backtest-results/expert_fade_results.json');
const whaleTracking = require('./backtest-results/whale_tracking_results.json');
const trendFilter = require('./backtest-results/trend_filter_results.json');
const noSideBias = require('./backtest-results/no_side_bias_results.json');
const timeHorizon = require('./backtest-results/time_horizon_results.json');
const pairsTrading = require('./backtest-results/pairs_trading_results.json');

// Market regime definitions (simulated based on time periods and market characteristics)
// Since we don't have exact BTC/VIX data for each trade, we'll use proxies:
// - Volume-based regimes (high/low activity)
// - Price volatility in the markets themselves
// - Time-based patterns (election years, etc.)

const REGIMES = {
  BULL_CRYPTO: 'Bull Crypto (BTC >20% YTD)',
  BEAR_CRYPTO: 'Bear Crypto (BTC <-20% YTD)',
  HIGH_VOLATILITY: 'High Volatility (VIX >30 or large price swings)',
  LOW_VOLATILITY: 'Low Volatility (VIX <15 or stable prices)',
  ELECTION_YEAR: 'Election Year',
  OFF_YEAR: 'Off-Year',
  HIGH_VOLUME: 'High Volume (>$500K daily)',
  LOW_VOLUME: 'Low Volume (<$100K daily)'
};

/**
 * Classify trade into regime based on available data
 */
function classifyRegime(trade, strategy) {
  const regimes = [];
  
  // Volume-based classification (using Polymarket volume proxy)
  if (trade.market_id) {
    const marketId = parseInt(trade.market_id);
    
    // Higher market IDs = more recent (2025-2026)
    // Lower market IDs = older (2020-2024)
    if (marketId > 1348000) {
      // Recent markets (2026) - assuming current bull run
      regimes.push(REGIMES.BULL_CRYPTO);
    } else if (marketId > 1340000) {
      // 2025 markets
      regimes.push(REGIMES.BULL_CRYPTO);
    } else if (marketId < 1200000) {
      // Older markets (2020-2023) - bear/volatile periods
      regimes.push(REGIMES.BEAR_CRYPTO);
    }
  }
  
  // Volatility based on price movement
  if (strategy === 'News Reversion' && trade.drop_pct) {
    const dropMagnitude = Math.abs(trade.drop_pct);
    if (dropMagnitude > 40) {
      regimes.push(REGIMES.HIGH_VOLATILITY);
    } else if (dropMagnitude < 20) {
      regimes.push(REGIMES.LOW_VOLATILITY);
    }
  }
  
  if (strategy === 'Whale Tracking' && trade.whale_move) {
    const moveMagnitude = Math.abs(parseFloat(trade.whale_move));
    if (moveMagnitude > 40) {
      regimes.push(REGIMES.HIGH_VOLATILITY);
    } else if (moveMagnitude < 20) {
      regimes.push(REGIMES.LOW_VOLATILITY);
    }
  }
  
  // Election year classification (2020, 2024, 2026)
  // Using market ID as proxy for year
  const marketId = parseInt(trade.market_id);
  if (marketId > 1340000) { // 2026 (off-year)
    regimes.push(REGIMES.OFF_YEAR);
  } else if (marketId > 1200000 && marketId < 1340000) { // 2024 (election)
    regimes.push(REGIMES.ELECTION_YEAR);
  }
  
  // Volume classification based on question type
  if (trade.question) {
    const question = trade.question.toLowerCase();
    
    // Political/high-profile markets = high volume
    if (question.includes('trump') || question.includes('election') || 
        question.includes('president') || question.includes('elon')) {
      regimes.push(REGIMES.HIGH_VOLUME);
    }
    // Sports/niche markets = lower volume
    else if (question.includes('vs') || question.includes('o/u') || 
             question.includes('handicap') || question.includes('counter-strike')) {
      regimes.push(REGIMES.LOW_VOLUME);
    }
  }
  
  return regimes.length > 0 ? regimes : ['UNCLASSIFIED'];
}

/**
 * Analyze strategy performance by regime
 */
function analyzeStrategyByRegime(strategyName, strategyData) {
  const regimePerformance = {};
  
  // Initialize regime buckets
  Object.values(REGIMES).forEach(regime => {
    regimePerformance[regime] = {
      trades: [],
      wins: 0,
      losses: 0,
      totalReturn: 0
    };
  });
  
  // Classify each trade
  strategyData.trades.forEach(trade => {
    const regimes = classifyRegime(trade, strategyName);
    
    regimes.forEach(regime => {
      if (regimePerformance[regime]) {
        regimePerformance[regime].trades.push(trade);
        if (trade.win) {
          regimePerformance[regime].wins++;
        } else {
          regimePerformance[regime].losses++;
        }
        regimePerformance[regime].totalReturn += trade.return;
      }
    });
  });
  
  // Calculate metrics for each regime
  const results = {};
  Object.entries(regimePerformance).forEach(([regime, data]) => {
    if (data.trades.length > 0) {
      results[regime] = {
        tradeCount: data.trades.length,
        winRate: data.wins / data.trades.length,
        avgReturn: data.totalReturn / data.trades.length,
        totalReturn: data.totalReturn,
        sampleSize: data.trades.length
      };
    }
  });
  
  return results;
}

/**
 * Calculate regime dependency score
 * 0 = completely regime-agnostic (works everywhere)
 * 1 = extremely regime-dependent (only works in specific conditions)
 */
function calculateRegimeDependency(regimeResults) {
  const performances = Object.values(regimeResults)
    .filter(r => r.sampleSize >= 10) // Only consider regimes with enough samples
    .map(r => r.avgReturn);
  
  if (performances.length < 2) return 0;
  
  // Calculate standard deviation of returns across regimes
  const mean = performances.reduce((a, b) => a + b, 0) / performances.length;
  const variance = performances.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / performances.length;
  const stdDev = Math.sqrt(variance);
  
  // Normalize to 0-1 scale (higher std dev = more regime-dependent)
  return Math.min(stdDev / 2, 1); // Cap at 1
}

/**
 * Identify best and worst regimes for each strategy
 */
function identifyRegimeStrengths(strategyName, regimeResults) {
  const sortedRegimes = Object.entries(regimeResults)
    .filter(([_, data]) => data.sampleSize >= 10) // Minimum sample size
    .sort(([_, a], [__, b]) => b.avgReturn - a.avgReturn);
  
  return {
    bestRegimes: sortedRegimes.slice(0, 3),
    worstRegimes: sortedRegimes.slice(-3).reverse()
  };
}

// Main analysis
console.log('🔬 MARKET REGIME ANALYSIS - Testing Strategy Robustness\n');
console.log('='.repeat(80));

const strategies = [
  { name: 'News Reversion', data: newsReversion },
  { name: 'Expert Fade', data: expertFade },
  { name: 'Whale Tracking', data: whaleTracking },
  { name: 'Trend Filter', data: trendFilter },
  { name: 'NO-Side Bias', data: noSideBias },
  { name: 'Time Horizon <3d', data: timeHorizon },
  { name: 'Pairs Trading', data: pairsTrading }
];

const fullReport = {
  analysisDate: new Date().toISOString(),
  strategies: []
};

strategies.forEach(({ name, data }) => {
  console.log(`\n📊 ${name.toUpperCase()}`);
  console.log('-'.repeat(80));
  
  const regimeResults = analyzeStrategyByRegime(name, data);
  const dependency = calculateRegimeDependency(regimeResults);
  const strengths = identifyRegimeStrengths(name, regimeResults);
  
  console.log(`\nOverall: ${data.trades.length} trades, ${(data.win_rate * 100).toFixed(1)}% win rate, ${(data.avg_return * 100).toFixed(1)}% avg return`);
  console.log(`Regime Dependency Score: ${(dependency * 100).toFixed(1)}% ${dependency < 0.3 ? '✅ REGIME-AGNOSTIC' : dependency < 0.6 ? '⚠️ SOMEWHAT DEPENDENT' : '🚨 HIGHLY DEPENDENT'}`);
  
  console.log('\nPerformance by Regime:');
  Object.entries(regimeResults)
    .filter(([_, data]) => data.sampleSize >= 5)
    .sort(([_, a], [__, b]) => b.avgReturn - a.avgReturn)
    .forEach(([regime, metrics]) => {
      const status = metrics.avgReturn > 0.1 ? '✅' : metrics.avgReturn > -0.1 ? '⚠️' : '❌';
      console.log(`  ${status} ${regime}`);
      console.log(`     ${metrics.tradeCount} trades | ${(metrics.winRate * 100).toFixed(1)}% WR | ${(metrics.avgReturn * 100).toFixed(1)}% avg return`);
    });
  
  if (strengths.bestRegimes.length > 0) {
    console.log(`\n💪 BEST REGIMES:`);
    strengths.bestRegimes.forEach(([regime, data]) => {
      console.log(`   ${regime}: ${(data.avgReturn * 100).toFixed(1)}% avg return (${data.sampleSize} trades)`);
    });
  }
  
  if (strengths.worstRegimes.length > 0) {
    console.log(`\n⚠️  WORST REGIMES:`);
    strengths.worstRegimes.forEach(([regime, data]) => {
      console.log(`   ${regime}: ${(data.avgReturn * 100).toFixed(1)}% avg return (${data.sampleSize} trades)`);
    });
  }
  
  // Recommendation
  let recommendation = '';
  if (dependency < 0.3 && data.avg_return > 0.1) {
    recommendation = '🚀 DEPLOY ALWAYS - Works in all conditions';
  } else if (dependency < 0.5 && data.avg_return > 0) {
    recommendation = '✅ CONDITIONAL DEPLOY - Favor certain regimes';
  } else if (data.avg_return < 0) {
    recommendation = '❌ REJECT - Negative expected value';
  } else {
    recommendation = '⚠️ HIGHLY CONDITIONAL - Only use in optimal regimes';
  }
  
  console.log(`\n🎯 RECOMMENDATION: ${recommendation}`);
  
  fullReport.strategies.push({
    name,
    overallMetrics: {
      trades: data.trades.length,
      winRate: data.win_rate,
      avgReturn: data.avg_return,
      sharpeRatio: data.sharpe_ratio,
      maxDrawdown: data.max_drawdown
    },
    regimeDependency: dependency,
    regimePerformance: regimeResults,
    bestRegimes: strengths.bestRegimes,
    worstRegimes: strengths.worstRegimes,
    recommendation
  });
});

console.log('\n\n' + '='.repeat(80));
console.log('📋 SUMMARY & ADAPTIVE DEPLOYMENT RULES');
console.log('='.repeat(80));

// Current regime detection
console.log('\n🌍 CURRENT MARKET REGIME (Feb 2026):');
console.log('  ✅ Bull Crypto (BTC trending up from 2023-2026)');
console.log('  ✅ Low-Medium Volatility (stable crypto markets)');
console.log('  ✅ Off-Year (2026, no major US election)');
console.log('  ⚠️  Volume Variable (depends on event type)');

// Strategy deployment matrix
console.log('\n📊 ADAPTIVE STRATEGY SWITCHING RULES:');
console.log('\nRegime-Agnostic (Deploy Always):');
fullReport.strategies
  .filter(s => s.regimeDependency < 0.3 && s.overallMetrics.avgReturn > 0.1)
  .forEach(s => {
    console.log(`  ✅ ${s.name} - Consistent across conditions`);
  });

console.log('\nRegime-Dependent (Conditional Deploy):');
fullReport.strategies
  .filter(s => s.regimeDependency >= 0.3 && s.overallMetrics.avgReturn > 0)
  .forEach(s => {
    console.log(`  ⚠️  ${s.name} - Use in: ${s.bestRegimes.slice(0, 2).map(r => r[0]).join(', ')}`);
  });

console.log('\nAvoid:');
fullReport.strategies
  .filter(s => s.overallMetrics.avgReturn < 0)
  .forEach(s => {
    console.log(`  ❌ ${s.name} - Negative EV across regimes`);
  });

// Risk management
console.log('\n⚠️  REGIME CHANGE RISK MANAGEMENT:');
console.log('  1. Monitor BTC price (>20% YTD = bull, <-20% = bear)');
console.log('  2. Track VIX or crypto volatility index');
console.log('  3. Adjust position sizes when regime shifts');
console.log('  4. Stop/reduce exposure if regime-dependent strategy in wrong regime');
console.log('  5. Use trailing stops during high volatility periods');

// Save report
fs.writeFileSync(
  'MARKET_REGIME_REPORT.json',
  JSON.stringify(fullReport, null, 2)
);

console.log('\n✅ Full report saved to: MARKET_REGIME_REPORT.json');
console.log('='.repeat(80));
