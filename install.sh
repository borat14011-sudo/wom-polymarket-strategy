#!/bin/bash
# Installation script for Polymarket Live Market Data System
# For Wom's trading operation

echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║     INSTALLING POLYMARKET LIVE MARKET DATA SYSTEM                        ║"
echo "║     For Wom's Trading Operation                                          ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.8+ required. Found: $python_version"
    exit 1
fi

echo "✓ Python version OK: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "Installing Python packages..."
pip install -r requirements.txt

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

# Create directories
echo ""
echo "Creating data directories..."
mkdir -p market_data
mkdir -p market_history
mkdir -p alerts

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════╗"
echo "║     ✓ INSTALLATION COMPLETE                                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Test API endpoints:    python run.py test"
echo "  2. Scrape markets:        python run.py scrape"
echo "  3. Start monitoring:      python run.py monitor"
echo "  4. Run everything:        python run.py full"
echo ""
echo "For help: python run.py help"
echo ""

# Offer to run a quick test
read -p "Run quick test now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Running API endpoint test..."
    python run.py test
fi