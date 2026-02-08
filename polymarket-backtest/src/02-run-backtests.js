/**
 * BACKTESTING ENGINE - Run all strategies on historical data
 * 
 * Calculates:
 * - Total return, Win rate, Profit factor
 * - Max drawdown, Sharpe ratio, Sortino ratio, Calmar ratio
 * - Trade logs with full P&L accounting
 */

import { promises as fs } from 'fs';
import { TradingStrategies } from './strategies.js';

const PROCESSED_DIR = './data/processed';
const RESULTS_DIR = './results';
const INITIAL_CAPITAL = 10000;  // $10,000 starting capital
const POSITION_SIZE = 0.10;  // 10% of capital per trade
const FEE_RATE = 0.02;  // 2% fees (1% entry + 1% exit)

class BacktestEngine {
  constructor(priceData) {
    this.priceData = priceData;
    this.results = new Map();
  }

  async initialize() {
    await fs.mkdir(RESULTS_DIR, { recursive: true });
  }

  /**
   * Run backtest for a single strategy on all markets
   */
  async runStrategy(strategyName, strategyFn) {
    console.log(`\n📊 Backtesting: ${strategyName}`);
    console.log('='.repeat(60));

    const trades = [];
    const equityCurve = [{ date: '2024-01-01', equity: INITIAL_CAPITAL }];
    let capital = INITIAL_CAPITAL;
    let openPositions = [];

    // Process each market
    for (const marketData of this.priceData) {
      const priceHistory = marketData.priceHistory;
      
      // Walk through price history
      for (let i = 0; i < priceHistory.length; i++) {
        const current = priceHistory[i];
        
        // Check for exit signals on open positions
        openPositions = openPositions.filter(pos => {
          const exitCheck = this.checkExit(pos, current, i);
          
          if (exitCheck.shouldExit) {
            const trade = this.closePosition(pos, exitCheck.exitPrice, current.date, exitCheck.reason);
            trades.push(trade);
            capital += trade.pnl;
            
            equityCurve.push({
              date: current.date,
              equity: capital
            });
            
            return false;  // Remove from open positions
          }
          
          return true;  // Keep position open
        });
        
        // Check for entry signals (only if we have capital and not too many open positions)
        if (openPositions.length < 5 && capital > INITIAL_CAPITAL * 0.20) {
          const signal = strategyFn.call(TradingStrategies, marketData, i);
          
          if (signal) {
            const positionSize = capital * POSITION_SIZE;
            const position = this.openPosition(signal, current, marketData.market, positionSize);
            
            if (position) {
              openPositions.push(position);
              capital -= position.capitalUsed;
            }
          }
        }
      }
      
      // Close any remaining positions at market end
      for (const pos of openPositions) {
        const finalPrice = priceHistory[priceHistory.length - 1];
        const trade = this.closePosition(pos, finalPrice.price, finalPrice.date, 'market-close');
        trades.push(trade);
        capital += trade.pnl;
      }
      openPositions = [];
    }

    // Calculate performance metrics
    const metrics = this.calculateMetrics(trades, equityCurve, INITIAL_CAPITAL);

    console.log(`\n✅ ${strategyName} Results:`);
    console.log(`   Trades: ${trades.length}`);
    console.log(`   Win Rate: ${metrics.winRate.toFixed(2)}%`);
    console.log(`   Total Return: ${metrics.totalReturn.toFixed(2)}%`);
    console.log(`   Sharpe Ratio: ${metrics.sharpeRatio.toFixed(3)}`);
    console.log(`   Max Drawdown: ${metrics.maxDrawdown.toFixed(2)}%`);

    return {
      strategy: strategyName,
      trades,
      equityCurve,
      metrics,
      finalCapital: capital
    };
  }

  /**
   * Open a new position
   */
  openPosition(signal, currentPrice, market, positionSize) {
    const entryPrice = currentPrice.price;
    const fees = positionSize * (FEE_RATE / 2);  // Entry fee
    const shares = (positionSize - fees) / entryPrice;

    return {
      ...signal,
      market: market.slug,
      marketQuestion: market.question,
      entryDate: currentPrice.date,
      entryTimestamp: currentPrice.timestamp,
      entryPrice: entryPrice,
      shares: shares,
      capitalUsed: positionSize,
      fees: fees
    };
  }

