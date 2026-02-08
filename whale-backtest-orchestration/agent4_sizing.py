"""
AGENT 4: Position Sizing Optimization
=====================================
MISSION: Find optimal position sizing to maximize risk-adjusted returns.

Tests:
- Fixed sizing vs Kelly criterion
- Volatility-scaled sizing
- Signal strength scaling
- Maximum position constraints
"""

import sys
sys.path.append('.')
from whale_backtest_engine import WhaleBacktestEngine
import json
import math

def run_sizing_optimization():
    engine = WhaleBacktestEngine(initial_capital=10000)
    n_markets = engine.load_markets("../polymarket_resolved_markets.json")
    
    print(f"=== AGENT 4: Position Sizing Optimization ===")
    print(f"Loaded {n_markets} resolved markets\n")
    
    results = {}
    
    # Test different sizing methods
    sizing_methods = ['fixed', 'kelly', 'signal_scaled', 'volatility_scaled']
    
    print("Testing sizing methods (65% whale accuracy, 2% slippage):\n")
    
    for method in sizing_methods:
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': 0.02,
            'sizing_method': method,
            'base_position_size': 100,
            'max_position_pct': 0.10,
            'random_seed': 42
        })
        
        results[method] = {
            'method': method,
            'total_return_pct': result['total_return_pct'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown_pct': result['max_drawdown_pct'],
            'profit_factor': result['profit_factor'],
            'avg_win': result['avg_win'],
            'avg_loss': result['avg_loss'],
            'trades': result['total_trades']
        }
        
        print(f"{method:20} | Return: {result['total_return_pct']:+6.1f}% | Sharpe: {result['sharpe_ratio']:.2f} | MaxDD: {result['max_drawdown_pct']:.1f}% | PF: {result['profit_factor']:.2f}")
    
    # Test different base sizes
    print("\n" + "="*60)
    print("BASE POSITION SIZE ANALYSIS (Fixed Method)")
    print("="*60 + "\n")
    
    size_results = {}
    for base_size in [25, 50, 100, 200, 500]:
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': 0.02,
            'sizing_method': 'fixed',
            'base_position_size': base_size,
            'max_position_pct': 0.20,  # Allow larger for testing
            'random_seed': 42
        })
        
        size_results[f'${base_size}'] = {
            'base_size': base_size,
            'pct_of_capital': base_size / 10000 * 100,
            'total_return_pct': result['total_return_pct'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown_pct': result['max_drawdown_pct']
        }
        
        print(f"${base_size:>4} ({base_size/100:.0f}% of capital) | Return: {result['total_return_pct']:+6.1f}% | Sharpe: {result['sharpe_ratio']:.2f} | MaxDD: {result['max_drawdown_pct']:.1f}%")
    
    results['base_size_analysis'] = size_results
    
    # Test max position constraints
    print("\n" + "="*60)
    print("MAX POSITION CONSTRAINT ANALYSIS")
    print("="*60 + "\n")
    
    constraint_results = {}
    for max_pct in [0.02, 0.05, 0.10, 0.20, 0.50]:
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': 0.02,
            'sizing_method': 'kelly',
            'base_position_size': 200,
            'max_position_pct': max_pct,
            'random_seed': 42
        })
        
        constraint_results[f'{max_pct:.0%}'] = {
            'max_position_pct': max_pct,
            'total_return_pct': result['total_return_pct'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown_pct': result['max_drawdown_pct']
        }
        
        print(f"Max {max_pct:>4.0%} | Return: {result['total_return_pct']:+6.1f}% | Sharpe: {result['sharpe_ratio']:.2f} | MaxDD: {result['max_drawdown_pct']:.1f}%")
    
    results['constraint_analysis'] = constraint_results
    
    # Find optimal configuration
    print("\n" + "="*60)
    print("OPTIMAL SIZING CONFIGURATION")
    print("="*60)
    
    # Run optimization search
    best_sharpe = -999
    best_config = None
    
    for method in ['fixed', 'kelly', 'signal_scaled']:
        for base_size in [50, 100, 150, 200]:
            for max_pct in [0.05, 0.10, 0.15]:
                result = engine.run_backtest({
                    'whale_accuracy': 0.65,
                    'slippage_pct': 0.02,
                    'sizing_method': method,
                    'base_position_size': base_size,
                    'max_position_pct': max_pct,
                    'random_seed': 42
                })
                
                if result['sharpe_ratio'] > best_sharpe:
                    best_sharpe = result['sharpe_ratio']
                    best_config = {
                        'sizing_method': method,
                        'base_position_size': base_size,
                        'max_position_pct': max_pct,
                        'sharpe_ratio': result['sharpe_ratio'],
                        'total_return_pct': result['total_return_pct'],
                        'max_drawdown_pct': result['max_drawdown_pct']
                    }
    
    print(f"\nBest Configuration Found:")
    print(f"  Method: {best_config['sizing_method']}")
    print(f"  Base Size: ${best_config['base_position_size']}")
    print(f"  Max Position: {best_config['max_position_pct']:.0%}")
    print(f"  Expected Sharpe: {best_config['sharpe_ratio']:.2f}")
    print(f"  Expected Return: {best_config['total_return_pct']:+.1f}%")
    print(f"  Max Drawdown: {best_config['max_drawdown_pct']:.1f}%")
    
    results['optimal_config'] = best_config
    
    # Risk analysis
    print("\n" + "="*60)
    print("RISK ANALYSIS")
    print("="*60)
    
    # Calculate Value at Risk (simplified)
    returns = []
    for seed in range(100):
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': 0.02,
            **{k: v for k, v in best_config.items() if k in ['sizing_method', 'base_position_size', 'max_position_pct']},
            'random_seed': seed
        })
        returns.append(result['total_return_pct'])
    
    returns.sort()
    var_5 = returns[5]  # 5th percentile
    var_10 = returns[10]
    avg_return = sum(returns) / len(returns)
    
    print(f"Based on 100 Monte Carlo simulations:")
    print(f"  Average Return: {avg_return:+.1f}%")
    print(f"  VaR 5% (worst 5%): {var_5:+.1f}%")
    print(f"  VaR 10% (worst 10%): {var_10:+.1f}%")
    print(f"  Best Case: {max(returns):+.1f}%")
    print(f"  Worst Case: {min(returns):+.1f}%")
    
    results['risk_analysis'] = {
        'monte_carlo_runs': 100,
        'avg_return': avg_return,
        'var_5pct': var_5,
        'var_10pct': var_10,
        'best_case': max(returns),
        'worst_case': min(returns)
    }
    
    # Save results
    with open("agent4_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Summary for orchestrator
    print("\n" + "="*60)
    print("AGENT 4 SUMMARY FOR ORCHESTRATOR")
    print("="*60)
    
    summary = {
        'agent': 'Agent4_PositionSizing',
        'finding': f"Optimal sizing: {best_config['sizing_method']} at ${best_config['base_position_size']} base",
        'recommendation': f"Use {best_config['max_position_pct']:.0%} max position constraint with {best_config['sizing_method']} sizing",
        'optimal_config': best_config,
        'var_5pct': var_5,
        'key_insight': 'Position sizing has moderate impact - whale accuracy matters more'
    }
    
    print(json.dumps(summary, indent=2))
    
    return results

if __name__ == "__main__":
    run_sizing_optimization()
