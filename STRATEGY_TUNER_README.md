# Strategy Tuner - ML-based Parameter Optimization

Automated parameter tuning system for Polymarket trading strategy. Optimizes RVR, ROC, Hype thresholds and risk parameters for maximum performance.

## Features

✅ **4 Optimization Methods:**
- **Grid Search** - Exhaustive search (slow but thorough)
- **Random Search** - Fast sampling (good baseline)
- **Bayesian Optimization** - Smart search using Gaussian Process (requires scikit-optimize)
- **Walk-Forward** - Adaptive gradient-based search

✅ **Multiple Objectives:**
- Sharpe Ratio (risk-adjusted returns)
- Profit Factor (gross profit / gross loss)
- Drawdown (minimize maximum loss)
- Composite Score (weighted combination)

✅ **Comprehensive Output:**
- Best parameter combination
- Performance metrics
- Convergence plots
- Sensitivity analysis
- Exportable config.yaml

## Installation

### Basic (Pure Python)
```bash
# Works out of the box with Python 3.7+
python strategy-tuner.py --method random
```

### With Advanced Features
```bash
# For Bayesian optimization
pip install scikit-optimize

# For plotting
pip install matplotlib

# For faster computation
pip install numpy
```

## Quick Start

### 1. Basic Random Search (Fastest)
```bash
python strategy-tuner.py --method random --iterations 200
```

### 2. Bayesian Optimization (Recommended)
```bash
python strategy-tuner.py --method bayesian --iterations 100 --objective sharpe
```

### 3. Grid Search (Thorough)
```bash
python strategy-tuner.py --method grid --grid-size 4
```

### 4. Walk-Forward (Adaptive)
```bash
python strategy-tuner.py --method walk_forward --iterations 50
```

## CLI Options

```
--method {grid|random|bayesian|walk_forward}
    Optimization method (default: random)

--objective {sharpe|profit_factor|drawdown|composite}
    Objective function to optimize (default: composite)

--iterations N
    Number of iterations for random/bayesian (default: 200)

--grid-size N
    Grid size per dimension for grid search (default: 4)
    Total combinations = N^5

--db PATH
    Path to database (default: polymarket_data.db)

--export FILE
    Export optimized parameters to YAML config

--plot
    Generate performance plots (requires matplotlib)

--sensitivity PARAM
    Run sensitivity analysis for parameter
    Options: rvr_threshold, roc_threshold, hype_threshold, stop_loss, take_profit
```

## Examples

### Export Optimized Config
```bash
python strategy-tuner.py \
    --method bayesian \
    --objective sharpe \
    --iterations 150 \
    --export config.yaml.optimized
```

### Generate Plots
```bash
python strategy-tuner.py \
    --method random \
    --plot
```

### Sensitivity Analysis
```bash
python strategy-tuner.py \
    --method random \
    --sensitivity rvr_threshold
```

### Custom Database
```bash
python strategy-tuner.py \
    --db /path/to/custom.db \
    --method bayesian
```

## Programmatic Use

```python
from strategy_tuner import StrategyTuner

# Initialize
tuner = StrategyTuner(db_path="polymarket_data.db")

# Run optimization
result = tuner.optimize(
    method="bayesian",
    objective="sharpe",
    n_calls=100
)

# Access results
print(f"Best Sharpe: {result.best_metrics.sharpe_ratio:.3f}")
print(f"Best RVR: {result.best_params.rvr_threshold:.2f}")

# Export config
tuner.export_config(result, "config.yaml.optimized")

# Generate plots
tuner.plot_results(result)

# Sensitivity analysis
tuner.sensitivity_analysis(result, "roc_threshold")
```

## Parameter Search Space

| Parameter | Min | Max | Description |
|-----------|-----|-----|-------------|
| RVR Threshold | 1.0 | 4.0 | Risk/Value Ratio threshold |
| ROC Threshold | 0.05 | 0.20 | Rate of Change threshold |
| Hype Threshold | 50 | 90 | Hype score threshold |
| Stop Loss | 5% | 20% | Maximum loss per trade |
| Take Profit | 5% | 30% | Target profit per trade |

## Objective Functions

### 1. Sharpe Ratio (Default for risk-adjusted returns)
- Measures return per unit of risk
- Higher is better
- Formula: (mean_return / std_dev) * √252

### 2. Profit Factor (For profit maximization)
- Ratio of gross profit to gross loss
- Value > 1.0 = profitable
- Higher is better

### 3. Drawdown (For risk minimization)
- Maximum peak-to-trough decline
- Lower is better
- Expressed as percentage

