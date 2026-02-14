#!/usr/bin/env python3
"""
COMPREHENSIVE POLYMARKET DATA VALIDATION
Cross-validates Gamma API vs CLOB API data
"""
import requests
import json
import time
from datetime import datetime, timezone

class PolymarketValidator:
    def __init__(self):
        self.validation_log = []
        self.issues_found = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.validation_log.append(log_entry)
        print(log_entry)
        
    def add_issue(self, issue_type, description, severity="WARN"):
        self.issues_found.append({
            "type": issue_type,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    def check_gamma_api(self):
        """Check Gamma API endpoint"""
        self.log("Testing Gamma API connectivity...")
        try:
            url = "https://gamma-api.polymarket.com/markets"
            params = {'limit': 5, 'closed': False}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                markets = response.json()
                self.log(f"Gamma API: Retrieved {len(markets)} markets")
                
                # Check data freshness
                if markets:
                    latest_update = max([m.get('updatedAt', '') for m in markets])
                    self.log(f"Latest Gamma update: {latest_update}")
                return markets
            else:
                self.add_issue("API_ERROR", f"Gamma API returned {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.add_issue("API_ERROR", f"Gamma API error: {e}", "ERROR")
            return None
            
    def check_clob_api(self):
        """Check CLOB API endpoint"""
        self.log("Testing CLOB API connectivity...")
        try:
            url = "https://clob.polymarket.com/markets"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # CLOB API might return different structure
                if isinstance(data, dict):
                    markets = data.get('markets', data.get('data', []))
                elif isinstance(data, list):
                    markets = data
                else:
                    markets = []
                    
                self.log(f"CLOB API: Retrieved {len(markets)} markets")
                return markets
            else:
                self.add_issue("API_ERROR", f"CLOB API returned {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.add_issue("API_ERROR", f"CLOB API error: {e}", "ERROR")
            return None
            
    def cross_validate_prices(self, gamma_markets, clob_markets):
        """Cross-validate prices between APIs"""
        self.log("Cross-validating prices between Gamma and CLOB APIs...")
        
        if not gamma_markets or not clob_markets:
            self.add_issue("VALIDATION_ERROR", "Cannot cross-validate: missing API data", "ERROR")
            return
            
        # Create lookup dictionaries
        gamma_dict = {m['id']: m for m in gamma_markets[:10] if 'id' in m}  # Check first 10
        clob_dict = {m['id']: m for m in clob_markets[:10] if 'id' in m}
        
        discrepancies = 0
        for market_id, gamma_market in gamma_dict.items():
            if market_id in clob_dict:
                clob_market = clob_dict[market_id]
                
                gamma_prices = gamma_market.get('outcomePrices', [])
                clob_prices = clob_market.get('outcomePrices', [])
                
                if len(gamma_prices) == len(clob_prices) == 2:
                    gamma_sum = float(gamma_prices[0]) + float(gamma_prices[1])
                    clob_sum = float(clob_prices[0]) + float(clob_prices[1])
                    
                    # Check if prices sum to ~1.0
                    if abs(gamma_sum - 1.0) > 0.01:
                        self.add_issue("PRICE_VALIDATION", 
                            f"Gamma prices sum to {gamma_sum:.4f} for market {market_id}", "WARN")
                        discrepancies += 1
                        
                    if abs(clob_sum - 1.0) > 0.01:
                        self.add_issue("PRICE_VALIDATION", 
                            f"CLOB prices sum to {clob_sum:.4f} for market {market_id}", "WARN")
                        discrepancies += 1
                        
                    # Check price differences between APIs
                    price_diff_0 = abs(float(gamma_prices[0]) - float(clob_prices[0]))
                    price_diff_1 = abs(float(gamma_prices[1]) - float(clob_prices[1]))
                    
                    if price_diff_0 > 0.001 or price_diff_1 > 0.001:  # 0.1% threshold
                        self.add_issue("PRICE_DISCREPANCY", 
                            f"Price mismatch for {market_id}: Gamma={gamma_prices}, CLOB={clob_prices}", "WARN")
                        discrepancies += 1
                        
        if discrepancies == 0:
            self.log("Price cross-validation: PASSED - No significant discrepancies found")
        else:
            self.log(f"Price cross-validation: FOUND {discrepancies} discrepancies")
            
    def check_local_file_freshness(self):
        """Check local active-markets.json freshness"""
        self.log("Checking local file freshness...")
        try:
            with open('active-markets.json', 'r') as f:
                data = json.load(f)
                
            fetch_time = datetime.fromisoformat(data.get('fetch_timestamp', datetime.now().isoformat()))
            now = datetime.now(timezone.utc)
            age_minutes = (now - fetch_time.replace(tzinfo=timezone.utc)).total_seconds() / 60
            
            self.log(f"Local file age: {age_minutes:.1f} minutes")
            
            if age_minutes > 30:
                self.add_issue("DATA_STALENESS", f"Local data is {age_minutes:.1f} minutes old", "ERROR")
            elif age_minutes > 15:
                self.add_issue("DATA_STALENESS", f"Local data is {age_minutes:.1f} minutes old", "WARN")
            else:
                self.log("Local file freshness: PASSED")
                
            return age_minutes
        except Exception as e:
            self.add_issue("FILE_ERROR", f"Error reading local file: {e}", "ERROR")
            return None
            
    def check_duplicate_markets(self):
        """Check for duplicate market IDs"""
        self.log("Checking for duplicate markets...")
        try:
            with open('active-markets.json', 'r') as f:
                data = json.load(f)
                
            markets = data.get('markets', [])
            ids = [m.get('id') for m in markets]
            duplicates = len(ids) - len(set(ids))
            
            if duplicates == 0:
                self.log(f"Duplicate check: PASSED - {len(ids)} unique markets")
            else:
                self.add_issue("DUPLICATE_MARKETS", f"Found {duplicates} duplicate market IDs", "WARN")
                
        except Exception as e:
            self.add_issue("FILE_ERROR", f"Error checking duplicates: {e}", "ERROR")
            
    def run_full_validation(self):
        """Run complete validation suite"""
        self.log("Starting comprehensive Polymarket data validation...")
        
        # Check APIs
        gamma_markets = self.check_gamma_api()
        clob_markets = self.check_clob_api()
        
        # Cross-validate
        if gamma_markets and clob_markets:
            self.cross_validate_prices(gamma_markets, clob_markets)
            
        # Check local file
        file_age = self.check_local_file_freshness()
        self.check_duplicate_markets()
        
        # Summary
        self.log("=" * 60)
        self.log("VALIDATION SUMMARY")
        self.log("=" * 60)
        
        if not self.issues_found:
            self.log("ALL CHECKS PASSED - No issues detected")
        else:
            self.log(f"ISSUES FOUND: {len(self.issues_found)}")
            for issue in self.issues_found:
                self.log(f"   {issue['severity']}: {issue['type']} - {issue['description']}")
                
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "issues_count": len(self.issues_found),
            "file_age_minutes": file_age,
            "issues": self.issues_found,
            "log": self.validation_log
        }

if __name__ == "__main__":
    validator = PolymarketValidator()
    results = validator.run_full_validation()
    
    # Save results to file
    with open('validation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"\nValidation complete. Results saved to validation_results.json")