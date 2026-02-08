#!/usr/bin/env node
/**
 * Polymarket Historical Data Collector v2 (2025-2026)
 * Modified approach: scan ALL markets (not just closed) and filter by date
 */

const https = require('https');
const fs = require('fs');
const sqlite3 = require('better-sqlite3');

const BASE_URL = 'gamma-api.polymarket.com';
const RATE_LIMIT_DELAY = 300; // ms
const MAX_RETRIES = 3;

const START_DATE = new Date('2025-01-01T00:00:00Z');
const END_DATE = new Date('2026-02-28T23:59:59Z');

class PolymarketCollector {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.stats = {
      markets_scanned: 0,
      markets_found: 0,
      markets_processed: 0,
      markets_resolved: 0,
      price_points_collected: 0,
      errors: [],
      skipped_markets: []
    };
    this.initDatabase();
  }

  initDatabase() {
    this.db = new sqlite3(this.dbPath);
    
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS markets (
        market_id TEXT PRIMARY KEY,
        question TEXT,
        end_date_iso TEXT,
        volume REAL,
        liquidity REAL,
        created_at TEXT,
        closed_time TEXT,
        closed BOOLEAN,
        outcome TEXT
      )
    `);
    
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS price_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market_id TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        price REAL NOT NULL,
        volume REAL,
        FOREIGN KEY (market_id) REFERENCES markets(market_id)
      )
    `);
    
    this.db.exec(`
      CREATE INDEX IF NOT EXISTS idx_price_market_time 
      ON price_history(market_id, timestamp)
    `);
    
    console.log(`✓ Database initialized: ${this.dbPath}`);
  }

  async httpGet(path, params = {}) {
    return new Promise((resolve, reject) => {
      const queryString = Object.keys(params)
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
      
      const fullPath = queryString ? `${path}?${queryString}` : path;
      
      const options = {
        hostname: BASE_URL,
        path: fullPath,
        method: 'GET',
        headers: {
          'User-Agent': 'Mozilla/5.0'
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        res.on('data', (chunk) => { data += chunk; });
        res.on('end', () => {
          if (res.statusCode === 200) {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`JSON parse: ${e.message}`));
            }
          } else {
            reject(new Error(`HTTP ${res.statusCode}`));
          }
        });
      });

      req.on('error', reject);
      req.setTimeout(30000, () => {
        req.destroy();
        reject(new Error('Timeout'));
      });
      
      req.end();
    });
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async fetchMarkets(limit = 100, offset = 0) {
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        // Remove the closed filter to get all markets
        const data = await this.httpGet('/markets', { limit, offset });
        await this.sleep(RATE_LIMIT_DELAY);
        return Array.isArray(data) ? data : [];
      } catch (e) {
        if (attempt === MAX_RETRIES - 1) {
          this.stats.errors.push(`Fetch failed (offset=${offset}): ${e.message}`);
          return [];
        }
        await this.sleep(Math.pow(2, attempt) * 1000);
      }
    }
    return [];
  }

  isInDateRange(market) {
    try {
      const endDateStr = market.endDate || market.end_date_iso;
      if (!endDateStr) return false;
      
      const endDate = new Date(endDateStr);
      return endDate >= START_DATE && endDate <= END_DATE;
    } catch (e) {
      return false;
    }
  }

  async fetchPriceHistory(conditionId) {
    // Try the most likely endpoint
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const data = await this.httpGet(`/prices/${conditionId}`);
        await this.sleep(RATE_LIMIT_DELAY);
        
        if (Array.isArray(data)) return data;
        if (data && data.history) return data.history;
        return [];
      } catch (e) {
        if (attempt === MAX_RETRIES - 1) {
          return null;
        }
        await this.sleep(Math.pow(2, attempt) * 500);
      }
    }
    return null;
  }

  storeMarket(market) {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO markets 
      (market_id, question, end_date_iso, volume, liquidity, created_at, closed_time, closed, outcome)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    stmt.run(
      market.conditionId || market.id,
      market.question || market.description,
      market.endDate || market.end_date_iso,
      parseFloat(market.volume || 0),
      parseFloat(market.liquidity || 0),
      market.createdAt || market.created_at,
      market.closedTime,
      market.closed ? 1 : 0,
      market.outcome
    );
  }

  storePriceHistory(marketId, history) {
    if (!history || history.length === 0) return;
    
    const stmt = this.db.prepare(`
      INSERT INTO price_history (market_id, timestamp, price, volume)
      VALUES (?, ?, ?, ?)
    `);
    
    const insert = this.db.transaction((points) => {
      for (const point of points) {
        const timestamp = point.t || point.timestamp || point.time;
        const price = point.p || point.price;
        const volume = point.v || point.volume;
        
        if (timestamp && price !== undefined) {
          stmt.run(marketId, parseInt(timestamp), parseFloat(price), volume ? parseFloat(volume) : null);
        }
      }
    });
    
    insert(history);
    this.stats.price_points_collected += history.length;
  }

  async collectAllData() {
    console.log('🚀 Polymarket Data Collection v2 (2025-2026)');
    console.log(`📅 Range: ${START_DATE.toISOString().split('T')[0]} to ${END_DATE.toISOString().split('T')[0]}\n`);
    
    let offset = 0;
    const limit = 100;
    const marketsInRange = [];
    
    // Phase 1: Scan for markets in date range (closed or not)
    console.log('📊 Phase 1: Scanning all markets for 2025-2026 dates...');
    
    // Start from a higher offset since we know early markets are from 2020
    offset = 9000; // We know offset 9000 is around Jan 2024
    
    while (offset < 30000) { // Safety limit
      const markets = await this.fetchMarkets(limit, offset);
      if (!markets || markets.length === 0) break;
      
      for (const market of markets) {
        this.stats.markets_scanned++;
        
        if (this.isInDateRange(market)) {
          marketsInRange.push(market);
          this.stats.markets_found++;
          
          // Show first few we find
          if (this.stats.markets_found <= 5) {
            console.log(`  ✓ Found: ${market.question.substring(0, 60)}... (${market.endDate})`);
          }
        } else {
          // Check if we've gone past our date range
          const endDate = new Date(market.endDate || '2020-01-01');
          if (endDate > END_DATE && this.stats.markets_found > 0) {
            console.log(`  Passed end date range at offset ${offset}, stopping scan.`);
            break;
          }
        }
      }
      
      process.stdout.write(`  Scanned ${this.stats.markets_scanned}, found ${this.stats.markets_found} in range...\r`);
      
      if (markets.length < limit) break;
      offset += limit;
    }
    
    console.log(`\n✓ Found ${marketsInRange.length} markets in date range (${this.stats.markets_scanned} scanned)`);
    
    // Filter for closed/resolved markets only
    const resolvedMarkets = marketsInRange.filter(m => m.closed);
    console.log(`✓ ${resolvedMarkets.length} are resolved/closed`);
    
    // Sort by volume (high to low)
    resolvedMarkets.sort((a, b) => parseFloat(b.volume || 0) - parseFloat(a.volume || 0));
    
    // Phase 2: Collect price history for resolved markets
    console.log(`\n📈 Phase 2: Collecting price history for resolved markets...`);
    
    for (let i = 0; i < resolvedMarkets.length; i++) {
      const market = resolvedMarkets[i];
      const marketId = market.conditionId || market.id;
      const question = (market.question || 'Unknown').substring(0, 60);
      const volume = market.volume || 0;
      
      console.log(`  [${i + 1}/${resolvedMarkets.length}] ${question}...`);
      console.log(`      Vol: $${parseFloat(volume).toLocaleString()}, End: ${market.endDate}`);
      
      // Store market metadata
      this.storeMarket(market);
      this.stats.markets_processed++;
      
      // Fetch and store price history
      const history = await this.fetchPriceHistory(marketId);
      if (history && history.length > 0) {
        this.storePriceHistory(marketId, history);
        console.log(`      ✓ ${history.length} price points`);
      } else {
        this.stats.skipped_markets.push({
          id: marketId,
          question,
          reason: 'No price history'
        });
        console.log(`      ⚠️  No price history`);
      }
    }
    
    console.log('\n✅ Collection complete!');
    this.printStats();
  }

  printStats() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 COLLECTION STATISTICS');
    console.log('='.repeat(60));
    console.log(`Markets scanned:            ${this.stats.markets_scanned}`);
    console.log(`Markets in range:           ${this.stats.markets_found}`);
    console.log(`Resolved markets:           ${this.stats.markets_processed}`);
    console.log(`Price points collected:     ${this.stats.price_points_collected.toLocaleString()}`);
    console.log(`Markets w/o price data:     ${this.stats.skipped_markets.length}`);
    console.log(`Errors:                     ${this.stats.errors.length}`);
    console.log('='.repeat(60));
  }

  generateQualityReport(reportPath) {
    const totalMarkets = this.db.prepare('SELECT COUNT(*) as count FROM markets').get().count;
    const totalPrices = this.db.prepare('SELECT COUNT(*) as count FROM price_history').get().count;
    const closedMarkets = this.db.prepare('SELECT COUNT(*) as count FROM markets WHERE closed = 1').get().count;
    
    const marketsWithoutPrices = this.db.prepare(`
      SELECT m.market_id, m.question
      FROM markets m
      LEFT JOIN price_history ph ON m.market_id = ph.market_id
      WHERE ph.id IS NULL
      LIMIT 50
    `).all();
    
    const sparseMarkets = this.db.prepare(`
      SELECT m.market_id, m.question, COUNT(ph.id) as count
      FROM markets m
      INNER JOIN price_history ph ON m.market_id = ph.market_id
      GROUP BY m.market_id
      HAVING count < 50
      ORDER BY count ASC
      LIMIT 20
    `).all();
    
    let report = '# Data Quality Report: Polymarket Historical Prices (2025-2026)\n\n';
    report += `**Generated:** ${new Date().toISOString()}\n\n`;
    
    report += '## Summary\n\n';
    report += `- **Collection Date:** ${new Date().toISOString().split('T')[0]}\n`;
    report += `- **Target Range:** Jan 1, 2025 - Feb 28, 2026\n`;
    report += `- **Total Markets Stored:** ${totalMarkets}\n`;
    report += `- **Closed/Resolved Markets:** ${closedMarkets}\n`;
    report += `- **Total Price Points:** ${totalPrices.toLocaleString()}\n`;
    report += `- **Avg Price Points per Market:** ${totalMarkets > 0 ? (totalPrices / totalMarkets).toFixed(1) : 0}\n`;
    report += `- **Markets Scanned (API):** ${this.stats.markets_scanned}\n\n`;
    
    report += '## Data Coverage\n\n';
    report += `### Markets Found vs Resolved\n\n`;
    report += `- Markets with endDate in range: ${this.stats.markets_found}\n`;
    report += `- Of those, closed/resolved: ${closedMarkets}\n`;
    report += `- Still active (not resolved): ${this.stats.markets_found - closedMarkets}\n\n`;
    
    report += '## Data Quality Issues\n\n';
    
    if (marketsWithoutPrices.length > 0) {
      report += `### Markets Without Price History (${marketsWithoutPrices.length})\n\n`;
      marketsWithoutPrices.forEach(m => {
        report += `- \`${m.market_id}\`: ${m.question}\n`;
      });
      report += '\n';
    } else {
      report += '✅ All markets have price history data.\n\n';
    }
    
    if (sparseMarkets.length > 0) {
      report += '### Markets with Sparse Data (<50 points)\n\n';
      sparseMarkets.forEach(m => {
        report += `- \`${m.market_id}\` (${m.count} points): ${m.question}\n`;
      });
      report += '\n';
    }
    
    if (this.stats.errors.length > 0) {
      report += '## API Errors\n\n';
      this.stats.errors.forEach(err => {
        report += `- ${err}\n`;
      });
      report += '\n';
    }
    
    report += '## Notes\n\n';
    report += '- **Data Source:** Polymarket Gamma API (`gamma-api.polymarket.com`)\n';
    report += '- **Collection Method:** Scanned markets starting from offset 9000\n';
    report += '- **Rate Limiting:** 300ms delay between requests\n';
    report += '- **Price Endpoint:** `/prices/{conditionId}`\n';
    report += '- **Caveat:** Only resolved/closed markets have complete price history\n';
    report += '- **Active Markets:** Markets still open may have partial or no historical data\n';
    
    fs.writeFileSync(reportPath, report);
    console.log(`✓ Quality report: ${reportPath}`);
  }

  close() {
    this.db.close();
  }
}

(async () => {
  const dbPath = 'historical_2025_2026.db';
  const reportPath = 'DATA_QUALITY_2025_2026.md';
  
  const collector = new PolymarketCollector(dbPath);
  
  try {
    await collector.collectAllData();
    collector.generateQualityReport(reportPath);
    collector.close();
    
    console.log(`\n✅ SUCCESS!`);
    console.log(`   📁 Database: ${dbPath}`);
    console.log(`   📄 Report:   ${reportPath}`);
  } catch (e) {
    console.error(`\n❌ Error: ${e.message}`);
    console.error(e.stack);
    collector.close();
    process.exit(1);
  }
})();
