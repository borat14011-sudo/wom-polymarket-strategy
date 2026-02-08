/**
 * Diagnostic script to test Polymarket API endpoints
 */

import axios from 'axios';

async function testAPIs() {
  console.log('🔍 Testing Polymarket API Endpoints...\n');

  // Test 1: Get a few active markets
  console.log('1. Testing Markets API (active markets)...');
  try {
    const response = await axios.get('https://gamma-api.polymarket.com/markets', {
      params: {
        limit: 5,
        closed: false  // Active markets
      }
    });
    console.log(`✅ Found ${response.data.length} active markets`);
    if (response.data.length > 0) {
      const market = response.data[0];
      console.log(`   Example: "${market.question}"`);
      console.log(`   Full market structure: ${JSON.stringify(market, null, 2).substring(0, 1000)}...`);
      
      // Find token ID - clobTokenIds is a JSON string!
      let tokenIds = null;
      if (market.clobTokenIds) {
        try {
          tokenIds = JSON.parse(market.clobTokenIds);
        } catch {
          tokenIds = market.clobTokenIds;
        }
      } else if (market.tokens) {
        tokenIds = market.tokens;
      }
      
      const tokenId = Array.isArray(tokenIds) ? tokenIds[0] : tokenIds;
      console.log(`   Token ID to use: ${tokenId}`);
      
      // Test 2: Try to get price history for this active market
      console.log('\n2. Testing Price History API (active market)...');
      if (tokenId) {
        // If tokenId is an array, use the first one
        const actualTokenId = Array.isArray(tokenId) ? tokenId[0] : tokenId;
        console.log(`   Using token ID: ${actualTokenId}`);
        
        try {
          const priceResponse = await axios.get('https://clob.polymarket.com/prices-history', {
            params: {
              market: actualTokenId,
              interval: '1h',
              fidelity: 1
            }
          });
          
          if (priceResponse.data && priceResponse.data.history) {
            console.log(`✅ Got ${priceResponse.data.history.length} price points`);
            console.log(`   Sample: ${JSON.stringify(priceResponse.data.history.slice(0, 3))}`);
          } else {
            console.log('❌ No history field in response');
            console.log('   Response:', JSON.stringify(priceResponse.data));
          }
        } catch (error) {
          console.log(`❌ Price API failed: ${error.message}`);
          if (error.response) {
            console.log(`   Status: ${error.response.status}`);
            console.log(`   Data: ${JSON.stringify(error.response.data)}`);
          }
        }
      } else {
        console.log('❌ No token ID found');
      }
    }
  } catch (error) {
    console.log(`❌ Markets API failed: ${error.message}`);
  }

  // Test 3: Try alternative price endpoint
  console.log('\n3. Testing alternative endpoints...');
  try {
    // Try gamma API for prices
    const response = await axios.get('https://gamma-api.polymarket.com/prices', {
      params: {
        limit: 5
      }
    });
    console.log(`✅ Gamma prices API response: ${JSON.stringify(response.data).substring(0, 200)}...`);
  } catch (error) {
    console.log(`❌ Gamma prices failed: ${error.message}`);
  }

  // Test 4: Check what endpoints are available
  console.log('\n4. Testing CLOB API base...');
  try {
    const response = await axios.get('https://clob.polymarket.com/');
    console.log(`✅ CLOB base response: ${response.status}`);
  } catch (error) {
    console.log(`Info: CLOB base returned ${error.response?.status || error.message}`);
  }

  console.log('\n✅ Diagnostic complete');
}

testAPIs().catch(console.error);
