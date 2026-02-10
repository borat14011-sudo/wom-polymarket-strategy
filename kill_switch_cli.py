#!/usr/bin/env python3
"""
Kill Switch System CLI
Command-line interface for manual kill switch operations.
"""

import asyncio
import argparse
import json
import sys
from datetime import datetime
from typing import Optional

from kill_switch_system import (
    KillSwitchSystem,
    get_kill_switch,
    KillSwitchLevel,
    StrategyState
)


class Colors:
    """Terminal colors for output."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_status(status: dict):
    """Print formatted status output."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}KILL SWITCH SYSTEM STATUS{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    # System state
    state = status.get('system_state', 'UNKNOWN')
    state_color = Colors.GREEN if state == 'NONE' else Colors.RED if state in ['EMERGENCY', 'PORTFOLIO_HARD'] else Colors.YELLOW
    print(f"System State: {state_color}{Colors.BOLD}{state}{Colors.END}")
    
    # Portfolio metrics
    print(f"\n{Colors.BOLD}Portfolio Metrics:{Colors.END}")
    metrics = status.get('portfolio_metrics', {})
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")
    
    # Strategy states
    print(f"\n{Colors.BOLD}Strategy States:{Colors.END}")
    strategies = status.get('strategy_states', {})
    if strategies:
        for sid, state in strategies.items():
            color = Colors.GREEN if state == 'active' else Colors.RED if state in ['inactive', 'closing'] else Colors.YELLOW
            print(f"  {sid}: {color}{state}{Colors.END}")
    else:
        print("  No strategies registered")
    
    # Performance
    avg_trigger = status.get('avg_trigger_time', 0)
    print(f"\n{Colors.BOLD}Performance:{Colors.END}")
    print(f"  Avg Trigger Response: {avg_trigger*1000:.1f}ms")
    print(f"  Uptime: {status.get('uptime', 0):.0f}s")
    
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}\n")


async def cmd_status(args):
    """Show system status."""
    ks = get_kill_switch(args.config)
    status = ks.get_status()
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print_status(status)


async def cmd_halt_strategy(args):
    """Halt a specific strategy."""
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.YELLOW}Halting strategy: {args.strategy_id}{Colors.END}")
    
    if not args.force:
        confirm = input(f"Confirm halt of {args.strategy_id}? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    await ks.halt_strategy(
        strategy_id=args.strategy_id,
        initiator=args.user,
        reason=args.reason
    )
    
    print(f"{Colors.GREEN}Strategy {args.strategy_id} halted successfully.{Colors.END}")


async def cmd_resume_strategy(args):
    """Resume a halted strategy."""
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.YELLOW}Resuming strategy: {args.strategy_id}{Colors.END}")
    
    if not args.force:
        confirm = input(f"Confirm resume of {args.strategy_id}? [y/N]: ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return
    
    await ks.resume_strategy(
        strategy_id=args.strategy_id,
        initiator=args.user
    )
    
    print(f"{Colors.GREEN}Strategy {args.strategy_id} resumed successfully.{Colors.END}")


async def cmd_portfolio_halt(args):
    """Soft halt entire portfolio."""
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.RED}{Colors.BOLD}PORTFOLIO SOFT HALT{Colors.END}")
    print("This will stop all new trades but keep existing positions open.")
    
    if not args.force:
        confirm = input("Confirm portfolio halt? [yes/no]: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    
    await ks._trigger(
        KillSwitchLevel.PORTFOLIO_SOFT,
        "manual_trigger",
        None,
        0.0, 0.0,
        args.user
    )
    
    print(f"{Colors.GREEN}Portfolio soft halt activated.{Colors.END}")


async def cmd_portfolio_close(args):
    """Hard halt and close all positions."""
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.RED}{Colors.BOLD}⚠️  PORTFOLIO HARD HALT  ⚠️{Colors.END}")
    print(f"{Colors.RED}This will IMMEDIATELY CLOSE ALL POSITIONS!{Colors.END}")
    
    if not args.force:
        confirm = input("Type 'CLOSE ALL' to confirm: ")
        if confirm != 'CLOSE ALL':
            print("Cancelled.")
            return
    
    await ks._trigger(
        KillSwitchLevel.PORTFOLIO_HARD,
        "manual_trigger",
        None,
        0.0, 0.0,
        args.user
    )
    
    print(f"{Colors.GREEN}Portfolio hard halt activated. Closing positions...{Colors.END}")


async def cmd_emergency(args):
    """Emergency lockdown - immediate full system shutdown."""
    ks = get_kill_switch(args.config)
    
    print(f"\n{Colors.RED}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}🚨  EMERGENCY LOCKDOWN  🚨{Colors.END}")
    print(f"{Colors.RED}{Colors.BOLD}{'='*60}{Colors.END}\n")
    print(f"{Colors.RED}This will:")
    print("  1. Cancel ALL pending orders")
    print("  2. Close ALL positions immediately")
    print("  3. Disconnect from ALL exchanges")
    print("  4. Alert on-call engineers")
    print(f"  5. SHUTDOWN THE ENTIRE SYSTEM{Colors.END}\n")
    
    if not args.force:
        confirm = input("Type 'EMERGENCY STOP' to execute: ")
        if confirm != 'EMERGENCY STOP':
            print("Cancelled.")
            return
    
    print(f"\n{Colors.RED}Executing emergency stop...{Colors.END}\n")
    
    start_time = asyncio.get_event_loop().time()
    
    await ks.emergency_stop(
        initiator=args.user,
        reason=args.reason
    )
    
    elapsed = asyncio.get_event_loop().time() - start_time
    print(f"\n{Colors.GREEN}Emergency lockdown completed in {elapsed:.2f} seconds.{Colors.END}")
    print(f"{Colors.RED}System is now LOCKED. Manual reset required.{Colors.END}\n")