### 4. Composite Score (Balanced optimization)
- Weighted combination:
  - Sharpe Ratio: 40%
  - Profit Factor: 30%
  - Drawdown: 20%
  - Win Rate: 10%

## Performance Metrics

Each optimization reports:

- **Sharpe Ratio** - Risk-adjusted return
- **Profit Factor** - Gross profit / gross loss
- **Max Drawdown** - Largest peak-to-trough decline
- **Total Return** - Overall percentage return
- **Win Rate** - Percentage of winning trades
- **Number of Trades** - Total trades executed
- **Avg Win** - Average profit per winning trade
- **Avg Loss** - Average loss per losing trade
- **Composite Score** - Weighted performance metric

## Output Files

### 1. Optimized Config (`config.yaml.optimized`)
```yaml
thresholds:
  rvr: 2.45
  roc: 0.123
  hype: 72

risk:
  stop_loss: 12.5  # %
  take_profit: 18.3  # %
```

### 2. Results JSON (`optimization_results_*.json`)
Detailed results including all parameter combinations tested.

### 3. Performance Plots (`optimization_*.png`)
Visual convergence and performance analysis.

## Optimization Methods Comparison

| Method | Speed | Quality | Best For |
|--------|-------|---------|----------|
| **Random** | ⚡⚡⚡ Fast | ⭐⭐ Good | Quick baseline |
| **Bayesian** | ⚡⚡ Medium | ⭐⭐⭐ Best | Production use |
| **Grid** | ⚡ Slow | ⭐⭐⭐ Best | Small spaces |
| **Walk-Forward** | ⚡⚡ Medium | ⭐⭐ Good | Local refinement |

### Recommendations

- **Getting started:** Use `random` with 200 iterations (~1-2 min)
- **Production:** Use `bayesian` with 100-150 iterations (~5-8 min)
- **Final tuning:** Use `walk_forward` to refine bayesian results
- **Verification:** Use `grid` with small grid-size for thorough check

## Tips

1. **Start with Random Search** - Fast baseline to understand parameter space
2. **Use Bayesian for Production** - Best quality per iteration
3. **Check Multiple Objectives** - Run optimization for each objective function
4. **Validate Results** - Test optimized parameters on holdout data
5. **Monitor Overfitting** - Too many iterations can overfit to historical data
6. **Save Everything** - Keep all result files for comparison

## Troubleshooting

### No market data found
```
❌ No market data found in database!
```
**Solution:** Run data collection first:
```bash
python polymarket-collector.py
```

### Bayesian optimization not available
```
⚠️  scikit-optimize not available
```
**Solution:** Install scikit-optimize:
```bash
pip install scikit-optimize
```

### Plotting disabled
```
⚠️  matplotlib not available
```
**Solution:** Install matplotlib:
```bash
pip install matplotlib
```

## Performance Notes

- **Random Search**: ~200 iterations in 1-2 minutes
- **Bayesian**: ~100 iterations in 5-8 minutes
- **Grid Search**: 4^5 = 1024 combinations in ~10 minutes
- **Walk-Forward**: ~50 iterations in 2-3 minutes

All timings assume ~1000 markets in database.

## Integration with Trading Bot

After optimization:

```python
# 1. Run optimization
tuner = StrategyTuner()
result = tuner.optimize(method="bayesian", objective="sharpe")

# 2. Export config
tuner.export_config(result, "config.yaml.optimized")

# 3. Use in trading bot
# Copy optimized values to main config.yaml
# Or load directly:
best_params = result.best_params
```

## Advanced Usage

### Custom Objective Function
```python
def custom_objective(metrics):
    # Your custom scoring logic
    return metrics.sharpe_ratio * 0.5 + metrics.win_rate * 0.5

# Modify _evaluate method in StrategyTuner class
```

### Constrained Optimization
```python
# Modify param_space in __init__
self.param_space = {
    'rvr_threshold': (2.0, 3.0),  # Narrower range
    'roc_threshold': (0.10, 0.15),
    # ...
}
```

### Multi-Objective Optimization
Run multiple optimizations and compare:
```bash
python strategy-tuner.py --method bayesian --objective sharpe --export config.sharpe.yaml
python strategy-tuner.py --method bayesian --objective profit_factor --export config.profit.yaml
python strategy-tuner.py --method bayesian --objective drawdown --export config.safe.yaml
```

## Great Success! 🎉

You now have a fully automated parameter optimization system. Use it to:
- Find optimal trading parameters
- Maximize risk-adjusted returns
- Minimize drawdown
- Adapt to changing market conditions

Run it regularly (weekly/monthly) to keep parameters aligned with current market dynamics.