  /**
   * Check if position should be closed
   */
  checkExit(position, currentPrice, currentIdx) {
    const current = currentPrice.price;
    const entryTime = new Date(position.entryDate).getTime();
    const currentTime = new Date(currentPrice.date).getTime();
    const hoursHeld = (currentTime - entryTime) / (1000 * 60 * 60);

    // Check stop loss
    if (position.signal === 'BUY' && current <= position.stopLoss) {
      return { shouldExit: true, exitPrice: current, reason: 'stop-loss' };
    }
    if (position.signal === 'SELL' && current >= position.stopLoss) {
      return { shouldExit: true, exitPrice: current, reason: 'stop-loss' };
    }

    // Check profit target
    if (position.signal === 'BUY' && current >= position.target) {
      return { shouldExit: true, exitPrice: current, reason: 'target' };
    }
    if (position.signal === 'SELL' && current <= position.target) {
      return { shouldExit: true, exitPrice: current, reason: 'target' };
    }

    // Check time-based exit
    const maxHours = position.maxHoldHours || (position.maxHoldDays * 24) || (7 * 24);
    if (hoursHeld >= maxHours) {
      return { shouldExit: true, exitPrice: current, reason: 'time-limit' };
    }

    return { shouldExit: false };
  }

  /**
   * Close a position and calculate P&L
   */
  closePosition(position, exitPrice, exitDate, exitReason) {
    const exitValue = position.shares * exitPrice;
    const exitFees = exitValue * (FEE_RATE / 2);  // Exit fee
    const netExitValue = exitValue - exitFees;
    
    const pnl = netExitValue - position.capitalUsed;
    const pnlPercent = (pnl / position.capitalUsed) * 100;
    
    const entryTime = new Date(position.entryDate).getTime();
    const exitTime = new Date(exitDate).getTime();
    const durationHours = (exitTime - entryTime) / (1000 * 60 * 60);

    return {
      strategy: position.strategy,
      market: position.market,
      signal: position.signal,
      entryDate: position.entryDate,
      exitDate: exitDate,
      entryPrice: position.entryPrice,
      exitPrice: exitPrice,
      shares: position.shares,
      capitalUsed: position.capitalUsed,
      pnl: pnl,
      pnlPercent: pnlPercent,
      fees: position.fees + exitFees,
      durationHours: durationHours,
      exitReason: exitReason,
      winner: pnl > 0
    };
  }

  /**
   * Calculate comprehensive performance metrics
   */
  calculateMetrics(trades, equityCurve, initialCapital) {
    if (trades.length === 0) {
      return this.emptyMetrics();
    }

    // Basic metrics
    const winners = trades.filter(t => t.winner);
    const losers = trades.filter(t => !t.winner);
    const winRate = (winners.length / trades.length) * 100;
    
    const totalGains = winners.reduce((sum, t) => sum + t.pnl, 0);
    const totalLosses = Math.abs(losers.reduce((sum, t) => sum + t.pnl, 0));
    const profitFactor = totalLosses > 0 ? totalGains / totalLosses : totalGains > 0 ? Infinity : 0;
    
    const finalEquity = equityCurve[equityCurve.length - 1].equity;
    const totalReturn = ((finalEquity - initialCapital) / initialCapital) * 100;
    
    const avgTradeDuration = trades.reduce((sum, t) => sum + t.durationHours, 0) / trades.length;

    // Calculate returns for risk metrics
    const returns = [];
    for (let i = 1; i < equityCurve.length; i++) {
      const ret = (equityCurve[i].equity - equityCurve[i-1].equity) / equityCurve[i-1].equity;
      returns.push(ret);
    }

    // Sharpe Ratio (annualized)
    const avgReturn = returns.reduce((a, b) => a + b, 0) / returns.length;
    const variance = returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length;
    const stdDev = Math.sqrt(variance);
    const sharpeRatio = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0;  // Annualized

    // Sortino Ratio (downside deviation only)
    const negativeReturns = returns.filter(r => r < 0);
    const downsideVariance = negativeReturns.length > 0
      ? negativeReturns.reduce((sum, r) => sum + Math.pow(r, 2), 0) / negativeReturns.length
      : 0;
    const downsideDeviation = Math.sqrt(downsideVariance);
    const sortinoRatio = downsideDeviation > 0 ? (avgReturn / downsideDeviation) * Math.sqrt(252) : 0;

    // Max Drawdown
    let peak = equityCurve[0].equity;
    let maxDrawdown = 0;
    
    for (const point of equityCurve) {
      if (point.equity > peak) {
        peak = point.equity;
      }
      const drawdown = ((peak - point.equity) / peak) * 100;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }

    // Calmar Ratio (Return / Max Drawdown)
    const calmarRatio = maxDrawdown > 0 ? totalReturn / maxDrawdown : 0;

    return {
      totalTrades: trades.length,
      winners: winners.length,
      losers: losers.length,
      winRate: winRate,
      totalReturn: totalReturn,
      profitFactor: profitFactor,
      avgTradeDuration: avgTradeDuration,
      sharpeRatio: sharpeRatio,
      sortinoRatio: sortinoRatio,
      calmarRatio: calmarRatio,
      maxDrawdown: maxDrawdown,
      finalEquity: finalEquity
    };
  }

