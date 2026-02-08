// Try to construct API calls with different sorting/filtering
const https = require('https');
const fs = require('fs');

async function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            });
        }).on('error', reject);
    });
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function tryDifferentEndpoints() {
    console.log("Trying different API endpoints and parameters...\n");
    
    // Try sorting by different fields
    const endpoints = [
        "https://gamma-api.polymarket.com/markets?closed=true&limit=20&order=closedTime&direction=desc",
        "https://gamma-api.polymarket.com/markets?closed=true&limit=20&_sort=-closedTime",
        "https://gamma-api.polymarket.com/markets?closed=true&limit=20&_sort=-updatedAt",
        "https://gamma-api.polymarket.com/events?closed=true&limit=20",
        "https://clob.polymarket.com/markets?closed=true&limit=20",
        "https://gamma-api.polymarket.com/markets?closed=true&active=false&limit=20"
    ];
    
    for (const url of endpoints) {
        try {
            console.log(`Trying: ${url}`);
            const data = await fetchUrl(url);
            
            if (Array.isArray(data)) {
                console.log(`  ✓ Got ${data.length} results`);
                if (data.length > 0) {
                    const first = data[0];
                    console.log(`  First result: ${first.question || first.title || 'unknown'}`);
                    console.log(`  Closed time: ${first.closedTime || first.closed_time || 'N/A'}`);
                    console.log(`  Updated: ${first.updatedAt || 'N/A'}`);
                }
            } else if (data.data) {
                console.log(`  ✓ Got ${data.data.length} results in data field`);
                if (data.data.length > 0) {
                    const first = data.data[0];
                    console.log(`  First result: ${first.question || first.title || 'unknown'}`);
                    console.log(`  Closed time: ${first.closedTime || first.closed_time || 'N/A'}`);
                }
            }
            
            console.log('');
            await sleep(1000);
        } catch (error) {
            console.log(`  ✗ Error: ${error.message}\n`);
        }
    }
}

tryDifferentEndpoints().catch(console.error);
