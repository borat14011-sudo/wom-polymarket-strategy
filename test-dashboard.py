#!/usr/bin/env python3
"""
Dashboard Test Script
Verifies that all components are properly set up
"""

import os
import sys
import sqlite3

def test_files():
    """Check if all required files exist"""
    print("📁 Checking files...")
    
    required_files = [
        'dashboard.html',
        'api.py',
        'requirements.txt',
        'DASHBOARD-README.md'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} (MISSING)")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    
    print("   ✅ All files present\n")
    return True

def test_database():
    """Check if database exists and has correct schema"""
    print("🗄️  Checking database...")
    
    db_path = "polymarket_data.db"
    
    if not os.path.exists(db_path):
        print(f"   ⚠️  Database not found: {db_path}")
        print("   Run data collectors first:")
        print("     python polymarket-data-collector.py")
        print("     python twitter-hype-monitor.py")
        print("")
        return False
    
    # Check database schema
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['markets', 'snapshots', 'tweets', 'hype_signals']
        
        for table in required_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   ✓ {table}: {count:,} records")
            else:
                print(f"   ✗ {table}: MISSING")
        
        conn.close()
        
        if all(table in tables for table in required_tables):
            print("   ✅ Database schema valid\n")
            return True
        else:
            print("   ❌ Database schema incomplete\n")
            return False
            
    except Exception as e:
        print(f"   ❌ Database error: {e}\n")
        return False

def test_python_dependencies():
    """Check if Python dependencies are installed"""
    print("🐍 Checking Python dependencies...")
    
    dependencies = {
        'flask': 'Flask',
        'flask_cors': 'flask-cors'
    }
    
    missing_deps = []
    
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (NOT INSTALLED)")
            missing_deps.append(package)
    
    if missing_deps:
        print(f"\n   ❌ Missing dependencies: {', '.join(missing_deps)}")
        print("   Install with: pip install -r requirements.txt\n")
        return False
    
    print("   ✅ All dependencies installed\n")
    return True

def test_api_syntax():
    """Check if api.py has valid Python syntax"""
    print("🔍 Checking api.py syntax...")
    
    try:
        with open('api.py', 'r') as f:
            code = f.read()
        compile(code, 'api.py', 'exec')
        print("   ✅ api.py syntax valid\n")
        return True
    except SyntaxError as e:
        print(f"   ❌ Syntax error in api.py: {e}\n")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("   Dashboard Test Suite")
    print("=" * 60)
    print("")
    
    results = {
        'Files': test_files(),
        'Python Dependencies': test_python_dependencies(),
        'API Syntax': test_api_syntax(),
        'Database': test_database()
    }
    
    print("=" * 60)
    print("   Test Results")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All tests passed! Dashboard is ready to run.")
        print("\nStart the dashboard with:")
        print("  Linux/Mac: ./start-dashboard.sh")
        print("  Windows:   start-dashboard.bat")
        print("  Manual:    python api.py (then open dashboard.html)")
        return 0
    else:
        print("\n⚠️  Some tests failed. Fix the issues above before running.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
