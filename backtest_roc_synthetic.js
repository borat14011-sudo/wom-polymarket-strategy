#!/usr/bin/env node
/**
 * Polymarket ROC Momentum Strategy Backtester
 * Uses synthetic data based on realistic Polymarket price patterns
 */

const fs = require('fs');

class SyntheticMarketGenerator {
    constructor() {
        this.markets = [
            { name: "2025 US Recession", volatility: 0.15, trend: -0.02 },
            { name: "Bitcoin to $100k in 2025", volatility: 0.25, trend: 0.05 },
            { name: "Trump wins GOP nomination", volatility: 0.10, trend: 0.03 },
            { name: "Fed cuts rates by June", volatility: 0.20, trend: 0.01 },
            { name: "SpaceX Mars landing 2025", volatility: 0.30, trend: -0.01 },
            { name: "AI achieves AGI in 2025", volatility: 0.35, trend: 0.02 },
            { name: "Inflation below 2% by Q4", volatility: 0.18, trend: -0.03 },
            { name: "S&P 500 above 6000", volatility: 0.22, trend: 0.04 },
            { name: "Major cyberattack in 2025", volatility: 0.28, trend: 0.01 },
            { name: "Climate bill passes Congress", volatility: 0.16, trend: -0.01 }
        ];
    }

    generatePriceHistory(market, hours = 720) { // 30 days of hourly data
        const prices = [];
        let currentPrice = 0.4 + Math.random() * 0.3; // Start between 0.4-0.7
        
        for (let i = 0; i < hours; i++) {
            // Add trend
            currentPrice += market.trend * (Math.random() - 0.5);
            
            // Add volatility
            currentPrice += market.volatility * (Math.random() - 0.5) * 0.1;
            
            // Add occasional momentum spikes
            if (Math.random() < 0.05) { // 5% chance
                const spike = (Math.random() - 0.5) * 0.15;
                currentPrice += spike;
            }
            
            // Keep price in valid range
            currentPrice = Math.max(0.05, Math.min(0.95, currentPrice));
            
            prices.push({
                price: currentPrice,
                timestamp: Date.now() - (hours - i) * 3600000,
                hour: i
            });
        }
        
        return prices;
    }
}

class PolymarketROCBacktester {
    constructor() {
        this.generator = new SyntheticMarketGenerator();
        this.results = [];
    }

    calculateROC(prices, timeframeHours) {
        if (prices.length < 2) return 0;
        
        const currentPrice = prices[prices.length - 1];
        const pastPrice = prices.length <= timeframeHours ? prices[0] : prices[prices.length - timeframeHours - 1];
        
        if (pastPrice === 0) return 0;
        
        return ((currentPrice - pastPrice) / pastPrice) * 100;
    }

    calculateRVR(entryPrice, currentPrice, stopLossPct = 0.12) {
        const risk = entryPrice * stopLossPct;
        const reward = 1.0 - currentPrice;
        
        if (risk === 0) return 0;
        return reward / risk;
    }

    simulateTrade(prices, entryIdx, entryPrice) {
        const stopLoss = entryPrice * 0.88; // 12% stop loss
        
        const profitTargets = [
            [1.10, 0.33], // 10% gain, exit 33%
            [1.20, 0.33], // 20% gain, exit another 33%
            [1.30, 0.34], // 30% gain, exit remainder
        ];
        
        let positionSize = 1.0;
        let totalPnl = 0.0;
        let exitReason = 'none';
        
        for (let i = entryIdx + 1; i < prices.length; i++) {
            const currentPrice = prices[i].price || entryPrice;
            
            // Check stop loss
            if (currentPrice <= stopLoss) {
                const pnlPct = ((currentPrice - entryPrice) / entryPrice) * 100;
                totalPnl = pnlPct * positionSize;
                exitReason = 'stop_loss';
                return { pnl: totalPnl, exitReason, duration: i - entryIdx };
            }
            
            // Check profit targets
            for (const [targetMultiplier, exitFraction] of profitTargets) {
                const targetPrice = entryPrice * targetMultiplier;
                if (currentPrice >= targetPrice && positionSize > 0) {
                    const pnlPct = ((currentPrice - entryPrice) / entryPrice) * 100;
                    totalPnl += pnlPct * exitFraction;
                    positionSize -= exitFraction;
                    
                    if (positionSize <= 0.01) {
                        exitReason = 'profit_target';
                        return { pnl: totalPnl, exitReason, duration: i - entryIdx };
                    }
                }
            }
        }
        
        // End of data - close remaining position
        if (positionSize > 0) {
            const finalPrice = prices[prices.length - 1].price || entryPrice;
            const pnlPct = ((finalPrice - entryPrice) / entryPrice) * 100;
            totalPnl += pnlPct * positionSize;
            exitReason = 'end_of_data';
        }
        
        return { pnl: totalPnl, exitReason, duration: prices.length - entryIdx };
    }

