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
                    resolve(null);
                }
            });
        }).on('error', () => resolve(null));
    });
}

async function debugMarkets() {
    const response = await fetchJSON('clob.polymarket.com', '/markets');
    
    if (response && response.data && response.data.length > 0) {
        console.log('Sample CLOB market structure:\n');
        console.log(JSON.stringify(response.data[0], null, 2));
        
        console.log('\n\nChecking date fields in first 10 markets:');
        response.data.slice(0, 10).forEach((m, i) => {
            console.log(`\n${i + 1}. ${m.question ? m.question.substring(0, 50) : 'N/A'}...`);
            console.log(`   end_date_iso: ${m.end_date_iso}`);
            console.log(`   end_date: ${m.end_date}`);
            console.log(`   closed: ${m.closed}`);
            
            if (m.end_date_iso) {
                const d = new Date(m.end_date_iso);
                console.log(`   Parsed: ${d.getFullYear()}-${d.getMonth() + 1}`);
            }
        });
    }
}

debugMarkets().catch(console.error);
