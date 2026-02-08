const https = require('https');
const fs = require('fs');
const path = require('path');

// Load the well data
const wellsData = JSON.parse(fs.readFileSync('wells_data.json', 'utf8'));

const outputDir = 'C:\\Users\\Borat\\.openclaw\\workspace\\sonris_unit_orders';

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

function fetchUrl(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (response) => {
            let data = '';
            response.on('data', chunk => data += chunk);
            response.on('end', () => resolve(data));
        }).on('error', reject);
    });
}

function parseDocuments(html) {
    const documents = [];
    
    // Look for document patterns in the HTML
    // The SONRIS system has document IDs like dDocname=12345678
    const docIdPattern = /dDocname=(\d+)/g;
    const docTypePattern = /UNIT\s+(?:AGREEMENT|ORDER)/gi;
    
    let match;
    const docIds = new Set();
    while ((match = docIdPattern.exec(html)) !== null) {
        docIds.add(match[1]);
    }
    
    // Check if UNIT AGREEMENT or UNIT ORDER appears in the HTML
    const hasUnitDocs = docTypePattern.test(html);
    
    // Extract more detailed info
    const rows = html.split(/<tr|<TR/).slice(1);
    
    for (const row of rows) {
        if (/UNIT\s+(?:AGREEMENT|ORDER)/i.test(row)) {
            const docMatch = /dDocname=(\d+)/.exec(row);
            if (docMatch) {
                const docId = docMatch[1];
                let docType = 'UNIT DOCUMENT';
                
                if (/UNIT\s+AGREEMENT/i.test(row)) {
                    docType = 'UNIT AGREEMENT/AMENDMENT';
                } else if (/UNIT\s+ORDER/i.test(row)) {
                    docType = 'UNIT ORDER';
                }
                
                // Try to extract date
                let date = null;
                const dateMatch = row.match(/\d{1,2}\/\d{1,2}\/\d{4}/);
                if (dateMatch) {
                    date = dateMatch[0];
                }
                
                documents.push({
                    docId,
                    docType,
                    date
                });
            }
        }
    }
    
    return documents;
}

function downloadDocument(docId, wellSerial, docType, index) {
    return new Promise((resolve, reject) => {
        const url = `https://sonlite.dnr.state.la.us/dnrservices/redirectUrl.jsp?dDocname=${docId}&showInline=True&nativeFile=True`;
        const filename = `well_${wellSerial}_unit_doc_${docId}.pdf`;
        const outputPath = path.join(outputDir, filename);
        
        console.log(`  Downloading: ${filename}`);
        
        https.get(url, (response) => {
            if (response.statusCode === 302 || response.statusCode === 301) {
                const redirectUrl = response.headers.location;
                https.get(redirectUrl, (redirectResponse) => {
                    const file = fs.createWriteStream(outputPath);
                    redirectResponse.pipe(file);
                    file.on('finish', () => {
                        file.close();
                        const stats = fs.statSync(outputPath);
                        console.log(`  ✓ Downloaded: ${filename} (${(stats.size / 1024).toFixed(2)} KB)`);
                        resolve({ wellSerial, docId, docType, filename, size: stats.size });
                    });
                }).on('error', reject);
            } else {
                const file = fs.createWriteStream(outputPath);
                response.pipe(file);
                file.on('finish', () => {
                    file.close();
                    const stats = fs.statSync(outputPath);
                    console.log(`  ✓ Downloaded: ${filename} (${(stats.size / 1024).toFixed(2)} KB)`);
                    resolve({ wellSerial, docId, docType, filename, size: stats.size });
                });
            }
        }).on('error', reject);
    });
}

async function processWells() {
    console.log('Fetching unit orders for 10 Haynesville Shale wells...\n');
    
    const results = {
        wells: [],
        totalDocuments: 0,
        successful: 0,
        failed: 0
    };
    
    for (let i = 0; i < wellsData.length && i < 10; i++) {
        const well = wellsData[i];
        console.log(`\n=== Well ${i + 1}/10: ${well.WELL_NAME} (Serial: ${well.WELL_SERIA}) ===`);
        console.log(`API: ${well.API_NUM}`);
        console.log(`Fetching documents from: ${well.DOC_ACCESS}`);
        
        try {
            const html = await fetchUrl(well.DOC_ACCESS);
            const documents = parseDocuments(html);
            
            console.log(`Found ${documents.length} unit-related documents`);
            
            const wellResult = {
                wellSerial: well.WELL_SERIA,
                wellName: well.WELL_NAME,
                apiNum: well.API_NUM,
                documents: []
            };
            
            if (documents.length > 0) {
                // Download up to 3 documents per well to avoid overwhelming
                const docsToDownload = documents.slice(0, 3);
                
                for (const doc of docsToDownload) {
                    try {
                        const downloadResult = await downloadDocument(
                            doc.docId,
                            well.WELL_SERIA,
                            doc.docType,
                            i
                        );
                        wellResult.documents.push(downloadResult);
                        results.successful++;
                        results.totalDocuments++;
                        
                        // Small delay
                        await new Promise(resolve => setTimeout(resolve, 500));
                    } catch (error) {
                        console.error(`  ✗ Failed to download ${doc.docId}: ${error.message}`);
                        results.failed++;
                    }
                }
            } else {
                console.log('  No unit orders found for this well');
            }
            
            results.wells.push(wellResult);
            
        } catch (error) {
            console.error(`Error processing well ${well.WELL_SERIA}: ${error.message}`);
        }
        
        // Delay between wells
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    console.log('\n\n=== Summary ===');
    console.log(`Wells processed: ${results.wells.length}`);
    console.log(`Total unit documents found: ${results.totalDocuments}`);
    console.log(`Successfully downloaded: ${results.successful}`);
    console.log(`Failed: ${results.failed}`);
    
    // Save detailed results
    fs.writeFileSync(
        path.join(outputDir, 'well_documents_summary.json'),
        JSON.stringify(results, null, 2)
    );
    
    console.log(`\nResults saved to: ${path.join(outputDir, 'well_documents_summary.json')}`);
}

processWells().catch(console.error);
