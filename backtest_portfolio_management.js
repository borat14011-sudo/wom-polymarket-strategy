#!/usr/bin/env node
/**
 * Portfolio Management Backtest - Multi-Position Strategy Testing
 * Tests portfolio allocation rules for multiple simultaneous positions
 * 
 * Scenarios:
 * 1. Multiple correlated positions (2x Iran markets)
 * 2. Opposite positions (hedge YES on one, NO on correlated)
 * 3. Concentration vs diversification (one 25% vs five 5% positions)
 * 4. Rebalancing rules (when to take profits on winners)
 */

const fs = require('fs');

// Constants
const STARTING_BANKROLL = 1000;  // Use $1000 for realistic position sizing
const NUM_SIMULATIONS = 1000;
const SIMULATION_DAYS = 180;  // 6 months
const WIN_RATE_BASE = 0.55;
const REWARD_RISK_RATIO = 1.5;

// Portfolio rules
const MAX_SINGLE_POSITION_PCT = 0.05;  // 5%
const MAX_TOTAL_EXPOSURE_PCT = 0.25;   // 25%
const MIN_CASH_RESERVE_PCT = 0.50;     // 50%

// Position sizing using quarter Kelly
const KELLY_FULL = 0.25;  // Full Kelly for 55% win rate, 1.5 R:R
const POSITION_SIZE_KELLY = KELLY_FULL * 0.25;  // Quarter Kelly = 6.25%

// Correlation coefficients
const CORRELATION_HIGH = 0.85;
const CORRELATION_MODERATE = 0.60;
const CORRELATION_LOW = 0.20;
const CORRELATION_NEGATIVE = -0.70;

class Position {
    constructor(marketId, entryPrice, sizeUsd, sizePct, direction, correlationGroup) {
        this.marketId = marketId;
        this.entryPrice = entryPrice;
        this.sizeUsd = sizeUsd;
        this.sizePct = sizePct;
        this.direction = direction;  // 'YES' or 'NO'
        this.correlationGroup = correlationGroup;
        this.daysHeld = 0;
        this.unrealizedPnl = 0.0;
    }
    
    updatePnl(currentPrice, rrr) {
        const priceChange = this.direction === 'YES' 
            ? currentPrice - this.entryPrice
            : this.entryPrice - currentPrice;
        
        this.unrealizedPnl = (priceChange / this.entryPrice) * this.sizeUsd * rrr;
    }
}

class Trade {
    constructor(marketId, entryPrice, exitPrice, sizeUsd, pnl, win, daysHeld, reason) {
        this.marketId = marketId;
        this.entryPrice = entryPrice;
        this.exitPrice = exitPrice;
        this.sizeUsd = sizeUsd;
        this.pnl = pnl;
        this.win = win;
        this.daysHeld = daysHeld;
        this.reason = reason;
    }
}

class Portfolio {
    constructor(startingCapital) {
        this.startingCapital = startingCapital;
        this.cash = startingCapital;
        this.positions = [];
        this.trades = [];
        this.equityCurve = [startingCapital];
        this.dailyReturns = [];
        this.maxDrawdown = 0.0;
        this.peakEquity = startingCapital;
    }
    
    get totalEquity() {
        const positionValue = this.positions.reduce((sum, p) => 
            sum + p.sizeUsd + p.unrealizedPnl, 0);
        return this.cash + positionValue;
    }
    
    get totalExposure() {
        return this.positions.reduce((sum, p) => sum + p.sizeUsd, 0);
    }
    
    get exposurePct() {
        return this.totalEquity > 0 ? this.totalExposure / this.totalEquity : 0;
    }
    
    get numPositions() {
        return this.positions.length;
    }
    
    canAddPosition(sizeUsd) {
        const totalEquity = this.totalEquity;
        
        // Check single position limit
        if (sizeUsd > totalEquity * MAX_SINGLE_POSITION_PCT) {
            return false;
        }
        
        // Check total exposure limit
        if ((this.totalExposure + sizeUsd) > totalEquity * MAX_TOTAL_EXPOSURE_PCT) {
            return false;
        }
        
        // Check minimum cash reserve
        if ((this.cash - sizeUsd) < totalEquity * MIN_CASH_RESERVE_PCT) {
            return false;
        }
        
        return true;
    }
    
