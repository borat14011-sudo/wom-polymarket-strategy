#!/usr/bin/env node
// Step 1: Find all markets with endDate in 2025-2026 range
const https = require('https');
const fs = require('fs');

const START = new Date('2025-01-01T00:00:00Z');
const END = new Date('2026-02-28T23:59:59Z');
const DELAY = 250;

function get(offset) {
  return new Promise((resolve, reject) => {
    https.get(`https://gamma-api.polymarket.com/markets?limit=100&offset=${offset}`, (res) => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => {
        try { resolve(JSON.parse(d)); }
        catch (e) { reject(e); }
      });
    }).on('error', reject);
  });
}

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

(async () => {
  const found = [];
  let offset = 10000; // Start at Mar 2024 approx
  
  console.log('Scanning for 2025-2026 markets...');
  
  while (offset < 30000) {
    try {
      const markets = await get(offset);
      if (!markets || markets.length === 0) break;
      
      for (const m of markets) {
        const ed = new Date(m.endDate || '2020-01-01');
        if (ed >= START && ed <= END) {
          found.push({
            id: m.conditionId || m.id,
            question: m.question,
            endDate: m.endDate,
            closed: m.closed,
            volume: m.volume
          });
        } else if (ed > END && found.length > 0) {
          console.log(`Past end date at offset ${offset}`);
          offset = 99999; // break outer loop
          break;
        }
      }
      
      process.stdout.write(`Offset ${offset}, found ${found.length}...\r`);
      
      if (markets.length < 100) break;
      offset += 100;
      await sleep(DELAY);
      
    } catch (e) {
      console.error(`\nError at offset ${offset}:`, e.message);
      break;
    }
  }
  
  console.log(`\n\nFound ${found.length} markets in range`);
  
  const resolved = found.filter(m => m.closed);
  console.log(`${resolved.length} are closed/resolved`);
  
  // Sort by volume
  resolved.sort((a, b) => parseFloat(b.volume || 0) - parseFloat(a.volume || 0));
  
  fs.writeFileSync('markets_2025_2026.json', JSON.stringify(resolved, null, 2));
  console.log(`✓ Saved to markets_2025_2026.json`);
  
  console.log(`\nTop 5 by volume:`);
  resolved.slice(0, 5).forEach((m, i) => {
    console.log(`  ${i + 1}. $${parseFloat(m.volume || 0).toLocaleString()} - ${m.question.substring(0, 50)}`);
  });
})();
