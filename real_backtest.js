const https = require('https');
const fs = require('fs');

function httpGet(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data) });
                } catch (e) {
                    resolve({ status: res.statusCode, data: data });
                }
            });
        }).on('error', reject);
    });
}

async function fetchHistoricalPrices(tokenId, interval = '1w') {
    const url = `https://clob.polymarket.com/prices-history?market=${tokenId}&interval=${interval}&fidelity=60`;
    console.log(`Fetching price history (interval: ${interval})...`);
    
    const result = await httpGet(url);
    if (result.status === 200 && result.data.history) {
        return result.data.history.map(h => ({
            timestamp: new Date(h.t * 1000),
            price: parseFloat(h.p),
            t: h.t
        })).sort((a, b) => a.timestamp - b.timestamp);
    }
    return [];
}

function calculateReturns(prices) {
    const returns = [];
    for (let i = 1; i < prices.length; i++) {
        returns.push({
            timestamp: prices[i].timestamp,
            return: (prices[i].price - prices[i - 1].price) / prices[i - 1].price,
            price: prices[i].price,
            prevPrice: prices[i - 1].price
        });
    }
    return returns;
}

function meanReversionStrategy(prices, lookbackHours = 24) {
    const trades = [];
    
    for (let i = 0; i < prices.length; i++) {
        // Calculate lookback window
        const lookbackStart = prices[i].timestamp.getTime() - (lookbackHours * 3600 * 1000);
        const window = prices.slice(0, i + 1).filter(p => p.timestamp.getTime() >= lookbackStart);
        
        if (window.length < 10) continue; // Need enough data
        
        const windowPrices = window.map(p => p.price);
        const mean = windowPrices.reduce((a, b) => a + b) / windowPrices.length;
        const std = Math.sqrt(windowPrices.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / windowPrices.length);
        
        const currentPrice = prices[i].price;
        const zScore = (currentPrice - mean) / (std + 0.0001);
        
        // Mean reversion signals
        // If price is 1.5 std below mean, BUY (expect reversion up)
        // If price is 1.5 std above mean, SELL (expect reversion down)
        
        if (zScore < -1.5 && currentPrice < 0.8) {
            trades.push({
                timestamp: prices[i].timestamp,
                action: 'BUY',
                price: currentPrice,
                zScore: zScore,
                reason: `Price ${currentPrice.toFixed(4)} is ${Math.abs(zScore).toFixed(2)} std below mean ${mean.toFixed(4)}`
            });
        } else if (zScore > 1.5 && currentPrice > 0.2) {
            trades.push({
                timestamp: prices[i].timestamp,
                action: 'SELL',
                price: currentPrice,
                zScore: zScore,
                reason: `Price ${currentPrice.toFixed(4)} is ${zScore.toFixed(2)} std above mean ${mean.toFixed(4)}`
            });
        }
    }
    
    return trades;
}

function evaluateTrades(trades, prices) {
    if (trades.length === 0) return { pnl: 0, winRate: 0, trades: 0 };
    
    const positions = [];
    let currentPosition = null;
    
    for (const trade of trades) {
        if (trade.action === 'BUY' && !currentPosition) {
            currentPosition = {
                entry: trade.price,
                entryTime: trade.timestamp,
                type: 'LONG'
            };
        } else if (trade.action === 'SELL' && currentPosition && currentPosition.type === 'LONG') {
            const pnl = trade.price - currentPosition.entry;
            const pnlPct = (pnl / currentPosition.entry) * 100;
            const holdTime = (trade.timestamp - currentPosition.entryTime) / (1000 * 3600);
            
            positions.push({
                entry: currentPosition.entry,
                exit: trade.price,
                pnl: pnl,
                pnlPct: pnlPct,
                holdTime: holdTime,
                win: pnl > 0
            });
            
            currentPosition = null;
        }
    }
    
    // Close any open position at current price
    if (currentPosition) {
        const lastPrice = prices[prices.length - 1].price;
        const pnl = lastPrice - currentPosition.entry;
        const pnlPct = (pnl / currentPosition.entry) * 100;
        const holdTime = (prices[prices.length - 1].timestamp - currentPosition.entryTime) / (1000 * 3600);
        
        positions.push({
            entry: currentPosition.entry,
            exit: lastPrice,
            pnl: pnl,
            pnlPct: pnlPct,
            holdTime: holdTime,
            win: pnl > 0,
            open: true
        });
    }
    
    const wins = positions.filter(p => p.win).length;
    const totalPnl = positions.reduce((sum, p) => sum + p.pnlPct, 0);
    const avgPnl = totalPnl / positions.length;
    const winRate = (wins / positions.length) * 100;
    
    return {
        positions: positions,
        totalTrades: positions.length,
        winRate: winRate,
        avgPnlPct: avgPnl,
        totalPnlPct: totalPnl
    };
}

