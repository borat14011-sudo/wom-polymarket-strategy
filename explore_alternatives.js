// Explore alternative sources for resolution data
const https = require('https');

function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

async function exploreAlternatives() {
  console.log("=== EXPLORING ALTERNATIVE DATA SOURCES ===\n");
  
  // 1. Try Strapi API with different hosts
  console.log("1. Testing Strapi API endpoints:");
  const strapiHosts = [
    'https://strapi-matic.polymarket.com',
    'https://strapi.polymarket.com',
    'https://polymarket-strapi.herokuapp.com',
    'https://api.polymarket.com'
  ];
  
  for (const host of strapiHosts) {
    try {
      const result = await fetchJSON(`${host}/markets?_limit=1`);
      console.log(`  ✓ ${host} - Works! Fields:`, Object.keys(result[0] || result));
    } catch (e) {
      console.log(`  ✗ ${host} - ${e.message}`);
    }
  }
  
  // 2. Check for dedicated resolution API
  console.log("\n2. Testing resolution-specific endpoints:");
  const resolutionEndpoints = [
    'https://gamma-api.polymarket.com/resolutions',
    'https://gamma-api.polymarket.com/resolved',
    'https://gamma-api.polymarket.com/outcomes',
    'https://data.polymarket.com/markets'
  ];
  
  for (const endpoint of resolutionEndpoints) {
    try {
      await fetchJSON(endpoint);
      console.log(`  ✓ ${endpoint} - Works!`);
    } catch (e) {
      console.log(`  ✗ ${endpoint} - ${e.message.substring(0, 50)}`);
    }
  }
  
  // 3. Check CLOB API documentation
  console.log("\n3. Testing CLOB API endpoints:");
  const clobEndpoints = [
    'https://clob.polymarket.com/sampling-markets',
    'https://clob.polymarket.com/sampling-simplified-markets',
    'https://clob.polymarket.com/simplified-markets?closed=true&limit=5'
  ];
  
  for (const endpoint of clobEndpoints) {
    try {
      const result = await fetchJSON(endpoint);
      console.log(`  ✓ ${endpoint} - Works!`);
      if (Array.isArray(result) && result.length > 0) {
        const sample = result[0];
        console.log(`    Sample fields:`, Object.keys(sample).slice(0, 10).join(', '));
        
        // Check for resolution fields
        const resFields = ['outcome', 'resolvedOutcome', 'winner', 'payoutNumerators'];
        resFields.forEach(field => {
          if (sample[field] !== undefined) {
            console.log(`    ✓ Has ${field}: ${JSON.stringify(sample[field])}`);
          }
        });
      }
    } catch (e) {
      console.log(`  ✗ ${endpoint} - Failed`);
    }
  }
  
  // 4. Test if individual market queries reveal more
  console.log("\n4. Testing individual market queries:");
  const testMarketId = '40'; // Trump 2020 election - we know this resolved
  
  const individualEndpoints = [
    `https://gamma-api.polymarket.com/markets/${testMarketId}`,
    `https://gamma-api.polymarket.com/market/${testMarketId}`,
  ];
  
  for (const endpoint of individualEndpoints) {
    try {
      const result = await fetchJSON(endpoint);
      console.log(`  ✓ ${endpoint}`);
      
      if (result.outcomePrices) {
        console.log(`    outcomePrices: ${result.outcomePrices}`);
      }
      
      // Check for any resolution-related fields
      const allKeys = Object.keys(result);
      const resKeys = allKeys.filter(k => 
        k.toLowerCase().includes('resol') || 
        k.toLowerCase().includes('outcome') ||
        k.toLowerCase().includes('winner') ||
        k.toLowerCase().includes('payout')
      );
      
      if (resKeys.length > 0) {
        console.log(`    Resolution-related fields:`, resKeys);
        resKeys.forEach(key => {
          console.log(`      ${key}: ${JSON.stringify(result[key])}`);
        });
      }
    } catch (e) {
      console.log(`  ✗ ${endpoint} - ${e.message.substring(0, 50)}`);
    }
  }
  
  console.log("\n\n=== RATE LIMITING CHECK ===\n");
  console.log("Testing burst requests...");
  
  const startTime = Date.now();
  const promises = [];
  
  for (let i = 0; i < 10; i++) {
    promises.push(fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=1&offset=' + i));
  }
  
  try {
    await Promise.all(promises);
    const elapsed = Date.now() - startTime;
    console.log(`✓ 10 parallel requests completed in ${elapsed}ms`);
    console.log(`  Average: ${(elapsed / 10).toFixed(0)}ms per request`);
    console.log(`  No rate limiting detected (yet)`);
  } catch (e) {
    console.log(`✗ Rate limited or error: ${e.message}`);
  }
}

exploreAlternatives().catch(console.error);
