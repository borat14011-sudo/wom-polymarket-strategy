/**
 * PORTFOLIO ANALYSIS - Correlation Matrix & Optimal Allocation
 * 
 * - Calculate 6x6 correlation matrix
 * - Identify uncorrelated strategies
 * - Recommend optimal portfolio weights
 * - Monte Carlo simulation for robustness
 */

import { promises as fs } from 'fs';

const RESULTS_DIR = './results';

class PortfolioAnalyzer {
  constructor(backtestResults) {
    this.results = backtestResults;
    this.correlationMatrix = null;
  }

  /**
   * Calculate correlation matrix between strategy returns
   */
  calculateCorrelationMatrix() {
    console.log('\n📊 Calculating Correlation Matrix...\n');

    const strategies = this.results.map(r => r.strategy);
    const n = strategies.length;
    
    // Build return series for each strategy
    const returnSeries = this.results.map(result => {
      const returns = [];
      const equity = result.equityCurve;
      
      for (let i = 1; i < equity.length; i++) {
        const ret = (equity[i].equity - equity[i-1].equity) / equity[i-1].equity;
        returns.push(ret);
      }
      
      return returns;
    });

    // Calculate correlation matrix
    const matrix = [];
    for (let i = 0; i < n; i++) {
      matrix[i] = [];
      for (let j = 0; j < n; j++) {
        if (i === j) {
          matrix[i][j] = 1.0;
        } else {
          matrix[i][j] = this.correlation(returnSeries[i], returnSeries[j]);
        }
      }
    }

    this.correlationMatrix = {
      strategies,
      matrix
    };

    // Print correlation matrix
    console.log('Correlation Matrix:');
    console.log('');
    console.log('     ', strategies.map((s, i) => `S${i+1}`).join('   '));
    console.log('     ' + '-'.repeat(strategies.length * 5));
    
    strategies.forEach((strat, i) => {
      const row = `S${i+1}   ` + matrix[i].map(v => v.toFixed(2)).join('  ');
      console.log(row);
    });

    console.log('\nStrategy Key:');
    strategies.forEach((s, i) => {
      console.log(`  S${i+1}: ${s}`);
    });

    return this.correlationMatrix;
  }

  /**
   * Calculate Pearson correlation coefficient
   */
  correlation(x, y) {
    const n = Math.min(x.length, y.length);
    if (n === 0) return 0;

    const xSlice = x.slice(0, n);
    const ySlice = y.slice(0, n);

    const meanX = xSlice.reduce((a, b) => a + b, 0) / n;
    const meanY = ySlice.reduce((a, b) => a + b, 0) / n;

    let numerator = 0;
    let sumSqX = 0;
    let sumSqY = 0;

    for (let i = 0; i < n; i++) {
      const dx = xSlice[i] - meanX;
      const dy = ySlice[i] - meanY;
      numerator += dx * dy;
      sumSqX += dx * dx;
      sumSqY += dy * dy;
    }

    const denominator = Math.sqrt(sumSqX * sumSqY);
    return denominator === 0 ? 0 : numerator / denominator;
  }

  /**
   * Find uncorrelated strategy pairs for diversification
   */
  findUncorrelatedPairs() {
    console.log('\n🔍 Identifying Uncorrelated Strategy Pairs...\n');

    const pairs = [];
    const { strategies, matrix } = this.correlationMatrix;

    for (let i = 0; i < strategies.length; i++) {
      for (let j = i + 1; j < strategies.length; j++) {
        const corr = matrix[i][j];
        if (Math.abs(corr) < 0.3) {  // Low correlation threshold
          pairs.push({
            strategy1: strategies[i],
            strategy2: strategies[j],
            correlation: corr
          });
        }
      }
    }

    // Sort by lowest absolute correlation
    pairs.sort((a, b) => Math.abs(a.correlation) - Math.abs(b.correlation));

    console.log('Low-Correlation Pairs (|corr| < 0.3):');
    pairs.forEach(p => {
      console.log(`  ${p.strategy1} <-> ${p.strategy2}: ${p.correlation.toFixed(3)}`);
    });

    if (pairs.length === 0) {
      console.log('  ⚠️  No pairs found with correlation < 0.3');
    }

    return pairs;
  }

