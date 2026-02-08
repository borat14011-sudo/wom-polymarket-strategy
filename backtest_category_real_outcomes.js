#!/usr/bin/env node
/**
 * Real Category Backtest - Using Actual Resolved Market Outcomes
 * Validates the 93.5% politics / 87.5% crypto "strategy fit" claims
 */

const fs = require('fs');

// Strategy parameters
const MIN_RVR = 2.5;  // Minimum risk/reward ratio
const MIN_ROC = 0.10;  // Minimum return on capital (10%)

// Category keywords
const CATEGORIES = {
    'POLITICS': [
        'election', 'senate', 'house', 'president', 'governor', 'congress',
        'democrat', 'republican', 'political', 'vote', 'poll', 'biden', 'trump'
    ],
    'CRYPTO': [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
        'blockchain', 'token', 'defi', 'nft', 'solana', 'cardano'
    ],
    'SPORTS': [
        'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball',
        'baseball', 'hockey', 'champion', 'super bowl', 'world series',
        'finals', 'playoff', 'game', 'match', 'team', 'player'
    ],
    'AI/TECH': [
        'ai', 'artificial intelligence', 'gpt', 'chatgpt', 'openai',
        'tech', 'technology', 'software', 'apple', 'google', 'microsoft',
        'meta', 'amazon', 'tesla'
    ],
    'WORLD/EVENTS': [
        'war', 'ukraine', 'russia', 'china', 'nato', 'conflict',
        'pandemic', 'covid', 'climate', 'disaster', 'weather'
    ]
};

function categorizeMarket(question, description = "") {
    const text = `${question} ${description}`.toLowerCase();
    
    const categoryScores = {};
    for (const [category, keywords] of Object.entries(CATEGORIES)) {
        categoryScores[category] = 0;
        for (const keyword of keywords) {
            if (text.includes(keyword.toLowerCase())) {
                categoryScores[category]++;
            }
        }
    }
    
    const maxCategory = Object.entries(categoryScores)
        .filter(([_, score]) => score > 0)
        .sort((a, b) => b[1] - a[1])[0];
    
    return maxCategory ? maxCategory[0] : 'OTHER';
}

function calculateEntrySignal(price) {
    if (price <= 0 || price >= 1) {
        return { qualifies: false, rvr: 0, roc: 0 };
    }
    
    const rvr = (1 - price) / price;
    const roc = (1 - price) / price;
    
    const qualifies = rvr >= MIN_RVR && roc >= MIN_ROC;
    return { qualifies, rvr, roc };
}

function analyzeMarketTrade(market) {
    const question = market.question || '';
    const description = market.description || '';
    const outcomes = (market.outcomes || '').split('|');
    const finalPricesStr = market.final_prices || '';
    const winner = market.winner || '';
    
    if (!finalPricesStr || !winner) {
        return null;
    }
    
    let finalPrices;
    try {
        finalPrices = finalPricesStr.split('|').map(p => parseFloat(p));
    } catch (e) {
        return null;
    }
    
    if (outcomes.length !== finalPrices.length) {
        return null;
    }
    
    const category = categorizeMarket(question, description);
    
    const trades = [];
    for (let i = 0; i < outcomes.length; i++) {
        const outcome = outcomes[i];
        const finalPrice = finalPrices[i];
        
        const { qualifies, rvr, roc } = calculateEntrySignal(finalPrice);
        
        if (qualifies) {
            const won = (outcome === winner && finalPrice === 1.0) || 
                       (outcome !== winner && finalPrice === 0.0);
            
            trades.push({
                category,
                market_id: market.market_id,
                question,
                outcome,
                final_price: finalPrice,
                rvr,
                roc,
                winner,
                won,
                volume: parseFloat(market.volume_num || 0)
            });
        }
    }
    
    return trades;
}

