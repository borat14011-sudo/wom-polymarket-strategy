#!/usr/bin/env node

const fs = require('fs');

function createRiskDashboard() {
    const positions = JSON.parse(fs.readFileSync('positions.json', 'utf8'));
    const portfolio = positions.portfolio;
    
    const dashboard = `
🎯 RISK MANAGEMENT DASHBOARD
═══════════════════════════════════════════════════════════

💰 PORTFOLIO OVERVIEW
   Total Capital: $${portfolio.total_capital.toLocaleString()}
   Current Value: $${portfolio.current_value.toLocaleString()}
   Peak Capital: $${portfolio.peak_capital.toLocaleString()}
   Drawdown: ${portfolio.drawdown.toFixed(2)}% ${portfolio.drawdown > 5 ? '⚠️' : '✅'}

📊 EXPOSURE ANALYSIS
   Total Exposure: ${portfolio.total_exposure}% / ${portfolio.risk_limits.max_total_exposure}% ${portfolio.total_exposure > portfolio.risk_limits.max_total_exposure * 0.8 ? '⚠️' : '✅'}
   Available Capacity: ${portfolio.available_capacity}%
   
🛡️ RISK LIMITS
   Max Position Size: ${portfolio.risk_limits.max_position_size}% ${portfolio.risk_limits.max_position_size > 2 ? '(TESTING PHASE)' : ''}
   Max Total Exposure: ${portfolio.risk_limits.max_total_exposure}%
   Stop Loss: ${portfolio.risk_limits.stop_loss}%
   Circuit Breaker: ${portfolio.risk_limits.circuit_breaker}%

📈 ACTIVE POSITIONS
${positions.positions.map(pos => {
    const riskStatus = pos.risk_metrics?.position_risk > portfolio.risk_limits.max_position_size ? '🚫' : '✅';
    const kellyStatus = pos.planned_size > pos.risk_metrics?.kelly_size ? '⚠️' : '✅';
    
    return `
   ${pos.market}
   ├─ Status: ${pos.status.toUpperCase()}
   ├─ Entry: ${pos.entry_price}%
   ├─ Size: $${pos.planned_size} (Risk: ${pos.risk_metrics?.position_risk.toFixed(2)}%) ${riskStatus}
   ├─ Kelly Size: $${pos.risk_metrics?.kelly_size.toFixed(2)} ${kellyStatus}
   ├─ Stop Loss: ${pos.risk_metrics?.stop_loss_price.toFixed(1)}%
   └─ Win/Loss Ratio: ${pos.risk_metrics?.risk_reward_ratio.toFixed(2)}`;
}).join('\n')}

⚡ ALERT STATUS
   ${portfolio.drawdown > portfolio.risk_limits.circuit_breaker ? '🚨 CIRCUIT BREAKER TRIGGERED!' : 
     portfolio.drawdown > 10 ? '⚠️  HIGH DRAWDOWN WARNING' :
     portfolio.total_exposure > portfolio.risk_limits.max_total_exposure * 0.9 ? '⚠️  NEAR EXPOSURE LIMIT' :
     '✅ ALL SYSTEMS NOMINAL'}

═══════════════════════════════════════════════════════════
Last Updated: ${new Date().toLocaleString()}
    `;
    
    return dashboard;
}

function saveDashboard() {
    const dashboard = createRiskDashboard();
    fs.writeFileSync('risk_dashboard.txt', dashboard);
    console.log(dashboard);
    console.log('\n📊 Dashboard saved to risk_dashboard.txt');
}

// If run directly, show dashboard
if (require.main === module) {
    saveDashboard();
}

module.exports = { createRiskDashboard, saveDashboard };