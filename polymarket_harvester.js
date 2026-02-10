#!/usr/bin/env node
/**
 * Continuous Data Harvester for Polymarket
 * Fetches market data every 5 minutes, analyzes every 30 minutes
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

// Configuration
const GAMMA_API = 'https://gamma-api.polymarket.com';
const DATA_FILE = path.join(__dirname, 'live_data_feed.jsonl');
const STATE_FILE = path.join(__dirname, '.harvester_state.json');
const REPORT_INTERVAL = 30 * 60 * 1000; // 30 minutes
const FETCH_INTERVAL = 5 * 60 * 1000;   // 5 minutes
const TOP_MARKETS_COUNT = 20;

// State tracking
let state = {
  lastPrices: {},      // marketId -> price
  lastVolumes: {},     // marketId -> volume
  lastReportTime: 0,
  startTime: Date.now(),
  fetchCount: 0
};

// Load previous state if exists
function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      const saved = JSON.parse(fs.readFileSync(STATE_FILE, 'utf8'));
      state = { ...state, ...saved };
      log('Loaded previous state');
    }
  } catch (e) {
    log('No previous state found, starting fresh');
  }
}

// Save state
function saveState() {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
  } catch (e) {
    log('Error saving state:', e.message);
  }
}

// Logging with timestamp
function log(...args) {
  const ts = new Date().toISOString();
  console.log(`[${ts}]`, ...args);
}

// HTTP GET helper
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https') ? https : http;
    const req = client.get(url, { timeout: 30000 }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve(data);
        }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request timeout'));
    });
  });
}

// Fetch markets from Gamma API
async function fetchMarkets() {
  try {
    // Fetch active markets with volume
    const markets = await httpGet(`${GAMMA_API}/markets?active=true&closed=false&liquidity_min=1000&limit=100`);
    return Array.isArray(markets) ? markets : markets.markets || [];
  } catch (e) {
    log('Error fetching markets:', e.message);
    return [];
  }
}

// Fetch order book for a market
async function fetchOrderBook(marketId) {
  try {
    const book = await httpGet(`${GAMMA_API}/order-books/${marketId}`);
    return book;
  } catch (e) {
    return null;
  }
}

// Calculate price change
function calculatePriceChange(marketId, currentPrice) {
  const lastPrice = state.lastPrices[marketId];
  if (!lastPrice || lastPrice === 0) return { change: 0, percent: 0 };
  const change = currentPrice - lastPrice;
  const percent = (change / lastPrice) * 100;
  return { change, percent };
}

// Calculate volume change
function calculateVolumeChange(marketId, currentVolume) {
  const lastVolume = state.lastVolumes[marketId];
  if (!lastVolume || lastVolume === 0) return { change: 0, multiplier: 1 };
  const change = currentVolume - lastVolume;
  const multiplier = currentVolume / lastVolume;
  return { change, multiplier };
}

// Append data to JSONL file
function appendData(record) {
  try {
    const line = JSON.stringify(record) + '\n';
    fs.appendFileSync(DATA_FILE, line);
  } catch (e) {
    log('Error writing data:', e.message);
  }
}

// Main data collection cycle
async function collectData() {
  const cycleStart = Date.now();
  state.fetchCount++;
  
  log(`=== CYCLE #${state.fetchCount} STARTED ===`);
  
  // 1. Fetch markets
  const markets = await fetchMarkets();
  if (markets.length === 0) {
    log('No markets fetched, skipping cycle');
    return;
  }
  
  // Sort by volume and take top 20
  const topMarkets = markets
    .sort((a, b) => (b.volume24hr || 0) - (a.volume24hr || 0))
    .slice(0, TOP_MARKETS_COUNT);
  
  log(`Fetched ${markets.length} markets, processing top ${topMarkets.length}`);
  
  const timestamp = new Date().toISOString();
  const opportunities = [];
  
  // 2. Process each market
  for (const market of topMarkets) {
    const marketId = market.id || market.slug;
    const currentPrice = market.midPoint || market.outcomePrices?.[0] || 0;
    const currentVolume = market.volume24hr || market.volume || 0;
    
    // 3. Calculate movements
    const priceMovement = calculatePriceChange(marketId, currentPrice);
    const volumeMovement = calculateVolumeChange(marketId, currentVolume);
    
    // 4. Fetch order book snapshot
    const orderBook = await fetchOrderBook(marketId);
    
    // Build record
    const record = {
      timestamp,
      cycle: state.fetchCount,
      marketId,
      market: {
        question: market.question,
        category: market.category,
        description: market.description?.substring(0, 200),
        endDate: market.endDate,
        liquidity: market.liquidity,
      },
      metrics: {
        price: currentPrice,
        priceChange: priceMovement.change,
        priceChangePercent: priceMovement.percent,
        volume24h: currentVolume,
        volumeChange: volumeMovement.change,
        volumeMultiplier: volumeMovement.multiplier,
      },
      orderBook: orderBook ? {
        bids: orderBook.bids?.slice(0, 5) || [],
        asks: orderBook.asks?.slice(0, 5) || [],
        spread: orderBook.spread,
      } : null,
      opportunity: null
    };
    
    // 4. Identify opportunities
    const isPriceSwing = Math.abs(priceMovement.percent) > 5;
    const isVolumeSpike = volumeMovement.multiplier > 1.5;
    const isNewMarket = !state.lastPrices[marketId];
    
    if (isPriceSwing || isVolumeSpike || isNewMarket) {
      record.opportunity = {
        type: isNewMarket ? 'NEW_MARKET' : isPriceSwing ? 'PRICE_SWING' : 'VOLUME_SPIKE',
        severity: Math.abs(priceMovement.percent) > 10 || volumeMovement.multiplier > 2 ? 'HIGH' : 'MEDIUM',
        description: isNewMarket 
          ? 'New market detected'
          : isPriceSwing 
            ? `Price moved ${priceMovement.percent.toFixed(2)}%`
            : `Volume spiked ${volumeMovement.multiplier.toFixed(2)}x`
      };
      opportunities.push(record);
    }
    
    // 5. Save to feed
    appendData(record);
    
    // Update state
    state.lastPrices[marketId] = currentPrice;
    state.lastVolumes[marketId] = currentVolume;
  }
  
  log(`Processed ${topMarkets.length} markets, found ${opportunities.length} opportunities`);
  
  // Save state after each cycle
  saveState();
  
  const cycleTime = Date.now() - cycleStart;
  log(`=== CYCLE COMPLETED in ${cycleTime}ms ===`);
  
  return opportunities;
}

// Analysis and reporting cycle
async function analyzeAndReport() {
  const now = Date.now();
  const timeSinceLastReport = now - state.lastReportTime;
  
  if (timeSinceLastReport < REPORT_INTERVAL) {
    return; // Not time yet
  }
  
  log('=== RUNNING 30-MINUTE ANALYSIS ===');
  
  // Read recent data from file
  let recentRecords = [];
  try {
    if (fs.existsSync(DATA_FILE)) {
      const lines = fs.readFileSync(DATA_FILE, 'utf8').trim().split('\n').filter(Boolean);
      // Get last 100 records
      recentRecords = lines.slice(-100).map(line => JSON.parse(line));
    }
  } catch (e) {
    log('Error reading data file:', e.message);
  }
  
  // Analyze for significant changes
  const hotMarkets = [];
  const marketGroups = {};
  
  // Group by market
  recentRecords.forEach(record => {
    if (!marketGroups[record.marketId]) {
      marketGroups[record.marketId] = [];
    }
    marketGroups[record.marketId].push(record);
  });
  
  // Analyze each market
  for (const [marketId, records] of Object.entries(marketGroups)) {
    if (records.length < 2) continue;
    
    const first = records[0];
    const last = records[records.length - 1];
    
    const priceChange = last.metrics.price - first.metrics.price;
    const priceChangePercent = first.metrics.price > 0 
      ? (priceChange / first.metrics.price) * 100 
      : 0;
    
    const volumeRatio = first.metrics.volume24h > 0
      ? last.metrics.volume24h / first.metrics.volume24h
      : 1;
    
    // Flag significant changes
    if (Math.abs(priceChangePercent) > 10 || volumeRatio > 2) {
      hotMarkets.push({
        marketId,
        question: last.market.question,
        category: last.market.category,
        priceChange: priceChangePercent,
        volumeMultiplier: volumeRatio,
        currentPrice: last.metrics.price,
        currentVolume: last.metrics.volume24h,
        flag: Math.abs(priceChangePercent) > 10 ? 'PRICE_SWING' : 'VOLUME_SPIKE'
      });
    }
  }
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    period: '30min',
    totalCycles: state.fetchCount,
    hotMarkets: hotMarkets.sort((a, b) => Math.abs(b.priceChange) - Math.abs(a.priceChange)),
    summary: {
      marketsTracked: Object.keys(state.lastPrices).length,
      priceSwings: hotMarkets.filter(m => m.flag === 'PRICE_SWING').length,
      volumeSpikes: hotMarkets.filter(m => m.flag === 'VOLUME_SPIKE').length,
    }
  };
  
  // Write report to file
  const reportFile = path.join(__dirname, `report_${Date.now()}.json`);
  fs.writeFileSync(reportFile, JSON.stringify(report, null, 2));
  
  // Console report
  log('\n🔥 HOT OPPORTUNITIES REPORT 🔥');
  log(`Period: Last 30 minutes`);
  log(`Cycles completed: ${state.fetchCount}`);
  log(`Markets tracked: ${report.summary.marketsTracked}`);
  log(`\nFlagged Markets (${hotMarkets.length}):`);
  
  hotMarkets.slice(0, 10).forEach((m, i) => {
    log(`  ${i+1}. [${m.flag}] ${m.question.substring(0, 60)}...`);
    log(`     Price: ${m.currentPrice.toFixed(3)} (${m.priceChange > 0 ? '+' : ''}${m.priceChange.toFixed(2)}%)`);
    log(`     Volume: ${m.currentVolume.toFixed(0)} (${m.volumeMultiplier.toFixed(2)}x)`);
  });
  
  // Report to parent agent via stdout marker
  console.log('\n=== REPORT_TO_MAIN_AGENT ===');
  console.log(JSON.stringify(report));
  console.log('=== END_REPORT ===\n');
  
  state.lastReportTime = now;
  saveState();
  
  log('=== ANALYSIS COMPLETE ===');
}

// Main loop
async function mainLoop() {
  log('╔══════════════════════════════════════╗');
  log('║   POLYMARKET DATA HARVESTER v1.0     ║');
  log('║   Collecting every 5 min             ║');
  log('║   Analyzing every 30 min             ║');
  log('╚══════════════════════════════════════╝');
  
  loadState();
  
  // Initial collection
  await collectData();
  state.lastReportTime = Date.now();
  
  // Set up intervals
  const fetchInterval = setInterval(async () => {
    try {
      await collectData();
    } catch (e) {
      log('Error in collection cycle:', e.message);
    }
  }, FETCH_INTERVAL);
  
  const analysisInterval = setInterval(async () => {
    try {
      await analyzeAndReport();
    } catch (e) {
      log('Error in analysis cycle:', e.message);
    }
  }, 60000); // Check every minute if it's time to report
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    log('\n🛑 SHUTDOWN SIGNAL RECEIVED');
    clearInterval(fetchInterval);
    clearInterval(analysisInterval);
    saveState();
    log('State saved. Goodbye!');
    process.exit(0);
  });
  
  process.on('SIGTERM', () => {
    log('\n🛑 TERMINATION SIGNAL RECEIVED');
    clearInterval(fetchInterval);
    clearInterval(analysisInterval);
    saveState();
    process.exit(0);
  });
  
  // Keep process alive
  log('\n✅ Harvester running. Press Ctrl+C to stop.\n');
}

// Start
mainLoop().catch(e => {
  log('Fatal error:', e);
  process.exit(1);
});
