#!/usr/bin/env node
const https = require('https');
const fs = require('fs');

class PolymarketScraper {
    constructor() {
        this.gammaBase = 'gamma-api.polymarket.com';
    }

    async fetchJSON(hostname, path) {
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

    isOctober2025(dateStr) {
        if (!dateStr) return false;
        try {
            const date = new Date(dateStr);
            return date.getFullYear() === 2025 && date.getMonth() === 9;
        } catch (e) {
            return false;
        }
    }

    extractMarketData(market) {
        try {
            const endDate = market.endDate || market.endDateIso;
            
            let outcome = null;
            let outcomePrices = [];
            
            if (typeof market.outcomePrices === 'string') {
                try {
                    outcomePrices = JSON.parse(market.outcomePrices);
                } catch (e) {}
            } else if (Array.isArray(market.outcomePrices)) {
                outcomePrices = market.outcomePrices;
            }
            
            // Determine outcome
            if (market.closed && outcomePrices.length >= 2) {
                const yesPrice = parseFloat(outcomePrices[0] || 0);
                const noPrice = parseFloat(outcomePrices[1] || 0);
                
                if (yesPrice > 0.98) {
                    outcome = "YES";
                } else if (noPrice > 0.98) {
                    outcome = "NO";
                } else if (yesPrice > 0.90) {
                    outcome = "YES (likely)";
                } else if (noPrice > 0.90) {
                    outcome = "NO (likely)";
                } else {
                    outcome = `UNCLEAR (Y:${yesPrice.toFixed(2)} N:${noPrice.toFixed(2)})`;
                }
            } else if (!market.closed) {
                // Market not closed yet - check if it should be
                const now = new Date();
                const endDateObj = new Date(endDate);
                if (endDateObj < now) {
                    outcome = "PENDING RESOLUTION";
                } else {
                    outcome = "NOT YET ENDED";
                }
            }

            return {
                question: market.question || '',
                outcome: outcome || 'UNKNOWN',
                category: market.category || '',
                resolution_date: endDate,
                volume: parseFloat(market.volume || market.volumeNum || 0),
                market_id: market.conditionId || market.id || '',
                closed: market.closed || false,
                final_yes_price: outcomePrices[0] || '0',
                final_no_price: outcomePrices[1] || '0'
            };
        } catch (e) {
            return null;
        }
    }

    async scrapeOctober2025Markets() {
        const allMarkets = [];
        const seenIds = new Set();
        
        console.log('Searching for ALL markets with October 2025 end dates...\n');

        // Try without closed filter - get everything!
        let offset = 0;
        const maxFetch = 5000; // Fetch up to 5000 markets
        
        while (offset < maxFetch) {
            process.stdout.write(`\rFetching offset ${offset}...`);
            
            const data = await this.fetchJSON(
                this.gammaBase,
                `/markets?limit=100&offset=${offset}`  // No closed filter!
            );

            if (!data) break;
            
            const markets = Array.isArray(data) ? data : (data.data || []);
            if (markets.length === 0) break;

            let foundInBatch = 0;
            for (const market of markets) {
                const marketData = this.extractMarketData(market);
                
                if (marketData && !seenIds.has(marketData.market_id)) {
                    if (this.isOctober2025(marketData.resolution_date)) {
                        seenIds.add(marketData.market_id);
                        allMarkets.push(marketData);
                        foundInBatch++;
                    }
                }
            }

            if (foundInBatch > 0) {
                console.log(` Found ${foundInBatch} Oct 2025 markets in this batch!`);
            }

            offset += 100;
            await new Promise(r => setTimeout(r, 200));
        }

        console.log(`\n\n✓ Total October 2025 markets found: ${allMarkets.length}\n`);
        return allMarkets;
    }

    saveToCSV(markets, filename = 'oct_2025_resolved.csv') {
        if (!markets || markets.length === 0) {
            console.log('⚠ No markets to save!');
            return;
        }

        const header = 'question,outcome,category,resolution_date,volume,market_id,closed,final_yes_price,final_no_price\n';
        const rows = markets.map(m => {
            const q = (m.question || '').replace(/"/g, '""');
            const o = (m.outcome || '').replace(/"/g, '""');
            const c = (m.category || '').replace(/"/g, '""');
            return `"${q}","${o}","${c}","${m.resolution_date}",${m.volume},"${m.market_id}",${m.closed},${m.final_yes_price},${m.final_no_price}`;
        }).join('\n');

        fs.writeFileSync(filename, header + rows, 'utf8');
        console.log(`✓ Saved to ${filename}`);
    }

    printSummary(markets) {
        console.log('\n' + '='.repeat(70));
        console.log('SUMMARY');
        console.log('='.repeat(70));
        console.log(`Total October 2025 markets: ${markets.length}`);
        console.log(`Closed/resolved: ${markets.filter(m => m.closed).length}`);
        console.log(`Pending resolution: ${markets.filter(m => !m.closed).length}`);
        console.log(`With clear outcomes: ${markets.filter(m => m.outcome && (m.outcome === 'YES' || m.outcome === 'NO')).length}`);
        
        const categories = [...new Set(markets.map(m => m.category || 'Unknown'))];
        console.log(`Categories: ${categories.length}`);
        console.log(`  ${categories.slice(0, 5).join(', ')}${categories.length > 5 ? '...' : ''}`);
        
        const totalVol = markets.reduce((s, m) => s + m.volume, 0);
        console.log(`Total volume: $${totalVol.toLocaleString('en-US', {maximumFractionDigits: 0})}`);

        console.log('\nTop 10 by volume:');
        markets
            .sort((a, b) => b.volume - a.volume)
            .slice(0, 10)
            .forEach((m, i) => {
                console.log(`\n${i + 1}. ${m.question.substring(0, 60)}...`);
                console.log(`   Outcome: ${m.outcome}`);
                console.log(`   Volume: $${m.volume.toLocaleString('en-US')}`);
                console.log(`   Closed: ${m.closed ? 'YES' : 'NO'}`);
            });
    }
}

async function main() {
    console.log('='.repeat(70));
    console.log('POLYMARKET OCTOBER 2025 MARKETS SCRAPER (ALL MARKETS)');
    console.log('='.repeat(70));
    console.log();

    const scraper = new PolymarketScraper();
    const markets = await scraper.scrapeOctober2025Markets();

    if (markets && markets.length > 0) {
        scraper.saveToCSV(markets);
        scraper.printSummary(markets);
        
        console.log('\n' + '='.repeat(70));
        console.log('NOTE: Some markets may still be pending resolution.');
        console.log('For backtesting, filter for closed=true and clear YES/NO outcomes.');
        console.log('='.repeat(70));
    } else {
        console.log('\n⚠ No October 2025 markets found!');
    }
}

main().catch(console.error);
