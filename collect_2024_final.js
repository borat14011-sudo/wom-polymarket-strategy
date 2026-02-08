const https = require('https');
const sqlite3 = require('better-sqlite3');

const DB = 'historical_2024.db';

// Initialize database
const db = new sqlite3(DB);
db.exec(`CREATE TABLE IF NOT EXISTS markets (market_id TEXT PRIMARY KEY, question TEXT, volume REAL, end_date TEXT, tokens TEXT)`);
db.exec(`CREATE TABLE IF NOT EXISTS price_history (id INTEGER PRIMARY KEY AUTOINCREMENT, market_id TEXT, token_id TEXT, timestamp INTEGER, price REAL)`);
db.exec(`CREATE INDEX IF NOT EXISTS idx_mkt ON price_history(market_id, timestamp)`);

console.log('\n' + '='.repeat(70));
console.log('POLYMARKET 2024 PRICE HISTORY COLLECTOR');
console.log('='.repeat(70) + '\n');

// The 18 markets we found from 2024
const MARKETS_2024 = [
    { id: '240613', question: 'Which party wins 2024 US Presidential Election?', volume: 8828319.28 },
    { id: '240380', question: '[Single Market] Will Donald J. Trump win the U.S. 2024 Republican...', volume: 6552460.32 },
    { id: '240382', question: '[Single Market] Will Joe Biden win the U.S. 2024 Democratic...', volume: 5770423.69 },
    { id: '246667', question: '[Single Market] Will Gavin Newsom win the U.S. 2024 Democrat...', volume: 576046.71 },
    { id: '240379', question: '[Single Market] Will Ron DeSantis win the U.S. 2024 Republic...', volume: 490480.59 },
    { id: '240381', question: '[Single Market] Will Nikki Haley win the U.S. 2024 Repu...', volume: 490480.59 },
    { id: '240383', question: '[Single Market] Will Kamala Harris win the U.S. 2024 De...', volume: 490480.59 },
    { id: '240385', question: '[Single Market] Will Hillary Clinton win the U.S. 2024...', volume: 490480.59 },
    { id: '240637', question: '[Single Market] Will Tucker Carlson win the U.S. 2024 R...', volume: 490480.59 },
    { id: '247745', question: '[Single Market] Will Mike Pence win the U.S. 2024 Repub...', volume: 490480.59 },
];

async function get(path) {
    return new Promise((resolve, reject) => {
        https.get({
            hostname: 'clob.polymarket.com',
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: 30000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try { resolve(JSON.parse(data)); }
                    catch (e) { reject(e); }
                } else {
                    reject(new Error(`HTTP ${res.statusCode}`));
                }
            });
        }).on('error', reject);
    });
}

async function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

(async () => {
    let successCount = 0;
    let totalPoints = 0;

    for (let i = 0; i < MARKETS_2024.length; i++) {
        const market = MARKETS_2024[i];
        console.log(`[${i + 1}/${MARKETS_2024.length}] ${market.question}`);
        console.log(`  Market ID: ${market.id} | Volume: $${market.volume.toLocaleString()}`);

        try {
            // Get market details from CLOB to find token IDs
            await delay(700);
            const marketData = await get(`/markets?condition_id=ANY`); // We'll filter client-side
            
            // Find our market in the response
            const foundMarket = marketData.data?.find(m => m.id === market.id || m.question.includes(market.question.slice(0, 30)));
            
            if (!foundMarket || !foundMarket.tokens || foundMarket.tokens.length === 0) {
                console.log(`  ⚠ Could not find tokens for this market\n`);
                continue;
            }

            console.log(`  Found ${foundMarket.tokens.length} tokens`);

            // Store market
            db.prepare(`INSERT OR REPLACE INTO markets (market_id, question, volume, end_date, tokens) VALUES (?, ?, ?, ?, ?)`)
                .run(market.id, market.question, market.volume, foundMarket.end_date_iso, JSON.stringify(foundMarket.tokens));

            // Fetch price history for each token
            for (const token of foundMarket.tokens) {
                await delay(700);
                
                try {
                    const priceHistory = await get(`/prices-history?market=${token.token_id}&interval=max&fidelity=1`);
                    
                    if (priceHistory && priceHistory.history && Array.isArray(priceHistory.history)) {
                        const points = priceHistory.history;
                        
                        if (points.length > 0) {
                            const insert = db.prepare(`INSERT INTO price_history (market_id, token_id, timestamp, price) VALUES (?, ?, ?, ?)`);
                            const insertMany = db.transaction((rows) => {
                                for (const row of rows) {
                                    insert.run(row.market_id, row.token_id, row.t, row.p);
                                }
                            });

                            insertMany(points.map(p => ({
                                market_id: market.id,
                                token_id: token.token_id,
                                t: p.t,
                                p: p.p
                            })));

                            totalPoints += points.length;
                            console.log(`    ✓ Token "${token.outcome}": ${points.length} price points`);
                        } else {
                            console.log(`    ⚠ Token "${token.outcome}": No history data`);
                        }
                    }
                } catch (error) {
                    console.log(`    ✗ Token "${token.outcome}": ${error.message}`);
                }
            }

            successCount++;
            console.log('');
            
        } catch (error) {
            console.log(`  ✗ Error: ${error.message}\n`);
        }
    }

    console.log('='.repeat(70));
    console.log('COLLECTION COMPLETE');
    console.log('='.repeat(70));
    console.log(`Markets processed:       ${MARKETS_2024.length}`);
    console.log(`Markets with price data: ${successCount}`);
    console.log(`Total price points:      ${totalPoints.toLocaleString()}`);
    console.log(`Database:                ${DB}`);
    console.log('='.repeat(70));

    db.close();
})();
