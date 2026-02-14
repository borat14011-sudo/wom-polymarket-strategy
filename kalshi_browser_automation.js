// Kalshi Browser Automation Fallback Script
// This script automates Kalshi trading via browser when API fails
// Usage: Run with browser automation tools (Playwright/Puppeteer)

const config = {
    // Kalshi credentials (to be filled by user)
    username: process.env.KALSHI_USERNAME || 'YOUR_USERNAME',
    password: process.env.KALSHI_PASSWORD || 'YOUR_PASSWORD',
    
    // Trading parameters
    maxMarkets: 3,
    tradeAmountMin: 1, // $1
    tradeAmountMax: 2, // $2
    screenshotPath: './kalshi_screenshots',
    
    // Timeouts
    navigationTimeout: 30000,
    loginTimeout: 15000,
    tradeTimeout: 20000,
    
    // Selectors (may need updating if Kalshi changes UI)
    selectors: {
        loginButton: 'button:has-text("Log in")',
        usernameInput: 'input[name="email"], input[name="username"], input[type="email"]',
        passwordInput: 'input[name="password"], input[type="password"]',
        submitButton: 'button[type="submit"]:has-text("Log in"), button:has-text("Sign in")',
        
        // Market selectors
        marketCard: '[data-testid="market-card"], .market-card, .market-item',
        marketTitle: '.market-title, .market-name, h3, h4',
        marketYesButton: 'button:has-text("Yes"), button:has-text("Buy Yes")',
        marketNoButton: 'button:has-text("No"), button:has-text("Buy No")',
        
        // Trade modal
        tradeAmountInput: 'input[name="amount"], input[type="number"], .amount-input',
        tradeSubmitButton: 'button:has-text("Place Trade"), button:has-text("Submit"), button[type="submit"]',
        tradeConfirmation: '.confirmation, .success-message, .trade-confirmed',
        
        // Navigation
        marketsTab: 'a[href*="/markets"], button:has-text("Markets")',
        portfolioTab: 'a[href*="/portfolio"], button:has-text("Portfolio")'
    }
};

class KalshiBrowserAutomation {
    constructor(page) {
        this.page = page;
        this.tradesExecuted = [];
        this.screenshots = [];
    }

    async setup() {
        console.log('Setting up browser automation...');
        await this.page.setViewportSize({ width: 1280, height: 800 });
        await this.page.setDefaultTimeout(config.navigationTimeout);
    }

    async navigateToKalshi() {
        console.log('Navigating to kalshi.com...');
        await this.page.goto('https://kalshi.com', { waitUntil: 'networkidle' });
        await this.page.waitForTimeout(2000);
        
        // Take screenshot
        const screenshot = await this.page.screenshot({ path: `${config.screenshotPath}/01_kalshi_home.png` });
        this.screenshots.push('01_kalshi_home.png');
        
        console.log('✓ Navigated to kalshi.com');
        return true;
    }

    async login() {
        console.log('Attempting login...');
        
        // Click login button if visible
        try {
            await this.page.click(config.selectors.loginButton);
            await this.page.waitForTimeout(1000);
        } catch (e) {
            console.log('Login button not found or already on login page');
        }
        
        // Fill credentials
        await this.page.fill(config.selectors.usernameInput, config.username);
        await this.page.fill(config.selectors.passwordInput, config.password);
        
        // Take screenshot before submitting
        await this.page.screenshot({ path: `${config.screenshotPath}/02_login_form.png` });
        this.screenshots.push('02_login_form.png');
        
        // Submit
        await this.page.click(config.selectors.submitButton);
        await this.page.waitForTimeout(3000);
        
        // Check for successful login (look for portfolio or markets tab)
        try {
            await this.page.waitForSelector(config.selectors.marketsTab, { timeout: config.loginTimeout });
            console.log('✓ Login successful');
            
            await this.page.screenshot({ path: `${config.screenshotPath}/03_logged_in.png` });
            this.screenshots.push('03_logged_in.png');
            return true;
        } catch (e) {
            console.log('✗ Login may have failed');
            await this.page.screenshot({ path: `${config.screenshotPath}/03_login_failed.png` });
            this.screenshots.push('03_login_failed.png');
            return false;
        }
    }

