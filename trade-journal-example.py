#!/usr/bin/env python3
"""
Trade Journal Example - Demonstrates all features
"""

from trade_journal import Journal
from datetime import datetime, timedelta
import random

def create_sample_trades():
    """Create sample trades to demonstrate the journal"""
    
    journal = Journal("example_trades.db")
    
    print("📝 Creating sample trade journal...\n")
    
    # Sample markets
    markets = [
        ("btc-80k-by-march", "Bitcoin to $80,000 by March 2026", "crypto"),
        ("trump-2024-election", "Trump wins 2024 election", "politics"),
        ("super-bowl-chiefs", "Chiefs win Super Bowl", "sports"),
        ("eth-5k-by-summer", "Ethereum to $5,000 by Summer", "crypto"),
        ("fed-rate-cut-march", "Fed cuts rates in March", "politics"),
    ]
    
    strategies = ["hype", "momentum", "mean-reversion"]
    signals = ["twitter-buzz", "whale-alert", "technical", "fundamental", "sentiment"]
    emotions = ["calm", "excited", "anxious", "fomo", "revenge", None]
    
    # Create 20 sample trades over the past week
    base_time = datetime.now() - timedelta(days=7)
    
    trade_ids = []
    
    for i in range(20):
        market = random.choice(markets)
        strategy = random.choice(strategies)
        signal = random.choice(signals)
        emotion = random.choice(emotions)
        
        # Entry time
        entry_time = base_time + timedelta(hours=random.randint(0, 168))
        
        # Random entry
        entry_price = random.uniform(0.30, 0.70)
        size = random.randint(50, 500)
        confidence = random.uniform(50, 95)
        
        notes = [
            "Strong Twitter momentum",
            "Following whale wallet",
            "Oversold on daily chart",
            "News catalyst",
            "Contrarian play",
            "Riding the hype wave",
            None
        ]
        
        trade_id = journal.log_entry(
            market_id=market[0],
            market_name=market[1],
            price=entry_price,
            size=size,
            signal=signal,
            confidence=confidence,
            category=market[2],
            strategy=strategy,
            notes=random.choice(notes),
            emotion=emotion,
            entry_timestamp=entry_time.isoformat()
        )
        
        trade_ids.append(trade_id)
        
        # 80% chance to close the trade
        if random.random() < 0.8:
            # Exit price (60% chance of profit)
            if random.random() < 0.6:
                exit_price = entry_price + random.uniform(0.05, 0.20)  # Win
            else:
                exit_price = entry_price - random.uniform(0.02, 0.15)  # Loss
            
            # Exit time (1-24 hours later)
            exit_time = entry_time + timedelta(hours=random.randint(1, 24))
            
            exit_notes = [
                "TP1 hit",
                "Stop loss triggered",
                "Market momentum shifted",
                "Taking profit early",
                "Cut losses quick",
                None
            ]
            
            journal.log_exit(
                trade_id=trade_id,
                price=exit_price,
                notes=random.choice(exit_notes),
                exit_timestamp=exit_time.isoformat()
            )
            
            # Tag some trades with quality
            if random.random() < 0.5:
                quality_tags = ["good", "bad", "lucky", "unlucky"]
                journal.tag_trade(trade_id, quality=random.choice(quality_tags))
    
    print(f"✅ Created {len(trade_ids)} sample trades\n")
    
    # Now demonstrate the features
    print("=" * 80)
    print("DEMONSTRATION OF TRADE JOURNAL FEATURES")
    print("=" * 80)
    
    # 1. Review recent trades
    print("\n📋 1. RECENT TRADES (Last 5)")
    print("-" * 80)
    
    trades = journal.get_trades(limit=5, closed_only=False)
    for trade in trades:
        status = "OPEN" if trade['exit_timestamp'] is None else trade['outcome'].upper()
        pnl_str = f"${trade['pnl']:.2f}" if trade['pnl'] is not None else "N/A"
        
        print(f"\n[{trade['id']}] {trade['market_name']}")
        print(f"  Entry: ${trade['entry_price']:.3f} @ {trade['entry_timestamp'][:16]}")
        print(f"  Strategy: {trade['strategy']} | Signal: {trade['signal']} | Category: {trade['category']}")
        print(f"  Confidence: {trade['confidence']:.0f}% | Emotion: {trade['emotion'] or 'calm'}")
        
        if trade['exit_timestamp']:
            print(f"  Exit: ${trade['exit_price']:.3f} | P&L: {pnl_str} ({trade['pnl_percent']:.2f}%) | {status}")
        else:
            print(f"  Status: {status}")
        
        if trade['quality']:
            print(f"  Quality: {trade['quality']}")
    
    # 2. Performance analytics
    print("\n\n📊 2. PERFORMANCE ANALYTICS")
    print("-" * 80)
    
    analytics = journal.get_analytics()
    overall = analytics['overall']
    
    print(f"\nOverall Performance:")
    print(f"  Total Trades: {overall['total_trades']}")
    print(f"  Win Rate: {overall['win_rate']:.1f}%")
    print(f"  Total P&L: ${overall['total_pnl'] or 0:.2f}")
    print(f"  Average P&L: ${overall['avg_pnl'] or 0:.2f}")
    print(f"  Best Trade: ${overall['best_trade'] or 0:.2f}")
    print(f"  Worst Trade: ${overall['worst_trade'] or 0:.2f}")
    print(f"  Expectancy: ${overall['expectancy']:.2f}")
    print(f"  Average Winner: ${overall['avg_win'] or 0:.2f}")
    print(f"  Average Loser: ${overall['avg_loss'] or 0:.2f}")
    
    if overall['avg_win'] and overall['avg_loss']:
        ratio = overall['avg_win'] / abs(overall['avg_loss'])
        print(f"  Win/Loss Ratio: {ratio:.2f}:1")
    
    print(f"\n📂 By Category:")
    for cat, stats in analytics['by_category'].items():
        print(f"  {cat:12s}: {stats['win_rate']:5.1f}% WR | ${stats['total_pnl']:7.2f} P&L | {stats['trades']:2d} trades")
    
    print(f"\n🎯 By Strategy:")
    for strat, stats in analytics['by_strategy'].items():
        print(f"  {strat:15s}: {stats['win_rate']:5.1f}% WR | ${stats['total_pnl']:7.2f} P&L | {stats['trades']:2d} trades")
    
    # 3. Behavioral analysis
    print("\n\n🧠 3. BEHAVIORAL ANALYSIS")
    print("-" * 80)
    
    print(f"\nPsychological Patterns:")
    print(f"  FOMO Trades: {overall['fomo_trades']}")
    print(f"  Revenge Trades: {overall['revenge_trades']}")
    print(f"  Overtrading Instances: {overall['overtrading_count']}")
    
    if analytics['by_quality']:
        print(f"\n📈 Trade Quality Assessment:")
        for quality, stats in analytics['by_quality'].items():
            print(f"  {quality:10s}: {stats['win_rate']:5.1f}% WR | ${stats['avg_pnl']:7.2f} avg | {stats['trades']:2d} trades")
    
    print(f"\n⏰ Performance by Hour (Top 5):")
    hours_sorted = sorted(analytics['by_hour'].items(), key=lambda x: x[1]['win_rate'], reverse=True)
    for hour, stats in hours_sorted[:5]:
        print(f"  {hour:02d}:00 - {stats['win_rate']:5.1f}% WR | ${stats['avg_pnl']:6.2f} avg | {stats['trades']:2d} trades")
    
    # 4. Trading insights
    print("\n\n🎯 4. TRADING INSIGHTS")
    print("-" * 80)
    
    insights = journal.get_insights()
    for insight in insights:
        print(f"  {insight}")
    
    # 5. Best and worst days
    print("\n\n📅 5. BEST & WORST DAYS")
    print("-" * 80)
    
    print("\n🏆 Best Days:")
    for day in analytics['best_days'][:3]:
        print(f"  {day['date']}: ${day['daily_pnl']:7.2f} ({day['trades']} trades)")
    
    print("\n❌ Worst Days:")
    for day in analytics['worst_days'][:3]:
        print(f"  {day['date']}: ${day['daily_pnl']:7.2f} ({day['trades']} trades)")
    
    # 6. Generate reports
    print("\n\n📄 6. REPORTS")
    print("-" * 80)
    
    print("\n--- Daily Report ---")
    daily_report = journal.generate_daily_report()
    print(daily_report[:500] + "..." if len(daily_report) > 500 else daily_report)
    
    print("\n--- Weekly Report (Summary) ---")
    weekly_report = journal.generate_weekly_report()
    print(weekly_report[:800] + "..." if len(weekly_report) > 800 else weekly_report)
    
    # 7. Export HTML
    print("\n\n📊 7. HTML EXPORT")
    print("-" * 80)
    
    export_result = journal.export_html("trade_journal_report.html", days=7)
    print(f"  {export_result}")
    
    print("\n" + "=" * 80)
    print("✅ DEMONSTRATION COMPLETE!")
    print("=" * 80)
    
    print("\n📝 CLI Commands to try:")
    print("  python trade-journal.py --db example_trades.db                  # Today's journal")
    print("  python trade-journal.py --db example_trades.db review           # Recent trades")
    print("  python trade-journal.py --db example_trades.db analytics        # Full analytics")
    print("  python trade-journal.py --db example_trades.db insights         # AI insights")
    print("  python trade-journal.py --db example_trades.db report weekly    # Weekly review")
    print("  python trade-journal.py --db example_trades.db export report.html  # HTML export")
    
    print("\n💡 Programmatic Usage:")
    print("""
from trade_journal import Journal

journal = Journal()

# Log entry
trade_id = journal.log_entry(
    market_id="btc-100k",
    market_name="Bitcoin to $100k by EOY",
    price=0.45,
    size=200,
    signal="hype",
    confidence=75,
    category="crypto",
    strategy="momentum",
    notes="Strong momentum after ETF approval",
    emotion="excited"
)

# Log exit
journal.log_exit(trade_id, price=0.62, notes="Target reached")

# Get analytics
analytics = journal.get_analytics()
print(f"Win Rate: {analytics['overall']['win_rate']:.1f}%")
print(f"Expectancy: ${analytics['overall']['expectancy']:.2f}")

# Get insights
insights = journal.get_insights()
for insight in insights:
    print(insight)
    """)
    
    journal.close()


if __name__ == "__main__":
    create_sample_trades()
