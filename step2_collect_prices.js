#!/usr/bin/env node
// Step 2: Collect price history for all found markets
const https = require('https');
const fs = require('fs');
const sqlite3 = require('better-sqlite3');

const DELAY = 200; // ms between requests
const MAX_RETRIES = 3;

// Initialize database
const db = new sqlite3('historical_2025_2026.db');

db.exec(`
  CREATE TABLE IF NOT EXISTS markets (
    market_id TEXT PRIMARY KEY,
    question TEXT,
    end_date_iso TEXT,
    volume REAL,
    closed BOOLEAN
  )
`);

db.exec(`
  CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    price REAL NOT NULL,
    volume REAL,
    FOREIGN KEY (market_id) REFERENCES markets(market_id)
  )
`);

db.exec(`
  CREATE INDEX IF NOT EXISTS idx_price_market_time 
  ON price_history(market_id, timestamp)
`);

function getPrices(conditionId) {
  return new Promise((resolve, reject) => {
    https.get(`https://gamma-api.polymarket.com/prices/${conditionId}`, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        if (res.statusCode === 200) {
          try { 
            const json = JSON.parse(d);
            resolve(Array.isArray(json) ? json : (json.history || []));
          } catch (e) { 
            resolve([]); 
          }
        } else {
          resolve([]);
        }
      });
    }).on('error', () => resolve([]));
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

const insertMarket = db.prepare(`
  INSERT OR REPLACE INTO markets (market_id, question, end_date_iso, volume, closed)
  VALUES (?, ?, ?, ?, ?)
`);

const insertPrice = db.prepare(`
  INSERT INTO price_history (market_id, timestamp, price, volume)
  VALUES (?, ?, ?, ?)
`);

(async () => {
  const markets = JSON.parse(fs.readFileSync('markets_2025_2026.json', 'utf8'));
  console.log(`Loading ${markets.length} markets for price collection...\n`);
  
  let processed = 0;
  let totalPrices = 0;
  let skipped = 0;
  const errors = [];
  
  for (const market of markets) {
    processed++;
    
    // Store market metadata
    insertMarket.run(
      market.id,
      market.question,
      market.endDate,
      parseFloat(market.volume || 0),
      market.closed ? 1 : 0
    );
    
    // Fetch price history
    const prices = await getPrices(market.id);
    
    if (prices && prices.length > 0) {
      for (const p of prices) {
        const ts = p.t || p.timestamp;
        const price = p.p || p.price;
        const vol = p.v || p.volume;
        
        if (ts && price !== undefined) {
          insertPrice.run(market.id, parseInt(ts), parseFloat(price), vol ? parseFloat(vol) : null);
        }
      }
      totalPrices += prices.length;
      
      if (processed % 50 === 0 || processed <= 10) {
        console.log(`[${processed}/${markets.length}] ${market.question.substring(0, 50)}...`);
        console.log(`  ✓ ${prices.length} price points | Total: ${totalPrices.toLocaleString()}`);
      }
    } else {
      skipped++;
      if (processed <= 10) {
        console.log(`[${processed}/${markets.length}] ${market.question.substring(0, 50)}...`);
        console.log(`  ⚠️  No price data`);
      }
    }
    
    await sleep(DELAY);
  }
  
  console.log(`\n${'='.repeat(60)}`);
  console.log('📊 COLLECTION COMPLETE');
  console.log(`${'='.repeat(60)}`);
  console.log(`Markets processed:      ${processed}`);
  console.log(`Total price points:     ${totalPrices.toLocaleString()}`);
  console.log(`Markets w/o prices:     ${skipped}`);
  console.log(`Avg prices per market:  ${(totalPrices / processed).toFixed(1)}`);
  console.log(`${'='.repeat(60)}`);
  
  db.close();
  console.log(`\n✓ Database saved: historical_2025_2026.db`);
})();
