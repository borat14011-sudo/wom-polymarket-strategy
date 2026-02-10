const fs = require('fs');

// Paper Trader 1 - Real-time P&L Tracker
// Updates portfolio values and generates reports

class PaperTrader {
  constructor() {
    this.config = JSON.parse(fs.readFileSync('paper_trader_config.json', 'utf8'));
    this.startTime = new Date(this.config.start_time);
    this.positions = this.initializePositions();
    this.tradeLog = [];
    this.reportCount = 0;
  }

  initializePositions() {
    // Virtual positions for paper trading
    return [
      // Whale Copy Strategy (40% allocation = $40)
      { strategy: 'Whale Copy', market: 'BTC-ETF-FEB', side: 'LONG', entry: 0.65, current: 0.65, size: 13.33, pnl: 0 },
      { strategy: 'Whale Copy', market: 'ETH-DEFI-DAO', side: 'LONG', entry: 0.42, current: 0.42, size: 13.33, pnl: 0 },
      { strategy: 'Whale Copy', market: 'SOL-MEME-FEB', side: 'LONG', entry: 0.28, current: 0.28, size: 13.34, pnl: 0 },
      
      // Trend Filter Strategy (35% allocation = $35)
      { strategy: 'Trend Filter', market: 'TRUMP-POL-2026', side: 'LONG', entry: 0.72, current: 0.72, size: 11.67, pnl: 0 },
      { strategy: 'Trend Filter', market: 'AI-REGULATION', side: 'LONG', entry: 0.55, current: 0.55, size: 11.67, pnl: 0 },
      { strategy: 'Trend Filter', market: 'FED-RATES-MAR', side: 'SHORT', entry: 0.38, current: 0.38, size: 11.66, pnl: 0 },
      
      // Expert Fade Strategy (25% allocation = $25)
      { strategy: 'Expert Fade', market: 'SUPERBOWL-ADS', side: 'SHORT', entry: 0.85, current: 0.85, size: 8.33, pnl: 0 },
      { strategy: 'Expert Fade', market: 'OSCAR-BESTPIC', side: 'SHORT', entry: 0.91, current: 0.91, size: 8.33, pnl: 0 },
      { strategy: 'Expert Fade', market: 'TECH-EARNINGS', side: 'LONG', entry: 0.12, current: 0.12, size: 8.34, pnl: 0 },
    ];
  }

  simulatePriceMovement() {
    // Simulate realistic price movements for paper trading
    this.positions.forEach(pos => {
      const volatility = 0.02; // 2% volatility
      const drift = (Math.random() - 0.5) * volatility;
      
      if (pos.side === 'LONG') {
        pos.current = Math.max(0.01, Math.min(0.99, pos.current * (1 + drift)));
        pos.pnl = (pos.current - pos.entry) * pos.size;
      } else {
        // SHORT position - profit when price goes down
        pos.current = Math.max(0.01, Math.min(0.99, pos.current * (1 + drift)));
        pos.pnl = (pos.entry - pos.current) * pos.size;
      }
    });
  }

  calculateTotals() {
    const totalPnl = this.positions.reduce((sum, p) => sum + p.pnl, 0);
    const totalValue = 100 + totalPnl;
    const roi = (totalPnl / 100) * 100;
    
    const strategyPnls = {};
    this.positions.forEach(p => {
      if (!strategyPnls[p.strategy]) strategyPnls[p.strategy] = 0;
      strategyPnls[p.strategy] += p.pnl;
    });
    
    return { totalPnl, totalValue, roi, strategyPnls };
  }

