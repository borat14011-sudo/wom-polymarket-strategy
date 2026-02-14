"""
Statistical validation framework for backtesting results.
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional
from scipy import stats
import warnings

class ValidationFramework:
    """Statistical validation of backtest results."""
    
    @staticmethod
    def bootstrap_returns(returns: np.ndarray, n_iterations: int = 10000, 
                          alpha: float = 0.05) -> dict:
        """
        Bootstrap confidence intervals for Sharpe ratio and mean return.
        
        Args:
            returns: Array of periodic returns (e.g., daily)
            n_iterations: Number of bootstrap samples
            alpha: Significance level
            
        Returns:
            Dictionary with confidence intervals and p-values
        """
        n = len(returns)
        bootstrapped_sharpe = []
        bootstrapped_mean = []
        
        for _ in range(n_iterations):
            sample = np.random.choice(returns, size=n, replace=True)
            if sample.std() > 0:
                sharpe = sample.mean() / sample.std() * np.sqrt(252)
            else:
                sharpe = 0
            bootstrapped_sharpe.append(sharpe)
            bootstrapped_mean.append(sample.mean())
        
        ci_sharpe = np.percentile(bootstrapped_sharpe, [100*alpha/2, 100*(1-alpha/2)])
        ci_mean = np.percentile(bootstrapped_mean, [100*alpha/2, 100*(1-alpha/2)])
        
        # p-value for H0: Sharpe <= 0
        p_sharpe = (np.array(bootstrapped_sharpe) <= 0).mean()
        p_mean = (np.array(bootstrapped_mean) <= 0).mean()
        
        return {
            'sharpe_ci': ci_sharpe,
            'mean_ci': ci_mean,
            'p_sharpe': p_sharpe,
            'p_mean': p_mean,
            'sharpe_distribution': bootstrapped_sharpe,
            'mean_distribution': bootstrapped_mean
        }
    
    @staticmethod
    def monte_carlo_paths(returns: np.ndarray, n_paths: int = 1000, 
                          periods: int = 252) -> np.ndarray:
        """
        Generate Monte Carlo simulated equity paths.
        
        Args:
            returns: Historical returns (assumed stationary)
            n_paths: Number of simulated paths
            periods: Number of periods per path
            
        Returns:
            Array of shape (n_paths, periods) with cumulative returns
        """
        n = len(returns)
        paths = np.zeros((n_paths, periods))
        for i in range(n_paths):
            # Sample with replacement
            sampled_returns = np.random.choice(returns, size=periods, replace=True)
            paths[i] = np.cumprod(1 + sampled_returns)
        return paths
    
    @staticmethod
    def compute_var_cvar(returns: np.ndarray, alpha: float = 0.05) -> dict:
        """
        Compute Value at Risk (VaR) and Conditional VaR (CVaR).
        
        Args:
            returns: Periodic returns
            alpha: Confidence level (e.g., 0.05 for 95% VaR)
            
        Returns:
            Dictionary with VaR and CVaR
        """
        var = np.percentile(returns, 100 * alpha)
        cvar = returns[returns <= var].mean()
        return {'var': var, 'cvar': cvar}
    
    @staticmethod
    def walk_forward_analysis(trades: pd.DataFrame, 
                              train_ratio: float = 0.7,
                              min_trades: int = 20) -> dict:
        """
        Perform walk-forward validation (time-series cross-validation).
        
        Args:
            trades: DataFrame with columns ['entry_date', 'roi']
            train_ratio: Proportion of data used for training each fold
            min_trades: Minimum number of trades per fold
            
        Returns:
            Dictionary with out-of-sample performance metrics
        """
        trades = trades.sort_values('entry_date').reset_index(drop=True)
        n_trades = len(trades)
        if n_trades < min_trades * 2:
            warnings.warn(f"Insufficient trades for walk-forward. Total: {n_trades}")
            return {}
        
        train_size = int(n_trades * train_ratio)
        oos_results = []
        
        for start in range(0, n_trades - train_size, max(1, train_size // 5)):
            end_train = start + train_size
            train = trades.iloc[start:end_train]
            test = trades.iloc[end_train:min(end_train + train_size, n_trades)]
            
            if len(test) < 5:
                break
            
            # Compute metrics on train and test
            train_roi = train['roi'].mean()
            test_roi = test['roi'].mean()
            oos_results.append({
                'train_start': train['entry_date'].iloc[0],
                'train_end': train['entry_date'].iloc[-1],
                'test_start': test['entry_date'].iloc[0],
                'test_end': test['entry_date'].iloc[-1],
                'train_roi': train_roi,
                'test_roi': test_roi,
                'train_trades': len(train),
                'test_trades': len(test)
            })
        
        oos_df = pd.DataFrame(oos_results)
        if len(oos_df) == 0:
            return {}
        
        # Compute degradation metric
        degradation = oos_df['test_roi'].mean() - oos_df['train_roi'].mean()
        correlation = oos_df['train_roi'].corr(oos_df['test_roi'])
        
        return {
            'walk_forward_results': oos_df,
            'average_train_roi': oos_df['train_roi'].mean(),
            'average_test_roi': oos_df['test_roi'].mean(),
            'performance_degradation': degradation,
            'train_test_correlation': correlation
        }
    
    @staticmethod
    def strategy_stability(trades: pd.DataFrame, 
                           window_size: int = 30) -> dict:
        """
        Analyze strategy stability over rolling windows.
        
        Args:
            trades: DataFrame with columns ['entry_date', 'roi']
            window_size: Number of trades per window
            
        Returns:
            Dictionary with stability metrics
        """
        trades = trades.sort_values('entry_date').reset_index(drop=True)
        n = len(trades)
        if n < window_size * 2:
            return {}
        
        rolling_roi = []
        for i in range(n - window_size + 1):
            window = trades.iloc[i:i+window_size]
            rolling_roi.append(window['roi'].mean())
        
        rolling_roi = np.array(rolling_roi)
        stability = rolling_roi.std() / (abs(rolling_roi.mean()) + 1e-10)
        
        return {
            'rolling_roi': rolling_roi,
            'stability_metric': stability,
            'rolling_std': rolling_roi.std(),
            'rolling_mean': rolling_roi.mean()
        }