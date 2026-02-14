#!/usr/bin/env node

const fs = require('fs');
const { execSync } = require('child_process');

function loadPositions() {
    return JSON.parse(fs.readFileSync('positions.json', 'utf8'));
}

function savePositions(positions) {
    fs.writeFileSync('positions.json', JSON.stringify(positions, null, 2));
}

function checkRiskLimits(positions) {
    const alerts = [];
    const portfolio = positions.portfolio;
    
    console.log('=== RISK MONITORING REPORT ===');
    console.log(`Time: ${new Date().toISOString()}`);
    console.log(`Total Capital: $${portfolio.total_capital}`);
    console.log(`Current Value: $${portfolio.current_value}`);
    console.log(`Total Exposure: ${portfolio.total_exposure}%`);
    console.log(`Available Capacity: ${portfolio.available_capacity}%`);
    console.log(`Drawdown: ${portfolio.drawdown}%`);
    console.log('');
    
    // Check each position
    positions.positions.forEach(position => {
        console.log(`Position: ${position.market}`);
        console.log(`  Status: ${position.status}`);
        console.log(`  Entry: ${position.entry_price}%`);
        console.log(`  Size: $${position.planned_size}`);
        
        if (position.risk_metrics) {
            console.log(`  Kelly Size: $${position.risk_metrics.kelly_size.toFixed(2)}`);
            console.log(`  Position Risk: ${position.risk_metrics.position_risk.toFixed(2)}%`);
            console.log(`  Stop Loss: ${position.risk_metrics.stop_loss_price.toFixed(1)}%`);
            
            // Check if position exceeds individual limit
            if (position.risk_metrics.position_risk > portfolio.risk_limits.max_position_size) {
                alerts.push(`🚫 Position ${position.id} exceeds max size limit: ${position.risk_metrics.position_risk.toFixed(2)}% > ${portfolio.risk_limits.max_position_size}%`);
            }
        }
        console.log('');
    });
    
    // Check portfolio limits
    if (portfolio.total_exposure > portfolio.risk_limits.max_total_exposure) {
        alerts.push(`🚫 Total exposure exceeds limit: ${portfolio.total_exposure}% > ${portfolio.risk_limits.max_total_exposure}%`);
    }
    
    if (portfolio.drawdown > portfolio.risk_limits.circuit_breaker) {
        alerts.push(`⚡ CIRCUIT BREAKER TRIGGERED: Drawdown ${portfolio.drawdown}% > ${portfolio.risk_limits.circuit_breaker}%`);
    }
    
    if (alerts.length > 0) {
        console.log('=== ALERTS ===');
        alerts.forEach(alert => {
            console.log(alert);
            // Send immediate alert to main session
            sendAlert(alert);
        });
    } else {
        console.log('✅ All risk limits within acceptable ranges');
    }
    
    return alerts;
}

function sendAlert(message) {
    // Send alert to main session via Telegram
    const alertMessage = `🚨 RISK ALERT: ${message}`;
    console.log(`SENDING ALERT: ${alertMessage}`);
    
    // This would integrate with your messaging system
    // For now, we'll just log it
}

function generateHourlyReport() {
    const positions = loadPositions();
    const portfolio = positions.portfolio;
    
    const report = {
        timestamp: new Date().toISOString(),
        exposure_percentage: portfolio.total_exposure,
        available_capacity: portfolio.available_capacity,
        drawdown: portfolio.drawdown,
        active_positions: positions.positions.filter(p => p.status === 'active').length,
        proposed_positions: positions.positions.filter(p => p.status === 'proposed').length,
        alerts: checkRiskLimits(positions)
    };
    
    console.log('=== HOURLY RISK REPORT ===');
    console.log(JSON.stringify(report, null, 2));
    
    return report;
}

function simulatePriceUpdate(marketId, newPrice) {
    const positions = loadPositions();
    const position = positions.positions.find(p => p.id === marketId);
    
    if (position && position.status === 'active') {
        const priceChange = ((newPrice - position.entry_price) / position.entry_price) * 100;
        
        console.log(`Price update for ${position.market}:`);
        console.log(`  Old: ${position.entry_price}% → New: ${newPrice}%`);
        console.log(`  Change: ${priceChange.toFixed(2)}%`);
        
        // Check stop loss
        if (priceChange < -12) {
            console.log(`🛑 STOP LOSS TRIGGERED: ${priceChange.toFixed(2)}% decline`);
            sendAlert(`Stop loss triggered for ${position.market}: ${priceChange.toFixed(2)}% decline`);
        }
        
        // Update position value and portfolio
        const positionValue = position.planned_size * (1 + (priceChange / 100));
        const portfolioChange = (positionValue - position.planned_size) / positions.portfolio.total_capital * 100;
        
        positions.portfolio.current_value += portfolioChange * positions.portfolio.total_capital / 100;
        positions.portfolio.drawdown = Math.max(0, ((positions.portfolio.peak_capital - positions.portfolio.current_value) / positions.portfolio.peak_capital) * 100);
        
        savePositions(positions);
    }
}

// Command line interface
const command = process.argv[2];

switch (command) {
    case 'monitor':
        checkRiskLimits(loadPositions());
        break;
    case 'report':
        generateHourlyReport();
        break;
    case 'price-update':
        if (process.argv.length < 5) {
            console.log('Usage: node risk_monitor.js price-update <marketId> <newPrice>');
            process.exit(1);
        }
        simulatePriceUpdate(process.argv[3], parseFloat(process.argv[4]));
        break;
    default:
        console.log('Usage: node risk_monitor.js [monitor|report|price-update]');
        console.log('  monitor      - Check current risk limits');
        console.log('  report       - Generate hourly report');
        console.log('  price-update - Simulate price update for testing');
}

module.exports = { checkRiskLimits, generateHourlyReport, sendAlert };