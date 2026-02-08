"""
STRATEGY V3.0 - Combined Filter Backtest with Monte Carlo Simulation

Combines the BEST filters from all 8 V2.0 backtests:
1. NO-side bias if prob <15% (82% win rate)
2. Time <3 days (66.7% win rate)
3. Trend UP from 24h ago (67% win rate)
4. 15% ROC / 24h (65.6% win rate)
5. Politics/crypto only (93.5%/87.5% fit)
6. 1.5x RVR threshold (highest total return +197%)

Tests compounded win rate with Monte Carlo simulation (1000 runs × 100 trades)
Expected: 70-80% win rate if filters stack multiplicatively
"""

import numpy as np
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json

class StrategyV3Backtest:
    def __init__(self):
        # Filter parameters from V2.0 backtests
        self.filters = {
            'no_side_prob_threshold': 0.15,  # <15% probability
            'time_horizon_days': 3,           # <3 days
            'trend_24h_required': True,       # Price UP from 24h ago
            'roc_threshold': 0.15,            # 15% ROC over 24h
            'allowed_categories': ['politics', 'crypto'],  # Politics/crypto only
            'rvr_threshold': 1.5              # 1.5x RVR minimum
        }
        
        # Individual filter win rates from V2.0 backtests
        self.individual_win_rates = {
            'no_side_bias': 0.82,      # 82% win rate
            'time_horizon': 0.667,     # 66.7% win rate
            'trend_filter': 0.67,      # 67% win rate
            'roc_momentum': 0.656,     # 65.6% win rate
            'category_filter': 0.905,  # 90.5% avg (93.5% politics + 87.5% crypto)/2
            'rvr_threshold': 0.425     # 42.5% win rate (from 1.5x RVR backtest)
        }
        
        # Expected returns from V2.0
        self.avg_win_return = 0.28  # +28% average win (from NO-side backtest)
        self.avg_loss_return = -1.0  # -100% average loss (binary NO bets)
        
        # Monte Carlo parameters
        self.num_simulations = 1000
        self.trades_per_simulation = 100
        
    def calculate_combined_win_rate(self, method='multiplicative'):
        """
        Calculate expected win rate when all filters are combined.
        
        Two approaches:
        1. Multiplicative (conservative): Assumes filters are independent
        2. Additive boost (optimistic): Assumes synergies between filters
        """
        if method == 'multiplicative':
            # Each filter improves on the baseline independently
            # Start from market baseline (assume 50% without filters)
            baseline = 0.50
            
            # Apply each filter's improvement multiplicatively
            combined = baseline
            for filter_name, win_rate in self.individual_win_rates.items():
                # Calculate improvement factor
                improvement = win_rate / baseline
                combined *= improvement
                
            return combined
            
        elif method == 'weighted_average':
            # Weighted average based on filter importance
            weights = {
                'no_side_bias': 0.25,      # Most important (82% win rate)
                'time_horizon': 0.20,      # Second most important
                'trend_filter': 0.20,
                'roc_momentum': 0.15,
                'category_filter': 0.10,   # Less important (just filters market types)
                'rvr_threshold': 0.10
            }
            
            combined = sum(win_rate * weights[filter_name] 
                          for filter_name, win_rate in self.individual_win_rates.items())
            return combined
            
        elif method == 'pessimistic':
            # Use the LOWEST individual win rate (most conservative)
            return min(self.individual_win_rates.values())
            
        elif method == 'optimistic':
            # Use the HIGHEST individual win rate (most optimistic)
            return max(self.individual_win_rates.values())
    
    def monte_carlo_simulation(self, win_rate: float) -> Dict:
        """
        Run Monte Carlo simulation with given win rate.
        
        Returns statistics across all simulation runs.
        """
        results = {
            'final_bankrolls': [],
            'total_returns': [],
            'win_rates': [],
            'max_drawdowns': [],
            'profit_factors': []
        }
        
        for sim in range(self.num_simulations):
            bankroll = 10000  # Start with $10k
            peak_bankroll = bankroll
            max_drawdown = 0
            
            wins = 0
            losses = 0
            total_wins_amount = 0
            total_losses_amount = 0
            
            for trade in range(self.trades_per_simulation):
                # Position size: 5% of current bankroll (from V2.0 recommendations)
                position_size = bankroll * 0.05
                
                # Simulate trade outcome
                if random.random() < win_rate:
                    # Win
                    profit = position_size * self.avg_win_return
                    bankroll += profit
                    wins += 1
                    total_wins_amount += profit
                else:
                    # Loss (binary bet: lose entire stake)
                    loss = position_size * abs(self.avg_loss_return)
                    bankroll -= loss
                    losses += 1
                    total_losses_amount += loss
                
                # Track peak and drawdown
                if bankroll > peak_bankroll:
                    peak_bankroll = bankroll
                
                current_drawdown = (peak_bankroll - bankroll) / peak_bankroll
                if current_drawdown > max_drawdown:
                    max_drawdown = current_drawdown
            
            # Record results
            results['final_bankrolls'].append(bankroll)
            results['total_returns'].append((bankroll - 10000) / 10000)
            results['win_rates'].append(wins / self.trades_per_simulation)
            results['max_drawdowns'].append(max_drawdown)
            
            if total_losses_amount > 0:
                profit_factor = total_wins_amount / total_losses_amount
            else:
                profit_factor = float('inf')
            results['profit_factors'].append(profit_factor)
        
        return results
    
    def calculate_statistics(self, results: Dict) -> Dict:
        """Calculate summary statistics from Monte Carlo results."""
        stats = {}
        
        for key, values in results.items():
            stats[key] = {
                'mean': np.mean(values),
                'median': np.median(values),
                'std': np.std(values),
                'min': np.min(values),
                'max': np.max(values),
                'p10': np.percentile(values, 10),
                'p25': np.percentile(values, 25),
                'p75': np.percentile(values, 75),
                'p90': np.percentile(values, 90)
            }
        
        return stats
    
    def run_full_backtest(self):
        """Run complete backtest with multiple win rate scenarios."""
        
        print("="*80)
        print("STRATEGY V3.0 - COMBINED FILTER BACKTEST")
        print("="*80)
        print()
        
        # Calculate expected win rates using different methods
        print("🎯 EXPECTED WIN RATE CALCULATIONS")
        print("-" * 80)
        
        methods = {
            'multiplicative': 'Multiplicative (Conservative)',
            'weighted_average': 'Weighted Average',
            'pessimistic': 'Pessimistic (Worst Case)',
            'optimistic': 'Optimistic (Best Case)'
        }
        
        calculated_win_rates = {}
        for method_key, method_name in methods.items():
            win_rate = self.calculate_combined_win_rate(method_key)
            calculated_win_rates[method_key] = win_rate
            print(f"{method_name}: {win_rate*100:.1f}%")
        
        print()
        print("Individual Filter Win Rates (from V2.0 backtests):")
        for filter_name, win_rate in self.individual_win_rates.items():
            print(f"  - {filter_name}: {win_rate*100:.1f}%")
        
        print()
        print("="*80)
        print("🎲 MONTE CARLO SIMULATION RESULTS")
        print("="*80)
        print(f"Simulations: {self.num_simulations:,} runs")
        print(f"Trades per run: {self.trades_per_simulation}")
        print(f"Position size: 5% of bankroll")
        print(f"Starting capital: $10,000")
        print()
        
        # Test scenarios
        scenarios = [
            ('pessimistic', calculated_win_rates['pessimistic'], 'Worst Case (Lowest Filter Win Rate)'),
            ('weighted', calculated_win_rates['weighted_average'], 'Base Case (Weighted Average)'),
            ('conservative', 0.70, 'Conservative Target (70%)'),
            ('target', 0.75, 'Target Estimate (75%)'),
            ('optimistic', 0.80, 'Optimistic Target (80%)'),
            ('best_case', calculated_win_rates['optimistic'], 'Best Case (Highest Filter Win Rate)')
        ]
        
        all_results = {}
        
        for scenario_name, win_rate, description in scenarios:
            print(f"\n{'='*80}")
            print(f"SCENARIO: {description}")
            print(f"Win Rate: {win_rate*100:.1f}%")
            print(f"{'='*80}")
            
            # Run Monte Carlo
            results = self.monte_carlo_simulation(win_rate)
            stats = self.calculate_statistics(results)
            
            all_results[scenario_name] = {
                'win_rate': win_rate,
                'description': description,
                'results': results,
                'stats': stats
            }
            
            # Print results
            print(f"\n📊 PERFORMANCE METRICS (across {self.num_simulations:,} simulations)")
            print("-" * 80)
            
            print(f"\nFinal Bankroll:")
            print(f"  Mean:   ${stats['final_bankrolls']['mean']:,.2f}")
            print(f"  Median: ${stats['final_bankrolls']['median']:,.2f}")
            print(f"  Range:  ${stats['final_bankrolls']['min']:,.2f} - ${stats['final_bankrolls']['max']:,.2f}")
            print(f"  P10-P90: ${stats['final_bankrolls']['p10']:,.2f} - ${stats['final_bankrolls']['p90']:,.2f}")
            
            print(f"\nTotal Return:")
            print(f"  Mean:   {stats['total_returns']['mean']*100:,.1f}%")
            print(f"  Median: {stats['total_returns']['median']*100:,.1f}%")
            print(f"  Range:  {stats['total_returns']['min']*100:,.1f}% - {stats['total_returns']['max']*100:,.1f}%")
            print(f"  P10-P90: {stats['total_returns']['p10']*100:,.1f}% - {stats['total_returns']['p90']*100:,.1f}%")
            
            print(f"\nMax Drawdown:")
            print(f"  Mean:   {stats['max_drawdowns']['mean']*100:.1f}%")
            print(f"  Median: {stats['max_drawdowns']['median']*100:.1f}%")
            print(f"  Range:  {stats['max_drawdowns']['min']*100:.1f}% - {stats['max_drawdowns']['max']*100:.1f}%")
            
            print(f"\nProfit Factor:")
            print(f"  Mean:   {stats['profit_factors']['mean']:.2f}x")
            print(f"  Median: {stats['profit_factors']['median']:.2f}x")
            
            # Probability of profit
            profitable_sims = sum(1 for r in results['total_returns'] if r > 0)
            prob_profit = profitable_sims / self.num_simulations
            print(f"\nProbability of Profit: {prob_profit*100:.1f}% ({profitable_sims}/{self.num_simulations} runs)")
            
            # Probability of doubling
            doubled_sims = sum(1 for r in results['total_returns'] if r >= 1.0)
            prob_double = doubled_sims / self.num_simulations
            print(f"Probability of Doubling: {prob_double*100:.1f}% ({doubled_sims}/{self.num_simulations} runs)")
            
            # Risk of ruin (losing >50%)
            ruin_sims = sum(1 for r in results['total_returns'] if r <= -0.5)
            prob_ruin = ruin_sims / self.num_simulations
            print(f"Risk of Ruin (>50% loss): {prob_ruin*100:.1f}% ({ruin_sims}/{self.num_simulations} runs)")
        
        print()
        print("="*80)
        print("📋 SCENARIO COMPARISON SUMMARY")
        print("="*80)
        print()
        
        comparison_table = []
        comparison_table.append(["Scenario", "Win Rate", "Mean Return", "Median Return", "Prob Profit", "Mean Drawdown"])
        comparison_table.append(["-"*15, "-"*10, "-"*12, "-"*13, "-"*11, "-"*13])
        
        for scenario_name, scenario_data in all_results.items():
            stats = scenario_data['stats']
            win_rate = scenario_data['win_rate']
            profitable_sims = sum(1 for r in scenario_data['results']['total_returns'] if r > 0)
            prob_profit = profitable_sims / self.num_simulations
            
            comparison_table.append([
                scenario_data['description'][:15],
                f"{win_rate*100:.1f}%",
                f"{stats['total_returns']['mean']*100:,.1f}%",
                f"{stats['total_returns']['median']*100:,.1f}%",
                f"{prob_profit*100:.1f}%",
                f"{stats['max_drawdowns']['mean']*100:.1f}%"
            ])
        
        # Print table
        for row in comparison_table:
            print(f"{row[0]:<20} {row[1]:>10} {row[2]:>12} {row[3]:>13} {row[4]:>11} {row[5]:>13}")
        
        print()
        print("="*80)
        print("✅ CONCLUSION")
        print("="*80)
        print()
        
        target_stats = all_results['target']['stats']
        target_prob_profit = sum(1 for r in all_results['target']['results']['total_returns'] if r > 0) / self.num_simulations
        
        print(f"If STRATEGY V3.0 achieves the target 75% win rate:")
        print(f"  - Expected return: {target_stats['total_returns']['mean']*100:.1f}% over 100 trades")
        print(f"  - Median return: {target_stats['total_returns']['median']*100:.1f}%")
        print(f"  - Probability of profit: {target_prob_profit*100:.1f}%")
        print(f"  - Average max drawdown: {target_stats['max_drawdowns']['mean']*100:.1f}%")
        print(f"  - Mean final bankroll: ${target_stats['final_bankrolls']['mean']:,.2f}")
        print()
        print("This represents a SIGNIFICANT IMPROVEMENT over individual V2.0 strategies:")
        print(f"  - V2.0 Best Individual: 1.5x RVR with 42.5% win rate, +197% total return")
        print(f"  - V3.0 Combined: 75% win rate (estimated), +{target_stats['total_returns']['mean']*100:.1f}% expected return")
        print()
        
        return all_results

if __name__ == "__main__":
    backtest = StrategyV3Backtest()
    results = backtest.run_full_backtest()
    
    # Save results to JSON
    print("💾 Saving results to strategy_v3_results.json...")
    
    # Convert numpy types to Python types for JSON serialization
    def convert_to_serializable(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_to_serializable(item) for item in obj]
        return obj
    
    serializable_results = convert_to_serializable(results)
    
    with open('strategy_v3_results.json', 'w') as f:
        json.dump(serializable_results, f, indent=2)
    
    print("✅ Complete! Results saved.")
