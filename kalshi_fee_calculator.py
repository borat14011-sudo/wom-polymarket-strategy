#!/usr/bin/env python3
"""
Kalshi Fee Calculator & Optimizer
Quick tool to calculate fees and compare to Polymarket
"""

def kalshi_fee(price, contracts=1, k=0.0007):
    """Calculate one-way Kalshi fee"""
    return k * contracts * price * (100 - price)

def kalshi_roundtrip(price, contracts=1, k=0.0007):
    """Calculate roundtrip Kalshi fee (buy + sell)"""
    return 2 * kalshi_fee(price, contracts, k)

def polymarket_roundtrip(price, contracts=1):
    """Calculate roundtrip Polymarket fee (4% total)"""
    return 0.04 * price * contracts

def compare_platforms(price, contracts=1):
    """Compare Kalshi vs Polymarket fees"""
    kalshi = kalshi_roundtrip(price, contracts)
    poly = polymarket_roundtrip(price, contracts)
    
    kalshi_pct = (kalshi / (price * contracts)) * 100 if price > 0 else 0
    poly_pct = 4.0  # Always 4%
    
    advantage = poly - kalshi
    better_platform = "KALSHI" if advantage > 0 else "POLYMARKET"
    
    return {
        'price': price,
        'contracts': contracts,
        'kalshi_fee': kalshi,
        'kalshi_pct': kalshi_pct,
        'poly_fee': poly,
        'poly_pct': poly_pct,
        'advantage': advantage,
        'better': better_platform,
        'savings': abs(advantage)
    }

def breakeven_win_rate(price, platform='kalshi'):
    """Calculate required win rate to break even"""
    if platform == 'kalshi':
        fee = kalshi_roundtrip(price, contracts=1)
        fee_pct = (fee / price) * 100 if price > 0 else 0
    else:  # polymarket
        fee_pct = 4.0
    
    return price + (price * fee_pct / 100)

def optimal_zones():
    """Print optimal trading zones"""
    print("\n" + "="*60)
    print("KALSHI OPTIMAL TRADING ZONES")
    print("="*60)
    
    print("\n[+] KALSHI ADVANTAGE (Use Kalshi):")
    print("  Price 0-26c:  Lower fees than Polymarket")
    print("  Price 74-99c: Lower fees than Polymarket")
    print("  SWEET SPOT: 85-95c (fees ~1.5-2%)")
    
    print("\n[-] POLYMARKET ADVANTAGE (Use Polymarket):")
    print("  Price 26-74c: Lower fees than Kalshi")
    print("  WORST KALSHI ZONE: 45-55c (fees ~7%)")
    
    print("\n" + "="*60)

def fee_table():
    """Generate comprehensive fee comparison table"""
    print("\n" + "="*80)
    print(f"{'Price':<8} {'Kalshi 1-Way':<14} {'Kalshi RT':<12} {'Poly RT':<12} {'Better':<12} {'Savings':<10}")
    print("="*80)
    
    prices = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95]
    
    for price in prices:
        result = compare_platforms(price, contracts=100)  # Per 100 contracts
        
        kalshi_1way = kalshi_fee(price, 100)
        kalshi_rt = result['kalshi_fee']
        poly_rt = result['poly_fee']
        better = result['better']
        savings = result['savings']
        
        # Format with color indicators
        indicator = "[+]" if better == "KALSHI" else "[-]"
        
        print(f"{price:>4}¢    "
              f"${kalshi_1way:>6.2f} ({result['kalshi_pct']/2:>4.1f}%)  "
              f"${kalshi_rt:>6.2f}     "
              f"${poly_rt:>6.2f}     "
              f"{better:<12} "
              f"${savings:>6.2f} {indicator}")
    
    print("="*80)

def calculate_edge_required(price):
    """Calculate minimum edge required for profitable trading"""
    kalshi_fee_pct = (kalshi_roundtrip(price) / price) * 100 if price > 0 else 0
    poly_fee_pct = 4.0
    
    return {
        'price': price,
        'kalshi_min_edge': kalshi_fee_pct,
        'poly_min_edge': poly_fee_pct,
        'kalshi_advantage': poly_fee_pct - kalshi_fee_pct
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("KALSHI FEE CALCULATOR & OPTIMIZER")
    print("="*60)
    
    # Show optimal zones
    optimal_zones()
    
    # Show fee table
    print("\n\nFEE COMPARISON (per 100 contracts):")
    fee_table()
    
    # Edge requirements
    print("\n\n" + "="*60)
    print("MINIMUM EDGE REQUIRED FOR PROFITABILITY")
    print("="*60)
    
    key_prices = [10, 25, 50, 75, 90]
    print(f"\n{'Price':<8} {'Kalshi Edge':<14} {'Poly Edge':<12} {'Kalshi Advantage':<18}")
    print("-"*60)
    
    for price in key_prices:
        edge = calculate_edge_required(price)
        advantage = edge['kalshi_advantage']
        indicator = "[+]" if advantage > 0 else "[-]"
        
        print(f"{price:>4}¢    "
              f"{edge['kalshi_min_edge']:>6.2f}%         "
              f"{edge['poly_min_edge']:>4.1f}%        "
              f"{advantage:>+6.2f}% {indicator}")
    
    print("\n" + "="*60)
    print("\n[!] KEY TAKEAWAY:")
    print("   Trade >74c or <26c on KALSHI for fee advantage")
    print("   Trade 26-74c on POLYMARKET for lower fees")
    print("   Optimal Kalshi zone: 85-95c (fees 1.4-2.0% vs 4.0%)")
    print("\n" + "="*60)
