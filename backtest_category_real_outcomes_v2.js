#!/usr/bin/env node
/**
 * Real Category Backtest Analysis
 * Analyzes resolved markets by category to understand outcome distributions
 * 
 * LIMITATION: We have final settlement prices (1|0) but NOT historical entry prices
 * Therefore we CANNOT validate actual win rates without historical price data
 */

const fs = require('fs');

// Category keywords
const CATEGORIES = {
    'POLITICS': [
        'election', 'senate', 'house', 'president', 'governor', 'congress',
        'democrat', 'republican', 'political', 'vote', 'poll', 'biden', 'trump',
        'ballot', 'primary', 'incumbent', 'campaign'
    ],
    'CRYPTO': [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
        'blockchain', 'token', 'defi', 'nft', 'solana', 'cardano', 'dogecoin',
        'ada', 'bnb', 'xrp', 'usdt', 'usdc'
    ],
    'SPORTS': [
        'nba', 'nfl', 'mlb', 'nhl', 'soccer', 'football', 'basketball',
        'baseball', 'hockey', 'champion', 'super bowl', 'world series',
        'finals', 'playoff', 'game', 'match', 'team', 'player', 'mvp',
        'championship', 'league', 'tournament'
    ],
    'AI/TECH': [
        'ai', 'artificial intelligence', 'gpt', 'chatgpt', 'openai',
        'tech', 'technology', 'software', 'apple', 'google', 'microsoft',
        'meta', 'amazon', 'tesla', 'nvidia', 'spacex'
    ],
    'WORLD/EVENTS': [
        'war', 'ukraine', 'russia', 'china', 'nato', 'conflict',
        'pandemic', 'covid', 'climate', 'disaster', 'weather', 'earthquake',
        'hurricane', 'wildfire', 'flood'
    ]
};

