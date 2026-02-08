"""
Telegram Alerter - Sends alerts for signals via OpenClaw
"""
import logging
import subprocess
import json
from datetime import datetime
from database import get_unalerted_signals, mark_signal_alerted

logger = logging.getLogger(__name__)

# Import Telegram settings from config
try:
    from config import TELEGRAM_TARGET
except ImportError:
    TELEGRAM_TARGET = "@MoneyManAmex"  # Fallback default


def format_signal_message(signal):
    """
    Format a signal into a Telegram message
    
    signal tuple: (id, market_id, market_name, rvr, roc, price, volume, timestamp)
    """
    signal_id, market_id, market_name, rvr, roc, price, volume, timestamp = signal
    
    # Format volume in millions/thousands
    if volume >= 1_000_000:
        volume_str = f"${volume/1_000_000:.1f}M"
    elif volume >= 1_000:
        volume_str = f"${volume/1_000:.0f}K"
    else:
        volume_str = f"${volume:.0f}"
    
    # Format price as percentage (0-100%)
    price_pct = price * 100
    
    # Format ROC with sign
    roc_sign = "+" if roc >= 0 else ""
    
    message = (
        f"🚨 POLYMARKET SIGNAL\n\n"
        f"📊 Market: {market_name}\n\n"
        f"📈 RVR: {rvr:.2f}x\n"
        f"📉 ROC: {roc_sign}{roc:.1f}%\n"
        f"💰 Price: {price_pct:.1f}%\n"
        f"💵 Volume: {volume_str}\n\n"
        f"⏰ {datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    return message


def send_telegram_message(message):
    """
    Send a message via OpenClaw's message tool
    
    Note: This needs to be called from within OpenClaw environment
    For standalone testing, this will fail gracefully
    """
    try:
        # Build the openclaw command
        # openclaw message send --channel telegram --target @username --message "text"
        cmd = [
            "openclaw",
            "message",
            "send",
            "--channel", "telegram",
            "--target", TELEGRAM_TARGET,
            "--message", message
        ]
        
        logger.info(f"Sending message to {TELEGRAM_TARGET}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            logger.info("Message sent successfully")
            return True
        else:
            logger.error(f"Failed to send message: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("Message send timeout")
        return False
    except FileNotFoundError:
        logger.error("OpenClaw CLI not found - are you running in OpenClaw environment?")
        return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False


def send_alerts():
    """
    Main function to send alerts for all unalerted signals
    """
    logger.info("=" * 60)
    logger.info(f"Checking for alerts at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    signals = get_unalerted_signals()
    
    if not signals:
        logger.info("No new signals to alert")
        logger.info("=" * 60)
        return 0
    
    logger.info(f"Found {len(signals)} signals to alert")
    
    sent_count = 0
    
    for signal in signals:
        signal_id = signal[0]
        market_name = signal[2]
        
        try:
            message = format_signal_message(signal)
            
            # Send the message
            if send_telegram_message(message):
                # Mark as alerted
                mark_signal_alerted(signal_id)
                sent_count += 1
                logger.info(f"✅ Alerted: {market_name[:40]}...")
            else:
                logger.warning(f"❌ Failed to alert: {market_name[:40]}...")
            
        except Exception as e:
            logger.error(f"Error processing signal {signal_id}: {e}")
    
    logger.info(f"Sent {sent_count}/{len(signals)} alerts")
    logger.info("=" * 60)
    
    return sent_count


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Test alert sending
    print("Testing Telegram alerter...")
    print(f"Target: {TELEGRAM_TARGET}")
    print()
    
    sent = send_alerts()
    print(f"\nSent {sent} alerts")