async def cmd_reset(args):
    """Reset system after halt."""
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.YELLOW}System Reset{Colors.END}")
    print("This will reset the kill switch system to normal operation.")
    
    if not args.force:
        auth = input("Enter authorization code: ")
        confirm = input("Confirm system reset? [yes/no]: ")
        if confirm.lower() != 'yes':
            print("Cancelled.")
            return
    else:
        auth = "DUAL_AUTH"
    
    await ks.reset_system(
        initiator=args.user,
        authorization=auth
    )
    
    print(f"{Colors.GREEN}System reset successful.{Colors.END}")


async def cmd_monitor(args):
    """Start continuous monitoring display."""
    ks = get_kill_switch(args.config)
    await ks.start_monitoring()
    
    print(f"{Colors.CYAN}Starting continuous monitoring (Ctrl+C to exit)...{Colors.END}\n")
    
    try:
        while True:
            # Clear screen (works on Unix/Windows)
            print("\033[2J\033[H", end='')
            
            status = ks.get_status()
            print_status(status)
            
            await asyncio.sleep(args.interval)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped.{Colors.END}")
        await ks.stop_monitoring()


async def cmd_test_alert(args):
    """Test alert delivery."""
    from kill_switch_system import TriggerEvent, AlertManager
    
    ks = get_kill_switch(args.config)
    
    print(f"{Colors.CYAN}Sending test alert...{Colors.END}")
    
    test_event = TriggerEvent(
        timestamp=datetime.now(),
        level=KillSwitchLevel.STRATEGY_HALT,
        source="test",
        reason="test_alert",
        threshold=0.05,
        actual_value=0.06,
        strategy_id="TEST_STRATEGY",
        initiator=args.user,
        metadata={"test": True}
    )
    
    await ks.alert_manager.send_alert(test_event, priority=args.priority)
    
    print(f"{Colors.GREEN}Test alert sent.{Colors.END}")


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description="Kill Switch System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show system status
  %(prog)s status
  
  # Halt a strategy
  %(prog)s halt-strategy my_strategy --user trader1
  
  # Emergency stop (requires confirmation)
  %(prog)s emergency --user trader1
  
  # Resume a strategy
  %(prog)s resume my_strategy --user senior_trader
  
  # Force emergency stop (no confirmation)
  %(prog)s emergency --force --user admin
        """
    )
    
    parser.add_argument(
        '--config', '-c',
        default='kill_switch_config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--user', '-u',
        default='cli_user',
        help='User ID for audit trail'
    )
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    status_parser.set_defaults(func=cmd_status)
    
    # Halt strategy command
    halt_parser = subparsers.add_parser('halt-strategy', help='Halt a specific strategy')
    halt_parser.add_argument('strategy_id', help='Strategy ID to halt')
    halt_parser.add_argument('--reason', default='manual_halt', help='Reason for halt')
    halt_parser.set_defaults(func=cmd_halt_strategy)
    
    # Resume strategy command
    resume_parser = subparsers.add_parser('resume', help='Resume a halted strategy')
    resume_parser.add_argument('strategy_id', help='Strategy ID to resume')
    resume_parser.set_defaults(func=cmd_resume_strategy)
    
    # Portfolio halt command
    portfolio_halt_parser = subparsers.add_parser('portfolio-halt', help='Soft halt entire portfolio')
    portfolio_halt_parser.set_defaults(func=cmd_portfolio_halt)
    
    # Portfolio close command
    portfolio_close_parser = subparsers.add_parser('portfolio-close', help='Hard halt and close all positions')
    portfolio_close_parser.set_defaults(func=cmd_portfolio_close)
    
    # Emergency command
    emergency_parser = subparsers.add_parser('emergency', help='Emergency lockdown')
    emergency_parser.add_argument('--reason', default='manual_emergency', help='Reason for emergency')
    emergency_parser.set_defaults(func=cmd_emergency)
    
    # Reset command
    reset_parser = subparsers.add_parser('reset', help='Reset system after halt')
    reset_parser.set_defaults(func=cmd_reset)
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--interval', type=int, default=2, help='Update interval in seconds')
    monitor_parser.set_defaults(func=cmd_monitor)
    
    # Test alert command
    test_parser = subparsers.add_parser('test-alert', help='Test alert delivery')
    test_parser.add_argument('--priority', default='high', choices=['low', 'high', 'critical'])
    test_parser.set_defaults(func=cmd_test_alert)
    
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        await args.func(args)
        return 0
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted.{Colors.END}")
        return 130
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        return 1


if __name__ == '__main__':
    exit(asyncio.run(main()))
