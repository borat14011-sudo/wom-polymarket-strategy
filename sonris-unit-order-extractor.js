/**
 * SONRIS Unit Order PDF Extractor
 * 
 * This script automates navigation to SONRIS, searches for unit orders,
 * PAUSES for manual CAPTCHA solving, then downloads PDFs.
 * 
 * LEGAL & ETHICAL:
 * - Does NOT bypass CAPTCHAs (you solve manually)
 * - Respects rate limits
 * - Complies with SONRIS Terms of Service
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// ============================================
// CONFIGURATION
// ============================================

const CONFIG = {
  // SONRIS URLs
  BASE_URL: 'http://sonris.com',
  UNIT_ORDERS_URL: 'http://sonris.com/unit_orders.asp', // Update with actual URL
  
  // Download settings
  DOWNLOAD_DIR: path.join(__dirname, 'sonris_downloads'),
  
  // Wait times (be respectful to server)
  PAGE_LOAD_WAIT: 3000,
  BETWEEN_REQUESTS_WAIT: 2000,
  
  // Search parameters (customize these)
  SEARCH_PARAMS: {
    // Example: unit order number, operator name, etc.
    // unitOrderNumber: '12345',
    // operator: 'XYZ Oil Company',
  }
};

// ============================================
// HELPER FUNCTIONS
// ============================================

async function setupDownloadDirectory() {
  if (!fs.existsSync(CONFIG.DOWNLOAD_DIR)) {
    fs.mkdirSync(CONFIG.DOWNLOAD_DIR, { recursive: true });
    console.log(`✅ Created download directory: ${CONFIG.DOWNLOAD_DIR}`);
  }
}

async function waitForManualCaptcha(page) {
  console.log('\n⚠️  CAPTCHA DETECTED!');
  console.log('👉 Please solve the CAPTCHA manually in the browser window.');
  console.log('⏳ Script will wait... Press ENTER in terminal when done.\n');
  
  // Wait for user input
  await new Promise(resolve => {
    process.stdin.once('data', () => {
      console.log('✅ Continuing...\n');
      resolve();
    });
  });
}

async function checkForCaptcha(page) {
  // Check for common CAPTCHA indicators
  const captchaSelectors = [
    'iframe[src*="recaptcha"]',
    'iframe[src*="captcha"]',
    '#captcha',
    '.captcha',
    '[class*="captcha"]',
    '[id*="captcha"]'
  ];
  
  for (const selector of captchaSelectors) {
    const captchaExists = await page.$(selector);
    if (captchaExists) {
      return true;
    }
  }
  
  return false;
}

// ============================================
// MAIN EXTRACTION FUNCTIONS
// ============================================

async function navigateToUnitOrders(page) {
  console.log('🌐 Navigating to SONRIS Unit Orders...');
  
  await page.goto(CONFIG.UNIT_ORDERS_URL, {
    waitUntil: 'networkidle2',
    timeout: 30000
  });
  
  await page.waitForTimeout(CONFIG.PAGE_LOAD_WAIT);
  
  // Check for CAPTCHA immediately after navigation
  if (await checkForCaptcha(page)) {
    await waitForManualCaptcha(page);
  }
  
  console.log('✅ Page loaded');
}

async function performSearch(page, searchParams) {
  console.log('🔍 Performing search...');
  
  // TODO: Update these selectors based on actual SONRIS form
  // Example for a unit order number search:
  
  // Fill search form
  if (searchParams.unitOrderNumber) {
    await page.type('#unit_order_number', searchParams.unitOrderNumber);
  }
  
  if (searchParams.operator) {
    await page.type('#operator_name', searchParams.operator);
  }
  
  // Submit search
  await page.click('#search_button'); // Update selector
  
  await page.waitForNavigation({ waitUntil: 'networkidle2' });
  await page.waitForTimeout(CONFIG.BETWEEN_REQUESTS_WAIT);
  
  // Check for CAPTCHA after search
  if (await checkForCaptcha(page)) {
    await waitForManualCaptcha(page);
  }
  
  console.log('✅ Search completed');
}

async function extractUnitOrderLinks(page) {
  console.log('📋 Extracting unit order PDF links...');
  
  // Get all PDF links from results
  const pdfLinks = await page.evaluate(() => {
    const links = Array.from(document.querySelectorAll('a[href*=".pdf"]'));
    return links.map(link => ({
      url: link.href,
      text: link.textContent.trim()
    }));
  });
  
  console.log(`✅ Found ${pdfLinks.length} PDF(s)`);
  return pdfLinks;
}

async function downloadPDF(page, pdfUrl, filename) {
  console.log(`⬇️  Downloading: ${filename}...`);
  
  // Navigate to PDF
  const response = await page.goto(pdfUrl, {
    waitUntil: 'networkidle2'
  });
  
  // Get PDF buffer
  const buffer = await response.buffer();
  
  // Save to file
  const filepath = path.join(CONFIG.DOWNLOAD_DIR, filename);
  fs.writeFileSync(filepath, buffer);
  
  console.log(`✅ Saved: ${filepath}`);
  
  // Wait between downloads (be nice to server)
  await page.waitForTimeout(CONFIG.BETWEEN_REQUESTS_WAIT);
}

async function downloadAllPDFs(page, pdfLinks) {
  console.log(`\n📥 Downloading ${pdfLinks.length} PDFs...`);
  
  for (let i = 0; i < pdfLinks.length; i++) {
    const link = pdfLinks[i];
    const filename = `unit_order_${i + 1}_${Date.now()}.pdf`;
    
    try {
      await downloadPDF(page, link.url, filename);
    } catch (error) {
      console.error(`❌ Failed to download ${link.url}:`, error.message);
    }
  }
  
  console.log('\n✅ All downloads completed!');
}

// ============================================
// MAIN FUNCTION
// ============================================

async function main() {
  console.log('🚀 SONRIS Unit Order PDF Extractor\n');
  
  // Setup
  await setupDownloadDirectory();
  
  // Launch browser
  console.log('🌐 Launching browser...');
  const browser = await puppeteer.launch({
    headless: false, // Show browser so user can solve CAPTCHA
    defaultViewport: null,
    args: ['--start-maximized']
  });
  
  const page = await browser.newPage();
  
  try {
    // Navigate to SONRIS
    await navigateToUnitOrders(page);
    
    // Perform search
    await performSearch(page, CONFIG.SEARCH_PARAMS);
    
    // Extract PDF links
    const pdfLinks = await extractUnitOrderLinks(page);
    
    if (pdfLinks.length === 0) {
      console.log('⚠️  No PDFs found. Check search parameters.');
      return;
    }
    
    // Download all PDFs
    await downloadAllPDFs(page, pdfLinks);
    
    console.log('\n🎉 Extraction complete!');
    console.log(`📁 Files saved to: ${CONFIG.DOWNLOAD_DIR}`);
    
  } catch (error) {
    console.error('\n❌ Error:', error.message);
    console.error('Stack:', error.stack);
  } finally {
    // await browser.close();
    console.log('\n⏸️  Browser left open. Close manually when done.');
  }
}

// ============================================
// RUN
// ============================================

if (require.main === module) {
  main().catch(console.error);
}

module.exports = { main, CONFIG };
