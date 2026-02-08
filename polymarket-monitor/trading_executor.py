"""
Polymarket Trading Executor
Executes trades based on signals with Kelly Criterion position sizing
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingExecutor:
    """Executes trades on Polymarket with risk management"""
    
    def __init__(self, wallet_key: str, bankroll: float = 100.0):
        """
        Initialize trading executor
        
        Args:
            wallet_key: Encrypted wallet private key
            bankroll: Starting capital in USDC
        """
        self.wallet_key = wallet_key
        self.initial_bankroll = bankroll
        self.current_bankroll = bankroll
        self.max_position_pct = 0.05  # 5% max per trade
        self.max_exposure_pct = 0.25  # 25% total exposure
        self.stop_loss_pct = 0.12  # 12% stop loss
        self.circuit_breaker_pct = 0.15  # 15% total loss = pause
        
        self.db_path = "polymarket_data.db"
        self.positions: List[Dict] = []
        self.total_exposure = 0.0
        
        logger.info(f"Trading Executor initialized with ${bankroll} bankroll")
    
    
    def calculate_kelly_size(self, win_prob: float, payout: float, 
                            current_price: float) -> float:
        """
        Calculate position size using Kelly Criterion (quarter-Kelly)
        
        Args:
            win_prob: Estimated probability of winning (0-1)
            payout: Potential payout ratio
            current_price: Current market price (0-1)
        
        Returns:
            Position size as fraction of bankroll
        """
        # Quarter-Kelly formula for conservative sizing
        # f = (p * payout - (1-p)) / payout * 0.25
        
        edge = win_prob * payout - (1 - win_prob)
        if edge <= 0:
            return 0.0
        
        kelly_fraction = (edge / payout) * 0.25  # Quarter-Kelly
        
        # Cap at max position size
        return min(kelly_fraction, self.max_position_pct)
    
    
    def check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should trigger"""
        total_loss = self.initial_bankroll - self.current_bankroll
        loss_pct = total_loss / self.initial_bankroll
        
        if loss_pct >= self.circuit_breaker_pct:
            logger.critical(f"🚨 CIRCUIT BREAKER TRIGGERED! Down {loss_pct*100:.1f}%")
            return True
        
        return False
    
    
    def can_open_position(self, position_size: float) -> bool:
        """Check if we can open a new position within exposure limits"""
        new_exposure = self.total_exposure + position_size
        max_exposure = self.current_bankroll * self.max_exposure_pct
        
        if new_exposure > max_exposure:
            logger.warning(f"Position rejected: Would exceed max exposure (${new_exposure:.2f} > ${max_exposure:.2f})")
            return False
        
        return True
    
    
    def evaluate_signal(self, signal: Dict) -> Optional[Dict]:
        """
        Evaluate a trading signal and generate trade decision
        
        Args:
            signal: Signal dict with market_id, rvr, roc, price, volume
        
        Returns:
            Trade decision dict or None if no trade
        """
        market_id = signal['market_id']
        market_name = signal['market_name']
        rvr = signal['rvr']
        roc = signal['roc']
        current_price = signal['price']
        volume = signal['volume']
        
        logger.info(f"\n📊 Evaluating signal: {market_name}")
        logger.info(f"   RVR: {rvr:.2f}x | ROC: {roc:+.1f}% | Price: {current_price:.1f}% | Vol: ${volume/1e6:.1f}M")
        
        # Determine direction based on ROC
        direction = "BUY" if roc > 0 else "SELL"
        
        # Estimate win probability based on signal strength
        # Strong RVR + Strong ROC = higher confidence
        rvr_score = min(rvr / 5.0, 1.0)  # Normalize RVR (5.0 = max)
        roc_score = min(abs(roc) / 20.0, 1.0)  # Normalize ROC (20% = max)
        
        win_prob = 0.50 + (rvr_score * 0.15) + (roc_score * 0.15)  # 50-80% range
        win_prob = min(win_prob, 0.75)  # Cap at 75% (never overconfident)
        
        # Calculate payout based on current price
        if direction == "BUY":
            payout = (100 - current_price) / current_price
        else:
            payout = current_price / (100 - current_price)
        
        # Kelly sizing
        kelly_fraction = self.calculate_kelly_size(win_prob, payout, current_price / 100)
        position_size = self.current_bankroll * kelly_fraction
        
        # Hard cap at $5 per trade (5% of $100)
        max_single_position = self.current_bankroll * self.max_position_pct
        position_size = min(position_size, max_single_position)
        
        if position_size < 1.0:
            logger.info(f"❌ Position too small: ${position_size:.2f} (skipping)")
            return None
        
        # Check exposure limits
        if not self.can_open_position(position_size):
            return None
        
        # Check circuit breaker
        if self.check_circuit_breaker():
            logger.critical("⛔ Circuit breaker active - no new trades!")
            return None
        
        # Calculate stop loss and take profit levels
        entry_price = current_price
        if direction == "BUY":
            stop_loss = entry_price * (1 - self.stop_loss_pct)
            take_profit_1 = entry_price * 1.20  # +20%
            take_profit_2 = entry_price * 1.30  # +30%
            take_profit_3 = entry_price * 1.50  # +50%
        else:
            stop_loss = entry_price * (1 + self.stop_loss_pct)
            take_profit_1 = entry_price * 0.80  # -20%
            take_profit_2 = entry_price * 0.70  # -30%
            take_profit_3 = entry_price * 0.50  # -50%
        
        trade_decision = {
            'market_id': market_id,
            'market_name': market_name,
            'direction': direction,
            'entry_price': entry_price,
            'position_size': position_size,
            'win_probability': win_prob,
            'rvr': rvr,
            'roc': roc,
            'volume': volume,
            'stop_loss': stop_loss,
            'take_profit_1': take_profit_1,
            'take_profit_2': take_profit_2,
            'take_profit_3': take_profit_3,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ TRADE APPROVED: {direction} ${position_size:.2f} @ {entry_price:.1f}%")
        logger.info(f"   Win Prob: {win_prob*100:.1f}% | Stop: {stop_loss:.1f}% | TP: {take_profit_1:.1f}%/{take_profit_2:.1f}%/{take_profit_3:.1f}%")
        
        return trade_decision
    
    
    def execute_trade(self, trade: Dict) -> bool:
        """
        Execute a trade on Polymarket
        
        Args:
            trade: Trade decision dict
        
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"\n🚀 EXECUTING TRADE:")
        logger.info(f"   Market: {trade['market_name']}")
        logger.info(f"   Direction: {trade['direction']}")
        logger.info(f"   Size: ${trade['position_size']:.2f}")
        logger.info(f"   Entry: {trade['entry_price']:.1f}%")
        
        # TODO: Implement actual Polymarket trade execution via Web3
        # For now, this is a placeholder that logs the trade
        
        # Store position
        self.positions.append(trade)
        self.total_exposure += trade['position_size']
        
        logger.info(f"✅ Trade executed successfully!")
        logger.info(f"   Total positions: {len(self.positions)}")
        logger.info(f"   Total exposure: ${self.total_exposure:.2f} ({self.total_exposure/self.current_bankroll*100:.1f}%)")
        
        return True
    
    
    def send_telegram_alert(self, trade: Dict):
        """Send trade alert via Telegram using OpenClaw"""
        message = f"""
🚨 TRADE EXECUTED

📊 Market: {trade['market_name']}
🎯 Direction: {trade['direction']}
💰 Size: ${trade['position_size']:.2f}
📈 Entry: {trade['entry_price']:.1f}%

📊 Signals:
   RVR: {trade['rvr']:.2f}x
   ROC: {trade['roc']:+.1f}%
   Volume: ${trade['volume']/1e6:.1f}M

🎲 Win Prob: {trade['win_probability']*100:.1f}%

🛡️ Risk Management:
   Stop Loss: {trade['stop_loss']:.1f}%
   Take Profit: {trade['take_profit_1']:.1f}% / {trade['take_profit_2']:.1f}% / {trade['take_profit_3']:.1f}%

💼 Portfolio:
   Bankroll: ${self.current_bankroll:.2f}
   Exposure: ${self.total_exposure:.2f} ({self.total_exposure/self.current_bankroll*100:.1f}%)
   Positions: {len(self.positions)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".strip()
        
        # Use OpenClaw message tool
        # This will be called from the main script
        return message
    
    
    def get_portfolio_status(self) -> Dict:
        """Get current portfolio status"""
        return {
            'bankroll': self.current_bankroll,
            'initial_bankroll': self.initial_bankroll,
            'total_pnl': self.current_bankroll - self.initial_bankroll,
            'total_pnl_pct': (self.current_bankroll - self.initial_bankroll) / self.initial_bankroll * 100,
            'total_exposure': self.total_exposure,
            'exposure_pct': self.total_exposure / self.current_bankroll * 100,
            'num_positions': len(self.positions),
            'positions': self.positions,
            'circuit_breaker_active': self.check_circuit_breaker()
        }


def main():
    """Test the trading executor"""
    # Test with dummy wallet key
    executor = TradingExecutor(wallet_key="DUMMY_KEY", bankroll=100.0)
    
    # Test signal evaluation
    test_signal = {
        'market_id': 'test-market-123',
        'market_name': 'Will Bitcoin hit $100k by March?',
        'rvr': 3.5,
        'roc': 12.3,
        'price': 67.5,
        'volume': 2_400_000
    }
    
    trade = executor.evaluate_signal(test_signal)
    
    if trade:
        executor.execute_trade(trade)
        alert = executor.send_telegram_alert(trade)
        print("\n" + "="*60)
        print("TELEGRAM ALERT:")
        print("="*60)
        print(alert)
        print("="*60)
    
    # Print portfolio status
    status = executor.get_portfolio_status()
    print(f"\n📊 PORTFOLIO STATUS:")
    print(f"   Bankroll: ${status['bankroll']:.2f}")
    print(f"   P&L: ${status['total_pnl']:+.2f} ({status['total_pnl_pct']:+.1f}%)")
    print(f"   Exposure: ${status['total_exposure']:.2f} ({status['exposure_pct']:.1f}%)")
    print(f"   Positions: {status['num_positions']}")


if __name__ == "__main__":
    main()
