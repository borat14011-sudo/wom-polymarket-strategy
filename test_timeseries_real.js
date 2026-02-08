const https = require('https');
const fs = require('fs');

function httpGet(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = '';
            res.on('data', (chunk) => data += chunk);
            res.on('end', () => {
                try {
                    resolve({ status: res.statusCode, data: JSON.parse(data) });
                } catch (e) {
                    resolve({ status: res.statusCode, data: data });
                }
            });
        }).on('error', reject);
    });
}

async function testTimeseries() {
    const markets = JSON.parse(fs.readFileSync('active_markets_test.json'));
    
    console.log('Testing timeseries API with active markets...\n');
    
    for (let i = 0; i < markets.length; i++) {
        const market = markets[i];
        console.log(`\n${'='.repeat(80)}`);
        console.log(`Market ${i + 1}: ${market.question.substring(0, 70)}`);
        console.log(`Token ID: ${market.token_id}`);
        console.log('='.repeat(80));
        
        // Test with 1 week, 1 hour fidelity
        const url = `https://clob.polymarket.com/prices-history?market=${market.token_id}&interval=1w&fidelity=60`;
        console.log(`\nFetching: ${url.substring(0, 100)}...`);
        
        const result = await httpGet(url);
        console.log(`Status: ${result.status}`);
        
        if (result.status === 200 && result.data.history) {
            const history = result.data.history;
            console.log(`✓ Data points: ${history.length}`);
            
            if (history.length > 0) {
                const first = history[0];
                const last = history[history.length - 1];
                
                console.log(`✓ First point: ${new Date(first.t * 1000).toISOString()} - Price: ${first.p}`);
                console.log(`✓ Last point: ${new Date(last.t * 1000).toISOString()} - Price: ${last.p}`);
                
                const duration = (last.t - first.t) / 3600;
                console.log(`✓ Duration: ${duration.toFixed(1)} hours`);
                
                // Calculate some stats
                const prices = history.map(h => parseFloat(h.p));
                const min = Math.min(...prices);
                const max = Math.max(...prices);
                const avg = prices.reduce((a, b) => a + b) / prices.length;
                
                console.log(`✓ Price range: ${min.toFixed(4)} - ${max.toFixed(4)}`);
                console.log(`✓ Average price: ${avg.toFixed(4)}`);
                
                // Check data quality
                const timeDiffs = [];
                for (let j = 1; j < history.length; j++) {
                    timeDiffs.push(history[j].t - history[j - 1].t);
                }
                const avgInterval = timeDiffs.reduce((a, b) => a + b) / timeDiffs.length;
                console.log(`✓ Average interval: ${(avgInterval / 60).toFixed(1)} minutes`);
                
                return true; // Success! We have data
            } else {
                console.log('⚠ Empty history array');
            }
        } else {
            console.log(`✗ Error or unexpected response`);
            console.log(JSON.stringify(result.data).substring(0, 200));
        }
        
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return false;
}

testTimeseries().then(success => {
    if (success) {
        console.log('\n\n' + '='.repeat(80));
        console.log('✅ TIMESERIES API VALIDATION: SUCCESS');
        console.log('The API works and provides historical price data!');
        console.log('='.repeat(80));
    } else {
        console.log('\n\n' + '='.repeat(80));
        console.log('❌ TIMESERIES API VALIDATION: FAILED');
        console.log('No historical data found for any active market');
        console.log('='.repeat(80));
    }
}).catch(err => {
    console.error('Fatal error:', err);
});
