#!/bin/bash
#
# Dashboard Launcher Script
# Starts Flask API backend and opens dashboard in browser
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Trading System Dashboard Launcher${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if database exists
if [ ! -f "polymarket_data.db" ]; then
    echo -e "${RED}⚠️  WARNING: Database not found!${NC}"
    echo ""
    echo -e "Expected file: ${YELLOW}polymarket_data.db${NC}"
    echo ""
    echo "Run the data collectors first:"
    echo "  python polymarket-data-collector.py"
    echo "  python twitter-hype-monitor.py"
    echo ""
    echo "The dashboard will still start, but will show no data."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found!${NC}"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}📦 Flask not found. Installing dependencies...${NC}"
    pip install -r requirements.txt
    echo ""
fi

# Check if api.py exists
if [ ! -f "api.py" ]; then
    echo -e "${RED}❌ api.py not found!${NC}"
    exit 1
fi

# Check if dashboard.html exists
if [ ! -f "dashboard.html" ]; then
    echo -e "${RED}❌ dashboard.html not found!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All dependencies found${NC}"
echo ""

# Start Flask API in background
echo -e "${BLUE}🚀 Starting Flask API server...${NC}"
python3 api.py &
API_PID=$!

# Give Flask time to start
sleep 2

# Check if Flask started successfully
if ! kill -0 $API_PID 2>/dev/null; then
    echo -e "${RED}❌ Failed to start Flask API${NC}"
    exit 1
fi

echo -e "${GREEN}✓ API server running on http://localhost:5000${NC}"
echo -e "${GREEN}   PID: $API_PID${NC}"
echo ""

# Open dashboard in browser
echo -e "${BLUE}🌐 Opening dashboard in browser...${NC}"
DASHBOARD_PATH="$(pwd)/dashboard.html"

# Detect OS and open browser
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open "$DASHBOARD_PATH"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open "$DASHBOARD_PATH"
    else
        echo -e "${YELLOW}⚠️  Could not auto-open browser${NC}"
        echo -e "   Open manually: file://$DASHBOARD_PATH"
    fi
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    # Windows Git Bash or Cygwin
    start "$DASHBOARD_PATH"
else
    echo -e "${YELLOW}⚠️  Unknown OS, could not auto-open browser${NC}"
    echo -e "   Open manually: file://$DASHBOARD_PATH"
fi

echo ""
echo -e "${GREEN}✅ Dashboard is running!${NC}"
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "   Dashboard URL: ${YELLOW}file://$DASHBOARD_PATH${NC}"
echo -e "   API URL:       ${YELLOW}http://localhost:5000${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Dashboard will auto-refresh every 60 seconds"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping server...'; kill $API_PID 2>/dev/null; exit 0" INT

# Keep script running
wait $API_PID
