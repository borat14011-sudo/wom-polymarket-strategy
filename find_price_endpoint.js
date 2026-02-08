const https = require('https');

// Sample 2024 market ID we found
const MARKET_ID = '240613'; // "Which party wins 2024 US Presidential Election?"
const CONDITION_ID = '0x05b06fa1f0f8ed3c7f77816f7ffacd4c17f6ddbb67f3d82a9e59e08901a45c6d'; // From earlier fetch

async function get(hostname, path) {
    return new Promise((resolve) => {
        https.get({
            hostname: hostname,
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: 10000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                resolve({ status: res.statusCode, data: data.substring(0, 500) });
            });
        }).on('error', (e) => resolve({ status: 'error', data: e.message }));
    });
}

(async () => {
    console.log('Testing price history endpoints...\n');
    console.log(`Market ID: ${MARKET_ID}`);
    console.log(`Condition ID: ${CONDITION_ID}\n`);
    
    // Test Gamma API endpoints
    const gammaTests = [
        `/markets/${MARKET_ID}/prices`,
        `/markets/${MARKET_ID}/prices-history`,
        `/prices?market=${MARKET_ID}`,
        `/price-history?market=${MARKET_ID}`,
        `/markets/${MARKET_ID}/history`,
        `/prices-history?market=${MARKET_ID}`,
        `/prices-history?condition_id=${CONDITION_ID}`,
    ];
    
    console.log('Testing Gamma API (gamma-api.polymarket.com):');
    for (const path of gammaTests) {
        const result = await get('gamma-api.polymarket.com', path);
        const status = result.status === 200 ? '✓' : '✗';
        console.log(`  ${status} ${result.status} - ${path}`);
        if (result.status === 200) {
            console.log(`     Preview: ${result.data.substring(0, 100)}...`);
        }
    }
    
    // Test CLOB API endpoints
    console.log('\nTesting CLOB API (clob.polymarket.com):');
    const clobTests = [
        `/prices?market=${MARKET_ID}`,
        `/price?market=${MARKET_ID}`,
        `/markets/${MARKET_ID}/prices`,
        `/prices-history?market=${MARKET_ID}`,
    ];
    
    for (const path of clobTests) {
        const result = await get('clob.polymarket.com', path);
        const status = result.status === 200 ? '✓' : '✗';
        console.log(`  ${status} ${result.status} - ${path}`);
        if (result.status === 200) {
            console.log(`     Preview: ${result.data.substring(0, 100)}...`);
        }
    }
    
    // Test data API
    console.log('\nTesting Data API (data-api.polymarket.com):');
    const dataTests = [
        `/prices?market=${MARKET_ID}`,
        `/markets/${MARKET_ID}/prices`,
        `/prices-history?market=${MARKET_ID}`,
    ];
    
    for (const path of dataTests) {
        const result = await get('data-api.polymarket.com', path);
        const status = result.status === 200 ? '✓' : '✗';
        console.log(`  ${status} ${result.status} - ${path}`);
        if (result.status === 200) {
            console.log(`     Preview: ${result.data.substring(0, 100)}...`);
        }
    }
    
    console.log('\nDone!');
})();
