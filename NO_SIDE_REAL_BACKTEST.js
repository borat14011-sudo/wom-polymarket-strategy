#!/usr/bin/env node
/**
 * NO-SIDE BIAS REAL BACKTEST
 * Test the strategy: bet NO when YES drops below 15%
 * 
 * Strategy:
 * - Find markets that ended with YES < 15% (proxy for markets that hit <15% at some point)
 * - Filter for volume > threshold (proxy for volume spike)
 * - Calculate: if we bet NO, did we win?
 * - Compare win rate to theoretical 82%
 */

const fs = require('fs');
const path = require('path');

class NOSideBacktester {
    constructor() {
        this.trades = [];
        this.wins = 0;
        this.losses = 0;
        this.totalVolume = 0;
    }

    loadResolvedMarkets(csvPath) {
        console.log('Loading resolved markets from CSV...\n');
        
        const csvContent = fs.readFileSync(csvPath, 'utf-8');
        const lines = csvContent.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.replace(/^"|"$/g, ''));
        
        const markets = [];
        for (let i = 1; i < lines.length; i++) {
            // Simple CSV parsing (handles quoted fields with commas)
            const values = this.parseCSVLine(lines[i]);
            const market = {};
            headers.forEach((header, idx) => {
                market[header] = values[idx];
            });
            markets.push(market);
        }
        
