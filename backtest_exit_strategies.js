#!/usr/bin/env node
/**
 * Exit Strategy Backtest Comparison
 * Tests 5 different exit strategies on the same synthetic market data
 * Compares: profit factor, max drawdown, win rate, expectancy
 */

const fs = require('fs');

// ============================================================================
// SYNTHETIC DATA GENERATION
// ============================================================================

function generateSyntheticMarkets(numMarkets = 15, daysHistory = 60) {
  console.log(`\n${'='.repeat(70)}`);
  console.log('GENERATING SYNTHETIC MARKET DATA');
  console.log(`${'='.repeat(70)}`);
  console.log(`Markets: ${numMarkets}`);
  console.log(`History: ${daysHistory} days`);
  
  const markets = [];
  const questions = [
    "Bitcoin reaches $100,000",
    "Ethereum ETF approved",
    "Fed cuts rates in March",
    "Lakers win championship",
    "S&P 500 above 6000",
    "Dogecoin reaches $1",
    "Tesla reaches $500/share",
    "New COVID variant",
    "Major AI breakthrough",
    "SpaceX lands on Mars",
    "Apple releases AR glasses",
    "Bitcoin dominance below 40%",
    "Recession declared in 2026",
    "Trump wins election",
    "New GTA game releases"
  ];
  
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - daysHistory);
  
  for (let m = 0; m < numMarkets; m++) {
    const marketId = `market_${m + 1}`;
    const question = questions[m];
    const daysToExpiry = 90 + Math.random() * 180;
    const endDate = new Date();
    endDate.setDate(endDate.getDate() + daysToExpiry);
    
    // Generate price path with occasional hype spikes
    const snapshots = [];
    let currentPrice = 0.3 + Math.random() * 0.4; // Start 30-70%
    let baseVolume = 5000 + Math.random() * 45000;
    
    for (let day = 0; day < daysHistory; day++) {
      const timestamp = new Date(startDate);
      timestamp.setDate(timestamp.getDate() + day);
      
      // Random walk with drift
      const drift = (Math.random() - 0.5) * 0.02;
      currentPrice += drift;
      currentPrice = Math.max(0.05, Math.min(0.95, currentPrice));
      
      // Occasional hype spikes (15% chance)
      const hasHypeSpike = Math.random() < 0.15;
      let volume = baseVolume * (0.8 + Math.random() * 0.4);
      let roc = drift * 100;
      
      if (hasHypeSpike) {
        const spikeSize = 1.5 + Math.random() * 3.5; // 1.5x to 5x volume
        volume *= spikeSize;
        const priceJump = (Math.random() - 0.3) * 0.08; // -3% to +8%
        currentPrice += priceJump;
        currentPrice = Math.max(0.05, Math.min(0.95, currentPrice));
        roc = priceJump * 100;
      }
      
      const liquidity = baseVolume * 0.8;
      const spread = 0.01 + Math.random() * 0.03;
      
      snapshots.push({
        timestamp: timestamp.toISOString(),
        price: currentPrice,
        volume_24h: volume,
        liquidity: liquidity,
        spread: spread,
        hasHypeSpike: hasHypeSpike,
        hoursToExpiry: (endDate - timestamp) / (1000 * 60 * 60)
      });
    }
    
    markets.push({
      marketId,
      question,
      endDate: endDate.toISOString(),
      snapshots
    });
  }
  
  console.log(`✓ Generated ${markets.length} markets with ${markets[0].snapshots.length} snapshots each`);
  return markets;
}

// ============================================================================
// SIGNAL GENERATOR
// ============================================================================

