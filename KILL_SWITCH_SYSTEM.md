# Kill Switch & Circuit Breaker System

## Overview

A multi-layered safety system designed to halt trading operations within 30 seconds of trigger activation. Protects against catastrophic losses through automated monitoring, manual overrides, and rapid shutdown protocols.

---

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

---

## 1. Strategy-Level Kill Switches

### Purpose
Individual strategy protection that isolates problematic strategies without affecting the entire portfolio.

### Triggers

| Trigger | Threshold | Action | Cooldown |
|---------|-----------|--------|----------|
| Max Drawdown | 5% per strategy | Stop new trades, close positions | 30 min |
| Consecutive Losses | 5 losing trades | Stop new trades | 15 min |
| Win Rate Drop | <30% over 20 trades | Stop new trades | 60 min |
| Sharpe Ratio Drop | <0.5 over 10 days | Stop new trades | 24 hours |
| Position Limit Breach | >max position size | Close excess, stop new | Until manual reset |
| Signal Error Rate | >10% failed signals | Stop new trades | Until fixed |

### Actions (in order)

1. **Stop New Trades** (immediate)
   - Reject all new entry signals
   - Existing positions remain open
   - Exit signals still processed

2. **Close Positions** (configurable delay)
   - Market orders for all open positions
   - Maximum 10 seconds per position
   - Prioritize by position size (largest first)

3. **Strategy Deactivation**
   - Remove from active strategy pool
   - Preserve state for analysis
   - Require manual reactivation

### State Management

```python
StrategyState = {
    "ACTIVE": "Normal operation",
    "HALTED": "No new trades, exits allowed",
    "CLOSING": "Actively closing positions",
    "INACTIVE": "Fully stopped, manual reset required",
    "RECOVERY": "Monitoring before reactivation"
}
```

---

## 2. Portfolio-Level Circuit Breakers

### Purpose
System-wide protection that halts ALL trading across all strategies.

### Triggers

| Trigger | Threshold | Response Time |
|---------|-----------|---------------|
| Daily Loss Limit | 3% of NAV | <5 seconds |
| Portfolio Drawdown | 10% from high water mark | <5 seconds |
| Correlation Spike | Avg correlation >0.8 | <10 seconds |
| VaR Breach | 95% VaR exceeded | <5 seconds |
| Margin Utilization | >90% | <3 seconds |
| System Error Rate | >5% order failures | <10 seconds |
| Data Feed Failure | >30 seconds stale | <5 seconds |
| API Latency Spike | >500ms p95 | <15 seconds |

### Circuit Breaker Levels

```
┌─────────────────────────────────────────────────────────┐
│  LEVEL 1: SOFT HALT  (< 5 seconds)                      │
│  • Cancel all pending orders                            │
│  • Stop accepting new signals                           │
│  • Existing positions remain                            │
│  • Manual reset required                                │
├─────────────────────────────────────────────────────────┤
│  LEVEL 2: HARD HALT  (< 15 seconds)                     │
│  • Cancel all orders                                    │
│  • Send market orders to close all positions            │
│  • Freeze all strategy activity                         │
│  • Require manual investigation                         │
├─────────────────────────────────────────────────────────┤
│  LEVEL 3: EMERGENCY LOCKDOWN  (< 30 seconds)            │
│  • Aggressive position closure                          │
│  • Disconnect from exchanges                            │
│  • Preserve all state/logs                              │
│  • Alert on-call engineer                               │
└─────────────────────────────────────────────────────────┘
```

### Auto-Recovery Protection

Circuit breakers NEVER auto-recover to prevent oscillation:
- All levels require manual intervention
- Recovery requires dual authorization
- Audit trail mandatory for all resets

---

## 3. Automated Triggers

### 3.1 Drawdown Monitor

```python
# Real-time drawdown calculation
def calculate_drawdown(equity_curve):
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak
    return drawdown

# Triggers
- Strategy: 5% drawdown → Halt
- Portfolio: 10% drawdown → Hard Halt
- Catastrophic: 15% drawdown → Emergency Lockdown
```

### 3.2 Consecutive Loss Tracker

```python
# Rolling window analysis
- 5 consecutive losses → Strategy halt
- 3 consecutive portfolio down days → Soft halt
- 10+ trades without profit → Review flag
```

### 3.3 Correlation Spike Detector

```python
# Real-time correlation monitoring
- Calculate pairwise correlations every 60 seconds
- Alert if average correlation > 0.7
- Halt if average correlation > 0.8 (concentration risk)
- Factor exposure correlation > 0.9 → Immediate halt
```

### 3.4 Volatility Monitor

```python
# VIX-style volatility tracking
- Portfolio vol > 2x target → Reduce position sizes 50%
- Portfolio vol > 3x target → Soft halt
- Single asset vol spike > 5x → Isolate strategy
```

### 3.5 Liquidity Monitor

```python
# Market impact estimation
- Bid-ask spread > 2x normal → Reduce size
- Order book depth < threshold → Halt new entries
- Market closed/disconnected → Immediate halt
```

### 3.6 Velocity Checks

