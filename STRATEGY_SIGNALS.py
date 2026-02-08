#!/usr/bin/env python3
"""
Strategy Signals Generator for Polymarket Paper Trading
Scans active markets and generates trading signals based on 3 strategies

Usage:
    python STRATEGY_SIGNALS.py --scan
    python STRATEGY_SIGNALS.py --paper-trade
    python STRATEGY_SIGNALS.py --report
"""

import requests
import json
import csv
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

# Configuration
POLYMARKET_API = "https://gamma-api.polymarket.com"
TRADE_LOG_FILE = "PAPER_TRADE_LOG.csv"
POSITIONS_FILE = "positions.json"
CONFIG_FILE = "config.json"

# Strategy Parameters
BANKROLL_START = 5000.00
MAX_EXPOSURE_PCT = 0.25
MAX_EXPOSURE_USD = BANKROLL_START * MAX_EXPOSURE_PCT
CIRCUIT_BREAKER_LOSS = -750.00
DAILY_LOSS_LIMIT = -500.00

# Strategy 1: Fair Price Entry
STRAT1_PRICE_MIN = 0.40
STRAT1_PRICE_MAX = 0.60
STRAT1_POSITION_SIZE = 100.00
STRAT1_MAX_POSITIONS = 3

# Strategy 2: Avoid Longshots
STRAT2_PRICE_MAX = 0.20
STRAT2_POSITION_SIZE = 50.00
STRAT2_MAX_POSITIONS = 2

# Strategy 3: Follow Momentum
STRAT3_PRICE_MIN = 0.50
STRAT3_MOMENTUM_PCT = 0.05
STRAT3_POSITION_SIZE = 75.00
STRAT3_MAX_POSITIONS = 2

# Fees
TRADING_FEE_PCT = 0.02


@dataclass
class Signal:
    """Represents a trading signal"""
    timestamp: str
    market_id: str
    market_question: str
    strategy: int
    side: str
    entry_price: float
    position_size: float
    fees: float
    confidence: str
    reason: str


@dataclass
class Position:
    """Represents an open position"""
    entry_timestamp: str
    market_id: str
    market_question: str
    entry_price: float
    position_size: float
    strategy: int
    side: str
    entry_fees: float
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None