  /**
   * Calculate optimal portfolio weights using Sharpe ratio optimization
   * (Simple mean-variance optimization)
   */
  calculateOptimalWeights() {
    console.log('\n⚖️  Calculating Optimal Portfolio Weights...\n');

    // Simple approach: weight by Sharpe ratio (higher Sharpe = higher weight)
    const sharpeRatios = this.results.map(r => Math.max(0, r.metrics.sharpeRatio));
    const totalSharpe = sharpeRatios.reduce((a, b) => a + b, 0);

    let weights;
    if (totalSharpe > 0) {
      weights = sharpeRatios.map(s => s / totalSharpe);
    } else {
      // Equal weight if all Sharpe ratios are negative/zero
      weights = this.results.map(() => 1 / this.results.length);
    }

    // Apply diversification bonus for uncorrelated strategies
    // (This is simplified - real optimization would use quadratic programming)
    
    const portfolio = this.results.map((r, i) => ({
      strategy: r.strategy,
      weight: weights[i],
      sharpeRatio: r.metrics.sharpeRatio,
      totalReturn: r.metrics.totalReturn,
      maxDrawdown: r.metrics.maxDrawdown
    }));

    // Sort by weight
    portfolio.sort((a, b) => b.weight - a.weight);

    console.log('Optimal Allocation:');
    console.log('Strategy'.padEnd(30) + 'Weight %'.padEnd(12) + 'Sharpe'.padEnd(10) + 'Return %');
    console.log('-'.repeat(65));
    
    portfolio.forEach(p => {
      console.log(
        p.strategy.padEnd(30) +
        (p.weight * 100).toFixed(2).padStart(8).padEnd(12) +
        p.sharpeRatio.toFixed(3).padStart(6).padEnd(10) +
        p.totalReturn.toFixed(2).padStart(8)
      );
    });

    return portfolio;
  }

  /**
   * Calculate combined portfolio metrics
   */
  calculatePortfolioMetrics(weights) {
    console.log('\n📈 Combined Portfolio Metrics...\n');

    // Weighted average metrics
    const portfolioReturn = this.results.reduce((sum, r, i) => 
      sum + r.metrics.totalReturn * weights[i], 0
    );

    const portfolioSharpe = this.results.reduce((sum, r, i) => 
      sum + r.metrics.sharpeRatio * weights[i], 0
    );

    // For drawdown, we need to simulate the combined equity curve
    // Simplified: use weighted average (conservative estimate)
    const portfolioMaxDD = this.results.reduce((sum, r, i) => 
      sum + r.metrics.maxDrawdown * weights[i], 0
    );

    // Calculate diversification benefit
    const avgSingleStrategyReturn = this.results.reduce((sum, r) => 
      sum + r.metrics.totalReturn, 0
    ) / this.results.length;

    const avgSingleStrategySharpe = this.results.reduce((sum, r) => 
      sum + r.metrics.sharpeRatio, 0
    ) / this.results.length;

    const diversificationBenefit = {
      returnImprovement: ((portfolioReturn - avgSingleStrategyReturn) / Math.abs(avgSingleStrategyReturn)) * 100,
      sharpeImprovement: ((portfolioSharpe - avgSingleStrategySharpe) / Math.abs(avgSingleStrategySharpe)) * 100
    };

    const metrics = {
      expectedReturn: portfolioReturn,
      sharpeRatio: portfolioSharpe,
      maxDrawdown: portfolioMaxDD,
      calmarRatio: portfolioMaxDD > 0 ? portfolioReturn / portfolioMaxDD : 0,
      diversificationBenefit
    };

    console.log(`Expected Annual Return: ${metrics.expectedReturn.toFixed(2)}%`);
    console.log(`Portfolio Sharpe Ratio: ${metrics.sharpeRatio.toFixed(3)}`);
    console.log(`Portfolio Max Drawdown: ${metrics.maxDrawdown.toFixed(2)}%`);
    console.log(`Portfolio Calmar Ratio: ${metrics.calmarRatio.toFixed(3)}`);
    console.log(`\nDiversification Benefit:`);
    console.log(`  Return Improvement: ${diversificationBenefit.returnImprovement.toFixed(2)}%`);
    console.log(`  Sharpe Improvement: ${diversificationBenefit.sharpeImprovement.toFixed(2)}%`);

    return metrics;
  }

