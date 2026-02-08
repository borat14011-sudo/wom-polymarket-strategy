import random
import numpy as np
import json

# Parameters
STARTING_BANKROLL = 100
NUM_TRADES = 100
WIN_RATE = 0.55
REWARD_RISK_RATIO = 1.5
NUM_SIMULATIONS = 1000  # Run multiple simulations for robustness

# Calculate Kelly Criterion
# Kelly formula: f* = (bp - q) / b
# b = reward/risk ratio, p = win probability, q = loss probability
p = WIN_RATE
q = 1 - WIN_RATE
b = REWARD_RISK_RATIO
kelly_fraction = (b * p - q) / b

print(f"Kelly Criterion Calculation:")
print(f"Win Rate: {WIN_RATE*100}%")
print(f"Reward/Risk: {REWARD_RISK_RATIO}:1")
print(f"Full Kelly: {kelly_fraction*100:.2f}%")
print(f"Half Kelly: {kelly_fraction*0.5*100:.2f}%")
print(f"Quarter Kelly: {kelly_fraction*0.25*100:.2f}%")
print()

def simulate_strategy(strategy_name, position_size_func, num_sims=NUM_SIMULATIONS):
    """Simulate a position sizing strategy over multiple runs"""
    all_results = []
    
    for sim in range(num_sims):
        bankroll = STARTING_BANKROLL
        equity_curve = [bankroll]
        max_drawdown = 0
        peak = bankroll
        
        for trade in range(NUM_TRADES):
            # Determine win or loss
            is_win = random.random() < WIN_RATE
            
            # Calculate position size
            position_size = position_size_func(bankroll)
            
            if is_win:
                profit = position_size * REWARD_RISK_RATIO
                bankroll += profit
            else:
                loss = position_size
                bankroll -= loss
            
            # Prevent negative bankroll (blown account)
            if bankroll <= 0:
                bankroll = 0
                equity_curve.append(bankroll)
                break
            
            equity_curve.append(bankroll)
            
            # Track drawdown
            if bankroll > peak:
                peak = bankroll
            drawdown = (peak - bankroll) / peak * 100
            max_drawdown = max(max_drawdown, drawdown)
        
        all_results.append({
            'final_bankroll': bankroll,
            'equity_curve': equity_curve,
            'max_drawdown': max_drawdown,
            'blown': bankroll == 0
        })
    
    return all_results

# Define position sizing strategies
strategies = {
    'Fixed $4': lambda bankroll: 4,
    'Fixed $5': lambda bankroll: 5,
    'Full Kelly (25%)': lambda bankroll: bankroll * kelly_fraction,
    'Half Kelly (12.5%)': lambda bankroll: bankroll * kelly_fraction * 0.5,
    'Quarter Kelly (6.25%)': lambda bankroll: bankroll * kelly_fraction * 0.25,
}

# Run simulations
print("Running simulations...")
results = {}

for strategy_name, position_func in strategies.items():
    print(f"Simulating {strategy_name}...")
    results[strategy_name] = simulate_strategy(strategy_name, position_func)

# Analyze results
print("\n" + "="*80)
print("POSITION SIZING BACKTEST RESULTS")
print("="*80)
print(f"Simulations: {NUM_SIMULATIONS} runs of {NUM_TRADES} trades each")
print(f"Win Rate: {WIN_RATE*100}%")
print(f"Reward/Risk: {REWARD_RISK_RATIO}:1")
print(f"Starting Bankroll: ${STARTING_BANKROLL}")
print("="*80)
print()

summary = {}

