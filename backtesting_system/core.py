"""
Core backtesting engine for Polymarket strategies.
"""
import pandas as pd
import numpy as np
from typing import Callable, Dict, List, Optional
import warnings

class BacktestEngine:
    """Generic backtesting engine for prediction market strategies."""
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000.0):
        """
        Args:
            data: DataFrame with columns ['market_id', 'timestamp', 'price', 'volume', 'liquidity', ...]
            initial_capital: Starting capital in USD
        """
        self.data = data.sort_values(['market_id', 'timestamp']).reset_index(drop=True)
        self.initial_capital = initial_capital
        self.results = None
        
    def run_strategy(self, 
                     entry_rule: Callable,
                     exit_rule: Callable,
                     position_sizing: Callable = None,
                     fees: Dict = None,
                     verbose: bool = False) -> pd.DataFrame:
        """
        Run a strategy defined by entry and exit rules.
        
        Args:
            entry_rule: Function that takes a row and returns True to enter a long position
            exit_rule: Function that takes a row and returns True to exit the position
            position_sizing: Function that returns position size as fraction of capital
            fees: Dict with 'entry_fee' and 'exit_fee' as percentages (e.g., 0.02 for 2%)
            verbose: Print debug information
            
        Returns:
            DataFrame with trade records
        """
        if fees is None:
            fees = {'entry_fee': 0.02, 'exit_fee': 0.02}
            
        if position_sizing is None:
            position_sizing = lambda row, capital: 0.1  # 10% of capital
            
        trades = []
        capital = self.initial_capital
        open_position = None
        trade_id = 0
        
        # Group by market to handle each market separately
        for market_id, group in self.data.groupby('market_id'):
            if verbose:
                print(f"Processing market {market_id}")
                
            for i, row in group.iterrows():
                # Check for exit if we have an open position
                if open_position is not None:
                    if exit_rule(row):
                        # Calculate exit
                        exit_price = row['price']
                        entry_price = open_position['entry_price']
                        shares = open_position['shares']
                        
                        # Apply exit fee
                        exit_proceeds = shares * exit_price * (1 - fees['exit_fee'])
                        entry_cost = shares * entry_price * (1 + fees['entry_fee'])
                        pnl = exit_proceeds - entry_cost
                        roi = pnl / entry_cost if entry_cost != 0 else 0
                        
                        trade = {
                            'trade_id': trade_id,
                            'market_id': market_id,
                            'entry_date': open_position['entry_date'],
                            'exit_date': row['timestamp'],
                            'entry_price': entry_price,
                            'exit_price': exit_price,
                            'shares': shares,
                            'pnl': pnl,
                            'roi': roi,
                            'capital_after': capital + pnl
                        }
                        trades.append(trade)
                        capital += pnl
                        trade_id += 1
                        open_position = None
                        if verbose:
                            print(f"  Exited at {exit_price}, PnL: {pnl:.2f}, Capital: {capital:.2f}")
                
                # Check for entry if no open position
                if open_position is None and entry_rule(row):
                    position_size = position_sizing(row, capital)
                    entry_price = row['price']
                    # Calculate shares we can buy with position_size of capital
                    shares = (capital * position_size) / (entry_price * (1 + fees['entry_fee']))
                    open_position = {
                        'entry_date': row['timestamp'],
                        'entry_price': entry_price,
                        'shares': shares
                    }
                    if verbose:
                        print(f"  Entered at {entry_price}, shares: {shares:.2f}")
        
        # Close any remaining position at last price
        if open_position is not None:
            last_row = self.data[self.data['market_id'] == market_id].iloc[-1]
            exit_price = last_row['price']
            entry_price = open_position['entry_price']
            shares = open_position['shares']
            exit_proceeds = shares * exit_price * (1 - fees['exit_fee'])
            entry_cost = shares * entry_price * (1 + fees['entry_fee'])
            pnl = exit_proceeds - entry_cost
            roi = pnl / entry_cost if entry_cost != 0 else 0
            trade = {
                'trade_id': trade_id,
                'market_id': market_id,
                'entry_date': open_position['entry_date'],
                'exit_date': last_row['timestamp'],
                'entry_price': entry_price,
                'exit_price': exit_price,
                'shares': shares,
                'pnl': pnl,
                'roi': roi,
                'capital_after': capital + pnl
            }
            trades.append(trade)
            capital += pnl
        
        self.results = pd.DataFrame(trades)
        return self.results
    
    def compute_metrics(self, results: pd.DataFrame = None) -> Dict:
        """Compute performance metrics from trade results."""
        if results is None:
            if self.results is None:
                raise ValueError("No results available. Run strategy first.")
            results = self.results
        
        if len(results) == 0:
            return {}
        
        # Basic metrics
        total_trades = len(results)
        winning_trades = (results['pnl'] > 0).sum()
        win_rate = winning_trades / total_trades
        
        total_pnl = results['pnl'].sum()
        avg_pnl = results['pnl'].mean()
        avg_roi = results['roi'].mean()
        median_roi = results['roi'].median()
        
        # Sharpe ratio (approximate annualized)
        if 'holding_days' not in results.columns:
            results['holding_days'] = (pd.to_datetime(results['exit_date']) - 
                                       pd.to_datetime(results['entry_date'])).dt.total_seconds() / (24*3600)
        results['daily_return'] = np.where(results['holding_days'] > 0,
                                           (1 + results['roi']) ** (1/results['holding_days']) - 1,
                                           0)
        if results['daily_return'].std() > 0:
            sharpe = results['daily_return'].mean() / results['daily_return'].std() * np.sqrt(252)
        else:
            sharpe = np.nan
        
        # Max drawdown from equity curve
        results = results.sort_values('exit_date')
        equity = self.initial_capital + results['pnl'].cumsum()
        peak = equity.expanding().max()
        drawdown = (equity - peak) / peak
        max_drawdown = drawdown.min()
        
        # Profit factor
        gross_profit = results[results['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(results[results['pnl'] < 0]['pnl'].sum())
        profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf
        
        metrics = {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'avg_roi': avg_roi,
            'median_roi': median_roi,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'profit_factor': profit_factor,
            'final_capital': equity.iloc[-1] if len(equity) > 0 else self.initial_capital
        }
        return metrics