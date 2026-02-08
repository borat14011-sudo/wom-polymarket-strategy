#!/usr/bin/env node
const https = require('https');
const fs = require('fs');

function fetchJSON(hostname, path) {
    return new Promise((resolve) => {
        https.get({
            hostname: hostname,
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' }
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    resolve(null);
                }
            });
        }).on('error', () => resolve(null));
    });
}

async function scrapeCLOB() {
    console.log('='.repeat(70));
    console.log('SCRAPING POLYMARKET OCTOBER 2025 MARKETS VIA CLOB API');
    console.log('='.repeat(70));
    console.log();
    
    const allMarkets = [];
    const seenIds = new Set();
    let cursor = '';
    let fetchCount = 0;
    const maxFetches = 100;
    
    while (fetchCount < maxFetches) {
        const path = cursor ? `/markets?next_cursor=${encodeURIComponent(cursor)}` : '/markets';
        console.log(`Fetch #${fetchCount + 1}: ${path.substring(0, 60)}...`);
        
        const response = await fetchJSON('clob.polymarket.com', path);
        
        if (!response || !response.data) {
            console.log('No more data');
            break;
        }
        
        const markets = response.data;
        console.log(`  Got ${markets.length} markets`);
        
        let oct2025Count = 0;
        
        for (const market of markets) {
            const marketId = market.condition_id || market.id;
            
            if (!marketId || seenIds.has(marketId)) continue;
            
            // Check if market has October 2025 end date
            const endDate = market.end_date_iso || market.end_date;
            
            if (endDate) {
                const date = new Date(endDate);
                if (date.getFullYear() === 2025 && date.getMonth() === 9) {
                    seenIds.add(marketId);
                    
                    // Extract outcome from tokens
                    let outcome = 'UNKNOWN';
                    if (market.closed || market.resolved) {
                        if (market.outcome) {
                            outcome = market.outcome;
                        } else if (market.tokens && market.tokens.length === 2) {
                            const token0 = market.tokens[0];
                            const token1 = market.tokens[1];
                            
                            // Check final prices
                            if (token0.price && parseFloat(token0.price) > 0.98) {
                                outcome = token0.outcome || 'YES';
                            } else if (token1.price && parseFloat(token1.price) > 0.98) {
                                outcome = token1.outcome || 'NO';
                            }
                        }
                    }
                    
                    allMarkets.push({
                        question: market.question || '',
                        outcome: outcome,
                        category: market.category || market.group_item_title || '',
                        resolution_date: endDate,
                        volume: parseFloat(market.volume || market.volume_num || 0),
                        market_id: marketId,
                        closed: market.closed || false
                    });
                    
                    oct2025Count++;
                }
            }
        }
        
        if (oct2025Count > 0) {
            console.log(`  ✓ Found ${oct2025Count} October 2025 markets!`);
        }
        
        // Check for next page
        if (response.next_cursor) {
            cursor = response.next_cursor;
        } else {
            console.log('No more pages');
            break;
        }
        
        fetchCount++;
        await new Promise(r => setTimeout(r, 300));
        
        // Early exit if we have enough
        if (allMarkets.length > 150) {
            console.log(`\nEarly exit - collected ${allMarkets.length} markets`);
            break;
        }
    }
    
    console.log(`\n${'='.repeat(70)}`);
    console.log(`TOTAL OCTOBER 2025 MARKETS: ${allMarkets.length}`);
    console.log('='.repeat(70));
    
    if (allMarkets.length > 0) {
        // Save to CSV
        const header = 'question,outcome,category,resolution_date,volume,market_id,closed\n';
        const rows = allMarkets.map(m => {
            const q = (m.question || '').replace(/"/g, '""');
            const o = (m.outcome || '').replace(/"/g, '""');
            const c = (m.category || '').replace(/"/g, '""');
            return `"${q}","${o}","${c}","${m.resolution_date}",${m.volume},"${m.market_id}",${m.closed}`;
        }).join('\n');
        
        fs.writeFileSync('oct_2025_resolved.csv', header + rows, 'utf8');
        console.log(`\n✓ Saved to oct_2025_resolved.csv`);
        
        // Stats
        console.log(`\nSTATISTICS:`);
        console.log(`  Total markets: ${allMarkets.length}`);
        console.log(`  Closed: ${allMarkets.filter(m => m.closed).length}`);
        console.log(`  With outcomes: ${allMarkets.filter(m => m.outcome && m.outcome !== 'UNKNOWN').length}`);
        
        const totalVol = allMarkets.reduce((s, m) => s + m.volume, 0);
        console.log(`  Total volume: $${totalVol.toLocaleString('en-US', {maximumFractionDigits: 0})}`);
        
        console.log(`\nTOP 10 BY VOLUME:`);
        allMarkets
            .sort((a, b) => b.volume - a.volume)
            .slice(0, 10)
            .forEach((m, i) => {
                console.log(`${i + 1}. ${m.question.substring(0, 55)}...`);
                console.log(`   Volume: $${m.volume.toLocaleString('en-US')} | Outcome: ${m.outcome} | Closed: ${m.closed}`);
            });
    }
}

scrapeCLOB().catch(console.error);
