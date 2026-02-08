#!/usr/bin/env python3
"""
Demo script showing how to use the Telegram Alert Bot in your trading system.

Run this after setting up config.yaml to see all alert types in action.
"""

from telegram_alerts import TelegramBot
import time

def demo_all_alerts():
    """Demonstrate all alert types."""
    
    print("🤖 Telegram Alert Bot Demo\n")
    
    # Initialize bot
    try:
        bot = TelegramBot()
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Run: python telegram-alerts.py --setup")
        return
    
    print("✅ Bot initialized\n")
    
    # 1. BUY Signal
    print("📤 Sending BUY signal...")
    bot.send_signal(
        signal_type="BUY",
        market="Bitcoin reaches $100k by March",
        price=0.52,
        confidence="HIGH",
        reasoning="Strong bullish momentum + favorable macro conditions"
    )
    time.sleep(2)
    
    # 2. SELL Signal
    print("📤 Sending SELL signal...")
    bot.send_signal(
        signal_type="SELL",
        market="Ethereum $5k by April",
        price=0.68,
        confidence="MEDIUM",
        reasoning="Price has peaked, volume declining"
    )
    time.sleep(2)
    
    # 3. Risk Warning
    print("📤 Sending risk warning...")
    bot.send_risk_warning(
        message="Portfolio approaching daily loss limit!",
        current_loss=450.00,
        limit=500.00,
        critical=False  # Will queue during quiet hours
    )
    time.sleep(2)
    
    # 4. System Alert
    print("📤 Sending system alert...")
    bot.send_system_alert(
        message="Data feed delayed by 15 minutes",
        component="Polymarket API",
        critical=False
    )
    time.sleep(2)
    
    # 5. Daily Summary
    print("📤 Sending daily summary...")
    bot.send_daily_summary(
        trades=12,
        pnl="+$347.50",
        win_rate=0.75,
        signals_generated=28
    )
    time.sleep(2)
    
    # 6. Generic Alert
    print("📤 Sending generic alert...")
    bot.send_alert(
        "Trading bot started successfully!",
        critical=False
    )
    
    print("\n✅ Demo complete! Check your Telegram for all messages.\n")
    
    # Show queue status
    status = bot.get_status()
    if status['queued_messages'] > 0:
        print(f"📬 {status['queued_messages']} message(s) queued (quiet hours active)")
        print("   Run: python telegram-alerts.py --flush")
    
    print()


def demo_trading_loop():
    """Simulate a trading bot sending periodic updates."""
    
    print("🔄 Simulating trading loop (5 iterations)...\n")
    
    try:
        bot = TelegramBot()
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    markets = [
        ("Bitcoin $100k", 0.52, "HIGH"),
        ("Ethereum $5k", 0.68, "MEDIUM"),
        ("S&P 500 new ATH", 0.73, "HIGH"),
        ("Gold $2500", 0.45, "LOW"),
        ("Tesla $300", 0.61, "MEDIUM")
    ]
    
    for i, (market, price, confidence) in enumerate(markets, 1):
        print(f"[{i}/5] Analyzing {market}...")
        
        # Simulate analysis delay
        time.sleep(1)
        
        # Send signal based on price
        signal = "BUY" if price < 0.60 else "SELL"
        
        bot.send_signal(
            signal_type=signal,
            market=market,
            price=price,
            confidence=confidence,
            reasoning=f"Automated signal based on price analysis"
        )
        
        print(f"       → {signal} signal sent\n")
        
        # Rate limiter will handle spacing
    
    print("✅ Trading loop simulation complete!\n")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--loop':
        demo_trading_loop()
    else:
        demo_all_alerts()
        
        print("💡 Try: python telegram_demo.py --loop")
        print("   (simulates a trading bot sending signals)\n")
