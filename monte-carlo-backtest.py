#!/usr/bin/env python3
"""
Monte Carlo Backtester for Polymarket Trading System
Advanced backtesting with simulation, stress testing, and sensitivity analysis
"""

import argparse
import json
import random
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import time

# Try to import numpy/scipy for performance, fallback to pure Python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    print("⚠️  NumPy not available, using pure Python (slower)")


@dataclass
class TradeConfig:
    """Trading strategy configuration"""
    rvr_threshold: float = 2.0  # Risk/Reward Ratio threshold
    stop_loss_pct: float = 0.12  # 12% stop loss
    position_size_pct: float = 0.03  # 3% per position
    max_positions: int = 5
    signal_threshold: float = 0.65  # Confidence threshold for entry
    
    # Risk management
    max_drawdown_circuit_breaker: float = 0.25  # 25% max drawdown
    daily_loss_limit: float = 0.05  # 5% daily loss limit


@dataclass
class SimulationConfig:
    """Monte Carlo simulation parameters"""
    num_runs: int = 1000
    entry_timing_jitter_hours: float = 1.0  # ±1 hour
    slippage_range: Tuple[float, float] = (0.01, 0.03)  # 1-3%
    signal_threshold_variance: float = 0.05  # ±5%
    
    # Stress test multipliers
    stress_volatility_multiplier: float = 2.0
    stress_slippage_multiplier: float = 2.0
    stress_liquidity_reduction: float = 0.5  # 50% liquidity


