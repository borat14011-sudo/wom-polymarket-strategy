#!/usr/bin/env python3
"""
Strategy Tuner - ML-based Parameter Optimization for Polymarket Trading
Optimizes RVR, ROC, Hype thresholds and risk parameters for maximum performance
"""

import argparse
import json
import sqlite3
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
import sys
import random
import math

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  NumPy not available - using pure Python (slower)")

try:
    from skopt import gp_minimize
    from skopt.space import Real, Integer
    from skopt.utils import use_named_args
    HAS_SKOPT = True
except ImportError:
    HAS_SKOPT = False
    print("⚠️  scikit-optimize not available - Bayesian optimization disabled")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not available - plotting disabled")


@dataclass
class ParameterSet:
    """Parameter combination to test"""
    rvr_threshold: float
    roc_threshold: float
    hype_threshold: float
    stop_loss: float  # percentage
    take_profit: float  # percentage
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def __str__(self) -> str:
        return (f"RVR={self.rvr_threshold:.2f}, ROC={self.roc_threshold:.3f}, "
                f"Hype={self.hype_threshold:.0f}, SL={self.stop_loss:.1f}%, "
                f"TP={self.take_profit:.1f}%")


@dataclass
class PerformanceMetrics:
    """Performance metrics for a parameter set"""
    sharpe_ratio: float
    profit_factor: float
    max_drawdown: float
    total_return: float
    win_rate: float
    num_trades: int
    avg_win: float
    avg_loss: float
    composite_score: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class OptimizationResult:
    """Result of optimization run"""
    best_params: ParameterSet
    best_metrics: PerformanceMetrics
    all_results: List[Tuple[ParameterSet, PerformanceMetrics]]
    method: str
    duration_seconds: float
    iterations: int


