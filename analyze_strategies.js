const fs = require('fs');
const lines = fs.readFileSync('backtest_results.csv', 'utf8').split('\n');
const strategies = {};

for (let i = 1; i < lines.length; i++) {
  const cols = lines[i].split(',');
  if (cols.length < 8) continue;
  const strat = cols[0];
  const pnl = parseFloat(cols[7]);
  if (!strategies[strat]) strategies[strat] = {trades: 0, pnl: 0, wins: 0};
  strategies[strat].trades++;
  strategies[strat].pnl += pnl;
  if (pnl > 0) strategies[strat].wins++;
}

console.log('STRATEGY PERFORMANCE SUMMARY');
console.log('='.repeat(70));
console.log('Strategy              Trades   WinRate    Total P&L     Avg P&L');
console.log('-'.repeat(70));

const sorted = Object.entries(strategies).sort((a,b) => b[1].pnl - a[1].pnl);
for (const [name, data] of sorted) {
  const winRate = (data.wins / data.trades * 100).toFixed(1);
  const avgPnl = (data.pnl / data.trades).toFixed(4);
  const pnlStr = data.pnl.toFixed(2).padEnd(13);
  const line = name.padEnd(20) + ' ' + data.trades.toString().padEnd(8) + ' ' + winRate.padEnd(10) + ' ' + pnlStr + ' ' + avgPnl;
  console.log(line);
}
