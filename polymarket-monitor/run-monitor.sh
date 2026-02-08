#!/bin/bash

# Polymarket Monitor - Start Script

echo "🚀 Starting Polymarket Volume Monitor..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "❌ Error: Python not found"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo "Using: $PYTHON_CMD"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import requests; import schedule" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

echo ""
echo "Starting monitor daemon..."
echo "Press Ctrl+C to stop"
echo ""

# Run the daemon
$PYTHON_CMD monitor_daemon.py