class StrategyBacktester:
    """Simplified backtester for parameter optimization"""
    
    def __init__(self, db_path: str = "polymarket_data.db"):
        self.db_path = db_path
        self.markets = self._load_markets()
    
    def _load_markets(self) -> List[Dict]:
        """Load market data from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get markets with signals
            cursor.execute("""
                SELECT 
                    condition_id,
                    title,
                    volume,
                    liquidity,
                    price,
                    rvr,
                    roc,
                    hype_score,
                    outcome_prices,
                    end_date_iso
                FROM markets
                WHERE rvr IS NOT NULL 
                AND roc IS NOT NULL
                AND hype_score IS NOT NULL
                ORDER BY timestamp DESC
            """)
            
            markets = []
            for row in cursor.fetchall():
                try:
                    outcome_prices = json.loads(row[8]) if row[8] else {}
                    markets.append({
                        'condition_id': row[0],
                        'title': row[1],
                        'volume': row[2],
                        'liquidity': row[3],
                        'price': row[4],
                        'rvr': row[5],
                        'roc': row[6],
                        'hype_score': row[7],
                        'outcome_prices': outcome_prices,
                        'end_date_iso': row[9]
                    })
                except:
                    continue
            
            conn.close()
            return markets
        except Exception as e:
            print(f"⚠️  Error loading markets: {e}")
            return []
    
    def backtest(self, params: ParameterSet) -> PerformanceMetrics:
        """Run backtest with given parameters"""
        if not self.markets:
            # Return dummy metrics if no data
            return PerformanceMetrics(
                sharpe_ratio=0.0,
                profit_factor=1.0,
                max_drawdown=0.0,
                total_return=0.0,
                win_rate=0.5,
                num_trades=0,
                avg_win=0.0,
                avg_loss=0.0,
                composite_score=0.0
            )
        
        trades = []
        equity = 10000.0  # Starting capital
        peak_equity = equity
        max_drawdown = 0.0
        
        for market in self.markets:
            # Check if market meets signal criteria
            if (market['rvr'] >= params.rvr_threshold and
                market['roc'] >= params.roc_threshold and
                market['hype_score'] >= params.hype_threshold):
                
                # Simulate trade
                entry_price = market['price']
                
                # Simulate outcome with price-based probability
                # Lower price = higher probability of "Yes" outcome
                win_probability = 1 - entry_price
                
                # Add some randomness but keep it consistent per market
                random.seed(hash(market['condition_id']) % 2**32)
                outcome_won = random.random() < win_probability
                
                if outcome_won:
                    # Winner - calculate profit
                    max_return = (1 / entry_price - 1) * 100  # Max possible return
                    actual_return = min(max_return, params.take_profit)
                    pnl = equity * (actual_return / 100)
                else:
                    # Loser - apply stop loss
                    pnl = -equity * (params.stop_loss / 100)
                
                equity += pnl
                trades.append({
                    'pnl': pnl,
                    'return_pct': (pnl / equity) * 100,
                    'won': outcome_won
                })
                
                # Track drawdown
                if equity > peak_equity:
                    peak_equity = equity
                drawdown = (peak_equity - equity) / peak_equity
                max_drawdown = max(max_drawdown, drawdown)
        
        if not trades:
            return PerformanceMetrics(
                sharpe_ratio=0.0,
                profit_factor=1.0,
                max_drawdown=0.0,
                total_return=0.0,
                win_rate=0.5,
                num_trades=0,
                avg_win=0.0,
                avg_loss=0.0,
                composite_score=0.0
            )
        
        # Calculate metrics
        winning_trades = [t for t in trades if t['won']]
        losing_trades = [t for t in trades if not t['won']]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = abs(sum(t['pnl'] for t in losing_trades) / len(losing_trades)) if losing_trades else 1
        
        total_return = ((equity - 10000) / 10000) * 100
        
        # Calculate Sharpe ratio (simplified)
        returns = [t['return_pct'] for t in trades]
        if len(returns) > 1:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            std_dev = math.sqrt(variance) if variance > 0 else 1
            sharpe_ratio = (mean_return / std_dev) * math.sqrt(252) if std_dev > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Profit factor
        gross_profit = sum(t['pnl'] for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t['pnl'] for t in losing_trades)) if losing_trades else 1
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 1
        
        # Composite score (weighted combination)
        composite_score = (
            sharpe_ratio * 0.4 +
            (profit_factor - 1) * 0.3 +
            (1 - max_drawdown) * 0.2 +
            win_rate * 0.1
        )
        
        return PerformanceMetrics(
            sharpe_ratio=sharpe_ratio,
            profit_factor=profit_factor,
            max_drawdown=max_drawdown * 100,
            total_return=total_return,
            win_rate=win_rate * 100,
            num_trades=len(trades),
            avg_win=avg_win,
            avg_loss=avg_loss,
            composite_score=composite_score
        )


class StrategyTuner:
    """Main strategy optimization class"""
    
    def __init__(self, db_path: str = "polymarket_data.db"):
        self.db_path = db_path
        self.backtester = StrategyBacktester(db_path)
        self.param_space = {
            'rvr_threshold': (1.0, 4.0),
            'roc_threshold': (0.05, 0.20),
            'hype_threshold': (50, 90),
            'stop_loss': (5.0, 20.0),
            'take_profit': (5.0, 30.0)
        }
        self.results_cache = []
    
    def _evaluate(self, params: ParameterSet, objective: str = 'sharpe') -> float:
        """Evaluate a parameter set and return objective value"""
        metrics = self.backtester.backtest(params)
        self.results_cache.append((params, metrics))
        
        # Return objective value (higher is better)
        if objective == 'sharpe':
            return metrics.sharpe_ratio
        elif objective == 'profit_factor':
            return metrics.profit_factor
        elif objective == 'drawdown':
            return -metrics.max_drawdown  # Minimize drawdown = maximize negative
        elif objective == 'composite':
            return metrics.composite_score
        else:
            return metrics.composite_score
    
    def grid_search(self, objective: str = 'sharpe', grid_size: int = 5) -> OptimizationResult:
        """Grid search optimization (exhaustive)"""
        print(f"\n🔍 Grid Search ({grid_size}^5 = {grid_size**5} combinations)")
        start_time = time.time()
        
        # Generate grid
        rvr_vals = self._linspace(self.param_space['rvr_threshold'][0], 
                                   self.param_space['rvr_threshold'][1], grid_size)
        roc_vals = self._linspace(self.param_space['roc_threshold'][0], 
                                   self.param_space['roc_threshold'][1], grid_size)
        hype_vals = self._linspace(self.param_space['hype_threshold'][0], 
                                    self.param_space['hype_threshold'][1], grid_size)
        sl_vals = self._linspace(self.param_space['stop_loss'][0], 
                                 self.param_space['stop_loss'][1], grid_size)
        tp_vals = self._linspace(self.param_space['take_profit'][0], 
                                 self.param_space['take_profit'][1], grid_size)
        
        best_score = float('-inf')
        best_params = None
        best_metrics = None
        iterations = 0
        
        total = len(rvr_vals) * len(roc_vals) * len(hype_vals) * len(sl_vals) * len(tp_vals)
        
        for rvr in rvr_vals:
            for roc in roc_vals:
                for hype in hype_vals:
                    for sl in sl_vals:
                        for tp in tp_vals:
                            params = ParameterSet(rvr, roc, hype, sl, tp)
                            score = self._evaluate(params, objective)
                            iterations += 1
                            
                            if iterations % 100 == 0:
                                print(f"  Progress: {iterations}/{total} ({iterations/total*100:.1f}%)")
                            
                            if score > best_score:
                                best_score = score
                                best_params = params
                                best_metrics = self.results_cache[-1][1]
                                print(f"  ✨ New best: {objective}={score:.3f} | {params}")
        
        duration = time.time() - start_time
        print(f"\n✅ Grid search complete in {duration:.1f}s")
        
        return OptimizationResult(
            best_params=best_params,
            best_metrics=best_metrics,
            all_results=self.results_cache.copy(),
            method='grid',
            duration_seconds=duration,
            iterations=iterations
        )
    
    def random_search(self, objective: str = 'sharpe', n_iterations: int = 200) -> OptimizationResult:
        """Random search optimization (faster)"""
        print(f"\n🎲 Random Search ({n_iterations} iterations)")
        start_time = time.time()
        
        best_score = float('-inf')
        best_params = None
        best_metrics = None
        
        for i in range(n_iterations):
            # Random sample from parameter space
            params = ParameterSet(
                rvr_threshold=random.uniform(*self.param_space['rvr_threshold']),
                roc_threshold=random.uniform(*self.param_space['roc_threshold']),
                hype_threshold=random.uniform(*self.param_space['hype_threshold']),
                stop_loss=random.uniform(*self.param_space['stop_loss']),
                take_profit=random.uniform(*self.param_space['take_profit'])
            )
            
            score = self._evaluate(params, objective)
            
            if (i + 1) % 20 == 0:
                print(f"  Progress: {i+1}/{n_iterations} ({(i+1)/n_iterations*100:.1f}%)")
            
            if score > best_score:
                best_score = score
                best_params = params
                best_metrics = self.results_cache[-1][1]
                print(f"  ✨ New best: {objective}={score:.3f} | {params}")
        
        duration = time.time() - start_time
        print(f"\n✅ Random search complete in {duration:.1f}s")
        
        return OptimizationResult(
            best_params=best_params,
            best_metrics=best_metrics,
            all_results=self.results_cache.copy(),
            method='random',
            duration_seconds=duration,
            iterations=n_iterations
        )
    
    def bayesian_optimization(self, objective: str = 'sharpe', n_calls: int = 100) -> OptimizationResult:
        """Bayesian optimization using Gaussian Process (requires scikit-optimize)"""
        if not HAS_SKOPT:
            print("❌ Bayesian optimization requires scikit-optimize")
            print("   Install with: pip install scikit-optimize")
            print("   Falling back to random search...")
            return self.random_search(objective, n_calls)
        
        print(f"\n🧠 Bayesian Optimization ({n_calls} iterations)")
        start_time = time.time()
        
        # Define search space for skopt
        space = [
            Real(*self.param_space['rvr_threshold'], name='rvr_threshold'),
            Real(*self.param_space['roc_threshold'], name='roc_threshold'),
            Real(*self.param_space['hype_threshold'], name='hype_threshold'),
            Real(*self.param_space['stop_loss'], name='stop_loss'),
            Real(*self.param_space['take_profit'], name='take_profit')
        ]
        
        # Objective function for skopt (minimize, so negate)
        @use_named_args(space)
        def objective_func(**params_dict):
            params = ParameterSet(**params_dict)
            score = self._evaluate(params, objective)
            return -score  # Minimize negative = maximize positive
        
        # Run optimization
        result = gp_minimize(
            objective_func,
            space,
            n_calls=n_calls,
            random_state=42,
            verbose=False
        )
        
        # Extract best parameters
        best_params = ParameterSet(
            rvr_threshold=result.x[0],
            roc_threshold=result.x[1],
            hype_threshold=result.x[2],
            stop_loss=result.x[3],
            take_profit=result.x[4]
        )
        
        # Find best metrics from cache
        best_score = -result.fun
        best_metrics = None
        for params, metrics in self.results_cache:
            if (abs(params.rvr_threshold - best_params.rvr_threshold) < 0.01 and
                abs(params.roc_threshold - best_params.roc_threshold) < 0.001):
                best_metrics = metrics
                break
        
        if best_metrics is None:
            # Re-evaluate if not found
            best_metrics = self.backtester.backtest(best_params)
        
        duration = time.time() - start_time
        print(f"\n✅ Bayesian optimization complete in {duration:.1f}s")
        print(f"  Best {objective}: {best_score:.3f}")
        print(f"  {best_params}")
        
        return OptimizationResult(
            best_params=best_params,
            best_metrics=best_metrics,
            all_results=self.results_cache.copy(),
            method='bayesian',
            duration_seconds=duration,
            iterations=n_calls
        )
    
    def walk_forward(self, objective: str = 'sharpe', n_iterations: int = 50) -> OptimizationResult:
        """Walk-forward optimization (adaptive grid search)"""
        print(f"\n🚶 Walk-Forward Optimization ({n_iterations} iterations)")
        start_time = time.time()
        
        # Start with center of parameter space
        current_params = ParameterSet(
            rvr_threshold=sum(self.param_space['rvr_threshold']) / 2,
            roc_threshold=sum(self.param_space['roc_threshold']) / 2,
            hype_threshold=sum(self.param_space['hype_threshold']) / 2,
            stop_loss=sum(self.param_space['stop_loss']) / 2,
            take_profit=sum(self.param_space['take_profit']) / 2
        )
        
        best_score = self._evaluate(current_params, objective)
        best_params = current_params
        best_metrics = self.results_cache[-1][1]
        
        # Adaptive step sizes
        step_sizes = {
            'rvr_threshold': 0.5,
            'roc_threshold': 0.02,
            'hype_threshold': 10,
            'stop_loss': 2.0,
            'take_profit': 3.0
        }
        
        for iteration in range(n_iterations):
            improved = False
            
            # Try neighbors in each dimension
            for param_name in step_sizes.keys():
                for direction in [-1, 1]:
                    # Create neighbor
                    neighbor_dict = best_params.to_dict()
                    neighbor_dict[param_name] += direction * step_sizes[param_name]
                    
                    # Clip to bounds
                    min_val, max_val = self.param_space[param_name]
                    neighbor_dict[param_name] = max(min_val, min(max_val, neighbor_dict[param_name]))
                    
                    neighbor_params = ParameterSet(**neighbor_dict)
                    score = self._evaluate(neighbor_params, objective)
                    
                    if score > best_score:
                        best_score = score
                        best_params = neighbor_params
                        best_metrics = self.results_cache[-1][1]
                        improved = True
                        print(f"  Iteration {iteration+1}: New best {objective}={score:.3f}")
            
            # Reduce step sizes if no improvement
            if not improved:
                for key in step_sizes:
                    step_sizes[key] *= 0.8
                print(f"  Iteration {iteration+1}: Reducing step sizes...")
            
            # Check if converged
            if all(step < 0.01 for step in step_sizes.values()):
                print(f"  Converged at iteration {iteration+1}")
                break
        
        duration = time.time() - start_time
        print(f"\n✅ Walk-forward complete in {duration:.1f}s")
        print(f"  Best {objective}: {best_score:.3f}")
        print(f"  {best_params}")
        
        return OptimizationResult(
            best_params=best_params,
            best_metrics=best_metrics,
            all_results=self.results_cache.copy(),
            method='walk_forward',
            duration_seconds=duration,
            iterations=len(self.results_cache)
        )
    
    def optimize(self, method: str = 'random', objective: str = 'sharpe', **kwargs) -> OptimizationResult:
        """Run optimization with specified method"""
        self.results_cache = []  # Clear cache
        
        if method == 'grid':
            return self.grid_search(objective, kwargs.get('grid_size', 4))
        elif method == 'random':
            return self.random_search(objective, kwargs.get('n_iterations', 200))
        elif method == 'bayesian':
            return self.bayesian_optimization(objective, kwargs.get('n_calls', 100))
        elif method == 'walk_forward':
            return self.walk_forward(objective, kwargs.get('n_iterations', 50))
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def export_config(self, result: OptimizationResult, output_path: str):
        """Export optimized parameters to YAML config"""
        params = result.best_params
        metrics = result.best_metrics
        
        config_text = f"""# Optimized Strategy Configuration