@dataclass
class Trade:
    """Individual trade record"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    pnl_pct: float
    slippage: float
    is_winner: bool


@dataclass
class SimulationResult:
    """Results from a single simulation run"""
    trades: List[Trade] = field(default_factory=list)
    final_balance: float = 10000.0
    total_return: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    total_trades: int = 0
    hit_circuit_breaker: bool = False
    drawdown_recovery_days: Optional[int] = None


class MarketDataSimulator:
    """Simulates realistic market data for backtesting"""
    
    def __init__(self, days: int = 90, volatility: float = 1.0):
        self.days = days
        self.volatility = volatility
        self.data = self._generate_market_data()
    
    def _generate_market_data(self) -> List[Dict]:
        """Generate synthetic market data with realistic patterns"""
        data = []
        base_time = datetime(2025, 1, 1)
        
        for day in range(self.days):
            # Generate 5-15 signals per day
            num_signals = random.randint(5, 15)
            
            for _ in range(num_signals):
                hours_offset = random.uniform(0, 24)
                timestamp = base_time + timedelta(days=day, hours=hours_offset)
                
                # Simulate signal strength (0-1)
                signal_strength = random.betavariate(2, 2)
                
                # Simulate market conditions
                volatility = random.uniform(0.5, 2.0) * self.volatility
                liquidity = random.uniform(0.3, 1.0)
                
                # Simulate outcome probability (correlated with signal strength)
                outcome_prob = 0.5 + (signal_strength - 0.5) * 0.4
                actual_outcome = random.random() < outcome_prob
                
                # Price movement based on outcome
                if actual_outcome:
                    price_move = random.uniform(0.10, 0.30) * volatility
                else:
                    price_move = random.uniform(-0.15, -0.05) * volatility
                
                data.append({
                    'timestamp': timestamp,
                    'signal_strength': signal_strength,
                    'volatility': volatility,
                    'liquidity': liquidity,
                    'price_move': price_move,
                    'outcome': actual_outcome
                })
        
        return sorted(data, key=lambda x: x['timestamp'])


class MonteCarloBacktester:
    """Monte Carlo simulation engine"""
    
    def __init__(self, config: TradeConfig, sim_config: SimulationConfig):
        self.config = config
        self.sim_config = sim_config
        self.results: List[SimulationResult] = []
    
    def run_simulation(self, run_id: int, market_data: MarketDataSimulator,
                      stress_test: bool = False) -> SimulationResult:
        """Run a single simulation with randomized parameters"""
        
        # Randomize parameters for this run
        rvr = self.config.rvr_threshold
        stop_loss = self.config.stop_loss_pct
        position_size = self.config.position_size_pct
        signal_thresh = self.config.signal_threshold
        
        # Apply randomization
        if not stress_test:
            signal_thresh += random.uniform(-self.sim_config.signal_threshold_variance,
                                          self.sim_config.signal_threshold_variance)
        
        # Initialize portfolio
        balance = 10000.0
        peak_balance = balance
        max_drawdown = 0.0
        trades = []
        daily_pnl = defaultdict(float)
        
        # Track drawdown periods
        in_drawdown = False
        drawdown_start = None
        recovery_days = []
        
        hit_circuit_breaker = False
        
        for signal in market_data.data:
            # Check circuit breaker
            current_drawdown = (peak_balance - balance) / peak_balance if peak_balance > 0 else 0
            if current_drawdown >= self.config.max_drawdown_circuit_breaker:
                hit_circuit_breaker = True
                break
            
            # Apply entry timing jitter
            jitter_hours = random.uniform(-self.sim_config.entry_timing_jitter_hours,
                                         self.sim_config.entry_timing_jitter_hours)
            entry_time = signal['timestamp'] + timedelta(hours=jitter_hours)
            
            # Check if signal meets threshold
            if signal['signal_strength'] < signal_thresh:
                continue
            
            # Calculate position size
            pos_size = balance * position_size
            
            # Apply slippage
            if stress_test:
                slippage_range = (
                    self.sim_config.slippage_range[0] * self.sim_config.stress_slippage_multiplier,
                    self.sim_config.slippage_range[1] * self.sim_config.stress_slippage_multiplier
                )
            else:
                slippage_range = self.sim_config.slippage_range
            
            slippage = random.uniform(*slippage_range)
            
            # Simulate trade outcome
            exit_time = entry_time + timedelta(hours=random.uniform(1, 48))
            
            # Adjust for stress test
            price_move = signal['price_move']
            if stress_test:
                price_move *= self.sim_config.stress_volatility_multiplier
            
            # Apply slippage to price move
            actual_price_move = price_move - slippage
            
            # Calculate P&L
            pnl = pos_size * actual_price_move
            pnl_pct = actual_price_move
            
            # Apply stop loss
            if pnl_pct < -stop_loss:
                pnl = -pos_size * stop_loss
                pnl_pct = -stop_loss
            
            balance += pnl
            
            # Track daily P&L
            day_key = entry_time.date()
            daily_pnl[day_key] += pnl
            
            # Check daily loss limit
            if daily_pnl[day_key] < -balance * self.config.daily_loss_limit:
                continue  # Skip rest of day
            
            # Record trade
            trade = Trade(
                entry_time=entry_time,
                exit_time=exit_time,
                entry_price=1.0,
                exit_price=1.0 + actual_price_move,
                position_size=pos_size,
                pnl=pnl,
                pnl_pct=pnl_pct,
                slippage=slippage,
                is_winner=pnl > 0
            )
            trades.append(trade)
            
            # Update peak and drawdown
            if balance > peak_balance:
                peak_balance = balance
                if in_drawdown:
                    # Recovered from drawdown
                    recovery_time = (entry_time.date() - drawdown_start).days
                    recovery_days.append(recovery_time)
                    in_drawdown = False
            else:
                current_dd = (peak_balance - balance) / peak_balance
                max_drawdown = max(max_drawdown, current_dd)
                if not in_drawdown and current_dd > 0.05:  # 5% threshold
                    in_drawdown = True
                    drawdown_start = entry_time.date()
        
        # Calculate metrics
        total_return = (balance - 10000.0) / 10000.0
        win_rate = sum(1 for t in trades if t.is_winner) / len(trades) if trades else 0
        
        # Calculate Sharpe ratio
        if trades:
            returns = [t.pnl_pct for t in trades]
            if HAS_NUMPY:
                sharpe = np.mean(returns) / np.std(returns) * (252 ** 0.5) if np.std(returns) > 0 else 0
            else:
                mean_ret = sum(returns) / len(returns)
                variance = sum((r - mean_ret) ** 2 for r in returns) / len(returns)
                std_ret = variance ** 0.5
                sharpe = mean_ret / std_ret * (252 ** 0.5) if std_ret > 0 else 0
        else:
            sharpe = 0
        
        avg_recovery = sum(recovery_days) / len(recovery_days) if recovery_days else None
        
        return SimulationResult(
            trades=trades,
            final_balance=balance,
            total_return=total_return,
            sharpe_ratio=sharpe,
            win_rate=win_rate,
            max_drawdown=max_drawdown,
            total_trades=len(trades),
            hit_circuit_breaker=hit_circuit_breaker,
            drawdown_recovery_days=avg_recovery
        )
    
    def run_monte_carlo(self, stress_test: bool = False) -> List[SimulationResult]:
        """Run multiple Monte Carlo simulations"""
        print(f"\n{'🔥 STRESS TEST' if stress_test else '🎲 MONTE CARLO SIMULATION'}")
        print(f"Running {self.sim_config.num_runs} simulations...")
        
        results = []
        start_time = time.time()
        
        # Generate base market data
        volatility = self.sim_config.stress_volatility_multiplier if stress_test else 1.0
        market_data = MarketDataSimulator(days=90, volatility=volatility)
        
        for i in range(self.sim_config.num_runs):
            if (i + 1) % 100 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                remaining = (self.sim_config.num_runs - i - 1) / rate
                print(f"  Progress: {i+1}/{self.sim_config.num_runs} "
                      f"({rate:.1f} sims/sec, ~{remaining:.0f}s remaining)")
            
            result = self.run_simulation(i, market_data, stress_test=stress_test)
            results.append(result)
        
        elapsed = time.time() - start_time
        print(f"✅ Completed in {elapsed:.1f} seconds ({self.sim_config.num_runs/elapsed:.1f} sims/sec)")
        
        self.results = results
        return results
    
    def sensitivity_analysis(self) -> Dict:
        """Run parameter sensitivity analysis"""
        print("\n📊 SENSITIVITY ANALYSIS")
        print("Testing parameter combinations...")
        
        # Parameter ranges
        rvr_values = [1.5, 2.0, 2.5]
        stop_loss_values = [0.10, 0.12, 0.15]
        position_size_values = [0.02, 0.03, 0.05]
        
        results_grid = {}
        total_combinations = len(rvr_values) * len(stop_loss_values) * len(position_size_values)
        current = 0
        
        market_data = MarketDataSimulator(days=90)
        
        for rvr in rvr_values:
            for stop_loss in stop_loss_values:
                for pos_size in position_size_values:
                    current += 1
                    print(f"  Testing {current}/{total_combinations}: "
                          f"RVR={rvr}, SL={stop_loss*100:.0f}%, Size={pos_size*100:.0f}%")
                    
                    # Temporarily modify config
                    original_rvr = self.config.rvr_threshold
                    original_sl = self.config.stop_loss_pct
                    original_ps = self.config.position_size_pct
                    
                    self.config.rvr_threshold = rvr
                    self.config.stop_loss_pct = stop_loss
                    self.config.position_size_pct = pos_size
                    
                    # Run smaller number of simulations for each combo
                    combo_results = []
                    for i in range(100):  # 100 runs per combo
                        result = self.run_simulation(i, market_data)
                        combo_results.append(result)
                    
                    # Calculate aggregate metrics
                    avg_return = sum(r.total_return for r in combo_results) / len(combo_results)
                    avg_sharpe = sum(r.sharpe_ratio for r in combo_results) / len(combo_results)
                    avg_drawdown = sum(r.max_drawdown for r in combo_results) / len(combo_results)
                    
                    results_grid[(rvr, stop_loss, pos_size)] = {
                        'avg_return': avg_return,
                        'avg_sharpe': avg_sharpe,
                        'avg_drawdown': avg_drawdown,
                        'results': combo_results
                    }
                    
                    # Restore original config
                    self.config.rvr_threshold = original_rvr
                    self.config.stop_loss_pct = original_sl
                    self.config.position_size_pct = original_ps
        
        print("✅ Sensitivity analysis complete")
        return results_grid
    
    def calculate_confidence_intervals(self, results: List[SimulationResult],
                                      confidence: float = 0.95) -> Dict:
        """Calculate bootstrap confidence intervals"""
        print("\n📈 CALCULATING CONFIDENCE INTERVALS")
        
        # Extract metrics
        returns = [r.total_return for r in results]
        sharpes = [r.sharpe_ratio for r in results]
        drawdowns = [r.max_drawdown for r in results]
        win_rates = [r.win_rate for r in results]
        
        def bootstrap_ci(data: List[float], confidence: float) -> Tuple[float, float, float]:
            """Calculate bootstrap confidence interval"""
            if HAS_NUMPY:
                data_array = np.array(data)
                mean = np.mean(data_array)
                lower = np.percentile(data_array, (1 - confidence) / 2 * 100)
                upper = np.percentile(data_array, (1 + confidence) / 2 * 100)
            else:
                sorted_data = sorted(data)
                n = len(sorted_data)
                mean = sum(sorted_data) / n
                lower_idx = int(n * (1 - confidence) / 2)
                upper_idx = int(n * (1 + confidence) / 2)
                lower = sorted_data[lower_idx]
                upper = sorted_data[upper_idx]
            
            return mean, lower, upper
        
        return {
            'total_return': bootstrap_ci(returns, confidence),
            'sharpe_ratio': bootstrap_ci(sharpes, confidence),
            'max_drawdown': bootstrap_ci(drawdowns, confidence),
            'win_rate': bootstrap_ci(win_rates, confidence)
        }
    
    def analyze_drawdowns(self, results: List[SimulationResult]) -> Dict:
        """Analyze drawdown patterns"""
        print("\n📉 DRAWDOWN ANALYSIS")
        
        drawdowns = [r.max_drawdown for r in results]
        recovery_times = [r.drawdown_recovery_days for r in results 
                         if r.drawdown_recovery_days is not None]
        circuit_breaker_hits = sum(1 for r in results if r.hit_circuit_breaker)
        
        if HAS_NUMPY:
            dd_array = np.array(drawdowns)
            percentiles = {
                '50th': np.percentile(dd_array, 50),
                '75th': np.percentile(dd_array, 75),
                '90th': np.percentile(dd_array, 90),
                '95th': np.percentile(dd_array, 95),
                '99th': np.percentile(dd_array, 99)
            }
        else:
            sorted_dd = sorted(drawdowns)
            n = len(sorted_dd)
            percentiles = {
                '50th': sorted_dd[int(n * 0.50)],
                '75th': sorted_dd[int(n * 0.75)],
                '90th': sorted_dd[int(n * 0.90)],
                '95th': sorted_dd[int(n * 0.95)],
                '99th': sorted_dd[int(n * 0.99)]
            }
        
        prob_of_ruin = circuit_breaker_hits / len(results)
        avg_recovery = sum(recovery_times) / len(recovery_times) if recovery_times else None
        
        return {
            'percentiles': percentiles,
            'prob_of_ruin': prob_of_ruin,
            'avg_recovery_days': avg_recovery,
            'max_drawdown': max(drawdowns)
        }


class HTMLReportGenerator:
    """Generate beautiful HTML reports with charts"""
    
    @staticmethod
    def generate(results: List[SimulationResult], confidence_intervals: Dict,
                drawdown_analysis: Dict, sensitivity_results: Optional[Dict],
                output_path: str, stress_test: bool = False):
        """Generate comprehensive HTML report"""
        
        print(f"\n📊 GENERATING HTML REPORT: {output_path}")
        
        # Calculate summary statistics
        avg_return = sum(r.total_return for r in results) / len(results)
        avg_sharpe = sum(r.sharpe_ratio for r in results) / len(results)
        avg_win_rate = sum(r.win_rate for r in results) / len(results)
        avg_trades = sum(r.total_trades for r in results) / len(results)
        
        # Prepare distribution data
        returns_dist = [r.total_return * 100 for r in results]
        sharpe_dist = [r.sharpe_ratio for r in results]
        drawdown_dist = [r.max_drawdown * 100 for r in results]
        
        # Create HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{'Stress Test' if stress_test else 'Monte Carlo Backtest'} Report - Polymarket Trading</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }}
        .metric-value.positive {{ color: #10b981; }}
        .metric-value.negative {{ color: #ef4444; }}
        .metric-ci {{
            font-size: 0.85em;
            color: #888;
            margin-top: 5px;
        }}
        .section {{
            padding: 40px;
        }}
        .section-title {{
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .chart {{
            margin: 30px 0;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .heatmap-container {{
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{ background: #d1fae5; color: #065f46; }}
        .badge-warning {{ background: #fed7aa; color: #92400e; }}
        .badge-danger {{ background: #fee2e2; color: #991b1b; }}
        .footer {{
            background: #f8f9fa;
            padding: 30px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{'🔥 Stress Test' if stress_test else '🎲 Monte Carlo Backtest'} Report</h1>
            <div class="subtitle">Polymarket Trading System Analysis</div>
            <div class="subtitle" style="margin-top: 10px; opacity: 0.7;">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
                Simulations: {len(results):,}
            </div>
        </div>

        <div class="metrics">
            <div class="metric-card">
                <div class="metric-label">Average Return</div>
                <div class="metric-value {'positive' if avg_return > 0 else 'negative'}">
                    {avg_return*100:+.2f}%
                </div>
                <div class="metric-ci">
                    95% CI: [{confidence_intervals['total_return'][1]*100:.2f}%, 
                    {confidence_intervals['total_return'][2]*100:.2f}%]
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">
                    {avg_sharpe:.3f}
                </div>
                <div class="metric-ci">
                    95% CI: [{confidence_intervals['sharpe_ratio'][1]:.3f}, 
                    {confidence_intervals['sharpe_ratio'][2]:.3f}]
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">
                    {avg_win_rate*100:.1f}%
                </div>
                <div class="metric-ci">
                    95% CI: [{confidence_intervals['win_rate'][1]*100:.1f}%, 
                    {confidence_intervals['win_rate'][2]*100:.1f}%]
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg Trades</div>
                <div class="metric-value">
                    {avg_trades:.0f}
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Max Drawdown (95th)</div>
                <div class="metric-value negative">
                    {drawdown_analysis['percentiles']['95th']*100:.2f}%
                </div>
                <div class="metric-ci">
                    Worst: {drawdown_analysis['max_drawdown']*100:.2f}%
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Probability of Ruin</div>
                <div class="metric-value {'negative' if drawdown_analysis['prob_of_ruin'] > 0.05 else 'positive'}">
                    {drawdown_analysis['prob_of_ruin']*100:.2f}%
                </div>
                <div class="metric-ci">
                    Circuit breaker: 25%
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">📊 Distribution Analysis</h2>
            
            <div class="chart" id="returns-hist"></div>
            <div class="chart" id="sharpe-hist"></div>
            <div class="chart" id="drawdown-hist"></div>
        </div>

        <div class="section">
            <h2 class="section-title">📉 Drawdown Analysis</h2>
            
            <table>
                <thead>
                    <tr>
                        <th>Percentile</th>
                        <th>Max Drawdown</th>
                        <th>Risk Level</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>50th (Median)</td>
                        <td>{drawdown_analysis['percentiles']['50th']*100:.2f}%</td>
                        <td><span class="badge badge-success">Low</span></td>
                    </tr>
                    <tr>
                        <td>75th</td>
                        <td>{drawdown_analysis['percentiles']['75th']*100:.2f}%</td>
                        <td><span class="badge badge-success">Moderate</span></td>
                    </tr>
                    <tr>
                        <td>90th</td>
                        <td>{drawdown_analysis['percentiles']['90th']*100:.2f}%</td>
                        <td><span class="badge badge-warning">Elevated</span></td>
                    </tr>
                    <tr>
                        <td>95th</td>
                        <td>{drawdown_analysis['percentiles']['95th']*100:.2f}%</td>
                        <td><span class="badge badge-warning">High</span></td>
                    </tr>
                    <tr>
                        <td>99th</td>
                        <td>{drawdown_analysis['percentiles']['99th']*100:.2f}%</td>
                        <td><span class="badge badge-danger">Critical</span></td>
                    </tr>
                </tbody>
            </table>
            
            <p style="margin-top: 20px; color: #666;">
                <strong>Expected Recovery Time:</strong> 
                {drawdown_analysis['avg_recovery_days']:.0f if drawdown_analysis['avg_recovery_days'] else 'N/A'} days
            </p>
        </div>
"""

        # Add sensitivity analysis if available
        if sensitivity_results:
            html += """
        <div class="section">
            <h2 class="section-title">🔬 Sensitivity Analysis</h2>
            <div class="chart" id="sensitivity-heatmap"></div>
            
            <table>
                <thead>
                    <tr>
                        <th>RVR Threshold</th>
                        <th>Stop Loss</th>
                        <th>Position Size</th>
                        <th>Avg Return</th>
                        <th>Avg Sharpe</th>
                        <th>Avg Drawdown</th>
                    </tr>
                </thead>
                <tbody>
"""
            
            # Sort by avg return
            sorted_results = sorted(sensitivity_results.items(), 
                                   key=lambda x: x[1]['avg_return'], 
                                   reverse=True)
            
            for params, metrics in sorted_results:
                rvr, sl, ps = params
                html += f"""
                    <tr>
                        <td>{rvr:.1f}</td>
                        <td>{sl*100:.0f}%</td>
                        <td>{ps*100:.0f}%</td>
                        <td class="{'positive' if metrics['avg_return'] > 0 else 'negative'}">
                            {metrics['avg_return']*100:+.2f}%
                        </td>
                        <td>{metrics['avg_sharpe']:.3f}</td>
                        <td class="negative">{metrics['avg_drawdown']*100:.2f}%</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
        </div>
"""

        html += """
        <div class="footer">
            <p><strong>Monte Carlo Backtester</strong> for Polymarket Trading System</p>
            <p style="margin-top: 10px;">
                ⚠️ Past performance does not guarantee future results. 
                This is a simulation based on historical patterns and should not be considered investment advice.
            </p>
        </div>
    </div>

    <script>
        // Returns distribution histogram
        const returnsData = """ + json.dumps(returns_dist) + """;
        Plotly.newPlot('returns-hist', [{
            x: returnsData,
            type: 'histogram',
            name: 'Returns',
            marker: { color: '#667eea' },
            nbinsx: 50
        }], {
            title: 'Total Returns Distribution',
            xaxis: { title: 'Return (%)' },
            yaxis: { title: 'Frequency' },
            showlegend: false
        }, {responsive: true});

        // Sharpe ratio distribution
        const sharpeData = """ + json.dumps(sharpe_dist) + """;
        Plotly.newPlot('sharpe-hist', [{
            x: sharpeData,
            type: 'histogram',
            marker: { color: '#10b981' },
            nbinsx: 50
        }], {
            title: 'Sharpe Ratio Distribution',
            xaxis: { title: 'Sharpe Ratio' },
            yaxis: { title: 'Frequency' },
            showlegend: false
        }, {responsive: true});

        // Drawdown distribution
        const drawdownData = """ + json.dumps(drawdown_dist) + """;
        Plotly.newPlot('drawdown-hist', [{
            x: drawdownData,
            type: 'histogram',
            marker: { color: '#ef4444' },
            nbinsx: 50
        }], {
            title: 'Maximum Drawdown Distribution',
            xaxis: { title: 'Max Drawdown (%)' },
            yaxis: { title: 'Frequency' },
            showlegend: false
        }, {responsive: true});
"""

        # Add sensitivity heatmap if available
        if sensitivity_results:
            # Create heatmap data for RVR vs Stop Loss (average across position sizes)
            rvr_values = sorted(set(k[0] for k in sensitivity_results.keys()))
            sl_values = sorted(set(k[1] for k in sensitivity_results.keys()))
            
            z_data = []
            for sl in sl_values:
                row = []
                for rvr in rvr_values:
                    # Average returns across all position sizes for this RVR/SL combo
                    returns = [v['avg_return'] for k, v in sensitivity_results.items() 
                              if k[0] == rvr and k[1] == sl]
                    avg = sum(returns) / len(returns) if returns else 0
                    row.append(avg * 100)
                z_data.append(row)
            
            html += """
        // Sensitivity heatmap
        const sensitivityZ = """ + json.dumps(z_data) + """;
        const rvrValues = """ + json.dumps(rvr_values) + """;
        const slValues = """ + json.dumps([sl*100 for sl in sl_values]) + """;
        
        Plotly.newPlot('sensitivity-heatmap', [{
            z: sensitivityZ,
            x: rvrValues,
            y: slValues,
            type: 'heatmap',
            colorscale: 'RdYlGn',
            reversescale: false,
            hoverongaps: false
        }], {
            title: 'Parameter Sensitivity: Average Return (%)',
            xaxis: { title: 'RVR Threshold' },
            yaxis: { title: 'Stop Loss (%)' }
        }, {responsive: true});
"""

        html += """
    </script>
</body>
</html>
"""

        # Write report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Report saved: {output_path}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description='Monte Carlo Backtester for Polymarket Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--runs', type=int, default=1000,
                       help='Number of Monte Carlo simulations (default: 1000)')
    parser.add_argument('--sensitivity', action='store_true',
                       help='Run parameter sensitivity analysis')
    parser.add_argument('--stress', action='store_true',
                       help='Run stress test with extreme conditions')
    parser.add_argument('--report', type=str,
                       help='Generate HTML report (specify output path)')
    parser.add_argument('--config', type=str,
                       help='Load configuration from JSON file')
    
    args = parser.parse_args()
    
    # Initialize configuration
    trade_config = TradeConfig()
    sim_config = SimulationConfig(num_runs=args.runs)
    
    # Load custom config if provided
    if args.config:
        with open(args.config, 'r') as f:
            config_data = json.load(f)
            for key, value in config_data.get('trade_config', {}).items():
                setattr(trade_config, key, value)
            for key, value in config_data.get('sim_config', {}).items():
                setattr(sim_config, key, value)
    
    # Initialize backtester
    backtester = MonteCarloBacktester(trade_config, sim_config)
    
    # Run analyses
    if args.sensitivity:
        sensitivity_results = backtester.sensitivity_analysis()
    else:
        sensitivity_results = None
    
    if args.stress:
        results = backtester.run_monte_carlo(stress_test=True)
    else:
        results = backtester.run_monte_carlo(stress_test=False)
    
    # Calculate statistics
    ci = backtester.calculate_confidence_intervals(results)
    dd_analysis = backtester.analyze_drawdowns(results)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 SUMMARY STATISTICS")
    print("="*60)
    print(f"Total Simulations: {len(results):,}")
    print(f"\nAverage Return: {ci['total_return'][0]*100:+.2f}% "
          f"[{ci['total_return'][1]*100:.2f}%, {ci['total_return'][2]*100:.2f}%]")
    print(f"Sharpe Ratio: {ci['sharpe_ratio'][0]:.3f} "
          f"[{ci['sharpe_ratio'][1]:.3f}, {ci['sharpe_ratio'][2]:.3f}]")
    print(f"Win Rate: {ci['win_rate'][0]*100:.1f}% "
          f"[{ci['win_rate'][1]*100:.1f}%, {ci['win_rate'][2]*100:.1f}%]")
    print(f"\nMax Drawdown (95th): {dd_analysis['percentiles']['95th']*100:.2f}%")
    print(f"Probability of Ruin: {dd_analysis['prob_of_ruin']*100:.2f}%")
    if dd_analysis['avg_recovery_days']:
        print(f"Avg Recovery Time: {dd_analysis['avg_recovery_days']:.0f} days")
    print("="*60)
    
    # Generate report if requested
    if args.report:
        HTMLReportGenerator.generate(
            results=results,
            confidence_intervals=ci,
            drawdown_analysis=dd_analysis,
            sensitivity_results=sensitivity_results,
            output_path=args.report,
            stress_test=args.stress
        )
    
    print("\n✅ Analysis complete! Great success! 🎉")


if __name__ == '__main__':
    main()