function calculateSignals(snapshots, currentIdx) {
  if (currentIdx < 4) return null; // Need history
  
  const current = snapshots[currentIdx];
  const lookback = snapshots.slice(Math.max(0, currentIdx - 24), currentIdx);
  
  if (lookback.length < 4) return null;
  
  // RVR (Relative Volume Ratio)
  const avgVolume = lookback.reduce((sum, s) => sum + s.volume_24h, 0) / lookback.length;
  const rvr = current.volume_24h / avgVolume;
  
  // ROC (Rate of Change) - last 6 hours
  const lookbackIdx = Math.max(0, currentIdx - 6);
  const pastPrice = snapshots[lookbackIdx].price;
  const roc = ((current.price - pastPrice) / pastPrice) * 100;
  
  // Signal strength classification
  let strong = 0, moderate = 0;
  
  if (rvr >= 3.0) strong++;
  else if (rvr >= 2.0) moderate++;
  
  if (Math.abs(roc) >= 15) strong++;
  else if (Math.abs(roc) >= 10) moderate++;
  
  let signalStrength = 'WEAK';
  let signalCount = strong + moderate;
  
  if (strong >= 2) signalStrength = 'STRONG';
  else if (strong >= 1 && moderate >= 1) signalStrength = 'MODERATE';
  else if (moderate >= 2) signalStrength = 'MODERATE';
  
  // Entry filters
  const shouldEnter = 
    signalCount >= 2 &&
    current.hoursToExpiry >= 48 &&
    current.liquidity >= 5000 &&
    current.spread <= 0.05 &&
    (signalStrength === 'STRONG' || signalStrength === 'MODERATE');
  
  return {
    rvr,
    roc,
    signalStrength,
    signalCount,
    shouldEnter
  };
}

// ============================================================================
// EXIT STRATEGIES
// ============================================================================

class ExitStrategy {
  constructor(name, config) {
    this.name = name;
    this.config = config;
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime, snapshots, currentIdx) {
    throw new Error('Must implement checkExit');
  }
}

// 1. BASELINE: Current strategy (12% stop, tiered profits)
class BaselineStrategy extends ExitStrategy {
  constructor() {
    super('Baseline (Current)', {
      stopLoss: 0.12,
      tpLevels: [0.08, 0.15, 0.25],
      tpAllocations: [0.25, 0.50, 0.25],
      timeDecay: [[3, 0.05], [7, 0.08]]
    });
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime) {
    const priceChange = (currentPrice - trade.entryPrice) / trade.entryPrice;
    const holdingHours = (new Date(currentTimestamp) - new Date(trade.entryTime)) / (1000 * 60 * 60);
    const holdingDays = holdingHours / 24;
    
    // Stop loss
    if (priceChange <= -this.config.stopLoss) {
      return { shouldExit: true, reason: 'STOP_LOSS', allocation: 1.0 };
    }
    
    // Take profit levels
    for (let i = 0; i < this.config.tpLevels.length; i++) {
      if (priceChange >= this.config.tpLevels[i]) {
        return { 
          shouldExit: true, 
          reason: `TP${i+1}`, 
          allocation: this.config.tpAllocations[i] 
        };
      }
    }
    
    // Time decay
    if (holdingDays > 7 && priceChange < 0.08) {
      return { shouldExit: true, reason: 'TIME_DECAY_7D', allocation: 1.0 };
    }
    if (holdingDays > 3 && priceChange < 0.05) {
      return { shouldExit: true, reason: 'TIME_DECAY_3D', allocation: 0.5 };
    }
    
    // Market expiry (7 days before)
    const hoursToExpiry = (new Date(marketEndTime) - new Date(currentTimestamp)) / (1000 * 60 * 60);
    if (hoursToExpiry < 168) {
      return { shouldExit: true, reason: 'MARKET_EXPIRY', allocation: 1.0 };
    }
    
    return { shouldExit: false };
  }
}

// 2. TRAILING STOP: Move stop to breakeven at +10%, then trail by 5%
class TrailingStopStrategy extends ExitStrategy {
  constructor() {
    super('Trailing Stop', {
      initialStop: 0.12,
      breakevenTrigger: 0.10,
      trailDistance: 0.05
    });
    this.highestPrice = new Map(); // Track highest price per trade
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime) {
    if (!this.highestPrice.has(trade.id)) {
      this.highestPrice.set(trade.id, trade.entryPrice);
    }
    
    const highPrice = Math.max(this.highestPrice.get(trade.id), currentPrice);
    this.highestPrice.set(trade.id, highPrice);
    
    const priceChange = (currentPrice - trade.entryPrice) / trade.entryPrice;
    const highChange = (highPrice - trade.entryPrice) / trade.entryPrice;
    
    // If we've hit +10%, move stop to breakeven
    let stopLevel = -this.config.initialStop;
    if (highChange >= this.config.breakevenTrigger) {
      // Trail by 5% from highest price
      stopLevel = (highPrice - trade.entryPrice) / trade.entryPrice - this.config.trailDistance;
    }
    
    if (priceChange <= stopLevel) {
      return { shouldExit: true, reason: 'TRAILING_STOP', allocation: 1.0 };
    }
    
    // Still use market expiry
    const hoursToExpiry = (new Date(marketEndTime) - new Date(currentTimestamp)) / (1000 * 60 * 60);
    if (hoursToExpiry < 168) {
      return { shouldExit: true, reason: 'MARKET_EXPIRY', allocation: 1.0 };
    }
    
    return { shouldExit: false };
  }
}

