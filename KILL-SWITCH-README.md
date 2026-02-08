# Emergency Kill Switch for Polymarket Trading System

**🚨 SAFETY-CRITICAL SYSTEM 🚨**

This is your emergency brake. When things go wrong, this stops everything.

## Quick Start

### 1. Arm the kill switch
```bash
python kill-switch.py --arm
```

### 2. Integrate into your trading loop
```python
from kill_switch import KillSwitch

ks = KillSwitch()
ks.arm(True)

while trading:
    current_balance = get_balance()
    
    # Check kill switch (automatic condition monitoring)
    if ks.check(current_balance=current_balance):
        print("Kill switch triggered - stopping")
        break
    
    # ... your trading logic ...
```

### 3. Monitor status
```bash
python kill-switch.py  # Show current status
```

## Trigger Methods

### 1. Manual Trigger (CLI)
```bash
python kill-switch.py --trigger "Manual stop - market conditions unsafe"
python kill-switch.py --trigger "Test" --level 2  # Specific level
```

### 2. Manual Trigger (Code)
```python
ks.trigger(reason="Manual stop", level=4, triggered_by="wom")
```

### 3. Automatic Conditions
The kill switch monitors these conditions automatically (when armed):
- **Circuit breaker**: -15% drop from peak balance
- **Daily loss limit**: -5% from session start
- **Emergency file**: `touch EMERGENCY_STOP` in workspace

### 4. Telegram (integrate with your bot)
```
/killswitch status
/killswitch trigger Manual stop
/killswitch reset
```

### 5. API Endpoint (integrate with Flask/FastAPI)
```bash
curl -X POST http://localhost:5000/api/kill-switch/trigger \
  -H "Content-Type: application/json" \
  -d '{"reason": "API trigger", "level": 3}'
```

## Response Levels

| Level | Name | Action |
|-------|------|--------|
| 1 | STOP_NEW_TRADES | Stop generating new signals and executing new trades |
| 2 | CLOSE_WINNING | Close winning positions, stop new trades |
| 3 | CLOSE_ALL | Close ALL positions immediately |
| 4 | FULL_SHUTDOWN | Close everything and shut down entire system |

## Cool-down Period

After triggering, the system enters a **24-hour cool-down** (configurable).

During cool-down:
- ✅ You can view status and history
- ❌ You cannot re-arm or trade
- ⚠️  Reset only after cool-down expires

### Reset After Cool-down
```bash
python kill-switch.py --reset
```

### Force Reset (CAUTION!)
```bash
python kill-switch.py --force-reset
# Will ask for confirmation
```

## Configuration

Create `kill-switch-config.json`:
```json
{
  "circuit_breaker_pct": -15.0,
  "daily_loss_limit_pct": -5.0,
  "cooldown_hours": 24,
  "state_file": "kill-switch-state.json",
  "log_file": "kill-switch-audit.log",
  "emergency_file": "EMERGENCY_STOP"
}
```

Then use it:
```bash
python kill-switch.py --config kill-switch-config.json
```

## Files Created

| File | Purpose |
|------|---------|
| `kill-switch-state.json` | Current state (triggered, armed, history) |
| `kill-switch-audit.log` | Complete audit trail of all actions |
| `EMERGENCY_STOP` | Emergency trigger file (created on trigger) |

## CLI Commands

```bash
# Status
python kill-switch.py                    # Show current status
python kill-switch.py --history          # Show activation history

# Arm/Disarm
python kill-switch.py --arm              # Arm (enable automatic triggers)
python kill-switch.py --disarm           # Disarm (disable automatic triggers)

# Trigger
python kill-switch.py --trigger "reason"           # Trigger at level 4
python kill-switch.py --trigger "reason" --level 2 # Trigger at level 2

# Reset
python kill-switch.py --reset                      # Reset after cooldown
python kill-switch.py --force-reset                # Force reset (dangerous!)
```

## Integration Examples

See `kill-switch-integration-example.py` for complete examples:

1. **Basic integration**: Simple trading loop
2. **Advanced integration**: Full trading system with health monitoring
3. **Telegram bot**: Remote control via Telegram
4. **Flask API**: RESTful API endpoint
5. **File-based trigger**: Emergency stop via file
6. **Market anomaly detection**: Auto-trigger on market crashes
7. **Testing**: Test all levels

