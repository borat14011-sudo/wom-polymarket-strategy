const https = require('https');

async function httpGet(path) {
    return new Promise((resolve, reject) => {
        https.get({
            hostname: 'gamma-api.polymarket.com',
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' }
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
    console.log('Testing Polymarket API endpoints...\n');

    // Test 1: /markets endpoint
    try {
        const markets = await httpGet('/markets');
        console.log(`✓ /markets returned ${markets.length} markets`);
        
        if (markets.length > 0) {
            const sample = markets[0];
            console.log('\nSample market structure:');
            console.log(`  ID: ${sample.id}`);
            console.log(`  Question: ${sample.question}`);
            console.log(`  End Date: ${sample.endDate}`);
            console.log(`  Closed: ${sample.closed}`);
            console.log(`  Created: ${sample.createdAt}`);
            console.log(`  Closed Time: ${sample.closedTime}`);
            
            // Check date distribution
            const years = {};
            markets.forEach(m => {
                const date = m.endDate || m.closedTime || m.createdAt || '';
                const year = date.substring(0, 4);
                years[year] = (years[year] || 0) + 1;
            });
            
            console.log('\nYear distribution:');
            Object.keys(years).sort().forEach(year => {
                console.log(`  ${year}: ${years[year]} markets`);
            });

            // Count closed vs open
            const closed = markets.filter(m => m.closed).length;
            console.log(`\nClosed markets: ${closed}/${markets.length}`);
        }
    } catch (error) {
        console.error(`✗ /markets failed: ${error.message}`);
    }

    // Test 2: Try pagination or filtering
    console.log('\n---\nTrying with query parameters...\n');
    
    const queries = [
        '/markets?limit=100',
        '/markets?closed=true',
        '/markets?offset=0&limit=50',
        '/markets?next_cursor=',
    ];

    for (const query of queries) {
        try {
            const result = await httpGet(query);
            console.log(`✓ ${query} returned ${Array.isArray(result) ? result.length : 'object'} items`);
        } catch (error) {
            console.log(`✗ ${query} failed: ${error.message}`);
        }
        await new Promise(r => setTimeout(r, 500));
    }
})();
