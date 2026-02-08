/**
 * CHART GENERATION - Create visualizations
 * 
 * Generates HTML/SVG charts for:
 * 1. Equity curves
 * 2. Drawdown chart
 * 3. Risk/Return scatter
 * 4. Correlation heatmap
 * 5. Monthly returns table
 * 6. Portfolio allocation pie chart
 */

import { promises as fs } from 'fs';

const RESULTS_DIR = './results';
const CHARTS_DIR = './charts';

class ChartGenerator {
  constructor(backtestResults, portfolioAnalysis) {
    this.results = backtestResults;
    this.analysis = portfolioAnalysis;
  }

  async initialize() {
    await fs.mkdir(CHARTS_DIR, { recursive: true });
  }

  /**
   * Generate all charts as standalone HTML files
   */
  async generateAllCharts() {
    console.log('\n📊 Generating Charts...\n');

    await this.generateEquityCurves();
    await this.generateDrawdownChart();
    await this.generateRiskReturnScatter();
    await this.generateCorrelationHeatmap();
    await this.generateMonthlyReturnsTable();
    await this.generatePortfolioAllocationPie();

    console.log('\n✅ All charts generated in ./charts/');
  }

  /**
   * Chart 1: Equity Curves
   */
  async generateEquityCurves() {
    console.log('  📈 Generating equity curves...');

    const datasets = this.results.map((result, idx) => {
      const color = this.getColor(idx);
      return {
        label: result.strategy,
        data: result.equityCurve.map(point => ({
          x: point.date,
          y: point.equity
        })),
        borderColor: color,
        backgroundColor: color + '20',
        fill: false,
        tension: 0.3
      };
    });

    const html = this.createChartHTML(
      'Equity Curves - All Strategies (2024-2026)',
      'line',
      datasets,
      {
        scales: {
          y: {
            beginAtZero: false,
            title: { display: true, text: 'Capital ($)' }
          },
          x: {
            type: 'time',
            title: { display: true, text: 'Date' }
          }
        }
      }
    );

    await fs.writeFile(`${CHARTS_DIR}/equity_curves.html`, html);
  }

  /**
   * Chart 2: Drawdown Chart
   */
  async generateDrawdownChart() {
    console.log('  📉 Generating drawdown chart...');

    const datasets = this.results.map((result, idx) => {
      const drawdowns = this.calculateDrawdowns(result.equityCurve);
      const color = this.getColor(idx);
      
      return {
        label: result.strategy,
        data: drawdowns.map(point => ({
          x: point.date,
          y: point.drawdown
        })),
        borderColor: color,
        backgroundColor: color + '40',
        fill: 'origin',
        tension: 0.3
      };
    });

    const html = this.createChartHTML(
      'Drawdown Chart - Risk Over Time',
      'line',
      datasets,
      {
        scales: {
          y: {
            reverse: true,
            title: { display: true, text: 'Drawdown (%)' }
          },
          x: {
            type: 'time',
            title: { display: true, text: 'Date' }
          }
        }
      }
    );

    await fs.writeFile(`${CHARTS_DIR}/drawdowns.html`, html);
  }

  /**
   * Chart 3: Risk/Return Scatter
   */
  async generateRiskReturnScatter() {
    console.log('  📊 Generating risk/return scatter...');

    const data = this.results.map((result, idx) => ({
      x: result.metrics.maxDrawdown,
      y: result.metrics.totalReturn,
      label: result.strategy,
      sharpe: result.metrics.sharpeRatio
    }));

    const datasets = [{
      label: 'Strategies',
      data: data,
      backgroundColor: data.map((_, idx) => this.getColor(idx)),
      borderColor: data.map((_, idx) => this.getColor(idx)),
      pointRadius: 10,
      pointHoverRadius: 15
    }];

    const html = this.createScatterHTML(
      'Risk vs Return (with Sharpe Ratios)',
      data
    );

    await fs.writeFile(`${CHARTS_DIR}/risk_return_scatter.html`, html);
  }

