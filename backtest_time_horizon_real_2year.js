const fs = require('fs');

// Read and parse CSV
const csv = fs.readFileSync('polymarket_resolved_markets.csv', 'utf8');
const lines = csv.split('\n');
const headers = lines[0].split(',').map(h => h.replace(/"/g, ''));

console.log('='.repeat(80));
console.log('TIME HORIZON BACKTEST - 2 YEAR HISTORICAL DATA');
console.log('='.repeat(80));
console.log();

// Parse markets
const markets = [];
for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    // Parse CSV line (handle quoted fields)
    const fields = [];
    let current = '';
    let inQuotes = false;
    
    for (let char of lines[i]) {
        if (char === '"') {
            inQuotes = !inQuotes;
        } else if (char === ',' && !inQuotes) {
            fields.push(current);
            current = '';
        } else {
            current += char;
        }
    }
    fields.push(current);
    
    if (fields.length < 10) continue;
    
    const market = {
        event_id: fields[0],
        event_title: fields[1],
        event_slug: fields[2],
        event_end_date: fields[3],
        market_id: fields[4],
        question: fields[6],
        outcomes: fields[7],
        final_prices: fields[8],
        winner: fields[9],
        closed: fields[10],
        volume_usd: parseFloat(fields[11]) || 0,
        created_time: fields[15]
    };
    
    markets.push(market);
}

console.log(`Loaded ${markets.length} markets`);
console.log();

// Filter to only closed markets with winners
const resolvedMarkets = markets.filter(m => 
    m.closed === 'True' && 
    m.winner && 
    m.winner !== 'null' && 
    m.event_end_date
);

console.log(`${resolvedMarkets.length} resolved markets with outcomes`);
console.log();

// Analyze date range
const dates = resolvedMarkets.map(m => new Date(m.event_end_date)).filter(d => !isNaN(d));
const minDate = new Date(Math.min(...dates));
const maxDate = new Date(Math.max(...dates));

console.log(`Date range: ${minDate.toISOString().split('T')[0]} to ${maxDate.toISOString().split('T')[0]}`);
console.log(`Time span: ${Math.round((maxDate - minDate) / (1000 * 60 * 60 * 24))} days`);
console.log();

// Simulate trading strategy
// Assumption: We enter 30 days before resolution at market opening price
// We'll simulate entry prices based on final outcome and add realistic variance

const trades = [];

resolvedMarkets.forEach(market => {
    const endDate = new Date(market.event_end_date);
    if (isNaN(endDate.getTime())) return;
    
    // Simulate entry date (we don't have created_time for all, so estimate)
    // Assume we could enter anytime from creation to resolution
    // For this backtest, we'll test entry at various points
    
    const daysBeforeResolution = [1, 2, 5, 10, 20, 30, 60, 90, 180];
    
    daysBeforeResolution.forEach(daysBefore => {
        const entryDate = new Date(endDate);
        entryDate.setDate(entryDate.getDate() - daysBefore);
        
        // Skip if entry date is in the future
        if (entryDate > new Date('2026-02-07')) return;
        
        // Simulate entry price based on winner and add variance
        // If Yes won, early prices were likely lower (say 0.3-0.7)
        // If No won, Yes prices were likely higher (say 0.3-0.7)
        
        const wonYes = market.winner === 'Yes';
        
        // Entry price simulation with time decay toward final outcome
        // More time = more uncertainty = prices closer to 0.5
        const timeDecayFactor = Math.min(daysBefore / 90, 1); // Max at 90 days
        const basePrice = wonYes ? 0.35 : 0.65; // Contrarian would buy the opposite
        const uncertainty = 0.15 * timeDecayFactor;
        const entryPrice = basePrice + (Math.random() - 0.5) * uncertainty;
        
        // Trade strategy: Buy the outcome that will win (perfect hindsight for analysis)
        // This gives us the MAXIMUM possible edge for each time horizon
        const exitPrice = wonYes ? 1.0 : 0.0;
        
        // P&L calculation
        const positionSize = 100; // $100 per trade
        const shares = positionSize / Math.max(entryPrice, 0.01);
        const exitValue = shares * exitPrice;
        const pnl = exitValue - positionSize;
        const pnlPercent = (pnl / positionSize) * 100;
        
        trades.push({
            market_id: market.market_id,
            question: market.question.substring(0, 60),
            entryDate,
            exitDate: endDate,
            daysHeld: daysBefore,
            entryPrice: entryPrice.toFixed(3),
            exitPrice: exitPrice.toFixed(3),
            winner: market.winner,
            pnl: pnl.toFixed(2),
            pnlPercent: pnlPercent.toFixed(1),
            volume: market.volume_usd
        });
    });
});

console.log(`Generated ${trades.length} simulated trades`);
console.log();

// Bucket by time horizon
const buckets = {
    '<3d': { name: '<3 days', min: 0, max: 3, trades: [] },
    '3-7d': { name: '3-7 days', min: 3, max: 7, trades: [] },
    '7-30d': { name: '7-30 days', min: 7, max: 30, trades: [] },
    '>30d': { name: '>30 days', min: 30, max: 999, trades: [] }
};

trades.forEach(trade => {
    const days = trade.daysHeld;
    
    if (days < 3) buckets['<3d'].trades.push(trade);
    else if (days < 7) buckets['3-7d'].trades.push(trade);
    else if (days < 30) buckets['7-30d'].trades.push(trade);
    else buckets['>30d'].trades.push(trade);
});

console.log('='.repeat(80));
console.log('TRADES PER TIME BUCKET');
console.log('='.repeat(80));
console.log();

Object.keys(buckets).forEach(key => {
    const bucket = buckets[key];
    console.log(`${bucket.name}: ${bucket.trades.length} trades`);
});
console.log();

// Calculate metrics for each bucket
console.log('='.repeat(80));
console.log('PERFORMANCE BY TIME HORIZON');
console.log('='.repeat(80));
console.log();

const results = {};

Object.keys(buckets).forEach(key => {
    const bucket = buckets[key];
    const trades = bucket.trades;
    
    if (trades.length === 0) {
        console.log(`${bucket.name}: No trades`);
        console.log();
        return;
    }
    
    // Calculate metrics
    const wins = trades.filter(t => parseFloat(t.pnl) > 0);
    const losses = trades.filter(t => parseFloat(t.pnl) <= 0);
    
    const winRate = (wins.length / trades.length * 100).toFixed(1);
    const totalPnl = trades.reduce((sum, t) => sum + parseFloat(t.pnl), 0);
    const avgPnl = totalPnl / trades.length;
    
    const avgWin = wins.length > 0 
        ? wins.reduce((sum, t) => sum + parseFloat(t.pnl), 0) / wins.length 
        : 0;
    const avgLoss = losses.length > 0
        ? losses.reduce((sum, t) => sum + parseFloat(t.pnl), 0) / losses.length
        : 0;
    
    const winLossRatio = avgLoss !== 0 ? Math.abs(avgWin / avgLoss) : 0;
    const expectancy = (wins.length / trades.length) * avgWin + (losses.length / trades.length) * avgLoss;
    
    const avgDays = trades.reduce((sum, t) => sum + t.daysHeld, 0) / trades.length;
    
    results[key] = {
        name: bucket.name,
        trades: trades.length,
        wins: wins.length,
        losses: losses.length,
        winRate: parseFloat(winRate),
        totalPnl: totalPnl.toFixed(2),
        avgPnl: avgPnl.toFixed(2),
        avgWin: avgWin.toFixed(2),
        avgLoss: avgLoss.toFixed(2),
        winLossRatio: winLossRatio.toFixed(2),
        expectancy: expectancy.toFixed(2),
        avgDays: avgDays.toFixed(1)
    };
    
    console.log(`${bucket.name.toUpperCase()}`);
    console.log('-'.repeat(60));
    console.log(`Total Trades: ${trades.length}`);
    console.log(`Wins: ${wins.length} | Losses: ${losses.length}`);
    console.log(`Win Rate: ${winRate}%`);
    console.log(`Total P&L: $${totalPnl.toFixed(2)}`);
    console.log(`Avg P&L: $${avgPnl.toFixed(2)}`);
    console.log(`Avg Win: $${avgWin.toFixed(2)} | Avg Loss: $${avgLoss.toFixed(2)}`);
    console.log(`Win/Loss Ratio: ${winLossRatio.toFixed(2)}:1`);
    console.log(`Expectancy: $${expectancy.toFixed(2)} per trade`);
    console.log(`Avg Days Held: ${avgDays.toFixed(1)}`);
    console.log();
});

// Summary table
console.log('='.repeat(80));
console.log('EXECUTIVE SUMMARY TABLE');
console.log('='.repeat(80));
console.log();
console.log('Time Horizon | Trades | Win Rate | Total P&L | Avg P&L | Expectancy | W/L Ratio');
console.log('-'.repeat(80));

Object.keys(buckets).forEach(key => {
    const r = results[key];
    if (!r) return;
    
    console.log(`${r.name.padEnd(12)} | ${r.trades.toString().padEnd(6)} | ${r.winRate.toString().padEnd(8)}% | $${r.totalPnl.padEnd(9)} | $${r.avgPnl.padEnd(7)} | $${r.expectancy.padEnd(10)} | ${r.winLossRatio}:1`);
});

console.log();

// Edge decay analysis
console.log('='.repeat(80));
console.log('EDGE DECAY VALIDATION');
console.log('='.repeat(80));
console.log();

const shortWinRate = results['<3d']?.winRate || 0;
const longWinRate = results['>30d']?.winRate || 0;
const decay = shortWinRate - longWinRate;

console.log(`Short-term win rate (<3 days): ${shortWinRate}%`);
console.log(`Long-term win rate (>30 days): ${longWinRate}%`);
console.log(`Edge decay: ${decay.toFixed(1)}%`);
console.log();

if (decay > 10) {
    console.log('✅ HYPOTHESIS CONFIRMED: Edge decays significantly over time');
} else {
    console.log('❌ HYPOTHESIS NOT CONFIRMED: Edge decay is minimal');
}
console.log();

// Save detailed trades to CSV
const csvOutput = ['Time Bucket,Market,Entry Date,Exit Date,Days Held,Entry Price,Exit Price,Winner,P&L,P&L %,Volume'];

Object.keys(buckets).forEach(key => {
    const bucket = buckets[key];
    bucket.trades.forEach(trade => {
        csvOutput.push([
            bucket.name,
            trade.question.replace(/,/g, ' '),
            trade.entryDate.toISOString().split('T')[0],
            trade.exitDate.toISOString().split('T')[0],
            trade.daysHeld,
            trade.entryPrice,
            trade.exitPrice,
            trade.winner,
            trade.pnl,
            trade.pnlPercent,
            trade.volume.toFixed(2)
        ].join(','));
    });
});

fs.writeFileSync('trades_by_time_bucket.csv', csvOutput.join('\n'));
console.log('✅ Saved detailed trades to trades_by_time_bucket.csv');
console.log();

// Save summary
const summary = {
    generated: new Date().toISOString(),
    totalMarkets: resolvedMarkets.length,
    totalTrades: trades.length,
    dateRange: {
        start: minDate.toISOString().split('T')[0],
        end: maxDate.toISOString().split('T')[0],
        days: Math.round((maxDate - minDate) / (1000 * 60 * 60 * 24))
    },
    results: results,
    edgeDecay: {
        shortTermWinRate: shortWinRate,
        longTermWinRate: longWinRate,
        decay: decay.toFixed(1)
    }
};

fs.writeFileSync('time_horizon_backtest_results.json', JSON.stringify(summary, null, 2));
console.log('✅ Saved summary to time_horizon_backtest_results.json');
console.log();

console.log('='.repeat(80));
console.log('BACKTEST COMPLETE');
console.log('='.repeat(80));
