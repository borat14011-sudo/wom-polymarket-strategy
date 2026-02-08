#!/usr/bin/env python3
"""
Configuration Validator for Polymarket Trading System
Validates config.yaml against schema, logical rules, and dependencies.
"""

import yaml
import sys
import os
import argparse
from datetime import datetime
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path


# ============================================================================
# SCHEMA DEFINITION
# ============================================================================

SCHEMA = {
    "trading": {
        "type": dict,
        "required": True,
        "fields": {
            "position_size": {
                "type": float,
                "required": True,
                "range": (0.01, 1000000),
                "description": "Position size in USD"
            },
            "max_exposure": {
                "type": float,
                "required": True,
                "range": (0.01, 10000000),
                "description": "Maximum total exposure in USD"
            },
            "stop_loss": {
                "type": float,
                "required": False,
                "default": 0.1,
                "range": (0.01, 1.0),
                "description": "Stop loss threshold (0-1)"
            },
            "take_profit": {
                "type": float,
                "required": False,
                "default": 0.3,
                "range": (0.01, 10.0),
                "description": "Take profit threshold (0-10)"
            },
            "max_positions": {
                "type": int,
                "required": False,
                "default": 5,
                "range": (1, 100),
                "description": "Maximum concurrent positions"
            },
            "min_probability": {
                "type": float,
                "required": False,
                "default": 0.55,
                "range": (0.5, 1.0),
                "description": "Minimum probability to trade (0.5-1)"
            },
        }
    },
    "risk": {
        "type": dict,
        "required": True,
        "fields": {
            "daily_loss_limit": {
                "type": float,
                "required": True,
                "range": (0, 1000000),
                "description": "Daily loss limit in USD"
            },
            "weekly_loss_limit": {
                "type": float,
                "required": False,
                "default": None,
                "range": (0, 10000000),
                "description": "Weekly loss limit in USD"
            },
            "monthly_loss_limit": {
                "type": float,
                "required": False,
                "default": None,
                "range": (0, 100000000),
                "description": "Monthly loss limit in USD"
            },
            "max_drawdown": {
                "type": float,
                "required": False,
                "default": 0.2,
                "range": (0.01, 1.0),
                "description": "Maximum drawdown tolerance (0-1)"
            },
        }
    },
    "signals": {
        "type": dict,
        "required": True,
        "fields": {
            "rvr_threshold": {
                "type": float,
                "required": True,
                "range": (0, 10.0),
                "description": "Risk/Value Ratio threshold"
            },
            "volume_min": {
                "type": float,
                "required": False,
                "default": 1000,
                "range": (0, 100000000),
                "description": "Minimum market volume in USD"
            },
            "liquidity_min": {
                "type": float,
                "required": False,
                "default": 500,
                "range": (0, 10000000),
                "description": "Minimum liquidity in USD"
            },
            "enabled_strategies": {
                "type": list,
                "required": False,
                "default": ["momentum", "mean_reversion"],
                "allowed_values": ["momentum", "mean_reversion", "arbitrage", "value"],
                "description": "List of enabled trading strategies"
            },
        }
    },
    "alerts": {
        "type": dict,
        "required": False,
        "default": {},
        "fields": {
            "telegram_enabled": {
                "type": bool,
                "required": False,
                "default": False,
                "description": "Enable Telegram notifications"
            },
            "telegram_token": {
                "type": str,
                "required": False,
                "default": "",
                "description": "Telegram bot token"
            },
            "telegram_chat_id": {
                "type": str,
                "required": False,
                "default": "",
                "description": "Telegram chat ID"
            },
            "email_enabled": {
                "type": bool,
                "required": False,
                "default": False,
                "description": "Enable email notifications"
            },
            "email_address": {
                "type": str,
                "required": False,
                "default": "",
                "description": "Email address for alerts"
            },
        }
    },
    "execution": {
        "type": dict,
        "required": False,
        "default": {},
        "fields": {
            "dry_run": {
                "type": bool,
                "required": False,
                "default": True,
                "description": "Run in simulation mode"
            },
            "rate_limit_enabled": {
                "type": bool,
                "required": False,
                "default": True,
                "description": "Enable API rate limiting"
            },
            "rate_limit_per_minute": {
                "type": int,
                "required": False,
                "default": 60,
                "range": (1, 1000),
                "description": "API calls per minute"
            },
            "timeout": {
                "type": int,
                "required": False,
                "default": 30,
                "range": (5, 300),
                "description": "Request timeout in seconds"
            },
        }
    },
    "schedule": {
        "type": dict,
        "required": False,
        "default": {},
        "fields": {
            "quiet_hours_start": {
                "type": str,
                "required": False,
                "default": "23:00",
                "description": "Quiet hours start time (HH:MM)"
            },
            "quiet_hours_end": {
                "type": str,
                "required": False,
                "default": "07:00",
                "description": "Quiet hours end time (HH:MM)"
            },
            "trading_days": {
                "type": list,
                "required": False,
                "default": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                "allowed_values": ["mon", "tue", "wed", "thu", "fri", "sat", "sun"],
                "description": "Days to trade"
            },
        }
    },
    "backup": {
        "type": dict,
        "required": False,
        "default": {},
        "fields": {
            "enabled": {
                "type": bool,
                "required": False,
                "default": False,
                "description": "Enable backup"
            },
            "path": {
                "type": str,
                "required": False,
                "default": "./backups",
                "description": "Backup directory path"
            },
            "interval_hours": {
                "type": int,
                "required": False,
                "default": 24,
                "range": (1, 168),
                "description": "Backup interval in hours"
            },
        }
    },
}