  /**
   * Chart 4: Correlation Heatmap
   */
  async generateCorrelationHeatmap() {
    console.log('  🔥 Generating correlation heatmap...');

    const { strategies, matrix } = this.analysis.correlationMatrix;
    
    const html = this.createHeatmapHTML(
      'Strategy Correlation Matrix',
      strategies,
      matrix
    );

    await fs.writeFile(`${CHARTS_DIR}/correlation_heatmap.html`, html);
  }

  /**
   * Chart 5: Monthly Returns Table
   */
  async generateMonthlyReturnsTable() {
    console.log('  📅 Generating monthly returns table...');

    const monthlyData = this.calculateMonthlyReturns();
    const html = this.createMonthlyTableHTML(monthlyData);

    await fs.writeFile(`${CHARTS_DIR}/monthly_returns_table.html`, html);
  }

  /**
   * Chart 6: Portfolio Allocation Pie
   */
  async generatePortfolioAllocationPie() {
    console.log('  🥧 Generating portfolio allocation pie...');

    const weights = this.analysis.optimalWeights;
    
    const html = this.createPieHTML(
      'Optimal Portfolio Allocation',
      weights.map(w => w.strategy),
      weights.map(w => w.weight * 100)
    );

    await fs.writeFile(`${CHARTS_DIR}/portfolio_allocation.html`, html);
  }

  // Helper Methods

  calculateDrawdowns(equityCurve) {
    let peak = equityCurve[0].equity;
    const drawdowns = [];

    for (const point of equityCurve) {
      if (point.equity > peak) peak = point.equity;
      const drawdown = ((peak - point.equity) / peak) * 100;
      drawdowns.push({
        date: point.date,
        drawdown: drawdown
      });
    }

    return drawdowns;
  }

