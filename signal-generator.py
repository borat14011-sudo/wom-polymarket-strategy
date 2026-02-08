#!/usr/bin/env python3
"""
Real-Time Trading Signal Generator
Monitors database for new snapshots and generates BUY/SELL signals based on strategy framework

Usage: python signal-generator.py [--continuous]
"""

import sqlite3
import json
import time
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import requests

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

class SignalDirection(Enum):
    BUY = "BUY"
    SELL = "SELL"

class ConfidenceLevel(Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class SignalStrength(Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"

@dataclass
class Signal:
    """Trading signal with all required parameters"""
    market_id: str
    market_question: str
    direction: SignalDirection
    confidence: ConfidenceLevel
    entry_price: float
    position_size_pct: float
    position_size_usd: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    
    # Signal metrics
    rvr: float
    roc: float
    hype_score: float
    liquidity: float
    spread: float
    
    # Signal strength breakdown
    volume_signal: SignalStrength
    momentum_signal: SignalStrength
    hype_signal: SignalStrength
    
    # Metadata
    timestamp: str
    reason: str
    
    def to_dict(self):
        return {
            **asdict(self),
            'direction': self.direction.value,
            'confidence': self.confidence.value,
            'volume_signal': self.volume_signal.value,
            'momentum_signal': self.momentum_signal.value,
            'hype_signal': self.hype_signal.value
        }

class SignalGenerator:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.last_check_time = datetime.now() - timedelta(hours=1)
        self.active_positions = self.load_positions()
        self.daily_pnl = self.load_daily_pnl()
        
    def load_positions(self) -> List[Dict]:
        """Load active positions from file"""
        try:
            with open(CONFIG['monitoring']['position_log_path'], 'r') as f:
                positions = json.load(f)
                return [p for p in positions if p.get('status') == 'ACTIVE']
        except FileNotFoundError:
            return []
    
    def save_positions(self):
        """Save active positions to file"""
        with open(CONFIG['monitoring']['position_log_path'], 'w') as f:
            json.dump(self.active_positions, f, indent=2)
    
    def load_daily_pnl(self) -> float:
        """Load today's PnL"""
        try:
            with open(CONFIG['monitoring']['performance_log_path'], 'r') as f:
                perf = json.load(f)
                today = datetime.now().strftime('%Y-%m-%d')
                return perf.get('daily_pnl', {}).get(today, 0.0)
        except FileNotFoundError:
            return 0.0
    
    def calculate_rvr(self, market_id: str) -> Optional[float]:
        """Calculate Relative Volume Ratio"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current volume
        cursor.execute('''
            SELECT volume_24h FROM snapshots
            WHERE market_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        current = cursor.fetchone()
        if not current or not current[0]:
            conn.close()
            return None
        
        current_volume = current[0]
        
        # Get average volume over lookback period
        lookback_hours = CONFIG['monitoring']['lookback_periods']
        cursor.execute('''
            SELECT AVG(volume_24h) FROM snapshots
            WHERE market_id = ?
              AND timestamp > datetime('now', ?)
              AND volume_24h > 0
        ''', (market_id, f'-{lookback_hours} hours'))
        
        avg = cursor.fetchone()
        conn.close()
        
        if not avg or not avg[0] or avg[0] == 0:
            return None
        
        avg_volume = avg[0]
        rvr = current_volume / avg_volume
        
        return rvr
    
    def calculate_roc(self, market_id: str, hours: int = None) -> Optional[float]:
        """Calculate Rate of Change (price momentum)"""
        if hours is None:
            hours = CONFIG['signal_thresholds']['roc_lookback_hours']
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get current price
        cursor.execute('''
            SELECT price_yes FROM snapshots
            WHERE market_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        current = cursor.fetchone()
        if not current or not current[0]:
            conn.close()
            return None
        
        current_price = current[0]
        
        # Get price N hours ago
        cursor.execute('''
            SELECT price_yes FROM snapshots
            WHERE market_id = ?
              AND timestamp <= datetime('now', ?)
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id, f'-{hours} hours'))
        
        past = cursor.fetchone()
        conn.close()
        
        if not past or not past[0] or past[0] == 0:
            return None
        
        past_price = past[0]
        roc = ((current_price - past_price) / past_price) * 100
        
        return roc
    
    def get_latest_hype_score(self, market_id: str) -> Optional[float]:
        """Get latest hype score from hype_signals table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT hype_score FROM hype_signals
            WHERE market_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 0.0
    
    def get_market_data(self, market_id: str) -> Optional[Dict]:
        """Get latest market snapshot and metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                m.question, m.category, m.end_time,
                s.price_yes, s.price_no, s.volume_24h, s.liquidity,
                s.spread, s.timestamp
            FROM markets m
            JOIN snapshots s ON m.market_id = s.market_id
            WHERE m.market_id = ?
            ORDER BY s.timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'market_id': market_id,
            'question': result[0],
            'category': result[1],
            'end_time': result[2],
            'price_yes': result[3],
            'price_no': result[4],
            'volume_24h': result[5],
            'liquidity': result[6],
            'spread': result[7],
            'timestamp': result[8]
        }
    
    def evaluate_signal_strength(self, value: float, thresholds: Dict) -> SignalStrength:
        """Evaluate signal strength based on thresholds"""
        if value >= thresholds.get('strong', float('inf')):
            return SignalStrength.STRONG
        elif value >= thresholds.get('moderate', float('inf')):
            return SignalStrength.MODERATE
        elif value >= thresholds.get('weak', float('inf')):
            return SignalStrength.WEAK
        else:
            return None
    
    def check_entry_signals(self, market_id: str) -> Optional[Tuple[int, List[SignalStrength]]]:
        """
        Check if market meets entry criteria
        Returns: (strong_count, [list of signal strengths]) or None
        """
        # Calculate metrics
        rvr = self.calculate_rvr(market_id)
        roc = self.calculate_roc(market_id)
        hype_score = self.get_latest_hype_score(market_id)
        market_data = self.get_market_data(market_id)
        
        if not market_data:
            return None
        
        # Check minimum requirements
        liquidity = market_data['liquidity']
        if liquidity < CONFIG['signal_thresholds']['liquidity_min']:
            return None
        
        # Evaluate each signal
        thresholds = CONFIG['signal_thresholds']
        
        volume_signal = None
        if rvr:
            volume_signal = self.evaluate_signal_strength(rvr, {
                'strong': thresholds['rvr_strong'],
                'moderate': thresholds['rvr_moderate'],
                'weak': thresholds['rvr_weak']
            })
        
        momentum_signal = None
        if roc:
            momentum_signal = self.evaluate_signal_strength(abs(roc), {
                'strong': thresholds['roc_strong'],
                'moderate': thresholds['roc_moderate'],
                'weak': thresholds['roc_weak']
            })
        
        hype_signal = None
        if hype_score:
            hype_signal = self.evaluate_signal_strength(hype_score, {
                'strong': thresholds['hype_strong'],
                'moderate': thresholds['hype_moderate'],
                'weak': thresholds['hype_weak']
            })
        
        # Filter out None signals
        signals = [s for s in [volume_signal, momentum_signal, hype_signal] if s]
        
        # Need at least 2 signals (relaxed from 3 for practicality)
        if len(signals) < 2:
            return None
        
        # Count strong signals
        strong_count = sum(1 for s in signals if s == SignalStrength.STRONG)
        
        return strong_count, [volume_signal, momentum_signal, hype_signal], {
            'rvr': rvr,
            'roc': roc,
            'hype_score': hype_score
        }
    
    def determine_confidence(self, strong_count: int, signal_count: int) -> ConfidenceLevel:
        """Determine confidence level based on signal matrix"""
        if strong_count >= 3:
            return ConfidenceLevel.HIGH
        elif strong_count >= 2:
            return ConfidenceLevel.HIGH
        elif strong_count >= 1 and signal_count >= 2:
            return ConfidenceLevel.MEDIUM
        else:
            return ConfidenceLevel.LOW
    
    def calculate_position_size(self, confidence: ConfidenceLevel, strong_count: int, 
                                moderate_count: int) -> float:
        """Calculate position size based on signal strength"""
        sizing = CONFIG['position_sizing']
        
        # Base position sizes from config
        if strong_count >= 3:
            base_size = sizing['strong_3_signals']
        elif strong_count >= 2 and moderate_count >= 1:
            base_size = sizing['strong_2_moderate_1']
        elif strong_count >= 1 and moderate_count >= 2:
            base_size = sizing['strong_1_moderate_2']
        elif moderate_count >= 3:
            base_size = sizing['moderate_3_signals']
        else:
            base_size = sizing['moderate_3_signals']  # Minimum
        
        return base_size
    
    def check_disqualifying_conditions(self, market_data: Dict) -> Tuple[bool, str]:
        """Check if market has disqualifying conditions"""
        disq = CONFIG['disqualifying_conditions']
        
        # Liquidity check
        if market_data['liquidity'] < disq['min_liquidity']:
            return True, f"Liquidity too low: ${market_data['liquidity']:,.0f}"
        
        # Spread check
        if market_data['spread'] and market_data['spread'] > disq['max_spread_pct']:
            return True, f"Spread too wide: {market_data['spread']:.2f}%"
        
        # Time to resolution
        if disq['check_resolution_time'] and market_data['end_time']:
            try:
                end_time = datetime.fromisoformat(market_data['end_time'].replace('Z', '+00:00'))
                hours_remaining = (end_time - datetime.now()).total_seconds() / 3600
                
                if hours_remaining < CONFIG['risk_management']['min_time_to_resolution_hours']:
                    return True, f"Too close to resolution: {hours_remaining:.1f}h remaining"
            except:
                pass
        
        # Check existing positions
        if disq['check_existing_positions']:
            category = market_data['category']
            category_positions = [p for p in self.active_positions if p.get('category') == category]
            
            if len(category_positions) >= CONFIG['risk_management']['max_positions_same_category']:
                return True, f"Max positions in category '{category}' reached"
        
        return False, ""
    
    def check_risk_limits(self, new_position_size: float, category: str) -> Tuple[bool, str]:
        """Check if adding position would violate risk limits"""
        bankroll = CONFIG['position_sizing']['bankroll']
        
        # Calculate current exposure
        total_exposure = sum(p['position_size_pct'] for p in self.active_positions)
        category_exposure = sum(p['position_size_pct'] for p in self.active_positions 
                               if p.get('category') == category)
        
        # Check total exposure limit
        if total_exposure + new_position_size > CONFIG['position_sizing']['max_total_exposure']:
            return False, f"Total exposure limit exceeded: {(total_exposure + new_position_size)*100:.1f}%"
        
        # Check category exposure limit
        if category_exposure + new_position_size > CONFIG['position_sizing']['max_category_exposure']:
            return False, f"Category exposure limit exceeded: {(category_exposure + new_position_size)*100:.1f}%"
        
        # Check daily loss limit
        daily_loss_limit = CONFIG['risk_management']['daily_loss_limit_pct'] / 100 * bankroll
        if self.daily_pnl <= daily_loss_limit:
            return False, f"Daily loss limit hit: ${self.daily_pnl:,.2f}"
        
        return True, ""
    
    def generate_signal(self, market_id: str, signals_result: Tuple) -> Optional[Signal]:
        """Generate complete trading signal"""
        strong_count, signal_strengths, metrics = signals_result
        volume_signal, momentum_signal, hype_signal = signal_strengths
        
        # Get market data
        market_data = self.get_market_data(market_id)
        if not market_data:
            return None
        
        # Check disqualifying conditions
        disqualified, reason = self.check_disqualifying_conditions(market_data)
        if disqualified:
            print(f"   ⊘ {market_data['question'][:50]}... - {reason}")
            return None
        
        # Count signal types
        moderate_count = sum(1 for s in signal_strengths if s == SignalStrength.MODERATE)
        
        # Determine confidence and position size
        confidence = self.determine_confidence(strong_count, len([s for s in signal_strengths if s]))
        position_size_pct = self.calculate_position_size(confidence, strong_count, moderate_count)
        
        # Check risk limits
        can_trade, risk_reason = self.check_risk_limits(position_size_pct, market_data['category'])
        if not can_trade:
            print(f"   ⚠ {market_data['question'][:50]}... - {risk_reason}")
            return None
        
        # Determine direction based on ROC
        roc = metrics['roc']
        direction = SignalDirection.BUY if roc > 0 else SignalDirection.SELL
        
        # Calculate entry price and exit levels
        entry_price = market_data['price_yes']
        bankroll = CONFIG['position_sizing']['bankroll']
        position_size_usd = position_size_pct * bankroll
        
        risk_mgmt = CONFIG['risk_management']
        
        if direction == SignalDirection.BUY:
            stop_loss = entry_price * (1 + risk_mgmt['stop_loss_pct'] / 100)
            tp1 = entry_price * (1 + risk_mgmt['take_profit_1_pct'] / 100)
            tp2 = entry_price * (1 + risk_mgmt['take_profit_2_pct'] / 100)
            tp3 = entry_price * (1 + risk_mgmt['take_profit_3_pct'] / 100)
        else:
            stop_loss = entry_price * (1 - risk_mgmt['stop_loss_pct'] / 100)
            tp1 = entry_price * (1 - risk_mgmt['take_profit_1_pct'] / 100)
            tp2 = entry_price * (1 - risk_mgmt['take_profit_2_pct'] / 100)
            tp3 = entry_price * (1 - risk_mgmt['take_profit_3_pct'] / 100)
        
        # Build reason string
        signal_list = []
        if volume_signal:
            signal_list.append(f"Volume {volume_signal.value} (RVR: {metrics['rvr']:.2f})")
        if momentum_signal:
            signal_list.append(f"Momentum {momentum_signal.value} (ROC: {metrics['roc']:+.1f}%)")
        if hype_signal:
            signal_list.append(f"Hype {hype_signal.value} (Score: {metrics['hype_score']:.1f})")
        
        reason = " | ".join(signal_list)
        
        signal = Signal(
            market_id=market_id,
            market_question=market_data['question'],
            direction=direction,
            confidence=confidence,
            entry_price=entry_price,
            position_size_pct=position_size_pct,
            position_size_usd=position_size_usd,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            rvr=metrics['rvr'] or 0,
            roc=metrics['roc'] or 0,
            hype_score=metrics['hype_score'] or 0,
            liquidity=market_data['liquidity'],
            spread=market_data['spread'] or 0,
            volume_signal=volume_signal or SignalStrength.WEAK,
            momentum_signal=momentum_signal or SignalStrength.WEAK,
            hype_signal=hype_signal or SignalStrength.WEAK,
            timestamp=datetime.now().isoformat(),
            reason=reason
        )
        
        return signal
    
    def send_telegram_notification(self, signal: Signal):
        """Send signal notification to Telegram"""
        if not CONFIG['telegram']['enabled']:
            return
        
        # Build message
        icon = "🚀" if signal.direction == SignalDirection.BUY else "🔻"
        
        message = f"""{icon} **{signal.direction.value} SIGNAL**

**Market:** {signal.market_question[:100]}

**Confidence:** {signal.confidence.value}
**Position Size:** {signal.position_size_pct*100:.1f}% (${signal.position_size_usd:,.0f})

**Entry:** ${signal.entry_price:.3f}
**Stop Loss:** ${signal.stop_loss:.3f} ({CONFIG['risk_management']['stop_loss_pct']:+.0f}%)
**TP1:** ${signal.take_profit_1:.3f} (+{CONFIG['risk_management']['take_profit_1_pct']:.0f}%)
**TP2:** ${signal.take_profit_2:.3f} (+{CONFIG['risk_management']['take_profit_2_pct']:.0f}%)
**TP3:** ${signal.take_profit_3:.3f} (+{CONFIG['risk_management']['take_profit_3_pct']:.0f}%)

**Signals:** {signal.reason}

**Liquidity:** ${signal.liquidity:,.0f}
**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        
        try:
            bot_token = CONFIG['telegram']['bot_token']
            chat_id = CONFIG['telegram']['chat_id']
            
            if bot_token == "YOUR_BOT_TOKEN_HERE" or chat_id == "YOUR_CHAT_ID_HERE":
                print("   ℹ Telegram not configured (skipping notification)")
                return
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            response = requests.post(url, json={
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }, timeout=5)
            
            if response.status_code == 200:
                print("   ✓ Telegram notification sent")
            else:
                print(f"   ✗ Telegram error: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Telegram error: {e}")
    
    def log_signal(self, signal: Signal):
        """Log signal to JSONL file"""
        log_path = CONFIG['monitoring']['signal_log_path']
        
        try:
            with open(log_path, 'a') as f:
                f.write(json.dumps(signal.to_dict()) + '\n')
        except Exception as e:
            print(f"   ✗ Error logging signal: {e}")
    
    def display_signal(self, signal: Signal):
        """Display signal to console"""
        icon = "🚀" if signal.direction == SignalDirection.BUY else "🔻"
        
        print(f"\n{'='*80}")
        print(f"{icon} {signal.direction.value} SIGNAL | Confidence: {signal.confidence.value}")
        print(f"{'='*80}")
        print(f"Market: {signal.market_question}")
        print(f"\nEntry: ${signal.entry_price:.3f}")
        print(f"Position: {signal.position_size_pct*100:.1f}% (${signal.position_size_usd:,.0f})")
        print(f"\nExit Levels:")
        print(f"  Stop Loss:    ${signal.stop_loss:.3f} ({CONFIG['risk_management']['stop_loss_pct']:+.0f}%)")
        print(f"  Take Profit 1: ${signal.take_profit_1:.3f} (+{CONFIG['risk_management']['take_profit_1_pct']:.0f}%)")
        print(f"  Take Profit 2: ${signal.take_profit_2:.3f} (+{CONFIG['risk_management']['take_profit_2_pct']:.0f}%)")
        print(f"  Take Profit 3: ${signal.take_profit_3:.3f} (+{CONFIG['risk_management']['take_profit_3_pct']:.0f}%)")
        print(f"\nSignals:")
        print(f"  {signal.reason}")
        print(f"\nMetrics:")
        print(f"  RVR: {signal.rvr:.2f} | ROC: {signal.roc:+.1f}% | Hype: {signal.hype_score:.1f}")
        print(f"  Liquidity: ${signal.liquidity:,.0f} | Spread: {signal.spread:.2f}%")
        print(f"\nTimestamp: {signal.timestamp}")
        print(f"{'='*80}\n")
    
    def scan_for_signals(self) -> List[Signal]:
        """Scan all markets for trading signals"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active markets with recent snapshots
        cursor.execute('''
            SELECT DISTINCT m.market_id
            FROM markets m
            JOIN snapshots s ON m.market_id = s.market_id
            WHERE m.resolved = 0
              AND s.timestamp > datetime('now', '-1 hour')
        ''')
        
        market_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        print(f"\n{'='*80}")
        print(f"Signal Scanner - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        print(f"Scanning {len(market_ids)} active markets...\n")
        
        signals = []
        
        for market_id in market_ids:
            try:
                # Check entry signals
                signals_result = self.check_entry_signals(market_id)
                
                if signals_result:
                    # Generate signal
                    signal = self.generate_signal(market_id, signals_result)
                    
                    if signal:
                        signals.append(signal)
                        
                        # Display signal
                        self.display_signal(signal)
                        
                        # Send Telegram notification
                        self.send_telegram_notification(signal)
                        
                        # Log signal
                        self.log_signal(signal)
                        
            except Exception as e:
                print(f"   ✗ Error processing market {market_id}: {e}")
        
        if not signals:
            print("✓ No signals found")
        else:
            print(f"\n✓ Generated {len(signals)} signal(s)")
        
        print(f"{'='*80}\n")
        
        return signals
    
    def run_continuous(self, interval: int = None):
        """Run signal generator continuously"""
        if interval is None:
            interval = CONFIG['monitoring']['check_interval_seconds']
        
        print(f"🔄 Running in continuous mode (check every {interval}s)")
        print(f"Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.scan_for_signals()
                print(f"💤 Sleeping for {interval}s...\n")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✓ Signal generator stopped")

def main():
    parser = argparse.ArgumentParser(description='Real-Time Trading Signal Generator')
    parser.add_argument('--continuous', action='store_true', 
                       help='Run continuously (default: single scan)')
    parser.add_argument('--interval', type=int, 
                       help=f"Check interval in seconds (default: {CONFIG['monitoring']['check_interval_seconds']})")
    
    args = parser.parse_args()
    
    # Initialize generator
    db_path = CONFIG['database']['path']
    generator = SignalGenerator(db_path)
    
    if args.continuous:
        generator.run_continuous(args.interval)
    else:
        generator.scan_for_signals()

if __name__ == "__main__":
    main()
