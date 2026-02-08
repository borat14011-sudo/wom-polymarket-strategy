#!/usr/bin/env node
/**
 * Polymarket Historical Data Collector - 2024 ONLY
 * Collects resolved markets and price history from Jan 2024 - Dec 2024
 */

const https = require('https');
const sqlite3 = require('better-sqlite3');

// Configuration
const BASE_URL = 'gamma-api.polymarket.com';
const DB_FILE = 'historical_2024.db';
const REQUEST_DELAY = 600; // ms - be gentle with rate limits

// Target year
const TARGET_YEAR = '2024';

class Collector2024 {
    constructor() {
        this.db = new sqlite3(DB_FILE);
        this.stats = {
            total_markets_scanned: 0,
            markets_2024_found: 0,
            markets_with_prices: 0,
            total_price_points: 0,
            errors: []
        };
        this.initDB();
    }

    initDB() {
        console.log(`\n${'='.repeat(60)}`);
        console.log('POLYMARKET 2024 DATA COLLECTION');
        console.log('='.repeat(60));
        console.log(`Database: ${DB_FILE}\n`);

        this.db.exec(`
            CREATE TABLE IF NOT EXISTS markets (
                market_id TEXT PRIMARY KEY,
                condition_id TEXT,
                question TEXT,
                slug TEXT,
                category TEXT,
                end_date TEXT,
                closed_time TEXT,
                volume REAL,
                created_at TEXT,
                metadata TEXT
            )
        `);

        this.db.exec(`
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market_id TEXT,
                timestamp INTEGER,
                price REAL,
                volume REAL,
                FOREIGN KEY (market_id) REFERENCES markets(market_id)
            )
        `);

        this.db.exec(`
            CREATE INDEX IF NOT EXISTS idx_market_time 
            ON price_history(market_id, timestamp)
        `);

        this.db.exec(`
            CREATE TABLE IF NOT EXISTS data_quality (
                market_id TEXT PRIMARY KEY,
                has_price_data INTEGER,
                price_count INTEGER,
                error TEXT
            )
        `);

        console.log('✓ Database schema initialized\n');
    }

    async httpGet(path) {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: BASE_URL,
                path: path,
                method: 'GET',
                headers: { 'User-Agent': 'Mozilla/5.0' },
                timeout: 30000
            };

