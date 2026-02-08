#!/usr/bin/env python3
"""
Kill Switch Integration Example
Demonstrates how to integrate the kill switch into your Polymarket trading system.
"""

import time
from kill_switch import KillSwitch, Level


# ============================================================================
# Example 1: Basic Integration in Main Trading Loop
# ============================================================================

def trading_loop_basic():
    """
    Basic integration: Check kill switch on every iteration.
    """
    # Initialize kill switch
    ks = KillSwitch(workspace=".")
    
    # Arm it (enable automatic condition monitoring)
    ks.arm(True)
    
    print("Starting trading loop with kill switch protection...")
    
    while True:
        try:
            # Get current account balance (from your trading system)
            current_balance = get_account_balance()  # Your function
            
            # CHECK KILL SWITCH (automatic condition monitoring)
            if ks.check(current_balance=current_balance):
                print("🚨 Kill switch triggered! Stopping trading loop.")
                break
            
            # Your normal trading logic
            analyze_markets()
            generate_signals()
            execute_trades()
            
            time.sleep(60)  # Check every minute
            
        except KeyboardInterrupt:
            print("Manual stop requested")
            ks.trigger(reason="Keyboard interrupt", level=Level.CLOSE_ALL, triggered_by="user")
            break
        except Exception as e:
            print(f"Error in trading loop: {e}")
            # On critical error, trigger kill switch
            ks.trigger(reason=f"Critical error: {e}", level=Level.FULL_SHUTDOWN, triggered_by="exception_handler")
            break


# ============================================================================
# Example 2: Advanced Integration with Health Monitoring
# ============================================================================

class TradingSystem:
    """
    Advanced integration: Kill switch as part of system health monitoring.
    """
    
    def __init__(self):
        self.ks = KillSwitch(workspace=".")
        self.positions = []
        self.balance = 1000.0
        self.health_status = "healthy"
    
    def start(self):
        """Start the trading system"""
        # Arm kill switch
        self.ks.arm(True)
        
        print("Trading system started with kill switch armed")
        
        # Main loop
        while True:
            try:
                # Update system state
                self.update_balance()
                self.update_positions()
                
                # Monitor system health
                self.check_system_health()
                
                # Check kill switch (with current balance)
                if self.ks.check(current_balance=self.balance):
                    print("Kill switch triggered - initiating shutdown")
                    self.emergency_shutdown()
                    break
                
                # Normal operations
                self.analyze_and_trade()
                
                time.sleep(30)
                
            except KeyboardInterrupt:
                self.graceful_shutdown()
                break
            except Exception as e:
                self.handle_error(e)
                break
    
    def check_system_health(self):
        """
        Monitor system health and trigger kill switch if critical issues detected.
        """
        issues = []
        
        # Check API connectivity
        if not self.check_api_health():
            issues.append("API connectivity lost")
        
        # Check data freshness
        if not self.check_data_freshness():
            issues.append("Stale data detected")
        
        # Check position count (too many positions = risk)
        if len(self.positions) > 50:
            issues.append(f"Too many positions: {len(self.positions)}")
        
        # Check for margin issues
        if self.get_margin_ratio() < 0.2:
            issues.append("Low margin ratio")
        
        if issues:
            self.health_status = "critical"
            reason = "System health critical: " + ", ".join(issues)
            print(f"⚠️  {reason}")
            
            # Trigger kill switch
            self.ks.trigger(
                reason=reason,
                level=Level.CLOSE_ALL,
                triggered_by="health_monitor"
            )
        else:
            self.health_status = "healthy"
    
    def handle_error(self, error: Exception):
        """Handle critical errors by triggering kill switch"""
        print(f"Critical error: {error}")
        
        # Determine severity
        if self.is_critical_error(error):
            level = Level.FULL_SHUTDOWN
        else:
            level = Level.STOP_NEW_TRADES
        
        self.ks.trigger(
            reason=f"Exception: {type(error).__name__}: {str(error)}",
            level=level,
            triggered_by="exception_handler"
        )
        
        self.emergency_shutdown()
    
    def emergency_shutdown(self):
        """Execute emergency shutdown procedures"""
        print("Executing emergency shutdown...")
        
        # Stop all data collection
        self.stop_data_feeds()
        
        # Stop signal generation
        self.stop_signal_generation()
        
        # Close positions (if not already done by kill switch)
        self.close_all_positions()
        
        # Disconnect from APIs
        self.disconnect()
        
        print("Emergency shutdown complete")
    
    def graceful_shutdown(self):
        """Graceful shutdown (user-initiated)"""
        print("Graceful shutdown initiated...")
        
        # Trigger kill switch at lower level
        self.ks.trigger(
            reason="User-initiated graceful shutdown",
            level=Level.STOP_NEW_TRADES,
            triggered_by="user"
        )
        
        # Give time for current trades to complete
        time.sleep(5)
        
        # Then close everything
        self.close_all_positions()
        self.disconnect()
        
        print("Graceful shutdown complete")
    
    # Stub methods (replace with your actual implementation)
    def update_balance(self):
        pass
    
    def update_positions(self):
        pass
    
    def analyze_and_trade(self):
        pass
    
    def check_api_health(self):
        return True
    
    def check_data_freshness(self):
        return True
    
    def get_margin_ratio(self):
        return 0.5
    
    def is_critical_error(self, error):
        return True
    
    def stop_data_feeds(self):
        pass
    
    def stop_signal_generation(self):
        pass
    
    def close_all_positions(self):
        pass
    
    def disconnect(self):
        pass