    addPosition(marketId, sizeUsd, direction, correlationGroup, entryPrice = 0.5) {
        if (!this.canAddPosition(sizeUsd)) {
            return false;
        }
        
        const sizePct = sizeUsd / this.totalEquity;
        const position = new Position(
            marketId, entryPrice, sizeUsd, sizePct, direction, correlationGroup
        );
        
        this.positions.push(position);
        this.cash -= sizeUsd;
        return true;
    }
    
    closePosition(position, exitPrice, reason) {
        const priceChange = position.direction === 'YES'
            ? exitPrice - position.entryPrice
            : position.entryPrice - exitPrice;
        
        const pnl = (priceChange / position.entryPrice) * position.sizeUsd * REWARD_RISK_RATIO;
        
        // Return capital + P&L to cash
        this.cash += position.sizeUsd + pnl;
        
        // Record trade
        const trade = new Trade(
            position.marketId,
            position.entryPrice,
            exitPrice,
            position.sizeUsd,
            pnl,
            pnl > 0,
            position.daysHeld,
            reason
        );
        this.trades.push(trade);
        
        // Remove from active positions
        const index = this.positions.indexOf(position);
        if (index > -1) {
            this.positions.splice(index, 1);
        }
        
        return pnl;
    }
    
    updateEquityCurve() {
        const equity = this.totalEquity;
        this.equityCurve.push(equity);
        
        // Calculate daily return
        if (this.equityCurve.length > 1) {
            const prevEquity = this.equityCurve[this.equityCurve.length - 2];
            const dailyReturn = (equity / prevEquity) - 1;
            this.dailyReturns.push(dailyReturn);
        }
        
        // Update drawdown
        if (equity > this.peakEquity) {
            this.peakEquity = equity;
        }
        
        const drawdown = (this.peakEquity - equity) / this.peakEquity;
        this.maxDrawdown = Math.max(this.maxDrawdown, drawdown);
    }
}

// Utility functions
function median(arr) {
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 === 0
        ? (sorted[mid - 1] + sorted[mid]) / 2
        : sorted[mid];
}

function mean(arr) {
    return arr.reduce((sum, val) => sum + val, 0) / arr.length;
}

function percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = (p / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index - lower;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

// Simulation functions
function simulateCorrelatedPositions(correlation, numPositions) {
    const results = [];
    
    for (let sim = 0; sim < NUM_SIMULATIONS; sim++) {
        const portfolio = new Portfolio(STARTING_BANKROLL);
        
        for (let day = 0; day < SIMULATION_DAYS; day++) {
            // Try to add positions if we have room
            while (portfolio.numPositions < numPositions) {
                const size = Math.min(
                    portfolio.totalEquity * POSITION_SIZE_KELLY,
                    portfolio.totalEquity * MAX_SINGLE_POSITION_PCT
                );
                
                if (portfolio.canAddPosition(size)) {
                    const marketId = `correlated_market_${portfolio.numPositions + 1}`;
                    portfolio.addPosition(marketId, size, 'YES', 'iran_cluster', 0.50);
                } else {
                    break;
                }
            }
            
            // Simulate correlated outcomes
            const baseOutcome = Math.random() < WIN_RATE_BASE;
            
            const positionsCopy = [...portfolio.positions];
            for (const position of positionsCopy) {
                // Correlated outcome
                const isWinner = Math.random() < correlation 
                    ? baseOutcome 
                    : Math.random() < WIN_RATE_BASE;
                
                position.daysHeld++;
                
                // Determine exit
                if (isWinner && Math.random() < 0.15) {
                    const exitPrice = position.entryPrice * 1.15;
                    portfolio.closePosition(position, exitPrice, 'target');
                } else if (!isWinner && Math.random() < 0.20) {
                    const exitPrice = position.entryPrice * 0.88;
                    portfolio.closePosition(position, exitPrice, 'stop');
                } else {
                    // Update unrealized P&L
                    position.updatePnl(
                        position.entryPrice * (isWinner ? 1.03 : 0.97),
                        REWARD_RISK_RATIO
                    );
                }
            }
            
            portfolio.updateEquityCurve();
        }
        
        results.push({
            finalEquity: portfolio.totalEquity,
            totalReturn: (portfolio.totalEquity / STARTING_BANKROLL - 1) * 100,
            maxDrawdown: portfolio.maxDrawdown * 100,
            numTrades: portfolio.trades.length,
            winRate: portfolio.trades.length > 0 
                ? portfolio.trades.filter(t => t.win).length / portfolio.trades.length 
                : 0
        });
    }
    
    return {
        medianReturn: median(results.map(r => r.totalReturn)),
        meanReturn: mean(results.map(r => r.totalReturn)),
        medianDrawdown: median(results.map(r => r.maxDrawdown)),
        maxDrawdown: Math.max(...results.map(r => r.maxDrawdown)),
        winRate: mean(results.map(r => r.winRate)),
        p25Return: percentile(results.map(r => r.totalReturn), 25),
        p75Return: percentile(results.map(r => r.totalReturn), 75)
    };
}

function simulateHedgePositions() {
    const results = [];
    
    for (let sim = 0; sim < NUM_SIMULATIONS; sim++) {
        const portfolio = new Portfolio(STARTING_BANKROLL);
        
        for (let day = 0; day < SIMULATION_DAYS; day++) {
            // Try to add hedge pair if we have room
            if (portfolio.numPositions < 2) {
                const size = Math.min(
                    portfolio.totalEquity * POSITION_SIZE_KELLY,
                    portfolio.totalEquity * MAX_SINGLE_POSITION_PCT
                );
                
                if (portfolio.canAddPosition(size * 2)) {
                    // Position 1: YES
                    portfolio.addPosition("iran_strike", size, 'YES', 'iran_hedge', 0.50);
                    // Position 2: NO on correlated (hedge)
                    portfolio.addPosition("oil_price_drop", size, 'NO', 'iran_hedge', 0.50);
                }
            }
            
            // Simulate inverse correlated outcomes
            const baseOutcome = Math.random() < WIN_RATE_BASE;
            
            const positionsCopy = [...portfolio.positions];
            positionsCopy.forEach((position, i) => {
                position.daysHeld++;
                
                // Positions are inversely correlated
                let isWinner;
                if (i % 2 === 0) {
                    isWinner = baseOutcome;
                } else {
                    // Inverse outcome with correlation strength
                    isWinner = Math.random() < Math.abs(CORRELATION_NEGATIVE)
                        ? !baseOutcome
                        : Math.random() < WIN_RATE_BASE;
                }
                
                // Determine exit
                if (isWinner && Math.random() < 0.15) {
                    const exitPrice = position.entryPrice * 1.15;
                    portfolio.closePosition(position, exitPrice, 'target');
                } else if (!isWinner && Math.random() < 0.20) {
                    const exitPrice = position.entryPrice * 0.88;
                    portfolio.closePosition(position, exitPrice, 'stop');
                } else {
                    position.updatePnl(
                        position.entryPrice * (isWinner ? 1.03 : 0.97),
                        REWARD_RISK_RATIO
                    );
                }
            });
            
            portfolio.updateEquityCurve();
        }
        
        results.push({
            finalEquity: portfolio.totalEquity,
            totalReturn: (portfolio.totalEquity / STARTING_BANKROLL - 1) * 100,
            maxDrawdown: portfolio.maxDrawdown * 100,
            numTrades: portfolio.trades.length,
            winRate: portfolio.trades.length > 0 
                ? portfolio.trades.filter(t => t.win).length / portfolio.trades.length 
                : 0
        });
    }
    
    return {
        medianReturn: median(results.map(r => r.totalReturn)),
        medianDrawdown: median(results.map(r => r.maxDrawdown)),
        maxDrawdown: Math.max(...results.map(r => r.maxDrawdown)),
        winRate: mean(results.map(r => r.winRate)),
        p25Return: percentile(results.map(r => r.totalReturn), 25),
        p75Return: percentile(results.map(r => r.totalReturn), 75)
    };
}

function simulateConcentrationVsDiversification() {
    const concentratedResults = [];
    const diversifiedResults = [];
    
    for (let sim = 0; sim < NUM_SIMULATIONS; sim++) {
        const portConcentrated = new Portfolio(STARTING_BANKROLL);
        const portDiversified = new Portfolio(STARTING_BANKROLL);
        
        for (let day = 0; day < SIMULATION_DAYS; day++) {
            // CONCENTRATED: Try to maintain one 25% position
            if (portConcentrated.numPositions === 0) {
                const size = portConcentrated.totalEquity * MAX_TOTAL_EXPOSURE_PCT;
                if (portConcentrated.cash >= size) {
                    portConcentrated.addPosition(
                        "concentrated_bet", size, 'YES', 'concentrated', 0.50
                    );
                }
            }
            
            // DIVERSIFIED: Try to maintain five 5% positions
            while (portDiversified.numPositions < 5) {
                const size = portDiversified.totalEquity * MAX_SINGLE_POSITION_PCT;
                if (portDiversified.canAddPosition(size)) {
                    portDiversified.addPosition(
                        `diversified_bet_${portDiversified.numPositions + 1}`,
                        size, 'YES', 'diversified', 0.50
                    );
                } else {
                    break;
                }
            }
            
            // Update both portfolios
            for (const portfolio of [portConcentrated, portDiversified]) {
                const positionsCopy = [...portfolio.positions];
                for (const position of positionsCopy) {
                    position.daysHeld++;
                    const isWinner = Math.random() < WIN_RATE_BASE;
                    
                    if (isWinner && Math.random() < 0.15) {
                        const exitPrice = position.entryPrice * 1.15;
                        portfolio.closePosition(position, exitPrice, 'target');
                    } else if (!isWinner && Math.random() < 0.20) {
                        const exitPrice = position.entryPrice * 0.88;
                        portfolio.closePosition(position, exitPrice, 'stop');
                    } else {
                        position.updatePnl(
                            position.entryPrice * (isWinner ? 1.03 : 0.97),
                            REWARD_RISK_RATIO
                        );
                    }
                }
                
                portfolio.updateEquityCurve();
            }
        }
        
        concentratedResults.push({
            finalEquity: portConcentrated.totalEquity,
            totalReturn: (portConcentrated.totalEquity / STARTING_BANKROLL - 1) * 100,
            maxDrawdown: portConcentrated.maxDrawdown * 100,
            numTrades: portConcentrated.trades.length,
            winRate: portConcentrated.trades.length > 0 
                ? portConcentrated.trades.filter(t => t.win).length / portConcentrated.trades.length 
                : 0
        });
        
        diversifiedResults.push({
            finalEquity: portDiversified.totalEquity,
            totalReturn: (portDiversified.totalEquity / STARTING_BANKROLL - 1) * 100,
            maxDrawdown: portDiversified.maxDrawdown * 100,
            numTrades: portDiversified.trades.length,
            winRate: portDiversified.trades.length > 0 
                ? portDiversified.trades.filter(t => t.win).length / portDiversified.trades.length 
                : 0
        });
    }
    
    return [
        {
            strategy: 'CONCENTRATED (One 25% position)',
            medianReturn: median(concentratedResults.map(r => r.totalReturn)),
            medianDrawdown: median(concentratedResults.map(r => r.maxDrawdown)),
            maxDrawdown: Math.max(...concentratedResults.map(r => r.maxDrawdown)),
            winRate: mean(concentratedResults.map(r => r.winRate)),
            p25Return: percentile(concentratedResults.map(r => r.totalReturn), 25),
            p75Return: percentile(concentratedResults.map(r => r.totalReturn), 75)
        },
        {
            strategy: 'DIVERSIFIED (Five 5% positions)',
            medianReturn: median(diversifiedResults.map(r => r.totalReturn)),
            medianDrawdown: median(diversifiedResults.map(r => r.maxDrawdown)),
            maxDrawdown: Math.max(...diversifiedResults.map(r => r.maxDrawdown)),
            winRate: mean(diversifiedResults.map(r => r.winRate)),
            p25Return: percentile(diversifiedResults.map(r => r.totalReturn), 25),
            p75Return: percentile(diversifiedResults.map(r => r.totalReturn), 75)
        }
    ];
}

function simulateRebalancingStrategies() {
    const results = {};
    
    for (const [strategyName, rebalancePct] of [
        ['NO_REBALANCE', 0.0],
        ['HALF_REBALANCE', 0.5],
        ['FULL_REBALANCE', 1.0]
    ]) {
        const strategyResults = [];
        
        for (let sim = 0; sim < NUM_SIMULATIONS; sim++) {
            const portfolio = new Portfolio(STARTING_BANKROLL);
            
            for (let day = 0; day < SIMULATION_DAYS; day++) {
                // Add positions up to max exposure
                while (portfolio.numPositions < 5) {
                    const size = Math.min(
                        portfolio.totalEquity * POSITION_SIZE_KELLY,
                        portfolio.totalEquity * MAX_SINGLE_POSITION_PCT
                    );
                    if (portfolio.canAddPosition(size)) {
                        portfolio.addPosition(
                            `rebalance_test_${portfolio.numPositions}`,
                            size, 'YES', 'rebalance', 0.50
                        );
                    } else {
                        break;
                    }
                }
                
                // Check rebalancing rules
                const positionsCopy = [...portfolio.positions];
                for (const position of positionsCopy) {
                    const gainPct = position.sizeUsd > 0 
                        ? position.unrealizedPnl / position.sizeUsd 
                        : 0;
                    
                    // Rebalance if winner > 25%
                    if (gainPct > 0.25 && rebalancePct > 0) {
                        if (rebalancePct === 1.0) {
                            // Full rebalance - close entire position
                            const exitPrice = position.entryPrice * 1.25;
                            portfolio.closePosition(position, exitPrice, 'rebalance');
                        } else if (rebalancePct === 0.5) {
                            // Half rebalance - take 50% profits
                            const exitPrice = position.entryPrice * 1.25;
                            const originalSize = position.sizeUsd;
                            portfolio.closePosition(position, exitPrice, 'rebalance');
                            // Re-enter at half size
                            if (portfolio.canAddPosition(originalSize * 0.5)) {
                                portfolio.addPosition(
                                    position.marketId + "_reentry",
                                    originalSize * 0.5,
                                    position.direction,
                                    position.correlationGroup,
                                    exitPrice
                                );
                            }
                        }
                    }
                }
                
                // Normal position updates
                const positionsCopy2 = [...portfolio.positions];
                for (const position of positionsCopy2) {
                    position.daysHeld++;
                    const isWinner = Math.random() < WIN_RATE_BASE;
                    
                    if (isWinner && Math.random() < 0.15) {
                        const exitPrice = position.entryPrice * 1.15;
                        portfolio.closePosition(position, exitPrice, 'target');
                    } else if (!isWinner && Math.random() < 0.20) {
                        const exitPrice = position.entryPrice * 0.88;
                        portfolio.closePosition(position, exitPrice, 'stop');
                    } else {
                        position.updatePnl(
                            position.entryPrice * (isWinner ? 1.03 : 0.97),
                            REWARD_RISK_RATIO
                        );
                    }
                }
                
                portfolio.updateEquityCurve();
            }
            
            strategyResults.push({
                finalEquity: portfolio.totalEquity,
                totalReturn: (portfolio.totalEquity / STARTING_BANKROLL - 1) * 100,
                maxDrawdown: portfolio.maxDrawdown * 100,
                numTrades: portfolio.trades.length,
                winRate: portfolio.trades.length > 0 
                    ? portfolio.trades.filter(t => t.win).length / portfolio.trades.length 
                    : 0
            });
        }
        
        results[strategyName] = {
            strategy: strategyName,
            medianReturn: median(strategyResults.map(r => r.totalReturn)),
            medianDrawdown: median(strategyResults.map(r => r.maxDrawdown)),
            maxDrawdown: Math.max(...strategyResults.map(r => r.maxDrawdown)),
            winRate: mean(strategyResults.map(r => r.winRate)),
            p25Return: percentile(strategyResults.map(r => r.totalReturn), 25),
            p75Return: percentile(strategyResults.map(r => r.totalReturn), 75)
        };
    }
    
    return results;
}

// Main execution
function main() {
    console.log("=".repeat(80));
    console.log("PORTFOLIO MANAGEMENT BACKTEST");
    console.log("=".repeat(80));
    console.log(`Starting Capital: $${STARTING_BANKROLL.toLocaleString()}`);
    console.log(`Simulation Period: ${SIMULATION_DAYS} days`);
    console.log(`Number of Simulations: ${NUM_SIMULATIONS.toLocaleString()}`);
    console.log(`Base Win Rate: ${(WIN_RATE_BASE*100).toFixed(0)}%`);
    console.log(`Reward/Risk Ratio: ${REWARD_RISK_RATIO}:1`);
    console.log();
    console.log("Current Portfolio Rules:");
    console.log(`  - Max Single Position: ${(MAX_SINGLE_POSITION_PCT*100).toFixed(0)}%`);
    console.log(`  - Max Total Exposure: ${(MAX_TOTAL_EXPOSURE_PCT*100).toFixed(0)}%`);
    console.log(`  - Min Cash Reserve: ${(MIN_CASH_RESERVE_PCT*100).toFixed(0)}%`);
    console.log(`  - Position Sizing: Quarter Kelly (${(POSITION_SIZE_KELLY*100).toFixed(2)}%)`);
    console.log("=".repeat(80));
    console.log();
    
    // SCENARIO 1: Correlated Positions
    console.log("📊 SCENARIO 1: Multiple Correlated Positions (2x Iran Markets)");
    console.log("-".repeat(80));
    console.log("Testing: Should we take multiple positions in correlated markets?");
    console.log();
    
    console.log("Running simulations for different correlation levels...");
    const highCorr = simulateCorrelatedPositions(CORRELATION_HIGH, 2);
    const moderateCorr = simulateCorrelatedPositions(CORRELATION_MODERATE, 2);
    const lowCorr = simulateCorrelatedPositions(CORRELATION_LOW, 2);
    
    console.log("\nResults:");
    console.log(`\n  HIGH CORRELATION (0.85) - Two Iran markets:`);
    console.log(`    Median Return: ${highCorr.medianReturn.toFixed(1)}%`);
    console.log(`    Median Drawdown: ${highCorr.medianDrawdown.toFixed(1)}%`);
    console.log(`    Max Drawdown: ${highCorr.maxDrawdown.toFixed(1)}%`);
    console.log(`    Win Rate: ${(highCorr.winRate*100).toFixed(1)}%`);
    
    console.log(`\n  MODERATE CORRELATION (0.60) - Related markets:`);
    console.log(`    Median Return: ${moderateCorr.medianReturn.toFixed(1)}%`);
    console.log(`    Median Drawdown: ${moderateCorr.medianDrawdown.toFixed(1)}%`);
    console.log(`    Max Drawdown: ${moderateCorr.maxDrawdown.toFixed(1)}%`);
    console.log(`    Win Rate: ${(moderateCorr.winRate*100).toFixed(1)}%`);
    
    console.log(`\n  LOW CORRELATION (0.20) - Diversified markets:`);
    console.log(`    Median Return: ${lowCorr.medianReturn.toFixed(1)}%`);
    console.log(`    Median Drawdown: ${lowCorr.medianDrawdown.toFixed(1)}%`);
    console.log(`    Max Drawdown: ${lowCorr.maxDrawdown.toFixed(1)}%`);
    console.log(`    Win Rate: ${(lowCorr.winRate*100).toFixed(1)}%`);
    
    console.log("\n" + "=".repeat(80) + "\n");
    
    // SCENARIO 2: Hedge Positions
    console.log("📊 SCENARIO 2: Opposite Positions (Hedging)");
    console.log("-".repeat(80));
    console.log("Testing: YES on one market, NO on inversely correlated market");
    console.log();
    
    const hedgeResults = simulateHedgePositions();
    
    console.log("Results:");
    console.log(`  Median Return: ${hedgeResults.medianReturn.toFixed(1)}%`);
    console.log(`  Median Drawdown: ${hedgeResults.medianDrawdown.toFixed(1)}%`);
    console.log(`  Max Drawdown: ${hedgeResults.maxDrawdown.toFixed(1)}%`);
    console.log(`  Win Rate: ${(hedgeResults.winRate*100).toFixed(1)}%`);
    
    console.log("\n" + "=".repeat(80) + "\n");
    
    // SCENARIO 3: Concentration vs Diversification
    console.log("📊 SCENARIO 3: Concentration vs Diversification");
    console.log("-".repeat(80));
    console.log("Testing: One 25% position vs Five 5% positions");
    console.log();
    
    const [concentrated, diversified] = simulateConcentrationVsDiversification();
    
    console.log("Results:");
    console.log(`\n  CONCENTRATED (One 25% position):`);
    console.log(`    Median Return: ${concentrated.medianReturn.toFixed(1)}%`);
    console.log(`    Median Drawdown: ${concentrated.medianDrawdown.toFixed(1)}%`);
    console.log(`    Max Drawdown: ${concentrated.maxDrawdown.toFixed(1)}%`);
    console.log(`    Win Rate: ${(concentrated.winRate*100).toFixed(1)}%`);
    console.log(`    25th-75th Percentile: ${concentrated.p25Return.toFixed(1)}% - ${concentrated.p75Return.toFixed(1)}%`);
    
    console.log(`\n  DIVERSIFIED (Five 5% positions):`);
    console.log(`    Median Return: ${diversified.medianReturn.toFixed(1)}%`);
    console.log(`    Median Drawdown: ${diversified.medianDrawdown.toFixed(1)}%`);
    console.log(`    Max Drawdown: ${diversified.maxDrawdown.toFixed(1)}%`);
    console.log(`    Win Rate: ${(diversified.winRate*100).toFixed(1)}%`);
    console.log(`    25th-75th Percentile: ${diversified.p25Return.toFixed(1)}% - ${diversified.p75Return.toFixed(1)}%`);
    
    console.log("\n" + "=".repeat(80) + "\n");
    
    // SCENARIO 4: Rebalancing Rules
    console.log("📊 SCENARIO 4: Rebalancing Strategies");
    console.log("-".repeat(80));
    console.log("Testing: When to take profits on winners");
    console.log();
    
    const rebalanceResults = simulateRebalancingStrategies();
    
    console.log("Results:");
    for (const [strategyName, results] of Object.entries(rebalanceResults)) {
        console.log(`\n  ${strategyName}:`);
        console.log(`    Median Return: ${results.medianReturn.toFixed(1)}%`);
        console.log(`    Median Drawdown: ${results.medianDrawdown.toFixed(1)}%`);
        console.log(`    Max Drawdown: ${results.maxDrawdown.toFixed(1)}%`);
        console.log(`    Win Rate: ${(results.winRate*100).toFixed(1)}%`);
        console.log(`    25th-75th Percentile: ${results.p25Return.toFixed(1)}% - ${results.p75Return.toFixed(1)}%`);
    }
    
    console.log("\n" + "=".repeat(80) + "\n");
    
    // Save results
    const allResults = {
        correlation_scenarios: {
            high: highCorr,
            moderate: moderateCorr,
            low: lowCorr
        },
        hedge_strategy: hedgeResults,
        concentration_vs_diversification: {
            concentrated,
            diversified
        },
        rebalancing_strategies: rebalanceResults,
        simulation_params: {
            starting_capital: STARTING_BANKROLL,
            simulation_days: SIMULATION_DAYS,
            num_simulations: NUM_SIMULATIONS,
            win_rate: WIN_RATE_BASE,
            reward_risk_ratio: REWARD_RISK_RATIO,
            max_single_position: MAX_SINGLE_POSITION_PCT,
            max_total_exposure: MAX_TOTAL_EXPOSURE_PCT,
            min_cash_reserve: MIN_CASH_RESERVE_PCT
        }
    };
    
    fs.writeFileSync('backtest_portfolio_results.json', JSON.stringify(allResults, null, 2));
    
    console.log("✅ Detailed results saved to backtest_portfolio_results.json");
    console.log();
}

// Set seed for reproducibility
Math.seedrandom = function(seed) {
    let state = seed;
    Math.random = function() {
        const x = Math.sin(state++) * 10000;
        return x - Math.floor(x);
    };
};

Math.seedrandom(42);

main();
