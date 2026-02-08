/**
 * GENERATE COMPREHENSIVE MARKDOWN REPORT
 */

import { promises as fs } from 'fs';

const RESULTS_DIR = './results';
const DATA_DIR = './data';

async function generateReport() {
  console.log('\n📝 Generating comprehensive markdown report...\n');

  const backtestResults = JSON.parse(
    await fs.readFile(`${RESULTS_DIR}/backtest_results.json`, 'utf-8')
  );
  const portfolioAnalysis = JSON.parse(
    await fs.readFile(`${RESULTS_DIR}/portfolio_analysis.json`, 'utf-8')
  );

  let qualityReport;
  try {
    qualityReport = JSON.parse(
      await fs.readFile(`${DATA_DIR}/quality_report.json`, 'utf-8')
    );
  } catch {
    qualityReport = null;
  }

  const report = `# POLYMARKET 2-YEAR HISTORICAL BACKTEST RESULTS

**Generated:** ${new Date().toISOString()}  
**Period:** January 1, 2024 - February 7, 2026  
**Strategies Tested:** 6  
**Data Source:** Polymarket CLOB API (real historical data)

---

## EXECUTIVE SUMMARY

### Portfolio Performance (Optimized Allocation)

| Metric | Value |
|--------|-------|
| **Expected Annual Return** | ${portfolioAnalysis.portfolioMetrics.expectedReturn.toFixed(2)}% |
| **Sharpe Ratio** | ${portfolioAnalysis.portfolioMetrics.sharpeRatio.toFixed(3)} |
| **Sortino Ratio** | ${portfolioAnalysis.portfolioMetrics.sortinoRatio || 'N/A'} |
| **Max Drawdown** | ${portfolioAnalysis.portfolioMetrics.maxDrawdown.toFixed(2)}% |
| **Calmar Ratio** | ${portfolioAnalysis.portfolioMetrics.calmarRatio.toFixed(3)} |

### Key Findings

${backtestResults.map(r => `- **${r.strategy}**: ${r.metrics.totalReturn.toFixed(2)}% return, ${r.metrics.sharpeRatio.toFixed(3)} Sharpe, ${r.metrics.totalTrades} trades`).join('\n')}

---

## 1. METHODOLOGY

### Data Collection

${qualityReport ? `
- **Total Markets Fetched:** ${qualityReport.totalMarkets}
- **Markets with Price Data:** ${qualityReport.marketsWithPriceData}
- **Data Coverage:** ${qualityReport.coverage.percentage}%
- **Data Quality Issues:** ${qualityReport.dataQualityIssues.length}
` : '- Data quality report not available'}

**API Endpoints Used:**
- Markets: \`https://gamma-api.polymarket.com/markets\`
- Price History: \`https://clob.polymarket.com/prices-history\`

**Data Resolution:** Hourly price data  
**Market Selection:** Resolved markets only (known outcomes)

### Backtesting Parameters

| Parameter | Value |
|-----------|-------|
| Initial Capital | $10,000 |
| Position Size | 10% per trade |
| Max Concurrent Positions | 5 |
| Fees (Entry + Exit) | 2% (1% each way) |
| Slippage Model | None (assumes fills at quoted prices) |

### Risk Metrics Calculated

1. **Sharpe Ratio:** (Return - Risk-Free Rate) / Standard Deviation (annualized)
2. **Sortino Ratio:** Return / Downside Deviation (annualized)
3. **Calmar Ratio:** Annual Return / Maximum Drawdown
4. **Max Drawdown:** Largest peak-to-trough decline in equity curve

---

## 2. STRATEGY-BY-STRATEGY RESULTS

${backtestResults.map((result, idx) => {
  const m = result.metrics;
  return `
### Strategy ${idx + 1}: ${result.strategy}

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Total Return | ${m.totalReturn.toFixed(2)}% |
| Win Rate | ${m.winRate.toFixed(2)}% |
| Total Trades | ${m.totalTrades} |
| Winners | ${m.winners} |
| Losers | ${m.losers} |
| Profit Factor | ${m.profitFactor.toFixed(2)} |
| Avg Trade Duration | ${(m.avgTradeDuration / 24).toFixed(1)} days |

**Risk-Adjusted Returns:**

| Metric | Value |
|--------|-------|
| Sharpe Ratio | ${m.sharpeRatio.toFixed(3)} |
| Sortino Ratio | ${m.sortinoRatio.toFixed(3)} |
| Calmar Ratio | ${m.calmarRatio.toFixed(3)} |
| Max Drawdown | ${m.maxDrawdown.toFixed(2)}% |
| Final Equity | $${m.finalEquity.toLocaleString()} |

**Strategy Logic:**
${getStrategyDescription(result.strategy)}

**Performance Assessment:**
${assessStrategy(m)}

---
`;
}).join('\n')}

## 3. CORRELATION ANALYSIS

### Correlation Matrix

Strategy correlations (1.0 = perfect correlation, 0.0 = uncorrelated, -1.0 = inverse):

\`\`\`
${portfolioAnalysis.correlationMatrix.strategies.map((s, i) => 
  `S${i+1} [${s}]`
).join('\n')}

${portfolioAnalysis.correlationMatrix.matrix.map((row, i) => 
  `S${i+1}: ` + row.map(v => v.toFixed(2).padStart(6)).join('  ')
).join('\n')}
\`\`\`

### Uncorrelated Strategy Pairs (for Diversification)

${portfolioAnalysis.uncorrelatedPairs.length > 0 
  ? portfolioAnalysis.uncorrelatedPairs.slice(0, 5).map(p => 
    `- **${p.strategy1}** ↔ **${p.strategy2}**: ${p.correlation.toFixed(3)}`
  ).join('\n')
  : '- No pairs found with correlation < 0.3 (all strategies show moderate to high correlation)'
}

**Diversification Insight:**
${portfolioAnalysis.uncorrelatedPairs.length > 2 
  ? 'Multiple low-correlation pairs identified. Portfolio diversification will provide significant risk reduction.'
  : 'Strategies show high correlation. Diversification benefits will be limited.'
}

---

## 4. PORTFOLIO OPTIMIZATION

### Optimal Allocation (Sharpe-Weighted)

${portfolioAnalysis.optimalWeights.map((w, idx) => 
  `${idx + 1}. **${w.strategy}**: ${(w.weight * 100).toFixed(2)}% (Sharpe: ${w.sharpeRatio.toFixed(3)})`
).join('\n')}

### Expected Portfolio Metrics

| Metric | Value | vs Avg Single Strategy |
|--------|-------|------------------------|
| Expected Return | ${portfolioAnalysis.portfolioMetrics.expectedReturn.toFixed(2)}% | ${portfolioAnalysis.portfolioMetrics.diversificationBenefit.returnImprovement >= 0 ? '+' : ''}${portfolioAnalysis.portfolioMetrics.diversificationBenefit.returnImprovement.toFixed(2)}% |
| Sharpe Ratio | ${portfolioAnalysis.portfolioMetrics.sharpeRatio.toFixed(3)} | ${portfolioAnalysis.portfolioMetrics.diversificationBenefit.sharpeImprovement >= 0 ? '+' : ''}${portfolioAnalysis.portfolioMetrics.diversificationBenefit.sharpeImprovement.toFixed(2)}% |
| Max Drawdown | ${portfolioAnalysis.portfolioMetrics.maxDrawdown.toFixed(2)}% | Lower risk |
| Calmar Ratio | ${portfolioAnalysis.portfolioMetrics.calmarRatio.toFixed(3)} | Better |

---

## 5. MONTE CARLO SIMULATION

**Methodology:** 1,000 simulations with random sampling from historical trade returns

### Results

| Percentile | Return |
|------------|--------|
| Worst Case | ${portfolioAnalysis.monteCarloSimulation.worstCase.toFixed(2)}% |
| 5th Percentile | ${portfolioAnalysis.monteCarloSimulation.percentile5.toFixed(2)}% |
| Median (50th) | ${portfolioAnalysis.monteCarloSimulation.median.toFixed(2)}% |
| 95th Percentile | ${portfolioAnalysis.monteCarloSimulation.percentile95.toFixed(2)}% |
| Best Case | ${portfolioAnalysis.monteCarloSimulation.bestCase.toFixed(2)}% |
| Mean | ${portfolioAnalysis.monteCarloSimulation.mean.toFixed(2)}% |

**Interpretation:**
- **50% probability** of returns between ${portfolioAnalysis.monteCarloSimulation.percentile5.toFixed(2)}% and ${portfolioAnalysis.monteCarloSimulation.percentile95.toFixed(2)}%
- **Median return** (most likely): ${portfolioAnalysis.monteCarloSimulation.median.toFixed(2)}%
- **Risk of loss** (returns < 0%): ${(portfolioAnalysis.monteCarloSimulation.percentile5 < 0 ? 'Moderate' : 'Low')}

---

## 6. DATA QUALITY & LIMITATIONS

### Data Quality Issues

${qualityReport && qualityReport.dataQualityIssues.length > 0 
  ? `${qualityReport.dataQualityIssues.slice(0, 10).map(issue => 
    `- ${issue.issue}: ${issue.market || issue.error || 'N/A'}`
  ).join('\n')}\n\n${qualityReport.dataQualityIssues.length > 10 ? `... and ${qualityReport.dataQualityIssues.length - 10} more issues` : ''}`
  : '- No major data quality issues detected'
}

### Known Limitations

1. **Historical Data Availability**
   - Not all markets have complete price history
   - Some markets may have data gaps during low-activity periods

2. **Backtesting Assumptions**
   - No slippage modeling
   - Assumes fills at exact quoted prices
   - Does not account for liquidity constraints
   - Fees are estimated (2% total)

3. **Market Conditions**
   - Past performance does not guarantee future results
   - Market dynamics may change
   - Strategy effectiveness may degrade with wider adoption

4. **Statistical Significance**
   - Limited sample size for some strategies
   - Results should be validated with paper trading

---

## 7. RECOMMENDATIONS

### ✅ Deployment Strategy

**Recommended Approach:** Deploy optimized portfolio with weights shown in Section 4

**Expected Risk-Adjusted Returns:**
- **Sharpe Ratio:** ${portfolioAnalysis.portfolioMetrics.sharpeRatio.toFixed(3)} (${portfolioAnalysis.portfolioMetrics.sharpeRatio > 1 ? 'Excellent' : portfolioAnalysis.portfolioMetrics.sharpeRatio > 0.5 ? 'Good' : 'Moderate'})
- **Max Drawdown:** ${portfolioAnalysis.portfolioMetrics.maxDrawdown.toFixed(2)}% (${portfolioAnalysis.portfolioMetrics.maxDrawdown < 15 ? 'Low risk' : portfolioAnalysis.portfolioMetrics.maxDrawdown < 25 ? 'Moderate risk' : 'High risk'})

### 🎯 Implementation Steps

1. **Paper Trading First**
   - Test strategies in live market without real capital
   - Validate entry/exit signals match backtest assumptions
   - Monitor for 2-4 weeks before committing capital

2. **Risk Management**
   - Set daily loss limit (e.g., 2-3% of capital)
   - Implement position size limits
   - Use stop-losses consistently
   - Monitor correlation drift

3. **Performance Monitoring**
   - Track actual vs expected Sharpe ratio weekly
   - Rebalance portfolio monthly
   - Review strategy performance quarterly
   - Be prepared to disable underperforming strategies

4. **Capital Allocation**
   - Start with small capital (10-20% of intended total)
   - Scale up gradually as confidence grows
   - Reserve capital for drawdown periods

### ⚠️ Risk Warnings

- **Market Risk:** Polymarket odds can be manipulated or irrational
- **Liquidity Risk:** Large positions may not fill at desired prices
- **Model Risk:** Strategies based on historical patterns may fail
- **Technology Risk:** API downtime, execution delays, bugs

---

## 8. VISUALIZATIONS

All charts available in \`./charts/\` directory:

1. **equity_curves.html** - Equity growth over time for all strategies
2. **drawdowns.html** - Risk visualization (drawdown over time)
3. **risk_return_scatter.html** - Risk vs return tradeoff analysis
4. **correlation_heatmap.html** - 6x6 strategy correlation matrix
5. **monthly_returns_table.html** - Monthly performance breakdown
6. **portfolio_allocation.html** - Optimal allocation pie chart

---

## 9. CONCLUSION

${generateConclusion(portfolioAnalysis, backtestResults)}

---

## APPENDICES

### A. Trade Log

Full trade log available in: \`${RESULTS_DIR}/backtest_results.csv\`

**Format:**
\`\`\`
Strategy,Market,Signal,Entry Date,Exit Date,Entry Price,Exit Price,P&L,P&L %,Duration (hrs),Exit Reason,Winner
\`\`\`

### B. Data Files

- **Raw Market Data:** \`data/raw/markets.json\`
- **Processed Price Data:** \`data/processed/price_data.json\`
- **Backtest Results:** \`results/backtest_results.json\`
- **Portfolio Analysis:** \`results/portfolio_analysis.json\`

### C. Code Repository

All strategy implementations available in: \`src/strategies.js\`

---

**END OF REPORT**

*Generated by Polymarket Backtest Engine v1.0*  
*For questions or issues, review the methodology section or examine raw data files.*
`;

  await fs.writeFile('BACKTEST_2YEAR_RESULTS.md', report);
  console.log('✅ Report saved: BACKTEST_2YEAR_RESULTS.md\n');
}

