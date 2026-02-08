/**
 * POLYMARKET DATA COLLECTION - 2 YEAR HISTORICAL BACKTEST
 * 
 * Fetches REAL historical data from Polymarket APIs:
 * - Markets API: https://gamma-api.polymarket.com/markets
 * - Price History: https://clob.polymarket.com/prices-history
 * 
 * Date Range: Jan 1, 2024 - Feb 7, 2026
 * Focus: RESOLVED markets with complete price history
 */

import axios from 'axios';
import { promises as fs } from 'fs';
import { format, subDays, parseISO } from 'date-fns';

const MARKETS_API = 'https://gamma-api.polymarket.com/markets';
const PRICES_API = 'https://clob.polymarket.com/prices-history';
const DATA_DIR = './data';
const RAW_DIR = `${DATA_DIR}/raw`;
const PROCESSED_DIR = `${DATA_DIR}/processed`;

// Date range for backtest
const START_DATE = '2024-01-01';
const END_DATE = '2026-02-07';

class PolymarketDataCollector {
  constructor() {
    this.markets = [];
    this.priceData = new Map();
    this.dataQualityIssues = [];
  }

  async initialize() {
    console.log('🚀 Initializing Polymarket Data Collector...\n');
    await this.ensureDirectories();
  }

  async ensureDirectories() {
    for (const dir of [DATA_DIR, RAW_DIR, PROCESSED_DIR]) {
      await fs.mkdir(dir, { recursive: true });
    }
  }

  /**
   * Fetch markets within our date range (both active and resolved)
   * Note: We fetch both because price history is more available for recently active markets
   */
  async fetchResolvedMarkets() {
    console.log('📊 Fetching markets with price history availability...\n');
    console.log('⚡ Strategy: Fetching high-volume markets (better data availability)\n');
    
    try {
      let allMarkets = [];
      
      // Fetch high-volume markets (more likely to have price data)
      for (const closed of [true, false]) {
        let offset = 0;
        const limit = 100;
        let batchCount = 0;
        const maxBatches = 3;  // Limit to 300 markets (150 closed + 150 active)

        while (batchCount < maxBatches) {
          console.log(`  Fetching ${closed ? 'closed' : 'active'} markets (batch ${batchCount + 1})...`);
          
          try {
            const response = await axios.get(MARKETS_API, {
              params: {
                limit,
                offset,
                closed: closed,
                order: 'volume',
                ascending: false
              },
              timeout: 30000
            });

            const markets = response.data;
            
            if (!markets || markets.length === 0) {
              break;
            }

            // Add all markets - we'll filter when collecting price data
            allMarkets = allMarkets.concat(markets);
            offset += limit;
            batchCount++;

            // Rate limiting
            await this.sleep(500);
          } catch (error) {
            console.log(`    ⚠️  Batch failed: ${error.message}`);
            break;
          }
        }
      }

      console.log(`✅ Fetched ${allMarkets.length} markets to analyze\n`);
      this.markets = allMarkets;

      // Save raw market data
      await fs.writeFile(
        `${RAW_DIR}/markets.json`,
        JSON.stringify(allMarkets, null, 2)
      );

      return allMarkets;

    } catch (error) {
      console.error('❌ Error fetching markets:', error.message);
      this.dataQualityIssues.push({
        issue: 'Market fetch failed',
        error: error.message
      });
      return [];
    }
  }

  /**
   * Fetch price history for a specific token
   */
  async fetchPriceHistory(tokenID, marketSlug) {
    try {
      const response = await axios.get(PRICES_API, {
        params: {
          market: tokenID,
          interval: '1h',  // Hourly data
          fidelity: 1      // Max resolution
        },
        timeout: 30000
      });

      if (!response.data || !response.data.history) {
        this.dataQualityIssues.push({
          issue: 'No price history',
          market: marketSlug,
          tokenID
        });
        return null;
      }

      return response.data.history;

    } catch (error) {
      this.dataQualityIssues.push({
        issue: 'Price fetch failed',
        market: marketSlug,
        tokenID,
        error: error.message
      });
      return null;
    }
  }

