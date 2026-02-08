/**
 * Test if whale/insider tracking data is available for backtesting
 */

import axios from 'axios';

async function testWhaleDataSources() {
  console.log('🔍 Testing Whale/Insider Data Availability...\n');

  // Test 1: Polymarket Analytics API
  console.log('1. Testing Polymarket Analytics...');
  try {
    // Try to access trader data
    const traderAddress = '0x53d2d3c78597a78402d4db455a680da7ef560c3f'; // abeautifulmind
    
    // Check if they have an API
    const endpoints = [
      `https://polymarketanalytics.com/api/traders/${traderAddress}`,
      `https://api.polymarketanalytics.com/traders/${traderAddress}`,
      `https://polymarketanalytics.com/traders/${traderAddress}`
    ];

    for (const url of endpoints) {
      try {
        const response = await axios.get(url, { timeout: 5000 });
        console.log(`✅ Found data at ${url}`);
        console.log(`   Sample: ${JSON.stringify(response.data).substring(0, 200)}...`);
        break;
      } catch (error) {
        console.log(`   ❌ ${url} - ${error.response?.status || error.message}`);
      }
    }
  } catch (error) {
    console.log(`❌ Polymarket Analytics failed: ${error.message}`);
  }

  // Test 2: Check for blockchain data (via gamma API or direct)
  console.log('\n2. Testing blockchain/on-chain data access...');
  try {
    // Polymarket uses Polygon (MATIC) blockchain
    // Try to get historical trades for a market
    
    const response = await axios.get('https://gamma-api.polymarket.com/markets', {
      params: { limit: 1 }
    });
    
    const market = response.data[0];
    console.log(`   Testing market: "${market.question}"`);
    console.log(`   Condition ID: ${market.conditionId}`);
    
    // Try to get trade history
    const tradeEndpoints = [
      `https://gamma-api.polymarket.com/trades?market=${market.id}`,
      `https://clob.polymarket.com/trades?market=${market.id}`,
      `https://gamma-api.polymarket.com/markets/${market.id}/trades`
    ];

    for (const url of tradeEndpoints) {
      try {
        const tradeResponse = await axios.get(url, { timeout: 5000 });
        console.log(`✅ Trade data available at ${url}`);
        console.log(`   Sample: ${JSON.stringify(tradeResponse.data).substring(0, 200)}...`);
        break;
      } catch (error) {
        console.log(`   ❌ ${url} - ${error.response?.status || error.message}`);
      }
    }
  } catch (error) {
    console.log(`❌ Blockchain data test failed: ${error.message}`);
  }

  // Test 3: Check Polywhaler
  console.log('\n3. Testing Polywhaler access...');
  try {
    const response = await axios.get('https://www.polywhaler.com/', { timeout: 5000 });
    console.log(`✅ Polywhaler accessible (status ${response.status})`);
    console.log('   Note: Likely requires authentication/payment for API access');
  } catch (error) {
    console.log(`   Status: ${error.response?.status || error.message}`);
  }

  // Test 4: Check if Polysights has historical data
  console.log('\n4. Checking Polysights/Insider Finder...');
  try {
    // Polysights likely posts on X/Twitter
    // We'd need Twitter API access to get historical flagged trades
    console.log('   ⚠️  Historical flagged trades require:');
    console.log('       - Twitter API access to Polysights account');
    console.log('       - OR manual scraping of their X feed');
    console.log('       - OR direct API from Polysights (if they offer one)');
  } catch (error) {
    console.log(`   Error: ${error.message}`);
  }

  console.log('\n5. Summary - Data Availability for Strategy #7:');
  console.log('   ━'.repeat(60));
  console.log('   Polymarket Analytics: Unknown (need to check if they expose API)');
  console.log('   Blockchain data: Potentially available via Polygon blockchain');
  console.log('   Polysights flags: Requires Twitter API or manual collection');
  console.log('   Historical whale positions: Unknown');
  console.log('\n   Bottom line: Investigate further or proceed with forward testing');

  console.log('\n✅ Diagnostic complete');
}

testWhaleDataSources().catch(console.error);