function categorizeMarket(question, description = "", title = "") {
    const text = `${question} ${description} ${title}`.toLowerCase();
    
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

function main() {
    console.log("Loading resolved markets data...");
    
    // Load resolved markets
    let marketsData = fs.readFileSync('polymarket_resolved_markets.json', 'utf-8');
    if (marketsData.charCodeAt(0) === 0xFEFF) {
        marketsData = marketsData.slice(1);
    }
    const markets = JSON.parse(marketsData);
    
    console.log(`Loaded ${markets.length} resolved markets`);
    
    // Categorize and analyze
    const categoryStats = {};
    const allMarkets = [];
    
    for (const market of markets) {
        const question = market.question || '';
        const description = market.description || '';
        const title = market.event_title || '';
        const category = categorizeMarket(question, description, title);
        
        const marketData = {
            category,
            market_id: market.market_id,
            event_title: title,
            question,
            outcomes: market.outcomes,
            winner: market.winner,
            volume: parseFloat(market.volume_num || 0),
            event_end_date: market.event_end_date
        };
        
        allMarkets.push(marketData);
        
        if (!categoryStats[category]) {
            categoryStats[category] = {
                total_markets: 0,
                total_volume: 0,
                markets: []
            };
        }
        
        categoryStats[category].total_markets++;
        categoryStats[category].total_volume += marketData.volume;
        categoryStats[category].markets.push(marketData);
    }
    
    // Calculate summary
    const results = [];
    for (const category of Object.keys(categoryStats).sort()) {
        const stats = categoryStats[category];
        
        results.push({
            category,
            total_markets: stats.total_markets,
            total_volume: stats.total_volume,
            avg_volume_per_market: stats.total_markets > 0 ? stats.total_volume / stats.total_markets : 0,
            percentage_of_total: (stats.total_markets / markets.length * 100)
        });
    }
    
    // Sort by market count
    results.sort((a, b) => b.total_markets - a.total_markets);
    
    // Calculate totals
    const totalVolume = results.reduce((sum, r) => sum + r.total_volume, 0);
    
    // Print results
    console.log("\n" + "=".repeat(90));
    console.log("RESOLVED MARKETS ANALYSIS BY CATEGORY");
    console.log("=".repeat(90));
    console.log(`\nTotal Resolved Markets: ${markets.length}`);
    console.log(`Total Volume: $${totalVolume.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}\n`);
    
    console.log(`${'Category'.padEnd(20)} ${'Markets'.padEnd(12)} ${'% of Total'.padEnd(12)} ${'Total Volume'.padEnd(20)} ${'Avg Volume'}`);
    console.log("-".repeat(90));
    
    for (const result of results) {
        console.log(
            `${result.category.padEnd(20)} ` +
            `${result.total_markets.toString().padEnd(12)} ` +
            `${result.percentage_of_total.toFixed(1).padEnd(12)}% ` +
            `$${result.total_volume.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0}).padEnd(18)} ` +
            `$${result.avg_volume_per_market.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`
        );
    }
    
    console.log("\n" + "=".repeat(90));
    console.log("❌ CANNOT VALIDATE CLAIMED WIN RATES");
    console.log("=".repeat(90));
    
    console.log("\nCLAIM: Politics = 93.5% 'strategy fit' | Crypto = 87.5% 'strategy fit'");
    console.log("\n⚠️  CRITICAL LIMITATION:");
    console.log("The resolved markets data contains only FINAL settlement prices (1|0).");
    console.log("We do NOT have historical price data during the market's lifetime.");
    console.log("\nWithout historical prices, we CANNOT:");
    console.log("  ✗ Determine which markets met entry criteria (RVR ≥2.5x)");
    console.log("  ✗ Simulate actual trade entry points");
    console.log("  ✗ Calculate real win/loss rates");
    console.log("  ✗ Validate the 93.5%/87.5% claims");
    
    console.log("\n" + "=".repeat(90));
    console.log("WHAT THE ORIGINAL 93.5%/87.5% ACTUALLY MEANT");
    console.log("=".repeat(90));
    
    console.log("\nThe original BACKTEST_CATEGORIES.md analyzed ACTIVE markets, not resolved ones.");
    console.log("\n'Strategy Fit' = % of active markets where AT LEAST ONE outcome meets:");
    console.log("  • RVR (Risk/Reward Ratio) ≥ 2.5x");
    console.log("  • ROC (Return on Capital) ≥ 10%");
    console.log("\nThis means:");
    console.log("  • 93.5% of politics markets had at least one tradeable outcome");
    console.log("  • 87.5% of crypto markets had at least one tradeable outcome");
    console.log("\n❗ STRATEGY FIT ≠ WIN RATE");
    console.log("  • Strategy fit: Can we enter? (opportunity exists)");
    console.log("  • Win rate: Did we win? (actual outcome profit/loss)");
    
    console.log("\n" + "=".repeat(90));
    console.log("DATA NEEDED FOR REAL BACKTEST");
    console.log("=".repeat(90));
    
    console.log("\nTo validate actual win rates, we need:");
    console.log("  1. Historical price snapshots (orderbook depth at multiple points)");
    console.log("  2. Entry price (price when we would have entered based on criteria)");
    console.log("  3. Exit price (final settlement: 0 or 1)");
    console.log("  4. Timing data (when did price reach entry threshold?)");
    
    console.log("\nPotential data sources:");
    console.log("  • Polymarket CLOB API (historical orderbook snapshots)");
    console.log("  • Archive.org snapshots of Polymarket pages");
    console.log("  • Gamma API historical price series (if available)");
    console.log("  • Blockchain event logs (on-chain trade data)");
    
    console.log("\n" + "=".repeat(90));
    console.log("WHAT WE CAN SAY FROM THIS DATA");
    console.log("=".repeat(90));
    
    const politics = results.find(r => r.category === 'POLITICS');
    const crypto = results.find(r => r.category === 'CRYPTO');
    const sports = results.find(r => r.category === 'SPORTS');
    
    if (politics) {
        console.log(`\n✓ POLITICS: ${politics.total_markets} resolved markets (${politics.percentage_of_total.toFixed(1)}%)`);
        console.log(`  Volume: $${politics.total_volume.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`);
    }
    
    if (crypto) {
        console.log(`\n✓ CRYPTO: ${crypto.total_markets} resolved markets (${crypto.percentage_of_total.toFixed(1)}%)`);
        console.log(`  Volume: $${crypto.total_volume.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`);
    }
    
    if (sports) {
        console.log(`\n✓ SPORTS: ${sports.total_markets} resolved markets (${sports.percentage_of_total.toFixed(1)}%)`);
        console.log(`  Volume: $${sports.total_volume.toLocaleString('en-US', {minimumFractionDigits: 0, maximumFractionDigits: 0})}`);
    }
    
    console.log("\nThese numbers show market DISTRIBUTION, not strategy performance.");
    
    // Save results
    const output = {
        summary: {
            total_markets: markets.length,
            total_volume: totalVolume,
            categories: results
        },
        limitation: "No historical price data - cannot validate win rates",
        original_claim_explanation: "93.5%/87.5% = strategy fit (entry opportunities), NOT win rate",
        all_markets: allMarkets
    };
    
    fs.writeFileSync('category_real_backtest_results.json', JSON.stringify(output, null, 2));
    
    console.log(`\n${'='.repeat(90)}`);
    console.log(`Results saved to: category_real_backtest_results.json`);
    console.log(`${'='.repeat(90)}\n`);
    
    return results;
}

main();