Run examples:
```bash
python kill-switch-integration-example.py basic
python kill-switch-integration-example.py advanced
python kill-switch-integration-example.py test
```

## Safety Features

✅ **Thread-safe**: Multiple processes can interact safely
✅ **Atomic state updates**: No corrupted state files
✅ **Comprehensive logging**: Every action is audited
✅ **Fail-safe design**: When in doubt, it triggers
✅ **Cool-down enforcement**: Prevents hasty restarts
✅ **Graduated response**: Choose appropriate level
✅ **Multiple triggers**: Manual, automatic, remote
✅ **Persistent state**: Survives restarts

## Customization

### Implement Trading System Integration

Edit the `_execute_response()` method in `kill-switch.py`:

```python
def _execute_response(self, level: Level):
    """Execute kill switch response"""
    if level >= Level.STOP_NEW_TRADES:
        # YOUR CODE: Stop signal generation
        trading_system.stop_signals()
        
    if level >= Level.CLOSE_WINNING:
        # YOUR CODE: Close winning positions
        for pos in trading_system.get_positions(filter="winning"):
            trading_system.close(pos.id)
    
    if level >= Level.CLOSE_ALL:
        # YOUR CODE: Close all positions
        for pos in trading_system.get_positions():
            trading_system.close(pos.id, urgency="immediate")
    
    if level >= Level.FULL_SHUTDOWN:
        # YOUR CODE: Full shutdown
        trading_system.stop_all()
        trading_system.disconnect()
```

### Implement Alert Channels

Edit the `_send_alerts()` method:

```python
def _send_alerts(self, level, reason, triggered_by):
    """Send emergency alerts"""
    message = f"🚨 KILL SWITCH: {reason}"
    
    # YOUR CODE: Send Telegram alert
    telegram_bot.send_message(ADMIN_CHAT_ID, message)
    
    # YOUR CODE: Send email
    send_email(to=ADMIN_EMAIL, subject="EMERGENCY", body=message)
    
    # YOUR CODE: Send SMS
    send_sms(to=ADMIN_PHONE, message=message)
```

## Testing

Before going live, **TEST EVERY LEVEL**:

```bash
python kill-switch-integration-example.py test
```

This will:
1. Trigger each level (1-4)
2. Verify state changes
3. Check history logging
4. Confirm reset works

## Best Practices

1. **Always arm** when trading: `ks.arm(True)`
2. **Check frequently**: Call `ks.check()` every loop iteration
3. **Use appropriate levels**: Don't use level 4 for everything
4. **Document triggers**: Give clear reasons when triggering manually
5. **Test regularly**: Run test suite weekly
6. **Monitor logs**: Review `kill-switch-audit.log` daily
7. **Respect cooldown**: Don't force reset without good reason
8. **Update peak balance**: Pass current balance to `check()`

## Troubleshooting

### Kill switch won't arm
- Check if already triggered
- Reset if in cooldown

### Kill switch won't reset
- Check cooldown period remaining
- Wait for cooldown to expire
- Use `--force-reset` only if absolutely necessary

### Automatic triggers not working
- Verify kill switch is armed
- Pass `current_balance` to `check()`
- Check configuration thresholds

### Lost state file
- State file: `kill-switch-state.json`
- If corrupted, delete and restart (will create fresh state)

## Emergency Procedures

### If system is out of control
```bash
# Option 1: CLI
python kill-switch.py --trigger "EMERGENCY" --level 4

# Option 2: File
touch EMERGENCY_STOP

# Option 3: Code
from kill_switch import KillSwitch
KillSwitch().trigger("EMERGENCY", level=4, triggered_by="human")
```

### If you need to override cooldown
```bash
python kill-switch.py --force-reset
# Type 'yes' when prompted
```

## Support

This is safety-critical code. If you find bugs:
1. Stop trading immediately
2. Document the issue
3. Fix before resuming

## License

Use at your own risk. This is a safety tool, not a guarantee.

---

**Remember**: This kill switch is your last line of defense. Test it. Trust it. Use it.

Great success! 🚀