function main() {
    console.log("Loading resolved markets data...");
    
    // Load resolved markets (strip BOM if present)
    let marketsData = fs.readFileSync('polymarket_resolved_markets.json', 'utf-8');
    // Remove BOM if present
    if (marketsData.charCodeAt(0) === 0xFEFF) {
        marketsData = marketsData.slice(1);
    }
    const markets = JSON.parse(marketsData);
    
    console.log(`Loaded ${markets.length} resolved markets`);
    
    // Analyze all markets
    const allTrades = [];
    for (const market of markets) {
        const trades = analyzeMarketTrade(market);
        if (trades) {
            allTrades.push(...trades);
        }
    }
    
    console.log(`Found ${allTrades.length} qualifying trades across all markets`);
    
    // Group by category
    const categoryStats = {};
    
    for (const trade of allTrades) {
        const cat = trade.category;
        if (!categoryStats[cat]) {
            categoryStats[cat] = {
                total_trades: 0,
                winning_trades: 0,
                total_volume: 0,
                winning_volume: 0,
                trades: []
            };
        }
        
        categoryStats[cat].total_trades++;
        categoryStats[cat].total_volume += trade.volume;
        categoryStats[cat].trades.push(trade);
        
        if (trade.won) {
            categoryStats[cat].winning_trades++;
            categoryStats[cat].winning_volume += trade.volume;
        }
    }
    
    // Calculate win rates
    const results = [];
    for (const category of Object.keys(categoryStats).sort()) {
        const stats = categoryStats[category];
        const total = stats.total_trades;
        const wins = stats.winning_trades;
        const winRate = total > 0 ? (wins / total * 100) : 0;
        
        results.push({
            category,
            total_trades: total,
            winning_trades: wins,
            losing_trades: total - wins,
            win_rate: winRate,
            total_volume: stats.total_volume,
            avg_volume_per_trade: total > 0 ? stats.total_volume / total : 0
        });
    }
    
    // Sort by win rate
    results.sort((a, b) => b.win_rate - a.win_rate);
    
    // Print results
    console.log("\n" + "=".repeat(80));
    console.log("REAL CATEGORY BACKTEST RESULTS");
    console.log("=".repeat(80));
    console.log(`\nStrategy: RVR >= ${MIN_RVR}x, ROC >= ${MIN_ROC*100}%`);
    console.log(`Data: ${markets.length} resolved Polymarket markets\n`);
    
    console.log(`${'Category'.padEnd(20)} ${'Trades'.padEnd(10)} ${'Wins'.padEnd(10)} ${'Losses'.padEnd(10)} ${'Win Rate'.padEnd(15)}`);
    console.log("-".repeat(80));
    
    for (const result of results) {
        console.log(
            `${result.category.padEnd(20)} ` +
            `${result.total_trades.toString().padEnd(10)} ` +
            `${result.winning_trades.toString().padEnd(10)} ` +
            `${result.losing_trades.toString().padEnd(10)} ` +
            `${result.win_rate.toFixed(1)}%`
        );
    }
    
    console.log("\n" + "=".repeat(80));
    console.log("VALIDATION OF CLAIMS");
    console.log("=".repeat(80));
    
    // Find politics and crypto results
    const politics = results.find(r => r.category === 'POLITICS');
    const crypto = results.find(r => r.category === 'CRYPTO');
    
    console.log(`\nCLAIM: Politics = 93.5% 'strategy fit'`);
    if (politics) {
        console.log(`REALITY: Politics = ${politics.win_rate.toFixed(1)}% WIN RATE (${politics.winning_trades}/${politics.total_trades} trades)`);
        console.log(`NOTE: Original 93.5% was % of markets meeting ENTRY criteria, not win rate!`);
    } else {
        console.log("REALITY: No politics trades found");
    }
    
    console.log(`\nCLAIM: Crypto = 87.5% 'strategy fit'`);
    if (crypto) {
        console.log(`REALITY: Crypto = ${crypto.win_rate.toFixed(1)}% WIN RATE (${crypto.winning_trades}/${crypto.total_trades} trades)`);
        console.log(`NOTE: Original 87.5% was % of markets meeting ENTRY criteria, not win rate!`);
    } else {
        console.log("REALITY: No crypto trades found");
    }
    
    console.log("\n" + "=".repeat(80));
    console.log("KEY INSIGHT");
    console.log("=".repeat(80));
    console.log("\nThe original analysis measured 'strategy fit' = % of markets meeting entry criteria");
    console.log("This analysis measures ACTUAL WIN RATE = % of qualifying trades that won");
    console.log("\nThese are VERY different metrics!");
    console.log("- Strategy fit: Can we enter this market? (yes/no)");
    console.log("- Win rate: Did we profit from this trade? (win/loss)");
    
    // Save detailed results
    const output = {
        summary: results,
        all_trades: allTrades,
        parameters: {
            min_rvr: MIN_RVR,
            min_roc: MIN_ROC,
            total_markets: markets.length,
            total_qualifying_trades: allTrades.length
        }
    };
    
    fs.writeFileSync('category_real_backtest_results.json', JSON.stringify(output, null, 2));
    
    console.log(`\nDetailed results saved to: category_real_backtest_results.json`);
    
    return results;
}

main();
