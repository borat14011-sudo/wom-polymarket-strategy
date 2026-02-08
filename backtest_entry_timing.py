#!/usr/bin/env python3
"""
Entry Timing Backtest
Tests WHEN to enter after signals align for optimal results

Hypothesis:
1. Signal quality degrades over time → immediate entry may beat waiting
2. Pullback entries get better prices → patience may be rewarded
3. Timing matters → market hours vs overnight affects outcomes

Strategies Tested:
1. IMMEDIATE - Enter as soon as signal fires
2. CONFIRMATION_HOLD - Wait for signal to hold 2+ hours  
3. PULLBACK_2PCT - Enter on first 2-5% pullback after initial spike
4. MARKET_HOURS_ONLY - Only enter during market hours (9am-4pm ET)
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from enum import Enum

# Simulate historical signal patterns based on existing backtest data
random.seed(42)  # Reproducible results

class EntryStrategy(Enum):
    IMMEDIATE = "IMMEDIATE"
    CONFIRMATION_HOLD = "CONFIRMATION_HOLD"
    PULLBACK = "PULLBACK"
    MARKET_HOURS = "MARKET_HOURS"

@dataclass
class SignalEvent:
    """A trading signal that fired"""
    market_id: str
    signal_time: datetime
    initial_price: float
    rvr: float
    roc: float
    hype_score: float
    category: str
    days_to_resolution: int
    
    # Simulated market behavior after signal
    signal_sustained_hours: int  # How long signal stays strong
    pullback_occurs: bool
    pullback_time_hours: float
    pullback_depth_pct: float
    
    # Actual outcome (simulated based on historical patterns)
    final_outcome: str  # 'win' or 'loss'
    peak_price_move_pct: float
    time_to_peak_hours: float

@dataclass
class TradeResult:
    market_id: str
    strategy: EntryStrategy
    entry_time: datetime
    entry_price: float
    exit_price: float
    pnl_pct: float
    holding_hours: float
    exit_reason: str

def generate_historical_signals(n=100) -> List[SignalEvent]:
    """
    Generate synthetic signal events based on patterns from:
    - BACKTEST_TIME_HORIZON.md (shorter = better win rate)
    - BACKTEST_POSITION_SIZING.md (55% win rate, 1.5:1 R/R)
    - Signal quality patterns observed
    """
    signals = []
    
    # Time distribution (from TIME_HORIZON analysis)
    time_distributions = {
        'short': (0.667, 2),    # <3 days, 66.7% win rate
        'medium': (0.500, 5),   # 3-7 days, 50% win rate  
        'long': (0.333, 17),    # 7-30 days, 33% win rate
        'very_long': (0.167, 153)  # >30 days, 16% win rate
    }
    
    for i in range(n):
        # Random signal time
        signal_time = datetime(2026, 1, 1) + timedelta(
            days=random.randint(0, 60),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Select time horizon (weighted towards shorter)
        horizon_type = random.choices(
            ['short', 'medium', 'long', 'very_long'],
            weights=[0.4, 0.3, 0.2, 0.1]
        )[0]
        win_rate, avg_days = time_distributions[horizon_type]
        
        days_to_resolution = max(1, int(random.gauss(avg_days, avg_days * 0.3)))
        
        # Generate signal strength
        rvr = random.uniform(2.5, 5.0)  # Volume spike
        roc = random.uniform(8, 20)     # Price momentum
        hype_score = random.uniform(60, 95)
        
        # Signal sustainability (stronger signals hold longer)
        signal_strength = (rvr/5 + roc/20 + hype_score/100) / 3
        signal_sustained_hours = max(0.5, random.gauss(signal_strength * 24, 6))
        
        # Pullback behavior (70% of signals see a pullback)
        pullback_occurs = random.random() < 0.70
        if pullback_occurs:
            pullback_time_hours = random.uniform(1, 8)
            pullback_depth_pct = random.uniform(2, 7)
        else:
            pullback_time_hours = 0
            pullback_depth_pct = 0
        
        # Determine outcome based on horizon
        is_winner = random.random() < win_rate
        
        if is_winner:
            # Winners: avg +7.5% to +12%, peak sooner
            peak_price_move_pct = random.uniform(6, 15)
            time_to_peak_hours = random.uniform(4, 48)
        else:
            # Losers: avg -6% to -10%, may initially move up then reverse
            peak_price_move_pct = random.uniform(-12, -3)
            time_to_peak_hours = random.uniform(12, 72)
        
        initial_price = 0.50  # Normalized starting price
        
        signals.append(SignalEvent(
            market_id=f"market_{i}",
            signal_time=signal_time,
            initial_price=initial_price,
            rvr=rvr,
            roc=roc,
            hype_score=hype_score,
            category=random.choice(['crypto', 'politics', 'sports', 'tech']),
            days_to_resolution=days_to_resolution,
            signal_sustained_hours=signal_sustained_hours,
            pullback_occurs=pullback_occurs,
            pullback_time_hours=pullback_time_hours,
            pullback_depth_pct=pullback_depth_pct,
            final_outcome='win' if is_winner else 'loss',
            peak_price_move_pct=peak_price_move_pct,
            time_to_peak_hours=time_to_peak_hours
        ))
    
    return signals

def simulate_immediate_entry(signal: SignalEvent) -> TradeResult:
    """Strategy 1: Enter immediately when signal fires"""
    entry_time = signal.signal_time
    entry_price = signal.initial_price
    
    # Apply slippage (1% on entry)
    entry_price *= 1.01
    
    # Simulate price movement to exit
    if signal.final_outcome == 'win':
        # Hit take profit (avg +8%)
        exit_price = entry_price * (1 + signal.peak_price_move_pct / 100)
        exit_reason = "TP_HIT"
        holding_hours = signal.time_to_peak_hours
    else:
        # Hit stop loss (-12%) or time decay
        exit_price = entry_price * (1 + signal.peak_price_move_pct / 100)
        exit_reason = "STOP_LOSS" if signal.peak_price_move_pct < -10 else "TIME_DECAY"
        holding_hours = min(signal.time_to_peak_hours, 72)
    
    # Apply exit slippage (1.5%)
    exit_price *= 0.985
    
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
    
    return TradeResult(
        market_id=signal.market_id,
        strategy=EntryStrategy.IMMEDIATE,
        entry_time=entry_time,
        entry_price=entry_price,
        exit_price=exit_price,
        pnl_pct=pnl_pct,
        holding_hours=holding_hours,
        exit_reason=exit_reason
    )

def simulate_confirmation_hold(signal: SignalEvent) -> TradeResult:
    """Strategy 2: Wait for signal to hold for 2+ hours before entering"""
    
    # If signal doesn't sustain for 2 hours, skip trade
    if signal.signal_sustained_hours < 2:
        # Signal faded, no trade taken
        return TradeResult(
            market_id=signal.market_id,
            strategy=EntryStrategy.CONFIRMATION_HOLD,
            entry_time=signal.signal_time + timedelta(hours=2),
            entry_price=0,
            exit_price=0,
            pnl_pct=0,
            holding_hours=0,
            exit_reason="SIGNAL_FADED"
        )
    
    # Enter 2 hours after signal
    entry_time = signal.signal_time + timedelta(hours=2)
    
    # Price may have moved up by 2-3% if signal is strong (opportunity cost)
    price_drift = random.uniform(1, 4) if signal.final_outcome == 'win' else random.uniform(-1, 2)
    entry_price = signal.initial_price * (1 + price_drift / 100)
    entry_price *= 1.01  # Slippage
    
    # Simulate exit
    if signal.final_outcome == 'win':
        # Reduced upside because entered higher
        remaining_move = signal.peak_price_move_pct - price_drift
        exit_price = entry_price * (1 + max(remaining_move, 2) / 100)
        exit_reason = "TP_HIT"
        holding_hours = max(2, signal.time_to_peak_hours - 2)
    else:
        # Same downside risk
        exit_price = entry_price * (1 + signal.peak_price_move_pct / 100)
        exit_reason = "STOP_LOSS" if signal.peak_price_move_pct < -10 else "TIME_DECAY"
        holding_hours = min(signal.time_to_peak_hours, 72)
    
    exit_price *= 0.985  # Exit slippage
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100
    
    return TradeResult(
        market_id=signal.market_id,
        strategy=EntryStrategy.CONFIRMATION_HOLD,
        entry_time=entry_time,
        entry_price=entry_price,
        exit_price=exit_price,
        pnl_pct=pnl_pct,
        holding_hours=holding_hours,
        exit_reason=exit_reason
    )

def simulate_pullback_entry(signal: SignalEvent) -> TradeResult:
    """Strategy 3: Wait for 2-5% pullback after initial spike"""
    
    if not signal.pullback_occurs:
        # No pullback, price runs away - missed trade
        return TradeResult(
            market_id=signal.market_id,
            strategy=EntryStrategy.PULLBACK,
            entry_time=signal.signal_time + timedelta(hours=8),
            entry_price=0,
            exit_price=0,
            pnl_pct=0,
            holding_hours=0,
            exit_reason="NO_PULLBACK"
        )
    
    # Enter at pullback price
    entry_time = signal.signal_time + timedelta(hours=signal.pullback_time_hours)
    entry_price = signal.initial_price * (1 - signal.pullback_depth_pct / 100)
    entry_price *= 1.01  # Slippage
    
    # Better entry price, but signal may be weakening
    if signal.final_outcome == 'win':
        # Same peak, better entry = higher returns
        peak_price = signal.initial_price * (1 + signal.peak_price_move_pct / 100)
        exit_price = peak_price
        exit_reason = "TP_HIT"
        holding_hours = max(2, signal.time_to_peak_hours - signal.pullback_time_hours)
    else:
        # 30% chance pullback signals trend reversal (worse outcome)
        if random.random() < 0.30:
            # Pullback was start of bigger move down
            exit_price = entry_price * 0.88  # Worse than normal stop
            exit_reason = "REVERSAL"
            holding_hours = random.uniform(4, 24)
        else:
            # Normal stop loss
            exit_price = entry_price * (1 + signal.peak_price_move_pct / 100)
            exit_reason = "STOP_LOSS"
            holding_hours = min(signal.time_to_peak_hours, 72)
    
    exit_price *= 0.985  # Exit slippage
    pnl_pct = ((exit_price - entry_price) / entry_price) * 100 if entry_price > 0 else 0
    
    return TradeResult(
        market_id=signal.market_id,
        strategy=EntryStrategy.PULLBACK,
        entry_time=entry_time,
        entry_price=entry_price,
        exit_price=exit_price,
        pnl_pct=pnl_pct,
        holding_hours=holding_hours,
        exit_reason=exit_reason
    )

def simulate_market_hours_entry(signal: SignalEvent) -> TradeResult:
    """Strategy 4: Only enter during market hours (9am-4pm ET)"""
    
    # Check if signal fires during market hours
    signal_hour = signal.signal_time.hour
    is_market_hours = 9 <= signal_hour < 16  # 9am-4pm
    
    if is_market_hours:
        # Enter immediately (same as immediate strategy)
        return simulate_immediate_entry(signal)
    else:
        # Wait until next market open (9am)
        hours_to_wait = (9 - signal_hour) % 24
        entry_time = signal.signal_time + timedelta(hours=hours_to_wait)
        
        # Price may have moved significantly overnight
        overnight_drift = random.uniform(-5, 8) if signal.final_outcome == 'win' else random.uniform(-8, 3)
        entry_price = signal.initial_price * (1 + overnight_drift / 100)
        
        # If price moved too much, skip trade (>10% gap)
        if abs(overnight_drift) > 10:
            return TradeResult(
                market_id=signal.market_id,
                strategy=EntryStrategy.MARKET_HOURS,
                entry_time=entry_time,
                entry_price=0,
                exit_price=0,
                pnl_pct=0,
                holding_hours=0,
                exit_reason="GAP_TOO_LARGE"
            )
        
        entry_price *= 1.01  # Slippage
        
        # Simulate exit
        if signal.final_outcome == 'win':
            remaining_move = signal.peak_price_move_pct - overnight_drift
            exit_price = entry_price * (1 + max(remaining_move, 2) / 100)
            exit_reason = "TP_HIT"
            holding_hours = max(2, signal.time_to_peak_hours - hours_to_wait)
        else:
            exit_price = entry_price * (1 + signal.peak_price_move_pct / 100)
            exit_reason = "STOP_LOSS" if signal.peak_price_move_pct < -10 else "TIME_DECAY"
            holding_hours = min(signal.time_to_peak_hours, 72)
        
        exit_price *= 0.985  # Exit slippage
        pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        
        return TradeResult(
            market_id=signal.market_id,
            strategy=EntryStrategy.MARKET_HOURS,
            entry_time=entry_time,
            entry_price=entry_price,
            exit_price=exit_price,
            pnl_pct=pnl_pct,
            holding_hours=holding_hours,
            exit_reason=exit_reason
        )

def analyze_strategy(results: List[TradeResult], strategy_name: str) -> Dict:
    """Calculate performance metrics for a strategy"""
    
    # Filter out skipped trades
    executed_trades = [r for r in results if r.entry_price > 0]
    all_trades_count = len(results)
    executed_count = len(executed_trades)
    skipped_count = all_trades_count - executed_count
    
    if executed_count == 0:
        return {
            'strategy': strategy_name,
            'total_signals': all_trades_count,
            'trades_executed': 0,
            'trades_skipped': skipped_count,
            'skip_rate': 100.0,
            'win_rate': 0,
            'avg_pnl': 0,
            'total_pnl': 0,
            'expectancy': 0
        }
    
    wins = [r for r in executed_trades if r.pnl_pct > 0]
    losses = [r for r in executed_trades if r.pnl_pct <= 0]
    
    win_rate = len(wins) / executed_count * 100
    avg_win = sum(r.pnl_pct for r in wins) / len(wins) if wins else 0
    avg_loss = sum(r.pnl_pct for r in losses) / len(losses) if losses else 0
    avg_pnl = sum(r.pnl_pct for r in executed_trades) / executed_count
    total_pnl = sum(r.pnl_pct for r in executed_trades)
    
    return {
        'strategy': strategy_name,
        'total_signals': all_trades_count,
        'trades_executed': executed_count,
        'trades_skipped': skipped_count,
        'skip_rate': (skipped_count / all_trades_count * 100) if all_trades_count > 0 else 0,
        'win_rate': win_rate,
        'wins': len(wins),
        'losses': len(losses),
        'avg_win': avg_win,
        'avg_loss': avg_loss,
        'avg_pnl': avg_pnl,
        'total_pnl': total_pnl,
        'expectancy': avg_pnl,
        'best_trade': max(r.pnl_pct for r in executed_trades) if executed_trades else 0,
        'worst_trade': min(r.pnl_pct for r in executed_trades) if executed_trades else 0,
        'avg_holding_hours': sum(r.holding_hours for r in executed_trades) / executed_count if executed_trades else 0
    }

def main():
    print("=" * 80)
    print("ENTRY TIMING BACKTEST")
    print("=" * 80)
    print()
    
    # Generate historical signals
    print("Generating 100 historical signal events...")
    signals = generate_historical_signals(100)
    print(f"✓ Generated {len(signals)} signals")
    print()
    
    # Test each strategy
    strategies = {
        'IMMEDIATE': simulate_immediate_entry,
        'CONFIRMATION (2hr hold)': simulate_confirmation_hold,
        'PULLBACK (2-5% dip)': simulate_pullback_entry,
        'MARKET HOURS ONLY': simulate_market_hours_entry
    }
    
    all_results = {}
    
    for strategy_name, strategy_func in strategies.items():
        print(f"Testing: {strategy_name}...")
        results = [strategy_func(signal) for signal in signals]
        metrics = analyze_strategy(results, strategy_name)
        all_results[strategy_name] = metrics
    
    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    # Print comparison table
    print(f"{'Strategy':<25} {'Executed':<12} {'Skip %':<10} {'Win Rate':<12} {'Avg P&L':<12} {'Expectancy':<12}")
    print("-" * 80)
    
    for strategy_name in strategies.keys():
        m = all_results[strategy_name]
        print(f"{strategy_name:<25} {m['trades_executed']:<12} {m['skip_rate']:<10.1f}% "
              f"{m['win_rate']:<12.1f}% {m['avg_pnl']:<12.2f}% {m['expectancy']:<12.2f}%")
    
    print()
    print("=" * 80)
    print("DETAILED ANALYSIS")
    print("=" * 80)
    print()
    
    # Rank strategies
    ranked = sorted(all_results.items(), key=lambda x: x[1]['expectancy'], reverse=True)
    
    for rank, (strategy_name, metrics) in enumerate(ranked, 1):
        print(f"\n#{rank} - {strategy_name}")
        print("-" * 40)
        print(f"Signals: {metrics['total_signals']}")
        print(f"Executed: {metrics['trades_executed']} ({100 - metrics['skip_rate']:.1f}%)")
        print(f"Skipped: {metrics['trades_skipped']} ({metrics['skip_rate']:.1f}%)")
        print(f"Win Rate: {metrics['win_rate']:.1f}% ({metrics['wins']}W / {metrics['losses']}L)")
        print(f"Average Win: {metrics['avg_win']:.2f}%")
        print(f"Average Loss: {metrics['avg_loss']:.2f}%")
        print(f"Average P&L per Trade: {metrics['avg_pnl']:.2f}%")
        print(f"Total P&L: {metrics['total_pnl']:.2f}%")
        print(f"Expectancy: {metrics['expectancy']:.2f}%")
        print(f"Best Trade: {metrics['best_trade']:.2f}%")
        print(f"Worst Trade: {metrics['worst_trade']:.2f}%")
        print(f"Avg Holding Time: {metrics['avg_holding_hours']:.1f} hours")
    
    # Save results
    with open('entry_timing_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print()
    print("=" * 80)
    print("✓ Results saved to: entry_timing_results.json")
    print("=" * 80)
    
    return all_results

if __name__ == '__main__':
    main()
