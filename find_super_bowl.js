const fs = require('fs');

const searchTerms = [
  /super.?bowl/i,
  /superbowl/i,
  /chiefs/i,
  /49ers/i,
  /seahawks/i,
  /patriots/i,
  /eagles/i,
  /ravens/i,
  /bengals/i,
  /bills/i,
  /rams/i,
  /buccaneers/i,
  /MVP/i,
  /coin.?toss/i,
  /gatorade/i,
  /anthem/i,
  /halftime/i
];

const results = [];
const seen = new Set();

console.log('Loading and parsing file...');
const data = JSON.parse(fs.readFileSync('markets_snapshot_20260207_221914.json', 'utf8'));
console.log(`Total markets: ${data.markets.length}`);

for (const market of data.markets) {
  const text = (market.question || '') + ' ' + (market.event_title || '') + ' ' + (market.description || '');
  
  for (const term of searchTerms) {
    if (term.test(text) && !seen.has(market.id)) {
      results.push({
        id: market.id,
        question: market.question,
        event_title: market.event_title,
        description: market.description?.substring(0, 200),
        active: market.active,
        closed: market.closed,
        volume: market.volume,
        endDate: market.endDate,
        outcomePrices: market.outcomePrices,
        outcomes: market.outcomes,
        bestBid: market.bestBid,
        bestAsk: market.bestAsk,
        slug: market.slug
      });
      seen.add(market.id);
      break;
    }
  }
}

console.log(`\nFound ${results.length} Super Bowl related markets`);
console.log('\n=== MARKETS ===');
results.slice(0, 50).forEach(m => {
  console.log(`\nID: ${m.id}`);
  console.log(`Q: ${m.question}`);
  console.log(`Event: ${m.event_title || 'N/A'}`);
  console.log(`Active: ${m.active}, Closed: ${m.closed}`);
  console.log(`End: ${m.endDate}`);
  console.log(`Volume: ${m.volume}`);
  console.log(`Prices: ${m.outcomePrices}`);
  console.log('---');
});

fs.writeFileSync('super_bowl_markets.json', JSON.stringify(results, null, 2));
console.log(`\nSaved ${results.length} markets to super_bowl_markets.json`);