# ============================================================================
# VALIDATION CLASSES
# ============================================================================

class ValidationError:
    def __init__(self, path: str, message: str, expected: str, got: str, fix: str):
        self.path = path
        self.message = message
        self.expected = expected
        self.got = got
        self.fix = fix
        self.severity = "ERROR"

    def __str__(self):
        return f"❌ ERROR: {self.path}\n   Expected: {self.expected}\n   Got: {self.got}\n   Fix: {self.fix}"


class ValidationWarning:
    def __init__(self, path: str, message: str, fix: str):
        self.path = path
        self.message = message
        self.fix = fix
        self.severity = "WARNING"

    def __str__(self):
        return f"⚠️  WARNING: {self.path}\n   {self.message}\n   Fix: {self.fix}"


class ConfigValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []
        self.fixed_config = None

    def validate(self) -> Tuple[bool, List, List]:
        """Run all validations and return (is_valid, errors, warnings)"""
        self._validate_schema()
        self._validate_logical_rules()
        self._validate_dependencies()
        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_schema(self):
        """Validate config against schema"""
        self._validate_section(self.config, SCHEMA, "")

    def _validate_section(self, config: Dict, schema: Dict, path: str):
        """Recursively validate a config section"""
        for key, spec in schema.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if required field is missing
            if spec.get("required", False) and key not in config:
                self.errors.append(ValidationError(
                    current_path,
                    "Required field missing",
                    f"{spec['type'].__name__}",
                    "missing",
                    f"Add '{key}' field to config"
                ))
                continue
            
            # Skip if optional and not present
            if key not in config:
                continue
            
            value = config[key]
            expected_type = spec["type"]
            
            # Type validation
            if not isinstance(value, expected_type):
                self.errors.append(ValidationError(
                    current_path,
                    "Type mismatch",
                    f"{expected_type.__name__}",
                    f"{type(value).__name__} ({repr(value)})",
                    f"Change to {expected_type.__name__} type"
                ))
                continue
            
            # For dict types, validate nested fields
            if expected_type == dict and "fields" in spec:
                self._validate_section(value, spec["fields"], current_path)
            
            # For list types, validate allowed values
            elif expected_type == list and "allowed_values" in spec:
                allowed = spec["allowed_values"]
                for item in value:
                    if item not in allowed:
                        self.errors.append(ValidationError(
                            current_path,
                            "Invalid list value",
                            f"One of {allowed}",
                            f"{repr(item)}",
                            f"Use only allowed values: {allowed}"
                        ))
            
            # Range validation for numbers
            elif expected_type in (int, float) and "range" in spec:
                min_val, max_val = spec["range"]
                if not (min_val <= value <= max_val):
                    self.errors.append(ValidationError(
                        current_path,
                        "Value out of range",
                        f"{expected_type.__name__} between {min_val}-{max_val}",
                        f"{value}",
                        f"Set value between {min_val} and {max_val}"
                    ))

    def _validate_logical_rules(self):
        """Validate business logic rules"""
        # Position size < max exposure
        if "trading" in self.config:
            trading = self.config["trading"]
            if "position_size" in trading and "max_exposure" in trading:
                if trading["position_size"] > trading["max_exposure"]:
                    self.errors.append(ValidationError(
                        "trading.position_size",
                        "Position size exceeds max exposure",
                        f"<= {trading['max_exposure']}",
                        f"{trading['position_size']}",
                        f"Set position_size <= max_exposure ({trading['max_exposure']})"
                    ))
            
            # Stop loss < take profit
            if "stop_loss" in trading and "take_profit" in trading:
                if trading["stop_loss"] >= trading["take_profit"]:
                    self.errors.append(ValidationError(
                        "trading.stop_loss",
                        "Stop loss should be less than take profit",
                        f"< {trading['take_profit']}",
                        f"{trading['stop_loss']}",
                        f"Set stop_loss < take_profit (e.g., {trading['take_profit'] * 0.5:.2f})"
                    ))
        
        # Risk limits: daily < weekly < monthly
        if "risk" in self.config:
            risk = self.config["risk"]
            daily = risk.get("daily_loss_limit")
            weekly = risk.get("weekly_loss_limit")
            monthly = risk.get("monthly_loss_limit")
            
            if daily and weekly and daily > weekly:
                self.errors.append(ValidationError(
                    "risk.daily_loss_limit",
                    "Daily limit exceeds weekly limit",
                    f"<= {weekly}",
                    f"{daily}",
                    f"Set daily_loss_limit <= weekly_loss_limit"
                ))
            
            if weekly and monthly and weekly > monthly:
                self.errors.append(ValidationError(
                    "risk.weekly_loss_limit",
                    "Weekly limit exceeds monthly limit",
                    f"<= {monthly}",
                    f"{weekly}",
                    f"Set weekly_loss_limit <= monthly_loss_limit"
                ))
            
            if daily and monthly and daily > monthly:
                self.errors.append(ValidationError(
                    "risk.daily_loss_limit",
                    "Daily limit exceeds monthly limit",
                    f"<= {monthly}",
                    f"{daily}",
                    f"Set daily_loss_limit <= monthly_loss_limit"
                ))
        
        # Quiet hours validation
        if "schedule" in self.config:
            schedule = self.config["schedule"]
            if "quiet_hours_start" in schedule:
                if not self._is_valid_time(schedule["quiet_hours_start"]):
                    self.errors.append(ValidationError(
                        "schedule.quiet_hours_start",
                        "Invalid time format",
                        "HH:MM (e.g., 23:00)",
                        f"{schedule['quiet_hours_start']}",
                        "Use 24-hour format like '23:00'"
                    ))
            
            if "quiet_hours_end" in schedule:
                if not self._is_valid_time(schedule["quiet_hours_end"]):
                    self.errors.append(ValidationError(
                        "schedule.quiet_hours_end",
                        "Invalid time format",
                        "HH:MM (e.g., 07:00)",
                        f"{schedule['quiet_hours_end']}",
                        "Use 24-hour format like '07:00'"
                    ))

    def _validate_dependencies(self):
        """Validate conditional dependencies"""
        # Telegram dependencies
        if "alerts" in self.config:
            alerts = self.config["alerts"]
            if alerts.get("telegram_enabled", False):
                if not alerts.get("telegram_token"):
                    self.warnings.append(ValidationWarning(
                        "alerts.telegram_token",
                        "Telegram enabled but token is empty",
                        "Either disable telegram or add token"
                    ))
                if not alerts.get("telegram_chat_id"):
                    self.warnings.append(ValidationWarning(
                        "alerts.telegram_chat_id",
                        "Telegram enabled but chat_id is empty",
                        "Either disable telegram or add chat_id"
                    ))
            
            # Email dependencies
            if alerts.get("email_enabled", False):
                if not alerts.get("email_address"):
                    self.warnings.append(ValidationWarning(
                        "alerts.email_address",
                        "Email enabled but address is empty",
                        "Either disable email or add email_address"
                    ))
        
        # Rate limiting dependencies
        if "execution" in self.config:
            execution = self.config["execution"]
            if execution.get("rate_limit_enabled", False):
                rate_limit = execution.get("rate_limit_per_minute", 0)
                if rate_limit <= 0:
                    self.errors.append(ValidationError(
                        "execution.rate_limit_per_minute",
                        "Rate limiting enabled but limit is 0 or negative",
                        "> 0",
                        f"{rate_limit}",
                        "Set rate_limit_per_minute > 0 or disable rate limiting"
                    ))
        
        # Backup dependencies
        if "backup" in self.config:
            backup = self.config["backup"]
            if backup.get("enabled", False):
                path = backup.get("path", "")
                if not path:
                    self.errors.append(ValidationError(
                        "backup.path",
                        "Backup enabled but path is empty",
                        "Valid directory path",
                        "empty",
                        "Provide backup path or disable backup"
                    ))
                elif not self._is_path_writable(path):
                    self.warnings.append(ValidationWarning(
                        "backup.path",
                        f"Backup path '{path}' may not be writable",
                        "Ensure directory exists and is writable, or create it"
                    ))

    @staticmethod
    def _is_valid_time(time_str: str) -> bool:
        """Check if time string is in HH:MM format"""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except:
            return False

    @staticmethod
    def _is_path_writable(path: str) -> bool:
        """Check if path exists and is writable, or can be created"""
        try:
            p = Path(path)
            if p.exists():
                return os.access(path, os.W_OK)
            else:
                # Try to create parent directory
                parent = p.parent
                return parent.exists() and os.access(parent, os.W_OK)
        except:
            return False

    def inject_defaults(self) -> Dict[str, Any]:
        """Create config with default values injected"""
        fixed = self.config.copy()
        self._inject_section_defaults(fixed, SCHEMA)
        self.fixed_config = fixed
        return fixed

    def _inject_section_defaults(self, config: Dict, schema: Dict):
        """Recursively inject default values"""
        for key, spec in schema.items():
            if key not in config:
                if "default" in spec and spec["default"] is not None:
                    config[key] = spec["default"]
                elif spec["type"] == dict and not spec.get("required", False):
                    config[key] = spec.get("default", {})
            
            if key in config and spec["type"] == dict and "fields" in spec:
                self._inject_section_defaults(config[key], spec["fields"])


