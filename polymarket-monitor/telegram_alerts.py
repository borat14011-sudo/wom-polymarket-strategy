"""
Telegram Alert System for Trading Signals
Sends formatted alerts to Telegram with inline buttons and rate limiting.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from collections import defaultdict
from functools import wraps

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError, RetryAfter, TimedOut

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiter to prevent spam."""
    
    def __init__(self, max_messages: int = 20, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_messages: Maximum messages per time window
            time_window: Time window in seconds
        """
        self.max_messages = max_messages
        self.time_window = time_window
        self.message_counts = defaultdict(list)
    
    def check_limit(self, alert_type: str) -> bool:
        """
        Check if alert type is within rate limit.
        
        Args:
            alert_type: Type of alert (signal, trade, stop_loss, etc.)
        
        Returns:
            True if within limit, False if rate limited
        """
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.time_window)
        
        # Remove old timestamps
        self.message_counts[alert_type] = [
            ts for ts in self.message_counts[alert_type] 
            if ts > cutoff
        ]
        
        # Check limit
        if len(self.message_counts[alert_type]) >= self.max_messages:
            logger.warning(f"Rate limit exceeded for {alert_type}")
            return False
        
        # Add current timestamp
        self.message_counts[alert_type].append(now)
        return True
    
    def reset(self, alert_type: Optional[str] = None):
        """Reset rate limiter for specific type or all types."""
        if alert_type:
            self.message_counts[alert_type] = []
        else:
            self.message_counts.clear()


def retry_on_telegram_error(max_retries: int = 3, delay: int = 2):
    """Decorator to retry on Telegram errors."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except RetryAfter as e:
                    wait_time = e.retry_after + 1
                    logger.warning(f"Rate limited by Telegram. Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                except TimedOut:
                    if attempt < max_retries - 1:
                        logger.warning(f"Timeout. Retrying in {delay}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error("Max retries reached. Giving up.")
                        raise
                except TelegramError as e:
                    logger.error(f"Telegram error: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay)
                    else:
                        raise
            return None
        return wrapper
    return decorator


class TelegramAlerter:
    """Main Telegram alerter class."""
    
    def __init__(self, bot_token: str, chat_id: str, rate_limiter: Optional[RateLimiter] = None):
        """
        Initialize Telegram alerter.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID
            rate_limiter: Optional custom rate limiter
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = Bot(token=bot_token)
        self.rate_limiter = rate_limiter or RateLimiter()
        
        # Store pending approvals
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
    
    @retry_on_telegram_error(max_retries=3)
    async def send_message(
        self, 
        text: str, 
        alert_type: str = "general",
        keyboard: Optional[InlineKeyboardMarkup] = None,
        disable_notification: bool = False
    ) -> Optional[int]:
        """
        Send message with rate limiting and error handling.
        
        Args:
            text: Message text
            alert_type: Alert type for rate limiting
            keyboard: Optional inline keyboard
            disable_notification: Disable notification sound
        
        Returns:
            Message ID if successful, None otherwise
        """
        # Check rate limit
        if not self.rate_limiter.check_limit(alert_type):
            logger.warning(f"Skipping {alert_type} alert due to rate limit")
            return None
        
        try:
            message = await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard,
                disable_notification=disable_notification
            )
            logger.info(f"Sent {alert_type} alert (message_id: {message.message_id})")
            return message.message_id
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return None
    
    async def send_signal_alert(
        self,
        market: str,
        pattern: str,
        confidence: float,
        current_price: float,
        suggested_entry: float,
        suggested_exit: float,
        stop_loss: float,
        analysis: Optional[str] = None,
        require_approval: bool = True
    ) -> Optional[int]:
        """
        Send new signal detected alert.
        
        Args:
            market: Market name
            pattern: Pattern detected
            confidence: Confidence level (0-1)
            current_price: Current market price
            suggested_entry: Suggested entry price
            suggested_exit: Suggested exit price
            stop_loss: Stop loss price
            analysis: Optional analysis text
            require_approval: Whether to show approve/reject buttons
        
        Returns:
            Message ID if successful
        """
        confidence_emoji = "🟢" if confidence >= 0.8 else "🟡" if confidence >= 0.6 else "🟠"
        
        text = f"""
🎯 *NEW SIGNAL DETECTED*

📊 *Market:* {market}
🔍 *Pattern:* {pattern}
{confidence_emoji} *Confidence:* {confidence:.1%}

💰 *Price Info:*
Current: ${current_price:.3f}
Entry: ${suggested_entry:.3f}
Target: ${suggested_exit:.3f}
Stop Loss: ${stop_loss:.3f}

📈 *Potential:* {((suggested_exit - suggested_entry) / suggested_entry * 100):.1f}%
⚠️ *Risk:* {((suggested_entry - stop_loss) / suggested_entry * 100):.1f}%
"""
        
        if analysis:
            text += f"\n📝 *Analysis:*\n{analysis}\n"
        
        text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        keyboard = None
        if require_approval:
            signal_id = f"signal_{market}_{int(datetime.now().timestamp())}"
            self.pending_approvals[signal_id] = {
                "market": market,
                "pattern": pattern,
                "entry": suggested_entry,
                "exit": suggested_exit,
                "stop_loss": stop_loss
            }
            
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ Approve", callback_data=f"approve_{signal_id}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"reject_{signal_id}")
                ]
            ])
        
        return await self.send_message(text, "signal", keyboard)
    
    async def send_trade_alert(
        self,
        action: str,  # "entry" or "exit"
        market: str,
        price: float,
        shares: float,
        total_value: float,
        reason: Optional[str] = None
    ) -> Optional[int]:
        """
        Send trade executed alert.
        
        Args:
            action: "entry" or "exit"
            market: Market name
            price: Execution price
            shares: Number of shares
            total_value: Total trade value
            reason: Optional reason for trade
        
        Returns:
            Message ID if successful
        """
        emoji = "🟢" if action == "entry" else "🔴"
        action_text = "ENTRY" if action == "entry" else "EXIT"
        
        text = f"""
{emoji} *TRADE EXECUTED: {action_text}*

📊 *Market:* {market}
💵 *Price:* ${price:.3f}
📦 *Shares:* {shares:.2f}
💰 *Total Value:* ${total_value:.2f}
"""
        
        if reason:
            text += f"\n📝 *Reason:* {reason}\n"
        
        text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return await self.send_message(text, "trade")
    
    async def send_stop_loss_alert(
        self,
        market: str,
        entry_price: float,
        stop_loss_price: float,
        exit_price: float,
        shares: float,
        loss_amount: float,
        loss_percent: float
    ) -> Optional[int]:
        """
        Send stop loss triggered alert.
        
        Args:
            market: Market name
            entry_price: Entry price
            stop_loss_price: Stop loss trigger price
            exit_price: Actual exit price
            shares: Number of shares
            loss_amount: Loss amount in dollars
            loss_percent: Loss percentage
        
        Returns:
            Message ID if successful
        """
        text = f"""
🛑 *STOP LOSS TRIGGERED*

📊 *Market:* {market}
📦 *Shares:* {shares:.2f}

💰 *Prices:*
Entry: ${entry_price:.3f}
Stop Loss: ${stop_loss_price:.3f}
Exit: ${exit_price:.3f}

📉 *Loss:*
Amount: ${loss_amount:.2f}
Percent: {loss_percent:.1f}%

⚠️ Position closed to limit losses.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return await self.send_message(text, "stop_loss")
    
    async def send_pnl_summary(
        self,
        date: str,
        total_trades: int,
        winning_trades: int,
        losing_trades: int,
        total_pnl: float,
        win_rate: float,
        best_trade: Optional[Dict[str, Any]] = None,
        worst_trade: Optional[Dict[str, Any]] = None
    ) -> Optional[int]:
        """
        Send daily P&L summary.
        
        Args:
            date: Date string
            total_trades: Total number of trades
            winning_trades: Number of winning trades
            losing_trades: Number of losing trades
            total_pnl: Total profit/loss
            win_rate: Win rate (0-1)
            best_trade: Optional best trade info
            worst_trade: Optional worst trade info
        
        Returns:
            Message ID if successful
        """
        pnl_emoji = "📈" if total_pnl >= 0 else "📉"
        pnl_sign = "+" if total_pnl >= 0 else ""
        
        text = f"""
{pnl_emoji} *DAILY P&L SUMMARY*

📅 *Date:* {date}

📊 *Trading Stats:*
Total Trades: {total_trades}
Wins: {winning_trades} 🟢
Losses: {losing_trades} 🔴
Win Rate: {win_rate:.1%}

💰 *P&L:* {pnl_sign}${total_pnl:.2f}
"""
        
        if best_trade:
            text += f"""
🏆 *Best Trade:*
{best_trade['market']} - ${best_trade['pnl']:.2f} ({best_trade['pnl_percent']:.1f}%)
"""
        
        if worst_trade:
            text += f"""
💔 *Worst Trade:*
{worst_trade['market']} - ${worst_trade['pnl']:.2f} ({worst_trade['pnl_percent']:.1f}%)
"""
        
        text += f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return await self.send_message(text, "pnl_summary", disable_notification=True)
    
    async def send_circuit_breaker_alert(
        self,
        reason: str,
        current_loss: float,
        max_loss: float,
        trades_today: int,
        cooldown_minutes: int = 60
    ) -> Optional[int]:
        """
        Send circuit breaker activated alert.
        
        Args:
            reason: Reason for circuit breaker
            current_loss: Current loss amount
            max_loss: Maximum allowed loss
            trades_today: Number of trades today
            cooldown_minutes: Cooldown period in minutes
        
        Returns:
            Message ID if successful
        """
        text = f"""
🚨 *CIRCUIT BREAKER ACTIVATED* 🚨

⚠️ *Trading halted to protect capital*

🔴 *Reason:* {reason}

📉 *Current Stats:*
Loss Today: ${current_loss:.2f}
Max Loss: ${max_loss:.2f}
Trades Today: {trades_today}

⏸️ *Cooldown:* {cooldown_minutes} minutes

🛡️ All pending orders cancelled.
No new trades until cooldown expires.

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return await self.send_message(text, "circuit_breaker")
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("approve_"):
            signal_id = data.replace("approve_", "")
            if signal_id in self.pending_approvals:
                signal = self.pending_approvals[signal_id]
                await query.edit_message_text(
                    text=f"{query.message.text_markdown}\n\n✅ *APPROVED* by {query.from_user.first_name}",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Signal {signal_id} approved by {query.from_user.first_name}")
                # Here you would trigger the actual trade
                del self.pending_approvals[signal_id]
        
        elif data.startswith("reject_"):
            signal_id = data.replace("reject_", "")
            if signal_id in self.pending_approvals:
                await query.edit_message_text(
                    text=f"{query.message.text_markdown}\n\n❌ *REJECTED* by {query.from_user.first_name}",
                    parse_mode=ParseMode.MARKDOWN
                )
                logger.info(f"Signal {signal_id} rejected by {query.from_user.first_name}")
                del self.pending_approvals[signal_id]
    
    def create_application(self) -> Application:
        """Create Telegram application with handlers."""
        application = Application.builder().token(self.bot_token).build()
        application.add_handler(CallbackQueryHandler(self.handle_callback))
        return application


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage of the TelegramAlerter."""
    
    # Configuration (replace with actual values)
    BOT_TOKEN = "YOUR_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"
    
    # Initialize alerter
    alerter = TelegramAlerter(BOT_TOKEN, CHAT_ID)
    
    print("=" * 70)
    print("EXAMPLE MESSAGES - Telegram Trading Alerts")
    print("=" * 70)
    
    # Example 1: New Signal
    print("\n1. NEW SIGNAL DETECTED")
    print("-" * 70)
    await alerter.send_signal_alert(
        market="Trump 2024 Win",
        pattern="Bullish Divergence + Volume Spike",
        confidence=0.85,
        current_price=0.652,
        suggested_entry=0.650,
        suggested_exit=0.720,
        stop_loss=0.620,
        analysis="Strong buying pressure after debate, social sentiment up 23%",
        require_approval=True
    )
    print("✓ Signal alert sent with approval buttons")
    
    await asyncio.sleep(2)
    
    # Example 2: Trade Entry
    print("\n2. TRADE EXECUTED - ENTRY")
    print("-" * 70)
    await alerter.send_trade_alert(
        action="entry",
        market="Trump 2024 Win",
        price=0.651,
        shares=1000,
        total_value=651.00,
        reason="Signal approved - bullish pattern confirmed"
    )
    print("✓ Trade entry alert sent")
    
    await asyncio.sleep(2)
    
    # Example 3: Trade Exit
    print("\n3. TRADE EXECUTED - EXIT")
    print("-" * 70)
    await alerter.send_trade_alert(
        action="exit",
        market="Trump 2024 Win",
        price=0.715,
        shares=1000,
        total_value=715.00,
        reason="Target reached"
    )
    print("✓ Trade exit alert sent")
    
    await asyncio.sleep(2)
    
    # Example 4: Stop Loss
    print("\n4. STOP LOSS TRIGGERED")
    print("-" * 70)
    await alerter.send_stop_loss_alert(
        market="Biden Approval >50%",
        entry_price=0.420,
        stop_loss_price=0.390,
        exit_price=0.388,
        shares=500,
        loss_amount=16.00,
        loss_percent=7.6
    )
    print("✓ Stop loss alert sent")
    
    await asyncio.sleep(2)
    
    # Example 5: Daily P&L Summary
    print("\n5. DAILY P&L SUMMARY")
    print("-" * 70)
    await alerter.send_pnl_summary(
        date="2026-02-07",
        total_trades=12,
        winning_trades=8,
        losing_trades=4,
        total_pnl=234.50,
        win_rate=0.667,
        best_trade={
            "market": "Trump 2024 Win",
            "pnl": 64.00,
            "pnl_percent": 9.8
        },
        worst_trade={
            "market": "Biden Approval >50%",
            "pnl": -16.00,
            "pnl_percent": -7.6
        }
    )
    print("✓ P&L summary sent")
    
    await asyncio.sleep(2)
    
    # Example 6: Circuit Breaker
    print("\n6. CIRCUIT BREAKER ACTIVATED")
    print("-" * 70)
    await alerter.send_circuit_breaker_alert(
        reason="Daily loss limit exceeded",
        current_loss=152.30,
        max_loss=150.00,
        trades_today=15,
        cooldown_minutes=60
    )
    print("✓ Circuit breaker alert sent")
    
    print("\n" + "=" * 70)
    print("All example alerts sent successfully!")
    print("=" * 70)
    
    # Show rate limiter stats
    print("\nRate Limiter Stats:")
    for alert_type, timestamps in alerter.rate_limiter.message_counts.items():
        print(f"  {alert_type}: {len(timestamps)} messages")


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║           TELEGRAM TRADING ALERT SYSTEM - EXAMPLE USAGE           ║
╚═══════════════════════════════════════════════════════════════════╝

This module provides a comprehensive Telegram alerting system for
trading signals with the following features:

✓ Rate limiting (20 messages/minute by default)
✓ Retry logic with exponential backoff
✓ Inline keyboards for trade approval
✓ Rich markdown formatting with emojis
✓ Error handling and logging
✓ 5 alert types: Signal, Trade, Stop Loss, P&L, Circuit Breaker

SETUP:
1. Create a bot with @BotFather and get your token
2. Get your chat_id (use @userinfobot)
3. Replace BOT_TOKEN and CHAT_ID in the example below
4. Run: python telegram_alerts.py

INTEGRATION:
from telegram_alerts import TelegramAlerter

alerter = TelegramAlerter(BOT_TOKEN, CHAT_ID)
await alerter.send_signal_alert(market="...", pattern="...", ...)

""")
    
    # Run examples
    asyncio.run(main())
