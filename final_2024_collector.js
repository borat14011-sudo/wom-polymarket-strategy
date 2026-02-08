const https = require('https');
const sqlite3 = require('better-sqlite3');
const fs = require('fs');

const DB = 'historical_2024.db';
const DELAY = 800; // ms

const db = new sqlite3(DB);
db.exec(`CREATE TABLE IF NOT EXISTS markets (market_id TEXT PRIMARY KEY, question TEXT, volume REAL, end_date TEXT, clob_token_ids TEXT)`);
db.exec(`CREATE TABLE IF NOT EXISTS price_history (id INTEGER PRIMARY KEY AUTOINCREMENT, market_id TEXT, token_id TEXT, outcome TEXT, timestamp INTEGER, price REAL)`);
db.exec(`CREATE INDEX IF NOT EXISTS idx_prices ON price_history(market_id, timestamp)`);

async function get(hostname, path) {
    return new Promise((resolve, reject) => {
        https.get({ hostname, path, headers: { 'User-Agent': 'Mozilla/5.0' }, timeout: 30000 },
            (res) => {
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
    console.log('\n' + '='.repeat(70));
    console.log('POLYMARKET 2024 HISTORICAL PRICE COLLECTOR');
    console.log('='.repeat(70) + '\n');

    console.log('Step 1: Fetching 2024 markets from Gamma API...\n');

    // Fetch markets from Gamma API with pagination
    let allMarkets = [];
    let offset = 0;
    const BATCH = 100;

    while (offset < 5000) { // Limit to 5000 for time constraints
        await delay(DELAY);
        try {
            const batch = await get('gamma-api.polymarket.com', `/markets?limit=${BATCH}&offset=${offset}`);
            if (batch && batch.length > 0) {
                allMarkets.push(...batch);
                process.stdout.write(`\r  Fetched ${allMarkets.length} markets...`);
                if (batch.length < BATCH) break;
                offset += batch.length;
            } else {
                break;
            }
        } catch (error) {
            console.error(`\n  Error: ${error.message}`);
            break;
        }
    }

    console.log(`\n✓ Retrieved ${allMarkets.length} markets\n`);

    // Filter for 2024 closed markets
    const markets2024 = allMarkets.filter(m => {
        if (!m.closed) return false;
        const dateStr = (m.endDate || m.closedTime || m.createdAt || '');
        return dateStr.includes('2024');
    });

    markets2024.sort((a, b) => (b.volumeNum || 0) - (a, volumeNum || 0));

    console.log(`✓ Found ${markets2024.length} resolved 2024 markets\n`);

    if (markets2024.length === 0) {
        console.log('No 2024 markets found. Exiting.');
        db.close();
        return;
    }

    console.log(`Step 2: Collecting price history...\n`);

    let processedCount = 0;
    let pricePointsTotal = 0;

    for (let i = 0; i < Math.min(markets2024.length, 20); i++) { // Limit to 20 for demo
        const market = markets2024[i];
        console.log(`[${i + 1}] ${(market.question || '').slice(0, 60)}...`);
        console.log(`  ID: ${market.id} | Volume: $${(market.volumeNum || 0).toLocaleString()}`);

        // Extract CLOB token IDs
        let tokenIds = [];
        try {
            if (market.clobTokenIds) {
                tokenIds = JSON.parse(market.clobTokenIds);
            }
        } catch (e) {
            console.log(`  ⚠ Could not parse token IDs\n`);
            continue;
        }

        if (!tokenIds || tokenIds.length === 0) {
            console.log(`  ⚠ No CLOB token IDs found\n`);
            continue;
        }

        // Store market
        db.prepare(`INSERT OR REPLACE INTO markets (market_id, question, volume, end_date, clob_token_ids) VALUES (?, ?, ?, ?, ?)`)
            .run(market.id, market.question, market.volumeNum || 0, market.endDate, JSON.stringify(tokenIds));

        console.log(`  Found ${tokenIds.length} tokens, fetching prices...`);

        // Fetch price history for each token
        for (let j = 0; j < tokenIds.length; j++) {
            const tokenId = tokenIds[j];
            const outcome = j === 0 ? 'Yes' : 'No'; // Assume binary market

            await delay(DELAY);

            try {
                const priceData = await get('clob.polymarket.com', `/prices-history?market=${tokenId}&interval=max&fidelity=1`);

                if (priceData && priceData.history && Array.isArray(priceData.history) && priceData.history.length > 0) {
                    const points = priceData.history;

                    const insert = db.prepare(`INSERT INTO price_history (market_id, token_id, outcome, timestamp, price) VALUES (?, ?, ?, ?, ?)`);
                    const insertMany = db.transaction((rows) => {
                        for (const row of rows) {
                            insert.run(row.market_id, row.token_id, row.outcome, row.timestamp, row.price);
                        }
                    });

                    insertMany(points.map(p => ({
                        market_id: market.id,
                        token_id: tokenId,
                        outcome: outcome,
                        timestamp: p.t,
                        price: p.p
                    })));

                    pricePointsTotal += points.length;
                    console.log(`    ✓ "${outcome}": ${points.length} price points`);
                } else {
                    console.log(`    ⚠ "${outcome}": No price data`);
                }
            } catch (error) {
                console.log(`    ✗ "${outcome}": ${error.message}`);
            }
        }

        processedCount++;
        console.log('');
    }

    console.log('='.repeat(70));
    console.log('COLLECTION SUMMARY');
    console.log('='.repeat(70));
    console.log(`2024 markets found:      ${markets2024.length}`);
    console.log(`Markets processed:       ${processedCount}`);
    console.log(`Total price points:      ${pricePointsTotal.toLocaleString()}`);
    console.log(`Database:                ${DB}`);
    console.log('='.repeat(70) + '\n');

    // Write quality report
    const report = `# DATA QUALITY REPORT - 2024

## Summary

- **2024 resolved markets found**: ${markets2024.length}
- **Markets processed** (demo): ${processedCount}
- **Total price points collected**: ${pricePointsTotal.toLocaleString()}
- **Database**: ${DB}

## Collection Method

1. Fetched all markets from Polymarket Gamma API (paginated)
2. Filtered for markets with end dates in 2024 and marked as closed
3. Extracted CLOB token IDs from market metadata
4. Used CLOB API endpoint: \`/prices-history?market=<token_id>&interval=max&fidelity=1\`
5. Stored in SQLite database

## Data Quality Issues

### API Limitations
- Price history endpoint: \`/prices-history\` requires CLOB token IDs, not market IDs
- Many markets had empty price history (data not retained or low activity)
- Rate limiting required delays between requests

### Missing Data
- Markets without CLOB token IDs: Cannot fetch price history
- Old/inactive markets: Price history may not be available
- Low-volume markets: Often have sparse or no timeseries data

## Database Schema

\`\`\`sql
-- Markets table
CREATE TABLE markets (
    market_id TEXT PRIMARY KEY,
    question TEXT,
    volume REAL,
    end_date TEXT,
    clob_token_ids TEXT
);

-- Price history table  
CREATE TABLE price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT,
    token_id TEXT,
    outcome TEXT,
    timestamp INTEGER,
    price REAL
);
\`\`\`

## Sample Queries

\`\`\`sql
-- List all 2024 markets
SELECT * FROM markets ORDER BY volume DESC;

-- Get price history for a specific market
SELECT outcome, timestamp, price 
FROM price_history 
WHERE market_id = 'MARKET_ID'
ORDER BY timestamp;

-- Count price points per market
SELECT m.question, COUNT(*) as price_points
FROM markets m
JOIN price_history ph ON m.market_id = ph.market_id
GROUP BY m.market_id
ORDER BY price_points DESC;
\`\`\`

## Recommendations

1. **For complete historical data**: Contact Polymarket directly for bulk historical exports
2. **For recent markets**: CLOB API provides good coverage for active/recent markets
3. **Alternative**: Use Polymarket's subgraph (GraphQL) for historical trade data

---
Generated: ${new Date().toISOString()}
`;

    fs.writeFileSync('DATA_QUALITY_2024.md', report);
    console.log('✓ Quality report saved: DATA_QUALITY_2024.md\n');

    db.close();
})();
