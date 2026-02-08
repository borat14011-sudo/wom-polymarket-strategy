#!/usr/bin/env node
const https = require('https');

function httpGet(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'gamma-api.polymarket.com',
      path: path,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
            reject(new Error(`JSON parse error: ${e.message}`));
          }
        } else {
          reject(new Error(`HTTP ${res.statusCode}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('Timeout'));
    });
    
    req.end();
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

(async () => {
  try {
    // Binary search to find where 2025 markets start
    const offsets = [10000, 12000, 14000, 16000, 18000, 20000];
    
    for (const offset of offsets) {
      console.log(`\nChecking offset ${offset}...`);
      await sleep(500);
      
      const markets = await httpGet(`/markets?limit=3&offset=${offset}&closed=true`);
      if (Array.isArray(markets) && markets.length > 0) {
        markets.forEach((m, i) => {
          console.log(`  ${i + 1}. ${m.endDate} - ${m.question.substring(0, 50)}`);
        });
      } else {
        console.log('  No more markets or empty response');
        break;
      }
    }
  } catch (e) {
    console.error('Error:', e.message);
  }
})();
