import numpy as np
import json

# Set seed for reproducibility
np.random.seed(42)

# Simulation parameters
N_SIMULATIONS = 10000
STARTING_CAPITAL = 100
BTC_ALLOCATION = 0.5
WEATHER_ALLOCATION = 0.5

# Strategy parameters (annualized)
# BTC Strategy - higher volatility, positive drift
BTC_PARAMS = {
    'annual_return': 0.45,      # 45% annual return
    'annual_volatility': 0.65,  # 65% annual volatility (high crypto volatility)
    'max_leverage': 2.0,
    'sharpe': 0.69
}

# Weather Strategy - lower volatility, steady returns
WEATHER_PARAMS = {
    'annual_return': 0.28,      # 28% annual return
    'annual_volatility': 0.35,  # 35% annual volatility
    'max_leverage': 1.5,
    'sharpe': 0.80
}

# Trading days
trading_days_30 = 30
trading_days_90 = 90
trading_days_1y = 252

def run_monte_carlo(simulations, days, strategy_params, capital):
    """Run Monte Carlo simulation for a single strategy"""
    dt = 1/252  # Daily time step
    
    # Convert annual parameters to daily
    mu = strategy_params['annual_return']
    sigma = strategy_params['annual_volatility']
    
    # Daily drift and volatility
    daily_drift = mu / 252
    daily_vol = sigma / np.sqrt(252)
    
    # Generate random returns
    returns = np.random.normal(daily_drift, daily_vol, (simulations, days))
    
    # Calculate cumulative returns
    cumulative_returns = np.cumprod(1 + returns, axis=1)
    
    # Final portfolio values
    final_values = capital * cumulative_returns[:, -1]
    
    # Calculate drawdowns
    running_max = np.maximum.accumulate(cumulative_returns, axis=1)
    drawdowns = (cumulative_returns - running_max) / running_max
    max_drawdowns = np.min(drawdowns, axis=1)
    
    return {
        'final_values': final_values,
        'max_drawdowns': max_drawdowns,
        'cumulative_returns': cumulative_returns
    }

def run_portfolio_monte_carlo(simulations, days, capital, btc_weight, weather_weight):
    """Run Monte Carlo for combined portfolio"""
    dt = 1/252
    
    # BTC daily parameters
    btc_mu = BTC_PARAMS['annual_return'] / 252
    btc_sigma = BTC_PARAMS['annual_volatility'] / np.sqrt(252)
    
    # Weather daily parameters
    weather_mu = WEATHER_PARAMS['annual_return'] / 252
    weather_sigma = WEATHER_PARAMS['annual_volatility'] / np.sqrt(252)
    
    # Correlation between strategies (assumed moderate positive correlation 0.3)
    correlation = 0.3
    
    # Generate correlated random returns
    btc_returns = np.random.normal(btc_mu, btc_sigma, (simulations, days))
    weather_noise = np.random.normal(0, 1, (simulations, days))
    weather_returns = (weather_mu + 
                       correlation * weather_sigma/btc_sigma * (btc_returns - btc_mu) + 
                       np.sqrt(1 - correlation**2) * weather_sigma * weather_noise)
    
    # Portfolio returns (weighted combination)
    portfolio_returns = btc_weight * btc_returns + weather_weight * weather_returns
    
    # Cumulative portfolio value
    cumulative_values = capital * np.cumprod(1 + portfolio_returns, axis=1)
    
    # Final values
    final_values = cumulative_values[:, -1]
    
    # Calculate drawdowns
    running_max = np.maximum.accumulate(cumulative_values, axis=1)
    drawdowns = (cumulative_values - running_max) / running_max
    max_drawdowns = np.min(drawdowns, axis=1)
    
    # Path-level stats
    return {
        'final_values': final_values,
        'max_drawdowns': max_drawdowns,
        'cumulative_values': cumulative_values,
        'portfolio_returns': portfolio_returns
    }

def calculate_percentiles(data):
    """Calculate percentile statistics"""
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    return {p: np.percentile(data, p) for p in percentiles}

def prob_of_profit(final_values, initial_capital):
    """Calculate probability of profit"""
    return np.mean(final_values > initial_capital) * 100

def risk_of_ruin(final_values, initial_capital, ruin_threshold=0.5):
    """Calculate risk of ruin (falling below threshold)"""
    return np.mean(final_values < initial_capital * ruin_threshold) * 100

def calculate_var(final_values, confidence=0.05):
    """Calculate Value at Risk"""
    return np.percentile(final_values, confidence * 100)

def calculate_cvar(final_values, confidence=0.05):
    """Calculate Conditional Value at Risk (Expected Shortfall)"""
    var = calculate_var(final_values, confidence)
    return np.mean(final_values[final_values <= var])