function getStrategyDescription(strategyName) {
  const descriptions = {
    'NO-side-bias': 'Entry when price < 15% with volume spike > 2x average. Exit at 30% or 7 days.',
    'contrarian-expert-fade': 'Fade strong consensus (>85%) - bet against the crowd. Exit on reversion to 60-70%.',
    'pairs-trading': 'Mean reversion strategy - enter on 20% deviation from 48h moving average.',
    'trend-filter': 'Follow momentum - enter when price > 24h ago by >5%. Exit after 3 days or trend reversal.',
    'time-horizon-filter': 'Only trade markets closing in <3 days. Momentum play near expiry.',
    'news-mean-reversion': 'Capitalize on overreactions - enter on >15% move in 6h, exit on reversion.'
  };
  return descriptions[strategyName] || 'No description available.';
}

function assessStrategy(metrics) {
  const assessments = [];
  
  if (metrics.sharpeRatio > 1.5) assessments.push('**Excellent risk-adjusted returns**');
  else if (metrics.sharpeRatio > 1.0) assessments.push('**Good risk-adjusted returns**');
  else if (metrics.sharpeRatio > 0.5) assessments.push('**Moderate risk-adjusted returns**');
  else assessments.push('**Below-average risk-adjusted returns**');

  if (metrics.winRate > 60) assessments.push('High win rate indicates consistent edge');
  else if (metrics.winRate < 40) assessments.push('Low win rate - relies on large winners');

  if (metrics.maxDrawdown > 25) assessments.push('⚠️ High drawdown risk - use cautious position sizing');
  else if (metrics.maxDrawdown < 10) assessments.push('Low drawdown - conservative strategy');

  if (metrics.totalTrades < 10) assessments.push('⚠️ Limited sample size - results may not be statistically significant');

  return assessments.join('. ') + '.';
}

