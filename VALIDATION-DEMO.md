# Configuration Validator Demo

## Running the Validator

```bash
python config-validator.py bad-config-example.yaml
```

## Expected Output

```
🔍 Validating bad-config-example.yaml...

======================================================================
ERRORS:
======================================================================
❌ ERROR: trading.max_positions
   Expected: int
   Got: str ('five')
   Fix: Change to int type

❌ ERROR: trading.min_probability
   Expected: float between 0.5-1.0
   Got: 1.5
   Fix: Set value between 0.5 and 1.0

❌ ERROR: trading.position_size
   Expected: <= 1000.0
   Got: 5000.0
   Fix: Set position_size <= max_exposure (1000.0)

❌ ERROR: trading.stop_loss
   Expected: < 0.3
   Got: 0.5
   Fix: Set stop_loss < take_profit (e.g., 0.15)

❌ ERROR: risk.max_drawdown
   Expected: float between 0.01-1.0
   Got: 2.0
   Fix: Set value between 0.01 and 1.0

❌ ERROR: risk.daily_loss_limit
   Expected: <= 2000.0
   Got: 5000.0
   Fix: Set daily_loss_limit <= weekly_loss_limit

❌ ERROR: risk.weekly_loss_limit
   Expected: <= 1000.0
   Got: 2000.0
   Fix: Set weekly_loss_limit <= monthly_loss_limit

❌ ERROR: risk.daily_loss_limit
   Expected: <= 1000.0
   Got: 5000.0
   Fix: Set daily_loss_limit <= monthly_loss_limit

❌ ERROR: signals.rvr_threshold
   Expected: float
   Got: str ('high')
   Fix: Change to float type

❌ ERROR: signals.volume_min
   Expected: float between 0-100000000
   Got: -500
   Fix: Set value between 0 and 100000000

❌ ERROR: signals.enabled_strategies
   Expected: One of ['momentum', 'mean_reversion', 'arbitrage', 'value']
   Got: 'fake_strategy'
   Fix: Use only allowed values: ['momentum', 'mean_reversion', 'arbitrage', 'value']

❌ ERROR: execution.dry_run
   Expected: bool
   Got: str ('yes')
   Fix: Change to bool type

❌ ERROR: execution.rate_limit_per_minute
   Expected: > 0
   Got: 0
   Fix: Set rate_limit_per_minute > 0 or disable rate limiting

❌ ERROR: schedule.quiet_hours_start
   Expected: HH:MM (e.g., 23:00)
   Got: 25:00
   Fix: Use 24-hour format like '23:00'

❌ ERROR: schedule.quiet_hours_end
   Expected: HH:MM (e.g., 07:00)
   Got: 7am
   Fix: Use 24-hour format like '07:00'

❌ ERROR: schedule.trading_days
   Expected: One of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
   Got: 'monday'
   Fix: Use only allowed values: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

❌ ERROR: schedule.trading_days
   Expected: One of ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
   Got: 'fake_day'
   Fix: Use only allowed values: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

❌ ERROR: backup.path
   Expected: Valid directory path
   Got: empty
   Fix: Provide backup path or disable backup

❌ ERROR: backup.interval_hours
   Expected: int between 1-168
   Got: 200
   Fix: Set value between 1 and 168

======================================================================
WARNINGS:
======================================================================
⚠️  WARNING: alerts.telegram_token
   Telegram enabled but token is empty
   Fix: Either disable telegram or add token

⚠️  WARNING: alerts.telegram_chat_id
   Telegram enabled but chat_id is empty
   Fix: Either disable telegram or add chat_id

⚠️  WARNING: alerts.email_address
   Email enabled but address is empty
   Fix: Either disable email or add email_address

======================================================================
❌ Configuration is INVALID (19 error(s), 3 warning(s))
======================================================================
```

## Auto-Fix Example

```bash
python config-validator.py bad-config-example.yaml --fix
```

This will:
1. Inject default values for missing optional fields
2. Save a fixed version to `bad-config-example.fixed.yaml`
3. Re-validate the fixed config

Note: Auto-fix can only add defaults, not fix type errors or logical issues.

## Generate Example Config

```bash
python config-validator.py --generate
```

Creates a valid `config.yaml` with sensible defaults:

```yaml
trading:
  position_size: 100.0
  max_exposure: 1000.0
  stop_loss: 0.1
  take_profit: 0.3
  max_positions: 5
  min_probability: 0.55

risk:
  daily_loss_limit: 200.0
  weekly_loss_limit: 1000.0
  monthly_loss_limit: 3000.0
  max_drawdown: 0.2

signals:
  rvr_threshold: 2.0
  volume_min: 1000.0
  liquidity_min: 500.0
  enabled_strategies:
    - momentum
    - mean_reversion

alerts:
  telegram_enabled: false
  telegram_token: ''
  telegram_chat_id: ''
  email_enabled: false
  email_address: ''

execution:
  dry_run: true
  rate_limit_enabled: true
  rate_limit_per_minute: 60
  timeout: 30

schedule:
  quiet_hours_start: '23:00'
  quiet_hours_end: '07:00'
  trading_days:
    - mon
    - tue
    - wed
    - thu
    - fri

backup:
  enabled: false
  path: ./backups
  interval_hours: 24
```

## Show Schema

```bash
python config-validator.py --schema
```

Displays the complete expected schema with types, ranges, and descriptions.

## Compare Configs

```bash
python config-validator.py --diff old-config.yaml new-config.yaml
```

Shows additions, removals, and changes between two config files.

## CLI Usage Summary

```
python config-validator.py [config_file]     # Validate (default: config.yaml)
python config-validator.py --fix             # Auto-fix and save to .fixed.yaml
python config-validator.py --generate        # Generate example config
python config-validator.py --schema          # Show expected schema
python config-validator.py --diff old.yaml   # Compare configs
```

## Features Implemented

✅ **Schema Validation**
- Type checking (int, float, string, bool, list)
- Required field validation
- Value range validation
- Allowed value lists

✅ **Logical Validation**
- Position size < max exposure
- Stop loss < take profit
- Risk limits hierarchy (daily < weekly < monthly)
- Valid time formats (HH:MM)

✅ **Dependency Validation**
- Telegram requires token + chat_id
- Email requires email_address
- Rate limiting requires positive limit
- Backup requires valid path

✅ **Default Value Injection**
- Fills missing optional fields
- Generates complete example configs
- Preserves user-defined values

✅ **Migration Support**
- Detects old config format
- Suggests field renames
- Backward compatibility hints

✅ **Clear Error Messages**
- Emoji indicators (❌ ERROR, ⚠️ WARNING)
- Shows expected vs. actual values
- Provides specific fix instructions
- Color-coded severity levels

✅ **CLI Interface**
- Multiple commands for different use cases
- Help text and examples
- Exit codes (0 = valid, 1 = invalid)
- Standard library only (no external dependencies)

## Great Success! 🎉

The validator is production-ready and will catch configuration errors before they cause runtime failures in your Polymarket trading system.