class PaperTradingSystem:
    """Main paper trading system controller"""
    
    def __init__(self):
        self.bankroll = BANKROLL_START
        self.positions: List[Position] = []
        self.signals: List[Signal] = []
        self.closed_trades: List[Dict] = []
        self.load_data()
        
    def load_data(self):
        """Load existing positions and trade history"""
        if os.path.exists(POSITIONS_FILE):
            with open(POSITIONS_FILE, 'r') as f:
                data = json.load(f)
                self.positions = [Position(**p) for p in data.get('positions', [])]
                self.bankroll = data.get('bankroll', BANKROLL_START)
        
        if os.path.exists(TRADE_LOG_FILE):
            with open(TRADE_LOG_FILE, 'r') as f:
                reader = csv.DictReader(f)
                self.closed_trades = list(reader)
    
    def save_data(self):
        """Save positions and bankroll to file"""
        data = {
            'positions': [self._position_to_dict(p) for p in self.positions],
            'bankroll': self.bankroll,
            'last_updated': datetime.utcnow().isoformat()
        }
        with open(POSITIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _position_to_dict(self, p: Position) -> Dict:
        return {
            'entry_timestamp': p.entry_timestamp,
            'market_id': p.market_id,
            'market_question': p.market_question,
            'entry_price': p.entry_price,
            'position_size': p.position_size,
            'strategy': p.strategy,
            'side': p.side,
            'entry_fees': p.entry_fees,
            'current_price': p.current_price,
            'unrealized_pnl': p.unrealized_pnl
        }
    
    def fetch_active_markets(self) -> List[Dict]:
        """Fetch active markets from Polymarket API"""
        print("Searching active markets from Polymarket...")
        
        try:
            # Get active markets with decent liquidity
            params = {
                'active': 'true',
                'closed': 'false',
                'limit': 100,
                'order': 'volume',
                'ascending': 'false'
            }
            
            response = requests.get(
                f"{POLYMARKET_API}/markets",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            markets = response.json()
            print(f"Retrieved {len(markets)} markets")
            
            # Filter for tradable markets
            tradable = []
            for market in markets:
                # Check if market has volume and not too close to resolution
                volume = market.get('volume', 0)
                end_date = market.get('endDate')
                
                if volume and float(volume) > 10000:  # Min $10k volume
                    if end_date:
                        try:
                            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                            days_to_resolution = (end - datetime.utcnow().replace(tzinfo=end.tzinfo)).days
                            if days_to_resolution > 1:  # At least 1 day left
                                tradable.append(market)
                        except:
                            tradable.append(market)  # Include if date parsing fails
            
            print(f"{len(tradable)} markets meet liquidity criteria")
            return tradable
            
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def get_current_price(self, market: Dict) -> Optional[float]:
        """Extract current YES price from market data"""
        try:
            # Debug: print market structure
            if 'outcomes' in market and market['outcomes']:
                # Handle different outcomes formats
                outcomes = market['outcomes']
                if isinstance(outcomes, list):
                    for outcome in outcomes:
                        if isinstance(outcome, dict) and outcome.get('name', '').upper() == 'YES':
                            return float(outcome.get('price', 0))
                elif isinstance(outcomes, dict):
                    # Maybe outcomes is a dict with YES/NO keys
                    if 'YES' in outcomes:
                        return float(outcomes['YES'])
            
            if 'yesAsk' in market:
                return float(market['yesAsk'])
            
            if 'bestAsk' in market:
                return float(market['bestAsk'])
            
            if 'price' in market:
                return float(market['price'])
                
        except (ValueError, TypeError) as e:
            print(f"Price parsing error: {e}")
            pass
        
        return None
    
    def get_price_history(self, market_id: str) -> List[Dict]:
        """Fetch price history for momentum calculation"""
        try:
            response = requests.get(
                f"{POLYMARKET_API}/markets/{market_id}/prices",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return []
    
    def check_momentum(self, market_id: str) -> Tuple[bool, float]:
        """Check if market is trending up (for Strategy 3)"""
        history = self.get_price_history(market_id)
        
        if len(history) < 2:
            return False, 0.0
        
        # Get price from 4 hours ago vs current
        cutoff_time = datetime.utcnow() - timedelta(hours=4)
        recent_prices = [
            h for h in history 
            if datetime.fromisoformat(h.get('timestamp', '').replace('Z', '+00:00')) > cutoff_time
        ]
        
        if len(recent_prices) < 2:
            return False, 0.0
        
        old_price = recent_prices[0].get('price', 0)
        new_price = recent_prices[-1].get('price', 0)
        
        if old_price > 0:
            change_pct = (new_price - old_price) / old_price
            return change_pct >= STRAT3_MOMENTUM_PCT, change_pct
        
        return False, 0.0
    
    def get_strategy_positions_count(self, strategy_num: int) -> int:
        """Count open positions for a specific strategy"""
        return sum(1 for p in self.positions if p.strategy == strategy_num)
    
    def get_total_exposure(self) -> float:
        """Calculate total capital at risk"""
        return sum(p.position_size for p in self.positions)
    
    def check_circuit_breakers(self) -> Tuple[bool, str]:
        """Check if trading should be halted"""
        # Calculate total P&L
        total_pnl = sum(
            float(t.get('net_pnl', 0) or 0) for t in self.closed_trades
        )
        
        # Add unrealized P&L
        for p in self.positions:
            if p.unrealized_pnl:
                total_pnl += p.unrealized_pnl
        
        if total_pnl <= CIRCUIT_BREAKER_LOSS:
            return False, f"CIRCUIT BREAKER: Loss of ${total_pnl:.2f} exceeds limit of ${CIRCUIT_BREAKER_LOSS}"
        
        # Check daily loss
        today = datetime.utcnow().strftime('%Y-%m-%d')
        daily_pnl = sum(
            float(t.get('net_pnl', 0) or 0) 
            for t in self.closed_trades 
            if t.get('exit_timestamp', '').startswith(today)
        )
        
        if daily_pnl <= DAILY_LOSS_LIMIT:
            return False, f"DAILY LIMIT: Loss of ${daily_pnl:.2f} exceeds limit of ${DAILY_LOSS_LIMIT}"
        
        return True, "Trading allowed"
    
    def has_position_in_market(self, market_id: str) -> bool:
        """Check if we already have a position in this market"""
        return any(p.market_id == market_id for p in self.positions)
    
    def generate_signals(self) -> List[Signal]:
        """Scan all markets and generate trading signals"""
        markets = self.fetch_active_markets()
        signals = []
        
        # Check circuit breakers
        can_trade, message = self.check_circuit_breakers()
        if not can_trade:
            print(f"⛔ {message}")
            return []
        
        current_exposure = self.get_total_exposure()
        
        print(f"\nCurrent bankroll: ${self.bankroll:.2f}")
        print(f"Current exposure: ${current_exposure:.2f} / ${MAX_EXPOSURE_USD:.2f}")
        print(f"Open positions: {len(self.positions)}")
        print("-" * 60)
        
        for market in markets:
            market_id = market.get('slug', market.get('id', 'unknown'))
            question = market.get('question', 'Unknown Question')
            
            # Skip if already in position
            if self.has_position_in_market(market_id):
                continue
            
            # Debug: print first market structure (commented out for production)
            # if markets.index(market) == 0:
            #     print(f"DEBUG: Market structure keys: {list(market.keys())}")
            #     if 'outcomes' in market:
            #         print(f"DEBUG: Outcomes type: {type(market['outcomes'])}")
            #         print(f"DEBUG: Outcomes: {market['outcomes'][:2] if isinstance(market['outcomes'], list) else market['outcomes']}")
            
            price = self.get_current_price(market)
            if price is None:
                continue
            
            timestamp = datetime.utcnow().isoformat() + 'Z'
            
            # === STRATEGY 1: Fair Price Entry ===
            s1_count = self.get_strategy_positions_count(1)
            if (s1_count < STRAT1_MAX_POSITIONS and 
                current_exposure + STRAT1_POSITION_SIZE <= MAX_EXPOSURE_USD and
                STRAT1_PRICE_MIN <= price <= STRAT1_PRICE_MAX):
                
                fees = STRAT1_POSITION_SIZE * TRADING_FEE_PCT
                signal = Signal(
                    timestamp=timestamp,
                    market_id=market_id,
                    market_question=question[:100] + "..." if len(question) > 100 else question,
                    strategy=1,
                    side="YES",
                    entry_price=price,
                    position_size=STRAT1_POSITION_SIZE,
                    fees=fees,
                    confidence="MEDIUM",
                    reason=f"Price {price:.2%} in fair value range ({STRAT1_PRICE_MIN:.0%}-{STRAT1_PRICE_MAX:.0%})"
                )
                signals.append(signal)
                print(f"S1 SIGNAL: {market_id} @ {price:.2%}")
            
            # === STRATEGY 2: Avoid Longshots ===
            s2_count = self.get_strategy_positions_count(2)
            if (s2_count < STRAT2_MAX_POSITIONS and 
                current_exposure + STRAT2_POSITION_SIZE <= MAX_EXPOSURE_USD and
                price < STRAT2_PRICE_MAX):
                
                no_price = 1.0 - price
                fees = STRAT2_POSITION_SIZE * TRADING_FEE_PCT
                signal = Signal(
                    timestamp=timestamp,
                    market_id=market_id,
                    market_question=question[:100] + "..." if len(question) > 100 else question,
                    strategy=2,
                    side="NO",
                    entry_price=no_price,
                    position_size=STRAT2_POSITION_SIZE,
                    fees=fees,
                    confidence="HIGH",
                    reason=f"Longshot fade: YES at {price:.2%}, buying NO at {no_price:.2%}"
                )
                signals.append(signal)
                print(f"S2 SIGNAL: {market_id} @ {no_price:.2%} (NO)")
            
            # === STRATEGY 3: Follow Momentum ===
            s3_count = self.get_strategy_positions_count(3)
            has_momentum, momentum_pct = self.check_momentum(market_id)
            
            if (s3_count < STRAT3_MAX_POSITIONS and 
                current_exposure + STRAT3_POSITION_SIZE <= MAX_EXPOSURE_USD and
                price > STRAT3_PRICE_MIN and has_momentum):
                
                fees = STRAT3_POSITION_SIZE * TRADING_FEE_PCT
                signal = Signal(
                    timestamp=timestamp,
                    market_id=market_id,
                    market_question=question[:100] + "..." if len(question) > 100 else question,
                    strategy=3,
                    side="YES",
                    entry_price=price,
                    position_size=STRAT3_POSITION_SIZE,
                    fees=fees,
                    confidence="MEDIUM",
                    reason=f"Momentum: Price {price:.2%} with +{momentum_pct:.1%} trend"
                )
                signals.append(signal)
                print(f"S3 SIGNAL: {market_id} @ {price:.2%} (momentum)")
        
        print(f"\nGenerated {len(signals)} signals")
        return signals
    
    def execute_paper_trade(self, signal: Signal):
        """Execute a paper trade from a signal"""
        # Create position
        position = Position(
            entry_timestamp=signal.timestamp,
            market_id=signal.market_id,
            market_question=signal.market_question,
            entry_price=signal.entry_price,
            position_size=signal.position_size,
            strategy=signal.strategy,
            side=signal.side,
            entry_fees=signal.fees
        )
        
        self.positions.append(position)
        
        # Log to CSV
        self._log_trade_entry(signal)
        
        print(f"PAPER TRADE EXECUTED: {signal.market_id}")
        print(f"   Strategy: {signal.strategy} | Side: {signal.side}")
        print(f"   Size: ${signal.position_size:.2f} | Fees: ${signal.fees:.2f}")
    
    def _log_trade_entry(self, signal: Signal):
        """Log trade entry to CSV"""
        row = {
            'entry_timestamp': signal.timestamp,
            'market_id': signal.market_id,
            'market_question': signal.market_question,
            'entry_price': signal.entry_price,
            'position_size': signal.position_size,
            'strategy': signal.strategy,
            'side': signal.side,
            'entry_fees': signal.fees,
            'exit_timestamp': '',
            'exit_price': '',
            'outcome': 'OPEN',
            'gross_pnl': '',
            'exit_fees': '',
            'net_pnl': '',
            'roi_pct': '',
            'holding_hours': '',
            'bankroll_balance': f"{self.bankroll:.2f}",
            'notes': f"Signal: {signal.reason}"
        }
        
        file_exists = os.path.exists(TRADE_LOG_FILE)
        with open(TRADE_LOG_FILE, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    
    def close_position(self, market_id: str, exit_price: float, outcome: str):
        """Close an open position"""
        position = next((p for p in self.positions if p.market_id == market_id), None)
        if not position:
            print(f"No position found for {market_id}")
            return
        
        # Calculate P&L
        exit_fees = position.position_size * TRADING_FEE_PCT
        
        if position.side == "YES":
            gross_pnl = (exit_price - position.entry_price) * position.position_size
        else:  # NO
            gross_pnl = (position.entry_price - exit_price) * position.position_size
        
        net_pnl = gross_pnl - exit_fees - position.entry_fees
        roi_pct = (net_pnl / position.position_size) * 100
        
        # Calculate holding time
        entry_time = datetime.fromisoformat(position.entry_timestamp.replace('Z', '+00:00'))
        exit_time = datetime.utcnow()
        holding_hours = (exit_time - entry_time).total_seconds() / 3600
        
        # Update bankroll
        self.bankroll += position.position_size + net_pnl
        
        # Remove from positions
        self.positions = [p for p in self.positions if p.market_id != market_id]
        
        # Log the close
        self._log_trade_exit(position, exit_price, outcome, gross_pnl, exit_fees, net_pnl, roi_pct, holding_hours)
        
        print(f"POSITION CLOSED: {market_id}")
        print(f"   Net P&L: ${net_pnl:+.2f} ({roi_pct:+.2f}%)")
        print(f"   New bankroll: ${self.bankroll:.2f}")
        
        self.save_data()
    
    def _log_trade_exit(self, position: Position, exit_price: float, outcome: str, 
                        gross_pnl: float, exit_fees: float, net_pnl: float, 
                        roi_pct: float, holding_hours: float):
        """Update CSV with exit data"""
        # Read all rows
        rows = []
        with open(TRADE_LOG_FILE, 'r') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row['market_id'] == position.market_id and row['outcome'] == 'OPEN':
                    row['exit_timestamp'] = datetime.utcnow().isoformat() + 'Z'
                    row['exit_price'] = f"{exit_price:.4f}"
                    row['outcome'] = outcome
                    row['gross_pnl'] = f"{gross_pnl:.2f}"
                    row['exit_fees'] = f"{exit_fees:.2f}"
                    row['net_pnl'] = f"{net_pnl:.2f}"
                    row['roi_pct'] = f"{roi_pct:.2f}"
                    row['holding_hours'] = f"{holding_hours:.1f}"
                rows.append(row)
        
        # Write back
        with open(TRADE_LOG_FILE, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    def check_resolved_markets(self):
        """Check if any open positions have resolved"""
        print("\nChecking for resolved markets...")
        
        for position in self.positions[:]:  # Copy list to allow modification
            try:
                response = requests.get(
                    f"{POLYMARKET_API}/markets/{position.market_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    market = response.json()
                    
                    if market.get('resolved', False):
                        outcome = market.get('resolution', 'UNKNOWN')
                        
                        if outcome == 'YES':
                            exit_price = 1.0 if position.side == 'YES' else 0.0
                        elif outcome == 'NO':
                            exit_price = 0.0 if position.side == 'YES' else 1.0
                        else:
                            continue  # Skip if ambiguous
                        
                        self.close_position(position.market_id, exit_price, outcome)
                        
            except Exception as e:
                print(f"Error checking {position.market_id}: {e}")
    
    def update_position_prices(self):
        """Update current prices and unrealized P&L for open positions"""
        print("\nUpdating position prices...")
        
        for position in self.positions:
            try:
                response = requests.get(
                    f"{POLYMARKET_API}/markets/{position.market_id}",
                    timeout=10
                )
                if response.status_code == 200:
                    market = response.json()
                    current_price = self.get_current_price(market)
                    
                    if current_price:
                        position.current_price = current_price
                        
                        if position.side == "YES":
                            position.unrealized_pnl = (current_price - position.entry_price) * position.position_size
                        else:
                            no_price = 1.0 - current_price
                            position.unrealized_pnl = (position.entry_price - no_price) * position.position_size
                            
            except Exception as e:
                print(f"Error updating {position.market_id}: {e}")
    
    def generate_report(self):
        """Generate performance report"""
        print("\n" + "=" * 60)
        print("PAPER TRADING PERFORMANCE REPORT")
        print("=" * 60)
        
        print(f"\nBankroll: ${self.bankroll:.2f} (${self.bankroll - BANKROLL_START:+.2f})")
        print(f"Open Positions: {len(self.positions)}")
        print(f"Total Exposure: ${self.get_total_exposure():.2f}")
        
        # Strategy breakdown
        print("\nPositions by Strategy:")
        for i in range(1, 4):
            count = self.get_strategy_positions_count(i)
            print(f"   Strategy {i}: {count} positions")
        
        # Calculate realized P&L
        realized_pnl = sum(
            float(t.get('net_pnl', 0) or 0) for t in self.closed_trades
        )
        print(f"\nRealized P&L: ${realized_pnl:+.2f}")
        
        # Calculate unrealized P&L
        unrealized_pnl = sum(
            p.unrealized_pnl or 0 for p in self.positions
        )
        print(f"Unrealized P&L: ${unrealized_pnl:+.2f}")
        
        total_pnl = realized_pnl + unrealized_pnl
        print(f"Total P&L: ${total_pnl:+.2f} ({(total_pnl/BANKROLL_START)*100:+.2f}%)")
        
        # Win rate
        closed = [t for t in self.closed_trades if t.get('outcome') in ['YES', 'NO']]
        winners = [t for t in closed if float(t.get('net_pnl', 0) or 0) > 0]
        
        if closed:
            win_rate = len(winners) / len(closed) * 100
            print(f"\nWin Rate: {win_rate:.1f}% ({len(winners)}/{len(closed)})")
        
        # Check circuit breakers
        can_trade, message = self.check_circuit_breakers()
        status = "TRADING ENABLED" if can_trade else "TRADING HALTED"
        print(f"\n{status}")
        if not can_trade:
            print(f"   Reason: {message}")
        
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket Paper Trading System')
    parser.add_argument('--scan', action='store_true', help='Scan for signals only')
    parser.add_argument('--paper-trade', action='store_true', help='Execute paper trades')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--check-resolved', action='store_true', help='Check for resolved markets')
    parser.add_argument('--update-prices', action='store_true', help='Update position prices')
    parser.add_argument('--run-all', action='store_true', help='Run full cycle')
    
    args = parser.parse_args()
    
    system = PaperTradingSystem()
    
    if args.scan or args.run_all:
        signals = system.generate_signals()
        
        if args.paper_trade or args.run_all:
            for signal in signals:
                system.execute_paper_trade(signal)
            system.save_data()
    
    if args.check_resolved or args.run_all:
        system.check_resolved_markets()
    
    if args.update_prices or args.run_all:
        system.update_position_prices()
        system.save_data()
    
    if args.report or args.run_all:
        system.generate_report()
    
    if not any(vars(args).values()):
        parser.print_help()


if __name__ == "__main__":
    main()
