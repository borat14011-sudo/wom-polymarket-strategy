#!/usr/bin/env python3
"""
Browser Automation Trade Execution
Uses Selenium to execute trade on Polymarket website
"""

import time
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Credentials
EMAIL = "Borat14011@gmail.com"
PASSWORD = "Montenegro@"
MARKET_URL = "https://polymarket.com/event/microstrategy-500k-btc-dec-31"
TRADE_AMOUNT = "8.00"

print("=" * 60)
print("BROWSER AUTOMATION TRADE EXECUTION")
print("=" * 60)

def execute_trade():
    # Setup Chrome
    print("\n[1/7] Opening Chrome...")
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # Uncomment to run headless:
    # chrome_options.add_argument("--headless")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    wait = WebDriverWait(driver, 20)
    
    try:
        # Step 1: Navigate to market
        print("[2/7] Navigating to MSTR market...")
        driver.get(MARKET_URL)
        time.sleep(3)
        
        # Step 2: Login
        print("[3/7] Logging in...")
        
        # Click login button
        login_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]"))
        )
        login_btn.click()
        time.sleep(2)
        
        # Enter email
        email_field = wait.until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
        email_field.clear()
        email_field.send_keys(EMAIL)
        
        # Enter password
        password_field = driver.find_element(By.NAME, "password")
        password_field.clear()
        password_field.send_keys(PASSWORD)
        
        # Click login
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(5)
        
        print("[4/7] Logged in successfully!")
        
        # Step 3: Click BUY NO
        print("[5/7] Clicking BUY NO...")
        buy_no_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Buy No')]"))
        )
        buy_no_btn.click()
        time.sleep(2)
        
        # Step 4: Enter amount
        print("[6/7] Entering trade amount...")
        amount_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='0.00' or contains(@name, 'amount')]"))
        )
        amount_field.clear()
        amount_field.send_keys(TRADE_AMOUNT)
        time.sleep(1)
        
        # Step 5: Confirm order
        print("[7/7] Confirming order...")
        confirm_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Confirm') or contains(text(), 'Place Order')]"))
        )
        confirm_btn.click()
        time.sleep(5)
        
        print("\n" + "=" * 60)
        print("TRADE EXECUTED!")
        print("=" * 60)
        print("\nTaking screenshot...")
        driver.save_screenshot("trade_confirmation.png")
        print("Screenshot saved: trade_confirmation.png")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        driver.save_screenshot("error_screenshot.png")
        print("Error screenshot saved: error_screenshot.png")
        input("\nPress Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    execute_trade()
