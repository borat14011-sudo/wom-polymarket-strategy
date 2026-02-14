"""
Update paper trades with current market prices
"""
import json
from datetime import datetime

# Current market prices (from research report)
current_prices = {
    "MSTR-500K-BTC-Dec31": 0.835,  # Same as entry
    "Trump-Deportations-250k-500k": 0.8995,  # From report: 89.95c
    "Tariff-Revenue-200-500B": 0.08  # From report: 8c
}

# Load paper trades
with open('forward_test_results.json', 'r') as f:
    data = json.load(f)

# Update each trade with current price and paper P&L
print("PAPER TRADE UPDATE - February 12, 2026 - 8:50 PM")
print("=" * 60)

for trade in data['trades']:
    market_key = trade['market']
    current_price = current_prices.get(market_key)
    
    if current_price is not None and trade['status'] == 'OPEN':
        entry_price = trade['entry_price']
        shares = trade['shares']
        size_usd = trade['size_usd']
        
        # Calculate paper P&L
        if trade['side'] == 'YES':
            # For YES positions: P&L = (current_price - entry_price) * shares
            paper_pnl = (current_price - entry_price) * shares
        else:  # NO position
            # For NO positions: P&L = ((1-current_price) - (1-entry_price)) * shares
            paper_pnl = ((1-current_price) - (1-entry_price)) * shares
        
        paper_pnl_percent = (paper_pnl / size_usd) * 100
        
        print(f"\nTrade #{trade['id']}: {trade['strategy']}")
        print(f"  Market: {market_key}")
        print(f"  Side: {trade['side']}")
        print(f"  Entry: {entry_price*100:.1f}c")
        print(f"  Current: {current_price*100:.1f}c")
        print(f"  Size: ${size_usd:.2f}")
        print(f"  Paper P&L: ${paper_pnl:.4f} ({paper_pnl_percent:+.1f}%)")
        
        # Update trade with current price and paper P&L
        trade['current_price'] = current_price
        trade['paper_pnl'] = paper_pnl
        trade['paper_pnl_percent'] = paper_pnl_percent
        trade['last_updated'] = datetime.now().isoformat()

# Calculate total paper P&L
total_paper_pnl = sum(trade.get('paper_pnl', 0) for trade in data['trades'])
total_paper_pnl_percent = (total_paper_pnl / data['capital']) * 100

print(f"\n" + "=" * 60)
print(f"TOTAL PAPER P&L: ${total_paper_pnl:.4f} ({total_paper_pnl_percent:+.2f}%)")
print(f"Capital: ${data['capital']:.2f}")
print(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Save updated data
with open('forward_test_results_updated.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"\nUpdated data saved to: forward_test_results_updated.json")

# Special note about tariff trade
print("\n" + "=" * 60)
print("🚨 TARIFF TRADE ALERT 🚨")
print("=" * 60)
tariff_trade = data['trades'][2]
print(f"Market dropped to {current_prices['Tariff-Revenue-200-500B']*100:.1f}c")
print(f"Paper gain: {tariff_trade['paper_pnl_percent']:+.1f}%")
print(f"Edge increased to: {35 - 8} percentage points")
print("ACTION: Execute REAL trade at 8c (manual execution required)")