            https.get(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    if (res.statusCode === 200) {
                        try {
                            resolve(JSON.parse(data));
                        } catch (e) {
                            reject(new Error(`Parse error: ${e.message}`));
                        }
                    } else {
                        reject(new Error(`HTTP ${res.statusCode}`));
                    }
                });
            }).on('error', reject);
        });
    }

    async delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async fetchMarkets() {
        console.log('📡 Fetching ALL markets from Polymarket (paginated)...');
        
        const allMarkets = [];
        const BATCH_SIZE = 100;
        let offset = 0;
        let hasMore = true;

        try {
            while (hasMore) {
                await this.delay(REQUEST_DELAY);
                
                const batch = await this.httpGet(`/markets?limit=${BATCH_SIZE}&offset=${offset}`);
                
                if (batch && batch.length > 0) {
                    allMarkets.push(...batch);
                    offset += batch.length;
                    process.stdout.write(`\r  Fetched ${allMarkets.length} markets...`);
                    
                    if (batch.length < BATCH_SIZE) {
                        hasMore = false;
                    }
                } else {
                    hasMore = false;
                }
            }
            
            this.stats.total_markets_scanned = allMarkets.length;
            console.log(`\n✓ Retrieved ${allMarkets.length} total markets\n`);
            return allMarkets;
        } catch (error) {
            console.error(`\n✗ Failed to fetch markets: ${error.message}`);
            return allMarkets; // Return what we got so far
        }
    }

    filter2024Markets(markets) {
        console.log('🔍 Filtering for 2024 resolved markets...');
        
        const filtered = markets.filter(m => {
            if (!m.closed) return false;
            
            const endDate = m.endDate || '';
            const closedTime = m.closedTime || '';
            const createdAt = m.createdAt || '';
            
            // Check if any date field contains 2024
            return endDate.includes(TARGET_YEAR) || 
                   closedTime.includes(TARGET_YEAR) ||
                   (createdAt.includes(TARGET_YEAR) && m.closed);
        });

        // Sort by volume descending (high-volume markets first)
        filtered.sort((a, b) => (b.volumeNum || 0) - (a.volumeNum || 0));

        this.stats.markets_2024_found = filtered.length;
        console.log(`✓ Found ${filtered.length} resolved markets from 2024\n`);
        
        return filtered;
    }

    storeMarket(market) {
        try {
            const stmt = this.db.prepare(`
                INSERT OR REPLACE INTO markets 
                (market_id, condition_id, question, slug, category, 
                 end_date, closed_time, volume, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `);

            stmt.run(
                market.id,
                market.conditionId,
                market.question,
                market.slug,
                market.category,
                market.endDate,
                market.closedTime,
                market.volumeNum || 0,
                market.createdAt,
                JSON.stringify(market)
            );
        } catch (error) {
            console.error(`  ✗ Error storing market: ${error.message}`);
        }
    }

    async fetchPriceHistory(marketId, conditionId) {
        // Try multiple endpoint formats
        const endpoints = [
            `/markets/${marketId}/prices`,
            `/prices?market=${marketId}`,
            `/price-history?market=${marketId}`,
            `/markets/${marketId}/prices-history`,
        ];

        for (const endpoint of endpoints) {
            try {
                await this.delay(REQUEST_DELAY);
                const data = await this.httpGet(endpoint);
                
                if (data && (Array.isArray(data) || typeof data === 'object')) {
                    return data;
                }
            } catch (error) {
                // Try next endpoint
                continue;
            }
        }

        return null;
    }

    storePriceHistory(marketId, priceData) {
        if (!priceData) return 0;

        const stmt = this.db.prepare(`
            INSERT INTO price_history (market_id, timestamp, price, volume)
            VALUES (?, ?, ?, ?)
        `);

        let count = 0;

        try {
            const transaction = this.db.transaction((points) => {
                for (const point of points) {
                    stmt.run(marketId, point.t, point.p, point.v || 0);
                    count++;
                }
            });

            let points = [];

            if (Array.isArray(priceData)) {
                points = priceData.map(p => ({
                    t: p.timestamp || p.t,
                    p: p.price || p.p,
                    v: p.volume || p.v || 0
                }));
            } else if (typeof priceData === 'object') {
                // Handle nested structure { "Yes": [...], "No": [...] }
                for (const outcome in priceData) {
                    if (Array.isArray(priceData[outcome])) {
                        points.push(...priceData[outcome].map(p => ({
                            t: p.timestamp || p.t,
                            p: p.price || p.p,
                            v: p.volume || p.v || 0
                        })));
                    }
                }
            }

            if (points.length > 0) {
                transaction(points);
                count = points.length;
            }

            return count;
        } catch (error) {
            this.stats.errors.push(`Price storage error for ${marketId}: ${error.message}`);
            return 0;
        }
    }

    updateQuality(marketId, hasPrices, count, error = null) {
        const stmt = this.db.prepare(`
            INSERT OR REPLACE INTO data_quality
            (market_id, has_price_data, price_count, error)
            VALUES (?, ?, ?, ?)
        `);
        stmt.run(marketId, hasPrices ? 1 : 0, count, error);
    }

    async collect(limit = null) {
        const startTime = Date.now();

        // Step 1: Fetch all markets
        const allMarkets = await this.fetchMarkets();
        if (allMarkets.length === 0) {
            console.error('No markets fetched. Aborting.');
            return;
        }

        // Step 2: Filter for 2024
        let markets2024 = this.filter2024Markets(allMarkets);

        if (limit) {
            markets2024 = markets2024.slice(0, limit);
            console.log(`⚙️  TEST MODE: Processing only ${limit} markets\n`);
        }

        // Step 3: Collect price data for each market
        console.log('💾 Collecting price history...\n');

        for (let i = 0; i < markets2024.length; i++) {
            const market = markets2024[i];
            const num = i + 1;
            const total = markets2024.length;
            const question = (market.question || 'N/A').slice(0, 65);
            const volume = market.volumeNum || 0;

            console.log(`[${num}/${total}] ${question}...`);
            console.log(`  ID: ${market.id} | Volume: $${volume.toLocaleString()}`);

            // Store market metadata
            this.storeMarket(market);

            // Fetch price history
            const priceData = await this.fetchPriceHistory(market.id, market.conditionId);

            if (priceData) {
                const count = this.storePriceHistory(market.id, priceData);
                if (count > 0) {
                    console.log(`  ✓ Stored ${count} price points`);
                    this.stats.markets_with_prices++;
                    this.stats.total_price_points += count;
                    this.updateQuality(market.id, true, count);
                } else {
                    console.log(`  ⚠ No valid price data`);
                    this.updateQuality(market.id, false, 0, 'No parseable price points');
                }
            } else {
                console.log(`  ⚠ No price history found`);
                this.updateQuality(market.id, false, 0, 'API endpoint not found');
            }

            console.log('');

            // Progress indicator every 10 markets
            if (num % 10 === 0) {
                const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
                const rate = (num / parseInt(elapsed)).toFixed(1);
                console.log(`⏱  Progress: ${num}/${total} markets | ${elapsed}s elapsed | ${rate} markets/sec\n`);
            }
        }

        this.printReport(startTime);
    }

    printReport(startTime) {
        const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);

        console.log('\n' + '='.repeat(60));
        console.log('DATA QUALITY REPORT - 2024');
        console.log('='.repeat(60));
        console.log(`Total markets scanned:     ${this.stats.total_markets_scanned.toLocaleString()}`);
        console.log(`2024 resolved markets:     ${this.stats.markets_2024_found}`);
        console.log(`Markets WITH price data:   ${this.stats.markets_with_prices}`);
        console.log(`Markets WITHOUT prices:    ${this.stats.markets_2024_found - this.stats.markets_with_prices}`);
        
        const coverage = this.stats.markets_2024_found > 0 
            ? (this.stats.markets_with_prices / this.stats.markets_2024_found * 100).toFixed(1) 
            : 0;
        console.log(`Coverage rate:             ${coverage}%`);
        console.log('');
        console.log(`Total price points:        ${this.stats.total_price_points.toLocaleString()}`);
        
        const avgPoints = this.stats.markets_with_prices > 0
            ? (this.stats.total_price_points / this.stats.markets_with_prices).toFixed(0)
            : 0;
        console.log(`Avg points per market:     ${avgPoints}`);
        console.log('');
        console.log(`Time elapsed:              ${elapsed} minutes`);
        console.log(`Database file:             ${DB_FILE}`);
        console.log('='.repeat(60));

        // Write detailed quality report
        this.writeQualityReport();
    }

    writeQualityReport() {
        const report = `# DATA QUALITY REPORT - 2024

## Summary Statistics

- **Total markets scanned**: ${this.stats.total_markets_scanned.toLocaleString()}
- **2024 resolved markets found**: ${this.stats.markets_2024_found}
- **Markets with price data**: ${this.stats.markets_with_prices}
- **Markets without price data**: ${this.stats.markets_2024_found - this.stats.markets_with_prices}
- **Coverage**: ${(this.stats.markets_with_prices / this.stats.markets_2024_found * 100).toFixed(1)}%

## Price Data Quality

- **Total price points collected**: ${this.stats.total_price_points.toLocaleString()}
- **Average points per market**: ${(this.stats.total_price_points / this.stats.markets_with_prices).toFixed(0)}

## Data Gaps

Markets without price history data typically fall into these categories:
1. **API endpoint not found** - Price history endpoint doesn't exist or has changed
2. **Low-volume markets** - May not have sufficient trading activity for timeseries
3. **Very old markets** - Historical data may not be retained

## Query the Database

\`\`\`sql
-- List all 2024 markets with price data
SELECT m.market_id, m.question, m.volume, dq.price_count
FROM markets m
JOIN data_quality dq ON m.market_id = dq.market_id
WHERE dq.has_price_data = 1
ORDER BY m.volume DESC;

-- Markets missing price data
SELECT m.market_id, m.question, m.volume, dq.error
FROM markets m
JOIN data_quality dq ON m.market_id = dq.market_id
WHERE dq.has_price_data = 0
ORDER BY m.volume DESC;

-- Price history for a specific market
SELECT timestamp, price, volume
FROM price_history
WHERE market_id = 'YOUR_MARKET_ID'
ORDER BY timestamp;
\`\`\`

## Issues Encountered

${this.stats.errors.length > 0 ? this.stats.errors.slice(0, 10).map((e, i) => `${i + 1}. ${e}`).join('\n') : 'None'}

## Next Steps

1. ✓ Database created: **${DB_FILE}**
2. Review markets without price data (see SQL queries above)
3. Consider alternate data sources for missing markets
4. Use this data for backtesting and analysis

---
Generated: ${new Date().toISOString()}
`;

        require('fs').writeFileSync('DATA_QUALITY_2024.md', report);
        console.log('\n✓ Detailed report saved to: DATA_QUALITY_2024.md');
    }

    close() {
        this.db.close();
    }
}

// Main execution
(async () => {
    const collector = new Collector2024();

    try {
        // Test with 15 markets first, then run full collection
        const TEST_LIMIT = 15;
        console.log(`Starting TEST collection (${TEST_LIMIT} markets)...\n`);
        
        await collector.collect(TEST_LIMIT);

        console.log('\n✓ TEST COMPLETE - Review results above');
        console.log('To run full collection, set TEST_LIMIT = null in code');

    } catch (error) {
        console.error(`\n✗ Fatal error: ${error.message}`);
        console.error(error.stack);
    } finally {
        collector.close();
    }
})();