// 3. TIME-BASED: Close at 80% of resolution time regardless of P/L
class TimeBasedStrategy extends ExitStrategy {
  constructor() {
    super('Time-Based Exit', {
      exitAtPctOfTime: 0.80,
      emergencyStop: 0.20 // Still have a -20% emergency stop
    });
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime) {
    const priceChange = (currentPrice - trade.entryPrice) / trade.entryPrice;
    
    // Emergency stop
    if (priceChange <= -this.config.emergencyStop) {
      return { shouldExit: true, reason: 'EMERGENCY_STOP', allocation: 1.0 };
    }
    
    // Calculate time elapsed
    const totalTime = new Date(marketEndTime) - new Date(trade.entryTime);
    const elapsed = new Date(currentTimestamp) - new Date(trade.entryTime);
    const pctElapsed = elapsed / totalTime;
    
    if (pctElapsed >= this.config.exitAtPctOfTime) {
      return { shouldExit: true, reason: 'TIME_TARGET', allocation: 1.0 };
    }
    
    return { shouldExit: false };
  }
}

// 4. VOLATILITY-BASED: Tighter stops on low-volume markets
class VolatilityBasedStrategy extends ExitStrategy {
  constructor() {
    super('Volatility-Based', {
      baseStop: 0.12,
      lowVolumeThreshold: 10000,
      tightStop: 0.08,
      tpLevels: [0.08, 0.15, 0.25],
      tpAllocations: [0.25, 0.50, 0.25]
    });
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime, snapshots, currentIdx) {
    const priceChange = (currentPrice - trade.entryPrice) / trade.entryPrice;
    
    // Determine stop based on recent volume
    const recentSnaps = snapshots.slice(Math.max(0, currentIdx - 4), currentIdx + 1);
    const avgVolume = recentSnaps.reduce((sum, s) => sum + s.volume_24h, 0) / recentSnaps.length;
    
    const stopLoss = avgVolume < this.config.lowVolumeThreshold 
      ? this.config.tightStop 
      : this.config.baseStop;
    
    if (priceChange <= -stopLoss) {
      return { 
        shouldExit: true, 
        reason: avgVolume < this.config.lowVolumeThreshold ? 'LOW_VOL_STOP' : 'STOP_LOSS',
        allocation: 1.0 
      };
    }
    
    // Take profits
    for (let i = 0; i < this.config.tpLevels.length; i++) {
      if (priceChange >= this.config.tpLevels[i]) {
        return { 
          shouldExit: true, 
          reason: `TP${i+1}`, 
          allocation: this.config.tpAllocations[i] 
        };
      }
    }
    
    // Market expiry
    const hoursToExpiry = (new Date(marketEndTime) - new Date(currentTimestamp)) / (1000 * 60 * 60);
    if (hoursToExpiry < 168) {
      return { shouldExit: true, reason: 'MARKET_EXPIRY', allocation: 1.0 };
    }
    
    return { shouldExit: false };
  }
}

// 5. AGGRESSIVE SCALE OUT: 50% at +15%, 50% at +25%
class AggressiveScaleStrategy extends ExitStrategy {
  constructor() {
    super('Aggressive Scale', {
      stopLoss: 0.12,
      tpLevels: [0.15, 0.25],
      tpAllocations: [0.50, 0.50]
    });
  }
  
