#!/usr/bin/env python3
"""
Forward Test Tracker for Polymarket Strategies
Tracks paper trades with 0.5% position sizing ($0.50 per trade)
Goal: Validate strategies with 30+ real-time trades before scaling up
"""

import json
import os
from datetime import datetime

TRACKER_FILE = "forward_test_results.json"
CAPITAL = 100.00  # Total capital for forward testing
MAX_POSITION_PCT = 0.005  # 0.5% per trade = $0.50
MAX_POSITIONS = 10

def load_tracker():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, 'r') as f:
            return json.load(f)
    return {
        "created": datetime.now().isoformat(),
        "capital": CAPITAL,
        "trades": [],
        "strategy_stats": {}
    }

def save_tracker(data):
    with open(TRACKER_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved to {TRACKER_FILE}")

def add_paper_trade(strategy, market, side, entry_price, size_usd=None):
    """Add a new paper trade"""
    tracker = load_tracker()
    
    if size_usd is None:
        size_usd = CAPITAL * MAX_POSITION_PCT  # $0.50 default
    
    trade = {
        "id": len(tracker["trades"]) + 1,
        "strategy": strategy,
        "market": market,
        "side": side,  # "YES" or "NO"
        "entry_price": entry_price,
        "entry_time": datetime.now().isoformat(),
        "size_usd": size_usd,
        "shares": size_usd / entry_price,
        "status": "OPEN",
        "exit_price": None,
        "exit_time": None,
        "pnl": None,
        "result": None  # "WIN", "LOSS", or "PUSH"
    }
    
    tracker["trades"].append(trade)
    save_tracker(tracker)
    
    print(f"\n📝 PAPER TRADE #{trade['id']} OPENED")
    print(f"   Strategy: {strategy}")
    print(f"   Market: {market}")
    print(f"   Side: {side} at {entry_price:.4f}")
    print(f"   Size: ${size_usd:.2f} ({trade['shares']:.2f} shares)")
    
    return trade

def close_trade(trade_id, exit_price, result):
    """Close a paper trade with result"""
    tracker = load_tracker()
    
    for trade in tracker["trades"]:
        if trade["id"] == trade_id and trade["status"] == "OPEN":
            trade["exit_price"] = exit_price
            trade["exit_time"] = datetime.now().isoformat()
            trade["status"] = "CLOSED"
            trade["result"] = result
            
            # Calculate P&L
            if result == "WIN":
                # Binary outcome: won the bet
                payout_per_share = 1.0 - trade["entry_price"]  # Profit per share
                gross_pnl = trade["shares"] * payout_per_share
                fees = trade["size_usd"] * 0.04  # 4% roundtrip fees
                trade["pnl"] = gross_pnl - fees
            elif result == "LOSS":
                # Lost the entire position plus fees
                trade["pnl"] = -trade["size_usd"]
            else:  # PUSH
                trade["pnl"] = -trade["size_usd"] * 0.02  # Just entry fees
            
            # Update strategy stats
            strategy = trade["strategy"]
            if strategy not in tracker["strategy_stats"]:
                tracker["strategy_stats"][strategy] = {
                    "trades": 0, "wins": 0, "losses": 0, 
                    "total_pnl": 0, "win_rate": 0
                }
            
            stats = tracker["strategy_stats"][strategy]
            stats["trades"] += 1
            if result == "WIN":
                stats["wins"] += 1
            elif result == "LOSS":
                stats["losses"] += 1
            stats["total_pnl"] += trade["pnl"]
            stats["win_rate"] = stats["wins"] / stats["trades"] * 100 if stats["trades"] > 0 else 0
            
            save_tracker(tracker)
            
            print(f"\n✅ TRADE #{trade_id} CLOSED")
            print(f"   Result: {result}")
            print(f"   P&L: ${trade['pnl']:.2f}")
            print(f"\n📊 {strategy} Stats: {stats['wins']}/{stats['trades']} wins ({stats['win_rate']:.1f}%), Total P&L: ${stats['total_pnl']:.2f}")
            
            return trade
    
    print(f"❌ Trade #{trade_id} not found or already closed")
    return None

def show_status():
    """Show current forward testing status"""
    tracker = load_tracker()
    
    print("\n" + "="*60)
    print("📊 FORWARD TEST STATUS")
    print("="*60)
    print(f"Capital: ${tracker['capital']:.2f}")
    print(f"Max Position: {MAX_POSITION_PCT*100:.1f}% (${CAPITAL*MAX_POSITION_PCT:.2f})")
    print(f"Total Trades: {len(tracker['trades'])}")
    
    open_trades = [t for t in tracker["trades"] if t["status"] == "OPEN"]
    closed_trades = [t for t in tracker["trades"] if t["status"] == "CLOSED"]
    
    print(f"\n🟢 OPEN POSITIONS: {len(open_trades)}")
    for t in open_trades:
        print(f"   #{t['id']} {t['strategy']}: {t['side']} {t['market'][:40]}... @ {t['entry_price']:.4f}")
    
    print(f"\n📈 CLOSED TRADES: {len(closed_trades)}")
    total_pnl = sum(t["pnl"] for t in closed_trades if t["pnl"])
    wins = len([t for t in closed_trades if t["result"] == "WIN"])
    losses = len([t for t in closed_trades if t["result"] == "LOSS"])
    
    print(f"   Wins: {wins}, Losses: {losses}")
    print(f"   Win Rate: {wins/(wins+losses)*100:.1f}%" if (wins+losses) > 0 else "   Win Rate: N/A")
    print(f"   Total P&L: ${total_pnl:.2f}")
    
    print(f"\n📊 STRATEGY BREAKDOWN:")
    for strategy, stats in tracker.get("strategy_stats", {}).items():
        print(f"   {strategy}: {stats['wins']}/{stats['trades']} ({stats['win_rate']:.1f}%) | P&L: ${stats['total_pnl']:.2f}")
    
    # Progress to 30-trade goal
    print(f"\n🎯 PROGRESS TO VALIDATION: {len(closed_trades)}/30 trades")
    print("="*60)

def get_recommended_trades():
    """Get recommended paper trades based on agent reports"""
    print("\n" + "="*60)
    print("🎯 RECOMMENDED FORWARD TEST TRADES")
    print("="*60)
    print("Based on 5-agent analysis, here are paper trades to track:\n")
    
    trades = [
        {
            "strategy": "DEPORTATION_MISPRICING",
            "market": "Trump deportations 250k-500k YES",
            "side": "YES",
            "price": 0.8905,
            "thesis": "Market at 89% but true probability ~70% - mispriced"
        },
        {
            "strategy": "TARIFF_EVENT_DRIVEN",
            "market": "Tariff revenue $200-500B YES",
            "side": "YES", 
            "price": 0.11,
            "thesis": "Market ignores March 12 tariff implementation"
        },
        {
            "strategy": "BTC_TIME_BIAS",
            "market": "MSTR 500K BTC Dec 31 NO",
            "side": "NO",
            "price": 0.835,
            "thesis": "Only validated strategy (58.8% WR)"
        }
    ]
    
    for i, t in enumerate(trades, 1):
        print(f"{i}. {t['strategy']}")
        print(f"   Market: {t['market']}")
        print(f"   Side: {t['side']} @ {t['price']:.2%}")
        print(f"   Thesis: {t['thesis']}")
        print(f"   Size: $0.50 (0.5% of capital)")
        print()
    
    print("To add a paper trade:")
    print("  python forward_test_tracker.py add <strategy> <market> <side> <price>")
    print("\nTo close a trade:")
    print("  python forward_test_tracker.py close <trade_id> <exit_price> <WIN/LOSS>")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        show_status()
        get_recommended_trades()
    elif sys.argv[1] == "status":
        show_status()
    elif sys.argv[1] == "recommend":
        get_recommended_trades()
    elif sys.argv[1] == "add" and len(sys.argv) >= 6:
        strategy = sys.argv[2]
        market = sys.argv[3]
        side = sys.argv[4]
        price = float(sys.argv[5])
        add_paper_trade(strategy, market, side, price)
    elif sys.argv[1] == "close" and len(sys.argv) >= 5:
        trade_id = int(sys.argv[2])
        exit_price = float(sys.argv[3])
        result = sys.argv[4].upper()
        close_trade(trade_id, exit_price, result)
    else:
        print("Usage:")
        print("  python forward_test_tracker.py [status|recommend]")
        print("  python forward_test_tracker.py add <strategy> <market> <side> <price>")
        print("  python forward_test_tracker.py close <trade_id> <exit_price> <WIN/LOSS>")
