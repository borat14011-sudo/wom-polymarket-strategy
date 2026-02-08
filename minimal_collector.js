const https = require('https');
const sqlite3 = require('better-sqlite3');

const DB = 'historical_2024.db';
const DELAY = 700;

// Initialize database
const db = new sqlite3(DB);
db.exec(`
    CREATE TABLE IF NOT EXISTS markets (
        market_id TEXT PRIMARY KEY, question TEXT, volume REAL, 
        end_date TEXT, category TEXT
    )
`);
db.exec(`
    CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_id TEXT, timestamp INTEGER, price REAL, volume REAL
    )
`);
db.exec(`CREATE INDEX IF NOT EXISTS idx_mkt_time ON price_history(market_id, timestamp)`);

console.log('='.repeat(60));
console.log('MINIMAL 2024 DATA COLLECTOR');
console.log('='.repeat(60) + '\n');

async function get(path) {
    return new Promise((resolve, reject) => {
        https.get({
            hostname: 'gamma-api.polymarket.com',
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

function delay(ms) {
    return new Promise(r => setTimeout(r, ms));
}

(async () => {
    console.log('Step 1: Fetching markets (paginated)...\n');
    
    const allMarkets = [];
    const MAX_PAGES = 50; // Limit for testing - fetch ~5000 markets
    
    for (let page = 0; page < MAX_PAGES; page++) {
        try {
            await delay(DELAY);
            const batch = await get(`/markets?limit=100&offset=${page * 100}`);
            
            if (batch && batch.length > 0) {
                allMarkets.push(...batch);
                process.stdout.write(`\r  Page ${page + 1}: ${allMarkets.length} markets fetched...`);
                
                if (batch.length < 100) break; // Last page
            } else {
                break;
            }
        } catch (error) {
            console.error(`\nError on page ${page}: ${error.message}`);
            break;
        }
    }
    
    console.log(`\n✓ Fetched ${allMarkets.length} markets total\n`);
    
    // Filter for 2024 closed markets
    console.log('Step 2: Filtering for 2024 resolved markets...\n');
    
    const markets2024 = allMarkets.filter(m => {
        if (!m.closed) return false;
        const dateStr = (m.endDate || m.closedTime || m.createdAt || '');
        return dateStr.includes('2024');
    });
    
    // Sort by volume
    markets2024.sort((a, b) => (b.volumeNum || 0) - (a.volumeNum || 0));
    
    console.log(`✓ Found ${markets2024.length} resolved 2024 markets`);
    console.log(`\nTop 5 by volume:`);
    markets2024.slice(0, 5).forEach((m, i) => {
        console.log(`  ${i + 1}. $${(m.volumeNum || 0).toLocaleString()} - ${m.question.slice(0, 60)}...`);
    });
    
    // Process a sample (first 10)
    const SAMPLE_SIZE = Math.min(10, markets2024.length);
    console.log(`\nStep 3: Collecting price history for ${SAMPLE_SIZE} markets...\n`);
    
    let successCount = 0;
    let totalPoints = 0;
    
    const storeMarket = db.prepare(`
        INSERT OR REPLACE INTO markets (market_id, question, volume, end_date, category)
        VALUES (?, ?, ?, ?, ?)
    `);
    
    const storePrice = db.prepare(`
        INSERT INTO price_history (market_id, timestamp, price, volume)
        VALUES (?, ?, ?, ?)
    `);
    
    for (let i = 0; i < SAMPLE_SIZE; i++) {
        const m = markets2024[i];
        console.log(`[${i + 1}/${SAMPLE_SIZE}] ${m.question.slice(0, 55)}...`);
        console.log(`  ID: ${m.id}`);
        
        // Store market
        storeMarket.run(m.id, m.question, m.volumeNum || 0, m.endDate, m.category);
        
        // Try to fetch price history
        try {
            await delay(DELAY);
            
            // Try this endpoint format (based on Polymarket docs)
            const prices = await get(`/markets/${m.id}/prices`);
            
            if (prices && Array.isArray(prices) && prices.length > 0) {
                const insert = db.transaction((points) => {
                    for (const p of points) {
                        storePrice.run(m.id, p.t, p.p, p.v || 0);
                    }
                });
                
                insert(prices);
                totalPoints += prices.length;
                successCount++;
                console.log(`  ✓ Stored ${prices.length} price points\n`);
            } else {
                console.log(`  ⚠ No price data\n`);
            }
        } catch (error) {
            console.log(`  ✗ Error: ${error.message}\n`);
        }
    }
    
    console.log('='.repeat(60));
    console.log('RESULTS');
    console.log('='.repeat(60));
    console.log(`Markets found (2024):        ${markets2024.length}`);
    console.log(`Markets processed (sample):  ${SAMPLE_SIZE}`);
    console.log(`Markets with price data:     ${successCount}`);
    console.log(`Total price points:          ${totalPoints.toLocaleString()}`);
    console.log(`Database:                    ${DB}`);
    console.log('='.repeat(60));
    
    db.close();
    
    console.log('\n✓ COMPLETE - This is a proof of concept');
    console.log('  To collect all 2024 markets, increase SAMPLE_SIZE and MAX_PAGES');
})();