  checkExit(trade, currentPrice, currentTimestamp, marketEndTime) {
    const priceChange = (currentPrice - trade.entryPrice) / trade.entryPrice;
    
    // Stop loss
    if (priceChange <= -this.config.stopLoss) {
      return { shouldExit: true, reason: 'STOP_LOSS', allocation: 1.0 };
    }
    
    // Take profits (more aggressive)
    for (let i = 0; i < this.config.tpLevels.length; i++) {
      if (priceChange >= this.config.tpLevels[i]) {
        return { 
          shouldExit: true, 
          reason: `TP${i+1}`, 
          allocation: this.config.tpAllocations[i] 
        };
      }
    }
    
    // Market expiry
    const hoursToExpiry = (new Date(marketEndTime) - new Date(currentTimestamp)) / (1000 * 60 * 60);
    if (hoursToExpiry < 168) {
      return { shouldExit: true, reason: 'MARKET_EXPIRY', allocation: 1.0 };
    }
    
    return { shouldExit: false };
  }
}

// ============================================================================
// BACKTEST ENGINE
// ============================================================================

class BacktestEngine {
  constructor(initialCapital = 10000) {
    this.initialCapital = initialCapital;
    this.capital = initialCapital;
    this.trades = [];
    this.openTrades = [];
    this.equityCurve = [];
    
    this.positionSizes = {
      'STRONG': 0.04,
      'MODERATE': 0.02,
      'WEAK': 0.01
    };
    
    this.slippageEntry = 0.01;
    this.slippageExit = 0.015;
    this.feeRate = 0.02;
  }
  
  runBacktest(markets, exitStrategy) {
    console.log(`\n${'='.repeat(70)}`);
    console.log(`BACKTESTING: ${exitStrategy.name}`);
    console.log(`${'='.repeat(70)}`);
    
    this.trades = [];
    this.openTrades = [];
    this.capital = this.initialCapital;
    this.equityCurve = [];
    let tradeIdCounter = 0;
    
    // Simulate trading across all markets
    for (const market of markets) {
      for (let i = 0; i < market.snapshots.length; i++) {
        const snapshot = market.snapshots[i];
        const signals = calculateSignals(market.snapshots, i);
        
        if (!signals) continue;
        
        // Check exits for open trades in this market
        this.openTrades = this.openTrades.map(trade => {
          if (trade.marketId !== market.marketId) return trade;
          
          const exitCheck = exitStrategy.checkExit(
            trade,
            snapshot.price,
            snapshot.timestamp,
            market.endDate,
            market.snapshots,
            i
          );
          
          if (exitCheck.shouldExit) {
            // Close position (partial or full)
            const closeSize = trade.remainingSize * exitCheck.allocation;
            const grossPnl = (snapshot.price - trade.entryPrice) * closeSize;
            const slippageCost = closeSize * (this.slippageEntry + this.slippageExit);
            const feeCost = Math.max(0, grossPnl) * this.feeRate;
            const netPnl = grossPnl - slippageCost - feeCost;
            
            this.trades.push({
              ...trade,
              exitTime: snapshot.timestamp,
              exitPrice: snapshot.price,
              exitReason: exitCheck.reason,
              sizeExited: closeSize,
              grossPnl: grossPnl,
              netPnl: netPnl,
              returnPct: (netPnl / closeSize) * 100,
              holdingHours: (new Date(snapshot.timestamp) - new Date(trade.entryTime)) / (1000 * 60 * 60)
            });
            
            this.capital += netPnl;
            trade.remainingSize -= closeSize;
            
            if (trade.remainingSize < 0.01) {
              return null; // Fully closed
            }
          }
          
          return trade;
        }).filter(t => t !== null);
        
        // Check for new entry signals
        if (signals.shouldEnter) {
          const posSize = this.capital * this.positionSizes[signals.signalStrength];
          
          if (posSize >= 100) { // Minimum $100 position
            const trade = {
              id: `trade_${++tradeIdCounter}`,
              marketId: market.marketId,
              question: market.question,
              entryTime: snapshot.timestamp,
              entryPrice: snapshot.price,
              positionSize: posSize,
              remainingSize: posSize,
              signalStrength: signals.signalStrength,
              rvr: signals.rvr,
              roc: signals.roc
            };
            
            this.openTrades.push(trade);
          }
        }
        
        // Track equity
        const openPnl = this.openTrades.reduce((sum, t) => {
          const unrealizedPnl = (snapshot.price - t.entryPrice) * t.remainingSize;
          return sum + unrealizedPnl;
        }, 0);
        
        this.equityCurve.push({
          timestamp: snapshot.timestamp,
          capital: this.capital + openPnl,
          openTrades: this.openTrades.length
        });
      }
    }
    
    // Close remaining positions
    for (const trade of this.openTrades) {
      const market = markets.find(m => m.marketId === trade.marketId);
      const lastSnapshot = market.snapshots[market.snapshots.length - 1];
      
      const grossPnl = (lastSnapshot.price - trade.entryPrice) * trade.remainingSize;
      const slippageCost = trade.remainingSize * (this.slippageEntry + this.slippageExit);
      const feeCost = Math.max(0, grossPnl) * this.feeRate;
      const netPnl = grossPnl - slippageCost - feeCost;
      
      this.trades.push({
        ...trade,
        exitTime: lastSnapshot.timestamp,
        exitPrice: lastSnapshot.price,
        exitReason: 'END_OF_BACKTEST',
        sizeExited: trade.remainingSize,
        grossPnl: grossPnl,
        netPnl: netPnl,
        returnPct: (netPnl / trade.remainingSize) * 100,
        holdingHours: (new Date(lastSnapshot.timestamp) - new Date(trade.entryTime)) / (1000 * 60 * 60)
      });
    }
    
    console.log(`✓ Completed: ${this.trades.length} trades executed`);
    
    return this.calculateMetrics();
  }
  
