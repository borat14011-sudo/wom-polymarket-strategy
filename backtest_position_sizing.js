// Position Sizing Backtest Simulation
const fs = require('fs');

// Parameters
const STARTING_BANKROLL = 100;
const NUM_TRADES = 100;
const WIN_RATE = 0.55;
const REWARD_RISK_RATIO = 1.5;
const NUM_SIMULATIONS = 1000;

// Calculate Kelly Criterion
// Kelly formula: f* = (bp - q) / b
const p = WIN_RATE;
const q = 1 - WIN_RATE;
const b = REWARD_RISK_RATIO;
const kelly_fraction = (b * p - q) / b;

console.log('Kelly Criterion Calculation:');
console.log(`Win Rate: ${WIN_RATE * 100}%`);
console.log(`Reward/Risk: ${REWARD_RISK_RATIO}:1`);
console.log(`Full Kelly: ${(kelly_fraction * 100).toFixed(2)}%`);
console.log(`Half Kelly: ${(kelly_fraction * 0.5 * 100).toFixed(2)}%`);
console.log(`Quarter Kelly: ${(kelly_fraction * 0.25 * 100).toFixed(2)}%`);
console.log();

function median(arr) {
    const sorted = [...arr].sort((a, b) => a - b);
    const mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

function percentile(arr, p) {
    const sorted = [...arr].sort((a, b) => a - b);
    const index = (p / 100) * (sorted.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    const weight = index % 1;
    return sorted[lower] * (1 - weight) + sorted[upper] * weight;
}

function mean(arr) {
    return arr.reduce((a, b) => a + b, 0) / arr.length;
}

function std(arr) {
    const avg = mean(arr);
    const squareDiffs = arr.map(value => Math.pow(value - avg, 2));
    return Math.sqrt(mean(squareDiffs));
}

function simulateStrategy(strategyName, positionSizeFunc, numSims = NUM_SIMULATIONS) {
    const allResults = [];
    
    for (let sim = 0; sim < numSims; sim++) {
        let bankroll = STARTING_BANKROLL;
        const equityCurve = [bankroll];
        let maxDrawdown = 0;
        let peak = bankroll;
        
        for (let trade = 0; trade < NUM_TRADES; trade++) {
            // Determine win or loss
            const isWin = Math.random() < WIN_RATE;
            
            // Calculate position size
            const positionSize = positionSizeFunc(bankroll);
            
            if (isWin) {
                const profit = positionSize * REWARD_RISK_RATIO;
                bankroll += profit;
            } else {
                const loss = positionSize;
                bankroll -= loss;
            }
            
            // Prevent negative bankroll
            if (bankroll <= 0) {
                bankroll = 0;
                equityCurve.push(bankroll);
                break;
            }
            
            equityCurve.push(bankroll);
            
            // Track drawdown
            if (bankroll > peak) {
                peak = bankroll;
            }
            const drawdown = (peak - bankroll) / peak * 100;
            maxDrawdown = Math.max(maxDrawdown, drawdown);
        }
        
        allResults.push({
            finalBankroll: bankroll,
            equityCurve: equityCurve,
            maxDrawdown: maxDrawdown,
            blown: bankroll === 0
        });
    }
    
    return allResults;
}

// Define position sizing strategies
const strategies = {
    'Fixed $4': (bankroll) => 4,
    'Fixed $5': (bankroll) => 5,
    'Full Kelly (25%)': (bankroll) => bankroll * kelly_fraction,
    'Half Kelly (12.5%)': (bankroll) => bankroll * kelly_fraction * 0.5,
    'Quarter Kelly (6.25%)': (bankroll) => bankroll * kelly_fraction * 0.25,
};

// Run simulations
console.log('Running simulations...');
const results = {};

for (const [strategyName, positionFunc] of Object.entries(strategies)) {
    console.log(`Simulating ${strategyName}...`);
    results[strategyName] = simulateStrategy(strategyName, positionFunc);
}

// Analyze results
console.log('\n' + '='.repeat(80));
console.log('POSITION SIZING BACKTEST RESULTS');
console.log('='.repeat(80));
console.log(`Simulations: ${NUM_SIMULATIONS} runs of ${NUM_TRADES} trades each`);
console.log(`Win Rate: ${WIN_RATE * 100}%`);
console.log(`Reward/Risk: ${REWARD_RISK_RATIO}:1`);
console.log(`Starting Bankroll: $${STARTING_BANKROLL}`);
console.log('='.repeat(80));
console.log();

const summary = {};

for (const [strategyName, sims] of Object.entries(results)) {
    const finalBankrolls = sims.map(s => s.finalBankroll);
    const maxDrawdowns = sims.map(s => s.maxDrawdown);
    const blownCount = sims.filter(s => s.blown).length;
    
    // Calculate statistics
    const medianFinal = median(finalBankrolls);
    const meanFinal = mean(finalBankrolls);
    const minFinal = Math.min(...finalBankrolls);
    const maxFinal = Math.max(...finalBankrolls);
    const stdFinal = std(finalBankrolls);
    
    const medianDD = median(maxDrawdowns);
    const maxDD = Math.max(...maxDrawdowns);
    
    // Calculate percentiles
    const p25 = percentile(finalBankrolls, 25);
    const p75 = percentile(finalBankrolls, 75);
    
    // Return percentage
    const returnPct = ((medianFinal / STARTING_BANKROLL) - 1) * 100;
    
    summary[strategyName] = {
        medianFinal,
        meanFinal,
        minFinal,
        maxFinal,
        stdFinal,
        p25,
        p75,
        medianDD,
        maxDD,
        blownCount,
        blownPct: (blownCount / NUM_SIMULATIONS) * 100,
        returnPct
    };
    
    console.log(`📊 ${strategyName}`);
    console.log(`   Final Bankroll (Median): $${medianFinal.toFixed(2)}`);
    console.log(`   Final Bankroll (Mean):   $${meanFinal.toFixed(2)}`);
    console.log(`   Range: $${minFinal.toFixed(2)} - $${maxFinal.toFixed(2)}`);
    console.log(`   25th-75th Percentile: $${p25.toFixed(2)} - $${p75.toFixed(2)}`);
    console.log(`   Std Dev: $${stdFinal.toFixed(2)}`);
    console.log(`   Return: ${returnPct.toFixed(1)}%`);
    console.log(`   Median Max Drawdown: ${medianDD.toFixed(1)}%`);
    console.log(`   Worst Drawdown: ${maxDD.toFixed(1)}%`);
    console.log(`   Blown Accounts: ${blownCount}/${NUM_SIMULATIONS} (${(blownCount/NUM_SIMULATIONS*100).toFixed(1)}%)`);
    console.log();
}

// Find best strategies
const entries = Object.entries(summary);
const bestReturn = entries.reduce((a, b) => a[1].medianFinal > b[1].medianFinal ? a : b);
const safestDD = entries.reduce((a, b) => a[1].medianDD < b[1].medianDD ? a : b);

console.log('='.repeat(80));
console.log('ANALYSIS');
console.log('='.repeat(80));
console.log(`🏆 Highest Median Return: ${bestReturn[0]} ($${bestReturn[1].medianFinal.toFixed(2)})`);
console.log(`🛡️  Lowest Median Drawdown: ${safestDD[0]} (${safestDD[1].medianDD.toFixed(1)}%)`);
console.log();

// Risk-adjusted return
console.log('Risk-Adjusted Performance (Return/Volatility):');
for (const [strategyName, stats] of Object.entries(summary)) {
    if (stats.stdFinal > 0) {
        const riskAdj = (stats.medianFinal - STARTING_BANKROLL) / stats.stdFinal;
        console.log(`   ${strategyName}: ${riskAdj.toFixed(3)}`);
    }
}

// Sample equity curves
console.log('\n' + '='.repeat(80));
console.log('SAMPLE EQUITY CURVES (Single Run)');
console.log('='.repeat(80));

// Set seed for reproducibility
let seed = 42;
function seededRandom() {
    seed = (seed * 9301 + 49297) % 233280;
    return seed / 233280;
}

for (const [strategyName, positionFunc] of Object.entries(strategies)) {
    seed = 42; // Reset seed for each strategy
    let bankroll = STARTING_BANKROLL;
    const equity = [bankroll];
    
    for (let trade = 0; trade < NUM_TRADES; trade++) {
        const isWin = seededRandom() < WIN_RATE;
        const positionSize = positionFunc(bankroll);
        
        if (isWin) {
            bankroll += positionSize * REWARD_RISK_RATIO;
        } else {
            bankroll -= positionSize;
        }
        
        if (bankroll <= 0) {
            bankroll = 0;
            equity.push(bankroll);
            break;
        }
        
        equity.push(bankroll);
    }
    
    // Print every 10th trade
    let output = `\n${strategyName}:\n  Start: $${STARTING_BANKROLL.toFixed(2)}`;
    for (let i = 10; i <= Math.min(equity.length - 1, NUM_TRADES); i += 10) {
        output += ` → T${i}: $${equity[i].toFixed(2)}`;
    }
    output += ` → Final: $${equity[equity.length - 1].toFixed(2)}`;
    console.log(output);
}

// Save results
fs.writeFileSync('backtest_results.json', JSON.stringify(summary, null, 2));
console.log('\n✅ Detailed results saved to backtest_results.json');