    async findTopMarkets() {
        console.log('Finding top markets...');
        
        // Navigate to markets if not already there
        try {
            await this.page.click(config.selectors.marketsTab);
            await this.page.waitForTimeout(2000);
        } catch (e) {
            console.log('Already on markets page or tab not found');
        }
        
        // Wait for markets to load
        await this.page.waitForSelector(config.selectors.marketCard, { timeout: 10000 });
        
        // Get market elements
        const marketElements = await this.page.$$(config.selectors.marketCard);
        console.log(`Found ${marketElements.length} markets`);
        
        // Take screenshot
        await this.page.screenshot({ path: `${config.screenshotPath}/04_markets_page.png` });
        this.screenshots.push('04_markets_page.png');
        
        // Extract top N markets
        const topMarkets = [];
        const limit = Math.min(marketElements.length, config.maxMarkets);
        
        for (let i = 0; i < limit; i++) {
            try {
                const market = marketElements[i];
                const title = await market.$eval(config.selectors.marketTitle, el => el.textContent.trim());
                const marketId = await market.getAttribute('data-market-id') || `market-${i}`;
                
                topMarkets.push({
                    element: market,
                    title: title,
                    id: marketId,
                    index: i
                });
                
                console.log(`  ${i+1}. ${title}`);
            } catch (e) {
                console.log(`  Could not extract market ${i}: ${e.message}`);
            }
        }
        
        return topMarkets;
    }

    async executeTrade(market, tradeType = 'yes') {
        console.log(`Executing ${tradeType.toUpperCase()} trade for: ${market.title}`);
        
        try {
            // Click on the market to open detail
            await market.element.click();
            await this.page.waitForTimeout(1500);
            
            // Take screenshot of market detail
            await this.page.screenshot({ path: `${config.screenshotPath}/05_market_${market.index}_detail.png` });
            this.screenshots.push(`05_market_${market.index}_detail.png`);
            
            // Click Yes or No button
            const buttonSelector = tradeType === 'yes' ? 
                config.selectors.marketYesButton : config.selectors.marketNoButton;
            
            await this.page.click(buttonSelector);
            await this.page.waitForTimeout(1000);
            
            // Fill trade amount
            const amount = Math.random() * (config.tradeAmountMax - config.tradeAmountMin) + config.tradeAmountMin;
            const roundedAmount = Math.round(amount * 100) / 100; // Round to 2 decimals
            
            await this.page.fill(config.selectors.tradeAmountInput, roundedAmount.toString());
            await this.page.waitForTimeout(500);
            
            // Take screenshot before submitting
            await this.page.screenshot({ path: `${config.screenshotPath}/06_market_${market.index}_trade_form.png` });
            this.screenshots.push(`06_market_${market.index}_trade_form.png`);
            
            // Submit trade
            await this.page.click(config.selectors.tradeSubmitButton);
            await this.page.waitForTimeout(2000);
            
            // Check for confirmation
            try {
                await this.page.waitForSelector(config.selectors.tradeConfirmation, { timeout: 5000 });
                console.log(`✓ Trade ${tradeType.toUpperCase()} executed for $${roundedAmount}`);
                
                // Take confirmation screenshot
                await this.page.screenshot({ path: `${config.screenshotPath}/07_market_${market.index}_trade_confirmed.png` });
                this.screenshots.push(`07_market_${market.index}_trade_confirmed.png`);
                
                // Record trade
                this.tradesExecuted.push({
                    market: market.title,
                    type: tradeType,
                    amount: roundedAmount,
                    timestamp: new Date().toISOString(),
                    screenshot: `07_market_${market.index}_trade_confirmed.png`
                });
                
                return { success: true, amount: roundedAmount };
            } catch (e) {
                console.log(`✗ Trade confirmation not found`);
                await this.page.screenshot({ path: `${config.screenshotPath}/07_market_${market.index}_trade_failed.png` });
                this.screenshots.push(`07_market_${market.index}_trade_failed.png`);
                return { success: false, error: 'No confirmation' };
            }
            
        } catch (e) {
            console.log(`✗ Trade execution failed: ${e.message}`);
            await this.page.screenshot({ path: `${config.screenshotPath}/error_market_${market.index}.png` });
            return { success: false, error: e.message };
        } finally {
            // Go back to markets page
            try {
                await this.page.goBack();
                await this.page.waitForTimeout(1000);
            } catch (e) {
                // Continue anyway
            }
        }
    }

