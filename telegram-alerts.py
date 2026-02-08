#!/usr/bin/env python3
"""
Telegram Alert Bot for Polymarket Trading System

A robust notification system with rich formatting, rate limiting, quiet hours,
and inline interactions.

Installation:
    pip install requests pyyaml

Quick Start:
    # First time setup
    python telegram-alerts.py --setup
    
    # Test your bot
    python telegram-alerts.py --test
    
    # Send a manual message
    python telegram-alerts.py --send "Hello from trading bot!"
    
    # Check bot status
    python telegram-alerts.py --status

Python Integration:
    from telegram_alerts import TelegramBot
    
    bot = TelegramBot()
    bot.send_signal("BUY", market="Bitcoin $100k", price=0.52, confidence="HIGH")
    bot.send_alert("System health warning", critical=False)
    bot.send_daily_summary(trades=5, pnl="+$150", win_rate=0.6)

Configuration:
    Edit config.yaml in the same directory:
    
    telegram:
      bot_token: "YOUR_BOT_TOKEN"
      chat_id: "YOUR_CHAT_ID"
    
    quiet_hours:
      enabled: true
      start: "23:00"
      end: "08:00"
    
    rate_limit:
      max_per_minute: 30
      cooldown_seconds: 2
"""

import argparse
import json
import os
import sys
import time
from collections import deque
from datetime import datetime, time as dt_time
from pathlib import Path
from typing import Dict, List, Optional, Any
import requests

# Import yaml with fallback
try:
    import yaml
