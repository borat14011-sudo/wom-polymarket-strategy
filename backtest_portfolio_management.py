#!/usr/bin/env python3
"""
Portfolio Management Backtest - Multi-Position Strategy Testing
Tests portfolio allocation rules for multiple simultaneous positions

Scenarios:
1. Multiple correlated positions (2x Iran markets)
2. Opposite positions (hedge YES on one, NO on correlated)
3. Concentration vs diversification (one 25% vs five 5% positions)
4. Rebalancing rules (when to take profits on winners)

Current Rules:
- Max 5% single position
- Max 25% total exposure
- 50% cash reserve minimum
"""

import random
import numpy as np
import json
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Constants
STARTING_BANKROLL = 1000  # Use $1000 for more realistic position sizing
NUM_SIMULATIONS = 1000
SIMULATION_DAYS = 180  # 6 months
WIN_RATE_BASE = 0.55
REWARD_RISK_RATIO = 1.5

# Portfolio rules
MAX_SINGLE_POSITION_PCT = 0.05  # 5%
MAX_TOTAL_EXPOSURE_PCT = 0.25   # 25%
MIN_CASH_RESERVE_PCT = 0.50     # 50%

# Position sizing using quarter Kelly (from previous backtest recommendation)
KELLY_FULL = 0.25  # Full Kelly for 55% win rate, 1.5 R:R
POSITION_SIZE_KELLY = KELLY_FULL * 0.25  # Quarter Kelly = 6.25%

# Correlation coefficients
CORRELATION_HIGH = 0.85  # Iran markets highly correlated
CORRELATION_MODERATE = 0.60  # Related but not perfectly correlated
CORRELATION_LOW = 0.20  # Weakly correlated
CORRELATION_NEGATIVE = -0.70  # Inverse correlation (hedge positions)

@dataclass
class Position:
    """Individual position in portfolio"""
    market_id: str
    entry_price: float
    size_usd: float
    size_pct: float
    direction: str  # 'YES' or 'NO'
    correlation_group: str
    days_held: int = 0
    unrealized_pnl: float = 0.0
    
    def update_pnl(self, current_price: float, rrr: float):
        """Update unrealized P&L"""
        if self.direction == 'YES':
            price_change = current_price - self.entry_price
        else:  # 'NO' position
            price_change = self.entry_price - current_price
        
        # Calculate P&L based on position size
        self.unrealized_pnl = (price_change / self.entry_price) * self.size_usd * rrr

@dataclass
class Trade:
    """Record of a completed trade"""
    market_id: str
    entry_price: float
    exit_price: float
    size_usd: float
    pnl: float
    win: bool
    days_held: int
    reason: str  # 'target', 'stop', 'rebalance'