# ============================================================================
# Example 3: Telegram Integration
# ============================================================================

def telegram_kill_switch_handler(bot, update):
    """
    Telegram bot command handler for /killswitch
    
    Usage:
    /killswitch status              - Show status
    /killswitch trigger "reason"    - Trigger kill switch
    /killswitch reset               - Reset after cooldown
    """
    ks = KillSwitch(workspace=".")
    
    # Parse command
    args = update.message.text.split()[1:]  # Skip /killswitch
    
    if not args or args[0] == "status":
        # Show status
        status = ks.get_status()
        
        if status["triggered"]:
            msg = (
                f"🚨 KILL SWITCH TRIGGERED 🚨\n"
                f"Level: {status['trigger_level_name']}\n"
                f"Reason: {status['trigger_reason']}\n"
                f"Time: {status['trigger_time']}\n"
                f"Cooldown: {status['cooldown_remaining_hours']:.1f}h remaining"
            )
        elif status["armed"]:
            msg = "⚡ Kill switch ARMED\nMonitoring conditions..."
        else:
            msg = "✓ Kill switch DISARMED"
        
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    
    elif args[0] == "trigger":
        # Trigger kill switch
        reason = " ".join(args[1:]) if len(args) > 1 else "Telegram command"
        username = update.message.from_user.username or "telegram_user"
        
        if ks.trigger(reason=reason, level=Level.FULL_SHUTDOWN, triggered_by=f"telegram:{username}"):
            bot.send_message(
                chat_id=update.message.chat_id,
                text="🚨 KILL SWITCH ACTIVATED 🚨\nTrading system stopped."
            )
        else:
            bot.send_message(
                chat_id=update.message.chat_id,
                text="Kill switch already triggered."
            )
    
    elif args[0] == "reset":
        # Reset kill switch
        username = update.message.from_user.username or "telegram_user"
        
        if ks.reset(authorized_by=f"telegram:{username}"):
            bot.send_message(
                chat_id=update.message.chat_id,
                text="✓ Kill switch reset.\nNote: System is now DISARMED. Restart trading system to re-arm."
            )
        else:
            status = ks.get_status()
            remaining = status.get("cooldown_remaining_hours", 0)
            bot.send_message(
                chat_id=update.message.chat_id,
                text=f"Cannot reset: still in cooldown ({remaining:.1f}h remaining)"
            )


# ============================================================================
# Example 4: API Endpoint Integration (Flask)
# ============================================================================

def create_flask_api():
    """
    Flask API with kill switch endpoint.
    """
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    ks = KillSwitch(workspace=".")
    
    @app.route('/api/kill-switch/status', methods=['GET'])
    def get_status():
        """GET /api/kill-switch/status - Get current status"""
        return jsonify(ks.get_status())
    
    @app.route('/api/kill-switch/trigger', methods=['POST'])
    def trigger():
        """
        POST /api/kill-switch/trigger
        Body: {"reason": "...", "level": 1-4, "triggered_by": "..."}
        """
        data = request.json
        reason = data.get('reason', 'API trigger')
        level = data.get('level', 4)
        triggered_by = data.get('triggered_by', request.remote_addr)
        
        success = ks.trigger(reason=reason, level=level, triggered_by=triggered_by)
        
        return jsonify({
            'success': success,
            'status': ks.get_status()
        })
    
    @app.route('/api/kill-switch/reset', methods=['POST'])
    def reset():
        """
        POST /api/kill-switch/reset
        Body: {"authorized_by": "...", "force": false}
        """
        data = request.json
        authorized_by = data.get('authorized_by', request.remote_addr)
        force = data.get('force', False)
        
        success = ks.reset(authorized_by=authorized_by, force=force)
        
        return jsonify({
            'success': success,
            'status': ks.get_status()
        })
    
    @app.route('/api/kill-switch/history', methods=['GET'])
    def history():
        """GET /api/kill-switch/history - Get activation history"""
        limit = request.args.get('limit', type=int, default=10)
        return jsonify(ks.get_history(limit=limit))
    
    return app


