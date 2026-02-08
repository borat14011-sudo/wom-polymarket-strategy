const fs = require('fs');

const data = JSON.parse(fs.readFileSync('super_bowl_markets.json', 'utf8'));

console.log('=== SUPER BOWL HISTORICAL ANALYSIS ===\n');

// Categorize markets
const categories = {
  winnerMarkets: [],
  mvpMarkets: [],
  gatoradeMarkets: [],
  coinTossMarkets: [],
  halftimeMarkets: [],
  anthemMarkets: [],
  propMarkets: [],
  quarterMarkets: [],
  taylorSwiftMarkets: [],
  activeMarkets: [],
  closedMarkets: []
};

data.forEach(m => {
  const q = (m.question || '').toLowerCase();
  
  if (m.active === true || m.closed === false) {
    categories.activeMarkets.push(m);
  } else {
    categories.closedMarkets.push(m);
  }
  
  if (q.includes('win super bowl') && !q.includes('mvp')) {
    categories.winnerMarkets.push(m);
  }
  if (q.includes('mvp')) {
    categories.mvpMarkets.push(m);
  }
  if (q.includes('gatorade')) {
    categories.gatoradeMarkets.push(m);
  }
  if (q.includes('coin toss')) {
    categories.coinTossMarkets.push(m);
  }
  if (q.includes('halftime') || q.includes('usher')) {
    categories.halftimeMarkets.push(m);
  }
  if (q.includes('anthem')) {
    categories.anthemMarkets.push(m);
  }
  if (q.includes('taylor swift') || q.includes('kelce')) {
    categories.taylorSwiftMarkets.push(m);
  }
  if (q.includes('quarter') && (q.includes('chiefs') || q.includes('49ers'))) {
    categories.quarterMarkets.push(m);
  }
});

console.log('MARKET COUNTS:');
console.log(`  Total SB Markets: ${data.length}`);
console.log(`  Active Markets: ${categories.activeMarkets.length}`);
console.log(`  Closed Markets: ${categories.closedMarkets.length}`);
console.log(`  Winner Markets: ${categories.winnerMarkets.length}`);
console.log(`  MVP Markets: ${categories.mvpMarkets.length}`);
console.log(`  Gatorade Markets: ${categories.gatoradeMarkets.length}`);
console.log(`  Coin Toss Markets: ${categories.coinTossMarkets.length}`);
console.log(`  Halftime Markets: ${categories.halftimeMarkets.length}`);
console.log(`  Anthem Markets: ${categories.anthemMarkets.length}`);
console.log(`  Quarter Markets: ${categories.quarterMarkets.length}`);
console.log(`  Taylor Swift Markets: ${categories.taylorSwiftMarkets.length}`);

console.log('\n=== ACTIVE SUPER BOWL MARKETS (TONIGHT) ===');
if (categories.activeMarkets.length === 0) {
  console.log('No active SB markets found in snapshot.');
} else {
  categories.activeMarkets.forEach(m => {
    console.log(`\nID: ${m.id}`);
    console.log(`Q: ${m.question}`);
    console.log(`Prices: ${m.outcomePrices}`);
    console.log(`Volume: ${m.volume}`);
    console.log(`End: ${m.endDate}`);
  });
}

// Analyze by Super Bowl year
console.log('\n=== SB MARKETS BY YEAR ===');
const yearPatterns = {
  'LVIII (2024)': /lviii|2024|super bowl 58/i,
  'LIX (2025)': /lix|super bowl 59/i,
  'LX (2026)': /lx|super bowl 60|2026/i,
  'LVII (2023)': /lvii|super bowl 57|2023/i
};

Object.entries(yearPatterns).forEach(([year, regex]) => {
  const matches = data.filter(m => regex.test(m.question || ''));
  console.log(`${year}: ${matches.length} markets`);
});

// Team markets analysis
console.log('\n=== TEAM-SPECIFIC MARKETS ===');
const teams = ['Chiefs', '49ers', 'Eagles', 'Ravens', 'Bengals', 'Bills', 'Rams', 'Buccaneers', 'Seahawks', 'Patriots'];
teams.forEach(team => {
  const regex = new RegExp(team, 'i');
  const count = data.filter(m => regex.test(m.question || '')).length;
  console.log(`  ${team}: ${count} markets`);
});

// Save categorized data
fs.writeFileSync('super_bowl_categorized.json', JSON.stringify(categories, null, 2));
console.log('\nSaved categorized data to super_bowl_categorized.json');
