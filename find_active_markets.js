#!/usr/bin/env node
const https = require('https');

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

async function findActiveMarkets() {
    console.log("Finding active markets with recent end dates...\n");
    
    const result = await httpGet('https://clob.polymarket.com/markets');
    const markets = result.data.data || result.data;
    
    console.log(`Total markets: ${markets.length}`);
    
    // Filter for:
    // 1. Active markets
    // 2. Not closed
    // 3. Recent end date (2025 or later)
    // 4. Has tokens
    
    const activeMarkets = markets.filter(m => {
        if (!m.tokens || m.tokens.length === 0) return false;
        if (m.closed === true) return false;
        if (m.active === false) return false;
        
        // Check end date if available
        if (m.end_date_iso) {
            const endDate = new Date(m.end_date_iso);
            const cutoff = new Date('2025-01-01');
            if (endDate < cutoff) return false;
        }
        
        // Check question doesn't contain old years
        const question = m.question || '';
        if (question.match(/\b202[0-4]\b/)) return false;
        
        return true;
    });
    
    console.log(`Active 2025+ markets: ${activeMarkets.length}\n`);
    
    // Show first 10
    console.log("Top 10 active markets:");
    for (let i = 0; i < Math.min(10, activeMarkets.length); i++) {
        const m = activeMarkets[i];
        const token = m.tokens[0];
        console.log(`${i + 1}. ${token.outcome}: ${m.question.substring(0, 80)}`);
        console.log(`   Token ID: ${token.token_id}`);
        console.log(`   End: ${m.end_date_iso || 'N/A'}`);
        console.log(`   Active: ${m.active}, Closed: ${m.closed}`);
        console.log('');
    }
    
    return activeMarkets.slice(0, 5);
}

findActiveMarkets().catch(console.error);
