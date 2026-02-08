#!/usr/bin/env python3
"""
Portfolio Optimizer - API Usage Examples

This file demonstrates how to use the PortfolioOptimizer class
programmatically in your own trading scripts.
"""

from portfolio_optimizer import PortfolioOptimizer, Sector


def example_basic_usage():
    """Basic usage example"""
    print("\n" + "="*60)
    print("Example 1: Basic API Usage")
    print("="*60)
    
    # Initialize optimizer with $10,000 bankroll
    # Using 25% fractional Kelly for conservative sizing
    optimizer = PortfolioOptimizer(bankroll=10000, fractional_kelly=0.25)
    
    # Add a position
    # You estimate 60% probability, market price is 50%
    optimizer.add_position(
        market_id="trump_wins_2024",
        amount=1000,  # Currently invested $1000
        probability=0.60,  # Your edge estimate
        market_price=0.50,  # Current market price
        sector=Sector.POLITICS
    )
    
    # Calculate optimal allocation
    allocation = optimizer.optimize()
    
    print(f"\nOptimal allocation: ${allocation['optimal_allocations']['trump_wins_2024']:,.2f}")
    print(f"Current position: $1,000.00")
    print(f"Suggested change: ${allocation['optimal_allocations']['trump_wins_2024'] - 1000:+,.2f}")


def example_multi_market():
    """Multi-market portfolio with correlations"""
    print("\n" + "="*60)
    print("Example 2: Multi-Market Portfolio with Correlations")
    print("="*60)
    
    optimizer = PortfolioOptimizer(bankroll=50000, fractional_kelly=0.25)
    
    # Add multiple correlated crypto positions
    optimizer.add_position(
        market_id="btc_100k",
        amount=5000,
        probability=0.70,
        market_price=0.60,
        sector=Sector.CRYPTO,
        historical_returns=[0.20, -0.10, 0.15, 0.25, -0.05]
    )
    
    optimizer.add_position(
        market_id="eth_5k",
        amount=3000,
        probability=0.65,
        market_price=0.55,
        sector=Sector.CRYPTO,
        historical_returns=[0.18, -0.12, 0.14, 0.22, -0.06]
    )
    
    optimizer.add_position(
        market_id="sol_500",
        amount=2000,
        probability=0.55,
        market_price=0.45,
        sector=Sector.CRYPTO,
        historical_returns=[0.25, -0.15, 0.20, 0.30, -0.10]
    )
    
    # Set correlations (crypto assets are highly correlated)
    optimizer.set_correlation("btc_100k", "eth_5k", 0.85)
    optimizer.set_correlation("btc_100k", "sol_500", 0.75)
    optimizer.set_correlation("eth_5k", "sol_500", 0.80)
    
    # Get analysis
    analysis = optimizer.analyze_portfolio()
    
    print(f"\nTotal exposure: ${analysis['total_exposure']:,.2f}")
    print(f"Portfolio utilization: {analysis['utilization']*100:.1f}%")
    print(f"Concentration (HHI): {analysis['hhi']:.3f}")
    
    # Check for warnings
    if analysis['warnings']:
        print("\n⚠️  Warnings:")
        for warning in analysis['warnings']:
            print(f"  {warning}")
    
    # Get risk metrics
    metrics = optimizer.calculate_risk_metrics()
    
    print("\n📊 Risk Metrics:")
    for market_id, m in metrics.items():
        if m['sharpe_ratio']:
            print(f"  {market_id}: Sharpe={m['sharpe_ratio']:.2f}, Edge={m['edge']:+.2f}")


def example_rebalancing():
    """Rebalancing example"""
    print("\n" + "="*60)
    print("Example 3: Dynamic Rebalancing")
    print("="*60)
    
    optimizer = PortfolioOptimizer(bankroll=20000, fractional_kelly=0.25)
    
    # Portfolio has drifted from optimal
    optimizer.add_position(
        market_id="market_a",
        amount=3000,  # Overweight
        probability=0.55,
        market_price=0.50,
        sector=Sector.POLITICS
    )
    
    optimizer.add_position(
        market_id="market_b",
        amount=500,  # Underweight
        probability=0.65,
        market_price=0.52,
        sector=Sector.SPORTS
    )
    
    # Get rebalance orders
    orders = optimizer.calculate_rebalance_orders(target_drift_threshold=0.05)
    
    if orders:
        print("\n🔄 Rebalancing needed:")
        for market_id, amount in orders.items():
            action = "BUY" if amount > 0 else "SELL"
            print(f"  {action} {market_id}: ${abs(amount):,.2f}")
    else:
        print("\n✓ Portfolio is balanced")


def example_sector_limits():
    """Sector exposure limits example"""
    print("\n" + "="*60)
    print("Example 4: Sector Exposure Limits")
    print("="*60)
    
    optimizer = PortfolioOptimizer(bankroll=100000, fractional_kelly=0.25)
    
    # Try to over-allocate to crypto (limit is 30%)
    for i in range(5):
        optimizer.add_position(
            market_id=f"crypto_market_{i}",
            amount=0,  # Start with no position
            probability=0.60,
            market_price=0.50,
            sector=Sector.CRYPTO
        )
    
    # Calculate optimal allocation
    allocations = optimizer.calculate_optimal_allocation()
    
    # Calculate actual crypto exposure
    crypto_total = sum(allocations.values())
    crypto_pct = (crypto_total / optimizer.bankroll) * 100
    
    print(f"\nRequested crypto allocation: 5 markets with good edges")
    print(f"After sector limits applied:")
    print(f"  Total crypto allocation: ${crypto_total:,.2f} ({crypto_pct:.1f}%)")
    print(f"  Limit: 30% = ${optimizer.bankroll * 0.30:,.2f}")
    
    if crypto_pct <= 30:
        print(f"  ✓ Within sector limits")
    else:
        print(f"  ⚠️  Exceeded sector limits (should not happen)")