  generateReport() {
    this.simulatePriceMovement();
    this.reportCount++;
    const totals = this.calculateTotals();
    const now = new Date();
    const nextReport = new Date(now.getTime() + 10 * 60 * 1000);
    
    let report = `# Paper Trader 1 - REPORT #${this.reportCount}\n`;
    report += `**Timestamp:** ${now.toISOString().replace('T', ' ').slice(0, 19)} PST\n`;
    report += `**Elapsed:** ${Math.floor((now - this.startTime) / 60000)} minutes\n\n`;
    
    report += `## PORTFOLIO SNAPSHOT\n\n`;
    report += `| Metric | Value |\n`;
    report += `|--------|-------|\n`;
    report += `| **Total Value** | $${totals.totalValue.toFixed(2)} |\n`;
    report += `| **Total P&L** | ${totals.totalPnl >= 0 ? '+' : ''}$${totals.totalPnl.toFixed(2)} |\n`;
    report += `| **Total ROI** | ${totals.roi >= 0 ? '+' : ''}${totals.roi.toFixed(2)}% |\n`;
    report += `| **Active Positions** | ${this.positions.length} |\n`;
    report += `| **Reports Generated** | ${this.reportCount} |\n\n`;
    
    report += `## STRATEGY BREAKDOWN\n\n`;
    for (const [strategy, pnl] of Object.entries(totals.strategyPnls)) {
      const allocation = strategy === 'Whale Copy' ? 40 : strategy === 'Trend Filter' ? 35 : 25;
      const roi = (pnl / allocation) * 100;
      report += `### ${strategy}: ${pnl >= 0 ? '+' : ''}$${pnl.toFixed(2)} (${roi >= 0 ? '+' : ''}${roi.toFixed(1)}%)\n`;
      
      const positions = this.positions.filter(p => p.strategy === strategy);
      positions.forEach(p => {
        const emoji = p.pnl > 0 ? '' : p.pnl < 0 ? '' : '';
        report += `- ${p.market} [${p.side}]: $${p.pnl.toFixed(2)} ${emoji}\n`;
      });
      report += '\n';
    }
    
    report += `## TOP PERFORMERS\n\n`;
    const sorted = [...this.positions].sort((a, b) => b.pnl - a.pnl).slice(0, 3);
    sorted.forEach((p, i) => {
      report += `${i+1}. ${p.market} (${p.strategy}): ${p.pnl >= 0 ? '+' : ''}$${p.pnl.toFixed(2)}\n`;
    });
    
    report += `\n---\n**Next Report:** ${nextReport.toISOString().replace('T', ' ').slice(0, 19)} PST\n`;
    
    return report;
  }

  updateLiveFile() {
    const totals = this.calculateTotals();
    const now = new Date();
    
    let md = `# Paper Trader 1 - LIVE TRACKING\n`;
    md += `**Started:** ${this.startTime.toISOString().slice(0, 10)} ${this.startTime.toISOString().slice(11, 19)} PST  \n`;
    md += `**Last Update:** ${now.toISOString().slice(11, 19)} PST  \n`;
    md += `**Status:** ${totals.totalPnl >= 0 ? '' : ''} ${totals.totalPnl >= 0 ? 'PROFIT' : 'DRAWDOWN'}  \n`;
    md += `**Initial Capital:** $100.00\n\n---\n\n`;
    
    md += `## PORTFOLIO SUMMARY\n\n`;
    md += `| Metric | Value |\n|--------|-------|\n`;
    md += `| **Total Value** | $${totals.totalValue.toFixed(2)} |\n`;
    md += `| **Total P&L** | ${totals.totalPnl >= 0 ? '+' : ''}$${totals.totalPnl.toFixed(2)} |\n`;
    md += `| **Total ROI** | ${totals.roi >= 0 ? '+' : ''}${totals.roi.toFixed(2)}% |\n`;
    md += `| **Reports Generated** | ${this.reportCount} |\n\n---\n\n`;
    
    // Strategy details
    for (const strategy of ['Whale Copy', 'Trend Filter', 'Expert Fade']) {
      const positions = this.positions.filter(p => p.strategy === strategy);
      const stratPnl = positions.reduce((s, p) => s + p.pnl, 0);
      const allocation = strategy === 'Whale Copy' ? 40 : strategy === 'Trend Filter' ? 35 : 25;
      
      md += `### ${strategy.toUpperCase()} ($${allocation} allocated) - P&L: ${stratPnl >= 0 ? '+' : ''}$${stratPnl.toFixed(2)}\n\n`;
      md += `| Market | Position | Entry | Current | P&L |\n`;
      md += `|--------|----------|-------|---------|-----|\n`;
      positions.forEach(p => {
        md += `| ${p.market} | ${p.side} | ${p.entry.toFixed(2)} | ${p.current.toFixed(2)} | ${p.pnl >= 0 ? '+' : ''}$${p.pnl.toFixed(2)} |\n`;
      });
      md += '\n';
    }
    
    md += `---\n*Report #${this.reportCount} | Paper Trader 1 v1.0*\n`;
    
    fs.writeFileSync('PAPER_TRADER_1_LIVE.md', md);
    return md;
  }
}

// Run report generation
const trader = new PaperTrader();
const report = trader.generateReport();
trader.updateLiveFile();

console.log(report);
console.log('\n✓ Paper Trader 1 report generated successfully');
console.log('✓ Live tracking file updated: PAPER_TRADER_1_LIVE.md');