  /**
   * Collect price data for all markets
   */
  async collectPriceData() {
    console.log('📈 Collecting price history for markets...\n');

    const results = [];
    let successCount = 0;
    let failCount = 0;

    const maxMarkets = Math.min(this.markets.length, 100);  // Reduced for faster execution
    
    for (let i = 0; i < maxMarkets; i++) {
      const market = this.markets[i];
      
      console.log(`  [${i + 1}/${maxMarkets}] ${market.question.substring(0, 60)}...`);

      // Parse token IDs (they come as JSON string!)
      let tokenIds = [];
      try {
        if (typeof market.clobTokenIds === 'string') {
          tokenIds = JSON.parse(market.clobTokenIds);
        } else if (Array.isArray(market.clobTokenIds)) {
          tokenIds = market.clobTokenIds;
        } else if (market.tokens) {
          tokenIds = Array.isArray(market.tokens) ? market.tokens : [market.tokens];
        }
      } catch (e) {
        console.log('    ⚠️  Failed to parse token IDs');
        failCount++;
        continue;
      }

      const token = tokenIds[0];
      
      if (!token) {
        console.log('    ⚠️  No token ID found');
        failCount++;
        continue;
      }

      const priceHistory = await this.fetchPriceHistory(token, market.slug);

      if (priceHistory && priceHistory.length > 0) {
        results.push({
          market: {
            id: market.id,
            slug: market.slug,
            question: market.question,
            outcome: market.outcome,
            endDate: market.endDate,
            category: market.category,
            volume: market.volume
          },
          tokenID: token,
          priceHistory: priceHistory.map(p => ({
            timestamp: p.t,
            price: parseFloat(p.p),
            date: new Date(p.t * 1000).toISOString()
          }))
        });
        console.log(`    ✅ ${priceHistory.length} price points`);
        successCount++;
      } else {
        console.log('    ❌ No price data');
        failCount++;
      }

      // Rate limiting - be respectful to API
      await this.sleep(300);
    }

    console.log(`\n✅ Successfully collected: ${successCount} markets`);
    console.log(`❌ Failed: ${failCount} markets\n`);

    // Save processed data
    await fs.writeFile(
      `${PROCESSED_DIR}/price_data.json`,
      JSON.stringify(results, null, 2)
    );

    return results;
  }

  /**
   * Generate data quality report
   */
  async generateQualityReport() {
    console.log('📋 Generating data quality report...\n');

    const report = {
      collectionDate: new Date().toISOString(),
      dateRange: { start: START_DATE, end: END_DATE },
      totalMarkets: this.markets.length,
      marketsWithPriceData: this.priceData.size,
      dataQualityIssues: this.dataQualityIssues,
      coverage: {
        percentage: ((this.priceData.size / this.markets.length) * 100).toFixed(2),
        missing: this.markets.length - this.priceData.size
      }
    };

    await fs.writeFile(
      `${DATA_DIR}/quality_report.json`,
      JSON.stringify(report, null, 2)
    );

    console.log(`Total Markets: ${report.totalMarkets}`);
    console.log(`Markets with Price Data: ${report.marketsWithPriceData}`);
    console.log(`Coverage: ${report.coverage.percentage}%`);
    console.log(`Issues: ${report.dataQualityIssues.length}\n`);

    return report;
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Main execution
   */
  async run() {
    await this.initialize();
    
    const markets = await this.fetchResolvedMarkets();
    
    if (markets.length === 0) {
      console.error('❌ No markets found. Cannot proceed with backtest.');
      process.exit(1);
    }

    const priceData = await this.collectPriceData();
    this.priceData = new Map(priceData.map(d => [d.market.id, d]));

    const report = await this.generateQualityReport();

    console.log('✅ Data collection complete!\n');
    console.log('Next steps:');
    console.log('  - Review: data/quality_report.json');
    console.log('  - Markets: data/raw/markets.json');
    console.log('  - Prices: data/processed/price_data.json');
    console.log('  - Run: npm run backtest\n');

    return { markets, priceData, report };
  }
}

// Execute if run directly
if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  const collector = new PolymarketDataCollector();
  collector.run().catch(console.error);
}

export default PolymarketDataCollector;
