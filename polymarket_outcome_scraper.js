#!/usr/bin/env node

/**
 * Polymarket Outcome Scraper
 * 
 * Fetches historical market outcomes from Polymarket's Gamma API
 * for closed markets.
 * 
 * Usage:
 *   node polymarket_outcome_scraper.js [--limit=N] [--output=file.json]
 */

const https = require('https');
const fs = require('fs');

// Configuration
const CONFIG = {
  baseUrl: 'https://gamma-api.polymarket.com',
  batchSize: 100,
  parallelRequests: 5,
  delayBetweenBatches: 100, // ms
  retryAttempts: 3,
  retryDelay: 1000, // ms
};

// CLI Arguments
const args = process.argv.slice(2).reduce((acc, arg) => {
  const [key, value] = arg.split('=');
  acc[key.replace('--', '')] = value || true;
  return acc;
}, {});

const LIMIT = parseInt(args.limit) || Infinity;
const OUTPUT_FILE = args.output || 'polymarket_outcomes.json';

/**
 * Fetch JSON from URL with retry logic
 */
async function fetchJSON(url, attempt = 1) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      
      res.on('data', chunk => data += chunk);
      
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          if (attempt < CONFIG.retryAttempts) {
            console.warn(`Parse error, retrying... (${attempt}/${CONFIG.retryAttempts})`);
            setTimeout(() => {
              fetchJSON(url, attempt + 1).then(resolve).catch(reject);
            }, CONFIG.retryDelay * attempt);
          } else {
            reject(new Error(`Parse failed after ${CONFIG.retryAttempts} attempts: ${e.message}`));
          }
        }
      });
      
    }).on('error', (err) => {
      if (attempt < CONFIG.retryAttempts) {
        console.warn(`Network error, retrying... (${attempt}/${CONFIG.retryAttempts})`);
        setTimeout(() => {
          fetchJSON(url, attempt + 1).then(resolve).catch(reject);
        }, CONFIG.retryDelay * attempt);
      } else {
        reject(err);
      }
    });
  });
}

/**
 * Fetch closed markets from Gamma API
 */
async function fetchClosedMarkets(limit = 100, offset = 0) {
  const url = `${CONFIG.baseUrl}/markets?closed=true&limit=${limit}&offset=${offset}`;
  return fetchJSON(url);
}

/**
 * Parse resolution outcome from market data
 */
function parseResolution(market) {
  try {
    const outcomes = JSON.parse(market.outcomes || '[]');
    const prices = JSON.parse(market.outcomePrices || '["0"]');
    
    const priceValues = prices.map(p => parseFloat(p));
    const maxPrice = Math.max(...priceValues);
    const winnerIndex = priceValues.indexOf(maxPrice);
    
    // Consider resolved if max price > 0.5
    const hasResolution = maxPrice > 0.5;
    
    // For scalar markets, outcome is a value not an option
    const isScalar = market.marketType === 'scalar';
    
    return {
      marketId: market.id,
      conditionId: market.conditionId,
      question: market.question,
      slug: market.slug,
      outcomes: outcomes,
      outcomePrices: priceValues,
      winner: hasResolution && !isScalar ? outcomes[winnerIndex] : null,
      winnerIndex: hasResolution ? winnerIndex : null,
      winnerProbability: hasResolution ? maxPrice : null,
      hasResolutionData: hasResolution,
      marketType: market.marketType,
      category: market.category,
      volume: parseFloat(market.volume || 0),
      closed: market.closed,
      closedTime: market.closedTime,
      endDate: market.endDate,
      isScalar: isScalar,
    };
  } catch (e) {
    console.error(`Error parsing market ${market.id}:`, e.message);
    return {
      marketId: market.id,
      error: e.message,
      hasResolutionData: false,
    };
  }
}

/**
 * Sleep utility
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Main scraper function
 */