except ImportError:
    print("⚠️  PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)


class RateLimiter:
    """Token bucket rate limiter for Telegram API calls."""
    
    def __init__(self, max_per_minute: int = 30, cooldown: float = 2.0):
        self.max_per_minute = max_per_minute
        self.cooldown = cooldown
        self.timestamps = deque(maxlen=max_per_minute)
    
    def wait_if_needed(self):
        """Block if rate limit would be exceeded."""
        now = time.time()
        
        # Remove timestamps older than 1 minute
        while self.timestamps and now - self.timestamps[0] > 60:
            self.timestamps.popleft()
        
        # If at limit, wait until oldest timestamp expires
        if len(self.timestamps) >= self.max_per_minute:
            sleep_time = 60 - (now - self.timestamps[0]) + 0.1
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        # Add cooldown between requests
        if self.timestamps:
            time_since_last = now - self.timestamps[-1]
            if time_since_last < self.cooldown:
                time.sleep(self.cooldown - time_since_last)
        
        self.timestamps.append(time.time())


class MessageQueue:
    """Queue for storing messages during quiet hours."""
    
    def __init__(self, queue_file: str = "telegram_queue.json"):
        self.queue_file = queue_file
        self.messages = self._load_queue()
    
    def _load_queue(self) -> List[Dict]:
        """Load queued messages from disk."""
        if os.path.exists(self.queue_file):
            try:
                with open(self.queue_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def _save_queue(self):
        """Save queued messages to disk."""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.messages, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save queue: {e}")
    
    def add(self, message: str, buttons: Optional[List[Dict]] = None):
        """Add a message to the queue."""
        self.messages.append({
            "message": message,
            "buttons": buttons,
            "queued_at": datetime.now().isoformat()
        })
        self._save_queue()
    
    def get_all(self) -> List[Dict]:
        """Get all queued messages."""
        return self.messages.copy()
    
    def clear(self):
        """Clear the queue."""
        self.messages = []
        self._save_queue()
    
    def count(self) -> int:
        """Get number of queued messages."""
        return len(self.messages)


class TelegramBot:
    """
    Telegram Alert Bot with rate limiting, quiet hours, and rich formatting.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize components
        rate_limit_config = self.config.get('rate_limit', {})
        self.rate_limiter = RateLimiter(
            max_per_minute=rate_limit_config.get('max_per_minute', 30),
            cooldown=rate_limit_config.get('cooldown_seconds', 2.0)
        )
        
        self.queue = MessageQueue()
        
        # Bot credentials
        self.token = self.config.get('telegram', {}).get('bot_token')
        self.chat_id = self.config.get('telegram', {}).get('chat_id')
        
        if not self.token or not self.chat_id:
            raise ValueError(
                "Missing telegram credentials in config.yaml. "
                "Run: python telegram-alerts.py --setup"
            )
        
        self.api_url = f"https://api.telegram.org/bot{self.token}"
    
    def _load_config(self) -> Dict:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            return self._create_default_config()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {}
    
    def _create_default_config(self) -> Dict:
        """Create default configuration."""
        return {
            'telegram': {
                'bot_token': '',
                'chat_id': ''
            },
            'quiet_hours': {
                'enabled': True,
                'start': '23:00',
                'end': '08:00'
            },
            'rate_limit': {
                'max_per_minute': 30,
                'cooldown_seconds': 2.0
            }
        }
    
    def _save_config(self):
        """Save configuration to YAML file."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        except Exception as e:
            print(f"⚠️  Error saving config: {e}")
    
    def _is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        quiet_config = self.config.get('quiet_hours', {})
        if not quiet_config.get('enabled', True):
            return False
        
        try:
            now = datetime.now().time()
            start = dt_time.fromisoformat(quiet_config.get('start', '23:00'))
            end = dt_time.fromisoformat(quiet_config.get('end', '08:00'))
            
            # Handle overnight quiet hours (e.g., 23:00 to 08:00)
            if start > end:
                return now >= start or now < end
            else:
                return start <= now < end
        except Exception:
            return False
    
    def _send_telegram_message(
        self,
        message: str,
        buttons: Optional[List[Dict]] = None,
        parse_mode: str = "Markdown"
    ) -> bool:
        """
        Send a message via Telegram Bot API.
        
        Args:
            message: Message text
            buttons: List of button dicts with 'text' and 'callback_data'
            parse_mode: Message parse mode (Markdown, HTML, or None)
        
        Returns:
            True if successful, False otherwise
        """
        self.rate_limiter.wait_if_needed()
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        # Add inline keyboard if buttons provided
        if buttons:
            keyboard = {
                'inline_keyboard': [[
                    {'text': btn['text'], 'callback_data': btn['callback_data']}
                    for btn in buttons
                ]]
            }
            payload['reply_markup'] = json.dumps(keyboard)
        
        try:
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to send message: {e}")
            return False
    
    def _send_or_queue(
        self,
        message: str,
        buttons: Optional[List[Dict]] = None,
        critical: bool = False
    ) -> bool:
        """
        Send message immediately or queue it based on quiet hours.
        
        Args:
            message: Message text
            buttons: Optional inline buttons
            critical: If True, send even during quiet hours
        
        Returns:
            True if sent/queued successfully
        """
        if critical or not self._is_quiet_hours():
            return self._send_telegram_message(message, buttons)
        else:
            self.queue.add(message, buttons)
            return True
    
    def send_signal(
        self,
        signal_type: str,
        market: str,
        price: float,
        confidence: str = "MEDIUM",
        reasoning: str = "",
        critical: bool = False
    ) -> bool:
        """
        Send a BUY or SELL trading signal.
        
        Args:
            signal_type: "BUY" or "SELL"
            market: Market name (e.g., "Bitcoin $100k")
            price: Current price (0.0-1.0 for Polymarket)
            confidence: "LOW", "MEDIUM", or "HIGH"
            reasoning: Optional reasoning for the signal
            critical: If True, send even during quiet hours
        
        Returns:
            True if sent/queued successfully
        """
        emoji = "🚀" if signal_type.upper() == "BUY" else "📉"
        
        message = f"{emoji} *{signal_type.upper()} SIGNAL*\n\n"
        message += f"📊 *Market:* {market}\n"
        message += f"💰 *Price:* {price:.4f}\n"
        message += f"🎯 *Confidence:* {confidence}\n"
        
        if reasoning:
            message += f"\n💡 *Reasoning:*\n{reasoning}\n"
        
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        buttons = [
            {'text': '✅ Acknowledge', 'callback_data': f'ack_{signal_type.lower()}'},
            {'text': '📊 View Details', 'callback_data': f'details_{market[:20]}'}
        ]
        
        return self._send_or_queue(message, buttons, critical)
    
    def send_risk_warning(
        self,
        message: str,
        current_loss: float = 0.0,
        limit: float = 0.0,
        critical: bool = True
    ) -> bool:
        """
        Send a risk warning alert.
        
        Args:
            message: Warning message
            current_loss: Current loss amount
            limit: Loss limit
            critical: If True, send even during quiet hours (default: True)
        
        Returns:
            True if sent/queued successfully
        """
        alert_text = "⚠️ *RISK WARNING*\n\n"
        alert_text += f"{message}\n\n"
        
        if current_loss and limit:
            percentage = (current_loss / limit * 100) if limit > 0 else 0
            alert_text += f"📉 *Current Loss:* ${current_loss:.2f}\n"
            alert_text += f"🚫 *Loss Limit:* ${limit:.2f}\n"
            alert_text += f"📊 *Usage:* {percentage:.1f}%\n"
        
        alert_text += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        buttons = [
            {'text': '✅ Acknowledge', 'callback_data': 'ack_risk'},
            {'text': '🛑 Stop Trading', 'callback_data': 'stop_trading'}
        ]
        
        return self._send_or_queue(alert_text, buttons, critical)
    
    def send_system_alert(
        self,
        message: str,
        component: str = "",
        critical: bool = False
    ) -> bool:
        """
        Send a system health alert.
        
        Args:
            message: Alert message
            component: Component name (optional)
            critical: If True, send even during quiet hours
        
        Returns:
            True if sent/queued successfully
        """
        alert_text = "🚨 *SYSTEM ALERT*\n\n"
        
        if component:
            alert_text += f"⚙️ *Component:* {component}\n"
        
        alert_text += f"📝 *Message:* {message}\n"
        alert_text += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        buttons = [
            {'text': '✅ Acknowledge', 'callback_data': 'ack_system'},
            {'text': '🔍 Investigate', 'callback_data': f'investigate_{component[:20]}'}
        ]
        
        return self._send_or_queue(alert_text, buttons, critical)
    
    def send_daily_summary(
        self,
        trades: int = 0,
        pnl: str = "$0",
        win_rate: float = 0.0,
        signals_generated: int = 0,
        critical: bool = False
    ) -> bool:
        """
        Send a daily performance summary.
        
        Args:
            trades: Number of trades executed
            pnl: Profit/Loss string (e.g., "+$150" or "-$50")
            win_rate: Win rate as decimal (0.0-1.0)
            signals_generated: Number of signals generated
            critical: If True, send even during quiet hours
        
        Returns:
            True if sent/queued successfully
        """
        # Determine emoji based on P&L
        pnl_emoji = "📈" if pnl.startswith("+") else "📉" if pnl.startswith("-") else "➡️"
        
        message = "📊 *DAILY SUMMARY*\n\n"
        message += f"📅 *Date:* {datetime.now().strftime('%Y-%m-%d')}\n\n"
        message += f"💼 *Trades Executed:* {trades}\n"
        message += f"{pnl_emoji} *P&L:* {pnl}\n"
        message += f"🎯 *Win Rate:* {win_rate*100:.1f}%\n"
        message += f"🔔 *Signals Generated:* {signals_generated}\n"
        
        # Add performance emoji
        if win_rate >= 0.7:
            performance = "🏆 Excellent"
        elif win_rate >= 0.5:
            performance = "✅ Good"
        elif win_rate >= 0.3:
            performance = "⚠️ Fair"
        else:
            performance = "❌ Poor"
        
        message += f"\n*Performance:* {performance}"
        
        buttons = [
            {'text': '📊 Full Report', 'callback_data': 'report_full'},
            {'text': '✅ Dismiss', 'callback_data': 'dismiss_summary'}
        ]
        
        return self._send_or_queue(message, buttons, critical)
    
    def send_alert(self, message: str, critical: bool = False) -> bool:
        """
        Send a generic alert message.
        
        Args:
            message: Alert message
            critical: If True, send even during quiet hours
        
        Returns:
            True if sent/queued successfully
        """
        alert_text = f"🔔 *ALERT*\n\n{message}\n\n"
        alert_text += f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        buttons = [
            {'text': '✅ Acknowledge', 'callback_data': 'ack_alert'}
        ]
        
        return self._send_or_queue(alert_text, buttons, critical)
    
    def flush_queue(self) -> int:
        """
        Send all queued messages (call this in the morning after quiet hours).
        
        Returns:
            Number of messages sent
        """
        messages = self.queue.get_all()
        count = len(messages)
        
        if count == 0:
            return 0
        
        # Send summary of queued messages first
        summary = f"🌅 *Good morning!*\n\n"
        summary += f"You had {count} queued message(s) during quiet hours.\n"
        summary += "Sending them now...\n"
        
        self._send_telegram_message(summary)
        
        # Send each queued message
        sent = 0
        for msg_data in messages:
            if self._send_telegram_message(msg_data['message'], msg_data.get('buttons')):
                sent += 1
        
        # Clear the queue
        self.queue.clear()
        
        return sent
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get bot status information.
        
        Returns:
            Dict with status information
        """
        return {
            'bot_configured': bool(self.token and self.chat_id),
            'quiet_hours_enabled': self.config.get('quiet_hours', {}).get('enabled', False),
            'is_quiet_hours': self._is_quiet_hours(),
            'queued_messages': self.queue.count(),
            'rate_limit': f"{self.rate_limiter.max_per_minute} msg/min",
            'config_path': self.config_path
        }
    
    def test_connection(self) -> bool:
        """
        Test the bot connection by sending a test message.
        
        Returns:
            True if successful
        """
        message = "✅ *Test Message*\n\n"
        message += "Your Telegram alert bot is working correctly!\n\n"
        message += f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self._send_telegram_message(message)


def setup_wizard():
    """Interactive setup wizard for first-time configuration."""
    print("\n" + "="*60)
    print("🤖 Telegram Alert Bot - Setup Wizard")
    print("="*60 + "\n")
    
    print("This wizard will help you configure your Telegram bot.\n")
    
    # Step 1: Bot Token
    print("📝 Step 1: Get your Bot Token")
    print("   1. Open Telegram and search for @BotFather")
    print("   2. Send /newbot and follow the instructions")
    print("   3. Copy the bot token\n")
    
    token = input("🔑 Enter your bot token: ").strip()
    if not token:
        print("❌ Bot token is required!")
        return False
    
    # Step 2: Chat ID
    print("\n📝 Step 2: Get your Chat ID")
    print("   1. Send a message to your bot")
    print("   2. Visit: https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates")
    print("   3. Look for 'chat':{'id': YOUR_CHAT_ID}")
    print("   (Or search for @userinfobot on Telegram)\n")
    
    chat_id = input("💬 Enter your chat ID: ").strip()
    if not chat_id:
        print("❌ Chat ID is required!")
        return False
    
    # Step 3: Quiet Hours
    print("\n📝 Step 3: Configure Quiet Hours")
    enable_quiet = input("🌙 Enable quiet hours? (y/n) [y]: ").strip().lower() or 'y'
    
    quiet_start = "23:00"
    quiet_end = "08:00"
    
    if enable_quiet == 'y':
        quiet_start = input("⏰ Quiet hours start (HH:MM) [23:00]: ").strip() or "23:00"
        quiet_end = input("⏰ Quiet hours end (HH:MM) [08:00]: ").strip() or "08:00"
    
    # Create config
    config = {
        'telegram': {
            'bot_token': token,
            'chat_id': chat_id
        },
        'quiet_hours': {
            'enabled': enable_quiet == 'y',
            'start': quiet_start,
            'end': quiet_end
        },
        'rate_limit': {
            'max_per_minute': 30,
            'cooldown_seconds': 2.0
        }
    }
    
    # Save config
    try:
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        print("\n" + "="*60)
        print("✅ Configuration saved to config.yaml")
        print("="*60 + "\n")
        
        # Test connection
        print("🧪 Testing connection...\n")
        try:
            bot = TelegramBot()
            if bot.test_connection():
                print("✅ Success! Your bot is ready to use.\n")
                print("Try running:")
                print("  python telegram-alerts.py --test")
                return True
            else:
                print("❌ Test failed. Check your token and chat ID.\n")
                return False
        except Exception as e:
            print(f"❌ Test failed: {e}\n")
            return False
    
    except Exception as e:
        print(f"❌ Failed to save config: {e}")
        return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Telegram Alert Bot for Polymarket Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python telegram-alerts.py --setup           # First time setup
  python telegram-alerts.py --test            # Send test message
  python telegram-alerts.py --status          # Check bot status
  python telegram-alerts.py --send "Hello!"   # Send custom message
  python telegram-alerts.py --flush           # Flush queued messages
        """
    )
    
    parser.add_argument('--setup', action='store_true',
                       help='Run interactive setup wizard')
    parser.add_argument('--test', action='store_true',
                       help='Send a test message')
    parser.add_argument('--status', action='store_true',
                       help='Show bot status')
    parser.add_argument('--send', type=str, metavar='MESSAGE',
                       help='Send a custom message')
    parser.add_argument('--flush', action='store_true',
                       help='Flush queued messages')
    parser.add_argument('--config', type=str, default='config.yaml',
                       help='Path to config file (default: config.yaml)')
    
    args = parser.parse_args()
    
    # Setup wizard
    if args.setup:
        setup_wizard()
        return
    
    # All other commands require a configured bot
    try:
        bot = TelegramBot(config_path=args.config)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Run: python telegram-alerts.py --setup")
        sys.exit(1)
    
    # Test connection
    if args.test:
        print("🧪 Sending test message...")
        if bot.test_connection():
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
            sys.exit(1)
        return
    
    # Show status
    if args.status:
        status = bot.get_status()
        print("\n" + "="*60)
        print("📊 Bot Status")
        print("="*60)
        print(f"✅ Configured: {status['bot_configured']}")
        print(f"🌙 Quiet Hours: {status['quiet_hours_enabled']}")
        print(f"🔕 Currently Quiet: {status['is_quiet_hours']}")
        print(f"📬 Queued Messages: {status['queued_messages']}")
        print(f"⏱️  Rate Limit: {status['rate_limit']}")
        print(f"📁 Config: {status['config_path']}")
        print("="*60 + "\n")
        return
    
    # Send custom message
    if args.send:
        print(f"📤 Sending message...")
        if bot.send_alert(args.send):
            print("✅ Message sent successfully!")
        else:
            print("❌ Failed to send message")
            sys.exit(1)
        return
    
    # Flush queue
    if args.flush:
        print("📬 Flushing message queue...")
        count = bot.flush_queue()
        print(f"✅ Sent {count} queued message(s)")
        return
    
    # No arguments - show help
    parser.print_help()


if __name__ == '__main__':
    main()
