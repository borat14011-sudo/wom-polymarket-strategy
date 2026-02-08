"""
AGENT 5: Market Category Filter Analysis
========================================
MISSION: Identify which market categories have strongest whale alpha.

Tests:
- Politics (elections, polls)
- Sports (games, matches)
- Crypto (price predictions)
- Economics (Fed, rates)
- Entertainment (celebrity, social media)
- Volume tiers within categories
"""

import sys
sys.path.append('.')
from whale_backtest_engine import WhaleBacktestEngine
import json

def run_category_analysis():
    engine = WhaleBacktestEngine(initial_capital=10000)
    n_markets = engine.load_markets("../polymarket_resolved_markets.json")
    
    print(f"=== AGENT 5: Market Category Analysis ===")
    print(f"Loaded {n_markets} resolved markets\n")
    
    results = {}
    
    # First, get category distribution
    print("Category Distribution in Dataset:")
    print("-" * 40)
    
    all_result = engine.run_backtest({'random_seed': 42})
    cat_breakdown = all_result['category_breakdown']
    
    for cat, stats in sorted(cat_breakdown.items(), key=lambda x: x[1]['trades'], reverse=True):
        print(f"{cat:15} | {stats['trades']:3} trades | {stats['win_rate']:.1%} WR | ${stats['total_pnl']:+.0f}")
    
    # Test each category independently
    print("\n" + "="*60)
    print("CATEGORY-SPECIFIC WHALE PERFORMANCE (65% baseline accuracy)")
    print("="*60 + "\n")
    
    categories = ['politics', 'sports', 'crypto', 'economics', 'entertainment', 'other']
    
    for cat in categories:
        result = engine.run_backtest({
            'whale_accuracy': 0.65,
            'slippage_pct': 0.02,
            'sizing_method': 'fixed',
            'base_position_size': 100,
            'category_filter': [cat],
            'random_seed': 42
        })
        
        if 'error' in result:
            results[cat] = {'category': cat, 'trades': 0, 'error': 'No trades'}
            print(f"{cat:15} | No trades in this category")
            continue
            
        results[cat] = {
            'category': cat,
            'trades': result['total_trades'],
            'win_rate': result['win_rate'],
            'total_return_pct': result['total_return_pct'],
            'sharpe_ratio': result['sharpe_ratio'],
            'max_drawdown_pct': result['max_drawdown_pct'],
            'avg_win': result['avg_win'],
            'avg_loss': result['avg_loss'],
            'profit_factor': result['profit_factor']
        }
        
        status = "✅" if result['total_return_pct'] > 0 else "❌"
        print(f"{cat:15} | Trades: {result['total_trades']:3} | WR: {result['win_rate']:.1%} | Return: {result['total_return_pct']:+6.1f}% | Sharpe: {result['sharpe_ratio']:.2f} {status}")
    
    # Test whale accuracy by category
    print("\n" + "="*60)
    print("CATEGORY-SPECIFIC WHALE ACCURACY REQUIREMENTS")
    print("="*60 + "\n")
    
    print("(Finding minimum whale accuracy for profitability per category)")
    
    for cat in categories:
        profitable_accuracy = None
        
        for accuracy in [0.55, 0.58, 0.60, 0.62, 0.65, 0.68, 0.70, 0.75]:
            result = engine.run_backtest({
                'whale_accuracy': accuracy,
                'slippage_pct': 0.02,
                'sizing_method': 'fixed',
                'base_position_size': 100,
                'category_filter': [cat],
                'random_seed': 42
            })
            
            if result['total_return_pct'] > 0 and profitable_accuracy is None:
                profitable_accuracy = accuracy
                break
        
        if profitable_accuracy:
            print(f"{cat:15} | Minimum profitable accuracy: {profitable_accuracy:.0%}")
        else:
            print(f"{cat:15} | Not profitable even at 75% accuracy ❌")
        
        results[cat]['min_profitable_accuracy'] = profitable_accuracy
    
    # Volume tier analysis within categories
    print("\n" + "="*60)
    print("VOLUME TIER ANALYSIS (Politics category)")
    print("="*60 + "\n")
    
    volume_tiers = [
        ('Low Volume', 1000, 10000),
        ('Medium Volume', 10000, 50000),
        ('High Volume', 50000, 200000),
        ('Mega Volume', 200000, 10000000)
    ]
    
    for tier_name, min_vol, max_vol in volume_tiers:
        # Custom filtering by volume
        engine_copy = WhaleBacktestEngine(initial_capital=10000)
        engine_copy.load_markets("../polymarket_resolved_markets.json")
        
        # Filter markets by volume
        original_markets = engine_copy.markets.copy()
        engine_copy.markets = [m for m in original_markets 
                               if min_vol <= m.volume_usd < max_vol 
                               and m.category == 'politics']
        
        if len(engine_copy.markets) > 0:
            result = engine_copy.run_backtest({
                'whale_accuracy': 0.65,
                'slippage_pct': 0.02,
                'sizing_method': 'fixed',
                'base_position_size': 100,
                'random_seed': 42
            })
            
            print(f"{tier_name:15} | Markets: {len(engine_copy.markets):3} | WR: {result['win_rate']:.1%} | Return: {result['total_return_pct']:+.1f}%")
        else:
            print(f"{tier_name:15} | No markets in this range")
    
    # Find optimal category combination
    print("\n" + "="*60)
    print("OPTIMAL CATEGORY COMBINATIONS")
    print("="*60)
    
    from itertools import combinations
    
    best_combos = []
    
    for r in range(1, len(categories) + 1):
        for combo in combinations(categories, r):
            result = engine.run_backtest({
                'whale_accuracy': 0.65,
                'slippage_pct': 0.02,
                'sizing_method': 'fixed',
                'base_position_size': 100,
                'category_filter': list(combo),
                'random_seed': 42
            })
            
            if result['total_trades'] >= 5:  # Minimum trades for validity
                best_combos.append({
                    'categories': combo,
                    'trades': result['total_trades'],
                    'sharpe': result['sharpe_ratio'],
                    'return': result['total_return_pct']
                })
    
    # Sort by Sharpe
    best_combos.sort(key=lambda x: x['sharpe'], reverse=True)
    
    print("\nTop 5 Category Combinations by Sharpe:")
    for i, combo in enumerate(best_combos[:5], 1):
        cats = ', '.join(combo['categories'])
        print(f"{i}. [{cats}] | Trades: {combo['trades']} | Sharpe: {combo['sharpe']:.2f} | Return: {combo['return']:+.1f}%")
    
    results['best_combinations'] = best_combos[:5]
    
    # Recommendation
    print("\n" + "="*60)
    print("AGENT 5 RECOMMENDATION")
    print("="*60)
    
    profitable_cats = [cat for cat, r in results.items() if isinstance(r, dict) and r.get('total_return_pct', -999) > 0]
    unprofitable_cats = [cat for cat, r in results.items() if isinstance(r, dict) and r.get('total_return_pct', -999) <= 0 and 'category' in r]
    
    if profitable_cats:
        print(f"✅ Profitable categories: {', '.join(profitable_cats)}")
    if unprofitable_cats:
        print(f"❌ Avoid categories: {', '.join(unprofitable_cats)}")
    
    if best_combos:
        best_combo = best_combos[0]
        print(f"\n🏆 Recommended filter: {', '.join(best_combo['categories'])}")
        print(f"   Expected Sharpe: {best_combo['sharpe']:.2f}")
        print(f"   Expected Return: {best_combo['return']:+.1f}%")
    
    # Save results
    with open("agent5_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Summary for orchestrator
    print("\n" + "="*60)
    print("AGENT 5 SUMMARY FOR ORCHESTRATOR")
    print("="*60)
    
    summary = {
        'agent': 'Agent5_Categories',
        'finding': f'Best categories: {", ".join(best_combos[0]["categories"]) if best_combos else "all"}',
        'recommendation': f'Focus on: {", ".join(profitable_cats) if profitable_cats else "no clear winner"}',
        'avoid_categories': unprofitable_cats,
        'best_sharpe': best_combos[0]['sharpe'] if best_combos else 0,
        'key_insight': 'Category filtering can improve Sharpe by avoiding noisy markets'
    }
    
    print(json.dumps(summary, indent=2))
    
    return results

if __name__ == "__main__":
    run_category_analysis()
