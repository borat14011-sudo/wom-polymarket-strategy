const fs = require('fs');

// Load all the data
const sbMarkets = JSON.parse(fs.readFileSync('super_bowl_categorized.json', 'utf8'));
const allMarkets = JSON.parse(fs.readFileSync('super_bowl_markets.json', 'utf8'));

// Filter for only SB LX (2026) active markets
const lxMarkets = allMarkets.filter(m => {
  const q = (m.question || '').toLowerCase();
  return (q.includes('super bowl lx') || q.includes('2026') || q.includes('seahawks') || q.includes('patriots')) && 
         (m.active === true || m.closed === false);
});

console.log(`Found ${lxMarkets.length} active SB LX markets\n`);

// Categorize LX markets
const categories = {
  gameWinner: [],
  mvp: [],
  spread: [],
  totals: [],
  halftime: [],
  coinToss: [],
  gatorade: [],
  anthem: [],
  props: [],
  attendance: []
};

lxMarkets.forEach(m => {
  const q = (m.question || '').toLowerCase();
  
  if (q.includes('mvp')) {
    categories.mvp.push(m);
  } else if (q.includes('spread')) {
    categories.spread.push(m);
  } else if (q.includes('o/u') || q.includes('total')) {
    categories.totals.push(m);
  } else if (q.includes('coin toss')) {
    categories.coinToss.push(m);
  } else if (q.includes('gatorade')) {
    categories.gatorade.push(m);
  } else if (q.includes('anthem')) {
    categories.anthem.push(m);
  } else if (q.includes('halftime') || q.includes('perform')) {
    categories.halftime.push(m);
  } else if (q.includes('attend')) {
    categories.attendance.push(m);
  } else if ((q.includes('seahawks') && q.includes('patriots')) || q === 'seahawks vs. patriots') {
    categories.gameWinner.push(m);
  } else {
    categories.props.push(m);
  }
});

// Print categorized markets
console.log('=== SUPER BOWL LX - ACTIVE MARKETS ===\n');

console.log('--- MONEYLINE / GAME WINNER ---');
categories.gameWinner.slice(0, 5).forEach(m => {
  console.log(`ID: ${m.id} | ${m.question}`);
  console.log(`Volume: $${m.volume}`);
  console.log('');
});

console.log('\n--- SPREAD MARKETS ---');
categories.spread.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- TOTALS (O/U) ---');
categories.totals.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- MVP MARKETS (Top 10) ---');
categories.mvp.slice(0, 10).forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- COIN TOSS ---');
categories.coinToss.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- GATORADE SHOWER ---');
categories.gatorade.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- NATIONAL ANTHEM ---');
categories.anthem.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- HALFTIME SHOW ---');
categories.halftime.slice(0, 10).forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

console.log('\n--- KEY PROP MARKETS ---');
const keyProps = categories.props.filter(m => {
  const q = m.question.toLowerCase();
  return q.includes('trump') || q.includes('elon') || q.includes('taylor') || 
         q.includes('viewers') || q.includes('said');
});
keyProps.forEach(m => {
  console.log(`ID: ${m.id} | ${m.question} | Vol: $${m.volume}`);
});

// Save LX markets
fs.writeFileSync('sb_lx_active_markets.json', JSON.stringify(lxMarkets, null, 2));
fs.writeFileSync('sb_lx_categories.json', JSON.stringify(categories, null, 2));
console.log(`\n\nSaved ${lxMarkets.length} markets to sb_lx_active_markets.json`);
