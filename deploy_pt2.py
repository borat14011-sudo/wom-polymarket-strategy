"""
Deploy $100 Paper Trading Portfolio on Experimental Strategies
Using live Polymarket data
"""
import json
import sys
sys.path.insert(0, 'polymarket-monitor/historical-data-scraper')

from paper_trader_2 import PaperTrader2

# Load the live market data
with open('markets_live_snapshot.json', 'r') as f:
    markets = json.load(f)

print("=" * 80)
print("PAPER TRADER 2 - DEPLOYING $100 ON EXPERIMENTAL STRATEGIES")
print("=" * 80)
print(f"Markets scanned: {len(markets)}")
print()

# Initialize trader
trader = PaperTrader2('polymarket-monitor/historical-data-scraper/data/paper_portfolio_pt2.json')

# Show starting state
summary = trader.get_portfolio_summary()
print(f"Starting Balance: ${summary['initial_balance']:.2f}")
print(f"Available: ${summary['available']:.2f}")
print()

# Scan for signals
print("Scanning markets for signals...")
signals = trader.scan_for_signals(markets)

# Sort by confidence (highest first)
signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)

print(f"Found {len(signals)} trading signals")
print()

# Execute trades on top signals
executed = 0
skipped = 0

print("=" * 80)
print("EXECUTING PAPER TRADES")
print("=" * 80)

for signal in signals[:10]:  # Top 10 signals
    result = trader.execute_paper_trade(signal)
    
    if result['status'] == 'executed':
        executed += 1
        pos = result['position']
        print(f"\n[EXECUTED] TRADE #{executed}")
        print(f"   Strategy: {pos['strategy']}")
        print(f"   Market: {pos['question'][:70]}...")
        print(f"   Direction: {pos['direction']}")
        print(f"   Entry: ${pos['entry_price']:.3f}")
        print(f"   Size: ${pos['size']:.2f}")
        print(f"   Risk: {pos['risk_level'].upper()}")
        print(f"   Remaining Balance: ${result['remaining_balance']:.2f}")
    else:
        skipped += 1
        print(f"\n[SKIPPED] {result['reason']}")

# Final summary
print("\n" + "=" * 80)
print("DEPLOYMENT SUMMARY")
print("=" * 80)

final_summary = trader.get_portfolio_summary()
print(f"\nInitial Balance: ${final_summary['initial_balance']:.2f}")
print(f"Allocated: ${final_summary['allocated']:.2f}")
print(f"Available Cash: ${final_summary['available']:.2f}")
print(f"Open Positions: {final_summary['open_positions']}")
print(f"Trades Executed: {final_summary['total_trades']}")

if final_summary['strategies_deployed']:
    print(f"\nStrategies Deployed:")
    for strat in final_summary['strategies_deployed']:
        print(f"   - {strat}")

# Save signal details
with open('polymarket-monitor/historical-data-scraper/data/pt2_signals.json', 'w') as f:
    json.dump(signals, f, indent=2)

print(f"\nSignals saved to: data/pt2_signals.json")
print(f"Portfolio saved to: data/paper_portfolio_pt2.json")
print("\n" + "=" * 80)
print("PAPER TRADER 2 DEPLOYMENT COMPLETE")
print("=" * 80)
