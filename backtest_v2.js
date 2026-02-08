// Pairs Trading Backtest - 2 Year Historical Analysis (v2)
const https = require('https');
const { URL } = require('url');
const fs = require('fs');

// Helper function to fetch JSON data
function fetchJSON(urlString) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlString);
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
      }
    };
    
    https.get(options, (res) => {
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

// Fetch crypto historical data from CoinGecko
async function fetchCryptoData(coinId, days) {
  const url = `https://api.coingecko.com/api/v3/coins/${coinId}/market_chart?vs_currency=usd&days=${days}&interval=daily`;
  console.log(`Fetching ${coinId} data (${days} days)...`);
  
  try {
    const data = await fetchJSON(url);
    if (!data || !data.prices || !Array.isArray(data.prices)) {
      throw new Error('Invalid data structure');
    }
    
    const prices = data.prices.map(p => ({
      timestamp: p[0],
      date: new Date(p[0]).toISOString().split('T')[0],
      price: p[1]
    }));
    
    console.log(`  ✓ Retrieved ${prices.length} data points`);
    return prices;
  } catch (error) {
    console.error(`  ✗ Error: ${error.message}`);
    return [];
  }
}

// Detect divergence events
function detectDivergences(data1, data2, threshold = 8) {
  const divergences = [];
  
  // Align data by date
  const aligned = [];
  for (const d1 of data1) {
    const d2 = data2.find(d => d.date === d1.date);
    if (d2) {
      aligned.push({ date: d1.date, price1: d1.price, price2: d2.price });
    }
  }
  
  if (aligned.length < 30) return divergences;
  
  // Use 30-day rolling baseline for divergence calculation
  for (let i = 30; i < aligned.length; i++) {
    const baseline = aligned[i - 30];
    const current = aligned[i];
    
    const pct1 = ((current.price1 - baseline.price1) / baseline.price1) * 100;
    const pct2 = ((current.price2 - baseline.price2) / baseline.price2) * 100;
    const divergence = Math.abs(pct1 - pct2);
    
    if (divergence > threshold) {
      // Check if this is a new event (not within 7 days of last divergence)
      const lastDiv = divergences[divergences.length - 1];
      if (!lastDiv || (i - lastDiv.index) > 7) {
        const lagging = pct1 < pct2 ? 'asset1' : 'asset2';
        const laggingPrice = lagging === 'asset1' ? current.price1 : current.price2;
        
        divergences.push({
          date: current.date,
          divergence: divergence.toFixed(2),
          pct1: pct1.toFixed(2),
          pct2: pct2.toFixed(2),
          lagging,
          laggingPrice,
          price1: current.price1,
          price2: current.price2,
          index: i
        });
      }
    }
  }
  
  return divergences;
}

// Simulate trades based on divergence strategy
function simulateTrades(divergences, data1, data2, pair1Name, pair2Name) {
  const trades = [];
  
  const dates1 = new Map(data1.map(d => [d.date, d]));
  const dates2 = new Map(data2.map(d => [d.date, d]));
  
  for (const div of divergences) {
    const entryDate = div.date;
    const lagging = div.lagging === 'asset1' ? pair1Name : pair2Name;
    const entryPrice = div.laggingPrice;
    const relevantData = div.lagging === 'asset1' ? data1 : data2;
    
    let exitDate = null;
    let exitPrice = null;
    let exitReason = null;
    const maxHoldDays = 90;
    
    const entryIndex = relevantData.findIndex(d => d.date === entryDate);
    
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
      const baseline1 = dates1.get(entryDate);
      const baseline2 = dates2.get(entryDate);
      
      if (other1 && other2 && baseline1 && baseline2) {
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
      profitFactor: 0,
      maxDrawdown: 0
    };
  }
  
  const returns = trades.map(t => parseFloat(t.returnPct));
  const winners = trades.filter(t => t.winner);
  const losers = trades.filter(t => !t.winner);
  
  const totalReturn = returns.reduce((a, b) => a + b, 0);
  const avgReturn = totalReturn / trades.length;
  const avgHoldDays = trades.reduce((a, t) => a + t.holdDays, 0) / trades.length;
  
  // Sharpe Ratio (simplified: avg return / std dev, annualized)
  const variance = returns.reduce((a, r) => a + Math.pow(r - avgReturn, 2), 0) / returns.length;
  const stdDev = Math.sqrt(variance);
  const sharpeRatio = stdDev > 0 ? (avgReturn / stdDev) * Math.sqrt(365 / avgHoldDays) : 0;
  
  // Profit Factor
  const grossProfit = winners.reduce((a, t) => a + parseFloat(t.returnPct), 0);
  const grossLoss = Math.abs(losers.reduce((a, t) => a + parseFloat(t.returnPct), 0));
  const profitFactor = grossLoss > 0 ? grossProfit / grossLoss : (grossProfit > 0 ? 999 : 0);
  
  // Max Drawdown
  let peak = 0;
  let maxDD = 0;
  let cumReturn = 0;
  for (const ret of returns) {
    cumReturn += ret;
    if (cumReturn > peak) peak = cumReturn;
    const dd = peak - cumReturn;
    if (dd > maxDD) maxDD = dd;
  }
  
  return {
    totalTrades: trades.length,
    winners: winners.length,
    losers: losers.length,
    winRate: (winners.length / trades.length * 100).toFixed(2),
    avgReturn: avgReturn.toFixed(2),
    totalReturn: totalReturn.toFixed(2),
    avgHoldDays: avgHoldDays.toFixed(1),
    sharpeRatio: sharpeRatio.toFixed(3),
    profitFactor: profitFactor.toFixed(2),
    maxDrawdown: maxDD.toFixed(2)
  };
}

// Main execution
async function main() {
  console.log('=== PAIRS TRADING BACKTEST - 2 YEAR HISTORICAL ===\n');
  
  // Fetch 730 days (2 years) of data
  const btcData = await fetchCryptoData('bitcoin', 730);
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const ethData = await fetchCryptoData('ethereum', 730);
  console.log('');
  
  if (btcData.length === 0 || ethData.length === 0) {
    console.error('Failed to fetch crypto data. Exiting.');
    process.exit(1);
  }
  
  // Calculate correlation
  const btcPrices = btcData.map(d => d.price);
  const ethPrices = ethData.map(d => d.price);
  const correlation = calculateCorrelation(btcPrices, ethPrices);
  
  console.log(`BTC/ETH Correlation: ${correlation.toFixed(3)} ${correlation > 0.7 ? '✓' : '✗'}\n`);
  
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
  
  console.log('=== PERFORMANCE SUMMARY ===');
  console.log(`Win Rate: ${metrics.winRate}%`);
  console.log(`Sharpe Ratio: ${metrics.sharpeRatio}`);
  console.log(`Profit Factor: ${metrics.profitFactor}`);
  console.log(`Total Return: ${metrics.totalReturn}%\n`);
  
  // Generate detailed report
  let report = `# PAIRS TRADING BACKTEST - 2 YEAR HISTORICAL\n\n`;
  report += `**Generated:** ${new Date().toISOString().split('T')[0]} ${new Date().toTimeString().split(' ')[0]} PST\n`;
  report += `**Period:** ${btcData[0]?.date} to ${btcData[btcData.length-1]?.date} (${btcData.length} days)\n`;
  report += `**Strategy:** Buy lagging asset on >8% divergence, exit on convergence (<4%) or +20% gain\n\n`;
  
  report += `## Market Pairs Analyzed\n\n`;
  report += `### BTC/ETH (Primary Pair)\n`;
  report += `- **Correlation:** ${correlation.toFixed(3)} ${correlation > 0.7 ? '✅ Strong positive correlation' : '⚠️ Weak correlation'}\n`;
  report += `- **Data Points:** ${btcData.length} daily candles\n`;
  report += `- **Divergence Events:** ${divergences.length} signals\n`;
  report += `- **Date Range:** ${btcData[0]?.date} → ${btcData[btcData.length-1]?.date}\n\n`;
  
  report += `## Performance Metrics\n\n`;
  report += `| Metric | Value | Assessment |\n`;
  report += `|--------|-------|------------|\n`;
  report += `| **Total Trades** | ${metrics.totalTrades} | Sample size ${metrics.totalTrades >= 20 ? 'adequate' : 'limited'} |\n`;
  report += `| **Winners** | ${metrics.winners} | ${metrics.winners} profitable trades |\n`;
  report += `| **Losers** | ${metrics.losers} | ${metrics.losers} unprofitable trades |\n`;
  report += `| **Win Rate** | **${metrics.winRate}%** | ${parseFloat(metrics.winRate) >= 70 ? '✅ Excellent' : parseFloat(metrics.winRate) >= 50 ? '⚠️ Acceptable' : '❌ Poor'} |\n`;
  report += `| **Avg Return/Trade** | ${metrics.avgReturn}% | Per trade expectancy |\n`;
  report += `| **Total Cumulative Return** | **${metrics.totalReturn}%** | Gross returns (no compounding) |\n`;
  report += `| **Avg Hold Period** | ${metrics.avgHoldDays} days | Average trade duration |\n`;
  report += `| **Sharpe Ratio** | **${metrics.sharpeRatio}** | ${parseFloat(metrics.sharpeRatio) > 1 ? '✅ Good risk-adj returns' : '⚠️ Moderate'} |\n`;
  report += `| **Profit Factor** | **${metrics.profitFactor}** | ${parseFloat(metrics.profitFactor) > 2 ? '✅ Excellent' : parseFloat(metrics.profitFactor) > 1 ? '⚠️ Acceptable' : '❌ Poor'} |\n`;
  report += `| **Max Drawdown** | ${metrics.maxDrawdown}% | Largest cumulative loss |\n\n`;
  
  report += `## Key Findings\n\n`;
  
  const winRate = parseFloat(metrics.winRate);
  const sharpe = parseFloat(metrics.sharpeRatio);
  const profitFactor = parseFloat(metrics.profitFactor);
  
  if (winRate >= 70 && profitFactor > 2) {
    report += `### ✅ Strategy Validated\n\n`;
    report += `The BTC/ETH pairs trading strategy demonstrates **strong performance** on 2 years of historical data:\n\n`;
    report += `- **${metrics.winRate}% win rate** confirms reliable mean-reversion patterns\n`;
    report += `- **${metrics.profitFactor}x profit factor** shows profits significantly exceed losses\n`;
    report += `- **${correlation.toFixed(3)} correlation** validates the pair selection\n`;
    report += `- **${metrics.avgHoldDays} day avg hold** indicates efficient capital deployment\n\n`;
  } else if (winRate >= 50) {
    report += `### ⚠️ Mixed Results\n\n`;
    report += `The strategy shows **moderate performance** with room for improvement:\n\n`;
    report += `- Win rate of ${metrics.winRate}% is acceptable but below target (73.3%)\n`;
    report += `- Consider tighter entry criteria or additional filters\n`;
    report += `- Risk management crucial for this performance level\n\n`;
  } else {
    report += `### ❌ Poor Performance\n\n`;
    report += `The strategy **underperforms** on historical data:\n\n`;
    report += `- ${metrics.winRate}% win rate below breakeven threshold\n`;
    report += `- Not recommended for live trading without significant modifications\n\n`;
  }
  
  report += `## Divergence Events Analysis\n\n`;
  report += `Total divergence events (>8% price spread): **${divergences.length}**\n\n`;
  
  if (divergences.length > 0) {
    report += `### Sample Divergence Events\n\n`;
    report += `| Date | Divergence | BTC Δ% | ETH Δ% | Lagging Asset |\n`;
    report += `|------|------------|--------|--------|---------------|\n`;
    
    for (let i = 0; i < Math.min(15, divergences.length); i++) {
      const d = divergences[i];
      const laggingName = d.lagging === 'asset1' ? 'BTC' : 'ETH';
      report += `| ${d.date} | ${d.divergence}% | ${d.pct1}% | ${d.pct2}% | ${laggingName} |\n`;
    }
    report += `\n`;
  }
  
  report += `## Trade-by-Trade Results\n\n`;
  
  if (trades.length > 0) {
    const convergedTrades = trades.filter(t => t.exitReason === 'Convergence');
    const targetTrades = trades.filter(t => t.exitReason === 'Target +20%');
    const maxHoldTrades = trades.filter(t => t.exitReason === 'Max hold period');
    
    report += `### Exit Distribution\n\n`;
    report += `| Exit Reason | Count | Percentage | Avg Return |\n`;
    report += `|-------------|-------|------------|------------|\n`;
    
    const convAvg = convergedTrades.length > 0 ? 
      (convergedTrades.reduce((a,t) => a + parseFloat(t.returnPct), 0) / convergedTrades.length).toFixed(2) : 'N/A';
    const targAvg = targetTrades.length > 0 ?
      (targetTrades.reduce((a,t) => a + parseFloat(t.returnPct), 0) / targetTrades.length).toFixed(2) : 'N/A';
    const holdAvg = maxHoldTrades.length > 0 ?
      (maxHoldTrades.reduce((a,t) => a + parseFloat(t.returnPct), 0) / maxHoldTrades.length).toFixed(2) : 'N/A';
    
    report += `| Convergence | ${convergedTrades.length} | ${(convergedTrades.length/trades.length*100).toFixed(1)}% | ${convAvg}% |\n`;
    report += `| Target +20% | ${targetTrades.length} | ${(targetTrades.length/trades.length*100).toFixed(1)}% | ${targAvg}% |\n`;
    report += `| Max hold (90d) | ${maxHoldTrades.length} | ${(maxHoldTrades.length/trades.length*100).toFixed(1)}% | ${holdAvg}% |\n\n`;
    
    report += `### Convergence Time Analysis\n\n`;
    const convergeTimes = convergedTrades.map(t => t.holdDays);
    if (convergeTimes.length > 0) {
      const avgConvergeTime = convergeTimes.reduce((a,b) => a+b, 0) / convergeTimes.length;
      const minTime = Math.min(...convergeTimes);
      const maxTime = Math.max(...convergeTimes);
      const medianTime = convergeTimes.sort((a,b) => a-b)[Math.floor(convergeTimes.length/2)];
      
      report += `- **Average convergence time:** ${avgConvergeTime.toFixed(1)} days\n`;
      report += `- **Median:** ${medianTime} days\n`;
      report += `- **Range:** ${minTime} - ${maxTime} days\n`;
      report += `- **Speed insight:** ${avgConvergeTime < 30 ? 'Fast mean-reversion' : 'Slow convergence, capital inefficient'}\n\n`;
    } else {
      report += `No trades exited via convergence. This suggests:\n`;
      report += `- Either divergences persist longer than expected\n`;
      report += `- Or exit criteria (4% convergence threshold) may need adjustment\n\n`;
    }
    
    report += `### Top 10 Trades\n\n`;
    const sortedTrades = [...trades].sort((a,b) => parseFloat(b.returnPct) - parseFloat(a.returnPct));
    
    report += `| Date | Asset | Entry | Exit | Return | Hold Days | Exit Reason |\n`;
    report += `|------|-------|-------|------|--------|-----------|-------------|\n`;
    
    for (let i = 0; i < Math.min(10, sortedTrades.length); i++) {
      const t = sortedTrades[i];
      report += `| ${t.entryDate} | ${t.asset} | $${t.entryPrice} | $${t.exitPrice} | **${t.returnPct}%** | ${t.holdDays}d | ${t.exitReason} |\n`;
    }
    report += `\n`;
  }
  
  report += `## Statistical Validation\n\n`;
  report += `### Correlation Analysis\n`;
  report += `- **BTC/ETH correlation:** ${correlation.toFixed(3)}\n`;
  report += `- **Threshold:** >0.70 required for pairs trading\n`;
  report += `- **Status:** ${correlation > 0.7 ? '✅ Pair qualifies' : '❌ Insufficient correlation'}\n\n`;
  
  report += `### Divergence Frequency\n`;
  const daysInSample = btcData.length;
  const divergencePct = (divergences.length / daysInSample * 100).toFixed(2);
  report += `- **Divergence events:** ${divergences.length} over ${daysInSample} days\n`;
  report += `- **Frequency:** ${divergencePct}% of days show >8% divergence\n`;
  report += `- **Trade opportunity:** Average 1 signal every ${(daysInSample / divergences.length).toFixed(1)} days\n\n`;
  
  report += `## Risk Assessment\n\n`;
  report += `### Drawdown Analysis\n`;
  report += `- **Maximum drawdown:** ${metrics.maxDrawdown}%\n`;
  report += `- **Risk level:** ${parseFloat(metrics.maxDrawdown) < 20 ? 'Low' : parseFloat(metrics.maxDrawdown) < 40 ? 'Moderate' : 'High'}\n\n`;
  
  report += `### Recommended Position Sizing\n`;
  const kellyFraction = winRate > 50 ? ((winRate/100 * Math.abs(parseFloat(metrics.avgReturn)) - (1-winRate/100) * Math.abs(parseFloat(metrics.avgReturn))) / Math.abs(parseFloat(metrics.avgReturn))).toFixed(3) : 0;
  report += `- **Kelly Criterion:** ${kellyFraction} (use 25-50% of Kelly for safety)\n`;
  report += `- **Suggested per-trade risk:** 2-5% of capital\n`;
  report += `- **Max concurrent positions:** 3-5 to manage correlation risk\n\n`;
  
  report += `## Conclusion\n\n`;
  
  if (winRate >= 70 && profitFactor > 2 && correlation > 0.7) {
    report += `### ✅ **STRATEGY APPROVED FOR LIVE TRADING**\n\n`;
    report += `The BTC/ETH pairs trading strategy has **passed backtesting validation**:\n\n`;
    report += `✅ Win rate (${metrics.winRate}%) exceeds 70% threshold\n`;
    report += `✅ Profit factor (${metrics.profitFactor}x) demonstrates strong edge\n`;
    report += `✅ Correlation (${correlation.toFixed(3)}) confirms pair validity\n`;
    report += `✅ ${metrics.totalTrades} trades provide statistical confidence\n\n`;
    report += `**Recommended Actions:**\n`;
    report += `1. Begin with small position sizes (2-3% per trade)\n`;
    report += `2. Monitor live performance vs backtest expectations\n`;
    report += `3. Set hard stop-loss at -10% per position\n`;
    report += `4. Re-validate correlation monthly\n`;
    report += `5. Paper trade for 2-4 weeks before live capital\n\n`;
  } else if (winRate >= 50 && profitFactor > 1) {
    report += `### ⚠️ **CONDITIONAL APPROVAL**\n\n`;
    report += `Strategy shows potential but requires optimization:\n\n`;
    report += `- Consider tighter entry criteria (>10% divergence)\n`;
    report += `- Add trend filter (only trade in ranging markets)\n`;
    report += `- Implement stricter stop-losses\n`;
    report += `- Paper trade extensively before live deployment\n\n`;
  } else {
    report += `### ❌ **NOT RECOMMENDED FOR LIVE TRADING**\n\n`;
    report += `The strategy fails to meet minimum performance thresholds:\n\n`;
    report += `❌ Win rate ${metrics.winRate}% below 50% minimum\n`;
    report += `❌ Profit factor ${metrics.profitFactor} insufficient\n`;
    report += `❌ High risk of capital erosion\n\n`;
    report += `**Required improvements before consideration:**\n`;
    report += `- Refine entry/exit criteria\n`;
    report += `- Add volatility filters\n`;
    report += `- Consider alternative pairs\n`;
    report += `- Implement machine learning for better timing\n\n`;
  }
  
  report += `## Data Sources & Methodology\n\n`;
  report += `- **Price Data:** CoinGecko API (daily candles)\n`;
  report += `- **Correlation Method:** Pearson correlation coefficient\n`;
  report += `- **Divergence Calculation:** 30-day rolling baseline\n`;
  report += `- **Entry Trigger:** >8% absolute percentage divergence\n`;
  report += `- **Exit Logic:** Convergence <4% OR +20% gain OR 90-day max hold\n`;
  report += `- **Sharpe Ratio:** Annualized, assuming reinvestment\n`;
  report += `- **Profit Factor:** Gross profits / Gross losses\n\n`;
  
  report += `## Notes & Limitations\n\n`;
  report += `⚠️ **Backtest Limitations:**\n`;
  report += `- No transaction costs included (expect 0.1-0.5% per trade)\n`;
  report += `- No slippage modeling\n`;
  report += `- Assumes perfect execution at daily close prices\n`;
  report += `- Does not account for liquidity constraints\n`;
  report += `- Past performance ≠ future results\n\n`;
  
  report += `⚠️ **Market Regime Risk:**\n`;
  report += `- Strategy assumes stable correlation\n`;
  report += `- Major market events (regulation, hacks) can break correlations\n`;
  report += `- Monitor correlation weekly in live trading\n\n`;
  
  report += `---\n\n`;
  report += `*Backtest completed: ${new Date().toISOString()}*\n`;
  report += `*Model: Claude Sonnet 4.5 | Framework: Node.js Backtest Engine*\n`;
  
  // Save report
  fs.writeFileSync('BACKTEST_PAIRS.md', report);
  console.log('✓ Full report saved to BACKTEST_PAIRS.md');
  
  // Generate CSV
  let csv = 'Pair,Entry Date,Exit Date,Asset,Entry Price,Exit Price,Return %,Hold Days,Divergence %,Exit Reason,Winner\n';
  for (const trade of trades) {
    csv += `${trade.pair},${trade.entryDate},${trade.exitDate},${trade.asset},${trade.entryPrice},${trade.exitPrice},${trade.returnPct},${trade.holdDays},${trade.divergence},${trade.exitReason},${trade.winner}\n`;
  }
  fs.writeFileSync('trades_pairs.csv', csv);
  console.log('✓ Trade log saved to trades_pairs.csv');
  
  console.log('\n=== BACKTEST COMPLETE ===');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