function generateConclusion(portfolioAnalysis, backtestResults) {
  const avgReturn = backtestResults.reduce((sum, r) => sum + r.metrics.totalReturn, 0) / backtestResults.length;
  const portfolioReturn = portfolioAnalysis.portfolioMetrics.expectedReturn;
  const portfolioSharpe = portfolioAnalysis.portfolioMetrics.sharpeRatio;

  let conclusion = '';

  if (portfolioSharpe > 1.5) {
    conclusion = `**Strong Positive Results:** The optimized portfolio shows excellent risk-adjusted returns with a Sharpe ratio of ${portfolioSharpe.toFixed(3)}. This indicates the strategies have demonstrated consistent edge over the 2-year backtest period. Diversification improved returns by ${portfolioAnalysis.portfolioMetrics.diversificationBenefit.returnImprovement.toFixed(2)}% vs average single strategy.`;
  } else if (portfolioSharpe > 1.0) {
    conclusion = `**Positive Results:** The portfolio demonstrates good risk-adjusted performance (Sharpe: ${portfolioSharpe.toFixed(3)}). While not exceptional, the strategies show consistent profitability when combined. Consider paper trading before live deployment.`;
  } else if (portfolioSharpe > 0.5) {
    conclusion = `**Mixed Results:** The portfolio shows moderate returns (Sharpe: ${portfolioSharpe.toFixed(3)}). Some strategies performed well while others struggled. Recommend focusing on top 2-3 strategies only and conducting additional validation.`;
  } else {
    conclusion = `**Weak Results:** The portfolio shows below-average risk-adjusted returns (Sharpe: ${portfolioSharpe.toFixed(3)}). Historical performance does not support live deployment without significant strategy improvements or additional validation.`;
  }

  conclusion += `\n\n**Data Quality:** ${backtestResults.reduce((sum, r) => sum + r.trades.length, 0)} total trades executed across all strategies provides ${backtestResults.reduce((sum, r) => sum + r.trades.length, 0) > 100 ? 'reasonable' : 'limited'} statistical confidence.`;

  conclusion += `\n\n**Recommendation:** ${
    portfolioSharpe > 1.0 
      ? 'Proceed to paper trading with optimized portfolio allocation. Monitor closely for 2-4 weeks before committing real capital.' 
      : 'Additional strategy refinement recommended. Consider longer backtest period or alternative market selection criteria.'
  }`;

  return conclusion;
}

if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  generateReport().catch(console.error);
}

export default generateReport;
