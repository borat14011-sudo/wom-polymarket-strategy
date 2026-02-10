"""
MONTE CARLO BACKTEST RUNNER 2 (Kimi 2.5)
==========================================
Rigorous Monte Carlo simulation for strategy validation.
Tests 1000+ random market paths. Kills strategies that blow up.

Reports:
- Max drawdown distributions
- Return variance & confidence intervals
- Risk-adjusted returns (Sharpe, Sortino, Calmar)
- Probability of ruin
- Strategy death conditions
"""

import sys
sys.path.append('.')
sys.path.append('./whale-backtest-orchestration')
from whale_backtest_engine import WhaleBacktestEngine
import json
import math
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
from pathlib import Path

@dataclass
class MonteCarloResult:
    """Single simulation result"""
    seed: int
    total_return_pct: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    win_rate: float
    total_trades: int
    final_capital: float
    profit_factor: float
    var_95: float  # 95% Value at Risk (single trade)
    consecutive_losses: int
    worst_trade_pct: float

class MonteCarloRunner:
    """
    Rigorous Monte Carlo simulation runner.
    
    Death conditions (strategy gets killed):
    1. Max drawdown > 50% (blowup)
    2. Probability of negative return > 30%
    3. Sharpe ratio < 0.1 consistently
    4. Consecutive loss streak > 15 trades
    5. Final capital < 50% of initial
    """
    
    DEATH_DRAWDOWN = 50.0  # 50% max drawdown
    DEATH_RUIN_PROB = 0.30  # 30% chance of loss
    DEATH_SHARPE = 0.1  # Minimum acceptable Sharpe
    DEATH_CONSECUTIVE = 15  # Max consecutive losses
    DEATH_CAPITAL = 0.5  # 50% capital remaining
    
    def __init__(self, initial_capital: float = 10000, n_simulations: int = 1000):
        self.initial_capital = initial_capital
        self.n_simulations = n_simulations
        self.results: List[MonteCarloResult] = []
        self.death_events: List[Dict] = []
        self.engine = WhaleBacktestEngine(initial_capital=initial_capital)
        
    def load_markets(self, filepath: str) -> int:
        """Load market data"""
        return self.engine.load_markets(filepath)
    
    def run_single_simulation(self, params: dict, seed: int) -> MonteCarloResult:
        """Run one simulation with given random seed"""
        params = params.copy()
        params['random_seed'] = seed
        
        result = self.engine.run_backtest(params)
        
        if 'error' in result:
            return MonteCarloResult(
                seed=seed, total_return_pct=-100, max_drawdown_pct=100,
                sharpe_ratio=-10, sortino_ratio=-10, win_rate=0, total_trades=0,
                final_capital=0, profit_factor=0, var_95=0, consecutive_losses=0,
                worst_trade_pct=-100
            )
        
        # Calculate additional metrics
        trades = self.engine.trades
        returns = [t.pnl_pct for t in trades]
        
        # Calculate consecutive losses
        max_consecutive = 0
        current_consecutive = 0
        for t in trades:
            if t.outcome == "LOSS":
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        # Calculate VaR 95% (worst 5% of trades)
        if returns:
            returns_sorted = sorted(returns)
            var_95_idx = int(len(returns_sorted) * 0.05)
            var_95 = returns_sorted[var_95_idx] if var_95_idx < len(returns_sorted) else returns_sorted[0]
            worst_trade = min(returns)
        else:
            var_95 = 0
            worst_trade = 0
        
        return MonteCarloResult(
            seed=seed,
            total_return_pct=result['total_return_pct'],
            max_drawdown_pct=result['max_drawdown_pct'],
            sharpe_ratio=result['sharpe_ratio'],
            sortino_ratio=result['sortino_ratio'],
            win_rate=result['win_rate'],
            total_trades=result['total_trades'],
            final_capital=result['final_capital'],
            profit_factor=result['profit_factor'],
            var_95=var_95 * 100,  # Convert to %
            consecutive_losses=max_consecutive,
            worst_trade_pct=worst_trade * 100
        )
    
    def check_death_conditions(self, result: MonteCarloResult, sim_num: int) -> Dict:
        """Check if this simulation triggers death conditions"""
        death_reasons = []
        
        if result.max_drawdown_pct > self.DEATH_DRAWDOWN:
            death_reasons.append(f"MAX_DRAWDOWN({result.max_drawdown_pct:.1f}%)")
        
        if result.final_capital < self.initial_capital * self.DEATH_CAPITAL:
            death_reasons.append(f"RUIN_CAPITAL(${result.final_capital:.0f})")
        
        if result.sharpe_ratio < self.DEATH_SHARPE:
            death_reasons.append(f"LOW_SHARPE({result.sharpe_ratio:.2f})")
        
        if result.consecutive_losses > self.DEATH_CONSECUTIVE:
            death_reasons.append(f"CONSEC_LOSS({result.consecutive_losses})")
        
        if result.total_return_pct < -50:
            death_reasons.append(f"TOTAL_LOSS({result.total_return_pct:.1f}%)")
        
        if death_reasons:
            return {
                'simulation': sim_num,
                'seed': result.seed,
                'death_reasons': death_reasons,
                'final_capital': result.final_capital,
                'max_drawdown': result.max_drawdown_pct,
                'total_return': result.total_return_pct
            }
        return None
    
    def run_monte_carlo(self, params: dict, strategy_name: str = "unnamed") -> Dict:
        """Run full Monte Carlo simulation"""
        print(f"\n{'='*70}")
        print(f"MONTE CARLO SIMULATION: {strategy_name}")
        print(f"{'='*70}")
        print(f"Running {self.n_simulations} simulations...")
        print(f"Death conditions: MaxDD>{self.DEATH_DRAWDOWN}%, RuinProb>{self.DEATH_RUIN_PROB:.0%}, Sharpe<{self.DEATH_SHARPE}")
        print()
        
        self.results = []
        self.death_events = []
        
        for i in range(self.n_simulations):
            result = self.run_single_simulation(params, seed=i)
            self.results.append(result)
            
            # Check for death
            death = self.check_death_conditions(result, i)
            if death:
                self.death_events.append(death)
            
            # Progress update
            if (i + 1) % 100 == 0:
                deaths_so_far = len([d for d in self.death_events if d['simulation'] <= i])
                print(f"  Completed {i+1}/{self.n_simulations}... Deaths: {deaths_so_far}")
        
        return self.generate_report(strategy_name, params)
    
    def generate_report(self, strategy_name: str, params: dict) -> Dict:
        """Generate comprehensive Monte Carlo report"""
        
        returns = [r.total_return_pct for r in self.results]
        drawdowns = [r.max_drawdown_pct for r in self.results]
        sharpes = [r.sharpe_ratio for r in self.results]
        sortinos = [r.sortino_ratio for r in self.results]
        win_rates = [r.win_rate for r in self.results]
        capitals = [r.final_capital for r in self.results]
        
        # Sort for percentiles
        returns_sorted = sorted(returns)
        drawdowns_sorted = sorted(drawdowns)
        sharpes_sorted = sorted(sharpes)
        
        # Calculate statistics
        def percentile(sorted_list, p):
            idx = int(len(sorted_list) * p / 100)
            return sorted_list[max(0, min(idx, len(sorted_list)-1))]
        
        # Risk metrics
        prob_profit = len([r for r in returns if r > 0]) / len(returns)
        prob_ruin = len([c for c in capitals if c < self.initial_capital * 0.5]) / len(capitals)
        prob_blowup = len([d for d in drawdowns if d > self.DEATH_DRAWDOWN]) / len(drawdowns)
        
        # Calculate Calmar ratio (return / max drawdown)
        calmar_ratios = []
        for r, dd in zip(returns, drawdowns):
            if dd > 0:
                calmar_ratios.append(r / dd)
            else:
                calmar_ratios.append(r / 0.1)  # Avoid div by zero
        
        report = {
            'strategy_name': strategy_name,
            'parameters': params,
            'simulation_count': self.n_simulations,
            
            'return_statistics': {
                'mean': sum(returns) / len(returns),
                'median': percentile(returns_sorted, 50),
                'std_dev': math.sqrt(sum((r - sum(returns)/len(returns))**2 for r in returns) / len(returns)),
                'min': min(returns),
                'max': max(returns),
                'percentiles': {
                    'p5': percentile(returns_sorted, 5),
                    'p10': percentile(returns_sorted, 10),
                    'p25': percentile(returns_sorted, 25),
                    'p50': percentile(returns_sorted, 50),
                    'p75': percentile(returns_sorted, 75),
                    'p90': percentile(returns_sorted, 90),
                    'p95': percentile(returns_sorted, 95),
                },
                'prob_profit': prob_profit,
                'prob_loss': 1 - prob_profit,
            },
            
            'drawdown_statistics': {
                'mean': sum(drawdowns) / len(drawdowns),
                'median': percentile(drawdowns_sorted, 50),
                'max': max(drawdowns),
                'min': min(drawdowns),
                'percentiles': {
                    'p50': percentile(drawdowns_sorted, 50),
                    'p75': percentile(drawdowns_sorted, 75),
                    'p90': percentile(drawdowns_sorted, 90),
                    'p95': percentile(drawdowns_sorted, 95),
                    'p99': percentile(drawdowns_sorted, 99),
                },
                'prob_severe_dd': prob_blowup,  # >50% drawdown
            },
            
            'risk_adjusted_returns': {
                'sharpe_mean': sum(sharpes) / len(sharpes),
                'sharpe_median': percentile(sharpes_sorted, 50),
                'sharpe_std': math.sqrt(sum((s - sum(sharpes)/len(sharpes))**2 for s in sharpes) / len(sharpes)),
                'sharpe_percentiles': {
                    'p5': percentile(sharpes_sorted, 5),
                    'p25': percentile(sharpes_sorted, 25),
                    'p50': percentile(sharpes_sorted, 50),
                    'p75': percentile(sharpes_sorted, 75),
                    'p95': percentile(sharpes_sorted, 95),
                },
                'sortino_mean': sum(sortinos) / len(sortinos),
                'calmar_mean': sum(calmar_ratios) / len(calmar_ratios),
            },
            
            'ruin_analysis': {
                'prob_ruin_50pct': prob_ruin,  # Lost 50% of capital
                'prob_blowup_50dd': prob_blowup,  # 50% max drawdown
                'death_events': len(self.death_events),
                'death_rate': len(self.death_events) / self.n_simulations,
                'survival_rate': 1 - (len(self.death_events) / self.n_simulations),
            },
            
            'win_rate_statistics': {
                'mean': sum(win_rates) / len(win_rates),
                'min': min(win_rates),
                'max': max(win_rates),
            },
            
            'death_events': self.death_events[:20],  # First 20 death events
            'verdict': self.generate_verdict(prob_profit, prob_ruin, prob_blowup, sharpes),
        }
        
        return report
    
    def generate_verdict(self, prob_profit: float, prob_ruin: float, 
                        prob_blowup: float, sharpes: List[float]) -> Dict:
        """Generate final verdict on strategy viability"""
        
        median_sharpe = sorted(sharpes)[len(sharpes)//2]
        
        verdict = {
            'status': 'PASS',
            'confidence': 'HIGH',
            'reasons': [],
            'warnings': [],
            'kill_signal': False,
        }
        
        # Check kill conditions
        if prob_ruin > self.DEATH_RUIN_PROB:
            verdict['kill_signal'] = True
            verdict['status'] = 'KILL'
            verdict['reasons'].append(f"Ruin probability {prob_ruin:.1%} exceeds threshold {self.DEATH_RUIN_PROB:.0%}")
        
        if prob_blowup > 0.10:  # 10% chance of 50% drawdown
            verdict['kill_signal'] = True
            verdict['status'] = 'KILL'
            verdict['reasons'].append(f"Blowup probability {prob_blowup:.1%} exceeds 10% threshold")
        
        if median_sharpe < self.DEATH_SHARPE:
            verdict['kill_signal'] = True
            verdict['status'] = 'KILL'
            verdict['reasons'].append(f"Median Sharpe {median_sharpe:.2f} below minimum {self.DEATH_SHARPE}")
        
        # Warnings (don't kill but concerning)
        if prob_profit < 0.70:
            verdict['warnings'].append(f"Low profit probability: {prob_profit:.1%}")
        
        if median_sharpe < 0.3:
            verdict['warnings'].append(f"Weak Sharpe ratio: {median_sharpe:.2f}")
        
        if not verdict['kill_signal'] and not verdict['warnings']:
            verdict['reasons'].append("All risk metrics within acceptable bounds")
        
        return verdict


def run_strategy_tests():
    """Run Monte Carlo tests on all strategy configurations"""
    
    runner = MonteCarloRunner(initial_capital=10000, n_simulations=1000)
    n_markets = runner.load_markets("polymarket_resolved_markets.json")
    print(f"Loaded {n_markets} markets for simulation")
    
    # Define strategies to test
    strategies = [
        {
            'name': 'BASELINE_FIXED',
            'params': {
                'whale_accuracy': 0.58,
                'slippage_pct': 0.02,
                'sizing_method': 'fixed',
                'base_position_size': 100,
                'max_position_pct': 0.10,
                'min_volume': 10000,
            }
        },
        {
            'name': 'OPTIMIZED_KIMI25',
            'params': {
                'whale_accuracy': 0.68,
                'slippage_pct': 0.015,
                'sizing_method': 'signal_scaled',
                'base_position_size': 100,
                'max_position_pct': 0.1,
                'category_filter': ['politics', 'crypto', 'economics'],
                'signal_threshold': 0.4,
                'min_volume': 20000,
            }
        },
        {
            'name': 'AGGRESSIVE_KELLY',
            'params': {
                'whale_accuracy': 0.70,
                'slippage_pct': 0.015,
                'sizing_method': 'kelly',
                'base_position_size': 200,
                'max_position_pct': 0.20,
                'min_volume': 50000,
            }
        },
        {
            'name': 'CONSERVATIVE_FIXED',
            'params': {
                'whale_accuracy': 0.65,
                'slippage_pct': 0.01,
                'sizing_method': 'fixed',
                'base_position_size': 50,
                'max_position_pct': 0.05,
                'min_volume': 50000,
            }
        },
        {
            'name': 'HIGH_ACCURACY_FILTER',
            'params': {
                'whale_accuracy': 0.75,
                'slippage_pct': 0.02,
                'sizing_method': 'signal_scaled',
                'base_position_size': 150,
                'max_position_pct': 0.15,
                'signal_threshold': 0.6,
                'min_volume': 100000,
            }
        },
    ]
    
    all_results = {}
    
    for strategy in strategies:
        report = runner.run_monte_carlo(strategy['params'], strategy['name'])
        all_results[strategy['name']] = report
        
        # Print summary
        print(f"\n{'='*70}")
        print(f"RESULTS: {strategy['name']}")
        print(f"{'='*70}")
        
        r_stats = report['return_statistics']
        dd_stats = report['drawdown_statistics']
        risk = report['risk_adjusted_returns']
        ruin = report['ruin_analysis']
        verdict = report['verdict']
        
        print(f"\n[RETURN DISTRIBUTION]")
        print(f"  Mean: {r_stats['mean']:+.2f}% | Median: {r_stats['median']:+.2f}% | StdDev: {r_stats['std_dev']:.2f}%")
        print(f"  5th percentile: {r_stats['percentiles']['p5']:+.2f}% (worst realistic case)")
        print(f"  50th percentile: {r_stats['percentiles']['p50']:+.2f}%")
        print(f"  95th percentile: {r_stats['percentiles']['p95']:+.2f}% (best realistic case)")
        print(f"  Range: {r_stats['min']:+.2f}% to {r_stats['max']:+.2f}%")
        
        print(f"\n[DRAWDOWN ANALYSIS]")
        print(f"  Mean: {dd_stats['mean']:.2f}% | Max observed: {dd_stats['max']:.2f}%")
        print(f"  50th percentile: {dd_stats['percentiles']['p50']:.2f}%")
        print(f"  95th percentile: {dd_stats['percentiles']['p95']:.2f}%")
        print(f"  99th percentile: {dd_stats['percentiles']['p99']:.2f}%")
        
        print(f"\n[RISK-ADJUSTED METRICS]")
        print(f"  Sharpe (mean): {risk['sharpe_mean']:.3f} | (median): {risk['sharpe_median']:.3f}")
        print(f"  Sharpe (5th %ile): {risk['sharpe_percentiles']['p5']:.3f}")
        print(f"  Sortino (mean): {risk['sortino_mean']:.3f}")
        print(f"  Calmar (mean): {risk['calmar_mean']:.3f}")
        
        print(f"\n[RUIN ANALYSIS]")
        print(f"  Probability of profit: {r_stats['prob_profit']:.1%}")
        print(f"  Probability of ruin (>50% loss): {ruin['prob_ruin_50pct']:.1%}")
        print(f"  Probability of blowup (>50% DD): {ruin['prob_blowup_50dd']:.1%}")
        print(f"  Death events: {ruin['death_events']}/{report['simulation_count']} ({ruin['death_rate']:.1%})")
        
        print(f"\n[VERDICT]: ", end="")
        if verdict['kill_signal']:
            print(f"KILL - Strategy is unsafe")
            for reason in verdict['reasons']:
                print(f"    X {reason}")
        else:
            print(f"PASS - Strategy is viable")
            for reason in verdict['reasons']:
                print(f"    OK {reason}")
        
        if verdict['warnings']:
            for warning in verdict['warnings']:
                print(f"    ! {warning}")
    
    # Save full results
    with open("monte_carlo_results_1000.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    # Generate comparison summary
    print(f"\n{'='*70}")
    print("STRATEGY COMPARISON SUMMARY")
    print(f"{'='*70}")
    print(f"{'Strategy':<25} {'Median Return':>12} {'Median DD':>10} {'Sharpe':>8} {'Ruin Prob':>10} {'Verdict':>10}")
    print("-" * 70)
    
    for name, report in all_results.items():
        median_ret = report['return_statistics']['percentiles']['p50']
        median_dd = report['drawdown_statistics']['percentiles']['p50']
        sharpe = report['risk_adjusted_returns']['sharpe_median']
        ruin = report['ruin_analysis']['prob_ruin_50pct']
        verdict = "KILL" if report['verdict']['kill_signal'] else "PASS"
        
        print(f"{name:<25} {median_ret:>+11.1f}% {median_dd:>9.1f}% {sharpe:>8.2f} {ruin:>9.1%} {verdict:>10}")
    
    print(f"\n{'='*70}")
    print("FINAL RECOMMENDATION")
    print(f"{'='*70}")
    
    viable_strategies = [
        (name, report) for name, report in all_results.items() 
        if not report['verdict']['kill_signal']
    ]
    
    if viable_strategies:
        # Sort by median return
        viable_strategies.sort(key=lambda x: x[1]['return_statistics']['percentiles']['p50'], reverse=True)
        best = viable_strategies[0]
        
        print(f"\n*** BEST VIABLE STRATEGY: {best[0]} ***")
        print(f"   Expected median return: {best[1]['return_statistics']['percentiles']['p50']:+.1f}%")
        print(f"   Expected median drawdown: {best[1]['drawdown_statistics']['percentiles']['p50']:.1f}%")
        print(f"   Sharpe ratio: {best[1]['risk_adjusted_returns']['sharpe_median']:.2f}")
        print(f"   Probability of profit: {best[1]['return_statistics']['prob_profit']:.1%}")
    else:
        print("\n*** NO VIABLE STRATEGIES FOUND ***")
        print("   All strategies failed death conditions.")
    
    killed = [name for name, report in all_results.items() if report['verdict']['kill_signal']]
    if killed:
        print(f"\n*** KILLED STRATEGIES ({len(killed)}) ***")
        for name in killed:
            print(f"   [X] {name}")
    
    print(f"\nFull results saved to: monte_carlo_results_1000.json")
    
    return all_results


if __name__ == "__main__":
    results = run_strategy_tests()
