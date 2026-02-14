#!/bin/bash

# Risk Manager Cron Setup
# This script sets up automated monitoring every 15 minutes

echo "Setting up risk monitoring cron jobs..."

# Add cron jobs for risk monitoring
(crontab -l 2>/dev/null; echo "*/15 * * * * cd /workspace && node risk_monitor.js monitor >> /workspace/logs/risk_monitor.log 2>&1") | crontab -
(crontab -l 2>/dev/null; echo "0 * * * * cd /workspace && node risk_monitor.js report >> /workspace/logs/hourly_report.log 2>&1") | crontab -

echo "Cron jobs added:"
echo "  - Risk monitoring every 15 minutes"
echo "  - Hourly reports"
echo ""
echo "Logs will be saved to:"
echo "  - /workspace/logs/risk_monitor.log"
echo "  - /workspace/logs/hourly_report.log"

# Create logs directory
mkdir -p /workspace/logs

echo "✅ Risk monitoring automation setup complete!"