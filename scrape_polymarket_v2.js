#!/usr/bin/env node
const https = require('https');
const fs = require('fs');

class PolymarketScraper {
    constructor() {
        this.gammaBase = 'gamma-api.polymarket.com';
    }

    async fetchJSON(hostname, path) {
        return new Promise((resolve, reject) => {
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
            }).on('error', reject);
        });
    }

    async fetchMarketsGamma(limit = 100, offset = 0, params = {}) {
        const queryParams = new URLSearchParams({
            limit: limit.toString(),
            offset: offset.toString(),
            closed: 'true',
            ...params
        });
        
        const path = `/markets?${queryParams.toString()}`;
        return await this.fetchJSON(this.gammaBase, path);
    }

    isOctober2025(dateStr) {
        if (!dateStr) return false;
        try {
            const date = new Date(dateStr);
            return date.getFullYear() === 2025 && date.getMonth() === 9; // October = month 9
        } catch (e) {
            return false;
        }
    }

    extractMarketData(market) {
        try {
            const endDate = market.endDate || market.endDateIso;
            
            // Try to get outcome - check outcomePrices
            let outcome = null;
            let outcomePrices = [];
            
            if (typeof market.outcomePrices === 'string') {
                try {
                    outcomePrices = JSON.parse(market.outcomePrices);
                } catch (e) {}
            } else if (Array.isArray(market.outcomePrices)) {
                outcomePrices = market.outcomePrices;
            }
            
            // Determine winner from final prices
            if (market.closed && outcomePrices.length >= 2) {
                const yesPrice = parseFloat(outcomePrices[0] || 0);
                const noPrice = parseFloat(outcomePrices[1] || 0);
                
                if (yesPrice > 0.95) {
                    outcome = "YES";
                } else if (noPrice > 0.95) {
                    outcome = "NO";
                } else if (yesPrice > noPrice) {
                    outcome = "YES (likely)";
                } else if (noPrice > yesPrice) {
                    outcome = "NO (likely)";
                }
            }

            return {
                question: market.question || '',
                outcome: outcome || 'UNKNOWN',
                category: market.category || '',
                resolution_date: endDate,
                volume: parseFloat(market.volume || market.volumeNum || 0),
                market_id: market.conditionId || market.id || '',
                closed: market.closed || false
            };
        } catch (e) {
            console.error('Error extracting:', e.message);
            return null;
        }
    }

    async scrapeOctober2025Markets() {
        const allMarkets = [];
        const seenIds = new Set();
        
        console.log('Scraping October 2025 markets...\n');
        console.log('Strategy: Fetching markets with various sort orders to find Oct 2025\n');

        // Try different sorting approaches
        const strategies = [
            { order: 'endDate', ascending: 'false', name: 'Recent end dates first' },
            { order: 'endDate', ascending: 'true', name: 'Oldest end dates first' },
            { order: 'createdAt', ascending: 'false', name: 'Recently created first' },
        ];

        for (const strategy of strategies) {
            console.log(`\nTrying strategy: ${strategy.name}`);
            let offset = 0;
            let foundCount = 0;
            const maxOffset = 1000; // Limit per strategy

            while (offset < maxOffset) {
                const data = await this.fetchJSON(
                    this.gammaBase,
                    `/markets?limit=100&offset=${offset}&closed=true&order=${strategy.order}&ascending=${strategy.ascending}`
                );

                if (!data) break;
                
                const markets = Array.isArray(data) ? data : (data.data || []);
                if (markets.length === 0) break;

                for (const market of markets) {
                    const marketData = this.extractMarketData(market);
                    
                    if (marketData && !seenIds.has(marketData.market_id)) {
                        if (this.isOctober2025(marketData.resolution_date)) {
                            seenIds.add(marketData.market_id);
                            allMarkets.push(marketData);
                            foundCount++;
                            
                            if (foundCount <= 3) {
                                console.log(`  ✓ ${marketData.question.substring(0, 60)}...`);
                            }
                        }
                    }
                }

                // Early exit if we found many
                if (foundCount > 50 && offset > 500) break;
                
                offset += 100;
                await new Promise(r => setTimeout(r, 300));
            }

            console.log(`  Found ${foundCount} October 2025 markets with this strategy`);
            
            if (allMarkets.length > 100) {
                console.log(`  ✓ Target reached! (${allMarkets.length} total)`);
                break;
            }
        }

        console.log(`\n✓ Total unique October 2025 markets: ${allMarkets.length}\n`);
        return allMarkets;
    }

    saveToCSV(markets, filename = 'oct_2025_resolved.csv') {
        if (!markets || markets.length === 0) {
            console.log('⚠ No markets to save!');
            return;
        }

        const header = 'question,outcome,category,resolution_date,volume,market_id\n';
        const rows = markets.map(m => {
            const q = (m.question || '').replace(/"/g, '""');
            const o = (m.outcome || '').replace(/"/g, '""');
            const c = (m.category || '').replace(/"/g, '""');
            return `"${q}","${o}","${c}","${m.resolution_date}",${m.volume},"${m.market_id}"`;
        }).join('\n');

        fs.writeFileSync(filename, header + rows, 'utf8');
        console.log(`✓ Saved to ${filename}`);
    }

    printSummary(markets) {
        console.log('\n' + '='.repeat(60));
        console.log('SUMMARY');
        console.log('='.repeat(60));
        console.log(`Total markets: ${markets.length}`);
        console.log(`With outcomes: ${markets.filter(m => m.outcome && m.outcome !== 'UNKNOWN').length}`);
        
        const categories = new Set(markets.map(m => m.category || 'Unknown'));
        console.log(`Categories: ${categories.size}`);
        
        const totalVol = markets.reduce((s, m) => s + m.volume, 0);
        console.log(`Total volume: $${totalVol.toLocaleString('en-US', {maximumFractionDigits: 0})}`);

        console.log('\nTop 5 by volume:');
        markets
            .sort((a, b) => b.volume - a.volume)
            .slice(0, 5)
            .forEach((m, i) => {
                console.log(`\n${i + 1}. ${m.question.substring(0, 65)}...`);
                console.log(`   Outcome: ${m.outcome}`);
                console.log(`   Volume: $${m.volume.toLocaleString('en-US')}`);
            });
    }
}

async function main() {
    console.log('='.repeat(60));
    console.log('POLYMARKET OCTOBER 2025 SCRAPER');
    console.log('='.repeat(60));
    console.log();

    const scraper = new PolymarketScraper();
    const markets = await scraper.scrapeOctober2025Markets();

    if (markets && markets.length > 0) {
        scraper.saveToCSV(markets);
        scraper.printSummary(markets);
    } else {
        console.log('\n⚠ No October 2025 markets found!');
        console.log('Possible reasons:');
        console.log('  - October 2025 hasn\'t happened yet (check current date)');
        console.log('  - API structure changed');
        console.log('  - Markets not yet resolved');
    }
}

main().catch(console.error);