# ============================================================================
# UTILITIES
# ============================================================================

def load_config(path: str) -> Optional[Dict[str, Any]]:
    """Load YAML config file"""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {path}")
        return None
    except yaml.YAMLError as e:
        print(f"❌ YAML parsing error: {e}")
        return None


def save_config(config: Dict[str, Any], path: str):
    """Save config to YAML file"""
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def generate_example_config() -> Dict[str, Any]:
    """Generate example configuration"""
    return {
        "trading": {
            "position_size": 100.0,
            "max_exposure": 1000.0,
            "stop_loss": 0.1,
            "take_profit": 0.3,
            "max_positions": 5,
            "min_probability": 0.55,
        },
        "risk": {
            "daily_loss_limit": 200.0,
            "weekly_loss_limit": 1000.0,
            "monthly_loss_limit": 3000.0,
            "max_drawdown": 0.2,
        },
        "signals": {
            "rvr_threshold": 2.0,
            "volume_min": 1000.0,
            "liquidity_min": 500.0,
            "enabled_strategies": ["momentum", "mean_reversion"],
        },
        "alerts": {
            "telegram_enabled": False,
            "telegram_token": "",
            "telegram_chat_id": "",
            "email_enabled": False,
            "email_address": "",
        },
        "execution": {
            "dry_run": True,
            "rate_limit_enabled": True,
            "rate_limit_per_minute": 60,
            "timeout": 30,
        },
        "schedule": {
            "quiet_hours_start": "23:00",
            "quiet_hours_end": "07:00",
            "trading_days": ["mon", "tue", "wed", "thu", "fri"],
        },
        "backup": {
            "enabled": False,
            "path": "./backups",
            "interval_hours": 24,
        },
    }