  calculateMonthlyReturns() {
    const monthlyData = {};

    for (const result of this.results) {
      const strategy = result.strategy;
      monthlyData[strategy] = {};

      const equity = result.equityCurve;
      let currentMonth = null;
      let monthStart = equity[0].equity;

      for (const point of equity) {
        const date = new Date(point.date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;

        if (monthKey !== currentMonth) {
          if (currentMonth) {
            const monthReturn = ((point.equity - monthStart) / monthStart) * 100;
            monthlyData[strategy][currentMonth] = monthReturn;
          }
          currentMonth = monthKey;
          monthStart = point.equity;
        }
      }
    }

    return monthlyData;
  }

  getColor(index) {
    const colors = [
      '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
    ];
    return colors[index % colors.length];
  }

  // HTML Generators

  createChartHTML(title, type, datasets, options = {}) {
    return `<!DOCTYPE html>
<html>
<head>
  <title>${title}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0/dist/chartjs-adapter-date-fns.bundle.min.js"></script>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
    h1 { color: #333; text-align: center; margin-bottom: 30px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${title}</h1>
    <canvas id="chart"></canvas>
  </div>
  <script>
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: '${type}',
      data: {
        datasets: ${JSON.stringify(datasets)}
      },
      options: ${JSON.stringify(options)}
    });
  </script>
</body>
</html>`;
  }

  createScatterHTML(title, data) {
    return `<!DOCTYPE html>
<html>
<head>
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
    h1 { text-align: center; color: #333; }
    table { width: 100%; border-collapse: collapse; margin-top: 30px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background-color: #4CAF50; color: white; }
    .positive { color: green; }
    .negative { color: red; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${title}</h1>
    <table>
      <tr>
        <th>Strategy</th>
        <th>Total Return (%)</th>
        <th>Max Drawdown (%)</th>
        <th>Sharpe Ratio</th>
      </tr>
      ${data.map(d => `
        <tr>
          <td><strong>${d.label}</strong></td>
          <td class="${d.y >= 0 ? 'positive' : 'negative'}">${d.y.toFixed(2)}%</td>
          <td>${d.x.toFixed(2)}%</td>
          <td>${d.sharpe.toFixed(3)}</td>
        </tr>
      `).join('')}
    </table>
  </div>
</body>
</html>`;
  }

  createHeatmapHTML(title, strategies, matrix) {
    const getCellColor = (value) => {
      const intensity = Math.abs(value);
      if (value > 0) {
        return `rgba(255, ${255 - intensity * 200}, ${255 - intensity * 200}, 1)`;
      } else {
        return `rgba(${255 + value * 200}, ${255 + value * 200}, 255, 1)`;
      }
    };

    return `<!DOCTYPE html>
<html>
<head>
  <title>${title}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
    h1 { text-align: center; color: #333; margin-bottom: 30px; }
    table { margin: 0 auto; border-collapse: collapse; }
    th, td { padding: 15px; text-align: center; border: 1px solid #ddd; min-width: 80px; }
    th { background-color: #4CAF50; color: white; font-size: 12px; }
    .legend { margin-top: 30px; text-align: center; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${title}</h1>
    <table>
      <tr>
        <th></th>
        ${strategies.map((s, i) => `<th>S${i+1}</th>`).join('')}
      </tr>
      ${strategies.map((strat, i) => `
        <tr>
          <th>S${i+1}</th>
          ${matrix[i].map(val => `
            <td style="background-color: ${getCellColor(val)}">
              ${val.toFixed(2)}
            </td>
          `).join('')}
        </tr>
      `).join('')}
    </table>
    <div class="legend">
      <p><strong>Strategy Key:</strong></p>
      ${strategies.map((s, i) => `<div>S${i+1}: ${s}</div>`).join('')}
    </div>
  </div>
</body>
</html>`;
  }

  createMonthlyTableHTML(monthlyData) {
    const strategies = Object.keys(monthlyData);
    const allMonths = new Set();
    
    strategies.forEach(strat => {
      Object.keys(monthlyData[strat]).forEach(month => allMonths.add(month));
    });
    
    const months = Array.from(allMonths).sort();

    return `<!DOCTYPE html>
<html>
<head>
  <title>Monthly Returns</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 100%; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; overflow-x: auto; }
    h1 { text-align: center; color: #333; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }
    th, td { padding: 8px; text-align: center; border: 1px solid #ddd; }
    th { background-color: #4CAF50; color: white; position: sticky; top: 0; }
    .positive { background-color: #d4edda; color: #155724; }
    .negative { background-color: #f8d7da; color: #721c24; }
  </style>
</head>
<body>
  <div class="container">
    <h1>Monthly Returns by Strategy (2024-2026)</h1>
    <table>
      <tr>
        <th>Strategy</th>
        ${months.map(m => `<th>${m}</th>`).join('')}
      </tr>
      ${strategies.map(strat => `
        <tr>
          <td><strong>${strat}</strong></td>
          ${months.map(month => {
            const ret = monthlyData[strat][month];
            if (ret === undefined) return '<td>-</td>';
            const className = ret >= 0 ? 'positive' : 'negative';
            return `<td class="${className}">${ret.toFixed(2)}%</td>`;
          }).join('')}
        </tr>
      `).join('')}
    </table>
  </div>
</body>
</html>`;
  }

  createPieHTML(title, labels, data) {
    return `<!DOCTYPE html>
<html>
<head>
  <title>${title}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; background: #f5f5f5; }
    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
    h1 { text-align: center; color: #333; margin-bottom: 30px; }
    canvas { max-height: 400px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>${title}</h1>
    <canvas id="chart"></canvas>
  </div>
  <script>
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type: 'pie',
      data: {
        labels: ${JSON.stringify(labels)},
        datasets: [{
          data: ${JSON.stringify(data)},
          backgroundColor: [
            '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40'
          ]
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: function(context) {
                return context.label + ': ' + context.parsed.toFixed(2) + '%';
              }
            }
          }
        }
      }
    });
  </script>
</body>
</html>`;
  }
}

// Main execution
async function main() {
  console.log('📊 Loading analysis results...\n');
  
  const backtestResults = JSON.parse(
    await fs.readFile(`${RESULTS_DIR}/backtest_results.json`, 'utf-8')
  );
  const portfolioAnalysis = JSON.parse(
    await fs.readFile(`${RESULTS_DIR}/portfolio_analysis.json`, 'utf-8')
  );

  const generator = new ChartGenerator(backtestResults, portfolioAnalysis);
  await generator.initialize();
  await generator.generateAllCharts();

  console.log('\n✅ CHART GENERATION COMPLETE');
  console.log('\nNext: npm run presentation\n');
}

if (import.meta.url === `file:///${process.argv[1].replace(/\\/g, '/')}`) {
  main().catch(console.error);
}

export default ChartGenerator;
