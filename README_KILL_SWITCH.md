# Kill Switch & Circuit Breaker System

A production-ready safety system for algorithmic trading platforms that can halt trading operations within 30 seconds of trigger activation.

## Quick Start

```bash
# 1. Install dependencies
pip install aiohttp pyyaml

# 2. Configure alerts in kill_switch_config.yaml
# Edit the file to add your Slack webhook, email settings, etc.

# 3. Run the example
python kill_switch_integration_example.py

# 4. Use the CLI
python kill_switch_cli.py status
python kill_switch_cli.py emergency --user your_name
```

## Files Overview

| File | Purpose |
|------|---------|
| `KILL_SWITCH_SYSTEM.md` | Complete documentation and architecture guide |
| `kill_switch_system.py` | Core implementation with async monitoring |
| `kill_switch_alerts.py` | Multi-channel alert system (Slack, Email, PagerDuty) |
| `kill_switch_cli.py` | Command-line interface for manual operations |
| `kill_switch_config.yaml` | Configuration file for thresholds and integrations |
| `kill_switch_integration_example.py` | Example integration with trading system |

## Features

### 1. Strategy-Level Kill Switches
- Per-strategy drawdown limits (default: 5%)
- Consecutive loss thresholds (default: 5 losses)
- Win rate monitoring (minimum 30%)
- Position size limits

### 2. Portfolio-Level Circuit Breakers
- Daily loss limits (default: 3%)
- Portfolio drawdown (default: 10%)
- Correlation spike detection (>0.8)
- Margin utilization monitoring (>90%)

### 3. Automated Triggers
- Real-time drawdown calculation
- Velocity checks (rapid P&L changes)
- Correlation spike detection
- Volatility monitoring
- Data feed health checks

### 4. Manual Override
- Emergency stop button functionality
- Strategy halt/resume commands
- Portfolio halt/close commands
- Dual authorization for critical actions

### 5. Recovery Protocols
- Graduated re-entry (paper → 25% → 50% → full)
- State validation before resuming
- Mandatory cool-down periods

### 6. Alerting & Audit
- Slack notifications
- Email alerts
- PagerDuty integration for critical events
- Complete audit trail for compliance

## Performance Targets

| Metric | Target | Maximum |
|--------|--------|---------|
| Trigger to Halt | < 1 sec | 5 sec |
| Position Closure | < 30 sec | 60 sec |
| Alert Delivery | < 5 sec | 10 sec |
| System Shutdown | < 30 sec | 60 sec |

## CLI Usage

```bash
# Show system status
python kill_switch_cli.py status

# Halt a specific strategy
python kill_switch_cli.py halt-strategy my_strategy --user trader1

# Resume a strategy
python kill_switch_cli.py resume my_strategy --user senior_trader

# Soft halt (stop new trades, keep positions)
python kill_switch_cli.py portfolio-halt --user risk_manager

# Hard halt (close all positions)
python kill_switch_cli.py portfolio-close --user risk_manager

# Emergency lockdown
python kill_switch_cli.py emergency --user admin

# Reset after resolution
python kill_switch_cli.py reset --user cto

# Continuous monitoring display
python kill_switch_cli.py monitor --interval 2
```

## Integration Example

```python
from kill_switch_system import get_kill_switch

# Get the kill switch instance
ks = get_kill_switch()

# Register callbacks
async def on_strategy_halt(strategy_id: str):
    print(f"Strategy {strategy_id} halted!")
    # Your code here: stop signal generation

ks.register_callback('strategy_halt', on_strategy_halt)

# Start monitoring
await ks.start_monitoring()

# Update metrics from your trading system
ks.update_strategy_metrics(
    strategy_id="my_strategy",
    max_drawdown=0.06,
    consecutive_losses=6
)

# Manual emergency stop if needed
await ks.emergency_stop(initiator="trader1")
```

## Configuration

Edit `kill_switch_config.yaml`:

```yaml
# Alert channels
alerts:
  slack_webhook: "https://hooks.slack.com/services/YOUR/WEBHOOK"
  
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    username: "alerts@yourfirm.com"
    password: "${EMAIL_PASSWORD}"  # Use env vars for secrets
    to_addresses: ["risk@yourfirm.com"]
  
  pagerduty_key: "${PAGERDUTY_KEY}"

# Trigger thresholds
triggers:
  strategy_drawdown: 0.05      # 5%
  portfolio_drawdown: 0.10     # 10%
  portfolio_daily_loss: 0.03   # 3%
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CIRCUIT BREAKER ENGINE                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  STRATEGY   │  │  PORTFOLIO  │  │   MANUAL OVERRIDE   │  │
│  │   LEVEL     │  │   LEVEL     │  │      CONTROLS       │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
│         │                │                    │             │
│         ▼                ▼                    ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              TRIGGER EVALUATION ENGINE               │   │
│  │  • Drawdown Monitor  • Correlation Spike Detector   │   │
│  │  • Loss Streak Tracker  • Volatility Monitor        │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              EMERGENCY STOP COORDINATOR              │   │
│  │  • Position Closer  • Order Canceller               │   │
│  │  • Risk Freezer     • System Lockdown               │   │
│  └────────────────────────┬────────────────────────────┘   │
│                           │                                  │
│              ┌────────────┴────────────┐                    │
│              ▼                         ▼                    │
│  ┌────────────────────┐   ┌────────────────────┐           │
│  │   ALERT SYSTEM     │   │   AUDIT LOGGER     │           │
│  │  • Slack/Email     │   │  • Event Trail     │           │
│  │  • PagerDuty       │   │  • Compliance Log  │           │
│  └────────────────────┘   └────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## Testing

```bash
# Run the integration example
python kill_switch_integration_example.py

# Test alerts
python kill_switch_cli.py test-alert --priority critical

# Simulate trigger (set metrics that exceed thresholds)
```

## Security Considerations

1. **Authentication**: CLI requires user identification for all actions
2. **Authorization**: Different actions require different permission levels
3. **Dual Authorization**: Critical actions require two-person approval
4. **Audit Trail**: Every action is logged with timestamp, user, and reason
5. **Cooldowns**: Alerts have cooldowns to prevent spam

## Monitoring

The system exposes status via:
- CLI status command
- JSON API (for integration with dashboards)
- Audit logs for compliance review

## License

MIT License - Use at your own risk. This is safety-critical software - thoroughly test before production use.

## Support

For issues or questions, refer to `KILL_SWITCH_SYSTEM.md` for complete documentation.

---

**⚠️ WARNING**: This is safety-critical software. Thoroughly test all scenarios before production deployment. Regularly review audit logs and conduct emergency drills.