for strategy_name, sims in results.items():
    final_bankrolls = [s['final_bankroll'] for s in sims]
    max_drawdowns = [s['max_drawdown'] for s in sims]
    blown_count = sum(1 for s in sims if s['blown'])
    
    # Calculate statistics
    median_final = np.median(final_bankrolls)
    mean_final = np.mean(final_bankrolls)
    min_final = np.min(final_bankrolls)
    max_final = np.max(final_bankrolls)
    std_final = np.std(final_bankrolls)
    
    median_dd = np.median(max_drawdowns)
    max_dd = np.max(max_drawdowns)
    
    # Calculate percentiles
    p25 = np.percentile(final_bankrolls, 25)
    p75 = np.percentile(final_bankrolls, 75)
    
    # CAGR (assuming 100 trades = 1 year for comparison)
    cagr = ((median_final / STARTING_BANKROLL) - 1) * 100
    
    summary[strategy_name] = {
        'median_final': median_final,
        'mean_final': mean_final,
        'min_final': min_final,
        'max_final': max_final,
        'std_final': std_final,
        'p25': p25,
        'p75': p75,
        'median_dd': median_dd,
        'max_dd': max_dd,
        'blown_count': blown_count,
        'blown_pct': (blown_count / NUM_SIMULATIONS) * 100,
        'cagr': cagr
    }
    
    print(f"📊 {strategy_name}")
    print(f"   Final Bankroll (Median): ${median_final:.2f}")
    print(f"   Final Bankroll (Mean):   ${mean_final:.2f}")
    print(f"   Range: ${min_final:.2f} - ${max_final:.2f}")
    print(f"   25th-75th Percentile: ${p25:.2f} - ${p75:.2f}")
    print(f"   Std Dev: ${std_final:.2f}")
    print(f"   Return: {cagr:.1f}%")
    print(f"   Median Max Drawdown: {median_dd:.1f}%")
    print(f"   Worst Drawdown: {max_dd:.1f}%")
    print(f"   Blown Accounts: {blown_count}/{NUM_SIMULATIONS} ({(blown_count/NUM_SIMULATIONS)*100:.1f}%)")
    print()

# Find best strategy
best_strategy = max(summary.items(), key=lambda x: x[1]['median_final'])
safest_strategy = min(summary.items(), key=lambda x: x[1]['median_dd'])

print("="*80)
print("ANALYSIS")
print("="*80)
print(f"🏆 Highest Median Return: {best_strategy[0]} (${best_strategy[1]['median_final']:.2f})")
print(f"🛡️  Lowest Median Drawdown: {safest_strategy[0]} ({safest_strategy[1]['median_dd']:.1f}%)")
print()

# Risk-adjusted return (Sharpe-like ratio)
print("Risk-Adjusted Performance (Return/Volatility):")
for strategy_name, stats in summary.items():
    if stats['std_final'] > 0:
        risk_adj = (stats['median_final'] - STARTING_BANKROLL) / stats['std_final']
        print(f"   {strategy_name}: {risk_adj:.3f}")

# Sample equity curve from one simulation for visualization
print("\n" + "="*80)
print("SAMPLE EQUITY CURVES (Single Run)")
print("="*80)

random.seed(42)  # For reproducibility
for strategy_name, position_func in strategies.items():
    bankroll = STARTING_BANKROLL
    equity = [bankroll]
    
    for trade in range(NUM_TRADES):
        is_win = random.random() < WIN_RATE
        position_size = position_func(bankroll)
        
        if is_win:
            bankroll += position_size * REWARD_RISK_RATIO
        else:
            bankroll -= position_size
        
        if bankroll <= 0:
            bankroll = 0
            equity.append(bankroll)
            break
        
        equity.append(bankroll)
    
    # Print every 10th trade
    print(f"\n{strategy_name}:")
    print(f"  Start: ${STARTING_BANKROLL:.2f}", end="")
    for i in range(10, min(len(equity), NUM_TRADES+1), 10):
        print(f" → T{i}: ${equity[i]:.2f}", end="")
    print(f" → Final: ${equity[-1]:.2f}")

# Save detailed results
with open('backtest_results.json', 'w') as f:
    # Convert numpy types to native Python for JSON serialization
    json_summary = {}
    for k, v in summary.items():
        json_summary[k] = {kk: float(vv) if isinstance(vv, np.floating) else vv 
                          for kk, vv in v.items()}
    json.dump(json_summary, f, indent=2)

print("\n✅ Detailed results saved to backtest_results.json")
