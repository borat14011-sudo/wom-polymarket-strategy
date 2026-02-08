const https = require('https');

https.get('https://clob.polymarket.com/markets', (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        const markets = JSON.parse(data).data;
        
        console.log('Total markets:', markets.length);
        
        // Find markets that are truly tradeable
        const tradeable = markets.filter(m => 
            m.closed === false && 
            m.archived === false && 
            m.tokens && 
            m.tokens.length > 0 &&
            m.tokens[0].token_id
        );
        
        console.log('Tradeable (not closed, not archived) markets:', tradeable.length);
        
        if (tradeable.length > 0) {
            console.log('\nFirst 10 tradeable markets:\n');
            
            tradeable.slice(0, 10).forEach((m, i) => {
                const token = m.tokens[0];
                console.log(`${i + 1}. ${m.question.substring(0, 80)}`);
                console.log(`   Token ID: ${token.token_id}`);
                console.log(`   Outcome: ${token.outcome}`);
                console.log(`   End: ${m.end_date_iso || 'N/A'}`);
                console.log('');
            });
            
            // Save first 5 for testing
            const testMarkets = tradeable.slice(0, 5).map(m => ({
                token_id: m.tokens[0].token_id,
                outcome: m.tokens[0].outcome,
                question: m.question
            }));
            
            require('fs').writeFileSync('tradeable_markets.json', JSON.stringify(testMarkets, null, 2));
            console.log('✓ Saved 5 tradeable markets to tradeable_markets.json');
        } else {
            console.log('\n❌ No tradeable markets found!');
            
            // Let's check what we DO have
            console.log('\nBreakdown of markets:');
            const closedCount = markets.filter(m => m.closed).length;
            const archivedCount = markets.filter(m => m.archived).length;
            const hasTokens = markets.filter(m => m.tokens && m.tokens.length > 0).length;
            
            console.log('Closed:', closedCount);
            console.log('Archived:', archivedCount);
            console.log('Has tokens:', hasTokens);
        }
    });
});