  calculateMetrics() {
    if (this.trades.length === 0) {
      return null;
    }
    
    const winners = this.trades.filter(t => t.netPnl > 0);
    const losers = this.trades.filter(t => t.netPnl < 0);
    
    const totalPnl = this.trades.reduce((sum, t) => sum + t.netPnl, 0);
    const winRate = (winners.length / this.trades.length) * 100;
    
    const avgWin = winners.length > 0 
      ? winners.reduce((sum, t) => sum + t.netPnl, 0) / winners.length 
      : 0;
    const avgLoss = losers.length > 0 
      ? losers.reduce((sum, t) => sum + t.netPnl, 0) / losers.length 
      : 0;
    
    const totalWins = winners.reduce((sum, t) => sum + t.netPnl, 0);
    const totalLosses = Math.abs(losers.reduce((sum, t) => sum + t.netPnl, 0));
    const profitFactor = totalLosses > 0 ? totalWins / totalLosses : 0;
    
    const expectancy = (winRate/100 * avgWin) + ((1 - winRate/100) * avgLoss);
    
    // Calculate max drawdown
    let peak = this.initialCapital;
    let maxDrawdown = 0;
    
    for (const point of this.equityCurve) {
      if (point.capital > peak) peak = point.capital;
      const drawdown = ((point.capital - peak) / peak) * 100;
      if (drawdown < maxDrawdown) maxDrawdown = drawdown;
    }
    
    // Risk-adjusted returns
    const returns = this.trades.map(t => t.returnPct);
    const avgReturn = returns.reduce((sum, r) => sum + r, 0) / returns.length;
    const stdDev = Math.sqrt(
      returns.reduce((sum, r) => sum + Math.pow(r - avgReturn, 2), 0) / returns.length
    );
    
    const sharpeRatio = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(252) : 0;
    
    const downside = returns.filter(r => r < 0);
    const downsideStd = downside.length > 0
      ? Math.sqrt(downside.reduce((sum, r) => sum + Math.pow(r, 2), 0) / downside.length)
      : 1;
    const sortinoRatio = (avgReturn / downsideStd) * Math.sqrt(252);
    
    const avgHolding = this.trades.reduce((sum, t) => sum + t.holdingHours, 0) / this.trades.length;
    
    return {
      totalTrades: this.trades.length,
      winningTrades: winners.length,
      losingTrades: losers.length,
      winRate: winRate,
      
      totalReturnPct: (totalPnl / this.initialCapital) * 100,
      totalReturnUsd: totalPnl,
      
      avgWinUsd: avgWin,
      avgLossUsd: avgLoss,
      
      profitFactor: profitFactor,
      expectancy: expectancy,
      
      sharpeRatio: sharpeRatio,
      sortinoRatio: sortinoRatio,
      maxDrawdownPct: Math.abs(maxDrawdown),
      
      avgHoldingHours: avgHolding,
      
      bestTrade: Math.max(...returns),
      worstTrade: Math.min(...returns)
    };
  }
}