class Portfolio:
    """Portfolio manager for multiple positions"""
    
    def __init__(self, starting_capital: float):
        self.starting_capital = starting_capital
        self.cash = starting_capital
        self.positions: List[Position] = []
        self.trades: List[Trade] = []
        self.equity_curve = [starting_capital]
        self.daily_returns = []
        self.max_drawdown = 0.0
        self.peak_equity = starting_capital
        
    @property
    def total_equity(self) -> float:
        """Total portfolio value (cash + unrealized P&L)"""
        position_value = sum(p.size_usd + p.unrealized_pnl for p in self.positions)
        return self.cash + position_value
    
    @property
    def total_exposure(self) -> float:
        """Total capital deployed in positions"""
        return sum(p.size_usd for p in self.positions)
    
    @property
    def exposure_pct(self) -> float:
        """Exposure as percentage of total equity"""
        return self.total_exposure / self.total_equity if self.total_equity > 0 else 0
    
    @property
    def num_positions(self) -> int:
        return len(self.positions)
    
    def can_add_position(self, size_usd: float) -> bool:
        """Check if we can add a new position within risk limits"""
        total_equity = self.total_equity
        
        # Check single position limit
        if size_usd > total_equity * MAX_SINGLE_POSITION_PCT:
            return False
        
        # Check total exposure limit
        if (self.total_exposure + size_usd) > total_equity * MAX_TOTAL_EXPOSURE_PCT:
            return False
        
        # Check minimum cash reserve
        if (self.cash - size_usd) < total_equity * MIN_CASH_RESERVE_PCT:
            return False
        
        return True
    
    def add_position(self, market_id: str, size_usd: float, direction: str, 
                     correlation_group: str, entry_price: float = 0.5):
        """Add a new position to portfolio"""
        if not self.can_add_position(size_usd):
            return False
        
        size_pct = size_usd / self.total_equity
        position = Position(
            market_id=market_id,
            entry_price=entry_price,
            size_usd=size_usd,
            size_pct=size_pct,
            direction=direction,
            correlation_group=correlation_group
        )
        
        self.positions.append(position)
        self.cash -= size_usd
        return True
    
    def close_position(self, position: Position, exit_price: float, reason: str):
        """Close a position and realize P&L"""
        # Calculate final P&L
        if position.direction == 'YES':
            price_change = exit_price - position.entry_price
        else:
            price_change = position.entry_price - exit_price
        
        pnl = (price_change / position.entry_price) * position.size_usd * REWARD_RISK_RATIO
        
        # Return capital + P&L to cash
        self.cash += position.size_usd + pnl
        
        # Record trade
        trade = Trade(
            market_id=position.market_id,
            entry_price=position.entry_price,
            exit_price=exit_price,
            size_usd=position.size_usd,
            pnl=pnl,
            win=pnl > 0,
            days_held=position.days_held,
            reason=reason
        )
        self.trades.append(trade)
        
        # Remove from active positions
        self.positions.remove(position)
        
        return pnl
    
    def update_positions(self):
        """Update all position P&L and check exit conditions"""
        for position in self.positions[:]:  # Copy list since we might remove items
            position.days_held += 1
            
            # Simulate price movement
            # Win/loss determined by base win rate, modified by correlation
            is_winner = random.random() < WIN_RATE_BASE
            
            if is_winner:
                # Winning trade - moves toward target
                exit_price = position.entry_price * 1.15  # +15% move
                if random.random() < 0.33:  # 33% chance to hit first target
                    self.close_position(position, exit_price, 'target')
            else:
                # Losing trade - hits stop
                exit_price = position.entry_price * 0.88  # -12% stop
                if random.random() < 0.25:  # 25% chance to hit stop on a given day
                    self.close_position(position, exit_price, 'stop')
            
            # Update unrealized P&L for positions still open
            if position in self.positions:
                position.update_pnl(
                    position.entry_price * (1.05 if is_winner else 0.98),
                    REWARD_RISK_RATIO
                )
    
    def update_equity_curve(self):
        """Record current equity"""
        equity = self.total_equity
        self.equity_curve.append(equity)
        
        # Calculate daily return
        if len(self.equity_curve) > 1:
            daily_return = (equity / self.equity_curve[-2]) - 1
            self.daily_returns.append(daily_return)
        
        # Update drawdown
        if equity > self.peak_equity:
            self.peak_equity = equity
        
        drawdown = (self.peak_equity - equity) / self.peak_equity
        self.max_drawdown = max(self.max_drawdown, drawdown)
    
    def should_rebalance(self) -> List[Position]:
        """Identify positions to close for rebalancing"""
        # Rebalance if we have winners > 25% gain
        winners_to_close = []
        for position in self.positions:
            if position.unrealized_pnl > position.size_usd * 0.25:  # 25% gain
                winners_to_close.append(position)
        return winners_to_close


