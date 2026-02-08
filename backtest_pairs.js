// Pairs Trading Backtest - 2 Year Historical Analysis
const https = require('https');
const fs = require('fs');

// Helper function to fetch JSON data
function fetchJSON(url) {
  return new Promise((resolve, reject) => {
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    };
    
    https.get(url, options, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (parsed.status && parsed.status.error_code) {
            reject(new Error(parsed.status.error_message));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

// Calculate correlation between two price series
function calculateCorrelation(series1, series2) {
  const n = Math.min(series1.length, series2.length);
  if (n === 0) return 0;
  
  const mean1 = series1.slice(0, n).reduce((a, b) => a + b, 0) / n;
  const mean2 = series2.slice(0, n).reduce((a, b) => a + b, 0) / n;
  
  let num = 0, den1 = 0, den2 = 0;
  
  for (let i = 0; i < n; i++) {
    const diff1 = series1[i] - mean1;
    const diff2 = series2[i] - mean2;
    num += diff1 * diff2;
    den1 += diff1 * diff1;
    den2 += diff2 * diff2;
  }
  
  return num / Math.sqrt(den1 * den2);
}

// Calculate percentage change
function pctChange(current, previous) {
  if (previous === 0) return 0;
  return ((current - previous) / previous) * 100;
}

// Fetch crypto historical data from CoinGecko
async function fetchCryptoData(coinId, days) {
  const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}&interval=daily`;
  console.log(`Fetching ${coinId} data...`);
  
  try {
    const data = await fetchJSON(url);
    if (!data || !data.prices || !Array.isArray(data.prices)) {
      console.error(`Invalid data structure for ${coinId}`);
      return [];
    }
    return data.prices.map(p => ({
      timestamp: p[0],
      date: new Date(p[0]).toISOString().split('T')[0],
      price: p[1]
    }));
  } catch (error) {
    console.error(`Error fetching ${coinId}:`, error.message);
    return [];
  }
}

// Detect divergence events
function detectDivergences(data1, data2, threshold = 8) {
  const divergences = [];
  
  // Align data by date
  const dates = new Set(data1.map(d => d.date));
  const aligned = [];
  
  for (const d1 of data1) {
    const d2 = data2.find(d => d.date === d1.date);
    if (d2) {
      aligned.push({ date: d1.date, price1: d1.price, price2: d2.price });
    }
  }
  
  // Calculate normalized price changes from a baseline
  if (aligned.length < 30) return divergences;
  
  const baseline = aligned[0];
  
  for (let i = 30; i < aligned.length; i++) {
    const pct1 = ((aligned[i].price1 - baseline.price1) / baseline.price1) * 100;
    const pct2 = ((aligned[i].price2 - baseline.price2) / baseline.price2) * 100;
    const divergence = Math.abs(pct1 - pct2);
    
    if (divergence > threshold) {
      // Determine which asset is lagging
      const lagging = pct1 < pct2 ? 'asset1' : 'asset2';
      const laggingPrice = lagging === 'asset1' ? aligned[i].price1 : aligned[i].price2;
      
      divergences.push({
        date: aligned[i].date,
        timestamp: aligned[i].date,
        divergence: divergence.toFixed(2),
        pct1: pct1.toFixed(2),
        pct2: pct2.toFixed(2),
        lagging,
        laggingPrice,
        price1: aligned[i].price1,
        price2: aligned[i].price2,
        index: i
      });
    }
  }
  
  return divergences;
}

// Simulate trades based on divergence strategy
function simulateTrades(divergences, data1, data2, pair1Name, pair2Name) {
  const trades = [];
  
  // Align data
  const dates1 = new Map(data1.map(d => [d.date, d]));
  const dates2 = new Map(data2.map(d => [d.date, d]));
  
  for (const div of divergences) {
    const entryDate = div.date;
    const lagging = div.lagging === 'asset1' ? pair1Name : pair2Name;
    const entryPrice = div.laggingPrice;
    const dataMap = div.lagging === 'asset1' ? dates1 : dates2;
    
    // Look for exit: convergence or +20% gain
    let exitDate = null;
    let exitPrice = null;
    let exitReason = null;
    let maxHoldDays = 90;
    
    // Get subsequent data points
    const entryIndex = data1.findIndex(d => d.date === entryDate);
    const relevantData = div.lagging === 'asset1' ? data1 : data2;
    
    for (let j = entryIndex + 1; j < Math.min(entryIndex + maxHoldDays, relevantData.length); j++) {
      const currentPrice = relevantData[j].price;
      const gain = ((currentPrice - entryPrice) / entryPrice) * 100;
      
      // Exit if +20% gain
      if (gain >= 20) {
        exitDate = relevantData[j].date;
        exitPrice = currentPrice;
        exitReason = 'Target +20%';
        break;
      }
      
      // Check for convergence (divergence < 4%)
      const other1 = dates1.get(relevantData[j].date);
      const other2 = dates2.get(relevantData[j].date);
      
      if (other1 && other2) {
        const baseline1 = dates1.get(entryDate);
        const baseline2 = dates2.get(entryDate);
        
        if (baseline1 && baseline2) {
          const pct1 = ((other1.price - baseline1.price) / baseline1.price) * 100;
          const pct2 = ((other2.price - baseline2.price) / baseline2.price) * 100;
          const currentDiv = Math.abs(pct1 - pct2);
          
          if (currentDiv < 4 && gain > 0) {
            exitDate = relevantData[j].date;
            exitPrice = currentPrice;
            exitReason = 'Convergence';
            break;
          }
        }
      }
    }
    
    // Force exit if still open
    if (!exitDate) {
      const exitIndex = Math.min(entryIndex + maxHoldDays, relevantData.length - 1);
      exitDate = relevantData[exitIndex].date;
      exitPrice = relevantData[exitIndex].price;
      exitReason = 'Max hold period';
    }
    
    const returnPct = ((exitPrice - entryPrice) / entryPrice) * 100;
    const holdDays = Math.floor((new Date(exitDate) - new Date(entryDate)) / (1000 * 60 * 60 * 24));
    
    trades.push({
      pair: `${pair1Name}/${pair2Name}`,
      entryDate,
      exitDate,
      asset: lagging,
      entryPrice: entryPrice.toFixed(2),
      exitPrice: exitPrice.toFixed(2),
      returnPct: returnPct.toFixed(2),
      holdDays,
      divergence: div.divergence,
      exitReason,
      winner: returnPct > 0
    });
  }
  
  return trades;
}

// Calculate performance metrics
function calculateMetrics(trades) {
  if (trades.length === 0) {
    return {
      totalTrades: 0,
      winners: 0,
      losers: 0,
      winRate: 0,
      avgReturn: 0,
      totalReturn: 0,
      avgHoldDays: 0,
      sharpeRatio: 0,
      profitFactor: 0
    };
  }
  
  const returns = trades.map(t => parseFloat(t.returnPct));
  const winners = trades.filter(t => t.winner);
  const losers = trades.filter(t => !t.winner);
  
  const totalReturn = returns.reduce((a, b) => a + b, 0);
  const avgReturn = totalReturn / trades.length;
  const avgHoldDays = trades.reduce((a, t) => a + t.holdDays, 0) / trades.length;
  
  // Sharpe Ratio (simplified: avg return / std dev)
  const variance = returns.reduce((a, r) => a + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);
  const sharpeRatio = stdDev > 0 ? avgReturn / stdDev : 0;
  
  // Profit Factor
  const grossProfit = winners.reduce((a, t) => a + parseFloat(t.returnPct), 0);
  const grossLoss = Math.abs(losers.reduce((a, t) => a + parseFloat(t.returnPct), 0));
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : (grossProfit > 0 ? 999 : 0);
  
  return {
    totalTrades: trades.length,
    winners: winners.length,
    losers: losers.length,
    winRate: (winners.length / trades.length * 100).toFixed(2),
    avgReturn: avgReturn.toFixed(2),
    totalReturn: totalReturn.toFixed(2),
    avgHoldDays: avgHoldDays.toFixed(1),
    sharpeRatio: sharpeRatio.toFixed(3),
    profitFactor: profitFactor.toFixed(2)
  };
}

// Main execution
async function main() {
  console.log('=== PAIRS TRADING BACKTEST - 2 YEAR HISTORICAL ===\n');
  
  // Fetch 730 days (2 years) of data
  const btcData = await fetchCryptoData('bitcoin', 730);
  console.log(`BTC data points: ${btcData.length}`);
  
  await new Promise(resolve => setTimeout(resolve, 2000)); // Rate limit
  
  const ethData = await fetchCryptoData('ethereum', 730);
  console.log(`ETH data points: ${ethData.length}\n`);
  
  if (btcData.length === 0 || ethData.length === 0) {
    console.error('Failed to fetch crypto data. Exiting.');
    return;
  }
  
  // Calculate correlation
  const btcPrices = btcData.map(d => d.price);
  const ethPrices = ethData.map(d => d.price);
  const correlation = calculateCorrelation(btcPrices, ethPrices);
  
  console.log(`BTC/ETH Correlation: ${correlation.toFixed(3)}\n`);
  
  // Detect divergences
  console.log('Detecting divergence events (>8%)...');
  const divergences = detectDivergences(btcData, ethData, 8);
  console.log(`Found ${divergences.length} divergence events\n`);
  
  // Simulate trades
  console.log('Simulating trades...');
  const trades = simulateTrades(divergences, btcData, ethData, 'BTC', 'ETH');
  console.log(`Executed ${trades.length} simulated trades\n`);
  
  // Calculate metrics
  const metrics = calculateMetrics(trades);
  
  // Generate report
  let report = `# PAIRS TRADING BACKTEST - 2 YEAR HISTORICAL\n\n`;
  report += `**Generated:** ${new Date().toISOString()}\n`;
  report += `**Period:** ${btcData[0]?.date} to ${btcData[btcData.length-1]?.date}\n`;
  report += `**Strategy:** Buy lagging asset on >8% divergence, exit on convergence or +20%\n\n`;
  
  report += `## Market Pairs Analyzed\n\n`;
  report += `### BTC/ETH\n`;
  report += `- **Correlation:** ${correlation.toFixed(3)} ${correlation > 0.7 ? '✓ (Strong)' : '✗ (Weak)'}\n`;
  report += `- **Data Points:** ${btcData.length} days\n`;
  report += `- **Divergence Events:** ${divergences.length}\n\n`;
  
  report += `## Performance Metrics\n\n`;
  report += `| Metric | Value |\n`;
  report += `|--------|-------|\n`;
  report += `| Total Trades | ${metrics.totalTrades} |\n`;
  report += `| Winners | ${metrics.winners} |\n`;
  report += `| Losers | ${metrics.losers} |\n`;
  report += `| **Win Rate** | **${metrics.winRate}%** |\n`;
  report += `| Avg Return per Trade | ${metrics.avgReturn}% |\n`;
  report += `| Total Cumulative Return | ${metrics.totalReturn}% |\n`;
  report += `| Avg Hold Period | ${metrics.avgHoldDays} days |\n`;
  report += `| **Sharpe Ratio** | **${metrics.sharpeRatio}** |\n`;
  report += `| **Profit Factor** | **${metrics.profitFactor}** |\n\n`;
  
  report += `## Key Findings\n\n`;
  
  if (parseFloat(metrics.winRate) >= 70) {
    report += `✅ **High Win Rate:** ${metrics.winRate}% confirms strong mean-reversion tendency\n`;
  } else if (parseFloat(metrics.winRate) >= 50) {
    report += `⚠️ **Moderate Win Rate:** ${metrics.winRate}% shows some predictive power\n`;
  } else {
    report += `❌ **Low Win Rate:** ${metrics.winRate}% - strategy underperforms\n`;
  }
  
  if (parseFloat(metrics.sharpeRatio) > 1) {
    report += `✅ **Strong Risk-Adjusted Returns:** Sharpe ${metrics.sharpeRatio} exceeds 1.0\n`;
  }
  
  if (parseFloat(metrics.profitFactor) > 2) {
    report += `✅ **Excellent Profit Factor:** ${metrics.profitFactor}x (gross profits ${metrics.profitFactor}x losses)\n`;
  }
  
  report += `\n## Divergence Events Detected\n\n`;
  report += `Total events with >8% price divergence: ${divergences.length}\n\n`;
  
  if (divergences.length > 0) {
    report += `### Sample Divergence Events (First 10)\n\n`;
    report += `| Date | Divergence | BTC % | ETH % | Lagging Asset |\n`;
    report += `|------|------------|-------|-------|---------------|\n`;
    
    for (let i = 0; i < Math.min(10, divergences.length); i++) {
      const d = divergences[i];
      report += `| ${d.date} | ${d.divergence}% | ${d.pct1}% | ${d.pct2}% | ${d.lagging === 'asset1' ? 'BTC' : 'ETH'} |\n`;
    }
    report += `\n`;
  }
  
  report += `## Trade Analysis\n\n`;
  
  if (trades.length > 0) {
    const convergedTrades = trades.filter(t => t.exitReason === 'Convergence');
    const targetTrades = trades.filter(t => t.exitReason === 'Target +20%');
    const maxHoldTrades = trades.filter(t => t.exitReason === 'Max hold period');
    
    report += `### Exit Reasons\n`;
    report += `- Convergence: ${convergedTrades.length} (${(convergedTrades.length/trades.length*100).toFixed(1)}%)\n`;
    report += `- Target +20%: ${targetTrades.length} (${(targetTrades.length/trades.length*100).toFixed(1)}%)\n`;
    report += `- Max hold: ${maxHoldTrades.length} (${(maxHoldTrades.length/trades.length*100).toFixed(1)}%)\n\n`;
    
    report += `### Convergence Time Analysis\n`;
    const convergeTimes = convergedTrades.map(t => t.holdDays);
    if (convergeTimes.length > 0) {
      const avgConvergeTime = convergeTimes.reduce((a,b) => a+b, 0) / convergeTimes.length;
      const minTime = Math.min(...convergeTimes);
      const maxTime = Math.max(...convergeTimes);
      report += `- Average: ${avgConvergeTime.toFixed(1)} days\n`;
      report += `- Range: ${minTime} - ${maxTime} days\n\n`;
    } else {
      report += `No trades exited via convergence\n\n`;
    }
  }
  
  report += `## Conclusion\n\n`;
  
  if (parseFloat(metrics.winRate) >= 70 && parseFloat(metrics.profitFactor) > 2) {
    report += `✅ **Strategy Validated:** BTC/ETH pairs trading shows strong performance with ${metrics.winRate}% win rate and ${metrics.profitFactor}x profit factor. The correlation of ${correlation.toFixed(3)} supports mean-reversion trades.\n\n`;
    report += `**Recommendation:** Strategy suitable for live trading with proper risk management.\n`;
  } else if (parseFloat(metrics.winRate) >= 50) {
    report += `⚠️ **Mixed Results:** Strategy shows moderate performance. Consider additional filters or tighter entry criteria.\n`;
  } else {
    report += `❌ **Poor Performance:** Strategy underperforms on historical data. Not recommended without significant modifications.\n`;
  }
  
  report += `\n\n---\n*Backtest Period: 2 years | Data Source: CoinGecko | Strategy: Divergence >8%, Exit convergence or +20%*\n`;
  
  // Save report
  fs.writeFileSync('BACKTEST_PAIRS.md', report);
  console.log('✓ Report saved to BACKTEST_PAIRS.md');
  
  // Generate CSV
  let csv = 'Pair,Entry Date,Exit Date,Asset,Entry Price,Exit Price,Return %,Hold Days,Divergence %,Exit Reason,Winner\n';
  for (const trade of trades) {
    csv += `${trade.pair},${trade.entryDate},${trade.exitDate},${trade.asset},${trade.entryPrice},${trade.exitPrice},${trade.returnPct},${trade.holdDays},${trade.divergence},${trade.exitReason},${trade.winner}\n`;
  }
  fs.writeFileSync('trades_pairs.csv', csv);
  console.log('✓ Trades saved to trades_pairs.csv');
  
  console.log('\n=== BACKTEST COMPLETE ===');
  console.log(`Win Rate: ${metrics.winRate}%`);
  console.log(`Sharpe Ratio: ${metrics.sharpeRatio}`);
  console.log(`Profit Factor: ${metrics.profitFactor}`);
}

main().catch(console.error);
