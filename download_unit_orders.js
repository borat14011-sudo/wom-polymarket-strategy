const https = require('https');
const fs = require('fs');
const path = require('path');

// First 10 unit agreement document IDs from the SONRIS search
const docIds = [
    '23133297',
    '23065015',
    '23065014',
    '15327598',
    '15327590',
    '15327589',
    '15134150',
    '15134149',
    '15076243',
    '15076241'
];

const outputDir = 'C:\\Users\\Borat\\.openclaw\\workspace\\sonris_unit_orders';

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
}

function downloadDocument(docId, index) {
    return new Promise((resolve, reject) => {
        const url = `https://sonlite.dnr.state.la.us/dnrservices/redirectUrl.jsp?dDocname=${docId}&showInline=True&nativeFile=True`;
        const outputPath = path.join(outputDir, `unit_order_${docId}.pdf`);
        
        console.log(`\nDownloading document ${index + 1}/10 (ID: ${docId})...`);
        console.log(`URL: ${url}`);
        
        https.get(url, (response) => {
            // Handle redirects
            if (response.statusCode === 302 || response.statusCode === 301) {
                const redirectUrl = response.headers.location;
                console.log(`Following redirect to: ${redirectUrl}`);
                
                https.get(redirectUrl, (redirectResponse) => {
                    const file = fs.createWriteStream(outputPath);
                    redirectResponse.pipe(file);
                    
                    file.on('finish', () => {
                        file.close();
                        const stats = fs.statSync(outputPath);
                        console.log(`✓ Downloaded: ${path.basename(outputPath)} (${(stats.size / 1024).toFixed(2)} KB)`);
                        resolve(docId);
                    });
                }).on('error', (err) => {
                    fs.unlink(outputPath, () => {}); // Delete incomplete file
                    console.error(`✗ Error downloading ${docId}:`, err.message);
                    reject(err);
                });
            } else {
                const file = fs.createWriteStream(outputPath);
                response.pipe(file);
                
                file.on('finish', () => {
                    file.close();
                    const stats = fs.statSync(outputPath);
                    console.log(`✓ Downloaded: ${path.basename(outputPath)} (${(stats.size / 1024).toFixed(2)} KB)`);
                    resolve(docId);
                });
            }
        }).on('error', (err) => {
            fs.unlink(outputPath, () => {}); // Delete incomplete file
            console.error(`✗ Error downloading ${docId}:`, err.message);
            reject(err);
        });
    });
}

async function downloadAll() {
    console.log('Starting download of 10 SONRIS unit orders...\n');
    
    const results = {
        successful: [],
        failed: []
    };
    
    for (let i = 0; i < docIds.length; i++) {
        try {
            await downloadDocument(docIds[i], i);
            results.successful.push(docIds[i]);
            // Small delay to avoid overwhelming the server
            await new Promise(resolve => setTimeout(resolve, 500));
        } catch (error) {
            results.failed.push({ docId: docIds[i], error: error.message });
        }
    }
    
    console.log('\n\n=== Download Summary ===');
    console.log(`Successfully downloaded: ${results.successful.length}/10`);
    if (results.failed.length > 0) {
        console.log(`Failed: ${results.failed.length}`);
        results.failed.forEach(f => console.log(`  - ${f.docId}: ${f.error}`));
    }
    console.log(`\nAll files saved to: ${outputDir}`);
    
    // Save summary
    fs.writeFileSync(
        path.join(outputDir, 'download_summary.json'),
        JSON.stringify(results, null, 2)
    );
}

downloadAll().catch(console.error);