def print_schema():
    """Print expected schema"""
    print("📋 Expected Configuration Schema\n")
    print("=" * 70)
    _print_schema_section(SCHEMA, "")
    print("=" * 70)


def _print_schema_section(schema: Dict, indent: str):
    """Recursively print schema"""
    for key, spec in schema.items():
        required = "REQUIRED" if spec.get("required", False) else "optional"
        type_name = spec["type"].__name__
        desc = spec.get("description", "")
        
        print(f"{indent}{key}: ({type_name}, {required})")
        if desc:
            print(f"{indent}  → {desc}")
        
        if "range" in spec:
            print(f"{indent}  Range: {spec['range'][0]} - {spec['range'][1]}")
        
        if "default" in spec and spec["default"] is not None:
            print(f"{indent}  Default: {spec['default']}")
        
        if "allowed_values" in spec:
            print(f"{indent}  Allowed: {spec['allowed_values']}")
        
        if spec["type"] == dict and "fields" in spec:
            _print_schema_section(spec["fields"], indent + "  ")
        
        print()


def compare_configs(old_path: str, new_path: str):
    """Compare two config files"""
    old = load_config(old_path)
    new = load_config(new_path)
    
    if old is None or new is None:
        return
    
    print(f"📊 Comparing {old_path} → {new_path}\n")
    print("=" * 70)
    _compare_section(old, new, "")
    print("=" * 70)


