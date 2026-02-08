const https = require('https');
const fs = require('fs');

https.get('https://gamma-api.polymarket.com/markets?closed=false&limit=100&archived=false', (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        const markets = JSON.parse(data);
        
        console.log('Total active markets:', markets.length);
        
        // Filter for markets with CLOB token IDs
        const withTokens = markets.filter(m => m.clobTokenIds && m.clobTokenIds.length > 0);
        
        console.log('Markets with CLOB tokens:', withTokens.length);
        
        // Get first 5 for testing
        const testMarkets = withTokens.slice(0, 5).map(m => {
            // Parse CLOB token IDs - they're JSON encoded arrays
            let tokenIds;
            try {
                tokenIds = JSON.parse(m.clobTokenIds);
            } catch (e) {
                tokenIds = m.clobTokenIds.split(',');
            }
            return {
                question: m.question,
                token_id: tokenIds[0], // Get first outcome token
                end_date: m.endDateIso,
                outcomes: m.outcomes
            };
        });
        
        console.log('\nTest markets:\n');
        testMarkets.forEach((m, i) => {
            console.log(`${i + 1}. ${m.question.substring(0, 80)}`);
            console.log(`   Token ID: ${m.token_id}`);
            console.log(`   End date: ${m.end_date}`);
            console.log('');
        });
        
        fs.writeFileSync('active_markets_test.json', JSON.stringify(testMarkets, null, 2));
        console.log('✓ Saved to active_markets_test.json');
    });
});
