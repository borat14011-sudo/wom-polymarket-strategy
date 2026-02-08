// Check if recent closed markets have better resolution data
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

async function testRecentClosed() {
  console.log("=== TESTING RECENT CLOSED MARKETS ===\n");
  
  // Try sorting by closedTime desc to get recently closed
  console.log("Fetching recently closed markets...\n");
  
  const markets = await fetchJSON('https://gamma-api.polymarket.com/markets?closed=true&limit=20&offset=0');
  
  // Sort by closedTime (most recent first)
  markets.sort((a, b) => {
    const dateA = new Date(a.closedTime || a.endDate);
    const dateB = new Date(b.closedTime || b.endDate);
    return dateB - dateA;
  });
  
  console.log("20 Most Recently Closed Markets:\n");
  
  let marketsWithResolution = 0;
  let marketsWithoutResolution = 0;
  
  markets.slice(0, 20).forEach((market, i) => {
    const outcomes = JSON.parse(market.outcomes);
    const prices = JSON.parse(market.outcomePrices);
    
    const closedDate = new Date(market.closedTime || market.endDate);
    
    const hasResolution = prices.some(p => parseFloat(p) > 0.9) || 
                          prices.some(p => parseFloat(p) > 0 && parseFloat(p) < 1);
    
    if (hasResolution) {
      marketsWithResolution++;
      const winner = prices.map(p => parseFloat(p)).indexOf(Math.max(...prices.map(p => parseFloat(p))));
      console.log(`${i + 1}. ✓ ${market.question.substring(0, 50)}...`);
      console.log(`   Closed: ${closedDate.toISOString().split('T')[0]}`);
      console.log(`   Resolution: ${outcomes[winner]} (${parseFloat(prices[winner]).toFixed(4)})`);
    } else {
      marketsWithoutResolution++;
      console.log(`${i + 1}. ✗ ${market.question.substring(0, 50)}...`);
      console.log(`   Closed: ${closedDate.toISOString().split('T')[0]}`);
      console.log(`   Resolution: NO DATA (prices: ${prices})`);
    }
    console.log();
  });
  
  console.log("\n=== SUMMARY ===");
  console.log(`Markets with resolution data: ${marketsWithResolution}/20`);
  console.log(`Markets without resolution data: ${marketsWithoutResolution}/20`);
  console.log(`\nConclusion: ${marketsWithResolution > 0 ? 'Some closed markets have resolution data' : 'No resolution data in outcomePrices'}`);
  
  // Check for polygon subgraph
  console.log("\n\n=== CHECKING FOR SUBGRAPH/BLOCKCHAIN DATA ===\n");
  
  const subgraphEndpoints = [
    'https://api.thegraph.com/subgraphs/name/polymarket/matic-markets-5',
    'https://api.thegraph.com/subgraphs/name/polymarket/matic-markets-4',
    'https://api.thegraph.com/subgraphs/name/polymarket/polymarket',
  ];
  
  for (const endpoint of subgraphEndpoints) {
    try {
      const query = JSON.stringify({
        query: '{ fixedProductMarketMakers(first: 1, where: {collateralVolume_gt: 1000}) { id, question, answerFinalizedTimestamp, currentAnswer } }'
      });
      
      console.log(`Trying: ${endpoint}`);
      const result = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: query
      });
      
      if (result.ok) {
        const data = await result.json();
        console.log(`  ✓ Works! Sample data:`, JSON.stringify(data).substring(0, 200));
      }
    } catch (e) {
      console.log(`  ✗ Failed: ${e.message}`);
    }
  }
}

testRecentClosed().catch(console.error);
