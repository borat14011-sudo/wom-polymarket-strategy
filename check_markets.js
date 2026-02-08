const https = require('https');

https.get('https://clob.polymarket.com/markets', (res) => {
    let data = '';
    res.on('data', (chunk) => data += chunk);
    res.on('end', () => {
        const markets = JSON.parse(data).data;
        
        console.log('Sample market 1:');
        const m = markets[0];
        console.log(JSON.stringify({
            question: m.question,
            active: m.active,
            closed: m.closed,
            archived: m.archived,
            end_date_iso: m.end_date_iso,
            tokens: m.tokens.length
        }, null, 2));
        
        console.log('\nSample market 50:');
        const m2 = markets[50];
        console.log(JSON.stringify({
            question: m2.question,
            active: m2.active,
            closed: m2.closed,
            end_date_iso: m2.end_date_iso
        }, null, 2));
        
        console.log('\nChecking first 100:');
        const activeCount = markets.slice(0, 100).filter(m => m.active).length;
        const notClosed = markets.slice(0, 100).filter(m => !m.closed).length;
        const notArchived = markets.slice(0, 100).filter(m => !m.archived).length;
        console.log('Active:', activeCount, '/100');
        console.log('Not closed:', notClosed, '/100');
        console.log('Not archived:', notArchived, '/100');
        
        // Find any from 2026
        console.log('\nSearching for 2026 markets...');
        const recent = markets.filter(m => {
            const q = m.question || '';
            return q.includes('2026');
        }).slice(0, 5);
        
        console.log('Found', recent.length, '2026 markets');
        recent.forEach((m, i) => {
            console.log(`${i + 1}. ${m.question.substring(0, 80)}`);
            console.log(`   Active: ${m.active}, Closed: ${m.closed}`);
            console.log(`   Token ID: ${m.tokens[0]?.token_id}`);
        });
    });
});