// ============================================================================
// COMPARISON & REPORTING
// ============================================================================

function compareStrategies(markets) {
  const strategies = [
    new BaselineStrategy(),
    new TrailingStopStrategy(),
    new TimeBasedStrategy(),
    new VolatilityBasedStrategy(),
    new AggressiveScaleStrategy()
  ];
  
  const results = [];
  
  for (const strategy of strategies) {
    const engine = new BacktestEngine(10000);
    const metrics = engine.runBacktest(markets, strategy);
    
    if (metrics) {
      results.push({
        strategy: strategy.name,
        config: strategy.config,
        metrics: metrics
      });
      
      console.log(`\nKEY METRICS:`);
      console.log(`  Total Return: ${metrics.totalReturnPct.toFixed(2)}%`);
      console.log(`  Win Rate: ${metrics.winRate.toFixed(1)}%`);
      console.log(`  Profit Factor: ${metrics.profitFactor.toFixed(2)}`);
      console.log(`  Max Drawdown: ${metrics.maxDrawdownPct.toFixed(1)}%`);
      console.log(`  Sharpe Ratio: ${metrics.sharpeRatio.toFixed(2)}`);
      console.log(`  Expectancy: $${metrics.expectancy.toFixed(2)}`);
    }
  }
  
  return results;
}