        console.log(`✓ Loaded ${markets.length} resolved markets\n`);
        return markets;
    }

    parseCSVLine(line) {
        const result = [];
        let current = '';
        let inQuotes = false;
        
        for (let i = 0; i < line.length; i++) {
            const char = line[i];
            
            if (char === '"') {
                inQuotes = !inQuotes;
            } else if (char === ',' && !inQuotes) {
                result.push(current.trim());
                current = '';
            } else {
                current += char;
            }
        }
        result.push(current.trim());
        
        return result;
    }

    parseOutcomes(outcomeStr) {
        if (!outcomeStr) return [];
        return outcomeStr.split('|');
    }

    parsePrices(priceStr) {
        if (!priceStr) return [];
        return priceStr.split('|').map(p => parseFloat(p));
    }

    filterMarkets(markets, minVolume = 1000) {
        console.log('Filtering markets for NO-side bias strategy...\n');
        console.log('Criteria:');
        console.log('  - YES final price < 0.15 (15%)');
        console.log('  - Volume > $' + minVolume.toLocaleString());
        console.log('  - Clear winner determined\n');
        
        const filtered = markets.filter(market => {
            const outcomes = this.parseOutcomes(market.outcomes);
            const prices = this.parsePrices(market.final_prices);
            const volume = parseFloat(market.volume_usd) || 0;
            const winner = market.winner;
            
            // Must have Yes/No outcomes
            if (outcomes.length !== 2) return false;
            if (!outcomes.includes('Yes') || !outcomes.includes('No')) return false;
            
            // Must have a winner
            if (!winner || winner === 'null') return false;
            
            // Find YES price
            const yesIndex = outcomes.indexOf('Yes');
            const yesPrice = prices[yesIndex];
            
            // Filter: YES price < 0.15 AND volume > threshold
            if (yesPrice < 0.15 && volume > minVolume) {
                return true;
            }
            
            return false;
        });
        
        console.log(`✓ Found ${filtered.length} markets matching criteria\n`);
        return filtered;
    }

    runBacktest(filteredMarkets) {
        console.log('=' .repeat(80));
        console.log('RUNNING BACKTEST: Betting NO on each market');
        console.log('=' .repeat(80));
        console.log();
        
        filteredMarkets.forEach((market, idx) => {
            const outcomes = this.parseOutcomes(market.outcomes);
            const prices = this.parsePrices(market.final_prices);
            const volume = parseFloat(market.volume_usd) || 0;
            const winner = market.winner;
            
            const yesIndex = outcomes.indexOf('Yes');
            const noIndex = outcomes.indexOf('No');
            const yesPrice = prices[yesIndex];
            const noPrice = prices[noIndex];
            
            // We bet NO - did NO win?
            const noWon = (winner === 'No');
            
            const trade = {
                id: idx + 1,
                question: market.question,
                eventTitle: market.event_title,
                yesEntryPrice: yesPrice,
                noEntryPrice: noPrice,
                volume: volume,
                winner: winner,
                noWon: noWon,
                outcome: noWon ? 'WIN' : 'LOSS'
            };
            
            this.trades.push(trade);
            
            if (noWon) {
                this.wins++;
            } else {
                this.losses++;
            }
            
            this.totalVolume += volume;
            
            // Print trade
            console.log(`Trade #${trade.id}: ${trade.outcome}`);
            console.log(`  Question: ${trade.question.slice(0, 70)}...`);
            console.log(`  YES Price: ${(yesPrice * 100).toFixed(1)}% | NO Price: ${(noPrice * 100).toFixed(1)}%`);
            console.log(`  Volume: $${volume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`);
            console.log(`  Winner: ${winner}`);
            console.log();
        });
    }

    calculateStats() {
        const total = this.trades.length;
        const winRate = total > 0 ? (this.wins / total) * 100 : 0;
        const avgVolume = total > 0 ? this.totalVolume / total : 0;
        
        return {
            totalTrades: total,
            wins: this.wins,
            losses: this.losses,
            winRate: winRate,
            avgVolume: avgVolume,
            totalVolume: this.totalVolume
        };
    }

    generateReport(outputPath) {
        const stats = this.calculateStats();
        const theoretical = 82; // Theoretical 82% win rate
        
        let report = '';
        
        report += '# NO-SIDE BIAS REAL BACKTEST RESULTS\n\n';
        report += `**Generated:** ${new Date().toISOString()}\n\n`;
        report += '## Strategy\n\n';
        report += 'Test betting NO on markets where YES dropped below 15% with volume spikes.\n\n';
        report += '**Entry Criteria:**\n';
        report += '- Market hit YES < 15% at some point (proxied by final YES < 15%)\n';
        report += '- Volume > $1,000 (proxy for volume spike)\n';
        report += '- Binary Yes/No markets only\n\n';
        
        report += '---\n\n';
        report += '## SUMMARY RESULTS\n\n';
        report += `| Metric | Value |\n`;
        report += `|--------|-------|\n`;
        report += `| **Total Trades** | ${stats.totalTrades} |\n`;
        report += `| **Wins** | ${stats.wins} |\n`;
        report += `| **Losses** | ${stats.losses} |\n`;
        report += `| **Win Rate** | **${stats.winRate.toFixed(2)}%** |\n`;
        report += `| **Theoretical Win Rate** | 82.00% |\n`;
        report += `| **Difference** | ${(stats.winRate - theoretical).toFixed(2)}% |\n`;
        report += `| **Total Volume Analyzed** | $${stats.totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} |\n`;
        report += `| **Avg Volume per Trade** | $${stats.avgVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})} |\n\n`;
        
        report += '---\n\n';
        report += '## ANALYSIS\n\n';
        
        if (stats.winRate >= theoretical) {
            report += `✅ **Strategy OUTPERFORMED theoretical expectations!**\n\n`;
            report += `The real win rate of ${stats.winRate.toFixed(2)}% exceeded the theoretical 82% by ${(stats.winRate - theoretical).toFixed(2)} percentage points.\n\n`;
        } else {
            report += `⚠️ **Strategy UNDERPERFORMED theoretical expectations.**\n\n`;
            report += `The real win rate of ${stats.winRate.toFixed(2)}% fell short of the theoretical 82% by ${(theoretical - stats.winRate).toFixed(2)} percentage points.\n\n`;
        }
        
        report += '**Key Insights:**\n\n';
        report += `1. Sample size: ${stats.totalTrades} trades (${stats.totalTrades >= 30 ? 'statistically significant' : 'limited sample'})\n`;
        report += `2. Win/Loss ratio: ${stats.wins}W / ${stats.losses}L\n`;
        report += `3. Average market volume: $${stats.avgVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}\n\n`;
        
        report += '---\n\n';
        report += '## DETAILED TRADE LOG\n\n';
        report += '| # | Outcome | Question | YES Price | Volume | Winner |\n';
        report += '|---|---------|----------|-----------|--------|--------|\n';
        
        this.trades.forEach(trade => {
            const emoji = trade.noWon ? '✅' : '❌';
            const question = trade.question.slice(0, 50) + (trade.question.length > 50 ? '...' : '');
            report += `| ${trade.id} | ${emoji} ${trade.outcome} | ${question} | ${(trade.yesEntryPrice * 100).toFixed(1)}% | $${trade.volume.toLocaleString('en-US', {maximumFractionDigits: 0})} | ${trade.winner} |\n`;
        });
        
        report += '\n---\n\n';
        report += '## METHODOLOGY NOTES\n\n';
        report += '**Data Source:** Real resolved Polymarket markets\n\n';
        report += '**Limitations:**\n';
        report += '- No precise time-series data available\n';
        report += '- Using final prices as proxy for "hit <15% at some point"\n';
        report += '- Volume spike criterion approximated by minimum volume threshold\n';
        report += '- Entry timing not precisely reconstructed\n\n';
        report += '**Assumptions:**\n';
        report += '- Markets with final YES < 15% likely experienced YES < 15% during lifecycle\n';
        report += '- High volume markets represent those with volume spikes\n';
        report += '- Betting NO when YES is low represents the strategy intent\n\n';
        
        report += '---\n\n';
        report += '## CONCLUSION\n\n';
        
        if (stats.totalTrades === 0) {
            report += '⚠️ No trades matched the criteria. Consider:\n';
            report += '- Lowering volume threshold\n';
            report += '- Expanding YES price threshold\n';
            report += '- Collecting more resolved market data\n';
        } else if (stats.winRate >= 75) {
            report += `✅ The NO-side bias strategy shows promise with a ${stats.winRate.toFixed(1)}% win rate.\n\n`;
            report += 'However, this backtest has limitations due to data constraints. ';
            report += 'For production use, implement:\n';
            report += '- Real-time price monitoring to catch exact <15% moments\n';
            report += '- Volume spike detection (>2.5x average)\n';
            report += '- Entry/exit timing optimization\n';
            report += '- Risk management and position sizing\n';
        } else {
            report += `⚠️ Win rate of ${stats.winRate.toFixed(1)}% suggests the strategy needs refinement.\n\n`;
            report += 'Consider:\n';
            report += '- More selective entry criteria\n';
            report += '- Better volume spike detection\n';
            report += '- Market quality filters\n';
            report += '- Time-based filters (avoid late entries)\n';
        }
        
        report += '\n';
        
        // Write report
        fs.writeFileSync(outputPath, report);
        console.log(`\n✓ Report saved to ${outputPath}\n`);
        
        return report;
    }

    printSummary() {
        const stats = this.calculateStats();
        
        console.log();
        console.log('=' .repeat(80));
        console.log('BACKTEST SUMMARY');
        console.log('=' .repeat(80));
        console.log();
        console.log(`Total Trades:     ${stats.totalTrades}`);
        console.log(`Wins:             ${stats.wins}`);
        console.log(`Losses:           ${stats.losses}`);
        console.log(`Win Rate:         ${stats.winRate.toFixed(2)}%`);
        console.log(`Theoretical:      82.00%`);
        console.log(`Difference:       ${(stats.winRate - 82).toFixed(2)}%`);
        console.log();
        console.log(`Total Volume:     $${stats.totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        console.log(`Avg Volume:       $${stats.avgVolume.toLocaleString('en-US', {minimumFractionDigits: 2})}`);
        console.log();
    }
}

// Main execution
async function main() {
    console.log('\n');
    console.log('═'.repeat(80));
    console.log('  NO-SIDE BIAS STRATEGY: REAL BACKTEST ON RESOLVED MARKETS');
    console.log('═'.repeat(80));
    console.log('\n');
    
    const backtester = new NOSideBacktester();
    
    // Load data
    const csvPath = path.join(__dirname, 'polymarket_resolved_markets.csv');
    const markets = backtester.loadResolvedMarkets(csvPath);
    
    // Filter for strategy criteria
    const filteredMarkets = backtester.filterMarkets(markets, 1000);
    
    if (filteredMarkets.length === 0) {
        console.log('⚠️  No markets matched the criteria!');
        console.log('\nTrying with lower volume threshold...\n');
        const filteredMarkets2 = backtester.filterMarkets(markets, 100);
        
        if (filteredMarkets2.length === 0) {
            console.log('❌ Still no matches. The dataset may be limited.');
            console.log('   Try collecting more resolved market data.');
            return;
        }
        
        backtester.runBacktest(filteredMarkets2);
    } else {
        backtester.runBacktest(filteredMarkets);
    }
    
    // Print summary
    backtester.printSummary();
    
    // Generate detailed report
    const reportPath = path.join(__dirname, 'NO_SIDE_REAL_BACKTEST.md');
    backtester.generateReport(reportPath);
    
    console.log('═'.repeat(80));
    console.log('  BACKTEST COMPLETE');
    console.log('═'.repeat(80));
    console.log();
}

main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
