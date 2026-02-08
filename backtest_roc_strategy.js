#!/usr/bin/env node
/**
 * Polymarket ROC Momentum Strategy Backtester
 * Tests different ROC thresholds and timeframes
 */

const https = require('https');
const fs = require('fs');

class PolymarketROCBacktester {
    constructor() {
        this.baseUrl = 'gamma-api.polymarket.com';
        this.results = [];
    }

    async fetchJson(path) {
        return new Promise((resolve, reject) => {
            https.get({
                hostname: this.baseUrl,
                path: path,
                headers: { 'User-Agent': 'Mozilla/5.0' }
            }, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(e);
                    }
                });
            }).on('error', reject);
        });
    }

    async fetchTopMarkets(limit = 20) {
        try {
            const data = await this.fetchJson(`/markets?limit=${limit}&closed=false`);
            return Array.isArray(data) ? data : [];
        } catch (e) {
            console.log(`Error fetching markets: ${e.message}`);
            return [];
        }
    }

    async fetchMarketPrices(conditionId, limit = 1000) {
        try {
            const data = await this.fetchJson(`/prices?market=${conditionId}&limit=${limit}`);
            return Array.isArray(data) ? data : [];
        } catch (e) {
            console.log(`Error fetching prices for ${conditionId}: ${e.message}`);
            return [];
        }
    }

    calculateROC(prices, timeframeHours) {
        if (prices.length < 2) return 0;
        
        const currentPrice = prices[prices.length - 1];
        const pastPrice = prices.length <= timeframeHours ? prices[0] : prices[prices.length - timeframeHours];
        
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
                return { pnl: totalPnl, exitReason };
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
                        return { pnl: totalPnl, exitReason };
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
        
        return { pnl: totalPnl, exitReason };
    }

    async backtestConfiguration(rocThreshold, timeframeHours, marketsData) {
        const trades = [];
        let totalTrades = 0;
        let winningTrades = 0;
        let losingTrades = 0;
        let totalPnl = 0.0;
        
        console.log('\n' + '='.repeat(60));
        console.log(`Testing ROC ${rocThreshold}% over ${timeframeHours}h timeframe`);
        console.log('='.repeat(60));
        
        for (const market of marketsData.slice(0, 10)) {
            const marketName = market.question || 'Unknown';
            const conditionId = market.conditionId || '';
            
            if (!conditionId) continue;
            
            console.log(`\nAnalyzing: ${marketName.substring(0, 60)}...`);
            
            // Fetch price history
            const priceData = await this.fetchMarketPrices(conditionId);
            await new Promise(resolve => setTimeout(resolve, 500)); // Rate limiting
            
            if (!priceData || priceData.length < timeframeHours + 10) {
                console.log(`  ⚠ Insufficient data (${priceData.length} points)`);
                continue;
            }
            
            // Process prices
            const prices = priceData
                .filter(p => p && typeof p.price !== 'undefined')
                .map(p => ({
                    price: parseFloat(p.price),
                    timestamp: p.timestamp || 0
                }));
            
            if (prices.length < timeframeHours + 10) continue;
            
            // Scan for entry signals
            for (let i = timeframeHours; i < prices.length - 10; i++) {
                const lookbackPrices = prices.slice(i - timeframeHours, i + 1).map(p => p.price);
                const currentPrice = prices[i].price;
                
                // Calculate ROC
                const roc = this.calculateROC(lookbackPrices, timeframeHours);
                
                // Calculate RVR
                const rvr = this.calculateRVR(currentPrice, currentPrice);
                
                // Entry signal: ROC above threshold AND RVR > 2.5
                if (roc >= rocThreshold && rvr > 2.5) {
                    // Simulate trade
                    const { pnl, exitReason } = this.simulateTrade(prices, i, currentPrice);
                    
                    totalTrades++;
                    totalPnl += pnl;
                    
                    if (pnl > 0) {
                        winningTrades++;
                    } else {
                        losingTrades++;
                    }
                    
                    trades.push({
                        market: marketName.substring(0, 40),
                        entryPrice: currentPrice,
                        roc: roc,
                        rvr: rvr,
                        pnl: pnl,
                        exitReason: exitReason
                    });
                    
                    console.log(`  📊 Trade #${totalTrades}: Entry=${currentPrice.toFixed(3)}, ROC=${roc.toFixed(1)}%, RVR=${rvr.toFixed(2)}x, PnL=${pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}%, Exit=${exitReason}`);
                    
                    // Skip ahead to avoid overlapping trades
                    i += 24;
                }
            }
        }
        
        const winRate = totalTrades > 0 ? (winningTrades / totalTrades * 100) : 0;
        const avgPnl = totalTrades > 0 ? (totalPnl / totalTrades) : 0;
        
        return {
            rocThreshold: rocThreshold,
            timeframeHours: timeframeHours,
            totalTrades: totalTrades,
            winningTrades: winningTrades,
            losingTrades: losingTrades,
            winRate: winRate,
            totalPnl: totalPnl,
            avgPnlPerTrade: avgPnl,
            trades: trades
        };
    }

    async runBacktestSuite() {
        console.log('🚀 Starting Polymarket ROC Momentum Strategy Backtest');
        console.log('='.repeat(60));
        
        // Fetch markets
        console.log('\n📊 Fetching top markets...');
        const markets = await this.fetchTopMarkets(20);
        
        if (!markets || markets.length === 0) {
            console.log('❌ Failed to fetch markets');
            return;
        }
        
        console.log(`✅ Loaded ${markets.length} markets`);
        
        // Test configurations
        const rocThresholds = [5, 10, 15, 20];
        const timeframes = [6, 12, 24];
        
        const allResults = [];
        
        for (const rocThreshold of rocThresholds) {
            for (const timeframe of timeframes) {
                const result = await this.backtestConfiguration(
                    rocThreshold,
                    timeframe,
                    markets
                );
                allResults.push(result);
                await new Promise(resolve => setTimeout(resolve, 1000)); // Rate limiting
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

`;
        }
        
        // Performance ranking
        report += `
---

## Performance Ranking

| Rank | Configuration | Total PnL | Win Rate | Trades | Avg PnL/Trade |
|------|---------------|-----------|----------|--------|---------------|
`;
        
        sortedResults.forEach((result, idx) => {
            const config = `${result.rocThreshold}% / ${result.timeframeHours}h`;
            report += `| ${idx + 1} | ${config} | ${result.totalPnl >= 0 ? '+' : ''}${result.totalPnl.toFixed(2)}% | ${result.winRate.toFixed(1)}% | ${result.totalTrades} | ${result.avgPnlPerTrade >= 0 ? '+' : ''}${result.avgPnlPerTrade.toFixed(2)}% |\n`;
        });
        
        // Optimal configuration
        const best = sortedResults[0];
        report += `
---

## Optimal Configuration

**🏆 Best Performer: ${best.rocThreshold}% ROC over ${best.timeframeHours}h timeframe**

- **Total Return**: ${best.totalPnl >= 0 ? '+' : ''}${best.totalPnl.toFixed(2)}%
- **Win Rate**: ${best.winRate.toFixed(2)}%
- **Total Trades**: ${best.totalTrades}
- **Average PnL per Trade**: ${best.avgPnlPerTrade >= 0 ? '+' : ''}${best.avgPnlPerTrade.toFixed(2)}%

### Key Insights

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
        
        report += `
1. **Threshold Analysis**:
   - High ROC thresholds (15-20%): Avg win rate ${avgHighWr.toFixed(1)}%
   - Low ROC thresholds (5-10%): Avg win rate ${avgLowWr.toFixed(1)}%

2. **Timeframe Analysis**:
`;
        
        for (const tf of [6, 12, 24]) {
            const tfResults = results.filter(r => r.timeframeHours === tf);
            const avgPnl = tfResults.length > 0 
                ? tfResults.reduce((sum, r) => sum + r.totalPnl, 0) / tfResults.length 
                : 0;
            report += `   - ${tf}h timeframe: Avg total PnL ${avgPnl >= 0 ? '+' : ''}${avgPnl.toFixed(2)}%\n`;
        }
        
        report += `
3. **Trade Frequency**:
`;
        
        sortedResults.slice(0, 3).forEach(result => {
            report += `   - ${result.rocThreshold}% / ${result.timeframeHours}h: ${result.totalTrades} trades\n`;
        });
        
        report += `
---

## Sample Trades (Top Configuration)

`;
        
        // Show sample trades from best configuration
        const sampleTrades = best.trades.slice(0, 10);
        
        if (sampleTrades.length > 0) {
            report += "| Market | Entry Price | ROC | RVR | PnL | Exit Reason |\n";
            report += "|--------|-------------|-----|-----|-----|-------------|\n";
            
            sampleTrades.forEach(trade => {
                report += `| ${trade.market.substring(0, 30)} | ${trade.entryPrice.toFixed(3)} | ${trade.roc.toFixed(1)}% | ${trade.rvr.toFixed(2)}x | ${trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}% | ${trade.exitReason} |\n`;
            });
        }
        
        report += `
---

## Methodology

1. **Data Source**: Gamma API historical price data for top 10 Polymarket markets
2. **Entry Signal**: When ROC over specified timeframe exceeds threshold AND RVR > 2.5x
3. **Position Sizing**: Equal position sizes for all trades
4. **Exit Logic**: 
   - Hit 12% stop loss → full exit
   - Hit 10% profit → exit 33% of position
   - Hit 20% profit → exit another 33%
   - Hit 30% profit → exit remainder
5. **Lookback Period**: Varies by timeframe (6h, 12h, or 24h)

## Limitations

- Historical data may be limited for some markets
- Does not account for liquidity constraints or slippage
- Past performance does not guarantee future results
- Market conditions on Polymarket can change rapidly
- Does not include transaction fees

## Recommendations

Based on this backtest:

1. **Optimal Setup**: Use **${best.rocThreshold}% ROC threshold** with **${best.timeframeHours}h timeframe**
2. **Risk Management**: The 12% stop loss is critical - do not override
3. **Position Sizing**: Consider reducing position size for lower ROC signals
4. **Market Selection**: Focus on high-volume, liquid markets
5. **Monitoring**: Re-run backtest monthly to validate strategy performance

---

*Backtest completed: ${new Date().toISOString().replace('T', ' ').substring(0, 19)}*
`;
        
        // Write report
        fs.writeFileSync('BACKTEST_ROC_RESULTS.md', report, 'utf-8');
        
        console.log('\n' + '='.repeat(60));
        console.log('✅ Backtest complete! Results saved to BACKTEST_ROC_RESULTS.md');
        console.log('='.repeat(60));
    }
}

// Run the backtest
const backtester = new PolymarketROCBacktester();
backtester.runBacktestSuite().catch(err => {
    console.error('Error running backtest:', err);
    process.exit(1);
});