    backtestConfiguration(rocThreshold, timeframeHours) {
        const trades = [];
        let totalTrades = 0;
        let winningTrades = 0;
        let losingTrades = 0;
        let totalPnl = 0.0;
        let totalDuration = 0;
        
        console.log('\n' + '='.repeat(60));
        console.log(`Testing ROC ${rocThreshold}% over ${timeframeHours}h timeframe`);
        console.log('='.repeat(60));
        
        for (const market of this.generator.markets) {
            console.log(`\nAnalyzing: ${market.name}...`);
            
            // Generate price history
            const priceHistory = this.generator.generatePriceHistory(market, 720);
            
            if (priceHistory.length < timeframeHours + 10) {
                console.log(`  ⚠ Insufficient data`);
                continue;
            }
            
            // Scan for entry signals
            let lastTradeHour = -100;
            for (let i = timeframeHours; i < priceHistory.length - 10; i++) {
                // Avoid overlapping trades
                if (i - lastTradeHour < 24) continue;
                
                const lookbackPrices = priceHistory.slice(i - timeframeHours, i + 1).map(p => p.price);
                const currentPrice = priceHistory[i].price;
                
                // Calculate ROC
                const roc = this.calculateROC(lookbackPrices, timeframeHours);
                
                // Calculate RVR
                const rvr = this.calculateRVR(currentPrice, currentPrice);
                
                // Entry signal: ROC above threshold AND RVR > 2.5
                if (roc >= rocThreshold && rvr > 2.5) {
                    // Simulate trade
                    const { pnl, exitReason, duration } = this.simulateTrade(priceHistory, i, currentPrice);
                    
                    totalTrades++;
                    totalPnl += pnl;
                    totalDuration += duration;
                    
                    if (pnl > 0) {
                        winningTrades++;
                    } else {
                        losingTrades++;
                    }
                    
                    trades.push({
                        market: market.name,
                        entryPrice: currentPrice,
                        roc: roc,
                        rvr: rvr,
                        pnl: pnl,
                        exitReason: exitReason,
                        duration: duration
                    });
                    
                    console.log(`  📊 Trade #${totalTrades}: Entry=${currentPrice.toFixed(3)}, ROC=${roc.toFixed(1)}%, RVR=${rvr.toFixed(2)}x, PnL=${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}%, Exit=${exitReason}, Duration=${duration}h`);
                    
                    lastTradeHour = i;
                }
            }
        }
        
        const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100) : 0;
        const avgPnl = totalTrades > 0 ? (totalPnl / totalTrades) : 0;
        const avgDuration = totalTrades > 0 ? (totalDuration / totalTrades) : 0;
        
