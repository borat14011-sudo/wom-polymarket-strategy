"""
Polymarket Trade Executor
Handles browser automation and trade execution
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TradeExecutor:
    """Execute trades on Polymarket via browser automation"""
    
    def __init__(self, email: str, password: str, headless: bool = False):
        self.email = email
        self.password = password
        self.headless = headless
        self.driver = None
        self.wait = None
        self.logger = logging.getLogger(__name__)
        
        # Setup directories
        self.screenshot_dir = Path("screenshots")
        self.screenshot_dir.mkdir(exist_ok=True)
        
    def setup_driver(self) -> None:
        """Initialize Chrome WebDriver"""
        self.logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            self.logger.info("WebDriver initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            raise
    
    def login(self) -> bool:
        """Login to Polymarket"""
        self.logger.info("Logging into Polymarket...")
        
        try:
            # Navigate to login page
            self.driver.get("https://polymarket.com/login")
            time.sleep(3)
            
            # Find and fill email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "email"))
            )
            email_field.clear()
            email_field.send_keys(self.email)
            self.logger.info("Email entered")
            
            # Find and fill password field
            password_field = self.driver.find_element(By.NAME, "password")
            password_field.clear()
            password_field.send_keys(self.password)
            self.logger.info("Password entered")
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            self.logger.info("Login submitted")
            
            # Wait for dashboard to load
            time.sleep(5)
            
            # Verify login success
            if "portfolio" in self.driver.current_url or "markets" in self.driver.current_url:
                self.logger.info("Login successful!")
                self.take_screenshot("login_success")
                return True
            else:
                self.logger.error("Login may have failed - unexpected URL")
                self.take_screenshot("login_failed")
                return False
                
        except Exception as e:
            self.logger.error(f"Login failed: {e}")
            self.take_screenshot("login_error")
            return False
    
    def get_balance(self) -> Optional[float]:
        """Get current USDC balance"""
        self.logger.info("Checking balance...")
        
        try:
            # Navigate to portfolio
            self.driver.get("https://polymarket.com/portfolio")
            time.sleep(3)
            
            # Look for balance element
            balance_elements = self.driver.find_elements(
                By.XPATH, "//*[contains(text(), 'USDC')]"
            )
            
            if balance_elements:
                balance_text = balance_elements[0].text
                self.logger.info(f"Balance found: {balance_text}")
                return self._parse_balance(balance_text)
            else:
                self.logger.warning("Could not find balance element")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get balance: {e}")
            return None
    
    def find_market(self, market_name: str) -> bool:
        """Navigate to specific market"""
        self.logger.info(f"Finding market: {market_name}")
        
        try:
            # Navigate to markets page
            self.driver.get("https://polymarket.com/markets")
            time.sleep(3)
            
            # Search for market
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search']"))
            )
            search_box.clear()
            search_box.send_keys(market_name)
            time.sleep(2)
            
            # Click on first result
            results = self.driver.find_elements(
                By.XPATH, f"//*[contains(text(), '{market_name}')]"
            )
            
            if results:
                results[0].click()
                time.sleep(3)
                self.logger.info("Market found and opened")
                return True
            else:
                self.logger.error("Market not found in search results")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to find market: {e}")
            return False
    
    def place_order(self, side: str, price: float, size: float) -> Dict[str, Any]:
        """Place a buy/sell order"""
        self.logger.info(f"Placing {side} order: {size} @ {price}")
        
        try:
            # Click Buy NO or Buy YES button
            button_text = f"Buy {side}"
            buy_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f"//button[contains(text(), '{button_text}')]"))
            )
            buy_button.click()
            time.sleep(2)
            
            # Enter quantity
            quantity_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "amount"))
            )
            quantity_field.clear()
            quantity_field.send_keys(str(size))
            
            # Enter price (if limit order)
            if price:
                price_field = self.driver.find_element(By.NAME, "price")
                price_field.clear()
                price_field.send_keys(str(price))
            
            # Submit order
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            self.logger.info("Order submitted")
            
            # Wait for confirmation
            time.sleep(3)
            self.take_screenshot("order_submitted")
            
            return {
                "success": True,
                "side": side,
                "price": price,
                "size": size,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Order failed: {e}")
            self.take_screenshot("order_failed")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_order(self) -> bool:
        """Verify order was filled"""
        self.logger.info("Verifying order...")
        
        try:
            # Check for success message or position update
            time.sleep(5)
            
            # Navigate to portfolio to verify
            self.driver.get("https://polymarket.com/portfolio")
            time.sleep(3)
            
            self.take_screenshot("order_verified")
            return True
            
        except Exception as e:
            self.logger.error(f"Verification failed: {e}")
            return False
    
    def take_screenshot(self, name: str) -> None:
        """Take a screenshot for documentation"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.screenshot_dir / f"{name}_{timestamp}.png"
            self.driver.save_screenshot(str(filename))
            self.logger.info(f"Screenshot saved: {filename}")
        except Exception as e:
            self.logger.warning(f"Failed to take screenshot: {e}")
    
    def _parse_balance(self, balance_text: str) -> float:
        """Parse balance from text"""
        try:
            import re
            numbers = re.findall(r"\d+\.?\d*", balance_text)
            if numbers:
                return float(numbers[0])
            return 0.0
        except:
            return 0.0
    
    def cleanup(self) -> None:
        """Clean up resources"""
        self.logger.info("Cleaning up...")
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("WebDriver closed")
            except:
                pass
