#!/usr/bin/env node

const fs = require('fs');
const positions = JSON.parse(fs.readFileSync('positions.json', 'utf8'));

// Kelly Criterion calculation
function calculateKelly(win_prob, win_loss_ratio, edge) {
    // Kelly formula: f = (bp - q) / b
    // where: f = fraction of capital to bet
    //        b = odds received on the bet (win_loss_ratio)
    //        p = probability of winning
    //        q = probability of losing (1-p)
    
    const p = win_prob;
    const q = 1 - p;
    const b = win_loss_ratio;
    
    const kelly_fraction = (b * p - q) / b;
    
    // Apply 0.25x Kelly for safety (common practice)
    const kelly_conservative = kelly_fraction * 0.25;
    
    return {
        full_kelly: kelly_fraction,
        conservative_kelly: kelly_conservative,
        percentage: kelly_conservative * 100
    };
}

// Calculate risk metrics for proposed position
function calculateRiskMetrics(position, portfolio) {
    // For the tariff position at 11% probability
    const win_prob = 0.11; // Market probability
    const implied_loss_prob = 0.89;
    
    // Estimated win/loss ratio based on market conditions
    const win_loss_ratio = (100 - 11) / 11; // ~8.09
    
    const kelly = calculateKelly(win_prob, win_loss_ratio, 0);
    
    // Calculate position risk
    const position_size = position.planned_size;
    const position_risk = (position_size / portfolio.total_capital) * 100;
    
    // Calculate stop loss level
    const stop_loss_price = position.entry_price * (1 - 0.12); // 12% stop loss
    
    return {
        kelly_size: kelly.conservative_kelly * portfolio.total_capital,
        kelly_percentage: kelly.percentage,
        position_risk: position_risk,
        stop_loss_price: stop_loss_price,
        risk_reward_ratio: win_loss_ratio
    };
}

// Update positions with risk metrics
positions.positions.forEach(position => {
    if (position.status === 'proposed') {
        const risk_metrics = calculateRiskMetrics(position, positions.portfolio);
        position.risk_metrics = risk_metrics;
        
        console.log('=== KELLY CRITERION ANALYSIS ===');
        console.log(`Market: ${position.market}`);
        console.log(`Entry Price: ${position.entry_price}%`);
        console.log(`Kelly Size: $${risk_metrics.kelly_size.toFixed(2)} (${risk_metrics.kelly_percentage.toFixed(2)}%)`);
        console.log(`Planned Size: $${position.planned_size}`);
        console.log(`Position Risk: ${risk_metrics.position_risk.toFixed(2)}%`);
        console.log(`Stop Loss Price: ${risk_metrics.stop_loss_price.toFixed(1)}%`);
        console.log(`Win/Loss Ratio: ${risk_metrics.risk_reward_ratio.toFixed(2)}`);
        
        // Check if planned size exceeds Kelly recommendation
        if (position.planned_size > risk_metrics.kelly_size) {
            console.log(`⚠️  WARNING: Planned size ($${position.planned_size}) exceeds Kelly recommendation ($${risk_metrics.kelly_size.toFixed(2)})`);
        }
        
        // Check risk limits
        if (risk_metrics.position_risk > positions.portfolio.risk_limits.max_position_size) {
            console.log(`🚫 RISK LIMIT EXCEEDED: Position risk (${risk_metrics.position_risk.toFixed(2)}%) exceeds max ${positions.portfolio.risk_limits.max_position_size}%`);
        }
    }
});

// Save updated positions
fs.writeFileSync('positions.json', JSON.stringify(positions, null, 2));
console.log('\n✅ Risk analysis complete and saved to positions.json');