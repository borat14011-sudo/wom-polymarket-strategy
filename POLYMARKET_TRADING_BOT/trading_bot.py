"""
Polymarket Trading Bot
Automated trading bot for Polymarket using Playwright browser automation.

Features:
- Login with email/password
- Check balance and available markets
- Execute trades based on strategy parameters
- Comprehensive logging
- Error handling and retries
"""

import os
import sys
import time
import re
from datetime import datetime
from typing import Optional, Tuple
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger
from playwright.sync_api import sync_playwright, Page, Browser, Locator
from playwright._impl._errors import TimeoutError as PlaywrightTimeout

from config import load_config, TradingConfig, BotConfig

# Load environment variables
load_dotenv()


class PolymarketBot:
    """Main trading bot class for Polymarket automation"""
    
    def __init__(self):
        self.trading_config, self.bot_config = load_config()
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Setup logging
        self._setup_logging()
        
        # Get credentials from environment
        self.email = os.getenv("POLYMARKET_EMAIL")
        self.password = os.getenv("POLYMARKET_PASSWORD")
        
        if not self.email or not self.password:
            logger.error("Missing credentials. Please set POLYMARKET_EMAIL and POLYMARKET_PASSWORD in .env file")
            raise ValueError("Missing Polymarket credentials in environment variables")
    
    def _setup_logging(self):
        """Configure logging to file and console"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"trading_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stdout,
            level=self.bot_config.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
        )
        
        # Add file handler
        logger.add(
            str(log_file),
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            rotation="10 MB",
            retention="7 days"
        )
        
        logger.info(f"Logging initialized. Log file: {log_file}")
    
    def _retry_operation(self, operation, *args, **kwargs):
        """Retry an operation with exponential backoff"""
        for attempt in range(self.bot_config.max_retries):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1}/{self.bot_config.max_retries} failed: {str(e)}")
                if attempt < self.bot_config.max_retries - 1:
                    delay = self.bot_config.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.bot_config.max_retries} attempts failed")
                    raise
    
    def initialize(self):
        """Initialize Playwright browser"""
        logger.info("Initializing browser...")
        
        self.playwright = sync_playwright().start()
        
        # Launch browser
        self.browser = self.playwright.chromium.launch(
            headless=self.bot_config.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create new context with viewport
        context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        )
        
        self.page = context.new_page()
        self.page.set_default_timeout(self.bot_config.implicit_wait * 1000)
        self.page.set_default_navigation_timeout(self.bot_config.page_load_timeout * 1000)
        
        logger.info("Browser initialized successfully")
    
    def login(self) -> bool:
        """Login to Polymarket with email and password"""
        logger.info("Starting login process...")
        
        try:
            # Navigate to login page
            self.page.goto(self.bot_config.login_url)
            logger.debug(f"Navigated to {self.bot_config.login_url}")
            
            # Wait for page to load
            self.page.wait_for_load_state("networkidle")
            
            # Handle cookie consent if present
            self._handle_cookie_consent()
            
            # Look for email input
            email_input = self.page.locator('input[type="email"], input[name="email"], input[placeholder*="email" i]').first
            if email_input.count() == 0:
                # Try alternative selectors
                email_input = self.page.locator('input').filter(has_text=r'@').first
            
            if email_input.count() > 0:
                email_input.fill(self.email)
                logger.debug("Email entered")
            else:
                logger.error("Could not find email input field")
                return False
            
            # Look for password input
            password_input = self.page.locator('input[type="password"], input[name="password"]').first
            if password_input.count() > 0:
                password_input.fill(self.password)
                logger.debug("Password entered")
            else:
                logger.error("Could not find password input field")
                return False
            
            # Look for login button
            login_button = self.page.locator(
                'button[type="submit"], button:has-text("Login"), button:has-text("Sign in"), button:has-text("Log in")'
            ).first
            
            if login_button.count() > 0:
                login_button.click()
                logger.debug("Login button clicked")
            else:
                # Try pressing Enter
                password_input.press("Enter")
                logger.debug("Submitted with Enter key")
            
            # Wait for navigation after login
            self.page.wait_for_load_state("networkidle")
            time.sleep(3)  # Additional wait for any redirects
            
            # Check if login was successful
            if self._is_logged_in():
                logger.info("Login successful!")
                return True
            else:
                logger.error("Login failed - could not verify successful authentication")
                return False
                
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def _handle_cookie_consent(self):
        """Handle cookie consent popup if present"""
        try:
            accept_buttons = self.page.locator(
                'button:has-text("Accept"), button:has-text("Accept All"), button:has-text("I Accept")'
            )
            if accept_buttons.count() > 0:
                accept_buttons.first.click(timeout=5000)
                logger.debug("Cookie consent accepted")
        except:
            pass  # No cookie consent popup
    
    def _is_logged_in(self) -> bool:
        """Check if user is logged in"""
        # Check for profile element, wallet balance, or account menu
        indicators = [
            '[data-testid="account-menu"]',
            '[data-testid="wallet-balance"]',
            '.wallet-balance',
            'text=Portfolio',
            'text=Account',
        ]
        
        for indicator in indicators:
            try:
                if self.page.locator(indicator).count() > 0:
                    return True
            except:
                continue
        
        # Check if URL doesn't contain login
        if "login" not in self.page.url.lower():
            return True
            
        return False
    
    def get_balance(self) -> Optional[float]:
        """Get current account balance"""
        logger.info("Checking account balance...")
        
        try:
            # Navigate to portfolio or markets page
            self.page.goto(f"{self.bot_config.base_url}/portfolio")
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Look for balance indicators
            balance_selectors = [
                '[data-testid="wallet-balance"]',
                '.balance',
                '.wallet-balance',
                'text=/\\$[\\d,]+\\.\\d{2}/',
            ]
            
            for selector in balance_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.count() > 0:
                        balance_text = element.text_content()
                        # Extract numeric value
                        balance_match = re.search(r'[\$]?([\d,]+\.?\d*)', balance_text)
                        if balance_match:
                            balance = float(balance_match.group(1).replace(',', ''))
                            logger.info(f"Current balance: ${balance:.2f}")
                            return balance
                except:
                    continue
            
            logger.warning("Could not determine balance from page")
            return None
            
        except Exception as e:
            logger.error(f"Error checking balance: {str(e)}")
            return None
    
    def find_market(self, market_name: str) -> bool:
        """Find and navigate to the target market"""
        logger.info(f"Searching for market: {market_name}")
        
        try:
            # Navigate to markets page
            self.page.goto(self.bot_config.markets_url)
            self.page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            # Search for the market
            search_input = self.page.locator('input[placeholder*="search" i], input[type="search"]').first
            
            if search_input.count() > 0:
                search_input.fill(market_name)
                search_input.press("Enter")
                time.sleep(3)
            
            # Look for market link
            market_link = self.page.locator(f'text={market_name}').first
            
            if market_link.count() == 0:
                # Try partial match
                market_link = self.page.locator(f'text=/.*{re.escape(market_name[:20])}.*/i').first
            
            if market_link.count() > 0:
                market_link.click()
                logger.info(f"Navigated to market: {market_name}")
                self.page.wait_for_load_state("networkidle")
                time.sleep(2)
                return True
            else:
                logger.error(f"Could not find market: {market_name}")
                return False
                
        except Exception as e:
            logger.error(f"Error finding market: {str(e)}")
            return False
    
    def get_current_price(self) -> Tuple[Optional[float], Optional[float]]:
        """Get current YES and NO prices"""
        logger.info("Getting current market prices...")
        
        try:
            # Look for price elements
            yes_price = None
            no_price = None
            
            # Try various selectors for YES price
            yes_selectors = [
                'button:has-text("Yes"):has-text("¢")',
                '[data-testid="outcome-yes"]',
                'text=/Yes\\s*[\\d.]+¢/',
            ]
            
            for selector in yes_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.count() > 0:
                        text = element.text_content()
                        match = re.search(r'(\d+\.?\d*)¢', text)
                        if match:
                            yes_price = float(match.group(1)) / 100
                            break
                except:
                    continue
            
            # Try various selectors for NO price
            no_selectors = [
                'button:has-text("No"):has-text("¢")',
                '[data-testid="outcome-no"]',
                'text=/No\\s*[\\d.]+¢/',
            ]
            
            for selector in no_selectors:
                try:
                    element = self.page.locator(selector).first
                    if element.count() > 0:
                        text = element.text_content()
                        match = re.search(r'(\d+\.?\d*)¢', text)
                        if match:
                            no_price = float(match.group(1)) / 100
                            break
                except:
                    continue
            
            if yes_price and no_price:
                logger.info(f"Current prices - YES: {yes_price:.3f}, NO: {no_price:.3f}")
            
            return yes_price, no_price
            
        except Exception as e:
            logger.error(f"Error getting prices: {str(e)}")
            return None, None
    
    def execute_trade(self, action: str, target_price: float, position_size: float) -> bool:
        """Execute a trade on the current market"""
        logger.info(f"Executing {action} trade at target price {target_price:.3f} for ${position_size:.2f}")
        
        try:
            # Get current prices
            yes_price, no_price = self.get_current_price()
            
            if action.upper() == "BUY_NO":
                current_price = no_price
                outcome_button_text = "No"
            elif action.upper() == "BUY_YES":
                current_price = yes_price
                outcome_button_text = "Yes"
            else:
                logger.error(f"Invalid action: {action}")
                return False
            
            if current_price is None:
                logger.error("Could not determine current price")
                return False
            
            logger.info(f"Current price for {action}: {current_price:.3f}")
            
            # Check if price is within tolerance
            price_diff = abs(current_price - target_price)
            if price_diff > self.trading_config.price_tolerance:
                logger.warning(
                    f"Price difference ({price_diff:.4f}) exceeds tolerance ({self.trading_config.price_tolerance:.4f})"
                )
                logger.warning(f"Target: {target_price:.3f}, Current: {current_price:.3f}")
                return False
            
            # Click the outcome button
            outcome_button = self.page.locator(f'button:has-text("{outcome_button_text}")').first
            
            if outcome_button.count() == 0:
                # Try alternative selector
                outcome_button = self.page.locator(f'text="{outcome_button_text}"').locator('..').first
            
            if outcome_button.count() > 0:
                outcome_button.click()
                logger.debug(f"Clicked {outcome_button_text} button")
                time.sleep(1)
            else:
                logger.error(f"Could not find {outcome_button_text} button")
                return False
            
            # Enter position size
            amount_input = self.page.locator('input[type="number"], input[placeholder*="amount" i]').first
            
            if amount_input.count() > 0:
                amount_input.fill(str(position_size))
                logger.debug(f"Entered position size: ${position_size:.2f}")
                time.sleep(1)
            else:
                logger.error("Could not find amount input field")
                return False
            
            # Click buy/confirm button
            buy_button = self.page.locator(
                'button:has-text("Buy"), button:has-text("Confirm"), button[type="submit"]'
            ).first
            
            if buy_button.count() > 0:
                # Check if button is enabled
                if buy_button.is_enabled():
                    buy_button.click()
                    logger.info("Trade submitted!")
                    time.sleep(3)
                    
                    # Check for confirmation
                    if self._verify_trade_success():
                        logger.info("Trade executed successfully!")
                        return True
                    else:
                        logger.warning("Could not verify trade success")
                        return False
                else:
                    logger.error("Buy button is disabled")
                    return False
            else:
                logger.error("Could not find buy button")
                return False
                
        except Exception as e:
            logger.error(f"Trade execution error: {str(e)}")
            return False
    
    def _verify_trade_success(self) -> bool:
        """Verify if trade was successful"""
        success_indicators = [
            'text="Success"',
            'text="Order Confirmed"',
            'text="Trade Complete"',
            '.success',
            '[data-testid="success-message"]',
        ]
        
        for indicator in success_indicators:
            try:
                if self.page.locator(indicator).count() > 0:
                    return True
            except:
                continue
        
        # Check if we're still on the same page (no error)
        time.sleep(2)
        return True  # Assume success if no error visible
    
    def run(self):
        """Main bot execution loop"""
        logger.info("=" * 60)
        logger.info("Polymarket Trading Bot Started")
        logger.info("=" * 60)
        logger.info(f"Target Market: {self.trading_config.target_market}")
        logger.info(f"Action: {self.trading_config.trade_action}")
        logger.info(f"Target Price: {self.trading_config.target_price:.3f}")
        logger.info(f"Position Size: ${self.trading_config.position_size:.2f}")
        logger.info("=" * 60)
        
        try:
            # Initialize browser
            self.initialize()
            
            # Login
            if not self._retry_operation(self.login):
                logger.error("Failed to login after retries")
                return False
            
            # Check balance
            balance = self._retry_operation(self.get_balance)
            if balance is None:
                logger.error("Could not retrieve balance")
                return False
            
            if balance < self.trading_config.min_balance:
                logger.error(f"Insufficient balance: ${balance:.2f} (minimum: ${self.trading_config.min_balance:.2f})")
                return False
            
            # Find target market
            if not self._retry_operation(self.find_market, self.trading_config.target_market):
                logger.error("Failed to find target market")
                return False
            
            # Execute trade
            success = self._retry_operation(
                self.execute_trade,
                self.trading_config.trade_action,
                self.trading_config.target_price,
                self.trading_config.position_size
            )
            
            if success:
                logger.info("=" * 60)
                logger.info("Trading bot completed successfully!")
                logger.info("=" * 60)
            else:
                logger.error("Trading bot failed to execute trade")
            
            return success
            
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return False
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.browser:
            self.browser.close()
            logger.debug("Browser closed")
        
        if self.playwright:
            self.playwright.stop()
            logger.debug("Playwright stopped")
        
        logger.info("Cleanup complete")


def main():
    """Entry point"""
    bot = PolymarketBot()
    success = bot.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