    async executeAllTrades(markets) {
        console.log(`\nExecuting trades for ${markets.length} markets...`);
        
        const results = [];
        for (const market of markets) {
            // Randomly choose Yes or No for diversity
            const tradeType = Math.random() > 0.5 ? 'yes' : 'no';
            const result = await this.executeTrade(market, tradeType);
            results.push({
                market: market.title,
                ...result
            });
            
            // Small delay between trades
            await this.page.waitForTimeout(1000);
        }
        
        return results;
    }

    async capturePortfolio() {
        console.log('\nCapturing portfolio snapshot...');
        
        try {
            await this.page.click(config.selectors.portfolioTab);
            await this.page.waitForTimeout(2000);
            
            await this.page.screenshot({ path: `${config.screenshotPath}/08_portfolio.png` });
            this.screenshots.push('08_portfolio.png');
            
            console.log('✓ Portfolio captured');
            return true;
        } catch (e) {
            console.log('✗ Could not capture portfolio');
            return false;
        }
    }

    generateReport() {
        console.log('\n=== TRADING REPORT ===');
        console.log(`Total trades executed: ${this.tradesExecuted.length}`);
        
        let totalAmount = 0;
        this.tradesExecuted.forEach((trade, i) => {
            console.log(`${i+1}. ${trade.market} - ${trade.type.toUpperCase()} - $${trade.amount} - ${trade.timestamp}`);
            totalAmount += trade.amount;
        });
        
        console.log(`Total amount traded: $${totalAmount.toFixed(2)}`);
        console.log(`Screenshots taken: ${this.screenshots.length}`);
        console.log('=====================\n');
        
        return {
            totalTrades: this.tradesExecuted.length,
            totalAmount: totalAmount,
            trades: this.tradesExecuted,
            screenshots: this.screenshots
        };
    }

    async runFullWorkflow() {
        console.log('Starting Kalshi browser automation workflow...\n');
        
        try {
            // Setup
            await this.setup();
            
            // Step 1: Navigate
            await this.navigateToKalshi();
            
            // Step 2: Login
            const loggedIn = await this.login();
            if (!loggedIn) {
                throw new Error('Login failed. Check credentials.');
            }
            
            // Step 3: Find markets
            const markets = await this.findTopMarkets();
            if (markets.length === 0) {
                throw new Error('No markets found');
            }
            
            // Step 4: Execute trades
            const tradeResults = await this.executeAllTrades(markets);
            
            // Step 5: Capture portfolio
            await this.capturePortfolio();
            
            // Generate report
            const report = this.generateReport();
            
            console.log('✓ Workflow completed successfully!');
            return {
                success: true,
                report: report,
                tradeResults: tradeResults
            };
            
        } catch (error) {
            console.error(`✗ Workflow failed: ${error.message}`);
            
            // Take error screenshot
            try {
                await this.page.screenshot({ path: `${config.screenshotPath}/error_final.png` });
            } catch (e) {
                // Ignore screenshot errors
            }
            
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// Export for use in different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        KalshiBrowserAutomation,
        config
    };
}

// Simple test if run directly
if (typeof window === 'undefined' && require.main === module) {
    console.log('This script is designed to be used with a browser automation framework.');
    console.log('Example usage with Playwright:');
    console.log(`
        const { KalshiBrowserAutomation } = require('./kalshi_browser_automation.js');
        const playwright = require('playwright');
        
        async function run() {
            const browser = await playwright.chromium.launch({ headless: false });
            const page = await browser.newPage();
            
            const automation = new KalshiBrowserAutomation(page);
            await automation.runFullWorkflow();
            
            await browser.close();
        }
        
        run().catch(console.error);
    `);
}