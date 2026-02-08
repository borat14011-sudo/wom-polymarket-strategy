#!/usr/bin/env node
/**
 * Polymarket Historical Data Collector (2025-2026)
 * Collects price history for all resolved markets from Jan 2025 to Feb 2026
 */

const https = require('https');
const fs = require('fs');
const sqlite3 = require('better-sqlite3');

// API Configuration
const BASE_URL = 'gamma-api.polymarket.com';
const RATE_LIMIT_DELAY = 500; // milliseconds
const MAX_RETRIES = 3;

// Date range: Jan 1, 2025 to Feb 28, 2026
const START_DATE = new Date('2025-01-01T00:00:00Z');
const END_DATE = new Date('2026-02-28T23:59:59Z');

class PolymarketCollector {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.stats = {
      markets_found: 0,
      markets_processed: 0,
      price_points_collected: 0,
      errors: [],
      skipped_markets: []
    };
    this.initDatabase();
  }

  initDatabase() {
    this.db = new sqlite3(this.dbPath);
    
    // Markets table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS markets (
        market_id TEXT PRIMARY KEY,
        question TEXT,
        end_date_iso TEXT,
        volume REAL,
        liquidity REAL,
        created_at TEXT,
        resolved_at TEXT,
        outcome TEXT
      )
    `);
    
    // Price history table
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
    
    // Create indexes
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
          'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
      };

      const req = https.request(options, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          if (res.statusCode === 200) {
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              reject(new Error(`JSON parse error: ${e.message}`));
            }
          } else {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        });
      });

      req.on('error', reject);
      req.setTimeout(30000, () => {
        req.destroy();
        reject(new Error('Request timeout'));
      });
      
      req.end();
    });
  }

  async sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async fetchResolvedMarkets(limit = 100, offset = 0) {
    for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
      try {
        const data = await this.httpGet('/markets', {
          limit,
          offset,
          closed: 'true'
        });
        await this.sleep(RATE_LIMIT_DELAY);
        return Array.isArray(data) ? data : [];
      } catch (e) {
        if (attempt === MAX_RETRIES - 1) {
          this.stats.errors.push(`Failed to fetch markets (offset=${offset}): ${e.message}`);
          return [];
        }
        await this.sleep(Math.pow(2, attempt) * 1000);
      }
    }
    return [];
  }

  isInDateRange(market) {
    try {
      const endDateStr = market.endDate || market.end_date_iso || market.closed_time;
      if (!endDateStr) return false;
      
      const endDate = new Date(endDateStr);
      return endDate >= START_DATE && endDate <= END_DATE;
    } catch (e) {
      return false;
    }
  }

  async fetchPriceHistory(marketId) {
    const endpoints = [
      { path: '/prices-history', params: { market: marketId } },
      { path: `/markets/${marketId}/prices-history`, params: {} },
      { path: '/prices', params: { market: marketId } }
    ];
    
    for (const endpoint of endpoints) {
      for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
        try {
          const data = await this.httpGet(endpoint.path, endpoint.params);
          await this.sleep(RATE_LIMIT_DELAY);
          
          if (Array.isArray(data)) return data;
          if (data && data.history) return data.history;
          if (data && data.data) return data.data;
          return [];
        } catch (e) {
          if (e.message.includes('404')) break; // Try next endpoint
          if (attempt === MAX_RETRIES - 1) continue;
          await this.sleep(Math.pow(2, attempt) * 1000);
        }
      }
    }
    return null;
  }

  storeMarket(market) {
    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO markets 
      (market_id, question, end_date_iso, volume, liquidity, created_at, resolved_at, outcome)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `);
    
    stmt.run(
      market.id || market.condition_id,
      market.question || market.description,
      market.endDate || market.end_date_iso,
      parseFloat(market.volume || 0),
      parseFloat(market.liquidity || 0),
      market.createdAt || market.created_at,
      market.resolvedAt || market.resolved_at,
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
    console.log('🚀 Starting Polymarket data collection (2025-2026)');
    console.log(`📅 Date range: ${START_DATE.toISOString().split('T')[0]} to ${END_DATE.toISOString().split('T')[0]}\n`);
    
    let offset = 0;
    const limit = 100;
    const marketsInRange = [];
    
    // Phase 1: Discover markets
    console.log('📊 Phase 1: Discovering resolved markets...');
    while (true) {
      const markets = await this.fetchResolvedMarkets(limit, offset);
      if (!markets || markets.length === 0) break;
      
      for (const market of markets) {
        if (this.isInDateRange(market)) {
          marketsInRange.push(market);
          this.stats.markets_found++;
        }
      }
      
      process.stdout.write(`  Scanned ${offset + markets.length} markets, found ${marketsInRange.length} in range...\r`);
      
      if (markets.length < limit) break;
      offset += limit;
      
      if (offset > 10000) {
        console.log('\n⚠️  Reached safety limit of 10,000 markets');
        break;
      }
    }
    
    console.log(`\n✓ Found ${marketsInRange.length} markets in date range`);
    
    // Sort by volume (high to low)
    marketsInRange.sort((a, b) => parseFloat(b.volume || 0) - parseFloat(a.volume || 0));
    
    // Phase 2: Collect price history
    console.log(`\n📈 Phase 2: Collecting price history...`);
    for (let i = 0; i < marketsInRange.length; i++) {
      const market = marketsInRange[i];
      const marketId = market.id || market.condition_id;
      const question = (market.question || 'Unknown').substring(0, 60);
      const volume = market.volume || 0;
      
      console.log(`  [${i + 1}/${marketsInRange.length}] ${question}... (vol: $${parseFloat(volume).toLocaleString()})`);
      
      // Store market metadata
      this.storeMarket(market);
      
      // Fetch and store price history
      const history = await this.fetchPriceHistory(marketId);
      if (history && history.length > 0) {
        this.storePriceHistory(marketId, history);
        console.log(`    ✓ Collected ${history.length} price points`);
      } else {
        this.stats.skipped_markets.push({
          id: marketId,
          question,
          reason: 'No price history available'
        });
        console.log(`    ⚠️  No price history found`);
      }
      
      this.stats.markets_processed++;
    }
    
    console.log('\n✅ Collection complete!');
    this.printStats();
  }

  printStats() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 COLLECTION STATISTICS');
    console.log('='.repeat(60));
    console.log(`Markets found in range:     ${this.stats.markets_found}`);
    console.log(`Markets processed:          ${this.stats.markets_processed}`);
    console.log(`Price points collected:     ${this.stats.price_points_collected.toLocaleString()}`);
    console.log(`Markets skipped:            ${this.stats.skipped_markets.length}`);
    console.log(`Errors encountered:         ${this.stats.errors.length}`);
    console.log('='.repeat(60));
  }

  generateQualityReport(reportPath) {
    // Gather statistics
    const totalMarkets = this.db.prepare('SELECT COUNT(*) as count FROM markets').get().count;
    const totalPrices = this.db.prepare('SELECT COUNT(*) as count FROM price_history').get().count;
    
    const marketsWithoutPrices = this.db.prepare(`
      SELECT m.market_id, m.question, COUNT(ph.id) as price_count
      FROM markets m
      LEFT JOIN price_history ph ON m.market_id = ph.market_id
      GROUP BY m.market_id
      HAVING price_count = 0
    `).all();
    
    const sparseMarkets = this.db.prepare(`
      SELECT market_id, COUNT(*) as count
      FROM price_history
      GROUP BY market_id
      ORDER BY count ASC
      LIMIT 10
    `).all();
    
    // Write report
    let report = '# Data Quality Report: Polymarket Historical Prices (2025-2026)\n\n';
    report += `**Generated:** ${new Date().toISOString()}\n\n`;
    
    report += '## Summary\n\n';
    report += `- **Total Markets:** ${totalMarkets}\n`;
    report += `- **Total Price Points:** ${totalPrices.toLocaleString()}\n`;
    report += `- **Average Price Points per Market:** ${totalMarkets > 0 ? (totalPrices / totalMarkets).toFixed(1) : 0}\n`;
    report += `- **Markets Without Price Data:** ${marketsWithoutPrices.length}\n\n`;
    
    report += '## Data Gaps\n\n';
    if (marketsWithoutPrices.length > 0) {
      report += '### Markets Missing Price History\n\n';
      for (let i = 0; i < Math.min(20, marketsWithoutPrices.length); i++) {
        const m = marketsWithoutPrices[i];
        report += `- \`${m.market_id}\`: ${m.question}\n`;
      }
      if (marketsWithoutPrices.length > 20) {
        report += `\n*... and ${marketsWithoutPrices.length - 20} more*\n`;
      }
    } else {
      report += '✅ All markets have price history data.\n';
    }
    
    report += '\n### Markets with Sparse Data (<50 points)\n\n';
    for (const m of sparseMarkets) {
      report += `- \`${m.market_id}\`: ${m.count} price points\n`;
    }
    
    if (this.stats.errors.length > 0) {
      report += '\n## Errors Encountered\n\n';
      for (const error of this.stats.errors) {
        report += `- ${error}\n`;
      }
    }
    
    if (this.stats.skipped_markets.length > 0) {
      report += '\n## Skipped Markets\n\n';
      for (let i = 0; i < Math.min(50, this.stats.skipped_markets.length); i++) {
        const skip = this.stats.skipped_markets[i];
        report += `- \`${skip.id}\`: ${skip.question} - ${skip.reason}\n`;
      }
      if (this.stats.skipped_markets.length > 50) {
        report += `\n*... and ${this.stats.skipped_markets.length - 50} more*\n`;
      }
    }
    
    report += '\n## Notes\n\n';
    report += '- Data source: Polymarket Gamma API\n';
    report += '- Only resolved markets included\n';
    report += '- Markets sorted by volume (high to low) during collection\n';
    report += '- Rate limiting: 500ms delay between requests\n';
    
    fs.writeFileSync(reportPath, report);
    console.log(`✓ Quality report generated: ${reportPath}`);
  }

  close() {
    this.db.close();
  }
}

// Main execution
(async () => {
  const dbPath = 'historical_2025_2026.db';
  const reportPath = 'DATA_QUALITY_2025_2026.md';
  
  const collector = new PolymarketCollector(dbPath);
  
  try {
    await collector.collectAllData();
    collector.generateQualityReport(reportPath);
    collector.close();
    
    console.log(`\n✅ SUCCESS!`);
    console.log(`   Database: ${dbPath}`);
    console.log(`   Report:   ${reportPath}`);
  } catch (e) {
    console.error(`\n❌ Error: ${e.message}`);
    console.error(e.stack);
    collector.close();
    process.exit(1);
  }
})();
