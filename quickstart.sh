#!/bin/bash
# Quick Start Script for Paper Trading System

echo "🚀 Polymarket Paper Trading System - Quick Start"
echo "=================================================="
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "Quick commands:"
echo "  ./quickstart.sh scan       - Scan for signals"
echo "  ./quickstart.sh trade      - Execute paper trades"
echo "  ./quickstart.sh report     - Generate report"
echo "  ./quickstart.sh full       - Run full cycle"
echo ""

# Run based on argument
case "$1" in
    scan)
        echo "🔍 Running market scan..."
        python STRATEGY_SIGNALS.py --scan
        ;;
    trade)
        echo "💰 Executing paper trades..."
        python STRATEGY_SIGNALS.py --paper-trade
        ;;
    report)
        echo "📊 Generating report..."
        python STRATEGY_SIGNALS.py --report
        ;;
    full)
        echo "🔄 Running full cycle..."
        python STRATEGY_SIGNALS.py --run-all
        ;;
    *)
        echo "Usage: ./quickstart.sh [scan|trade|report|full]"
        ;;
esac
