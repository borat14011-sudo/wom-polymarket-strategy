#!/usr/bin/env python3
"""
Trade Journal Integration Example
Shows how to integrate the journal with your Polymarket trading system
"""

from trade_journal import Journal
from datetime import datetime
from typing import Optional


class JournaledTrader:
    """
    Example trader class with integrated trade journaling
    """
    
    def __init__(self, db_path: str = "polymarket_trades.db"):
        self.journal = Journal(db_path)
        self.active_trades = {}  # Maps order_id -> journal_trade_id
    
    def execute_trade(self, market_id: str, market_name: str, 
                      price: float, size: float, signal: str,
                      confidence: float, category: str, strategy: str,
                      notes: Optional[str] = None, emotion: Optional[str] = None) -> dict:
        """
        Execute trade and log to journal
        
        Returns:
            dict with order_id and trade_id
        """
        
        # Log entry in journal BEFORE executing
        trade_id = self.journal.log_entry(
            market_id=market_id,
            market_name=market_name,
            price=price,
            size=size,
            signal=signal,
            confidence=confidence,
            category=category,
            strategy=strategy,
            notes=notes,
            emotion=emotion
        )
        
        # Execute trade on Polymarket (your actual trading logic here)
        order_id = self._execute_polymarket_order(market_id, price, size)
        
        # Map order to journal entry
        self.active_trades[order_id] = trade_id
        
        print(f"✅ Trade executed: Order #{order_id} | Journal #{trade_id}")
        print(f"   {market_name}")
        print(f"   Entry: ${price:.3f} × {size} = ${price * size:.2f}")
        print(f"   Strategy: {strategy} | Signal: {signal} | Confidence: {confidence}%")
        
        return {
            'order_id': order_id,
            'trade_id': trade_id,
            'market_name': market_name,
            'entry_price': price,
            'size': size
        }
    
    def close_trade(self, order_id: int, exit_price: float, 
                    notes: Optional[str] = None) -> dict:
        """
        Close trade and log exit to journal
        
        Returns:
            dict with P&L and trade stats
        """
        
        # Get journal trade_id
        if order_id not in self.active_trades:
            raise ValueError(f"Order {order_id} not found in active trades")
        
        trade_id = self.active_trades[order_id]
        
        # Log exit in journal
        self.journal.log_exit(
            trade_id=trade_id,
            price=exit_price,
            notes=notes
        )
        
        # Get trade details for reporting
        trades = self.journal.get_trades(limit=1000)
        trade = next((t for t in trades if t['id'] == trade_id), None)
        
        if trade:
            pnl = trade['pnl']
            pnl_percent = trade['pnl_percent']
            outcome = trade['outcome']
            
            print(f"✅ Trade closed: Order #{order_id} | Journal #{trade_id}")
            print(f"   {trade['market_name']}")
            print(f"   Exit: ${exit_price:.3f}")
            print(f"   P&L: ${pnl:.2f} ({pnl_percent:.2f}%) | {outcome.upper()}")
            
            # Remove from active trades
            del self.active_trades[order_id]
            
            return {
                'trade_id': trade_id,
                'pnl': pnl,
                'pnl_percent': pnl_percent,
                'outcome': outcome
            }
        
        return {}
    
    def tag_trade_quality(self, order_id: int, quality: str):
        """
        Tag trade quality after reviewing it
        
        Args:
            order_id: Polymarket order ID
            quality: 'good', 'bad', 'lucky', 'unlucky'
        """
        if order_id not in self.active_trades:
            # Might be closed already, search by order_id
            # For now, just require trade_id
            raise ValueError(f"Order {order_id} not found. Use trade_id instead.")
        
        trade_id = self.active_trades[order_id]
        self.journal.tag_trade(trade_id, quality=quality)
        print(f"✅ Trade #{trade_id} tagged as '{quality}'")
    
    def check_performance_before_trading(self) -> bool:
        """
        Check recent performance and behavioral patterns before trading
        
        Returns:
            bool: True if OK to trade, False if should take a break
        """
        analytics = self.journal.get_analytics(days=7)
        insights = self.journal.get_insights()
        
        overall = analytics['overall']
        
        print("\n📊 Pre-Trade Performance Check")
        print("=" * 60)
        
        # Performance metrics
        print(f"Last 7 days:")
        print(f"  Win Rate: {overall['win_rate']:.1f}%")
        print(f"  Total P&L: ${overall['total_pnl'] or 0:.2f}")
        print(f"  Expectancy: ${overall['expectancy']:.2f}")
        
        # Behavioral issues
        issues = []
        
        if overall['win_rate'] < 45:
            issues.append("⚠️ Win rate below 45% - Consider reviewing strategy")
        
        if overall['expectancy'] < 0:
            issues.append("🚨 Negative expectancy - Stop trading until you fix this!")
        
        if overall['fomo_trades'] > 2:
            issues.append(f"⚠️ {overall['fomo_trades']} FOMO trades detected - Slow down!")
        
        if overall['revenge_trades'] > 0:
            issues.append(f"😤 {overall['revenge_trades']} revenge trades - Take a break!")
        
        if issues:
            print("\n⚠️ Issues Detected:")
            for issue in issues:
                print(f"  {issue}")
            
            # Serious issues = don't trade
            if overall['expectancy'] < 0 or overall['win_rate'] < 40:
                print("\n🚨 RECOMMENDATION: Take a break and review your strategy!")
                return False
        else:
            print("\n✅ All clear - Good to trade!")
        
        print()
        return True
    
    def daily_review(self):
        """
        Run daily performance review
        """
        report = self.journal.generate_daily_report()
        print(report)
        
        insights = self.journal.get_insights()
        print("\n🎯 Today's Insights:")
        for insight in insights:
            print(f"  {insight}")
    
    def weekly_review(self):
        """
        Run weekly performance review
        """
        report = self.journal.generate_weekly_report()
        print(report)
    
    def export_performance_report(self, output_path: str = "performance_report.html"):
        """
        Export detailed performance report
        """
        result = self.journal.export_html(output_path, days=30)
        print(result)
    
    def _execute_polymarket_order(self, market_id: str, price: float, size: float) -> int:
        """
        Placeholder for actual Polymarket order execution
        Replace this with your real trading logic
        """
        # This is where you'd call your Polymarket API
        # For now, just return a mock order_id
        import random
        return random.randint(10000, 99999)


