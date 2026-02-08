
# Strategy H: Combined Multi-Factor Fade
print("\n--- STRATEGY H: MULTI-FACTOR SUPER FADE ---")
# Combines: High hype score + High price + Not objective
multi_factor_trades = []
for m in resolved_markets:
    yes_price = float(m.get('lastTradePrice', 0.5))
    hype_score = m['_hype_score']
    
    # Must have high hype score AND high price
    if hype_score >= 3 and yes_price >= 0.7:
        # Exclude objective markets
        is_objective = any(word in m.get('question', '').lower() 
                          for word in ['temperature', 'rain', 'score', 'vs', 'match', 'game winner'])
        
        if not is_objective:
            if m['_resolved_no']:
                gross_return = yes_price / (1 - yes_price) if yes_price < 1 else 1
                multi_factor_trades.append({
                    'market_id': m['id'],
                    'question': m['question'][:60],
                    'entry_price': yes_price,
                    'hype_score': hype_score,
                    'win': True,
                    'gross_return': gross_return
                })
            else:
                multi_factor_trades.append({
                    'market_id': m['id'],
                    'question': m['question'][:60],
                    'entry_price': yes_price,
                    'hype_score': hype_score,
                    'win': False,
                    'gross_return': 0
                })

strategy_h = calculate_strategy_metrics(multi_factor_trades)
if strategy_h:
    print(f"Trades: {strategy_h['trades']}, Wins: {strategy_h['wins']}, Win Rate: {strategy_h['win_rate']*100:.1f}%")
    print(f"Avg Return: {strategy_h['avg_return']:.2f}, Total P&L: {strategy_h['total_pnl']:.2f}")
    print(f"Sharpe: {strategy_h['sharpe_ratio']:.2f}, Max DD: {strategy_h['max_drawdown']:.1f}%")

# Strategy I: Extreme Consensus Fade (YES > 85%)
print("\n--- STRATEGY I: EXTREME CONSENSUS FADE (YES > 85%) ---")
extreme_consensus_trades = []
for m in resolved_markets:
    yes_price = float(m.get('lastTradePrice', 0.5))
    
    if yes_price >= 0.85:
        if m['_resolved_no']:
            gross_return = yes_price / (1 - yes_price) if yes_price < 1 else 1
            extreme_consensus_trades.append({
                'market_id': m['id'],
                'question': m['question'][:60],
                'entry_price': yes_price,
                'win': True,
                'gross_return': gross_return
            })
        else:
            extreme_consensus_trades.append({
                'market_id': m['id'],
                'question': m['question'][:60],
                'entry_price': yes_price,
                'win': False,
                'gross_return': 0
            })

strategy_i = calculate_strategy_metrics(extreme_consensus_trades)
if strategy_i:
    print(f"Trades: {strategy_i['trades']}, Wins: {strategy_i['wins']}, Win Rate: {strategy_i['win_rate']*100:.1f}%")
    print(f"Avg Return: {strategy_i['avg_return']:.2f}, Total P&L: {strategy_i['total_pnl']:.2f}")
    print(f"Sharpe: {strategy_i['sharpe_ratio']:.2f}, Max DD: {strategy_i['max_drawdown']:.1f}%")

# Strategy J: Crypto Fade
print("\n--- STRATEGY J: CRYPTO FADE ---")
crypto_trades = []
for m in resolved_markets:
    if 'crypto' in m['_categories']:
        entry_price = float(m.get('lastTradePrice', 0.5))
        if entry_price >= 0.6:  # Fade when YES > 60%
            if m['_resolved_no']:
                gross_return = entry_price / (1 - entry_price) if entry_price < 1 else 1
                crypto_trades.append({
                    'market_id': m['id'],
                    'question': m['question'][:60],
                    'entry_price': entry_price,
                    'win': True,
                    'gross_return': gross_return
                })
            else:
                crypto_trades.append({
                    'market_id': m['id'],
                    'question': m['question'][:60],
                    'entry_price': entry_price,
                    'win': False,
                    'gross_return': 0
                })

strategy_j = calculate_strategy_metrics(crypto_trades)
if strategy_j:
    print(f"Trades: {strategy_j['trades']}, Wins: {strategy_j['wins']}, Win Rate: {strategy_j['win_rate']*100:.1f}%")
    print(f"Avg Return: {strategy_j['avg_return']:.2f}, Total P&L: {strategy_j['total_pnl']:.2f}")
    print(f"Sharpe: {strategy_j['sharpe_ratio']:.2f}, Max DD: {strategy_j['max_drawdown']:.1f}%")

# Compile all strategies
all_strategies = {
    'A_Celebrity_Fade': strategy_a,
    'B_Tech_Hype_Fade': strategy_b,
    'C_Viral_Event_Fade': strategy_c,
    'D_Consensus_Enhanced': strategy_d,
    'E_Long_Duration_Fade': strategy_e,
    'F_High_Hype_Score': strategy_f,
    'G_Low_Vol_High_Price': strategy_g,
    'H_Multi_Factor': strategy_h,
    'I_Extreme_Consensus': strategy_i,
    'J_Crypto_Fade': strategy_j
}

# Filter valid strategies (50+ trades)
valid_strategies = {k: v for k, v in all_strategies.items() if v and v['trades'] >= 20}

print("\n" + "="*70)
print("STRATEGY COMPARISON SUMMARY")
print("="*70)
print(f"{'Strategy':<25} {'Trades':>8} {'Win%':>8} {'P&L':>10} {'Sharpe':>8} {'Max DD':>8}")
print("-" * 70)

sorted_strategies = sorted(valid_strategies.items(), key=lambda x: x[1]['win_rate'], reverse=True)
for name, metrics in sorted_strategies:
    print(f"{name:<25} {metrics['trades']:>8} {metrics['win_rate']*100:>7.1f}% "
          f"{metrics['total_pnl']:>9.1f} {metrics['sharpe_ratio']:>7.2f} {metrics['max_drawdown']:>7.1f}%")

# Save all results
with open('analysis6_strategies.json', 'w') as f:
    json.dump({k: {sk: sv for sk, sv in v.items() if sk != 'trades_detail'} 
               for k, v in valid_strategies.items()}, f, indent=2)
print("\nSaved: analysis6_strategies.json")

print("\n" + "="*70)
print("ANALYSIS COMPLETE - Results saved to JSON files")
print("="*70)