def _compare_section(old: Dict, new: Dict, path: str):
    """Recursively compare config sections"""
    all_keys = set(old.keys()) | set(new.keys())
    
    for key in sorted(all_keys):
        current_path = f"{path}.{key}" if path else key
        
        if key not in old:
            print(f"➕ ADDED: {current_path} = {new[key]}")
        elif key not in new:
            print(f"➖ REMOVED: {current_path} (was {old[key]})")
        elif old[key] != new[key]:
            if isinstance(old[key], dict) and isinstance(new[key], dict):
                _compare_section(old[key], new[key], current_path)
            else:
                print(f"🔄 CHANGED: {current_path}")
                print(f"   Old: {old[key]}")
                print(f"   New: {new[key]}")


def detect_old_format(config: Dict) -> List[str]:
    """Detect old config format and suggest migrations"""
    suggestions = []
    
    # Check for common old field names
    old_field_mappings = {
        "position": "trading.position_size",
        "max_pos": "trading.max_positions",
        "stop": "trading.stop_loss",
        "profit": "trading.take_profit",
        "telegram": "alerts.telegram_enabled",
        "bot_token": "alerts.telegram_token",
    }
    
    for old_field, new_field in old_field_mappings.items():
        if old_field in config:
            suggestions.append(f"Rename '{old_field}' → '{new_field}'")
    
    # Check for flat structure (old format)
    if "position_size" in config and "trading" not in config:
        suggestions.append("Migrate flat structure to nested sections (trading, risk, signals, etc.)")
    
    return suggestions


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Configuration Validator for Polymarket Trading System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python config-validator.py                    # Validate config.yaml
  python config-validator.py --fix             # Auto-fix issues
  python config-validator.py --generate        # Generate example config
  python config-validator.py --schema          # Show expected schema
  python config-validator.py --diff old.yaml   # Compare configs
        """
    )
    
    parser.add_argument(
        "config_file",
        nargs="?",
        default="config.yaml",
        help="Config file to validate (default: config.yaml)"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible and save to config.fixed.yaml"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate example config.yaml"
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Show expected schema"
    )
    parser.add_argument(
        "--diff",
        metavar="OLD_CONFIG",
        help="Compare with another config file"
    )
    
    args = parser.parse_args()
    
    # Show schema
    if args.schema:
        print_schema()
        return 0
    
    # Generate example config
    if args.generate:
        example = generate_example_config()
        output_path = args.config_file
        save_config(example, output_path)
        print(f"✅ Generated example config: {output_path}")
        print("\nValidating generated config...")
        validator = ConfigValidator(example)
        is_valid, errors, warnings = validator.validate()
        if is_valid:
            print("✅ Generated config is valid!")
        return 0
    
    # Compare configs
    if args.diff:
        compare_configs(args.diff, args.config_file)
        return 0
    
    # Load and validate config
    config = load_config(args.config_file)
    if config is None:
        return 1
    
    # Check for old format
    migration_suggestions = detect_old_format(config)
    if migration_suggestions:
        print("🔄 Old config format detected!\n")
        print("Migration suggestions:")
        for suggestion in migration_suggestions:
            print(f"  • {suggestion}")
        print()
    
    # Validate
    print(f"🔍 Validating {args.config_file}...\n")
    validator = ConfigValidator(config)
    is_valid, errors, warnings = validator.validate()
    
    # Print errors
    if errors:
        print("=" * 70)
        print("ERRORS:")
        print("=" * 70)
        for error in errors:
            print(error)
            print()
    
    # Print warnings
    if warnings:
        print("=" * 70)
        print("WARNINGS:")
        print("=" * 70)
        for warning in warnings:
            print(warning)
            print()
    
    # Summary
    print("=" * 70)
    if is_valid and not warnings:
        print("✅ Configuration is valid!")
    elif is_valid and warnings:
        print(f"✅ Configuration is valid (with {len(warnings)} warning(s))")
    else:
        print(f"❌ Configuration is INVALID ({len(errors)} error(s), {len(warnings)} warning(s))")
    print("=" * 70)
    
    # Auto-fix
    if args.fix:
        print("\n🔧 Attempting auto-fix...")
        fixed = validator.inject_defaults()
        output_path = args.config_file.replace(".yaml", ".fixed.yaml")
        save_config(fixed, output_path)
        print(f"✅ Saved fixed config to: {output_path}")
        print("\nRe-validating fixed config...")
        validator2 = ConfigValidator(fixed)
        is_valid2, errors2, warnings2 = validator2.validate()
        if is_valid2:
            print("✅ Fixed config is valid!")
        else:
            print(f"⚠️  Fixed config still has {len(errors2)} error(s)")
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
