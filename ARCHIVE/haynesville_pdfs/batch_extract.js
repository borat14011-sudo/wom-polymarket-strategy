const fs = require('fs');
const https = require('https');

const ordersFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\orders_to_process.txt';
const csvFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\content_id_index.csv';
const progressFile = 'C:\\Users\\Borat\\.openclaw\\workspace\\haynesville_pdfs\\progress.json';

// Read orders
let orders = fs.readFileSync(ordersFile, 'utf-8')
  .split('\n')
  .map(o => o.trim().replace(/^\uFEFF/, ''))  // Remove BOM
  .filter(o => o.length > 0);

console.log(`Total orders: ${orders.length}`);

// Read already processed
let processed = new Set();
if (fs.existsSync(csvFile)) {
  const lines = fs.readFileSync(csvFile, 'utf-8').split('\n');
  for (let i = 1; i < lines.length; i++) {  // Skip header
    const cols = lines[i].split(',');
    if (cols[0]) processed.add(cols[0].trim());
  }
}

console.log(`Already processed: ${processed.size}`);

// Remaining orders
const remaining = orders.filter(o => !processed.has(o));
console.log(`Remaining: ${remaining.length}`);
console.log(`\nFirst 10 remaining orders:`);
remaining.slice(0, 10).forEach(o => console.log(`  ${o}`));