# ============================================
# RUN SIMULATIONS
# ============================================

print("Running Monte Carlo Simulations...")
print(f"Simulations: {N_SIMULATIONS:,}")
print(f"Starting Capital: ${STARTING_CAPITAL}")
print(f"Allocation: {BTC_ALLOCATION*100:.0f}% BTC / {WEATHER_ALLOCATION*100:.0f}% Weather")
print()

# Run portfolio-level simulations
portfolio_30d = run_portfolio_monte_carlo(N_SIMULATIONS, trading_days_30, STARTING_CAPITAL, BTC_ALLOCATION, WEATHER_ALLOCATION)
portfolio_90d = run_portfolio_monte_carlo(N_SIMULATIONS, trading_days_90, STARTING_CAPITAL, BTC_ALLOCATION, WEATHER_ALLOCATION)
portfolio_1y = run_portfolio_monte_carlo(N_SIMULATIONS, trading_days_1y, STARTING_CAPITAL, BTC_ALLOCATION, WEATHER_ALLOCATION)

# Run individual strategy simulations (50/50 split of $100 = $50 each)
btc_capital = STARTING_CAPITAL * BTC_ALLOCATION
weather_capital = STARTING_CAPITAL * WEATHER_ALLOCATION

btc_1y = run_monte_carlo(N_SIMULATIONS, trading_days_1y, BTC_PARAMS, btc_capital)
weather_1y = run_monte_carlo(N_SIMULATIONS, trading_days_1y, WEATHER_PARAMS, weather_capital)

# ============================================
# CALCULATE STATISTICS
# ============================================

results = {
    'portfolio': {},
    'btc': {},
    'weather': {}
}

# Portfolio statistics
for horizon, sim_data, days in [('30d', portfolio_30d, 30), ('90d', portfolio_90d, 90), ('1y', portfolio_1y, 252)]:
    returns_pct = ((sim_data['final_values'] - STARTING_CAPITAL) / STARTING_CAPITAL) * 100
    results['portfolio'][horizon] = {
        'percentiles': calculate_percentiles(sim_data['final_values']),
        'return_percentiles': calculate_percentiles(returns_pct),
        'max_dd_percentiles': calculate_percentiles(sim_data['max_drawdowns'] * 100),
        'prob_profit': prob_of_profit(sim_data['final_values'], STARTING_CAPITAL),
        'risk_of_ruin': risk_of_ruin(sim_data['final_values'], STARTING_CAPITAL),
        'var_95': calculate_var(sim_data['final_values'], 0.05),
        'cvar_95': calculate_cvar(sim_data['final_values'], 0.05),
        'mean_return': np.mean(returns_pct),
        'median_return': np.median(returns_pct),
        'std_return': np.std(returns_pct),
        'mean_final': np.mean(sim_data['final_values']),
        'median_final': np.median(sim_data['final_values'])
    }

# Individual strategy statistics (1-year)
for name, sim_data in [('btc', btc_1y), ('weather', weather_1y)]:
    returns_pct = ((sim_data['final_values'] - (STARTING_CAPITAL * 0.5)) / (STARTING_CAPITAL * 0.5)) * 100
    results[name] = {
        'percentiles': calculate_percentiles(sim_data['final_values']),
        'return_percentiles': calculate_percentiles(returns_pct),
        'max_dd_percentiles': calculate_percentiles(sim_data['max_drawdowns'] * 100),
        'prob_profit': prob_of_profit(sim_data['final_values'], STARTING_CAPITAL * 0.5),
        'risk_of_ruin': risk_of_ruin(sim_data['final_values'], STARTING_CAPITAL * 0.5),
        'var_95': calculate_var(sim_data['final_values'], 0.05),
        'cvar_95': calculate_cvar(sim_data['final_values'], 0.05),
        'mean_return': np.mean(returns_pct),
        'median_return': np.median(returns_pct),
        'std_return': np.std(returns_pct),
        'mean_final': np.mean(sim_data['final_values']),
        'median_final': np.median(sim_data['final_values'])
    }

# Save results
with open('monte_carlo_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=float)

print("Simulation complete. Results saved to monte_carlo_results.json")

# Print summary
print("\n" + "="*60)
print("SUMMARY STATISTICS")
print("="*60)

for horizon in ['30d', '90d', '1y']:
    data = results['portfolio'][horizon]
    print(f"\nPortfolio - {horizon}:")
    print(f"  Mean Return: {data['mean_return']:.2f}%")
    print(f"  Median Return: {data['median_return']:.2f}%")
    print(f"  P(Profit): {data['prob_profit']:.1f}%")
    print(f"  Risk of Ruin: {data['risk_of_ruin']:.2f}%")
    print(f"  Mean Final Value: ${data['mean_final']:.2f}")
