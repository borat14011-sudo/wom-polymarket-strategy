#!/bin/bash
# Setup cron job for Polymarket Historical Price Scraper
# Run: chmod +x setup_scraper_cron.sh && ./setup_scraper_cron.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRAPER_PATH="$SCRIPT_DIR/historical_scraper.py"
PYTHON_BIN=$(which python3)

echo "🔧 Setting up cron job for Polymarket Historical Scraper"
echo "=========================================="
echo "Script directory: $SCRIPT_DIR"
echo "Python: $PYTHON_BIN"
echo ""

# Create cron entry
CRON_ENTRY="0 * * * * cd $SCRIPT_DIR && $PYTHON_BIN historical_scraper.py >> logs/scraper_cron.log 2>&1"

# Check if cron entry already exists
if crontab -l 2>/dev/null | grep -q "historical_scraper.py"; then
    echo "⚠️  Cron job already exists. Updating..."
    # Remove old entry
    crontab -l 2>/dev/null | grep -v "historical_scraper.py" | crontab -
fi

# Add new cron entry
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "✅ Cron job installed successfully!"
echo ""
echo "Cron entry:"
echo "  $CRON_ENTRY"
echo ""
echo "To verify:"
echo "  crontab -l | grep historical_scraper"
echo ""
echo "To view logs:"
echo "  tail -f $SCRIPT_DIR/logs/scraper_cron.log"
echo ""
echo "To remove cron job:"
echo "  crontab -e  (then delete the line containing 'historical_scraper.py')"
