// Check how to extract resolution outcomes
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

async function checkResolutions() {
  console.log("=== CHECKING RESOLUTION DATA ===\n");
  
  // Get some closed markets
  const markets = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=10');
  
  console.log("Analyzing outcome prices for closed markets:\n");
  
  markets.forEach((market, i) => {
    const outcomes = JSON.parse(market.outcomes);
    const prices = JSON.parse(market.outcomePrices);
    
    console.log(`${i + 1}. ${market.question.substring(0, 60)}...`);
    console.log(`   ID: ${market.id}`);
    outcomes.forEach((outcome, j) => {
      const price = parseFloat(prices[j]);
      const status = price > 0.9 ? '✓ WINNER' : price < 0.1 ? '✗ LOSER' : '? UNCLEAR';
      console.log(`   ${status} ${outcome}: ${price.toFixed(6)}`);
    });
    
    // Determine winner
    const winner = prices.map(p => parseFloat(p)).indexOf(Math.max(...prices.map(p => parseFloat(p))));
    if (parseFloat(prices[winner]) > 0.5) {
      console.log(`   => Resolved to: ${outcomes[winner]}`);
    } else {
      console.log(`   => Resolution unclear (both prices ~0.5?)`);
    }
    console.log();
  });
  
  // Check if there are any other fields that might help
  console.log("\n=== CHECKING FOR OTHER RESOLUTION INDICATORS ===\n");
  
  const marketWithAllFields = markets[0];
  const allKeys = Object.keys(marketWithAllFields);
  
  console.log("All available fields in market object:");
  allKeys.forEach(key => {
    const value = marketWithAllFields[key];
    const valueStr = typeof value === 'string' ? value : JSON.stringify(value);
    const display = valueStr.length > 80 ? valueStr.substring(0, 80) + '...' : valueStr;
    console.log(`  ${key}: ${display}`);
  });
  
  // Check CLOB token pricing
  console.log("\n\n=== CHECKING CLOB TOKEN ENDPOINT ===\n");
  
  const tokenIds = JSON.parse(markets[0].clobTokenIds);
  console.log(`Token IDs for market ${markets[0].id}:`);
  console.log(`  Token 0: ${tokenIds[0]}`);
  console.log(`  Token 1: ${tokenIds[1]}`);
  
  try {
    const tokenPrice = await fetchJSON(`https://clob.polymarket.com/prices-history?market=${markets[0].conditionId}&interval=max`);
    console.log("\nPrice history data:", JSON.stringify(tokenPrice).substring(0, 200));
  } catch (e) {
    console.log("\nPrice history not available:", e.message);
  }
}

checkResolutions().catch(console.error);
