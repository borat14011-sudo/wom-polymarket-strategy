// SONRIS Batch Processor
// This script processes orders and extracts Content IDs

const fs = require('fs');
const path = require('path');

const ordersFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\orders_to_process.txt';
const csvFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\content_id_index.csv';
const progressFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\progress.json';

// Read orders
const orders = fs.readFileSync(ordersFile, 'utf-8')
  .split('\n')
  .map(o => o.trim())
  .filter(o => o.length > 0);

// Read progress
let processed = [];
if (fs.existsSync(progressFile)) {
  processed = JSON.parse(fs.readFileSync(progressFile, 'utf-8'));
}

// Find remaining
const remaining = orders.filter(o => !processed.includes(o));

console.log(`Total orders: ${orders.length}`);
console.log(`Already processed: ${processed.length}`);
console.log(`Remaining: ${remaining.length}`);

// Output next batch to process (50 at a time)
const batchSize = 50;
const nextBatch = remaining.slice(0, batchSize);
console.log('\n--- Next batch ---');
console.log(JSON.stringify(nextBatch));