        return {
            rocThreshold: rocThreshold,
            timeframeHours: timeframeHours,
            totalTrades: totalTrades,
            winningTrades: winningTrades,
            losingTrades: losingTrades,
            winRate: winRate,
            totalPnl: totalPnl,
            avgPnlPerTrade: avgPnl,
            avgDuration: avgDuration,
            trades: trades
        };
    }

    runBacktestSuite() {
        console.log('🚀 Starting Polymarket ROC Momentum Strategy Backtest');
        console.log('📊 Using synthetic data based on realistic market patterns');
        console.log('='.repeat(60));
        
        // Test configurations
        const rocThresholds = [5, 10, 15, 20];
        const timeframes = [6, 12, 24];
        
        const allResults = [];
        
        for (const rocThreshold of rocThresholds) {
            for (const timeframe of timeframes) {
                const result = this.backtestConfiguration(rocThreshold, timeframe);
                allResults.push(result);
            }
        }
        
        // Generate report
        this.generateReport(allResults);
        
        return allResults;
    }

    generateReport(results) {
        let report = `# Polymarket ROC Momentum Strategy Backtest Results

## Executive Summary

This backtest evaluates a momentum-based trading strategy on Polymarket markets using Rate of Change (ROC) indicators combined with Risk/Reward Ratio (RVR) filters.

**Data Source**: Synthetic data based on realistic Polymarket market patterns (10 markets, 30 days of hourly data)

### Strategy Parameters
- **Entry Conditions**: ROC ≥ threshold AND RVR > 2.5x
- **Exit Conditions**: 
  - Stop Loss: 12% below entry
  - Tiered Profit Targets: 10% (exit 33%), 20% (exit 33%), 30% (exit 34%)

### ROC Thresholds Tested
- 5%, 10%, 15%, 20%

### Timeframes Tested
- 6 hours, 12 hours, 24 hours

---

## Results by Configuration

`;

        // Sort by total PnL
        const sortedResults = [...results].sort((a, b) => b.totalPnl - a.totalPnl);
        
        for (const result of sortedResults) {
            report += `
### Configuration: ${result.rocThreshold}% ROC over ${result.timeframeHours}h

| Metric | Value |
|--------|-------|
| **Total Trades** | ${result.totalTrades} |
| **Winning Trades** | ${result.winningTrades} |
| **Losing Trades** | ${result.losingTrades} |
| **Win Rate** | ${result.winRate.toFixed(2)}% |
| **Total PnL** | ${result.totalPnl >= 0 ? '+' : ''}${result.totalPnl.toFixed(2)}% |
| **Avg PnL/Trade** | ${result.avgPnlPerTrade >= 0 ? '+' : ''}${result.avgPnlPerTrade.toFixed(2)}% |
| **Avg Duration** | ${result.avgDuration.toFixed(1)}h |

`;
        }
        
        // Performance ranking
        report += `
---

## Performance Ranking

| Rank | Configuration | Total PnL | Win Rate | Trades | Avg PnL/Trade | Avg Duration |
|------|---------------|-----------|----------|--------|---------------|--------------|
`;
        
        sortedResults.forEach((result, idx) => {
            const config = `${result.rocThreshold}% / ${result.timeframeHours}h`;
            report += `| ${idx + 1} | ${config} | ${result.totalPnl >= 0 ? '+' : ''}${result.totalPnl.toFixed(2)}% | ${result.winRate.toFixed(1)}% | ${result.totalTrades} | ${result.avgPnlPerTrade >= 0 ? '+' : ''}${result.avgPnlPerTrade.toFixed(2)}% | ${result.avgDuration.toFixed(1)}h |\n`;
        });
        
        // Optimal configuration
        const best = sortedResults[0];
        const worst = sortedResults[sortedResults.length - 1];
        
        report += `
---

## Optimal Configuration

**🏆 Best Performer: ${best.rocThreshold}% ROC over ${best.timeframeHours}h timeframe**

- **Total Return**: ${best.totalPnl >= 0 ? '+' : ''}${best.totalPnl.toFixed(2)}%
- **Win Rate**: ${best.winRate.toFixed(2)}%
- **Total Trades**: ${best.totalTrades}
- **Average PnL per Trade**: ${best.avgPnlPerTrade >= 0 ? '+' : ''}${best.avgPnlPerTrade.toFixed(2)}%
- **Average Trade Duration**: ${best.avgDuration.toFixed(1)} hours

**⚠️ Worst Performer: ${worst.rocThreshold}% ROC over ${worst.timeframeHours}h timeframe**

- **Total Return**: ${worst.totalPnl >= 0 ? '+' : ''}${worst.totalPnl.toFixed(2)}%
- **Win Rate**: ${worst.winRate.toFixed(2)}%

---

## Key Insights

`;
        
        // Analysis
        const highThresholdResults = results.filter(r => r.rocThreshold >= 15);
        const lowThresholdResults = results.filter(r => r.rocThreshold < 15);
        
        const avgHighWr = highThresholdResults.length > 0 
            ? highThresholdResults.reduce((sum, r) => sum + r.winRate, 0) / highThresholdResults.length 
            : 0;
        const avgLowWr = lowThresholdResults.length > 0 
            ? lowThresholdResults.reduce((sum, r) => sum + r.winRate, 0) / lowThresholdResults.length 
            : 0;
        
        const avgHighPnl = highThresholdResults.length > 0 
            ? highThresholdResults.reduce((sum, r) => sum + r.totalPnl, 0) / highThresholdResults.length 
            : 0;
        const avgLowPnl = lowThresholdResults.length > 0 
            ? lowThresholdResults.reduce((sum, r) => sum + r.totalPnl, 0) / lowThresholdResults.length 
            : 0;
        
        report += `
### 1. ROC Threshold Analysis

| Threshold Range | Avg Win Rate | Avg Total PnL | Observations |
|----------------|--------------|---------------|--------------|
| **High (15-20%)** | ${avgHighWr.toFixed(1)}% | ${avgHighPnl >= 0 ? '+' : ''}${avgHighPnl.toFixed(2)}% | ${avgHighWr > avgLowWr ? '✅ Higher quality signals' : '⚠️ Fewer opportunities'} |
| **Low (5-10%)** | ${avgLowWr.toFixed(1)}% | ${avgLowPnl >= 0 ? '+' : ''}${avgLowPnl.toFixed(2)}% | ${avgLowWr > avgHighWr ? '✅ More consistent' : '⚠️ More false signals'} |

**Key Finding**: ${avgHighPnl > avgLowPnl ? 'Higher ROC thresholds filter for stronger momentum, leading to better performance' : 'Lower ROC thresholds capture more opportunities with acceptable quality'}

### 2. Timeframe Analysis
`;
        
        for (const tf of [6, 12, 24]) {
            const tfResults = results.filter(r => r.timeframeHours === tf);
            const avgPnl = tfResults.length > 0 
                ? tfResults.reduce((sum, r) => sum + r.totalPnl, 0) / tfResults.length 
                : 0;
            const avgWr = tfResults.length > 0 
                ? tfResults.reduce((sum, r) => sum + r.winRate, 0) / tfResults.length 
                : 0;
            const avgTrades = tfResults.length > 0 
                ? tfResults.reduce((sum, r) => sum + r.totalTrades, 0) / tfResults.length 
                : 0;
                
            report += `
**${tf}h Timeframe**:
- Average Total PnL: ${avgPnl >= 0 ? '+' : ''}${avgPnl.toFixed(2)}%
- Average Win Rate: ${avgWr.toFixed(1)}%
- Average Trades: ${avgTrades.toFixed(1)}
`;
        }
        
        report += `
### 3. Trade Frequency vs Performance

`;
        
        // Show top 3 by trade count
        const byTradeCount = [...sortedResults].sort((a, b) => b.totalTrades - a.totalTrades).slice(0, 3);
        
        report += "| Configuration | Trades | Total PnL | Win Rate |\n";
        report += "|---------------|--------|-----------|----------|\n";
        
        byTradeCount.forEach(result => {
            report += `| ${result.rocThreshold}% / ${result.timeframeHours}h | ${result.totalTrades} | ${result.totalPnl >= 0 ? '+' : ''}${result.totalPnl.toFixed(2)}% | ${result.winRate.toFixed(1)}% |\n`;
        });
        
        report += `
**Observation**: ${byTradeCount[0].totalPnl > 0 ? 'Higher frequency can work with good risk management' : 'More trades ≠ more profit; quality > quantity'}

---

## Sample Trades (Top Configuration)

`;
        
        // Show sample trades from best configuration
        const sampleTrades = best.trades.slice(0, 12);
        
        if (sampleTrades.length > 0) {
            report += "| Market | Entry | ROC | RVR | PnL | Duration | Exit |\n";
            report += "|--------|-------|-----|-----|-----|----------|------|\n";
            
            sampleTrades.forEach(trade => {
                report += `| ${trade.market} | ${trade.entryPrice.toFixed(3)} | ${trade.roc.toFixed(1)}% | ${trade.rvr.toFixed(2)}x | ${trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}% | ${trade.duration}h | ${trade.exitReason} |\n`;
            });
        }
        
        report += `
---

## Methodology

1. **Data Source**: Synthetic price histories for 10 diverse Polymarket-style markets
2. **Time Period**: 30 days of hourly price data per market (720 data points)
3. **Entry Signal**: ROC over specified timeframe ≥ threshold AND RVR > 2.5x
4. **Position Sizing**: Equal position sizes for all trades
5. **Exit Logic**: 
   - Hit 12% stop loss → full exit
   - Hit 10% profit → exit 33% of position
   - Hit 20% profit → exit another 33%
   - Hit 30% profit → exit remainder
6. **Lookback Period**: Varies by timeframe (6h, 12h, or 24h)
7. **Trade Spacing**: Minimum 24 hours between trades on same market

## Limitations

- **Synthetic Data**: Real markets may behave differently
- **No Liquidity Modeling**: Assumes perfect fills at market price
- **No Slippage**: Actual execution would incur slippage costs
- **No Fees**: Transaction fees would reduce returns
- **Limited History**: 30 days may not capture all market regimes
- **No External Factors**: News events, major announcements not modeled

## Recommendations

Based on this backtest:

1. **🎯 Optimal Setup**: Use **${best.rocThreshold}% ROC threshold** with **${best.timeframeHours}h timeframe**
   - Expected win rate: ~${best.winRate.toFixed(0)}%
   - Expected avg PnL per trade: ~${best.avgPnlPerTrade >= 0 ? '+' : ''}${best.avgPnlPerTrade.toFixed(1)}%
   - Avg trade duration: ~${best.avgDuration.toFixed(0)} hours

2. **📊 Risk Management**:
   - The 12% stop loss is CRITICAL - never override it
   - Position size should account for correlation between markets
   - Don't exceed 20% of capital per trade

3. **⚙️ Strategy Tuning**:
   - ${best.rocThreshold >= 15 ? 'High threshold = fewer but better signals' : 'Low threshold = more frequent trades, watch win rate'}
   - ${best.timeframeHours >= 24 ? 'Longer timeframe = more stable signals' : 'Shorter timeframe = faster entries/exits'}
   - Consider RVR > 3.0x for even higher quality signals

4. **📈 Market Selection**:
   - Focus on high-volume, liquid markets
   - Avoid markets with binary news catalysts
   - Prefer markets with gradual price discovery

5. **🔄 Monitoring**:
   - Re-run backtest weekly with live data
   - Track actual vs expected performance
   - Pause strategy if win rate drops below ${(best.winRate * 0.7).toFixed(0)}%

6. **💡 Advanced Optimizations**:
   - Combine with volume analysis for confirmation
   - Add market sentiment filters
   - Use dynamic position sizing based on RVR
   - Implement partial entry on weaker signals

---

## Risk Disclosure

⚠️ **Important**: This backtest uses synthetic data and does not guarantee future performance. Polymarket trading involves substantial risk. Always:

- Start with small position sizes
- Never risk more than you can afford to lose
- Monitor positions actively
- Have a plan for every trade
- Be aware of regulatory considerations

---

*Backtest completed: ${new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC*
*Total configurations tested: ${results.length}*
*Total trades simulated: ${results.reduce((sum, r) => sum + r.totalTrades, 0)}*
`;
        
        // Write report
        fs.writeFileSync('BACKTEST_ROC_RESULTS.md', report, 'utf-8');
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ Backtest complete! Results saved to BACKTEST_ROC_RESULTS.md');
        console.log('='.repeat(60));
        console.log(`\n📊 Summary:`);
        console.log(`   Best config: ${best.rocThreshold}% ROC / ${best.timeframeHours}h`);
        console.log(`   Total PnL: ${best.totalPnl >= 0 ? '+' : ''}${best.totalPnl.toFixed(2)}%`);
        console.log(`   Win Rate: ${best.winRate.toFixed(1)}%`);
        console.log(`   Trades: ${best.totalTrades}`);
    }
}

// Run the backtest
const backtester = new PolymarketROCBacktester();
backtester.runBacktestSuite();
