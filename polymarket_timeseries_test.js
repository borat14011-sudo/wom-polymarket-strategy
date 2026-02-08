#!/usr/bin/env node
/**
 * Polymarket Timeseries API Validation Script
 * Tests historical price data API and validates data quality
 */

const https = require('https');
const fs = require('fs');

const CLOB_BASE = "https://clob.polymarket.com";

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

async function fetchPriceHistory(tokenId, interval = "1w", fidelity = 60) {
    const params = new URLSearchParams({
        market: tokenId,
        fidelity: fidelity.toString(),
        interval: interval
    });
    
    const url = `${CLOB_BASE}/prices-history?${params}`;
    console.log(`Fetching: ${url}`);
    
    try {
        const result = await httpGet(url);
        console.log(`Status: ${result.status}`);
        
        if (result.status === 200) {
            const keys = typeof result.data === 'object' ? Object.keys(result.data) : 'Array';
            console.log(`Response type: ${typeof result.data}, keys/length: ${keys}`);
            return result.data;
        } else {
            console.log(`Error: ${result.status} - ${JSON.stringify(result.data).substring(0, 200)}`);
            return null;
        }
    } catch (e) {
        console.log(`Exception: ${e.message}`);
        return null;
    }
}

function analyzeDataQuality(data, tokenId, description = "") {
    if (!data) {
        return { error: "No data received" };
    }
    
    // Handle different response formats
    let history;
    if (data.history && Array.isArray(data.history)) {
        history = data.history;
    } else if (Array.isArray(data)) {
        history = data;
    } else {
        return { error: `Unexpected data format: ${typeof data}` };
    }
    
    if (!history || history.length === 0) {
        return { error: "Empty history" };
    }
    
    // Check structure
    if (!history[0].t || history[0].p === undefined) {
        return { error: `Missing expected fields. Found: ${Object.keys(history[0])}` };
    }
    
    // Convert to timestamps
    const points = history.map(h => ({
        timestamp: new Date(h.t * 1000),
        price: parseFloat(h.p)
    })).sort((a, b) => a.timestamp - b.timestamp);
    
    // Calculate metrics
    const prices = points.map(p => p.price);
    const timestamps = points.map(p => p.timestamp.getTime());
    
    const analysis = {
        token_id: tokenId,
        description: description,
        total_points: points.length,
        start_time: points[0].timestamp.toISOString(),
        end_time: points[points.length - 1].timestamp.toISOString(),
        duration_hours: (timestamps[timestamps.length - 1] - timestamps[0]) / (1000 * 3600),
        price_range: [Math.min(...prices), Math.max(...prices)],
        price_mean: prices.reduce((a, b) => a + b) / prices.length,
        data_sample: points.slice(0, 5).map(p => ({
            time: p.timestamp.toISOString(),
            price: p.price
        }))
    };
    
    // Check for time gaps
    const timeDiffs = [];
    for (let i = 1; i < timestamps.length; i++) {
        timeDiffs.push(timestamps[i] - timestamps[i - 1]);
    }
    timeDiffs.sort((a, b) => a - b);
    const medianDiff = timeDiffs[Math.floor(timeDiffs.length / 2)];
    const largeGaps = timeDiffs.filter(d => d > medianDiff * 3);
    
    analysis.missing_data_gaps = largeGaps.length;
    analysis.median_interval_seconds = medianDiff / 1000;
    
    return { analysis, points };
}

async function testApiEndpoint() {
    console.log("\n" + "=".repeat(80));
    console.log("TEST 1: API ENDPOINT VALIDATION");
    console.log("=".repeat(80));
    
    // Fetch active markets to get real token IDs
    console.log("\nFetching active markets to get real token IDs...");
    const marketsUrl = `${CLOB_BASE}/markets`;
    
    try {
        const result = await httpGet(marketsUrl);
        if (result.status !== 200) {
            console.log(`Failed to fetch markets: ${result.status}`);
            return [];
        }
        
        const markets = result.data.data || result.data;
        if (!Array.isArray(markets)) {
            console.log(`Unexpected format: ${typeof markets}, keys: ${Object.keys(markets)}`);
            return [];
        }
        console.log(`Found ${markets.length} markets`);
        
        // Get first 5 active markets with tokens
        const testMarkets = [];
        for (const market of markets.slice(0, 30)) {
            if (market.tokens && market.tokens.length > 0 && market.active !== false) {
                const token = market.tokens[0];
                testMarkets.push({
                    token_id: token.token_id,
                    outcome: token.outcome || 'Unknown',
                    question: (market.question || 'Unknown').substring(0, 80)
                });
                
                if (testMarkets.length >= 5) break;
            }
        }
        
        console.log(`\nSelected ${testMarkets.length} markets for testing:`);
        testMarkets.forEach((m, i) => {
            console.log(`${i + 1}. ${m.outcome}: ${m.question}`);
        });
        
        return testMarkets;
    } catch (e) {
        console.log(`Error fetching markets: ${e.message}`);
        return [];
    }
}