def example_risk_calculations():
    """Risk calculation examples"""
    print("\n" + "="*60)
    print("Example 5: Risk Calculations (Sharpe, Sortino, VaR)")
    print("="*60)
    
    optimizer = PortfolioOptimizer(bankroll=25000)
    
    # Add position with historical returns
    optimizer.add_position(
        market_id="volatile_market",
        amount=5000,
        probability=0.58,
        market_price=0.52,
        sector=Sector.OTHER,
        historical_returns=[
            0.15, -0.08, 0.22, -0.12, 0.18, -0.05, 0.10,
            0.25, -0.15, 0.08, -0.20, 0.30, -0.10, 0.12
        ]
    )
    
    # Calculate metrics
    sharpe = optimizer.calculate_sharpe_ratio("volatile_market")
    sortino = optimizer.calculate_sortino_ratio("volatile_market")
    max_dd = optimizer.calculate_max_drawdown("volatile_market")
    var_95 = optimizer.calculate_var(0.95)
    
    print(f"\nRisk Metrics for volatile_market:")
    print(f"  Sharpe Ratio: {sharpe:.3f}")
    print(f"  Sortino Ratio: {sortino:.3f}")
    print(f"  Max Drawdown: {max_dd*100:.1f}%")
    print(f"  Portfolio VaR (95%): ${var_95:,.2f}")
    
    print(f"\nInterpretation:")
    print(f"  - Sharpe > 1.0 is good, > 2.0 is excellent")
    print(f"  - Sortino > Sharpe means downside is well controlled")
    print(f"  - Max Drawdown shows worst peak-to-trough decline")
    print(f"  - VaR: 95% confident you won't lose more than ${var_95:,.2f}")


def example_integration_workflow():
    """Full integration workflow"""
    print("\n" + "="*60)
    print("Example 6: Full Integration Workflow")
    print("="*60)
    
    # Step 1: Initialize
    optimizer = PortfolioOptimizer(bankroll=100000, fractional_kelly=0.25)
    
    # Step 2: Load current positions from your trading system
    # (In practice, this would come from Polymarket API)
    current_positions = [
        {"id": "btc_100k", "amount": 10000, "prob": 0.65, "price": 0.58, "sector": "crypto"},
        {"id": "eth_5k", "amount": 8000, "prob": 0.60, "price": 0.54, "sector": "crypto"},
        {"id": "dem_wins", "amount": 15000, "prob": 0.52, "price": 0.49, "sector": "politics"},
        {"id": "lakers_champ", "amount": 5000, "prob": 0.30, "price": 0.22, "sector": "sports"},
    ]
    
    for pos in current_positions:
        optimizer.add_position(
            market_id=pos["id"],
            amount=pos["amount"],
            probability=pos["prob"],
            market_price=pos["price"],
            sector=Sector(pos["sector"])
        )
    
    # Set correlations
    optimizer.set_correlation("btc_100k", "eth_5k", 0.85)
    
    # Step 3: Analyze
    print("\n📊 Portfolio Analysis:")
    analysis = optimizer.analyze_portfolio()
    print(f"  Total exposure: ${analysis['total_exposure']:,.2f} / ${optimizer.bankroll:,.2f}")
    print(f"  Expected return: ${analysis['expected_return']:,.2f}")
    print(f"  Concentration (HHI): {analysis['hhi']:.3f}")
    
    # Step 4: Optimize
    print("\n🎯 Optimization:")
    allocations = optimizer.calculate_optimal_allocation()
    for market_id, optimal in allocations.items():
        current = optimizer.positions[market_id].amount
        diff = optimal - current
        if abs(diff) > 100:  # Only show significant changes
            print(f"  {market_id}: ${current:,.0f} → ${optimal:,.0f} ({diff:+,.0f})")
    
    # Step 5: Rebalance
    print("\n🔄 Rebalancing:")
    orders = optimizer.calculate_rebalance_orders()
    if orders:
        print(f"  {len(orders)} orders needed:")
        for market_id, amount in orders.items():
            action = "BUY" if amount > 0 else "SELL"
            print(f"    {action} {market_id}: ${abs(amount):,.2f}")
    else:
        print("  ✓ No rebalancing needed")
    
    # Step 6: Check warnings
    if analysis['warnings']:
        print("\n⚠️  Warnings:")
        for warning in analysis['warnings']:
            print(f"  {warning}")


if __name__ == "__main__":
    # Run all examples
    example_basic_usage()
    example_multi_market()
    example_rebalancing()
    example_sector_limits()
    example_risk_calculations()
    example_integration_workflow()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60)
    print("\nTo use in your own code:")
    print("  from portfolio_optimizer import PortfolioOptimizer, Sector")
    print("  optimizer = PortfolioOptimizer(bankroll=10000)")
    print("  optimizer.add_position(...)")
    print("  result = optimizer.optimize()")