def simulate_correlated_positions(correlation: float, num_positions: int) -> Dict:
    """
    Simulate multiple correlated positions (e.g., 2x Iran markets)
    
    High correlation means if one loses, others likely lose too.
    This tests whether diversification works with correlated assets.
    """
    results = []
    
    for sim in range(NUM_SIMULATIONS):
        portfolio = Portfolio(STARTING_BANKROLL)
        
        for day in range(SIMULATION_DAYS):
            # Try to add positions if we have room
            if portfolio.num_positions < num_positions:
                size = min(
                    portfolio.total_equity * POSITION_SIZE_KELLY,
                    portfolio.total_equity * MAX_SINGLE_POSITION_PCT
                )
                
                if portfolio.can_add_position(size):
                    market_id = f"correlated_market_{portfolio.num_positions + 1}"
                    portfolio.add_position(
                        market_id=market_id,
                        size_usd=size,
                        direction='YES',
                        correlation_group='iran_cluster',
                        entry_price=0.50
                    )
            
            # Simulate correlated outcomes
            # If correlation is high, positions move together
            base_outcome = random.random() < WIN_RATE_BASE
            
            for position in portfolio.positions[:]:
                # Correlated outcome: blend base outcome with correlation strength
                if random.random() < correlation:
                    is_winner = base_outcome  # Correlated
                else:
                    is_winner = random.random() < WIN_RATE_BASE  # Independent
                
                # Determine exit
                if is_winner and random.random() < 0.15:  # 15% daily prob of hitting target
                    exit_price = position.entry_price * 1.15
                    portfolio.close_position(position, exit_price, 'target')
                elif not is_winner and random.random() < 0.20:  # 20% daily prob of hitting stop
                    exit_price = position.entry_price * 0.88
                    portfolio.close_position(position, exit_price, 'stop')
                else:
                    # Update unrealized P&L
                    position.update_pnl(
                        position.entry_price * (1.03 if is_winner else 0.97),
                        REWARD_RISK_RATIO
                    )
            
            portfolio.update_equity_curve()
        
        results.append({
            'final_equity': portfolio.total_equity,
            'total_return': (portfolio.total_equity / STARTING_BANKROLL - 1) * 100,
            'max_drawdown': portfolio.max_drawdown * 100,
            'num_trades': len(portfolio.trades),
            'win_rate': sum(1 for t in portfolio.trades if t.win) / len(portfolio.trades) if portfolio.trades else 0,
            'total_pnl': sum(t.pnl for t in portfolio.trades)
        })
    
    return {
        'median_return': np.median([r['total_return'] for r in results]),
        'mean_return': np.mean([r['total_return'] for r in results]),
        'median_drawdown': np.median([r['max_drawdown'] for r in results]),
        'max_drawdown': np.max([r['max_drawdown'] for r in results]),
        'median_trades': np.median([r['num_trades'] for r in results]),
        'win_rate': np.mean([r['win_rate'] for r in results]),
        'p25_return': np.percentile([r['total_return'] for r in results], 25),
        'p75_return': np.percentile([r['total_return'] for r in results], 75),
        'results': results
    }


def simulate_hedge_positions() -> Dict:
    """
    Simulate opposite positions (YES on one market, NO on correlated market)
    
    This tests if hedging reduces risk or just reduces returns.
    """
    results = []
    
    for sim in range(NUM_SIMULATIONS):
        portfolio = Portfolio(STARTING_BANKROLL)
        
        for day in range(SIMULATION_DAYS):
            # Try to add hedge pair if we have room
            if portfolio.num_positions < 2:
                size = min(
                    portfolio.total_equity * POSITION_SIZE_KELLY,
                    portfolio.total_equity * MAX_SINGLE_POSITION_PCT
                )
                
                if portfolio.can_add_position(size * 2):  # Need room for both
                    # Position 1: YES
                    portfolio.add_position(
                        market_id="iran_strike",
                        size_usd=size,
                        direction='YES',
                        correlation_group='iran_hedge',
                        entry_price=0.50
                    )
                    # Position 2: NO on correlated (hedge)
                    portfolio.add_position(
                        market_id="oil_price_drop",  # Inverse correlated
                        size_usd=size,
                        direction='NO',
                        correlation_group='iran_hedge',
                        entry_price=0.50
                    )
            
            # Simulate inverse correlated outcomes
            base_outcome = random.random() < WIN_RATE_BASE
            
            for i, position in enumerate(portfolio.positions[:]):
                # Positions are inversely correlated
                if i % 2 == 0:
                    is_winner = base_outcome
                else:
                    # Inverse outcome with correlation strength
                    if random.random() < abs(CORRELATION_NEGATIVE):
                        is_winner = not base_outcome
                    else:
                        is_winner = random.random() < WIN_RATE_BASE
                
                # Determine exit
                if is_winner and random.random() < 0.15:
                    exit_price = position.entry_price * 1.15
                    portfolio.close_position(position, exit_price, 'target')
                elif not is_winner and random.random() < 0.20:
                    exit_price = position.entry_price * 0.88
                    portfolio.close_position(position, exit_price, 'stop')
                else:
                    position.update_pnl(
                        position.entry_price * (1.03 if is_winner else 0.97),
                        REWARD_RISK_RATIO
                    )
            
            portfolio.update_equity_curve()
        
        results.append({
            'final_equity': portfolio.total_equity,
            'total_return': (portfolio.total_equity / STARTING_BANKROLL - 1) * 100,
            'max_drawdown': portfolio.max_drawdown * 100,
            'num_trades': len(portfolio.trades),
            'win_rate': sum(1 for t in portfolio.trades if t.win) / len(portfolio.trades) if portfolio.trades else 0
        })
    
    return {
        'median_return': np.median([r['total_return'] for r in results]),
        'median_drawdown': np.median([r['max_drawdown'] for r in results]),
        'max_drawdown': np.max([r['max_drawdown'] for r in results]),
        'win_rate': np.mean([r['win_rate'] for r in results]),
        'p25_return': np.percentile([r['total_return'] for r in results], 25),
        'p75_return': np.percentile([r['total_return'] for r in results], 75)
    }