```python
# Rate of change monitoring
- P&L drop > 1% in 60 seconds → Alert
- P&L drop > 2% in 60 seconds → Soft halt
- P&L drop > 3% in 60 seconds → Hard halt
```

---

## 4. Manual Override Procedures

### Emergency Stop Button

**Physical/Digital**: Big red button accessible to authorized personnel

```python
# Immediate effect - no confirmation required
emergency_stop(
    initiator="user_id",
    reason="manual_trigger",
    level="EMERGENCY"
)
```

### Authorization Levels

| Action | Required Authorization | Timeout |
|--------|----------------------|---------|
| Strategy Halt | Trader | None |
| Strategy Resume | Senior Trader + Risk Manager | 15 min |
| Portfolio Soft Halt | Senior Trader | None |
| Portfolio Hard Halt | Risk Manager | None |
| Emergency Lockdown | Any authorized + confirmation | 5 min |
| System Restart | CTO + Risk Manager + 24h wait | N/A |

### Manual Commands

```bash
# CLI commands
kill-switch strategy <id> halt      # Halt specific strategy
kill-switch strategy <id> resume    # Resume strategy
kill-switch portfolio halt          # Soft halt all
kill-switch portfolio close         # Hard halt + close all
kill-switch emergency               # Emergency lockdown
kill-switch status                  # Show system status
kill-switch reset                   # Reset after resolution
```

### Override Procedures

1. **Strategy Override**
   ```
   1. Verify strategy issue resolved
   2. Check market conditions suitable
   3. Obtain secondary approval
   4. Execute: kill-switch strategy <id> resume
   5. Monitor for 30 minutes
   ```

2. **Portfolio Override**
   ```
   1. Incident review completed
   2. Root cause identified
   3. Fix implemented and tested
   4. Dual authorization obtained
   5. Market conditions assessed
   6. Gradual reactivation (10% size first)
   ```

---

## 5. Recovery and Restart Protocols

### Post-Halt Assessment

```python
RECOVERY_CHECKLIST = {
    "market_conditions": "Favorable volatility regime",
    "system_health": "All services operational",
    "data_quality": "No stale or erroneous data",
    "strategy_validation": "Backtests pass current market",
    "risk_metrics": "Within acceptable bounds",
    "authorization": "Required approvals obtained"
}
```

### Graduated Recovery

```
Phase 1: Paper Trading (1-4 hours)
   └─ Validate strategies in real-time without risk

Phase 2: Reduced Size (25% of normal, 1-2 days)
   └─ Limit exposure while monitoring behavior

Phase 3: Partial Size (50% of normal, 2-3 days)
   └─ Increase exposure if metrics stable

Phase 4: Full Operation
   └─ Resume normal trading parameters
```

### Restart Sequence

```python
async def restart_sequence():
    # 1. Pre-flight checks
    await verify_exchange_connectivity()
    await verify_data_feeds()
    await verify_risk_systems()
    
    # 2. Load state
    positions = await load_position_state()
    strategies = await load_strategy_configs()
    
    # 3. Validate
    await validate_position_consistency(positions)
    await validate_strategy_configs(strategies)
    
    # 4. Gradual activation
    await activate_risk_monitors()
    await activate_strategy("strategy_1", size_pct=0.25)
    await wait_and_validate(3600)  # 1 hour
    await activate_strategy("strategy_2", size_pct=0.25)
    
    # 5. Full activation
    await scale_to_full_size()
    await confirm_operational_status()
```

---

## Implementation Files

- `kill_switch_system.py` - Core implementation
- `kill_switch_cli.py` - Command line interface
- `kill_switch_config.yaml` - Configuration
- `kill_switch_alerts.py` - Alert integrations

---

## Performance Requirements

| Metric | Target | Maximum |
|--------|--------|---------|
| Trigger to Halt | < 1 second | 5 seconds |
| Position Closure | < 30 seconds | 60 seconds |
| Alert Delivery | < 5 seconds | 10 seconds |
| Audit Log Write | < 100ms | 500ms |
| System Shutdown | < 30 seconds | 60 seconds |

---

## Testing

### Monthly Drills
- Simulate each trigger type
- Verify closure times
- Test alert delivery
- Validate audit trails

### Quarterly Reviews
- Analyze trigger frequency
- Tune thresholds
- Review recovery times
- Update procedures

---

## Integration Points

- **Order Management**: Cancel/reject orders
- **Position Manager**: Close positions
- **Risk Engine**: Freeze calculations
- **Data Feeds**: Monitor staleness
- **Exchange APIs**: Connection management
- **Monitoring**: Metrics and dashboards
- **Alerting**: Slack, Email, PagerDuty
- **Audit**: Compliance logging

---

## Contact & Escalation

| Level | Role | Response Time |
|-------|------|---------------|
| 1 | On-call Trader | 5 minutes |
| 2 | Risk Manager | 15 minutes |
| 3 | CTO/Head of Trading | 30 minutes |

---

**Last Updated**: 2026-02-08  
**Version**: 1.0  
**Owner**: Risk Management Team