def example_usage():
    """
    Example usage of the journaled trader
    """
    
    print("🚀 Trade Journal Integration Example")
    print("=" * 80)
    
    trader = JournaledTrader()
    
    # 1. Check performance before trading
    print("\n1️⃣ Pre-Trade Check")
    print("-" * 80)
    
    if trader.check_performance_before_trading():
        
        # 2. Execute a trade
        print("\n2️⃣ Execute Trade")
        print("-" * 80)
        
        trade = trader.execute_trade(
            market_id="btc-100k-eoy",
            market_name="Bitcoin to $100,000 by End of Year",
            price=0.52,
            size=100,
            signal="hype",
            confidence=75,
            category="crypto",
            strategy="momentum",
            notes="Strong momentum after ETF approval",
            emotion="excited"
        )
        
        order_id = trade['order_id']
        
        # 3. Later... close the trade
        print("\n3️⃣ Close Trade")
        print("-" * 80)
        
        result = trader.close_trade(
            order_id=order_id,
            exit_price=0.68,
            notes="Target reached, took profit at TP1"
        )
        
        # 4. Tag trade quality
        print("\n4️⃣ Tag Trade Quality")
        print("-" * 80)
        
        # Review: Did I follow my plan? Was it a quality trade?
        # Even if it won, if you broke your rules, it's a "bad" trade
        # Even if it lost, if you followed your rules, it's a "good" trade
        trader.journal.tag_trade(trade['trade_id'], quality="good")
        print(f"✅ Trade tagged as 'good' (followed the plan)")
        
        # 5. Daily review
        print("\n5️⃣ Daily Review")
        print("-" * 80)
        
        trader.daily_review()
    
    print("\n" + "=" * 80)
    print("✅ Integration example complete!")
    print("\nIntegrate this pattern into your Polymarket trading system:")
    print("1. Log every trade entry immediately")
    print("2. Log every trade exit with P&L")
    print("3. Tag trades for quality (good process vs good outcome)")
    print("4. Review performance daily/weekly")
    print("5. Use insights to improve your edge")


def automated_trading_loop_example():
    """
    Example of integrating journal into an automated trading loop
    """
    
    print("\n🤖 Automated Trading Loop Example")
    print("=" * 80)
    
    trader = JournaledTrader()
    
    # In a real system, this would be your trading loop
    while True:
        # 1. Check if it's safe to trade
        if not trader.check_performance_before_trading():
            print("⏸️ Pausing trading due to performance issues")
            break  # In real system: wait and retry later
        
        # 2. Get trading signal (your signal generation logic)
        signal = get_trading_signal()  # Your function
        
        if signal:
            # 3. Execute and journal the trade
            trade = trader.execute_trade(
                market_id=signal['market_id'],
                market_name=signal['market_name'],
                price=signal['price'],
                size=signal['size'],
                signal=signal['type'],
                confidence=signal['confidence'],
                category=signal['category'],
                strategy=signal['strategy'],
                notes=signal['reasoning'],
                emotion="calm"  # Automated = always calm
            )
            
            # 4. Monitor and close when conditions met
            # (your exit logic here)
            
            # 5. Log exit
            trader.close_trade(
                order_id=trade['order_id'],
                exit_price=signal['exit_price'],  # From your exit logic
                notes="Exit condition met"
            )
        
        # 6. Periodic review
        if is_end_of_day():  # Your function
            trader.daily_review()
        
        if is_end_of_week():  # Your function
            trader.weekly_review()
            trader.export_performance_report()
        
        break  # Just for example


def get_trading_signal():
    """Placeholder for your signal generation"""
    # Your actual signal logic here
    return None


def is_end_of_day():
    """Placeholder"""
    return False


def is_end_of_week():
    """Placeholder"""
    return False


if __name__ == "__main__":
    # Run the example
    example_usage()
    
    print("\n" + "=" * 80)
    print("\n💡 Key Integration Points:")
    print("""
1. **Initialize once:**
   trader = JournaledTrader()

2. **Before trading:**
   if trader.check_performance_before_trading():
       # Execute trades
   else:
       # Take a break, review strategy

3. **Execute trade:**
   trade = trader.execute_trade(
       market_id, market_name, price, size,
       signal, confidence, category, strategy,
       notes, emotion
   )

4. **Close trade:**
   trader.close_trade(order_id, exit_price, notes)

5. **Tag quality:**
   trader.journal.tag_trade(trade_id, quality="good")

6. **Daily review:**
   trader.daily_review()

7. **Weekly review:**
   trader.weekly_review()
   trader.export_performance_report()

8. **Get insights:**
   insights = trader.journal.get_insights()
   for insight in insights:
       print(insight)

9. **Analytics:**
   analytics = trader.journal.get_analytics(days=30)
   print(f"Win Rate: {analytics['overall']['win_rate']:.1f}%")
   print(f"Expectancy: ${analytics['overall']['expectancy']:.2f}")
    """)
    
    print("\n✅ Copy JournaledTrader class into your main trading system!")
    print("📊 Start building your edge through data-driven insights!")
    print("\n🎯 Great success! 🚀")
