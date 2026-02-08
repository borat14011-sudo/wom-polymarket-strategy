// Polymarket API exploration script
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

async function exploreAPI() {
  console.log("=== POLYMARKET API EXPLORATION ===\n");
  
  // 1. Get a closed market
  console.log("1. Fetching closed markets from Gamma API...");
  const markets = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=3');
  
  const firstMarket = markets[0];
  console.log(`\nSample closed market (ID: ${firstMarket.id}):`);
  console.log(`  Question: ${firstMarket.question}`);
  console.log(`  Closed: ${firstMarket.closed}`);
  console.log(`  Outcomes: ${firstMarket.outcomes}`);
  console.log(`  Outcome Prices: ${firstMarket.outcomePrices}`);
  
  // Check for resolution fields
  const resolutionFields = [
    'resolvedOutcome', 'winningOutcome', 'resolution', 'payoutNumerators',
    'resolved', 'result', 'winner', 'finalOutcome', 'resolutionValue'
  ];
  
  console.log("\n  Checking for resolution fields:");
  resolutionFields.forEach(field => {
    if (firstMarket[field] !== undefined) {
      console.log(`    ✓ ${field}: ${JSON.stringify(firstMarket[field])}`);
    }
  });
  
  // 2. Check CLOB API
  console.log("\n2. Checking CLOB API for market data...");
  const conditionId = firstMarket.conditionId;
  
  try {
    const clobData = await fetchJSON(`https://clob.polymarket.com/prices?market=${conditionId}`);
    console.log(`  CLOB prices for ${conditionId}:`, JSON.stringify(clobData).substring(0, 200));
  } catch (e) {
    console.log(`  CLOB API error: ${e.message}`);
  }
  
  // 3. Check if events have more data
  console.log("\n3. Checking events endpoint...");
  const events = await fetchJSON('https://gamma-api.polymarket.com/events?closed=true&limit=2');
  const firstEvent = events[0];
  
  console.log(`\nSample event (ID: ${firstEvent.id}):`);
  console.log(`  Title: ${firstEvent.title}`);
  console.log(`  Closed: ${firstEvent.closed}`);
  
  if (firstEvent.markets && firstEvent.markets.length > 0) {
    const eventMarket = firstEvent.markets[0];
    console.log(`\n  First market in event:`);
    console.log(`    Question: ${eventMarket.question}`);
    console.log(`    Outcome Prices: ${eventMarket.outcomePrices}`);
    
    resolutionFields.forEach(field => {
      if (eventMarket[field] !== undefined) {
        console.log(`    ✓ ${field}: ${JSON.stringify(eventMarket[field])}`);
      }
    });
  }
  
  // 4. Check for pagination info
  console.log("\n4. Checking pagination capabilities...");
  const largeBatch = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=100&offset=0');
  console.log(`  Fetched ${largeBatch.length} markets with limit=100`);
  
  // 5. Check if there are other API endpoints
  console.log("\n5. Testing potential endpoints...");
  const endpointsToTest = [
    'https://gamma-api.polymarket.com/markets?_sort=id&closed=true&limit=1',
    'https://data-api.polymarket.com/markets'
  ];
  
  for (const endpoint of endpointsToTest) {
    try {
      await fetchJSON(endpoint);
      console.log(`  ✓ ${endpoint} - works`);
    } catch (e) {
      console.log(`  ✗ ${endpoint} - failed`);
    }
  }
  
  // 6. Look for total count
  console.log("\n6. Estimating total closed markets...");
  const highOffset = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=1&offset=15000');
  console.log(`  Markets at offset 15000: ${highOffset.length > 0 ? 'exists' : 'none'}`);
  
  console.log("\n=== SUMMARY ===");
  console.log("- Gamma API supports: ?closed=true&limit=X&offset=Y");
  console.log("- Market objects include: id, question, conditionId, closed, outcomes, outcomePrices");
  console.log("- Resolution data needs further investigation (outcomePrices may indicate resolution)");
}

exploreAPI().catch(console.error);
