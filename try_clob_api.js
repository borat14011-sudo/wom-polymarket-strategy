#!/usr/bin/env node
const https = require('https');

function fetchJSON(hostname, path) {
    return new Promise((resolve) => {
        https.get({
            hostname: hostname,
            path: path,
            headers: { 'User-Agent': 'Mozilla/5.0' }
        }, (res) => {
            let data = '';
            res.on('data', (chunk) => { data += chunk; });
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    console.error('Parse error:', e.message);
                    console.log('Response:', data.substring(0, 500));
                    resolve(null);
                }
            });
        }).on('error', (e) => {
            console.error('Request error:', e.message);
            resolve(null);
        });
    });
}

async function tryAPIs() {
    console.log('Trying different Polymarket API endpoints...\n');
    
    // Try CLOB API
    console.log('1. CLOB API - /markets endpoint:');
    let data = await fetchJSON('clob.polymarket.com', '/markets');
    console.log(data ? `Got data with ${Object.keys(data).length} keys` : 'Failed');
    if (data) console.log('Keys:', Object.keys(data).slice(0, 10));
    
    console.log('\n2. CLOB API - /sampling-markets:');
    data = await fetchJSON('clob.polymarket.com', '/sampling-markets');
    console.log(data ? `Got ${Array.isArray(data) ? data.length : 'object'} items` : 'Failed');
    
    console.log('\n3. Gamma API - simpler endpoint:');
    data = await fetchJSON('gamma-api.polymarket.com', '/markets?limit=5');
    console.log(data ? `Got data` : 'Failed');
    if (data && data[0]) {
        console.log('Sample market:', data[0].question);
        console.log('End date:', data[0].endDate);
    }
    
    console.log('\n4. Trying strfry.api (alternative):');
    data = await fetchJSON('strfry-charts.poly.market', '/markets');
    console.log(data ? `Got data` : 'Failed');
    
    console.log('\n5. Direct Polymarket data API:');
    data = await fetchJSON('data-api.polymarket.com', '/markets');
    console.log(data ? `Got data` : 'Failed');
}

tryAPIs().catch(console.error);
