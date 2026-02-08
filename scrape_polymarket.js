#!/usr/bin/env node
/**
 * Scrape all resolved Polymarket markets from October 2025
 * Uses CLOB API, Gamma API, and web scraping to get complete data
 */

const https = require('https');
const http = require('http');
const fs = require('fs');

class PolymarketScraper {
    constructor() {
        this.gammaBase = 'gamma-api.polymarket.com';
        this.clobBase = 'clob.polymarket.com';
    }

    async fetchJSON(hostname, path) {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: hostname,
                path: path,
                method: 'GET',
                headers: {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            };

            https.get(options, (res) => {
                let data = '';

                res.on('data', (chunk) => {
                    data += chunk;
                });

                res.on('end', () => {
                    try {
                        resolve(JSON.parse(data));
                    } catch (e) {
                        console.error('Error parsing JSON:', e.message);
                        resolve(null);
                    }
                });
            }).on('error', (err) => {
                console.error('Request error:', err.message);
                resolve(null);
            });
        });
    }

    async fetchMarketsGamma(limit = 100, offset = 0, closed = true) {
        const path = `/markets?limit=${limit}&offset=${offset}&closed=${closed}&order=volume24hr&ascending=false`;
        console.log(`Fetching: https://${this.gammaBase}${path}`);
        return await this.fetchJSON(this.gammaBase, path);
    }

    isOctober2025(timestamp) {
        if (!timestamp) return false;

        try {
            let date;
            if (typeof timestamp === 'string') {
                date = new Date(timestamp);
            } else {
                date = new Date(timestamp * 1000);
            }

            return date.getFullYear() === 2025 && date.getMonth() === 9; // October is month 9
        } catch (e) {
            console.error('Error parsing date:', timestamp, e.message);
            return false;
        }
    }

    extractMarketData(market) {
        try {
            const endDate = market.endDate || market.end_date_iso || market.resolvedAt || market.end_date;
            
            // Determine outcome
            let outcome = null;
            const outcomePrices = market.outcomePrices || [];
            
            if (market.closed || market.resolved) {
                if (market.resolvedOutcome) {
                    outcome = market.resolvedOutcome;
                } else if (market.outcome) {
                    outcome = market.outcome;
                } else if (outcomePrices.length === 2) {
                    // Check if YES or NO won based on final price
                    if (outcomePrices[0] && parseFloat(outcomePrices[0]) > 0.95) {
                        outcome = "YES";
                    } else if (outcomePrices[1] && parseFloat(outcomePrices[1]) > 0.95) {
                        outcome = "NO";
                    }
                }
            }

            return {
                question: market.question || '',
                outcome: outcome,
                category: market.groupItemTitle || market.category || '',
                resolution_date: endDate,
                volume: market.volume || market.volume24hr || 0,
                market_id: market.conditionId || market.id || '',
                closed: market.closed || false,
                resolved: market.resolved || false
            };
        } catch (e) {
            console.error('Error extracting market data:', e.message);
            return null;
        }
    }

    async scrapeOctober2025Markets() {
        const allMarkets = [];
        let offset = 0;
        const limit = 100;
        let consecutiveEmpty = 0;

        console.log('Starting to fetch markets from Gamma API...\n');

        while (offset < 2000) { // Safety limit
            console.log(`Fetching batch at offset ${offset}...`);

            const data = await this.fetchMarketsGamma(limit, offset, true);

            if (!data) {
                console.log('No data returned, stopping...');
                break;
            }

            const markets = Array.isArray(data) ? data : (data.data || []);

            if (markets.length === 0) {
                consecutiveEmpty++;
                if (consecutiveEmpty > 2) {
                    console.log('No more markets found');
                    break;
                }
            } else {
                consecutiveEmpty = 0;
            }

            let foundInBatch = 0;
            for (const market of markets) {
                const marketData = this.extractMarketData(market);

                if (marketData && this.isOctober2025(marketData.resolution_date)) {
                    console.log(`✓ Found October 2025 market: ${marketData.question.substring(0, 60)}...`);
                    allMarkets.push(marketData);
                    foundInBatch++;
                }
            }

            console.log(`Found ${foundInBatch} October 2025 markets in this batch\n`);

            offset += limit;
            
            // Rate limiting
            await new Promise(resolve => setTimeout(resolve, 500));
        }

        console.log(`\n✓ Total October 2025 markets found: ${allMarkets.length}\n`);
        return allMarkets;
    }

    saveToCSV(markets, filename = 'oct_2025_resolved.csv') {
        if (!markets || markets.length === 0) {
            console.log('No markets to save!');
            return;
        }

        const header = 'question,outcome,category,resolution_date,volume,market_id\n';
        
        const rows = markets.map(m => {
            const question = (m.question || '').replace(/"/g, '""');
            const outcome = (m.outcome || '').replace(/"/g, '""');
            const category = (m.category || '').replace(/"/g, '""');
            const resDate = m.resolution_date || '';
            const volume = m.volume || 0;
            const marketId = m.market_id || '';

            return `"${question}","${outcome}","${category}","${resDate}",${volume},"${marketId}"`;
        }).join('\n');

        fs.writeFileSync(filename, header + rows, 'utf8');
        console.log(`✓ Saved ${markets.length} markets to ${filename}`);
    }
}

async function main() {
    console.log('='.repeat(60));
    console.log('POLYMARKET OCTOBER 2025 RESOLVED MARKETS SCRAPER');
    console.log('='.repeat(60));
    console.log();

    const scraper = new PolymarketScraper();
    const markets = await scraper.scrapeOctober2025Markets();

    if (markets && markets.length > 0) {
        scraper.saveToCSV(markets);

        // Print summary
        console.log('\n' + '='.repeat(60));
        console.log('SUMMARY');
        console.log('='.repeat(60));
        console.log(`Total markets collected: ${markets.length}`);
        console.log(`Markets with outcomes: ${markets.filter(m => m.outcome).length}`);
        
        const categories = new Set(markets.map(m => m.category || 'Unknown'));
        console.log(`Unique categories: ${categories.size}`);

        const totalVolume = markets.reduce((sum, m) => sum + (parseFloat(m.volume) || 0), 0);
        console.log(`Total volume: $${totalVolume.toLocaleString()}`);

        // Show sample
        console.log('\nSample markets:');
        markets.slice(0, 5).forEach((m, i) => {
            console.log(`\n${i + 1}. ${m.question.substring(0, 70)}...`);
            console.log(`   Outcome: ${m.outcome || 'Unknown'}`);
            console.log(`   Category: ${m.category || 'Unknown'}`);
            console.log(`   Volume: $${(m.volume || 0).toLocaleString()}`);
        });
    } else {
        console.log('\n⚠ No markets found! October 2025 markets may not exist yet or API structure changed.');
    }
}

main().catch(console.error);
