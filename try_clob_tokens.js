const https = require('https');

// From the 2024 Presidential market
const CONDITION_ID = '0x05b06fa1f0f8ed3c7f77816f7ffacd4c17f6ddbb67f3d82a9e59e08901a45c6d';
const TOKEN_ID_YES = '21742633143463906290569050155826241533067272736897614950488156847949938836455';
const TOKEN_ID_NO = '48331043336612883890938759509493159234755048973500640148014422747788308965732';

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
                resolve({ status: res.statusCode, data: data.substring(0, 1000) });
            });
        }).on('error', (e) => resolve({ status: 'error', data: e.message }));
    });
}

(async () => {
    console.log('Testing CLOB API with token IDs...\n');
    
    const tests = [
        // CLOB endpoints with token IDs
        `/prices?token_id=${TOKEN_ID_YES}`,
        `/price?token_id=${TOKEN_ID_YES}`,
        `/prices-history?token_id=${TOKEN_ID_YES}`,
        `/candles?token_id=${TOKEN_ID_YES}`,
        `/markets?condition_id=${CONDITION_ID}`,
        `/book?token_id=${TOKEN_ID_YES}`,
        `/trades?token_id=${TOKEN_ID_YES}`,
    ];
    
    for (const path of tests) {
        console.log(`Testing: ${path}`);
        const result = await get('clob.polymarket.com', path);
        console.log(`  Status: ${result.status}`);
        if (result.status === 200) {
            console.log(`  ✓ SUCCESS!`);
            console.log(`  Data: ${result.data.substring(0, 300)}...\n`);
        } else if (result.status === 400) {
            console.log(`  ✗ Bad Request: ${result.data}\n`);
        } else {
            console.log(`  ✗ ${result.status}\n`);
        }
    }
})();