# Generated by Strategy Tuner
# Method: {result.method}
# Objective: Sharpe Ratio = {metrics.sharpe_ratio:.3f}
# Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

thresholds:
  rvr: {params.rvr_threshold:.2f}
  roc: {params.roc_threshold:.3f}
  hype: {params.hype_threshold:.0f}

risk:
  stop_loss: {params.stop_loss:.1f}  # %
  take_profit: {params.take_profit:.1f}  # %

# Performance Metrics
# Sharpe Ratio: {metrics.sharpe_ratio:.3f}
# Profit Factor: {metrics.profit_factor:.3f}
# Max Drawdown: {metrics.max_drawdown:.2f}%
# Total Return: {metrics.total_return:.2f}%
# Win Rate: {metrics.win_rate:.2f}%
# Trades: {metrics.num_trades}
# Composite Score: {metrics.composite_score:.3f}
"""
        
        with open(output_path, 'w') as f:
            f.write(config_text)
        
        print(f"\n✅ Config exported to {output_path}")
    
    def sensitivity_analysis(self, result: OptimizationResult, param_name: str, steps: int = 10):
        """Analyze sensitivity of objective to one parameter"""
        print(f"\n📊 Sensitivity Analysis: {param_name}")
        
        base_params = result.best_params
        param_range = self.param_space[param_name]
        
        values = []
        scores = []
        
        for val in self._linspace(param_range[0], param_range[1], steps):
            test_params_dict = base_params.to_dict()
            test_params_dict[param_name] = val
            test_params = ParameterSet(**test_params_dict)
            
            score = self._evaluate(test_params, 'composite')
            values.append(val)
            scores.append(score)
            print(f"  {param_name}={val:.3f} → score={score:.3f}")
        
        return values, scores
    
    def plot_results(self, result: OptimizationResult, output_dir: str = "."):
        """Generate performance plots"""
        if not HAS_MATPLOTLIB:
            print("⚠️  matplotlib not available - skipping plots")
            return
        
        print("\n📈 Generating plots...")
        
        # Extract data
        all_params = [r[0] for r in result.all_results]
        all_metrics = [r[1] for r in result.all_results]
        
        # Plot 1: Convergence
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        sharpe_vals = [m.sharpe_ratio for m in all_metrics]
        axes[0, 0].plot(sharpe_vals)
        axes[0, 0].set_title('Sharpe Ratio Convergence')
        axes[0, 0].set_xlabel('Iteration')
        axes[0, 0].set_ylabel('Sharpe Ratio')
        axes[0, 0].grid(True)
        
        # Plot 2: Profit Factor
        pf_vals = [m.profit_factor for m in all_metrics]
        axes[0, 1].plot(pf_vals)
        axes[0, 1].set_title('Profit Factor Convergence')
        axes[0, 1].set_xlabel('Iteration')
        axes[0, 1].set_ylabel('Profit Factor')
        axes[0, 1].grid(True)
        
        # Plot 3: Drawdown
        dd_vals = [m.max_drawdown for m in all_metrics]
        axes[1, 0].plot(dd_vals)
        axes[1, 0].set_title('Max Drawdown')
        axes[1, 0].set_xlabel('Iteration')
        axes[1, 0].set_ylabel('Drawdown %')
        axes[1, 0].grid(True)
        
        # Plot 4: Composite Score
        comp_vals = [m.composite_score for m in all_metrics]
        axes[1, 1].plot(comp_vals)
        axes[1, 1].set_title('Composite Score')
        axes[1, 1].set_xlabel('Iteration')
        axes[1, 1].set_ylabel('Score')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        output_path = Path(output_dir) / f"optimization_{result.method}_{int(time.time())}.png"
        plt.savefig(output_path, dpi=150)
        print(f"  Saved: {output_path}")
        
        plt.close()
    
    def _linspace(self, start: float, stop: float, num: int) -> List[float]:
        """Generate evenly spaced values (like numpy.linspace)"""
        if num == 1:
            return [start]
        step = (stop - start) / (num - 1)
        return [start + step * i for i in range(num)]


def main():
    parser = argparse.ArgumentParser(
        description='Strategy Tuner - ML-based Parameter Optimization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python strategy-tuner.py --method random
  python strategy-tuner.py --method bayesian --objective sharpe
  python strategy-tuner.py --method grid --grid-size 3
  python strategy-tuner.py --export config.yaml.optimized
        """
    )
    
    parser.add_argument('--method', default='random',
                       choices=['grid', 'random', 'bayesian', 'walk_forward'],
                       help='Optimization method')
    parser.add_argument('--objective', default='composite',
                       choices=['sharpe', 'profit_factor', 'drawdown', 'composite'],
                       help='Objective function to optimize')
    parser.add_argument('--iterations', type=int, default=200,
                       help='Number of iterations (for random/bayesian)')
    parser.add_argument('--grid-size', type=int, default=4,
                       help='Grid size per dimension (for grid search)')
    parser.add_argument('--db', default='polymarket_data.db',
                       help='Path to database')
    parser.add_argument('--export', type=str,
                       help='Export optimized config to file')
    parser.add_argument('--plot', action='store_true',
                       help='Generate performance plots')
    parser.add_argument('--sensitivity', type=str,
                       help='Run sensitivity analysis for parameter')
    
    args = parser.parse_args()
    
    # Initialize tuner
    print("🚀 Strategy Tuner - ML-based Parameter Optimization")
    print(f"   Database: {args.db}")
    print(f"   Method: {args.method}")
    print(f"   Objective: {args.objective}")
    
    tuner = StrategyTuner(db_path=args.db)
    
    # Check if we have data
    if not tuner.backtester.markets:
        print("\n❌ No market data found in database!")
        print("   Please run data collection first.")
        sys.exit(1)
    
    print(f"   Markets loaded: {len(tuner.backtester.markets)}")
    
    # Run optimization
    kwargs = {}
    if args.method == 'grid':
        kwargs['grid_size'] = args.grid_size
    elif args.method in ['random', 'bayesian']:
        kwargs['n_iterations'] = args.iterations
        kwargs['n_calls'] = args.iterations
    
    result = tuner.optimize(method=args.method, objective=args.objective, **kwargs)
    
    # Print results
    print("\n" + "="*70)
    print("🎯 OPTIMIZATION RESULTS")
    print("="*70)
    print(f"\nMethod: {result.method}")
    print(f"Duration: {result.duration_seconds:.1f}s")
    print(f"Iterations: {result.iterations}")
    
    print("\n📊 BEST PARAMETERS:")
    print(f"  RVR Threshold: {result.best_params.rvr_threshold:.2f}")
    print(f"  ROC Threshold: {result.best_params.roc_threshold:.3f}")
    print(f"  Hype Threshold: {result.best_params.hype_threshold:.0f}")
    print(f"  Stop Loss: {result.best_params.stop_loss:.1f}%")
    print(f"  Take Profit: {result.best_params.take_profit:.1f}%")
    
    print("\n📈 PERFORMANCE METRICS:")
    print(f"  Sharpe Ratio: {result.best_metrics.sharpe_ratio:.3f}")
    print(f"  Profit Factor: {result.best_metrics.profit_factor:.3f}")
    print(f"  Max Drawdown: {result.best_metrics.max_drawdown:.2f}%")
    print(f"  Total Return: {result.best_metrics.total_return:.2f}%")
    print(f"  Win Rate: {result.best_metrics.win_rate:.2f}%")
    print(f"  Number of Trades: {result.best_metrics.num_trades}")
    print(f"  Avg Win: ${result.best_metrics.avg_win:.2f}")
    print(f"  Avg Loss: ${result.best_metrics.avg_loss:.2f}")
    print(f"  Composite Score: {result.best_metrics.composite_score:.3f}")
    
    # Export config
    if args.export:
        tuner.export_config(result, args.export)
    
    # Sensitivity analysis
    if args.sensitivity:
        tuner.sensitivity_analysis(result, args.sensitivity)
    
    # Generate plots
    if args.plot:
        tuner.plot_results(result)
    
    # Save detailed results
    results_file = f"optimization_results_{result.method}_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump({
            'method': result.method,
            'duration_seconds': result.duration_seconds,
            'iterations': result.iterations,
            'best_params': result.best_params.to_dict(),
            'best_metrics': result.best_metrics.to_dict(),
            'all_results': [
                {
                    'params': p.to_dict(),
                    'metrics': m.to_dict()
                }
                for p, m in result.all_results[:100]  # Save top 100
            ]
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    print("\n✅ Great success! Optimization complete.")


if __name__ == '__main__':
    main()