function generateMarkdownReport(results) {
  const timestamp = new Date().toISOString().split('T')[0];
  
  let md = `# Exit Strategy Backtest Comparison

**Generated:** ${timestamp}  
**Initial Capital:** $10,000  
**Test Period:** 60 days synthetic data, 15 markets  
**Objective:** Maximize risk-adjusted returns (Profit Factor / Max Drawdown)

---

## Executive Summary

Tested 5 exit strategies on identical market data to determine which approach maximizes risk-adjusted returns.

### Strategy Variants

1. **Baseline (Current)**: 12% stop-loss, tiered take-profits at 8%/15%/25% (25%/50%/25% allocation)
2. **Trailing Stop**: Move stop to breakeven at +10%, then trail by 5%
3. **Time-Based**: Exit at 80% of time to resolution regardless of P/L
4. **Volatility-Based**: Tighter 8% stops on low-volume (<$10k) markets, otherwise 12%
5. **Aggressive Scale**: Take profits at 15% (50%) and 25% (50%)

---

## Performance Comparison

### Summary Table

| Strategy | Return % | Profit Factor | Max DD % | Sharpe | Win Rate | Trades |
|----------|----------|---------------|----------|--------|----------|--------|
`;

  // Sort by profit factor / max drawdown ratio
  const sorted = [...results].sort((a, b) => {
    const ratioA = a.metrics.profitFactor / Math.max(a.metrics.maxDrawdownPct, 1);
    const ratioB = b.metrics.profitFactor / Math.max(b.metrics.maxDrawdownPct, 1);
    return ratioB - ratioA;
  });

  for (const result of sorted) {
    const m = result.metrics;
    md += `| ${result.strategy} | ${m.totalReturnPct.toFixed(1)}% | ${m.profitFactor.toFixed(2)} | ${m.maxDrawdownPct.toFixed(1)}% | ${m.sharpeRatio.toFixed(2)} | ${m.winRate.toFixed(1)}% | ${m.totalTrades} |\n`;
  }

  md += `\n### Risk-Adjusted Score

**Formula:** Profit Factor / Max Drawdown %  
*(Higher is better - rewards high profits with controlled risk)*

| Strategy | Score | Rank |
|----------|-------|------|
`;

  sorted.forEach((result, i) => {
    const score = result.metrics.profitFactor / Math.max(result.metrics.maxDrawdownPct, 1);
    md += `| ${result.strategy} | ${score.toFixed(3)} | ${i + 1} |\n`;
  });

  md += `\n---

## Detailed Analysis

`;

  for (const result of sorted) {
    const m = result.metrics;
    
    md += `### ${result.strategy}

**Configuration:**
\`\`\`json
${JSON.stringify(result.config, null, 2)}
\`\`\`

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Total Return | ${m.totalReturnPct.toFixed(2)}% ($${m.totalReturnUsd.toFixed(2)}) |
| Win Rate | ${m.winRate.toFixed(1)}% (${m.winningTrades}W / ${m.losingTrades}L) |
| Profit Factor | ${m.profitFactor.toFixed(2)} |
| Sharpe Ratio | ${m.sharpeRatio.toFixed(2)} |
| Sortino Ratio | ${m.sortinoRatio.toFixed(2)} |
| Max Drawdown | ${m.maxDrawdownPct.toFixed(1)}% |
| Expectancy | $${m.expectancy.toFixed(2)} per trade |
| Avg Win | $${m.avgWinUsd.toFixed(2)} |
| Avg Loss | $${m.avgLossUsd.toFixed(2)} |
| Avg Holding | ${(m.avgHoldingHours / 24).toFixed(1)} days |
| Best Trade | ${m.bestTrade.toFixed(1)}% |
| Worst Trade | ${m.worstTrade.toFixed(1)}% |

**Strengths:**
`;

    // Analyze strengths
    const strengths = [];
    if (m.profitFactor > 1.5) strengths.push(`High profit factor (${m.profitFactor.toFixed(2)}) - wins significantly larger than losses`);
    if (m.winRate > 55) strengths.push(`Strong win rate (${m.winRate.toFixed(1)}%) - consistent profitability`);
    if (m.sharpeRatio > 1.0) strengths.push(`Good Sharpe ratio (${m.sharpeRatio.toFixed(2)}) - solid risk-adjusted returns`);
    if (m.maxDrawdownPct < 20) strengths.push(`Low max drawdown (${m.maxDrawdownPct.toFixed(1)}%) - capital preservation`);
    
    if (strengths.length > 0) {
      strengths.forEach(s => md += `- ${s}\n`);
    } else {
      md += `- None identified\n`;
    }

    md += `\n**Weaknesses:**
`;

    // Analyze weaknesses
    const weaknesses = [];
    if (m.profitFactor < 1.3) weaknesses.push(`Low profit factor (${m.profitFactor.toFixed(2)}) - wins barely exceed losses`);
    if (m.winRate < 50) weaknesses.push(`Below 50% win rate (${m.winRate.toFixed(1)}%) - more losers than winners`);
    if (m.sharpeRatio < 0.8) weaknesses.push(`Weak Sharpe ratio (${m.sharpeRatio.toFixed(2)}) - poor risk-adjusted returns`);
    if (m.maxDrawdownPct > 25) weaknesses.push(`High max drawdown (${m.maxDrawdownPct.toFixed(1)}%) - significant capital at risk`);
    
    if (weaknesses.length > 0) {
      weaknesses.forEach(w => md += `- ${w}\n`);
    } else {
      md += `- None identified\n`;
    }

    md += `\n---\n\n`;
  }

  md += `## Recommendations

### 🏆 Best Overall: ${sorted[0].strategy}

**Why:**
- Highest risk-adjusted score (${(sorted[0].metrics.profitFactor / Math.max(sorted[0].metrics.maxDrawdownPct, 1)).toFixed(3)})
- Profit Factor: ${sorted[0].metrics.profitFactor.toFixed(2)}
- Max Drawdown: ${sorted[0].metrics.maxDrawdownPct.toFixed(1)}%
- Win Rate: ${sorted[0].metrics.winRate.toFixed(1)}%

**Use When:**
- Capital preservation is priority
- Consistent returns preferred over maximum gains
- Moderate risk tolerance

---

### 🚀 Most Aggressive: ${results.find(r => r.strategy === 'Aggressive Scale').strategy}

**Stats:**
- Return: ${results.find(r => r.strategy === 'Aggressive Scale').metrics.totalReturnPct.toFixed(1)}%
- Win Rate: ${results.find(r => r.strategy === 'Aggressive Scale').metrics.winRate.toFixed(1)}%

**Use When:**
- Maximizing absolute returns
- Can tolerate higher drawdowns
- Shorter holding periods desired

---

### 🛡️ Most Conservative: ${sorted[sorted.length - 1].strategy}

**Stats:**
- Max Drawdown: ${sorted[sorted.length - 1].metrics.maxDrawdownPct.toFixed(1)}%
- Profit Factor: ${sorted[sorted.length - 1].metrics.profitFactor.toFixed(2)}

**Use When:**
- Risk minimization is critical
- Long-term capital growth
- High risk aversion

---

## Implementation Notes

### Key Findings

1. **Trailing stops** ${sorted[0].strategy === 'Trailing Stop' || sorted[1].strategy === 'Trailing Stop' ? 'perform well' : 'may underperform'} - ${sorted.find(r => r.strategy === 'Trailing Stop').metrics.profitFactor > 1.5 ? 'lock in gains while allowing upside' : 'can cut winners short'}

2. **Time-based exits** ${sorted.find(r => r.strategy === 'Time-Based Exit').metrics.totalReturnPct > 10 ? 'are effective' : 'may be suboptimal'} - ${sorted.find(r => r.strategy === 'Time-Based Exit').metrics.winRate > 50 ? 'forces discipline' : 'exits prematurely'}

3. **Volatility-based stops** ${sorted.find(r => r.strategy === 'Volatility-Based').metrics.maxDrawdownPct < sorted.find(r => r.strategy === 'Baseline (Current)').metrics.maxDrawdownPct ? 'reduce drawdowns' : 'may increase drawdowns'} in low-volume markets

4. **Aggressive scaling** ${sorted.find(r => r.strategy === 'Aggressive Scale').metrics.totalReturnPct > sorted.find(r => r.strategy === 'Baseline (Current)').metrics.totalReturnPct ? 'increases returns' : 'reduces returns'} but ${sorted.find(r => r.strategy === 'Aggressive Scale').metrics.maxDrawdownPct > sorted.find(r => r.strategy === 'Baseline (Current)').metrics.maxDrawdownPct ? 'increases risk' : 'manages risk well'}

### Recommended Hybrid Approach

Combine best elements:

\`\`\`python
# Recommended exit strategy
EXIT_RULES = {
    # From ${sorted[0].strategy}
    'primary_strategy': '${sorted[0].strategy}',
    
    # Incorporate strong elements from others
    'use_trailing_stop': ${sorted[0].strategy.includes('Trailing') || sorted[1].strategy.includes('Trailing')},
    'use_time_filter': ${sorted.find(r => r.strategy === 'Time-Based Exit').metrics.profitFactor > 1.3},
    'adjust_for_volatility': ${sorted.find(r => r.strategy === 'Volatility-Based').metrics.maxDrawdownPct < 22},
    
    # Optimal parameters
    'stop_loss': ${sorted[0].config.stopLoss || sorted[0].config.baseStop || sorted[0].config.initialStop},
    'profit_targets': ${JSON.stringify(sorted[0].config.tpLevels)},
    'allocations': ${JSON.stringify(sorted[0].config.tpAllocations)}
}
\`\`\`

---

## Next Steps

1. **Paper trade** the winning strategy for 2-4 weeks
2. **Monitor** actual slippage vs 1-2% assumptions
3. **A/B test** top 2 strategies with small capital
4. **Iterate** based on real market feedback

---

**Backtest Limitations:**

⚠️ Synthetic data - real markets may behave differently  
⚠️ No liquidity impact modeled (large orders would move markets)  
⚠️ Fixed slippage assumptions (1% entry, 1.5% exit)  
⚠️ No black swan events or regime changes  
⚠️ Limited sample size (60 days, 15 markets)  

**Always validate with live paper trading before risking capital.**

---

*Generated by Exit Strategy Backtest Engine v1.0*  
*Date: ${timestamp}*
`;

  return md;
}

// ============================================================================
// MAIN
// ============================================================================

function main() {
  console.log('\n🚀 EXIT STRATEGY BACKTEST COMPARISON');
  console.log('Testing 5 different exit strategies on synthetic data\n');
  
  // Generate data
  const markets = generateSyntheticMarkets(15, 60);
  
  // Run comparisons
  const results = compareStrategies(markets);
  
  // Generate report
  console.log(`\n${'='.repeat(70)}`);
  console.log('GENERATING REPORT');
  console.log(`${'='.repeat(70)}`);
  
  const markdown = generateMarkdownReport(results);
  fs.writeFileSync('BACKTEST_EXIT_STRATEGIES.md', markdown);
  
  console.log(`✓ Report saved to: BACKTEST_EXIT_STRATEGIES.md`);
  console.log(`\n✅ Backtest complete!`);
  console.log(`📊 Open BACKTEST_EXIT_STRATEGIES.md to view results\n`);
}

main();