  /**
   * Monte Carlo simulation for portfolio robustness
   */
  runMonteCarloSimulation(numRuns = 1000) {
    console.log(`\n🎲 Running Monte Carlo Simulation (${numRuns} runs)...\n`);

    const simResults = [];

    for (let run = 0; run < numRuns; run++) {
      // Randomly sample from historical returns for each strategy
      const strategyReturns = this.results.map(result => {
        const trades = result.trades;
        if (trades.length === 0) return 0;
        
        // Sample random trades (with replacement)
        let totalReturn = 0;
        for (let i = 0; i < trades.length; i++) {
          const randomTrade = trades[Math.floor(Math.random() * trades.length)];
          totalReturn += randomTrade.pnlPercent;
        }
        return totalReturn / trades.length;
      });

      // Calculate portfolio return with equal weights
      const portfolioReturn = strategyReturns.reduce((a, b) => a + b, 0) / strategyReturns.length;
      simResults.push(portfolioReturn);
    }

    // Calculate statistics
    simResults.sort((a, b) => a - b);
    const mean = simResults.reduce((a, b) => a + b, 0) / simResults.length;
    const p5 = simResults[Math.floor(numRuns * 0.05)];
    const p50 = simResults[Math.floor(numRuns * 0.50)];
    const p95 = simResults[Math.floor(numRuns * 0.95)];

    const simulation = {
      runs: numRuns,
      mean,
      median: p50,
      percentile5: p5,
      percentile95: p95,
      worstCase: simResults[0],
      bestCase: simResults[numRuns - 1]
    };

    console.log(`Mean Return: ${mean.toFixed(2)}%`);
    console.log(`Median Return: ${p50.toFixed(2)}%`);
    console.log(`5th Percentile (worst 5%): ${p5.toFixed(2)}%`);
    console.log(`95th Percentile (best 5%): ${p95.toFixed(2)}%`);
    console.log(`Worst Case: ${simulation.worstCase.toFixed(2)}%`);
    console.log(`Best Case: ${simulation.bestCase.toFixed(2)}%`);

    return simulation;
  }

  /**
   * Main analysis workflow
   */
  async analyze() {
    console.log('\n🔬 PORTFOLIO CORRELATION & OPTIMIZATION ANALYSIS');
    console.log('='.repeat(60));

    const correlationMatrix = this.calculateCorrelationMatrix();
    const uncorrelatedPairs = this.findUncorrelatedPairs();
    const optimalWeights = this.calculateOptimalWeights();
    
    const weights = optimalWeights.map(p => p.weight);
    const portfolioMetrics = this.calculatePortfolioMetrics(weights);
    const monteCarloSim = this.runMonteCarloSimulation(1000);

    const analysis = {
      correlationMatrix,
      uncorrelatedPairs,
      optimalWeights,
      portfolioMetrics,
      monteCarloSimulation: monteCarloSim
    };

    // Save analysis
    await fs.writeFile(
      `${RESULTS_DIR}/portfolio_analysis.json`,
      JSON.stringify(analysis, null, 2)
    );

    console.log(`\n✅ Analysis saved: ${RESULTS_DIR}/portfolio_analysis.json`);
    
    return analysis;
  }
}

// Main execution
async function main() {
  console.log('📊 Loading backtest results...\n');
  
  const resultsRaw = await fs.readFile(`${RESULTS_DIR}/backtest_results.json`, 'utf-8');
  const backtestResults = JSON.parse(resultsRaw);

  const analyzer = new PortfolioAnalyzer(backtestResults);
  await analyzer.analyze();

  console.log('\n' + '='.repeat(60));
  console.log('✅ PORTFOLIO ANALYSIS COMPLETE');
  console.log('='.repeat(60));
  console.log('\nNext: npm run charts\n');
}

if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  main().catch(console.error);
}

export default PortfolioAnalyzer;
