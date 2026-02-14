"""
Demonstration of the backtesting system with a simple strategy.
"""
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from data_pipeline import PolymarketData
from core import BacktestEngine
from validation import ValidationFramework

def demo_simple_strategy():
    """Demo with synthetic data since real price history is missing."""
    print("=== Polymarket Backtesting System Demo ===\n")
    
    # 1. Load data
    data_loader = PolymarketData()
    print("Loading resolved markets...")
    resolved = data_loader.load_resolved_markets()
    print(f"Loaded {len(resolved)} resolved markets.")
    
    # 2. Create synthetic price history for demonstration
    # In a real scenario, we would fetch historical price feeds
    print("\nGenerating synthetic price history for demo...")
    np.random.seed(42)
    n_markets = 10
    synthetic_data = []
    for i in range(n_markets):
        market_id = f"demo_market_{i}"
        # Simulate 100 time steps
        base_price = np.random.uniform(0.1, 0.9)
        for t in range(100):
            timestamp = pd.Timestamp('2025-01-01') + pd.Timedelta(hours=t)
            # Random walk with mean reversion
            if t == 0:
                price = base_price
            else:
                price = synthetic_data[-1]['price'] + np.random.normal(0, 0.02)
                price = np.clip(price, 0.01, 0.99)
            volume = np.random.lognormal(3, 1)
            liquidity = np.random.lognormal(4, 1)
            synthetic_data.append({
                'market_id': market_id,
                'timestamp': timestamp,
                'price': price,
                'volume': volume,
                'liquidity': liquidity
            })
    df = pd.DataFrame(synthetic_data)
    print(f"Synthetic data shape: {df.shape}")
    
    # 3. Define a simple strategy: buy when price < 0.3, sell when price > 0.7
    def entry_rule(row):
        return row['price'] < 0.3
    
    def exit_rule(row):
        return row['price'] > 0.7
    
    def position_sizing(row, capital):
        # Risk 2% of capital per trade
        return 0.02
    
    # 4. Run backtest
    engine = BacktestEngine(df, initial_capital=10000)
    trades = engine.run_strategy(entry_rule, exit_rule, position_sizing, verbose=False)
    
    print(f"\nBacktest completed. Generated {len(trades)} trades.")
    if len(trades) > 0:
        print(trades[['market_id', 'entry_price', 'exit_price', 'pnl', 'roi']].head())
        
        # 5. Compute metrics
        metrics = engine.compute_metrics(trades)
        print("\n=== Strategy Performance ===")
        for key, val in metrics.items():
            if isinstance(val, float):
                print(f"{key}: {val:.4f}")
            else:
                print(f"{key}: {val}")
        
        # 6. Statistical validation
        print("\n=== Statistical Validation ===")
        returns = trades['roi'].values
        if len(returns) > 10:
            bootstrap = ValidationFramework.bootstrap_returns(returns, n_iterations=1000)
            print(f"Sharpe 95% CI: {bootstrap['sharpe_ci']}")
            print(f"P(Sharpe <= 0): {bootstrap['p_sharpe']:.4f}")
            
            var_cvar = ValidationFramework.compute_var_cvar(returns)
            print(f"VaR (95%): {var_cvar['var']:.4f}")
            print(f"CVaR (95%): {var_cvar['cvar']:.4f}")
            
            # Walk-forward analysis
            wf = ValidationFramework.walk_forward_analysis(trades, train_ratio=0.7)
            if wf:
                print(f"Walk-forward degradation: {wf['performance_degradation']:.4f}")
                print(f"Train-test correlation: {wf['train_test_correlation']:.4f}")
    else:
        print("No trades generated.")
    
    print("\n=== Demo Completed ===")
    return trades

if __name__ == '__main__':
    demo_simple_strategy()