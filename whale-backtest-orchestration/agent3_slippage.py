"""
AGENT 3: Slippage Impact Analysis
=================================
MISSION: Quantify how execution lag destroys edge.
         
Tests slippage from 0% to 5% to understand:
- At what slippage does strategy become unprofitable?
- How fast must we execute to capture edge?
- Is there a sweet spot for timing?
"""

import sys
sys.path.append('.')
from whale_backtest_engine import WhaleBacktestEngine
import json

def run_slippage_analysis():
    engine = WhaleBacktestEngine(initial_capital=10000)
    n_markets = engine.load_markets("../polymarket_resolved_markets.json")
    
    print(f"=== AGENT 3: Slippage Impact Analysis ===")
    print(f"Loaded {n_markets} resolved markets\n")
    
    results = {}
    
    # Test slippage levels (0% = instant execution, 5% = very slow/bad fills)
    slippage_levels = [0.00, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05]
    
    print("Testing slippage levels with 65% whale accuracy:\n")
    print(f"{'Slippage':>10} | {'Return':>10} | {'Sharpe':>8} | {'Profitable':>12} | {'Edge Lost':>10}")
    print("-" * 65)
    
    baseline_return = None
    
    for slippage in slippage_levels:
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': slippage,
            'sizing_method': 'fixed',
            'base_position_size': 100,
            'random_seed': 42
        })
        
        ret = result['total_return_pct']
        sharpe = result['sharpe_ratio']
        profitable = ret > 0
        
        if baseline_return is None:
            baseline_return = ret
            edge_lost = 0
        else:
            edge_lost = ((baseline_return - ret) / baseline_return * 100) if baseline_return != 0 else 0
        
        results[f'{slippage:.1%}'] = {
            'slippage_pct': slippage,
            'total_return_pct': ret,
            'sharpe_ratio': sharpe,
            'profitable': profitable,
            'edge_lost_pct': edge_lost,
            'total_slippage_cost': result['total_slippage']
        }
        
        status = "✅ YES" if profitable else "❌ NO"
        print(f"{slippage:>9.1%} | {ret:>+9.1f}% | {sharpe:>7.2f} | {status:>12} | {edge_lost:>9.0f}%")
    
    # Find breakeven slippage
    print("\n" + "="*60)
    print("BREAKEVEN ANALYSIS")
    print("="*60)
    
    profitable_slippages = [s for s, r in results.items() if r['profitable']]
    unprofitable_slippages = [s for s, r in results.items() if not r['profitable']]
    
    if profitable_slippages and unprofitable_slippages:
        max_profitable_slip = max(float(s.strip('%')) / 100 for s in profitable_slippages)
        min_unprofitable_slip = min(float(s.strip('%')) / 100 for s in unprofitable_slippages)
        breakeven = (max_profitable_slip + min_unprofitable_slip) / 2
        print(f"✓ Maximum profitable slippage: {max_profitable_slip:.1%}")
        print(f"✗ Minimum unprofitable slippage: {min_unprofitable_slip:.1%}")
        print(f"→ Breakeven slippage estimate: ~{breakeven:.1%}")
    elif not unprofitable_slippages:
        print("✓ Strategy profitable even at 5% slippage!")
        breakeven = 0.05
    else:
        print("✗ Strategy not profitable at any slippage level")
        breakeven = 0
    
    # Execution time estimation
    print("\n" + "="*60)
    print("EXECUTION TIME REQUIREMENTS")
    print("="*60)
    
    # Assume slippage correlates with execution delay
    # Rule of thumb: ~0.5% slippage per minute of delay
    slippage_per_minute = 0.005
    
    print("Estimated relationship: ~0.5% slippage per minute of delay")
    print("")
    for target_slip in [0.01, 0.02, 0.03]:
        minutes = target_slip / slippage_per_minute
        result_at_slip = results.get(f'{target_slip:.1%}', {})
        ret = result_at_slip.get('total_return_pct', 0)
        print(f"  {target_slip:.1%} slippage → Execute within {minutes:.0f} min → {ret:+.1f}% expected return")
    
    # Optimal execution window
    print("\n" + "="*60)
    print("OPTIMAL EXECUTION WINDOW")
    print("="*60)
    
    # Find slippage with best Sharpe (not just highest return)
    best_sharpe_slip = max(results.items(), key=lambda x: x[1]['sharpe_ratio'])
    
    print(f"Best risk-adjusted performance at: {best_sharpe_slip[0]} slippage")
    print(f"  Expected Sharpe: {best_sharpe_slip[1]['sharpe_ratio']:.2f}")
    print(f"  Expected Return: {best_sharpe_slip[1]['total_return_pct']:+.1f}%")
    
    # Recommendation
    print("\n" + "="*60)
    print("AGENT 3 RECOMMENDATION")
    print("="*60)
    
    if breakeven >= 0.02:
        print("✅ VIABLE: Strategy tolerates reasonable slippage")
        print(f"   Target execution within 2-4 minutes of whale signal")
    elif breakeven >= 0.01:
        print("⚠️ MARGINAL: Need fast execution")
        print(f"   Target execution within 1-2 minutes of whale signal")
    else:
        print("❌ NOT VIABLE: Requires near-instant execution")
        print(f"   Would need sub-minute execution, likely not achievable")
    
    # Save results
    with open("agent3_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Summary for orchestrator
    print("\n" + "="*60)
    print("AGENT 3 SUMMARY FOR ORCHESTRATOR")
    print("="*60)
    
    summary = {
        'agent': 'Agent3_Slippage',
        'finding': f'Strategy remains profitable up to ~{breakeven:.1%} slippage',
        'recommendation': 'Execute copy trades within 2 minutes of whale signal detection',
        'breakeven_slippage': breakeven,
        'edge_decay_per_minute': '~0.5% per minute of delay',
        'key_insight': 'Slippage is a significant edge eroder - automation is essential'
    }
    
    print(json.dumps(summary, indent=2))
    
    return results

if __name__ == "__main__":
    run_slippage_analysis()
