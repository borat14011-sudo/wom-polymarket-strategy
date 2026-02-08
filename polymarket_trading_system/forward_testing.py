"""
Forward Testing Framework
=========================
Validates that backtest results translate to live markets.

Purpose:
- Track real-time performance vs backtest expectations
- Detect strategy degradation early
- Provide confidence for live deployment

Process:
1. Paper trade for 30+ days
2. Compare actual metrics vs backtest expectations
3. Alert if performance deviates >20% from expectations
4. Generate reports for decision-making
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import statistics


@dataclass
class BacktestBenchmark:
    """Expected performance from backtests"""
    metric_name: str
    expected_value: float
    expected_range: tuple[float, float]
    sample_size: int
    source: str


@dataclass
class ForwardTestResult:
    """Forward test performance"""
    metric_name: str
    actual_value: float
    expected_value: float
    delta_pct: float
    status: str  # 'EXCELLENT', 'GOOD', 'ACCEPTABLE', 'WARNING', 'FAILURE'
    sample_size: int


class ForwardTestingFramework:
    """
    Forward testing framework to validate strategy in live markets.
    """
    
    def __init__(self):
        # Backtest benchmarks from MASTER_REAL_BACKTEST_REPORT.md
        self.benchmarks = {
            'win_rate': BacktestBenchmark(
                metric_name='Win Rate',
                expected_value=0.58,
                expected_range=(0.55, 0.65),
                sample_size=1500,
                source='Adjusted from filter averages'
            ),
            'profit_factor': BacktestBenchmark(
                metric_name='Profit Factor',
                expected_value=1.8,
                expected_range=(1.6, 2.0),
                sample_size=1500,
                source='Average of validated strategies'
            ),
            'expectancy_per_trade': BacktestBenchmark(
                metric_name='Expectancy Per Trade',
                expected_value=0.025,
                expected_range=(0.020, 0.030),
                sample_size=1500,
                source='Weighted from proven filters'
            ),
            'max_drawdown': BacktestBenchmark(
                metric_name='Max Drawdown',
                expected_value=-0.20,
                expected_range=(-0.22, -0.18),
                sample_size=132,
                source='Volatility exit strategy'
            ),
            'avg_hold_hours': BacktestBenchmark(
                metric_name='Average Hold Time (hours)',
                expected_value=36.0,
                expected_range=(24.0, 60.0),
                sample_size=24,
                source='<3 day markets'
            ),
            'trades_per_month': BacktestBenchmark(
                metric_name='Trades Per Month',
                expected_value=10.0,
                expected_range=(8.0, 12.0),
                sample_size=4,
                source='After all filters applied'
            ),
            'no_side_win_rate': BacktestBenchmark(
                metric_name='NO-Side Win Rate',
                expected_value=0.82,
                expected_range=(0.75, 0.90),
                sample_size=22,
                source='NO-side bias backtest'
            ),
            'trend_win_rate': BacktestBenchmark(
                metric_name='Trend Filter Win Rate',
                expected_value=0.67,
                expected_range=(0.60, 0.75),
                sample_size=54,
                source='Trend filter backtest'
            ),
        }
        
        # Tolerance levels
        self.EXCELLENT_THRESHOLD = 0.10  # Within 10% of expected
        self.GOOD_THRESHOLD = 0.20       # Within 20% of expected
        self.ACCEPTABLE_THRESHOLD = 0.30  # Within 30% of expected
        
    def analyze_performance(self, trade_history: List[Dict]) -> Dict:
        """
        Analyze forward test performance vs backtests.
        
        Args:
            trade_history: List of completed trades from bot
            
        Returns:
            Forward test analysis report
        """
        if not trade_history:
            return {
                'status': 'INSUFFICIENT_DATA',
                'message': 'No trades to analyze',
                'results': []
            }
        
        # Calculate actual metrics
        actual_metrics = self._calculate_actual_metrics(trade_history)
        
        # Compare vs benchmarks
        results = []
        for metric_key, actual_value in actual_metrics.items():
            if metric_key in self.benchmarks:
                result = self._compare_metric(
                    metric_key,
                    actual_value,
                    len(trade_history)
                )
                results.append(result)
        
        # Overall assessment
        overall_status = self._assess_overall_status(results)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'test_duration_days': self._calculate_duration(trade_history),
            'total_trades': len(trade_history),
            'overall_status': overall_status,
            'results': [asdict(r) for r in results],
            'recommendation': self._generate_recommendation(overall_status, results)
        }
    
    def _calculate_actual_metrics(self, trade_history: List[Dict]) -> Dict:
        """Calculate actual metrics from trade history"""
        if not trade_history:
            return {}
        
        # Win rate
        wins = [t for t in trade_history if t['pnl'] > 0]
        win_rate = len(wins) / len(trade_history)
        
        # Profit factor
        total_wins = sum(t['pnl'] for t in wins)
        losses = [t for t in trade_history if t['pnl'] <= 0]
        total_losses = abs(sum(t['pnl'] for t in losses))
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        # Expectancy per trade
        expectancy = sum(t['pnl_pct'] for t in trade_history) / len(trade_history)
        
        # Max drawdown (simplified - would need equity curve in practice)
        cumulative_returns = []
        cumulative = 0
        for trade in sorted(trade_history, key=lambda x: x['exit_time']):
            cumulative += trade['pnl_pct']
            cumulative_returns.append(cumulative)
        
        peak = cumulative_returns[0]
        max_drawdown = 0
        for ret in cumulative_returns:
            if ret > peak:
                peak = ret
            drawdown = (ret - peak) / (1 + peak)
            if drawdown < max_drawdown:
                max_drawdown = drawdown
        
        # Average hold time
        avg_hold_hours = statistics.mean([t['hold_duration_hours'] for t in trade_history])
        
        # Trades per month
        duration_days = self._calculate_duration(trade_history)
        trades_per_month = len(trade_history) / (duration_days / 30) if duration_days > 0 else 0
        
        # Strategy-specific win rates
        no_side_trades = [t for t in trade_history if 'no_side' in str(t.get('filters_used', [])).lower()]
        no_side_win_rate = len([t for t in no_side_trades if t['pnl'] > 0]) / len(no_side_trades) if no_side_trades else None
        
        trend_trades = [t for t in trade_history if 'trend' in str(t.get('filters_used', [])).lower()]
        trend_win_rate = len([t for t in trend_trades if t['pnl'] > 0]) / len(trend_trades) if trend_trades else None
        
        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'expectancy_per_trade': expectancy,
            'max_drawdown': max_drawdown,
            'avg_hold_hours': avg_hold_hours,
            'trades_per_month': trades_per_month,
            'no_side_win_rate': no_side_win_rate,
            'trend_win_rate': trend_win_rate,
        }
    
    def _calculate_duration(self, trade_history: List[Dict]) -> float:
        """Calculate test duration in days"""
        if len(trade_history) < 2:
            return 0
        
        dates = [datetime.fromisoformat(t['exit_time']) if isinstance(t['exit_time'], str) else t['exit_time'] for t in trade_history]
        duration = (max(dates) - min(dates)).total_seconds() / 86400  # Convert to days
        return duration
    
    def _compare_metric(
        self, 
        metric_key: str, 
        actual_value: Optional[float],
        sample_size: int
    ) -> ForwardTestResult:
        """Compare actual metric vs benchmark"""
        benchmark = self.benchmarks[metric_key]
        
        if actual_value is None:
            return ForwardTestResult(
                metric_name=benchmark.metric_name,
                actual_value=0.0,
                expected_value=benchmark.expected_value,
                delta_pct=0.0,
                status='NO_DATA',
                sample_size=0
            )
        
        # Calculate delta percentage
        if benchmark.expected_value != 0:
            delta_pct = (actual_value - benchmark.expected_value) / abs(benchmark.expected_value)
        else:
            delta_pct = 0.0
        
        # Determine status
        abs_delta = abs(delta_pct)
        
        if abs_delta <= self.EXCELLENT_THRESHOLD:
            status = 'EXCELLENT'
        elif abs_delta <= self.GOOD_THRESHOLD:
            status = 'GOOD'
        elif abs_delta <= self.ACCEPTABLE_THRESHOLD:
            status = 'ACCEPTABLE'
        elif abs_delta <= 0.50:
            status = 'WARNING'
        else:
            status = 'FAILURE'
        
        # For metrics where lower is better (max_drawdown), invert the logic
        if metric_key == 'max_drawdown':
            # Less negative drawdown is better
            if actual_value > benchmark.expected_value:  # e.g., -15% > -20%
                if delta_pct >= -self.EXCELLENT_THRESHOLD:
                    status = 'EXCELLENT'
                elif delta_pct >= -self.GOOD_THRESHOLD:
                    status = 'GOOD'
                else:
                    status = 'ACCEPTABLE'
        
        return ForwardTestResult(
            metric_name=benchmark.metric_name,
            actual_value=actual_value,
            expected_value=benchmark.expected_value,
            delta_pct=delta_pct,
            status=status,
            sample_size=sample_size
        )
    
    def _assess_overall_status(self, results: List[ForwardTestResult]) -> str:
        """Assess overall forward test status"""
        if not results:
            return 'INSUFFICIENT_DATA'
        
        status_counts = {
            'EXCELLENT': 0,
            'GOOD': 0,
            'ACCEPTABLE': 0,
            'WARNING': 0,
            'FAILURE': 0,
            'NO_DATA': 0
        }
        
        for result in results:
            status_counts[result.status] += 1
        
        # Decision logic
        if status_counts['FAILURE'] > 0:
            return 'FAILURE'
        elif status_counts['WARNING'] >= 3:
            return 'WARNING'
        elif status_counts['WARNING'] >= 1:
            return 'ACCEPTABLE'
        elif status_counts['EXCELLENT'] >= len(results) * 0.7:
            return 'EXCELLENT'
        elif status_counts['GOOD'] >= len(results) * 0.5:
            return 'GOOD'
        else:
            return 'ACCEPTABLE'
    
    def _generate_recommendation(self, overall_status: str, results: List[ForwardTestResult]) -> str:
        """Generate actionable recommendation"""
        recommendations = {
            'EXCELLENT': (
                "✅ PROCEED TO LIVE TRADING\n"
                "Performance exceeds backtest expectations. "
                "Start with 10-25% of intended capital. "
                "Monitor closely for first 50 trades."
            ),
            'GOOD': (
                "✅ PROCEED TO LIVE TRADING (CAUTIOUSLY)\n"
                "Performance meets backtest expectations. "
                "Start with 10% of intended capital. "
                "Monitor closely and increase gradually."
            ),
            'ACCEPTABLE': (
                "⚠️ CONTINUE PAPER TRADING\n"
                "Performance is acceptable but below optimal. "
                "Extend paper trading another 30 days. "
                "Consider only live trading with 5% capital if urgent."
            ),
            'WARNING': (
                "❌ DO NOT GO LIVE YET\n"
                "Performance significantly below expectations. "
                "Review trades for patterns. "
                "Check filter implementation. "
                "Continue paper trading until metrics improve."
            ),
            'FAILURE': (
                "🚨 STOP - STRATEGY NOT WORKING\n"
                "Performance far below backtest expectations. "
                "Do NOT deploy live. "
                "Review code for bugs. "
                "Consider strategy may not work in current market conditions."
            ),
            'INSUFFICIENT_DATA': (
                "⏳ CONTINUE TESTING\n"
                "Not enough trades to make a decision. "
                "Continue paper trading. "
                "Minimum 30 trades recommended before assessment."
            )
        }
        
        base_rec = recommendations.get(overall_status, "Unknown status")
        
        # Add specific concerns
        concerns = []
        for result in results:
            if result.status in ['WARNING', 'FAILURE']:
                concerns.append(f"- {result.metric_name}: {result.actual_value:.2%} vs expected {result.expected_value:.2%}")
        
        if concerns:
            base_rec += "\n\n⚠️ Specific Concerns:\n" + "\n".join(concerns)
        
        return base_rec
    
    def generate_report(self, trade_history: List[Dict], output_format: str = 'text') -> str:
        """
        Generate forward test report.
        
        Args:
            trade_history: List of completed trades
            output_format: 'text' or 'json'
            
        Returns:
            Formatted report
        """
        analysis = self.analyze_performance(trade_history)
        
        if output_format == 'json':
            return json.dumps(analysis, indent=2)
        
        # Text format
        report = []
        report.append("=" * 70)
        report.append("FORWARD TEST REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {analysis['timestamp']}")
        report.append(f"Test Duration: {analysis['test_duration_days']:.1f} days")
        report.append(f"Total Trades: {analysis['total_trades']}")
        report.append(f"Overall Status: {analysis['overall_status']}")
        report.append("")
        
        report.append("Backtest Expectations vs Actual:")
        report.append("-" * 70)
        report.append(f"{'METRIC':<30} {'EXPECTED':<12} {'ACTUAL':<12} {'DELTA':<10} {'STATUS'}")
        report.append("-" * 70)
        
        for result in analysis['results']:
            metric = result['metric_name']
            expected = result['expected_value']
            actual = result['actual_value']
            delta = result['delta_pct']
            status = result['status']
            
            # Format based on metric type
            if 'rate' in metric.lower() or 'drawdown' in metric.lower():
                expected_str = f"{expected*100:.1f}%"
                actual_str = f"{actual*100:.1f}%"
            elif 'factor' in metric.lower():
                expected_str = f"{expected:.2f}x"
                actual_str = f"{actual:.2f}x"
            elif 'hours' in metric.lower():
                expected_str = f"{expected:.1f}h"
                actual_str = f"{actual:.1f}h"
            elif 'month' in metric.lower():
                expected_str = f"{expected:.1f}"
                actual_str = f"{actual:.1f}"
            else:
                expected_str = f"{expected:.4f}"
                actual_str = f"{actual:.4f}"
            
            delta_str = f"{delta*100:+.1f}%"
            
            status_emoji = {
                'EXCELLENT': '🟢',
                'GOOD': '✅',
                'ACCEPTABLE': '⚠️',
                'WARNING': '🟠',
                'FAILURE': '🔴',
                'NO_DATA': '⚪'
            }.get(status, '❓')
            
            report.append(f"{metric:<30} {expected_str:<12} {actual_str:<12} {delta_str:<10} {status_emoji}")
        
        report.append("-" * 70)
        report.append("")
        report.append("RECOMMENDATION:")
        report.append("-" * 70)
        report.append(analysis['recommendation'])
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def monitor_live_performance(self, trade_history: List[Dict]) -> Dict:
        """
        Continuously monitor live trading performance.
        
        Detects strategy degradation in real-time.
        """
        analysis = self.analyze_performance(trade_history)
        
        # Check for degradation
        degradation_alerts = []
        
        for result_dict in analysis['results']:
            result = ForwardTestResult(**result_dict)
            
            # Critical metrics
            if result.metric_name in ['Win Rate', 'Profit Factor']:
                if result.status in ['WARNING', 'FAILURE']:
                    degradation_alerts.append({
                        'severity': 'HIGH',
                        'metric': result.metric_name,
                        'message': f"{result.metric_name} at {result.actual_value:.2%}, expected {result.expected_value:.2%}"
                    })
            
            # Check for consistent underperformance
            if result.delta_pct < -0.30:  # 30%+ below expected
                degradation_alerts.append({
                    'severity': 'CRITICAL',
                    'metric': result.metric_name,
                    'message': f"{result.metric_name} 30%+ below expectations - REVIEW STRATEGY"
                })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'status': analysis['overall_status'],
            'alerts': degradation_alerts,
            'action_required': len(degradation_alerts) > 0
        }


def load_trade_history(filepath: str = "data/trade_history.json") -> List[Dict]:
    """Load trade history from file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_forward_test_report(report: str, filepath: str = "forward_test_report.txt"):
    """Save report to file"""
    with open(filepath, 'w') as f:
        f.write(report)
    print(f"Report saved to {filepath}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Forward Testing Framework")
    parser.add_argument('--report', choices=['weekly', 'monthly', 'current'], default='current',
                        help='Generate report')
    parser.add_argument('--compare', action='store_true',
                        help='Compare actual vs backtest expectations')
    parser.add_argument('--monitor', action='store_true',
                        help='Monitor for strategy degradation')
    parser.add_argument('--trade-file', default='data/trade_history.json',
                        help='Path to trade history file')
    
    args = parser.parse_args()
    
    framework = ForwardTestingFramework()
    trades = load_trade_history(args.trade_file)
    
    if args.monitor:
        monitoring = framework.monitor_live_performance(trades)
        print(json.dumps(monitoring, indent=2))
        
        if monitoring['action_required']:
            print("\n🚨 ACTION REQUIRED - Review alerts above!")
    
    else:
        report = framework.generate_report(trades, output_format='text')
        print(report)
        
        if args.compare:
            save_forward_test_report(report)
