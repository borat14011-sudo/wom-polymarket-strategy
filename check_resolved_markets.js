const fs = require('fs');

try {
    const data = fs.readFileSync('polymarket_resolved_markets.json', 'utf8');
    console.log('File size:', data.length, 'bytes');
    console.log('First 500 chars:', data.substring(0, 500));
    
    // Try to parse it
    const markets = JSON.parse(data);
    console.log('\nTotal markets:', markets.length);
    
    if (markets.length > 0) {
        console.log('\nSample market keys:', Object.keys(markets[0]));
        console.log('\nFirst market:', JSON.stringify(markets[0], null, 2));
    }
} catch (e) {
    console.error('Error:', e.message);
}
