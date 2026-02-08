const fs = require('fs');
const data = JSON.parse(fs.readFileSync('time_horizon_real_backtest_results.json', 'utf8'));

console.log('\n=== SAMPLE >7 DAY MARKETS (showing 10) ===\n');
data.buckets.over7days.slice(0, 10).forEach((m, i) => {
    console.log(`${i+1}. ${m.question.substring(0, 70)}`);
    console.log(`   Horizon: ${m.horizonDays}, Won: ${m.won}, Winner: ${m.winner || 'N/A'}`);
    console.log('');
});

console.log('\n=== SAMPLE <3 DAY MARKETS (all) ===\n');
data.buckets.under3days.forEach((m, i) => {
    console.log(`${i+1}. ${m.question.substring(0, 70)}`);
    console.log(`   Horizon: ${m.horizonDays}, Won: ${m.won}, Winner: ${m.winner || 'N/A'}`);
    console.log('');
});

console.log('\n=== ANALYSIS ===');
console.log(`Total >7 day markets: ${data.buckets.over7days.length}`);
console.log(`Wins: ${data.buckets.over7days.filter(m => m.won).length}`);
console.log(`Losses: ${data.buckets.over7days.filter(m => !m.won).length}`);
