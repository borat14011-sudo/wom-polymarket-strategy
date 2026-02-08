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

async function checkDateRanges() {
    console.log('Checking date ranges in Polymarket API...\n');
    
    // Fetch recent closed markets
    const data = await fetchJSON('gamma-api.polymarket.com', '/markets?limit=50&closed=true&order=endDate&ascending=false');
    
    if (!data) {
        console.log('Failed to fetch data');
        return;
    }
    
    const markets = Array.isArray(data) ? data : (data.data || []);
    
    const dates = markets
        .map(m => m.endDate)
        .filter(d => d)
        .map(d => new Date(d));
    
    dates.sort((a, b) => b - a);
    
    console.log('Most recent 20 end dates:');
    dates.slice(0, 20).forEach((d, i) => {
        console.log(`${i + 1}. ${d.toISOString().split('T')[0]} (${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')})`);
    });
    
    console.log(`\nOldest in sample: ${dates[dates.length - 1].toISOString().split('T')[0]}`);
    console.log(`Newest in sample: ${dates[0].toISOString().split('T')[0]}`);
    
    // Count by month/year
    const byMonth = {};
    dates.forEach(d => {
        const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
        byMonth[key] = (byMonth[key] || 0) + 1;
    });
    
    console.log('\nMarkets by month (in this sample):');
    Object.entries(byMonth)
        .sort((a, b) => b[0].localeCompare(a[0]))
        .slice(0, 15)
        .forEach(([month, count]) => {
            console.log(`  ${month}: ${count} markets`);
        });
}

checkDateRanges().catch(console.error);