def simulate_concentration_vs_diversification() -> Tuple[Dict, Dict]:
    """
    Compare: One 25% position vs Five 5% positions
    
    Tests if concentration or diversification performs better.
    """
    concentrated_results = []
    diversified_results = []
    
    for sim in range(NUM_SIMULATIONS):
        # Concentrated strategy: One large position
        port_concentrated = Portfolio(STARTING_BANKROLL)
        
        # Diversified strategy: Multiple small positions
        port_diversified = Portfolio(STARTING_BANKROLL)
        
        for day in range(SIMULATION_DAYS):
            # CONCENTRATED: Try to maintain one 25% position
            if port_concentrated.num_positions == 0:
                size = port_concentrated.total_equity * MAX_TOTAL_EXPOSURE_PCT
                if port_concentrated.cash >= size:
                    port_concentrated.add_position(
                        market_id="concentrated_bet",
                        size_usd=size,
                        direction='YES',
                        correlation_group='concentrated',
                        entry_price=0.50
                    )
            
            # DIVERSIFIED: Try to maintain five 5% positions
            if port_diversified.num_positions < 5:
                size = port_diversified.total_equity * MAX_SINGLE_POSITION_PCT
                if port_diversified.can_add_position(size):
                    port_diversified.add_position(
                        market_id=f"diversified_bet_{port_diversified.num_positions + 1}",
                        size_usd=size,
                        direction='YES',
                        correlation_group='diversified',
                        entry_price=0.50
                    )
            
            # Update both portfolios
            for portfolio in [port_concentrated, port_diversified]:
                for position in portfolio.positions[:]:
                    is_winner = random.random() < WIN_RATE_BASE
                    
                    if is_winner and random.random() < 0.15:
                        exit_price = position.entry_price * 1.15
                        portfolio.close_position(position, exit_price, 'target')
                    elif not is_winner and random.random() < 0.20:
                        exit_price = position.entry_price * 0.88
                        portfolio.close_position(position, exit_price, 'stop')
                    else:
                        position.update_pnl(
                            position.entry_price * (1.03 if is_winner else 0.97),
                            REWARD_RISK_RATIO
                        )
                
                portfolio.update_equity_curve()
        
        concentrated_results.append({
            'final_equity': port_concentrated.total_equity,
            'total_return': (port_concentrated.total_equity / STARTING_BANKROLL - 1) * 100,
            'max_drawdown': port_concentrated.max_drawdown * 100,
            'num_trades': len(port_concentrated.trades),
            'win_rate': sum(1 for t in port_concentrated.trades if t.win) / len(port_concentrated.trades) if port_concentrated.trades else 0
        })
        
        diversified_results.append({
            'final_equity': port_diversified.total_equity,
            'total_return': (port_diversified.total_equity / STARTING_BANKROLL - 1) * 100,
            'max_drawdown': port_diversified.max_drawdown * 100,
            'num_trades': len(port_diversified.trades),
            'win_rate': sum(1 for t in port_diversified.trades if t.win) / len(port_diversified.trades) if port_diversified.trades else 0
        })
    
    return (
        {
            'strategy': 'CONCENTRATED (One 25% position)',
            'median_return': np.median([r['total_return'] for r in concentrated_results]),
            'median_drawdown': np.median([r['max_drawdown'] for r in concentrated_results]),
            'max_drawdown': np.max([r['max_drawdown'] for r in concentrated_results]),
            'win_rate': np.mean([r['win_rate'] for r in concentrated_results]),
            'p25_return': np.percentile([r['total_return'] for r in concentrated_results], 25),
            'p75_return': np.percentile([r['total_return'] for r in concentrated_results], 75)
        },
        {
            'strategy': 'DIVERSIFIED (Five 5% positions)',
            'median_return': np.median([r['total_return'] for r in diversified_results]),
            'median_drawdown': np.median([r['max_drawdown'] for r in diversified_results]),
            'max_drawdown': np.max([r['max_drawdown'] for r in diversified_results]),
            'win_rate': np.mean([r['win_rate'] for r in diversified_results]),
            'p25_return': np.percentile([r['total_return'] for r in diversified_results], 25),
            'p75_return': np.percentile([r['total_return'] for r in diversified_results], 75)
        }
    )


