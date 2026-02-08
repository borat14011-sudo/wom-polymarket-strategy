#!/usr/bin/env node
const https = require('https');
const fs = require('fs');

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

async function enhanceWithVolume() {
    console.log('Reading CSV...');
    const csvContent = fs.readFileSync('oct_2025_resolved.csv', 'utf8');
    const lines = csvContent.split('\n');
    const header = lines[0];
    const dataLines = lines.slice(1).filter(l => l.trim());
    
    console.log(`Found ${dataLines.length} markets\n`);
    console.log('Fetching volume data from Gamma API...\n');
    
    const markets = dataLines.map(line => {
        const match = line.match(/"([^"]*?)","([^"]*?)","([^"]*?)","([^"]*?)",(\d+),"([^"]*?)",(\w+)/);
        if (match) {
            return {
                question: match[1],
                outcome: match[2],
                category: match[3],
                resolution_date: match[4],
                volume: parseFloat(match[5]),
                market_id: match[6],
                closed: match[7] === 'true'
            };
        }
        return null;
    }).filter(m => m);
    
    // Fetch Gamma API data for volume
    console.log('Scanning Gamma API for matching markets...');
    const volumeMap = {};
    
    for (let offset = 0; offset < 50000; offset += 100) {
        if (offset % 1000 === 0) {
            process.stdout.write(`\rFetched ${offset} markets from Gamma...`);
        }
        
        const data = await fetchJSON('gamma-api.polymarket.com', `/markets?limit=100&offset=${offset}`);
        if (!data) break;
        
        const gammaMarkets = Array.isArray(data) ? data : (data.data || []);
        if (gammaMarkets.length === 0) break;
        
        for (const gm of gammaMarkets) {
            const condId = gm.conditionId || gm.condition_id;
            if (condId) {
                volumeMap[condId] = {
                    volume: parseFloat(gm.volume || gm.volumeNum || 0),
                    category: gm.category || gm.groupItemTitle || ''
                };
            }
        }
        
        await new Promise(r => setTimeout(r, 100));
    }
    
    console.log(`\n\nMatching ${markets.length} markets with Gamma data...`);
    
    let matched = 0;
    markets.forEach(m => {
        if (volumeMap[m.market_id]) {
            m.volume = volumeMap[m.market_id].volume;
            if (!m.category && volumeMap[m.market_id].category) {
                m.category = volumeMap[m.market_id].category;
            }
            matched++;
        }
    });
    
    console.log(`✓ Matched ${matched} markets with volume data\n`);
    
    // Save enhanced CSV
    const newHeader = 'question,outcome,category,resolution_date,volume,market_id,closed\n';
    const newRows = markets.map(m => {
        const q = m.question.replace(/"/g, '""');
        const o = m.outcome.replace(/"/g, '""');
        const c = m.category.replace(/"/g, '""');
        return `"${q}","${o}","${c}","${m.resolution_date}",${m.volume},"${m.market_id}",${m.closed}`;
    }).join('\n');
    
    fs.writeFileSync('oct_2025_resolved.csv', newHeader + newRows, 'utf8');
    console.log('✓ Updated oct_2025_resolved.csv with volume data\n');
    
    // Print summary
    console.log('='.repeat(70));
    console.log('FINAL SUMMARY');
    console.log('='.repeat(70));
    console.log(`Total markets: ${markets.length}`);
    console.log(`All closed: ${markets.filter(m => m.closed).length}`);
    console.log(`All with outcomes: ${markets.filter(m => m.outcome !== 'UNKNOWN').length}`);
    
    const totalVol = markets.reduce((s, m) => s + m.volume, 0);
    console.log(`Total volume: $${totalVol.toLocaleString('en-US', {maximumFractionDigits: 0})}`);
    console.log(`Markets with volume > 0: ${markets.filter(m => m.volume > 0).length}`);
    
    const categories = [...new Set(markets.map(m => m.category).filter(c => c))];
    console.log(`Categories: ${categories.length > 0 ? categories.join(', ') : 'None'}`);
    
    console.log(`\nTop 15 by volume:`);
    markets
        .sort((a, b) => b.volume - a.volume)
        .slice(0, 15)
        .forEach((m, i) => {
            console.log(`${i + 1}. ${m.question.substring(0, 60)}...`);
            console.log(`   Volume: $${m.volume.toLocaleString('en-US')} | Outcome: ${m.outcome}`);
        });
}

enhanceWithVolume().catch(console.error);
