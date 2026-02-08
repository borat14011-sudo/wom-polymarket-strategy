#!/usr/bin/env python3
"""
Emergency Kill Switch for Polymarket Trading System
SAFETY-CRITICAL CODE - Handle with extreme care

This module provides emergency stop functionality with graduated response levels,
automatic condition monitoring, and comprehensive audit logging.
"""

import os
import sys
import json
import argparse
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import IntEnum
import logging


class Level(IntEnum):
    """Kill switch response levels (graduated)"""
    STOP_NEW_TRADES = 1      # Stop new trades only
    CLOSE_WINNING = 2         # Close winning positions
    CLOSE_ALL = 3             # Close all positions
    FULL_SHUTDOWN = 4         # Full system shutdown


class KillSwitch:
    """
    Emergency kill switch for trading system.
    
    Thread-safe, persistent state, comprehensive logging.
    Designed to fail-safe: when in doubt, trigger.
    """
    
    DEFAULT_CONFIG = {
        "circuit_breaker_pct": -15.0,     # % drop from peak
        "daily_loss_limit_pct": -5.0,     # % daily loss
        "cooldown_hours": 24,              # Hours before manual reset allowed
        "state_file": "kill-switch-state.json",
        "log_file": "kill-switch-audit.log",
        "emergency_file": "EMERGENCY_STOP",  # Touch to trigger
    }
    
    def __init__(self, config_path: Optional[str] = None, workspace: Optional[str] = None):
        """
        Initialize kill switch.
        
        Args:
            config_path: Path to config JSON file (optional)
            workspace: Workspace directory (defaults to current directory)
        """
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Load configuration
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self.config.update(json.load(f))
        
        # Set up paths
        self.state_file = self.workspace / self.config["state_file"]
        self.log_file = self.workspace / self.config["log_file"]
        self.emergency_file = self.workspace / self.config["emergency_file"]
        
        # Set up logging
        self._setup_logging()
        
        # Load state
        self.state = self._load_state()
        
        # Log initialization
        self.logger.info("KillSwitch initialized", extra={
            "workspace": str(self.workspace),
            "armed": self.state.get("armed", False),
            "triggered": self.state.get("triggered", False)
        })
    
    def _setup_logging(self):
        """Set up audit logging"""
        self.logger = logging.getLogger("KillSwitch")
        self.logger.setLevel(logging.INFO)
        
        # File handler for audit trail
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Detailed format for audit trail
        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s | %(details)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add custom filter to include extra fields
        class ContextFilter(logging.Filter):
            def filter(self, record):
                if not hasattr(record, 'details'):
                    record.details = ''
                else:
                    record.details = json.dumps(record.__dict__.get('extra', {}))
                return True
        
        fh.addFilter(ContextFilter())
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def _load_state(self) -> Dict[str, Any]:
        """Load state from disk (thread-safe)"""
        with self.lock:
            if self.state_file.exists():
                try:
                    with open(self.state_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    self.logger.error(f"Failed to load state: {e}. Using default state.")
            
            # Default state
            return {
                "armed": False,
                "triggered": False,
                "trigger_level": None,
                "trigger_time": None,
                "trigger_reason": None,
                "triggered_by": None,
                "cooldown_until": None,
                "history": [],
                "peak_balance": None,
                "session_start_balance": None,
            }
    
    def _save_state(self):
        """Save state to disk (thread-safe, atomic)"""
        with self.lock:
            try:
                # Atomic write: write to temp file, then rename
                temp_file = self.state_file.with_suffix('.tmp')
                with open(temp_file, 'w') as f:
                    json.dump(self.state, f, indent=2)
                temp_file.replace(self.state_file)
                self.logger.debug("State saved successfully")
            except Exception as e:
                self.logger.error(f"CRITICAL: Failed to save state: {e}")
                raise
    
    def arm(self, armed: bool = True) -> bool:
        """
        Arm or disarm the kill switch.
        
        Args:
            armed: True to arm, False to disarm
            
        Returns:
            True if successful
        """
        with self.lock:
            if self.state["triggered"]:
                self.logger.warning("Cannot arm/disarm: kill switch is triggered")
                return False
            
            self.state["armed"] = armed
            self._save_state()
            
            self.logger.info(
                f"Kill switch {'ARMED' if armed else 'DISARMED'}",
                extra={"action": "arm", "armed": armed}
            )
            return True
    
    def check(self, current_balance: Optional[float] = None) -> bool:
        """
        Check if kill switch should trigger based on automatic conditions.
        Call this from your main trading loop.
        
        Args:
            current_balance: Current account balance (for circuit breaker checks)
            
        Returns:
            True if kill switch was triggered
        """
        with self.lock:
            # If already triggered, nothing to check
            if self.state["triggered"]:
                return True
            
            # If not armed, automatic conditions don't apply
            if not self.state["armed"]:
                return False
            
            # Check emergency file
            if self.emergency_file.exists():
                self.logger.warning(f"Emergency file detected: {self.emergency_file}")
                self.trigger(
                    reason=f"Emergency file {self.emergency_file.name} detected",
                    level=Level.FULL_SHUTDOWN,
                    triggered_by="file_system"
                )
                return True
            
            # Check balance-based conditions if balance provided
            if current_balance is not None:
                # Initialize session start balance
                if self.state["session_start_balance"] is None:
                    self.state["session_start_balance"] = current_balance
                    self._save_state()
                
                # Update peak balance
                if self.state["peak_balance"] is None or current_balance > self.state["peak_balance"]:
                    self.state["peak_balance"] = current_balance
                    self._save_state()
                
                # Check circuit breaker (% drop from peak)
                if self.state["peak_balance"] is not None:
                    pct_from_peak = ((current_balance - self.state["peak_balance"]) / 
                                    self.state["peak_balance"]) * 100
                    
                    if pct_from_peak <= self.config["circuit_breaker_pct"]:
                        self.logger.warning(
                            f"Circuit breaker triggered: {pct_from_peak:.2f}% from peak"
                        )
                        self.trigger(
                            reason=f"Circuit breaker: {pct_from_peak:.2f}% drop from peak ${self.state['peak_balance']:.2f}",
                            level=Level.CLOSE_ALL,
                            triggered_by="circuit_breaker"
                        )
                        return True
                
                # Check daily loss limit
                if self.state["session_start_balance"] is not None:
                    daily_pct = ((current_balance - self.state["session_start_balance"]) / 
                                self.state["session_start_balance"]) * 100
                    
                    if daily_pct <= self.config["daily_loss_limit_pct"]:
                        self.logger.warning(
                            f"Daily loss limit triggered: {daily_pct:.2f}%"
                        )
                        self.trigger(
                            reason=f"Daily loss limit: {daily_pct:.2f}% (${current_balance:.2f} from ${self.state['session_start_balance']:.2f})",
                            level=Level.CLOSE_ALL,
                            triggered_by="daily_loss_limit"
                        )
                        return True
            
            return False
    
    def trigger(self, reason: str, level: int = Level.FULL_SHUTDOWN, 
                triggered_by: str = "manual") -> bool:
        """
        TRIGGER THE KILL SWITCH
        
        This is the big red button. Once triggered, system enters cool-down.
        
        Args:
            reason: Human-readable reason for trigger
            level: Response level (1-4)
            triggered_by: Who/what triggered it (for audit)
            
        Returns:
            True if trigger successful, False if already triggered
        """
        with self.lock:
            if self.state["triggered"]:
                self.logger.warning(
                    f"Kill switch already triggered at level {self.state['trigger_level']}"
                )
                return False
            
            # Validate level
            try:
                level = Level(level)
            except ValueError:
                self.logger.error(f"Invalid level: {level}. Using FULL_SHUTDOWN.")
                level = Level.FULL_SHUTDOWN
            
            # Mark as triggered
            now = datetime.now().isoformat()
            cooldown_until = (datetime.now() + 
                            timedelta(hours=self.config["cooldown_hours"])).isoformat()
            
            self.state["triggered"] = True
            self.state["trigger_level"] = int(level)
            self.state["trigger_time"] = now
            self.state["trigger_reason"] = reason
            self.state["triggered_by"] = triggered_by
            self.state["cooldown_until"] = cooldown_until
            
            # Add to history
            history_entry = {
                "timestamp": now,
                "level": int(level),
                "reason": reason,
                "triggered_by": triggered_by,
                "cooldown_until": cooldown_until,
            }
            self.state["history"].append(history_entry)
            
            self._save_state()
            
            # LOG CRITICAL EVENT
            self.logger.critical(
                f"🚨 KILL SWITCH TRIGGERED 🚨",
                extra={
                    "action": "trigger",
                    "level": int(level),
                    "level_name": level.name,
                    "reason": reason,
                    "triggered_by": triggered_by,
                    "cooldown_until": cooldown_until,
                }
            )
            
            # Execute response
            self._execute_response(level)
            
            # Send alerts
            self._send_alerts(level, reason, triggered_by)
            
            return True
    
    def _execute_response(self, level: Level):
        """
        Execute kill switch response at specified level.
        
        This is where you integrate with your trading system.
        Override or extend this method for your specific needs.
        """
        actions_taken = []
        
        try:
            if level >= Level.STOP_NEW_TRADES:
                # Level 1: Stop new trades
                self.logger.info("Executing Level 1: Stop new trades")
                # TODO: Implement - stop signal generation, disable trade execution
                # Example:
                # trading_system.stop_new_trades()
                actions_taken.append("Stopped new trades")
            
            if level >= Level.CLOSE_WINNING:
                # Level 2: Close winning positions
                self.logger.info("Executing Level 2: Close winning positions")
                # TODO: Implement - close positions with positive P&L
                # Example:
                # winning_positions = trading_system.get_positions(filter="winning")
                # for pos in winning_positions:
                #     trading_system.close_position(pos.id)
                actions_taken.append("Closed winning positions")
            
            if level >= Level.CLOSE_ALL:
                # Level 3: Close ALL positions
                self.logger.info("Executing Level 3: Close ALL positions")
                # TODO: Implement - close all open positions immediately
                # Example:
                # all_positions = trading_system.get_positions()
                # for pos in all_positions:
                #     trading_system.close_position(pos.id, urgency="immediate")
                actions_taken.append("Closed ALL positions")
            
            if level >= Level.FULL_SHUTDOWN:
                # Level 4: Full system shutdown
                self.logger.info("Executing Level 4: Full system shutdown")
                # TODO: Implement - stop all processes, disconnect APIs
                # Example:
                # trading_system.stop_all_data_collection()
                # trading_system.disconnect()
                # sys.exit(0)  # If you want to actually exit
                actions_taken.append("Full system shutdown initiated")
            
            # Log all actions taken
            self.logger.info(
                f"Response executed: {', '.join(actions_taken)}",
                extra={"actions": actions_taken}
            )
            
        except Exception as e:
            self.logger.critical(
                f"CRITICAL ERROR during kill switch execution: {e}",
                extra={"error": str(e), "level": int(level)}
            )
            # Even if execution fails, keep the kill switch triggered
            # This is fail-safe behavior
    
    def _send_alerts(self, level: Level, reason: str, triggered_by: str):
        """
        Send emergency alerts via all available channels.
        """
        alert_message = (
            f"🚨 EMERGENCY KILL SWITCH ACTIVATED 🚨\n"
            f"Level: {level} ({level.name})\n"
            f"Reason: {reason}\n"
            f"Triggered by: {triggered_by}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Cooldown: {self.config['cooldown_hours']}h"
        )
        
        self.logger.critical(alert_message)
        
        # TODO: Implement alert channels
        # Example integrations:
        
        # Telegram
        # try:
        #     telegram_bot.send_message(chat_id=ADMIN_CHAT_ID, text=alert_message)
        # except Exception as e:
        #     self.logger.error(f"Failed to send Telegram alert: {e}")
        
        # Email
        # try:
        #     send_email(to=ADMIN_EMAIL, subject="TRADING KILL SWITCH", body=alert_message)
        # except Exception as e:
        #     self.logger.error(f"Failed to send email alert: {e}")
        
        # SMS
        # try:
        #     send_sms(to=ADMIN_PHONE, message=alert_message)
        # except Exception as e:
        #     self.logger.error(f"Failed to send SMS alert: {e}")
        
        # Write to emergency file as backup
        try:
            with open(self.emergency_file, 'w') as f:
                f.write(alert_message)
        except Exception as e:
            self.logger.error(f"Failed to write emergency file: {e}")
    
    def reset(self, authorized_by: str, force: bool = False) -> bool:
        """
        Reset kill switch after cool-down period.
        
        Args:
            authorized_by: Name/ID of person authorizing reset
            force: Skip cool-down check (use with extreme caution)
            
        Returns:
            True if reset successful
        """
        with self.lock:
            if not self.state["triggered"]:
                self.logger.info("Kill switch not triggered, nothing to reset")
                return True
            
            # Check cool-down period
            if not force:
                cooldown_until = datetime.fromisoformat(self.state["cooldown_until"])
                now = datetime.now()
                
                if now < cooldown_until:
                    remaining = cooldown_until - now
                    hours = remaining.total_seconds() / 3600
                    self.logger.warning(
                        f"Cannot reset: still in cool-down period ({hours:.1f}h remaining)"
                    )
                    return False
            
            # Reset state
            old_state = self.state.copy()
            
            self.state["triggered"] = False
            self.state["trigger_level"] = None
            self.state["trigger_time"] = None
            self.state["trigger_reason"] = None
            self.state["triggered_by"] = None
            self.state["cooldown_until"] = None
            self.state["armed"] = False  # Require explicit re-arming
            self.state["peak_balance"] = None
            self.state["session_start_balance"] = None
            
            self._save_state()
            
            # Clear emergency file if exists
            if self.emergency_file.exists():
                try:
                    self.emergency_file.unlink()
                except Exception as e:
                    self.logger.error(f"Failed to remove emergency file: {e}")
            
            self.logger.info(
                f"Kill switch RESET by {authorized_by}",
                extra={
                    "action": "reset",
                    "authorized_by": authorized_by,
                    "force": force,
                    "previous_trigger": {
                        "level": old_state.get("trigger_level"),
                        "reason": old_state.get("trigger_reason"),
                        "time": old_state.get("trigger_time"),
                    }
                }
            )
            
            return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current kill switch status.
        
        Returns:
            Dictionary with status information
        """
        with self.lock:
            status = {
                "armed": self.state["armed"],
                "triggered": self.state["triggered"],
            }
            
            if self.state["triggered"]:
                status.update({
                    "trigger_level": self.state["trigger_level"],
                    "trigger_level_name": Level(self.state["trigger_level"]).name,
                    "trigger_time": self.state["trigger_time"],
                    "trigger_reason": self.state["trigger_reason"],
                    "triggered_by": self.state["triggered_by"],
                    "cooldown_until": self.state["cooldown_until"],
                })
                
                # Calculate remaining cooldown
                cooldown_until = datetime.fromisoformat(self.state["cooldown_until"])
                remaining = cooldown_until - datetime.now()
                if remaining.total_seconds() > 0:
                    status["cooldown_remaining_hours"] = remaining.total_seconds() / 3600
                else:
                    status["cooldown_remaining_hours"] = 0
            
            status["emergency_file_exists"] = self.emergency_file.exists()
            status["config"] = self.config.copy()
            
            return status
    
    def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get kill switch activation history.
        
        Args:
            limit: Maximum number of entries to return (most recent first)
            
        Returns:
            List of historical activation records
        """
        with self.lock:
            history = self.state["history"].copy()
            history.reverse()  # Most recent first
            
            if limit:
                history = history[:limit]
            
            return history


# ============================================================================
# CLI Interface
# ============================================================================

def format_status(status: Dict[str, Any]) -> str:
    """Format status dict as human-readable string"""
    lines = []
    lines.append("=" * 60)
    lines.append("KILL SWITCH STATUS")
    lines.append("=" * 60)
    
    if status["triggered"]:
        lines.append("🚨 STATUS: TRIGGERED 🚨")
        lines.append(f"   Level: {status['trigger_level']} ({status['trigger_level_name']})")
        lines.append(f"   Time: {status['trigger_time']}")
        lines.append(f"   Reason: {status['trigger_reason']}")
        lines.append(f"   Triggered by: {status['triggered_by']}")
        lines.append(f"   Cooldown until: {status['cooldown_until']}")
        lines.append(f"   Cooldown remaining: {status['cooldown_remaining_hours']:.1f}h")
    elif status["armed"]:
        lines.append("⚡ STATUS: ARMED")
        lines.append("   System is monitoring conditions")
    else:
        lines.append("✓ STATUS: DISARMED")
        lines.append("   Automatic triggers disabled")
    
    lines.append("")
    lines.append(f"Emergency file exists: {status['emergency_file_exists']}")
    lines.append("")
    lines.append("Configuration:")
    lines.append(f"   Circuit breaker: {status['config']['circuit_breaker_pct']}% from peak")
    lines.append(f"   Daily loss limit: {status['config']['daily_loss_limit_pct']}%")
    lines.append(f"   Cooldown period: {status['config']['cooldown_hours']}h")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def format_history(history: List[Dict[str, Any]]) -> str:
    """Format history as human-readable string"""
    if not history:
        return "No activation history."
    
    lines = []
    lines.append("=" * 80)
    lines.append("KILL SWITCH ACTIVATION HISTORY")
    lines.append("=" * 80)
    
    for i, entry in enumerate(history, 1):
        lines.append(f"\n#{i}")
        lines.append(f"  Time: {entry['timestamp']}")
        lines.append(f"  Level: {entry['level']} ({Level(entry['level']).name})")
        lines.append(f"  Reason: {entry['reason']}")
        lines.append(f"  Triggered by: {entry['triggered_by']}")
        lines.append(f"  Cooldown until: {entry['cooldown_until']}")
    
    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Emergency Kill Switch for Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Show current status
  %(prog)s --arm                        Arm the kill switch
  %(prog)s --trigger "Manual stop"      Trigger kill switch
  %(prog)s --level 2 --trigger "Test"   Trigger at specific level
  %(prog)s --reset                      Reset after cooldown
  %(prog)s --history                    Show activation history
        """
    )
    
    parser.add_argument('--arm', action='store_true',
                       help='Arm the kill switch (enable automatic triggers)')
    parser.add_argument('--disarm', action='store_true',
                       help='Disarm the kill switch (disable automatic triggers)')
    parser.add_argument('--trigger', type=str, metavar='REASON',
                       help='Trigger kill switch with given reason')
    parser.add_argument('--level', type=int, choices=[1, 2, 3, 4], default=4,
                       help='Response level (1-4, default: 4)')
    parser.add_argument('--reset', action='store_true',
                       help='Reset kill switch after cooldown')
    parser.add_argument('--force-reset', action='store_true',
                       help='Force reset (skip cooldown check) - USE WITH CAUTION')
    parser.add_argument('--history', action='store_true',
                       help='Show activation history')
    parser.add_argument('--config', type=str,
                       help='Path to config JSON file')
    parser.add_argument('--workspace', type=str,
                       help='Workspace directory (default: current directory)')
    parser.add_argument('--authorized-by', type=str, default=os.getenv('USER', 'unknown'),
                       help='Name/ID of person performing action (for audit)')
    
    args = parser.parse_args()
    
    # Initialize kill switch
    ks = KillSwitch(config_path=args.config, workspace=args.workspace)
    
    # Execute command
    if args.arm:
        if ks.arm(True):
            print("✓ Kill switch ARMED")
            print(format_status(ks.get_status()))
        else:
            print("✗ Failed to arm kill switch")
            sys.exit(1)
    
    elif args.disarm:
        if ks.arm(False):
            print("✓ Kill switch DISARMED")
            print(format_status(ks.get_status()))
        else:
            print("✗ Failed to disarm kill switch")
            sys.exit(1)
    
    elif args.trigger:
        print(f"Triggering kill switch at level {args.level}...")
        if ks.trigger(reason=args.trigger, level=args.level, triggered_by=args.authorized_by):
            print("🚨 KILL SWITCH TRIGGERED 🚨")
            print(format_status(ks.get_status()))
        else:
            print("✗ Kill switch already triggered")
            sys.exit(1)
    
    elif args.reset or args.force_reset:
        if args.force_reset:
            confirm = input("⚠️  Force reset will skip cooldown. Are you sure? (yes/no): ")
            if confirm.lower() != 'yes':
                print("Reset cancelled.")
                sys.exit(0)
        
        if ks.reset(authorized_by=args.authorized_by, force=args.force_reset):
            print("✓ Kill switch RESET")
            print("   Note: Kill switch is now DISARMED. Use --arm to re-enable.")
            print(format_status(ks.get_status()))
        else:
            print("✗ Failed to reset kill switch (still in cooldown?)")
            status = ks.get_status()
            if status["triggered"]:
                print(f"   Cooldown remaining: {status['cooldown_remaining_hours']:.1f}h")
            sys.exit(1)
    
    elif args.history:
        history = ks.get_history()
        print(format_history(history))
    
    else:
        # Default: show status
        print(format_status(ks.get_status()))


if __name__ == "__main__":
    main()