def simulate_rebalancing_strategies() -> Dict:
    """
    Test different rebalancing rules:
    1. Never rebalance (let winners run)
    2. Take 50% profits at +25% gain
    3. Full rebalance at +25% (close entire position)
    """
    results = {}
    
    for strategy_name, rebalance_pct in [
        ('NO_REBALANCE', 0.0),
        ('HALF_REBALANCE', 0.5),
        ('FULL_REBALANCE', 1.0)
    ]:
        strategy_results = []
        
        for sim in range(NUM_SIMULATIONS):
            portfolio = Portfolio(STARTING_BANKROLL)
            
            for day in range(SIMULATION_DAYS):
                # Add positions up to max exposure
                while portfolio.num_positions < 5:
                    size = min(
                        portfolio.total_equity * POSITION_SIZE_KELLY,
                        portfolio.total_equity * MAX_SINGLE_POSITION_PCT
                    )
                    if portfolio.can_add_position(size):
                        portfolio.add_position(
                            market_id=f"rebalance_test_{portfolio.num_positions}",
                            size_usd=size,
                            direction='YES',
                            correlation_group='rebalance',
                            entry_price=0.50
                        )
                    else:
                        break
                
                # Check rebalancing rules
                for position in portfolio.positions[:]:
                    gain_pct = position.unrealized_pnl / position.size_usd if position.size_usd > 0 else 0
                    
                    # Rebalance if winner > 25%
                    if gain_pct > 0.25 and rebalance_pct > 0:
                        if rebalance_pct == 1.0:
                            # Full rebalance - close entire position
                            exit_price = position.entry_price * 1.25
                            portfolio.close_position(position, exit_price, 'rebalance')
                        elif rebalance_pct == 0.5:
                            # Half rebalance - take 50% profits
                            # Simulate by closing position and re-entering at half size
                            exit_price = position.entry_price * 1.25
                            original_size = position.size_usd
                            portfolio.close_position(position, exit_price, 'rebalance')
                            # Re-enter at half size
                            if portfolio.can_add_position(original_size * 0.5):
                                portfolio.add_position(
                                    market_id=position.market_id + "_reentry",
                                    size_usd=original_size * 0.5,
                                    direction=position.direction,
                                    correlation_group=position.correlation_group,
                                    entry_price=exit_price
                                )
                
                # Normal position updates
                for position in portfolio.positions[:]:
                    is_winner = random.random() < WIN_RATE_BASE
                    
                    if is_winner and random.random() < 0.15:
                        exit_price = position.entry_price * 1.15
                        portfolio.close_position(position, exit_price, 'target')
                    elif not is_winner and random.random() < 0.20:
                        exit_price = position.entry_price * 0.88
                        portfolio.close_position(position, exit_price, 'stop')
                    else:
                        position.update_pnl(
                            position.entry_price * (1.03 if is_winner else 0.97),
                            REWARD_RISK_RATIO
                        )
                
                portfolio.update_equity_curve()
            
            strategy_results.append({
                'final_equity': portfolio.total_equity,
                'total_return': (portfolio.total_equity / STARTING_BANKROLL - 1) * 100,
                'max_drawdown': portfolio.max_drawdown * 100,
                'num_trades': len(portfolio.trades),
                'win_rate': sum(1 for t in portfolio.trades if t.win) / len(portfolio.trades) if portfolio.trades else 0
            })
        
        results[strategy_name] = {
            'strategy': strategy_name,
            'median_return': np.median([r['total_return'] for r in strategy_results]),
            'median_drawdown': np.median([r['max_drawdown'] for r in strategy_results]),
            'max_drawdown': np.max([r['max_drawdown'] for r in strategy_results]),
            'win_rate': np.mean([r['win_rate'] for r in strategy_results]),
            'p25_return': np.percentile([r['total_return'] for r in strategy_results], 25),
            'p75_return': np.percentile([r['total_return'] for r in strategy_results], 75)
        }
    
    return results


