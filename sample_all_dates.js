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

async function sampleDates() {
    console.log('Sampling 500 markets to see date distribution...\n');
    
    const allDates = [];
    
    for (let offset = 0; offset < 500; offset += 100) {
        const data = await fetchJSON('gamma-api.polymarket.com', `/markets?limit=100&offset=${offset}`);
        if (!data) continue;
        
        const markets = Array.isArray(data) ? data : (data.data || []);
        markets.forEach(m => {
            if (m.endDate) {
                const d = new Date(m.endDate);
                allDates.push({
                    date: d,
                    yearMonth: `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`,
                    question: m.question,
                    closed: m.closed
                });
            }
        });
        
        await new Promise(r => setTimeout(r, 200));
    }
    
    console.log(`Sampled ${allDates.length} markets\n`);
    
    // Group by year-month
    const byMonth = {};
    allDates.forEach(({yearMonth, closed}) => {
        if (!byMonth[yearMonth]) byMonth[yearMonth] = {total: 0, closed: 0};
        byMonth[yearMonth].total++;
        if (closed) byMonth[yearMonth].closed++;
    });
    
    console.log('Date distribution:');
    Object.entries(byMonth)
        .sort((a, b) => a[0].localeCompare(b[0]))
        .forEach(([month, counts]) => {
            console.log(`  ${month}: ${counts.total} markets (${counts.closed} closed)`);
        });
    
    // Check specifically for October 2025
    const oct2025 = allDates.filter(d => d.yearMonth === '2025-10');
    console.log(`\n*** October 2025 markets in sample: ${oct2025.length} ***`);
    if (oct2025.length > 0) {
        oct2025.slice(0, 5).forEach(m => {
            console.log(`  - ${m.question.substring(0, 60)}... (closed: ${m.closed})`);
        });
    }
}

sampleDates().catch(console.error);
