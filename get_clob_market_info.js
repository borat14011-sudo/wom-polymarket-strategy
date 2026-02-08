const https = require('https');

const CONDITION_ID = '0x05b06fa1f0f8ed3c7f77816f7ffacd4c17f6ddbb67f3d82a9e59e08901a45c6d';

async function get(hostname, path) {
    return new Promise((resolve, reject) => {
        https.get({
            hostname: hostname,
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' },
            timeout: 10000
        }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        reject(e);
                    }
                } else {
                    reject(new Error(`HTTP ${res.statusCode}`));
                }
            });
        }).on('error', reject);
    });
}

(async () => {
    console.log('Fetching CLOB market info...\n');
    
    const marketInfo = await get('clob.polymarket.com', `/markets?condition_id=${CONDITION_ID}`);
    
    console.log('Market data:');
    console.log(JSON.stringify(marketInfo, null, 2));
    
    if (marketInfo.data && marketInfo.data.length > 0) {
        const market = marketInfo.data[0];
        console.log(`\n\nKey fields:`);
        console.log(`  Condition ID: ${market.condition_id}`);
        console.log(`  Question ID: ${market.question_id}`);
        console.log(`  Neg risk: ${market.neg_risk}`);
        console.log(`  Tokens: ${JSON.stringify(market.tokens)}`);
        
        // Try to get price history with the asset/market ID
        if (market.tokens && market.tokens.length > 0) {
            const tokenId = market.tokens[0].token_id;
            console.log(`\n\nTrying /prices-history with token: ${tokenId}`);
            
            try {
                const priceHistory = await get('clob.polymarket.com', 
                    `/prices-history?market=${tokenId}&interval=max&fidelity=1`);
                console.log('✓ SUCCESS!');
                console.log(`Price history data:`);
                console.log(JSON.stringify(priceHistory, null, 2).substring(0, 1000));
            } catch (e) {
                console.log(`✗ Error: ${e.message}`);
            }
        }
    }
})();