async function testDataQuality(testMarkets) {
    console.log("\n" + "=".repeat(80));
    console.log("TEST 2: DATA QUALITY VALIDATION");
    console.log("=".repeat(80));
    
    const results = [];
    
    for (const market of testMarkets) {
        const { token_id, outcome, question } = market;
        const description = `${outcome}: ${question}`;
        
        console.log(`\n--- Testing: ${description}`);
        
        // Test different fidelity settings
        for (const fidelity of [60, 360, 1440]) { // 1h, 6h, 1d
            console.log(`\nFidelity: ${fidelity} minutes`);
            const data = await fetchPriceHistory(token_id, "1w", fidelity);
            
            if (data) {
                const result = analyzeDataQuality(data, token_id, description);
                if (result.analysis) {
                    const { analysis } = result;
                    analysis.fidelity = fidelity;
                    results.push(analysis);
                    
                    console.log(`✓ Points: ${analysis.total_points}`);
                    console.log(`✓ Duration: ${analysis.duration_hours.toFixed(1)} hours`);
                    console.log(`✓ Price range: ${JSON.stringify(analysis.price_range)}`);
                    console.log(`✓ Gaps detected: ${analysis.missing_data_gaps}`);
                } else {
                    console.log(`✗ Error: ${result.error}`);
                }
            } else {
                console.log(`✗ Failed to fetch data`);
            }
            
            // Rate limit courtesy
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }
    
    return results;
}

async function main() {
    console.log("POLYMARKET TIMESERIES API VALIDATION");
    console.log("Starting tests...\n");
    
    // Test 1: Get real market token IDs
    const testMarkets = await testApiEndpoint();
    
    if (testMarkets.length === 0) {
        console.log("\n❌ CRITICAL: Could not fetch test markets. Aborting.");
        process.exit(1);
    }
    
    // Test 2: Validate data quality
    const qualityResults = await testDataQuality(testMarkets);
    
    // Save results
    console.log("\n" + "=".repeat(80));
    console.log("SAVING RESULTS");
    console.log("=".repeat(80));
    
    const output = {
        test_markets: testMarkets,
        quality_results: qualityResults,
        timestamp: new Date().toISOString()
    };
    
    fs.writeFileSync('api_test_results.json', JSON.stringify(output, null, 2));
    console.log("✓ Saved to api_test_results.json");
    
    // Generate summary
    console.log("\n" + "=".repeat(80));
    console.log("SUMMARY");
    console.log("=".repeat(80));
    
    if (qualityResults.length > 0) {
        console.log(`✓ API is functional`);
        console.log(`✓ Tested ${testMarkets.length} markets`);
        console.log(`✓ Retrieved ${qualityResults.length} datasets`);
        
        const avgPoints = qualityResults.reduce((sum, r) => sum + r.total_points, 0) / qualityResults.length;
        console.log(`✓ Average data points per dataset: ${avgPoints.toFixed(0)}`);
        
        const totalGaps = qualityResults.reduce((sum, r) => sum + r.missing_data_gaps, 0);
        console.log(`⚠ Total data gaps detected: ${totalGaps}`);
        
        return { success: true, testMarkets, qualityResults };
    } else {
        console.log("❌ No data retrieved - API may not be working");
        return { success: false, testMarkets, qualityResults };
    }
}

main().then(result => {
    if (!result.success) {
        process.exit(1);
    }
}).catch(err => {
    console.error("Fatal error:", err);
    process.exit(1);
});