async function runBacktest() {
    console.log('='.repeat(80));
    console.log('REAL BACKTEST: Mean Reversion Strategy');
    console.log('='.repeat(80));
    console.log('');
    
    // Fetch real historical data
    const markets = JSON.parse(fs.readFileSync('active_markets_test.json'));
    const market = markets[0]; // Test first market
    
    console.log(`Market: ${market.question}`);
    console.log(`Token ID: ${market.token_id}`);
    console.log('');
    
    const prices = await fetchHistoricalPrices(market.token_id, '1w');
    
    if (prices.length === 0) {
        console.log('❌ No price data available');
        return;
    }
    
    console.log(`✓ Fetched ${prices.length} price points`);
    console.log(`✓ Period: ${prices[0].timestamp.toISOString()} to ${prices[prices.length - 1].timestamp.toISOString()}`);
    console.log(`✓ Duration: ${((prices[prices.length - 1].timestamp - prices[0].timestamp) / (1000 * 3600 * 24)).toFixed(1)} days`);
    console.log('');
    
    // Run mean reversion strategy
    console.log('Running mean reversion strategy (24h lookback, ±1.5 std threshold)...');
    const trades = meanReversionStrategy(prices, 24);
    
    console.log(`✓ Generated ${trades.length} trade signals`);
    console.log('');
    
    if (trades.length > 0) {
        console.log('Trade signals:');
        trades.slice(0, 5).forEach((t, i) => {
            console.log(`  ${i + 1}. ${t.timestamp.toISOString()} - ${t.action} at ${t.price.toFixed(4)}`);
            console.log(`     ${t.reason}`);
        });
        if (trades.length > 5) {
            console.log(`  ... and ${trades.length - 5} more`);
        }
        console.log('');
    }
    
    // Evaluate performance
    const results = evaluateTrades(trades, prices);
    
    console.log('='.repeat(80));
    console.log('BACKTEST RESULTS');
    console.log('='.repeat(80));
    console.log('');
    console.log(`Total Trades: ${results.totalTrades}`);
    console.log(`Win Rate: ${results.winRate.toFixed(1)}%`);
    console.log(`Average P&L per trade: ${results.avgPnlPct.toFixed(2)}%`);
    console.log(`Total P&L: ${results.totalPnlPct.toFixed(2)}%`);
    console.log('');
    
    if (results.positions.length > 0) {
        console.log('Individual trades:');
        results.positions.forEach((p, i) => {
            const status = p.open ? '(OPEN)' : '';
            const result = p.win ? '✓' : '✗';
            console.log(`  ${i + 1}. ${result} Entry: ${p.entry.toFixed(4)} → Exit: ${p.exit.toFixed(4)} | P&L: ${p.pnlPct.toFixed(2)}% | Hold: ${p.holdTime.toFixed(1)}h ${status}`);
        });
    }
    
    console.log('');
    console.log('='.repeat(80));
    console.log('ASSESSMENT');
    console.log('='.repeat(80));
    
    if (results.winRate >= 60) {
        console.log('✅ Strategy shows promise! Win rate >= 60%');
    } else if (results.winRate >= 50) {
        console.log('⚠ Strategy is marginal. Win rate 50-60%');
    } else {
        console.log('❌ Strategy underperforms. Win rate < 50%');
    }
    
    // Save results
    const report = {
        market: market.question,
        token_id: market.token_id,
        data_points: prices.length,
        period: {
            start: prices[0].timestamp,
            end: prices[prices.length - 1].timestamp
        },
        strategy: 'Mean Reversion (24h lookback, ±1.5 std)',
        results: {
            total_trades: results.totalTrades,
            win_rate: results.winRate,
            avg_pnl_pct: results.avgPnlPct,
            total_pnl_pct: results.totalPnlPct
        },
        trades: results.positions
    };
    
    fs.writeFileSync('backtest_results.json', JSON.stringify(report, null, 2));
    console.log('✓ Detailed results saved to backtest_results.json');
}

runBacktest().catch(console.error);