async function scrapeOutcomes() {
  console.log('🚀 Starting Polymarket Outcome Scraper\n');
  console.log(`Configuration:`);
  console.log(`  Batch size: ${CONFIG.batchSize}`);
  console.log(`  Parallel requests: ${CONFIG.parallelRequests}`);
  console.log(`  Limit: ${LIMIT === Infinity ? 'All markets' : LIMIT}`);
  console.log(`  Output: ${OUTPUT_FILE}\n`);
  
  const results = [];
  let offset = 0;
  let totalFetched = 0;
  let withResolution = 0;
  let withoutResolution = 0;
  
  const startTime = Date.now();
  
  try {
    while (totalFetched < LIMIT) {
      // Fetch batch
      console.log(`\n📦 Fetching markets ${offset} to ${offset + CONFIG.batchSize}...`);
      
      const markets = await fetchClosedMarkets(CONFIG.batchSize, offset);
      
      if (!markets || markets.length === 0) {
        console.log('✅ No more markets to fetch');
        break;
      }
      
      // Parse results
      const parsed = markets.map(parseResolution);
      results.push(...parsed);
      
      // Update stats
      totalFetched += markets.length;
      const batchWithRes = parsed.filter(m => m.hasResolutionData).length;
      const batchWithoutRes = parsed.length - batchWithRes;
      
      withResolution += batchWithRes;
      withoutResolution += batchWithoutRes;
      
      console.log(`   ✓ Fetched ${markets.length} markets`);
      console.log(`   ✓ With resolution: ${batchWithRes}`);
      console.log(`   ✗ Without resolution: ${batchWithoutRes}`);
      console.log(`   Total progress: ${totalFetched} markets`);
      
      offset += CONFIG.batchSize;
      
      // Delay between batches
      if (markets.length === CONFIG.batchSize) {
        await sleep(CONFIG.delayBetweenBatches);
      }
    }
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
    
    console.log('\n\n📊 SCRAPING COMPLETE!\n');
    console.log('Statistics:');
    console.log(`  Total markets: ${totalFetched}`);
    console.log(`  With resolution: ${withResolution} (${(withResolution/totalFetched*100).toFixed(1)}%)`);
    console.log(`  Without resolution: ${withoutResolution} (${(withoutResolution/totalFetched*100).toFixed(1)}%)`);
    console.log(`  Time elapsed: ${elapsed}s`);
    console.log(`  Average speed: ${(totalFetched / elapsed).toFixed(1)} markets/sec`);
    
    // Save results
    console.log(`\n💾 Saving to ${OUTPUT_FILE}...`);
    
    const output = {
      metadata: {
        scrapedAt: new Date().toISOString(),
        totalMarkets: totalFetched,
        withResolution: withResolution,
        withoutResolution: withoutResolution,
        coveragePercent: (withResolution/totalFetched*100).toFixed(2),
        timeElapsedSeconds: parseFloat(elapsed),
      },
      markets: results
    };
    
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(output, null, 2));
    
    console.log('✅ Done!\n');
    
    // Sample output
    console.log('Sample resolved markets:');
    const sampleResolved = results.filter(m => m.hasResolutionData).slice(0, 3);
    sampleResolved.forEach((m, i) => {
      console.log(`\n${i + 1}. ${m.question}`);
      console.log(`   Winner: ${m.winner || 'N/A'} (${(m.winnerProbability * 100).toFixed(2)}%)`);
      console.log(`   Closed: ${m.closedTime}`);
    });
    
  } catch (error) {
    console.error('\n❌ Error during scraping:', error);
    
    // Save partial results
    if (results.length > 0) {
      console.log(`\n💾 Saving ${results.length} partial results to ${OUTPUT_FILE}.partial...`);
      fs.writeFileSync(`${OUTPUT_FILE}.partial`, JSON.stringify(results, null, 2));
    }
    
    process.exit(1);
  }
}

// Run scraper
if (require.main === module) {
  scrapeOutcomes();
}

module.exports = { fetchClosedMarkets, parseResolution };
