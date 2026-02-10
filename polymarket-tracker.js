#!/usr/bin/env node
/**
 * POLYMARKET WHALE & BOT TRACKING SYSTEM
 * 
 * This script runs every hour to:
 * 1. Fetch latest market data from Gamma API
 * 2. Analyze trade patterns for whale activity
 * 3. Detect bot behaviors
 * 4. Track capital flows
 * 5. Update markdown reports
 * 
 * Usage: node tracker.js
 * Schedule: Run every hour during market hours
 */

const fs = require('fs');
const path = require('path');

// API Endpoints
const GAMMA_API = 'https://gamma-api.polymarket.com';
const CLOB_API = 'https://clob.polymarket.com';

// Configuration
const CONFIG = {
    whaleThreshold: 50000,      // $50K+ for whale classification
    largeOrderThreshold: 10000,  // $10K+ for large orders
    botTradeSize: 50,           // Max trade size for bot detection
    updateInterval: 3600000,    // 1 hour in ms
    marketsToTrack: 100,        // Number of markets to analyze
};

// State
let whaleWallets = new Set();
let botPatterns = new Map();
let lastUpdate = null;

/**
 * Fetch markets data from Gamma API
 */
async function fetchMarkets(limit = 100) {
    try {
        const response = await fetch(`${GAMMA_API}/markets?active=true&limit=${limit}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Error fetching markets:', error.message);
        return [];
    }
}

/**
 * Fetch CLOB market data
 */
async function fetchClobMarkets() {
    try {
        const response = await fetch(`${CLOB_API}/markets?active=true&closed=false`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        return data.data || [];
    } catch (error) {
        console.error('Error fetching CLOB markets:', error.message);
        return [];
    }
}

/**
 * Analyze markets for whale activity
 */
function analyzeWhaleActivity(markets) {
    const whales = [];
    
    for (const market of markets) {
        const volume = parseFloat(market.volume || 0);
        const volume24h = parseFloat(market.volume24hr || 0);
        const liquidity = parseFloat(market.liquidity || 0);
        
        // Whale indicators
        if (volume > 10000000) { // $10M+ total volume
            whales.push({
                market: market.question,
                slug: market.slug,
                volume: volume,
                volume24h: volume24h,
                liquidity: liquidity,
                signal: volume > 50000000 ? 'MEGA_WHALE' : 'WHALE',
                price: market.outcomePrices,
                spread: market.spread,
                oneWeekChange: market.oneWeekPriceChange
            });
        }
    }
    
    return whales.sort((a, b) => b.volume - a.volume);
}

/**
 * Detect bot patterns in activity
 */
function detectBotPatterns(markets) {
    const bots = [];
    
    for (const market of markets) {
        // High velocity + low spread = bot activity
        const volume = parseFloat(market.volume24hr || 0);
        const liquidity = parseFloat(market.liquidity || 0);
        const spread = parseFloat(market.spread || 1);
        
        if (liquidity > 0) {
            const velocity = volume / liquidity;
            
            if (velocity > 50 && spread < 0.05) {
                bots.push({
                    market: market.question,
                    velocity: velocity.toFixed(2),
                    spread: spread,
                    volume24h: volume,
                    confidence: velocity > 200 ? 'CONFIRMED' : 'LIKELY',
                    type: velocity > 100 ? 'ARBITRAGE' : 'MARKET_MAKER'
                });
            }
        }
    }
    
    return bots.sort((a, b) => b.velocity - a.velocity);
}

/**
 * Analyze capital flows
 */
function analyzeFlows(markets) {
    const flows = {
        political: { inflow: 0, outflow: 0, markets: [] },
        sports: { inflow: 0, outflow: 0, markets: [] },
        crypto: { inflow: 0, outflow: 0, markets: [] },
        other: { inflow: 0, outflow: 0, markets: [] }
    };
    
    for (const market of markets) {
        const volume24h = parseFloat(market.volume24hr || 0);
        const oneWeekVol = parseFloat(market.volume1wk || 0);
        const avgDaily = oneWeekVol / 7;
        
        const change = avgDaily > 0 ? ((volume24h - avgDaily) / avgDaily) * 100 : 0;
        
        const flow = {
            market: market.question,
            volume24h: volume24h,
            change: change.toFixed(2),
            direction: change > 20 ? 'INFLOW' : change < -20 ? 'OUTFLOW' : 'NEUTRAL'
        };
        
        // Categorize
        const category = market.category?.toLowerCase() || '';
        const question = market.question?.toLowerCase() || '';
        
        if (category.includes('politic') || question.includes('trump') || question.includes('election')) {
            flows.political.markets.push(flow);
            if (change > 20) flows.political.inflow += volume24h;
            if (change < -20) flows.political.outflow += volume24h;
        } else if (category.includes('sport') || question.includes('nba') || question.includes('nfl') || question.includes('super bowl')) {
            flows.sports.markets.push(flow);
            if (change > 20) flows.sports.inflow += volume24h;
            if (change < -20) flows.sports.outflow += volume24h;
        } else if (category.includes('crypto') || question.includes('bitcoin') || question.includes('btc') || question.includes('eth')) {
            flows.crypto.markets.push(flow);
            if (change > 20) flows.crypto.inflow += volume24h;
            if (change < -20) flows.crypto.outflow += volume24h;
        } else {
            flows.other.markets.push(flow);
            if (change > 20) flows.other.inflow += volume24h;
            if (change < -20) flows.other.outflow += volume24h;
        }
    }
    
    return flows;
}

/**
 * Generate timestamp
 */
function getTimestamp() {
    return new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';
}

/**
 * Update WHALE_ALERTS.md
 */
function updateWhaleAlerts(whales) {
    const timestamp = getTimestamp();
    
    const content = `# 🐋 WHALE ALERTS - Polymarket Smart Money Tracker

> **Last Updated:** ${timestamp}  
> **Status:** ACTIVE | Tracking ${CONFIG.marketsToTrack}+ markets

---

## 📊 CURRENT HIGH-VOLUME MARKETS (Whale Targets)

| Market | Volume | Signal Strength |
|--------|--------|-----------------|
${whales.slice(0, 10).map(w => `| ${w.market.slice(0, 50)}${w.market.length > 50 ? '...' : ''} | $${(w.volume / 1000000).toFixed(2)}M | ${w.signal === 'MEGA_WHALE' ? '🔴 MEGA' : '🟢 WHALE'} |`).join('\n')}

---

## 🚨 ACTIVE WHALE ALERTS

${whales.filter(w => w.volume24h > 10000).map(w => `
### ${w.market.slice(0, 40)}
- **Volume:** $${w.volume.toLocaleString()}
- **24h Flow:** $${w.volume24h.toLocaleString()}
- **Spread:** ${w.spread}
- **Weekly Change:** ${(w.oneWeekChange * 100).toFixed(2)}%
`).join('')}

---

## 🎯 WHALE INDICATORS

- **Mega Whales:** >$50M positions
- **Whales:** >$10M positions  
- **Dolphins:** >$1M positions

---

**Next Update:** Next hour

*This file is auto-generated by the Whale Tracking System*
`;

    fs.writeFileSync('WHALE_ALERTS.md', content);
    console.log('✅ WHALE_ALERTS.md updated');
}

/**
 * Update BOT_MIRRORING.md
 */
function updateBotMirroring(bots) {
    const timestamp = getTimestamp();
    
    const content = `# 🤖 BOT MIRRORING - Automated Strategy Replication

> **Last Updated:** ${timestamp}  
> **Active Bots Detected:** ${bots.length}

---

## 🤖 DETECTED BOT ACTIVITY

| Market | Velocity | Type | Confidence |
|--------|----------|------|------------|
${bots.slice(0, 15).map(b => `| ${b.market.slice(0, 40)}${b.market.length > 40 ? '...' : ''} | ${b.velocity}x | ${b.type} | ${b.confidence} |`).join('\n')}

---

## 📊 BOT METRICS

**High Velocity Markets (Bot Active):**
${bots.filter(b => parseFloat(b.velocity) > 100).map(b => `- ${b.market.slice(0, 50)}: ${b.velocity}x velocity`).join('\n')}

---

*This file is auto-generated by the Bot Detection System*
`;

    fs.writeFileSync('BOT_MIRRORING.md', content);
    console.log('✅ BOT_MIRRORING.md updated');
}

/**
 * Update FLOW_ANALYSIS.md
 */
function updateFlowAnalysis(flows) {
    const timestamp = getTimestamp();
    
    const politicalNet = flows.political.inflow - flows.political.outflow;
    const sportsNet = flows.sports.inflow - flows.sports.outflow;
    const cryptoNet = flows.crypto.inflow - flows.crypto.outflow;
    
    const content = `# 💰 FLOW ANALYSIS - Capital Movement Tracker

> **Last Updated:** ${timestamp}

---

## 📈 CATEGORY FLOWS (24h)

| Category | Inflow | Outflow | Net Flow |
|----------|--------|---------|----------|
| Political | $${flows.political.inflow.toLocaleString()} | $${flows.political.outflow.toLocaleString()} | ${politicalNet >= 0 ? '🟢' : '🔴'} $${Math.abs(politicalNet).toLocaleString()} |
| Sports | $${flows.sports.inflow.toLocaleString()} | $${flows.sports.outflow.toLocaleString()} | ${sportsNet >= 0 ? '🟢' : '🔴'} $${Math.abs(sportsNet).toLocaleString()} |
| Crypto | $${flows.crypto.inflow.toLocaleString()} | $${flows.crypto.outflow.toLocaleString()} | ${cryptoNet >= 0 ? '🟢' : '🔴'} $${Math.abs(cryptoNet).toLocaleString()} |

---

## 🌊 TOP FLOWING MARKETS

### Political Markets
${flows.political.markets.slice(0, 5).map(m => `- ${m.market.slice(0, 50)}: ${m.direction} (${m.change}%)`).join('\n')}

### Sports Markets  
${flows.sports.markets.slice(0, 5).map(m => `- ${m.market.slice(0, 50)}: ${m.direction} (${m.change}%)`).join('\n')}

### Crypto Markets
${flows.crypto.markets.slice(0, 5).map(m => `- ${m.market.slice(0, 50)}: ${m.direction} (${m.change}%)`).join('\n')}

---

*This file is auto-generated by the Flow Analysis System*
`;

    fs.writeFileSync('FLOW_ANALYSIS.md', content);
    console.log('✅ FLOW_ANALYSIS.md updated');
}

/**
 * Main tracking loop
 */
async function runTracker() {
    console.log('\n🔍 Starting Polymarket Whale & Bot Tracker...');
    console.log(`⏰ ${getTimestamp()}\n`);
    
    try {
        // Fetch data
        console.log('📡 Fetching market data...');
        const markets = await fetchMarkets(CONFIG.marketsToTrack);
        const clobMarkets = await fetchClobMarkets();
        
        console.log(`✅ Fetched ${markets.length} markets from Gamma API`);
        console.log(`✅ Fetched ${clobMarkets.length} markets from CLOB API`);
        
        // Analyze
        console.log('\n🐋 Analyzing whale activity...');
        const whales = analyzeWhaleActivity(markets);
        console.log(`   Found ${whales.length} whale markets`);
        
        console.log('\n🤖 Detecting bot patterns...');
        const bots = detectBotPatterns(markets);
        console.log(`   Found ${bots.length} bot-active markets`);
        
        console.log('\n💰 Analyzing capital flows...');
        const flows = analyzeFlows(markets);
        
        // Update files
        console.log('\n📝 Updating reports...');
        updateWhaleAlerts(whales);
        updateBotMirroring(bots);
        updateFlowAnalysis(flows);
        
        lastUpdate = new Date();
        console.log(`\n✅ Tracking complete at ${getTimestamp()}`);
        console.log('⏳ Next update in 1 hour\n');
        
    } catch (error) {
        console.error('❌ Tracker error:', error.message);
    }
}

// Run immediately if executed directly
if (require.main === module) {
    runTracker();
}

// Export for module use
module.exports = { runTracker, fetchMarkets, analyzeWhaleActivity };
