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
          reject(new Error(`HTTP ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.setTimeout(10000, () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
    
    req.end();
  });
}

(async () => {
  try {
    console.log('Fetching first 3 closed markets...\n');
    const markets = await httpGet('/markets?limit=3&closed=true');
    
    if (Array.isArray(markets)) {
      markets.forEach((m, i) => {
        console.log(`\n=== Market ${i + 1} ===`);
        console.log('ID:', m.id || m.condition_id);
        console.log('Question:', m.question);
        console.log('End Date:', m.endDate || m.end_date_iso || m.closed_time);
        console.log('Volume:', m.volume);
        console.log('Keys:', Object.keys(m).join(', '));
      });
    } else {
      console.log('Response:', JSON.stringify(markets, null, 2));
    }
  } catch (e) {
    console.error('Error:', e.message);
  }
})();