# ============================================================================
# Example 5: File-Based Emergency Stop
# ============================================================================

def file_based_trigger_example():
    """
    Monitor for emergency stop file.
    
    To trigger externally: touch EMERGENCY_STOP
    """
    ks = KillSwitch(workspace=".")
    ks.arm(True)
    
    print("Monitoring for EMERGENCY_STOP file...")
    print(f"To trigger: touch {ks.emergency_file}")
    
    while True:
        # check() will automatically detect the file
        if ks.check():
            print("Emergency stop file detected - system stopped")
            break
        
        # Your trading logic here
        time.sleep(10)


# ============================================================================
# Example 6: Market Anomaly Detection
# ============================================================================

def market_anomaly_detector():
    """
    Detect market anomalies and trigger kill switch.
    """
    ks = KillSwitch(workspace=".")
    ks.arm(True)
    
    while True:
        # Get market data
        prices = get_market_prices()  # Your function
        
        # Detect anomalies
        if detect_flash_crash(prices):
            ks.trigger(
                reason="Flash crash detected",
                level=Level.CLOSE_ALL,
                triggered_by="anomaly_detector"
            )
            break
        
        if detect_unusual_volatility(prices):
            ks.trigger(
                reason="Unusual volatility detected",
                level=Level.STOP_NEW_TRADES,
                triggered_by="anomaly_detector"
            )
            break
        
        if detect_liquidity_crisis(prices):
            ks.trigger(
                reason="Liquidity crisis detected",
                level=Level.FULL_SHUTDOWN,
                triggered_by="anomaly_detector"
            )
            break
        
        time.sleep(5)


# ============================================================================
# Example 7: Testing Kill Switch Levels
# ============================================================================

def test_kill_switch_levels():
    """
    Test script to verify all kill switch levels work correctly.
    """
    ks = KillSwitch(workspace=".")
    
    # Test Level 1: Stop new trades
    print("\n=== Testing Level 1: Stop New Trades ===")
    ks.trigger(reason="Test Level 1", level=Level.STOP_NEW_TRADES, triggered_by="test_script")
    print("Status:", ks.get_status())
    
    # Reset
    ks.reset(authorized_by="test_script", force=True)
    
    # Test Level 2: Close winning positions
    print("\n=== Testing Level 2: Close Winning Positions ===")
    ks.trigger(reason="Test Level 2", level=Level.CLOSE_WINNING, triggered_by="test_script")
    print("Status:", ks.get_status())
    
    # Reset
    ks.reset(authorized_by="test_script", force=True)
    
    # Test Level 3: Close all positions
    print("\n=== Testing Level 3: Close All Positions ===")
    ks.trigger(reason="Test Level 3", level=Level.CLOSE_ALL, triggered_by="test_script")
    print("Status:", ks.get_status())
    
    # Reset
    ks.reset(authorized_by="test_script", force=True)
    
    # Test Level 4: Full shutdown
    print("\n=== Testing Level 4: Full Shutdown ===")
    ks.trigger(reason="Test Level 4", level=Level.FULL_SHUTDOWN, triggered_by="test_script")
    print("Status:", ks.get_status())
    
    # Check history
    print("\n=== History ===")
    for entry in ks.get_history():
        print(f"- {entry['timestamp']}: Level {entry['level']} - {entry['reason']}")


# ============================================================================
# Stub functions (replace with your actual implementations)
# ============================================================================

def get_account_balance():
    """Get current account balance from Polymarket"""
    return 1000.0  # Placeholder

def analyze_markets():
    """Analyze market data"""
    pass

def generate_signals():
    """Generate trading signals"""
    pass

def execute_trades():
    """Execute trades"""
    pass

def get_market_prices():
    """Get current market prices"""
    return {}

def detect_flash_crash(prices):
    """Detect flash crash"""
    return False

def detect_unusual_volatility(prices):
    """Detect unusual volatility"""
    return False

def detect_liquidity_crisis(prices):
    """Detect liquidity crisis"""
    return False


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "basic":
            trading_loop_basic()
        elif example == "advanced":
            system = TradingSystem()
            system.start()
        elif example == "file":
            file_based_trigger_example()
        elif example == "test":
            test_kill_switch_levels()
        else:
            print(f"Unknown example: {example}")
            print("Available: basic, advanced, file, test")
    else:
        print("Kill Switch Integration Examples")
        print("=" * 60)
        print("Run with: python kill-switch-integration-example.py <example>")
        print("")
        print("Available examples:")
        print("  basic     - Basic integration in trading loop")
        print("  advanced  - Advanced integration with health monitoring")
        print("  file      - File-based emergency trigger")
        print("  test      - Test all kill switch levels")
        print("")
        print("See code for more examples:")
        print("  - Telegram integration")
        print("  - Flask API integration")
        print("  - Market anomaly detection")
