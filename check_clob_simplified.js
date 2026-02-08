// Check CLOB simplified-markets for better resolution data
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

async function checkCLOBSimplified() {
  console.log("=== CHECKING CLOB SIMPLIFIED MARKETS ===\n");
  
  // Get closed markets from CLOB
  console.log("Fetching closed markets from CLOB simplified-markets...\n");
  
  const markets = await fetchJSON('https://clob.polymarket.com/simplified-markets?closed=true&limit=10');
  
  console.log(`Fetched ${markets.length} closed markets\n`);
  
  if (markets.length > 0) {
    const firstMarket = markets[0];
    
    console.log("Sample market structure:");
    console.log("Available fields:", Object.keys(firstMarket));
    console.log();
    
    // Check for resolution fields
    console.log("Checking for resolution-related fields:\n");
    
    markets.slice(0, 5).forEach((market, i) => {
      console.log(`${i + 1}. ${market.question ? market.question.substring(0, 50) : 'N/A'}...`);
      
      const resFields = [
        'outcome', 'resolvedOutcome', 'winner', 'winningOutcome',
        'payoutNumerators', 'outcomes', 'outcomePrices', 'resolution'
      ];
      
      resFields.forEach(field => {
        if (market[field] !== undefined) {
          const val = typeof market[field] === 'object' ? JSON.stringify(market[field]) : market[field];
          console.log(`   ${field}: ${val.toString().substring(0, 80)}`);
        }
      });
      
      console.log();
    });
  }
  
  // Try sampling-markets
  console.log("\n=== CHECKING SAMPLING MARKETS ===\n");
  
  const samplingMarkets = await fetchJSON('https://clob.polymarket.com/sampling-markets');
  
  console.log(`Fetched ${samplingMarkets.length} sampling markets`);
  
  if (samplingMarkets.length > 0) {
    console.log("\nSample market fields:", Object.keys(samplingMarkets[0]));
    
    const closedSampling = samplingMarkets.filter(m => m.closed);
    console.log(`Closed sampling markets: ${closedSampling.length}`);
    
    if (closedSampling.length > 0) {
      const sample = closedSampling[0];
      console.log("\nSample closed market from sampling:");
      console.log(`  Question: ${sample.question}`);
      console.log(`  Closed: ${sample.closed}`);
      
      const resFields = ['outcome', 'resolvedOutcome', 'winner', 'outcomePrices', 'outcomes'];
      resFields.forEach(field => {
        if (sample[field] !== undefined) {
          console.log(`  ${field}: ${JSON.stringify(sample[field])}`);
        }
      });
    }
  }
  
  // Calculate data availability
  console.log("\n\n=== DATA AVAILABILITY ASSESSMENT ===\n");
  
  const gammaMarkets = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=100');
  
  let withResolution = 0;
  let withoutResolution = 0;
  
  gammaMarkets.forEach(market => {
    const prices = JSON.parse(market.outcomePrices || '["0", "0"]');
    const hasData = prices.some(p => parseFloat(p) > 0.5);
    
    if (hasData) {
      withResolution++;
    } else {
      withoutResolution++;
    }
  });
  
  console.log("Sample of 100 closed markets from Gamma API:");
  console.log(`  With resolution data: ${withResolution} (${(withResolution/100*100).toFixed(1)}%)`);
  console.log(`  Without resolution data: ${withoutResolution} (${(withoutResolution/100*100).toFixed(1)}%)`);
  console.log();
  console.log("Conclusion:");
  if (withResolution >= 50) {
    console.log("  ✓ Majority of markets have resolution data available");
  } else if (withResolution >= 25) {
    console.log("  ~ Partial resolution data available (~50%)");
  } else {
    console.log("  ✗ Most markets lack resolution data in API");
  }
}

checkCLOBSimplified().catch(console.error);
