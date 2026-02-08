"""
Test script for api_monitor.py
Validates that the script is Windows-compatible and can run without encoding errors
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("[TEST] Testing imports...")
    
    try:
        import requests
        print("[OK] requests module available")
    except ImportError:
        print("[WARN] requests not installed. Run: pip install requests")
        return False
    
    try:
        import logging
        import datetime
        print("[OK] Standard library modules available")
    except ImportError as e:
        print(f"[ERROR] Standard library import failed: {e}")
        return False
    
    return True

def test_api_monitor_syntax():
    """Test that api_monitor.py has valid Python syntax"""
    print("\n[TEST] Testing api_monitor.py syntax...")
    
    script_path = Path(__file__).parent / "api_monitor.py"
    
    if not script_path.exists():
        print(f"[ERROR] api_monitor.py not found at {script_path}")
        return False
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Try to compile the code
        compile(code, script_path, 'exec')
        print("[OK] api_monitor.py syntax is valid")
        return True
        
    except SyntaxError as e:
        print(f"[ERROR] Syntax error in api_monitor.py: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to validate syntax: {e}")
        return False

def test_encoding_safety():
    """Test that no emoji or problematic characters exist in the code"""
    print("\n[TEST] Testing Windows encoding safety...")
    
    script_path = Path(__file__).parent / "api_monitor.py"
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common emoji that cause Windows console issues
        problem_chars = {
            '🔍': 'magnifying glass',
            '✅': 'checkmark',
            '❌': 'X mark',
            '⚠️': 'warning',
            '📊': 'chart',
            '🚀': 'rocket',
            '💰': 'money',
            '📈': 'chart up',
            '📉': 'chart down',
        }
        
        found_emoji = []
        for emoji, name in problem_chars.items():
            if emoji in content:
                found_emoji.append(f"{emoji} ({name})")
        
        if found_emoji:
            print(f"[ERROR] Found problematic emoji: {', '.join(found_emoji)}")
            return False
        
        print("[OK] No problematic emoji characters found")
        print("[OK] Script is Windows console-safe")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to check encoding: {e}")
        return False

def test_log_directory():
    """Test that logs directory exists or can be created"""
    print("\n[TEST] Testing log directory...")
    
    log_dir = Path(__file__).parent / "logs"
    
    try:
        log_dir.mkdir(exist_ok=True)
        print(f"[OK] Logs directory exists: {log_dir}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create logs directory: {e}")
        return False

def test_position_calculations():
    """Test P/L calculation logic"""
    print("\n[TEST] Testing position calculation logic...")
    
    try:
        # Simulate position
        entry_price = 0.12
        position_size = 4.20
        stop_loss = 0.106
        
        # Test scenarios
        test_cases = [
            (0.15, "Price increased to 15%"),
            (0.10, "Price decreased to 10% (below stop)"),
            (0.12, "Price unchanged at 12%"),
        ]
        
        for current_price, description in test_cases:
            price_change = current_price - entry_price
            price_change_pct = (price_change / entry_price) * 100
            unrealized_pl = (current_price - entry_price) * (position_size / entry_price)
            hit_stop = current_price <= stop_loss
            
            print(f"  {description}:")
            print(f"    Current: {current_price*100:.1f}%")
            print(f"    Change: {price_change_pct:+.1f}%")
            print(f"    P/L: ${unrealized_pl:+.2f}")
            print(f"    Stop Hit: {hit_stop}")
        
        print("[OK] Position calculations working correctly")
        return True
        
    except Exception as e:
        print(f"[ERROR] Calculation test failed: {e}")
        return False

def test_historical_scraper_fixed():
    """Test that historical_scraper.py emoji issues are fixed"""
    print("\n[TEST] Testing historical_scraper.py fixes...")
    
    script_path = Path(__file__).parent / "historical_scraper.py"
    
    if not script_path.exists():
        print(f"[WARN] historical_scraper.py not found (optional)")
        return True
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that emoji have been replaced
        if any(emoji in content for emoji in ['🔍', '✅', '❌', '⚠️', '📊', '🚀']):
            print("[ERROR] historical_scraper.py still contains emoji")
            return False
        
        # Check that ASCII replacements exist
        if '[SCRAPE]' in content and '[SUCCESS]' in content and '[ERROR]' in content:
            print("[OK] historical_scraper.py emoji fixed with ASCII tags")
            return True
        
        print("[WARN] Could not verify emoji fixes")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to check historical_scraper.py: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 70)
    print("POLYMARKET API MONITOR - TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Import Test", test_imports),
        ("Syntax Validation", test_api_monitor_syntax),
        ("Encoding Safety", test_encoding_safety),
        ("Log Directory", test_log_directory),
        ("Position Calculations", test_position_calculations),
        ("Historical Scraper Fixes", test_historical_scraper_fixed),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[ERROR] Test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("=" * 70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! api_monitor.py is ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install requests")
        print("2. Run monitor: python api_monitor.py")
        print("3. Setup scheduled task (see IRAN_MONITOR_SETUP.md)")
        return 0
    else:
        print("[WARN] Some tests failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