def main():
    print("=" * 80)
    print("PORTFOLIO MANAGEMENT BACKTEST")
    print("=" * 80)
    print(f"Starting Capital: ${STARTING_BANKROLL:,}")
    print(f"Simulation Period: {SIMULATION_DAYS} days")
    print(f"Number of Simulations: {NUM_SIMULATIONS:,}")
    print(f"Base Win Rate: {WIN_RATE_BASE*100}%")
    print(f"Reward/Risk Ratio: {REWARD_RISK_RATIO}:1")
    print()
    print("Current Portfolio Rules:")
    print(f"  - Max Single Position: {MAX_SINGLE_POSITION_PCT*100}%")
    print(f"  - Max Total Exposure: {MAX_TOTAL_EXPOSURE_PCT*100}%")
    print(f"  - Min Cash Reserve: {MIN_CASH_RESERVE_PCT*100}%")
    print(f"  - Position Sizing: Quarter Kelly ({POSITION_SIZE_KELLY*100:.2f}%)")
    print("=" * 80)
    print()
    
    # SCENARIO 1: Correlated Positions
    print("📊 SCENARIO 1: Multiple Correlated Positions (2x Iran Markets)")
    print("-" * 80)
    print("Testing: Should we take multiple positions in correlated markets?")
    print()
    
    print("Running simulations for different correlation levels...")
    high_corr = simulate_correlated_positions(CORRELATION_HIGH, 2)
    moderate_corr = simulate_correlated_positions(CORRELATION_MODERATE, 2)
    low_corr = simulate_correlated_positions(CORRELATION_LOW, 2)
    
    print("\nResults:")
    print(f"\n  HIGH CORRELATION (0.85) - Two Iran markets:")
    print(f"    Median Return: {high_corr['median_return']:.1f}%")
    print(f"    Median Drawdown: {high_corr['median_drawdown']:.1f}%")
    print(f"    Max Drawdown: {high_corr['max_drawdown']:.1f}%")
    print(f"    Win Rate: {high_corr['win_rate']*100:.1f}%")
    
    print(f"\n  MODERATE CORRELATION (0.60) - Related markets:")
    print(f"    Median Return: {moderate_corr['median_return']:.1f}%")
    print(f"    Median Drawdown: {moderate_corr['median_drawdown']:.1f}%")
    print(f"    Max Drawdown: {moderate_corr['max_drawdown']:.1f}%")
    print(f"    Win Rate: {moderate_corr['win_rate']*100:.1f}%")
    
    print(f"\n  LOW CORRELATION (0.20) - Diversified markets:")
    print(f"    Median Return: {low_corr['median_return']:.1f}%")
    print(f"    Median Drawdown: {low_corr['median_drawdown']:.1f}%")
    print(f"    Max Drawdown: {low_corr['max_drawdown']:.1f}%")
    print(f"    Win Rate: {low_corr['win_rate']*100:.1f}%")
    
    print("\n" + "=" * 80)
    print()
    
    # SCENARIO 2: Hedge Positions
    print("📊 SCENARIO 2: Opposite Positions (Hedging)")
    print("-" * 80)
    print("Testing: YES on one market, NO on inversely correlated market")
    print()
    
    hedge_results = simulate_hedge_positions()
    
    print("Results:")
    print(f"  Median Return: {hedge_results['median_return']:.1f}%")
    print(f"  Median Drawdown: {hedge_results['median_drawdown']:.1f}%")
    print(f"  Max Drawdown: {hedge_results['max_drawdown']:.1f}%")
    print(f"  Win Rate: {hedge_results['win_rate']*100:.1f}%")
    
    print("\n" + "=" * 80)
    print()
    
    # SCENARIO 3: Concentration vs Diversification
    print("📊 SCENARIO 3: Concentration vs Diversification")
    print("-" * 80)
    print("Testing: One 25% position vs Five 5% positions")
    print()
    
    concentrated, diversified = simulate_concentration_vs_diversification()
    
    print("Results:")
    print(f"\n  CONCENTRATED (One 25% position):")
    print(f"    Median Return: {concentrated['median_return']:.1f}%")
    print(f"    Median Drawdown: {concentrated['median_drawdown']:.1f}%")
    print(f"    Max Drawdown: {concentrated['max_drawdown']:.1f}%")
    print(f"    Win Rate: {concentrated['win_rate']*100:.1f}%")
    print(f"    25th-75th Percentile: {concentrated['p25_return']:.1f}% - {concentrated['p75_return']:.1f}%")
    
    print(f"\n  DIVERSIFIED (Five 5% positions):")
    print(f"    Median Return: {diversified['median_return']:.1f}%")
    print(f"    Median Drawdown: {diversified['median_drawdown']:.1f}%")
    print(f"    Max Drawdown: {diversified['max_drawdown']:.1f}%")
    print(f"    Win Rate: {diversified['win_rate']*100:.1f}%")
    print(f"    25th-75th Percentile: {diversified['p25_return']:.1f}% - {diversified['p75_return']:.1f}%")
    
    print("\n" + "=" * 80)
    print()
    
    # SCENARIO 4: Rebalancing Rules
    print("📊 SCENARIO 4: Rebalancing Strategies")
    print("-" * 80)
    print("Testing: When to take profits on winners")
    print()
    
    rebalance_results = simulate_rebalancing_strategies()
    
    print("Results:")
    for strategy_name, results in rebalance_results.items():
        print(f"\n  {strategy_name}:")
        print(f"    Median Return: {results['median_return']:.1f}%")
        print(f"    Median Drawdown: {results['median_drawdown']:.1f}%")
        print(f"    Max Drawdown: {results['max_drawdown']:.1f}%")
        print(f"    Win Rate: {results['win_rate']*100:.1f}%")
        print(f"    25th-75th Percentile: {results['p25_return']:.1f}% - {results['p75_return']:.1f}%")
    
    print("\n" + "=" * 80)
    print()
    
    # Save detailed results
    all_results = {
        'correlation_scenarios': {
            'high': high_corr,
            'moderate': moderate_corr,
            'low': low_corr
        },
        'hedge_strategy': hedge_results,
        'concentration_vs_diversification': {
            'concentrated': concentrated,
            'diversified': diversified
        },
        'rebalancing_strategies': rebalance_results,
        'simulation_params': {
            'starting_capital': STARTING_BANKROLL,
            'simulation_days': SIMULATION_DAYS,
            'num_simulations': NUM_SIMULATIONS,
            'win_rate': WIN_RATE_BASE,
            'reward_risk_ratio': REWARD_RISK_RATIO,
            'max_single_position': MAX_SINGLE_POSITION_PCT,
            'max_total_exposure': MAX_TOTAL_EXPOSURE_PCT,
            'min_cash_reserve': MIN_CASH_RESERVE_PCT
        }
    }
    
    with open('backtest_portfolio_results.json', 'w') as f:
        # Convert numpy types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        json.dump(convert_numpy(all_results), f, indent=2)
    
    print("✅ Detailed results saved to backtest_portfolio_results.json")
    print()


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    np.random.seed(42)
    main()