  emptyMetrics() {
    return {
      totalTrades: 0,
      winners: 0,
      losers: 0,
      winRate: 0,
      totalReturn: 0,
      profitFactor: 0,
      avgTradeDuration: 0,
      sharpeRatio: 0,
      sortinoRatio: 0,
      calmarRatio: 0,
      maxDrawdown: 0,
      finalEquity: INITIAL_CAPITAL
    };
  }

  /**
   * Run all strategies
   */
  async runAllStrategies() {
    console.log('\n🚀 Starting Backtest - All 6 Strategies');
    console.log('='.repeat(60));
    console.log(`Date Range: Jan 2024 - Feb 2026`);
    console.log(`Initial Capital: $${INITIAL_CAPITAL.toLocaleString()}`);
    console.log(`Position Size: ${POSITION_SIZE * 100}% per trade`);
    console.log(`Fees: ${FEE_RATE * 100}%`);

    const strategies = TradingStrategies.getAllStrategies();
    const allResults = [];
    const allTrades = [];

    for (const { name, fn } of strategies) {
      const result = await this.runStrategy(name, fn);
      allResults.push(result);
      
      // Add to master trade log
      allTrades.push(...result.trades);
    }

    // Save results
    await this.saveResults(allResults, allTrades);

    return allResults;
  }

  /**
   * Save backtest results
   */
  async saveResults(allResults, allTrades) {
    // Save detailed results
    await fs.writeFile(
      `${RESULTS_DIR}/backtest_results.json`,
      JSON.stringify(allResults, null, 2)
    );

    // Save trade log CSV
    const csvRows = [
      'Strategy,Market,Signal,Entry Date,Exit Date,Entry Price,Exit Price,P&L,P&L %,Duration (hrs),Exit Reason,Winner'
    ];

    for (const trade of allTrades) {
      csvRows.push([
        trade.strategy,
        `"${trade.market}"`,
        trade.signal,
        trade.entryDate,
        trade.exitDate,
        trade.entryPrice.toFixed(4),
        trade.exitPrice.toFixed(4),
        trade.pnl.toFixed(2),
        trade.pnlPercent.toFixed(2),
        trade.durationHours.toFixed(1),
        trade.exitReason,
        trade.winner ? 'Yes' : 'No'
      ].join(','));
    }

    await fs.writeFile(
      `${RESULTS_DIR}/backtest_results.csv`,
      csvRows.join('\n')
    );

    console.log(`\n✅ Results saved:`);
    console.log(`   - ${RESULTS_DIR}/backtest_results.json`);
    console.log(`   - ${RESULTS_DIR}/backtest_results.csv`);
  }
}

// Main execution
async function main() {
  console.log('📊 Loading historical price data...\n');
  
  const priceDataRaw = await fs.readFile(`${PROCESSED_DIR}/price_data.json`, 'utf-8');
  const priceData = JSON.parse(priceDataRaw);

  console.log(`✅ Loaded ${priceData.length} markets with price history\n`);

  const engine = new BacktestEngine(priceData);
  await engine.initialize();
  
  const results = await engine.runAllStrategies();

  console.log('\n' + '='.repeat(60));
  console.log('✅ BACKTEST COMPLETE');
  console.log('='.repeat(60));

  // Print summary table
  console.log('\n📊 PERFORMANCE SUMMARY:\n');
  console.log('Strategy'.padEnd(30) + 'Return %'.padEnd(12) + 'Sharpe'.padEnd(10) + 'Max DD %'.padEnd(12) + 'Trades');
  console.log('-'.repeat(75));
  
  for (const result of results) {
    const m = result.metrics;
    console.log(
      result.strategy.padEnd(30) +
      m.totalReturn.toFixed(2).padStart(8).padEnd(12) +
      m.sharpeRatio.toFixed(3).padStart(6).padEnd(10) +
      m.maxDrawdown.toFixed(2).padStart(8).padEnd(12) +
      m.totalTrades.toString()
    );
  }

  console.log('\nNext: npm run analyze\n');
}

if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  main().catch(console.error);
}

export default BacktestEngine;
