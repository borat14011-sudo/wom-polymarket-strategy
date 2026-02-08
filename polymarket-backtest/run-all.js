/**
 * MASTER EXECUTION SCRIPT - Run full 2-year backtest pipeline
 */

import PolymarketDataCollector from './src/01-collect-data.js';
import BacktestEngine from './src/02-run-backtests.js';
import PortfolioAnalyzer from './src/03-analyze-portfolio.js';
import ChartGenerator from './src/04-generate-charts.js';
import PresentationBuilder from './src/05-build-presentation.js';
import generateReport from './src/06-generate-report.js';
import { promises as fs } from 'fs';

const PROCESSED_DIR = './data/processed';
const RESULTS_DIR = './results';

async function main() {
  console.log('\n' + '='.repeat(80));
  console.log('🚀 POLYMARKET 2-YEAR HISTORICAL BACKTEST - FULL PIPELINE');
  console.log('='.repeat(80));
  console.log('\n📅 Period: January 2024 - February 2026');
  console.log('📊 Strategies: 6 distinct trading strategies');
  console.log('💰 Initial Capital: $10,000');
  console.log('⚡ Real historical data from Polymarket CLOB API\n');

  const startTime = Date.now();

  try {
    // STEP 1: Data Collection
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 1/6: DATA COLLECTION');
    console.log('─'.repeat(80));
    
    const collector = new PolymarketDataCollector();
    const { markets, priceData, report: qualityReport } = await collector.run();
    
    console.log(`\n✅ Step 1 complete: ${priceData.size} markets with price data\n`);

    // STEP 2: Run Backtests
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 2/6: STRATEGY BACKTESTS');
    console.log('─'.repeat(80));
    
    const priceDataArray = Array.from(priceData.values());
    const backtestEngine = new BacktestEngine(priceDataArray);
    await backtestEngine.initialize();
    const backtestResults = await backtestEngine.runAllStrategies();
    
    console.log(`\n✅ Step 2 complete: ${backtestResults.length} strategies tested\n`);

    // STEP 3: Portfolio Analysis
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 3/6: CORRELATION & PORTFOLIO OPTIMIZATION');
    console.log('─'.repeat(80));
    
    const analyzer = new PortfolioAnalyzer(backtestResults);
    const portfolioAnalysis = await analyzer.analyze();
    
    console.log(`\n✅ Step 3 complete: Optimal allocation calculated\n`);

    // STEP 4: Generate Charts
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 4/6: CHART GENERATION');
    console.log('─'.repeat(80));
    
    const chartGenerator = new ChartGenerator(backtestResults, portfolioAnalysis);
    await chartGenerator.initialize();
    await chartGenerator.generateAllCharts();
    
    console.log(`\n✅ Step 4 complete: 6 charts generated\n`);

    // STEP 5: Build Presentation
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 5/6: PRESENTATION BUILD');
    console.log('─'.repeat(80));
    
    const presentationBuilder = new PresentationBuilder(backtestResults, portfolioAnalysis);
    await presentationBuilder.build();
    
    console.log(`\n✅ Step 5 complete: Presentation ready\n`);

    // STEP 6: Generate Markdown Report
    console.log('\n' + '─'.repeat(80));
    console.log('STEP 6/6: COMPREHENSIVE REPORT');
    console.log('─'.repeat(80));
    
    await generateReport();
    
    console.log(`\n✅ Step 6 complete: Full report generated\n`);

    // Final Summary
    const endTime = Date.now();
    const duration = ((endTime - startTime) / 1000 / 60).toFixed(1);

    console.log('\n' + '='.repeat(80));
    console.log('✅ PIPELINE COMPLETE!');
    console.log('='.repeat(80));
    console.log(`\n⏱️  Total Time: ${duration} minutes\n`);

    console.log('📊 RESULTS SUMMARY:\n');
    console.log(`Portfolio Expected Return: ${portfolioAnalysis.portfolioMetrics.expectedReturn.toFixed(2)}%`);
    console.log(`Portfolio Sharpe Ratio: ${portfolioAnalysis.portfolioMetrics.sharpeRatio.toFixed(3)}`);
    console.log(`Portfolio Max Drawdown: ${portfolioAnalysis.portfolioMetrics.maxDrawdown.toFixed(2)}%`);
    console.log(`Total Trades Executed: ${backtestResults.reduce((sum, r) => sum + r.trades.length, 0)}`);

    console.log('\n📁 OUTPUT FILES:\n');
    console.log('  📄 BACKTEST_2YEAR_RESULTS.md - Comprehensive report (20-30 KB)');
    console.log('  🎨 polymarket-strategies-presentation-v2.html - Interactive presentation');
    console.log('  📊 results/backtest_results.csv - Full trade log');
    console.log('  📈 charts/ - 6 interactive HTML charts');
    console.log('  💾 results/ - JSON data files (detailed results)\n');

    console.log('🎯 NEXT STEPS:\n');
    console.log('  1. Review: BACKTEST_2YEAR_RESULTS.md');
    console.log('  2. Open: polymarket-strategies-presentation-v2.html in browser');
    console.log('  3. Explore: ./charts/ for detailed visualizations');
    console.log('  4. Analyze: ./results/backtest_results.csv for trade-by-trade breakdown\n');

    console.log('🔔 Ready to send summary to Telegram!\n');

    return {
      success: true,
      duration,
      portfolioMetrics: portfolioAnalysis.portfolioMetrics,
      backtestResults,
      portfolioAnalysis
    };

  } catch (error) {
    console.error('\n❌ Pipeline failed:', error.message);
    console.error(error.stack);
    return {
      success: false,
      error: error.message
    };
  }
}

// Execute
main().catch(console.error);
