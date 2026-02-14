#!/usr/bin/env python3
"""
Browser Automation Backup for Polymarket Trading
Uses Selenium as fallback when API fails
"""

import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Load credentials
load_dotenv('POLYMARKET_TRADING_BOT/.env.api')

EMAIL = os.getenv('POLYMARKET_EMAIL')
PASSWORD = os.getenv('POLYMARKET_PASSWORD')

class PolymarketBrowserTrader:
    """
    Browser-based trader as backup for API failures
    """
    
    def __init__(self, headless=False):
        """
        Initialize browser driver
        """
        self.headless = headless
        self.driver = None
        self.logged_in = False
        
    def setup_driver(self):
        """
        Setup Chrome driver with options
        """
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        # Add arguments to avoid detection
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Execute CDP commands to avoid detection
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def login(self):
        """
        Login to Polymarket
        """
        if not EMAIL or not PASSWORD:
            print("ERROR: Email or password not set in .env.api")
            print("Add these lines to .env.api:")
            print('POLYMARKET_EMAIL="your_email@example.com"')
            print('POLYMARKET_PASSWORD="your_password"')
            return False
        
        print("Navigating to Polymarket login...")
        self.driver.get("https://polymarket.com/login")
        
        try:
            # Wait for login page to load
            wait = WebDriverWait(self.driver, 10)
            
            # Enter email
            email_field = wait.until(EC.presence_of_element_located((By.NAME, "email")))
            email_field.send_keys(EMAIL)
            
            # Enter password
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.send_keys(PASSWORD)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login successful
            if "portfolio" in self.driver.current_url.lower() or "account" in self.driver.current_url.lower():
                print("Login successful!")
                self.logged_in = True
                return True
            else:
                print("Login may have failed")
                return False
                
        except TimeoutException:
            print("Timeout waiting for login page")
            return False
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def navigate_to_market(self, market_slug):
        """
        Navigate to specific market
        """
        url = f"https://polymarket.com/event/{market_slug}"
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(3)
        
        # Check if market loaded
        return "event" in self.driver.current_url
    
    def place_trade(self, position="NO", amount_usd=0.20):
        """
        Place a trade via browser interface
        """
        if not self.logged_in:
            print("Not logged in. Please login first.")
            return False
        
        try:
            wait = WebDriverWait(self.driver, 10)
            
            # Select position (YES or NO)
            if position.upper() == "NO":
                # Click NO button
                no_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'NO') or contains(@class, 'no-button')]")
                ))
                no_button.click()
            else:
                # Click YES button
                yes_button = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'YES') or contains(@class, 'yes-button')]")
                ))
                yes_button.click()
            
            time.sleep(1)
            
            # Enter amount
            amount_field = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@placeholder='Amount' or contains(@class, 'amount-input')]")
            ))
            amount_field.clear()
            amount_field.send_keys(str(amount_usd))
            
            time.sleep(1)
            
            # Click buy button
            buy_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), 'Buy') or contains(text(), 'Place Order')]")
            ))
            buy_button.click()
            
            print(f"Trade placed: {position} ${amount_usd}")
            
            # Wait for confirmation
            time.sleep(3)
            
            # Check for success message
            success_indicators = [
                "order placed", "success", "confirmed", "transaction"
            ]
            
            page_text = self.driver.page_source.lower()
            if any(indicator in page_text for indicator in success_indicators):
                print("Trade appears successful!")
                return True
            else:
                print("Trade may not have completed")
                return False
                
        except Exception as e:
            print(f"Trade placement error: {e}")
            return False
    
    def close(self):
        """
        Close browser
        """
        if self.driver:
            self.driver.quit()
            print("Browser closed")

def main():
    """
    Example usage
    """
    print("=" * 60)
    print("BROWSER AUTOMATION BACKUP FOR POLYMARKET")
    print("=" * 60)
    
    print("\nThis is a backup solution when API fails.")
    print("Requires:")
    print("1. Chrome browser installed")
    print("2. ChromeDriver matching your Chrome version")
    print("3. Email/password in .env.api")
    
    print("\nExample .env.api additions:")
    print('POLYMARKET_EMAIL="Borat14011@gmail.com"')
    print('POLYMARKET_PASSWORD="Montenegro@"')
    
    print("\nTo use:")
    print("1. Install: pip install selenium webdriver-manager")
    print("2. Add credentials to .env.api")
    print("3. Run: python browser_trade_backup.py")
    
    print("\n" + "=" * 60)
    print("RECOMMENDED: Use manual trading for now")
    print("Browser automation is complex and may break")
    print("=" * 60)

if __name__ == "__main__":
    main()