const https = require('https');
const fs = require('fs');

async function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
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

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchResolvedMarketsJanuary2026() {
    const baseUrl = "https://gamma-api.polymarket.com/markets";
    const allMarkets = [];
    let offset = 0;
    const limit = 100;
    
    const janStart = new Date('2026-01-01T00:00:00Z');
    const janEnd = new Date('2026-02-01T00:00:00Z');
    
    console.log("Fetching resolved markets from January 2026...");
    
    while (true) {
        const url = `${baseUrl}?closed=true&limit=${limit}&offset=${offset}`;
        
        try {
            const markets = await fetchUrl(url);
            
            if (!markets || markets.length === 0) {
                console.log(`No more markets found at offset ${offset}`);
                break;
            }
            
            console.log(`Fetched ${markets.length} markets at offset ${offset}`);
            
            for (const market of markets) {
                if (market.closedTime) {
                    try {
                        let closedTimeStr = market.closedTime;
                        if (closedTimeStr.includes('+')) {
                            closedTimeStr = closedTimeStr.split('+')[0];
                        }
                        if (closedTimeStr.includes('.')) {
                            closedTimeStr = closedTimeStr.split('.')[0];
                        }
                        
                        const closedTime = new Date(closedTimeStr.trim() + 'Z');
                        
                        if (closedTime >= janStart && closedTime < janEnd) {
                            allMarkets.push(market);
                            const questionPreview = (market.question || 'Unknown').substring(0, 60);
                            console.log(`  ✓ Found January 2026 market: ${questionPreview}...`);
                        }
                    } catch (e) {
                        // Skip if we can't parse the date
                    }
                }
            }
            
            // Check if we should continue
            let newestClosed = null;
            for (const m of markets) {
                if (m.closedTime) {
                    try {
                        let ctStr = m.closedTime.split('+')[0].split('.')[0].trim();
                        const ct = new Date(ctStr + 'Z');
                        if (!newestClosed || ct > newestClosed) {
                            newestClosed = ct;
                        }
                    } catch (e) {}
                }
            }
            
            if (newestClosed && newestClosed < new Date('2025-12-01T00:00:00Z')) {
                console.log('Reached markets before December 2025, stopping...');
                break;
            }
            
            offset += limit;
            await sleep(500); // Be nice to the API
            
        } catch (error) {
            console.error(`Error fetching markets at offset ${offset}:`, error.message);
            break;
        }
    }
    
    return allMarkets;
}

function extractOutcome(market) {
    try {
        const outcomes = typeof market.outcomes === 'string' 
            ? JSON.parse(market.outcomes) 
            : market.outcomes;
        
        const prices = typeof market.outcomePrices === 'string' 
            ? JSON.parse(market.outcomePrices) 
            : market.outcomePrices;
        
        if (outcomes && prices && outcomes.length === prices.length) {
            const priceFloats = prices.map(p => parseFloat(p));
            const maxPrice = Math.max(...priceFloats);
            
            if (maxPrice > 0.9) {
                const winnerIdx = priceFloats.indexOf(maxPrice);
                return outcomes[winnerIdx];
            }
        }
    } catch (e) {}
    
    return "Resolved (outcome TBD)";
}

function saveToCsv(markets, filename = "jan_2026_resolved.csv") {
    if (!markets || markets.length === 0) {
        console.log("No markets found for January 2026!");
        return;
    }
    
    console.log(`\nSaving ${markets.length} markets to ${filename}...`);
    
    const headers = 'question,outcome,category,resolution_date,volume\n';
    const rows = markets.map(market => {
        const question = (market.question || 'Unknown').replace(/"/g, '""');
        const outcome = extractOutcome(market).replace(/"/g, '""');
        const category = (market.category || 'Unknown').replace(/"/g, '""');
        const volume = market.volume || '0';
        
        let resolutionDate = market.closedTime || 'Unknown';
        try {
            if (market.closedTime && market.closedTime !== 'Unknown') {
                const ctStr = market.closedTime.split('+')[0].split('.')[0].trim();
                const dt = new Date(ctStr + 'Z');
                resolutionDate = dt.toISOString().replace('T', ' ').replace('Z', '').substring(0, 19);
            }
        } catch (e) {}
        
        return `"${question}","${outcome}","${category}","${resolutionDate}","${volume}"`;
    }).join('\n');
    
    fs.writeFileSync(filename, headers + rows);
    console.log(`✓ Successfully saved ${markets.length} markets to ${filename}`);
}

async function main() {
    const markets = await fetchResolvedMarketsJanuary2026();
    console.log(`\nTotal markets found in January 2026: ${markets.length}`);
    saveToCsv(markets);
}

main().catch(console.error);
