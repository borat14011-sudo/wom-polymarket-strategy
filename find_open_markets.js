const https = require('https');

https.get('https://clob.polymarket.com/markets', (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        const markets = JSON.parse(data).data;
        
        console.log('Total markets:', markets.length);
        
        // Find markets that are NOT closed
        const openMarkets = markets.filter(m => m.closed === false && m.tokens && m.tokens.length > 0);
        
        console.log('Open (not closed) markets:', openMarkets.length);
        console.log('\nFirst 10 open markets:\n');
        
        openMarkets.slice(0, 10).forEach((m, i) => {
            const token = m.tokens[0];
            console.log(`${i + 1}. ${m.question.substring(0, 80)}`);
            console.log(`   Token ID: ${token.token_id}`);
            console.log(`   End: ${m.end_date_iso || 'N/A'}`);
            console.log(`   Active: ${m.active}, Closed: ${m.closed}, Archived: ${m.archived}`);
            console.log('');
        });
    });
});
