"""
Paper Trading Mode - Test the system without real money
Tracks signals and simulates trades to verify everything works
"""

import time
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('paper_trading.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PaperTrader:
    """Paper trading simulator - NO REAL MONEY"""
    
    def __init__(self, starting_balance: float = 100.0):
        self.starting_balance = starting_balance
        self.current_balance = starting_balance
        self.positions = []
        self.closed_trades = []
        self.trade_count = 0
        
        logger.info("="*60)
        logger.info("📝 PAPER TRADING MODE - NO REAL MONEY")
        logger.info("="*60)
        logger.info(f"Starting Balance: ${starting_balance:.2f}")
        logger.info("This will track what I WOULD trade")
        logger.info("="*60)
    
    
    def evaluate_opportunity(self, market: Dict) -> Dict:
        """
        Evaluate if we should enter this market (paper trade)
        
        Args:
            market: Dict with name, price, volume, signals
        
        Returns:
            Trade decision or None
        """
        # Example evaluation logic
        name = market.get('name', 'Unknown Market')
        price = market.get('price', 50.0)
        volume = market.get('volume', 0)
        rvr = market.get('rvr', 1.0)
        roc = market.get('roc', 0.0)
        
        # Determine if signals are strong enough
        if rvr < 2.5 or abs(roc) < 8.0:
            return None
        
        # Determine direction
        direction = "BUY" if roc > 0 else "SELL"
        
        # Calculate position size (5% max)
        position_size = self.current_balance * 0.05
        position_size = min(position_size, 5.0)  # Cap at $5
        
        # Calculate entry/exit
        entry_price = price
        if direction == "BUY":
            stop_loss = entry_price * 0.88  # -12%
            take_profit = entry_price * 1.30  # +30%
        else:
            stop_loss = entry_price * 1.12  # +12%
            take_profit = entry_price * 0.70  # -30%
        
        trade = {
            'id': self.trade_count,
            'market_name': name,
            'direction': direction,
            'entry_price': entry_price,
            'position_size': position_size,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'rvr': rvr,
            'roc': roc,
            'volume': volume,
            'entry_time': datetime.now().isoformat(),
            'status': 'OPEN'
        }
        
        self.trade_count += 1
        return trade
    
    
    def execute_paper_trade(self, trade: Dict):
        """Log a paper trade (simulated)"""
        logger.info(f"\n{'='*60}")
        logger.info(f"📝 PAPER TRADE #{trade['id']} (SIMULATED - NO REAL MONEY)")
        logger.info(f"{'='*60}")
        logger.info(f"Market: {trade['market_name']}")
        logger.info(f"Direction: {trade['direction']}")
        logger.info(f"Entry: {trade['entry_price']:.1f}%")
        logger.info(f"Position: ${trade['position_size']:.2f}")
        logger.info(f"Stop Loss: {trade['stop_loss']:.1f}%")
        logger.info(f"Take Profit: {trade['take_profit']:.1f}%")
        logger.info(f"\nSignals:")
        logger.info(f"  RVR: {trade['rvr']:.2f}x")
        logger.info(f"  ROC: {trade['roc']:+.1f}%")
        logger.info(f"  Volume: ${trade['volume']/1e6:.1f}M")
        logger.info(f"{'='*60}")
        
        self.positions.append(trade)
        
        return self.format_telegram_alert(trade)
    
    
    def format_telegram_alert(self, trade: Dict) -> str:
        """Format trade alert for Telegram"""
        return f"""
📝 PAPER TRADE (TEST MODE - NO REAL MONEY)

📊 Market: {trade['market_name']}
🎯 Direction: {trade['direction']}
💰 Position: ${trade['position_size']:.2f}
📈 Entry: {trade['entry_price']:.1f}%

📊 Signals:
   RVR: {trade['rvr']:.2f}x
   ROC: {trade['roc']:+.1f}%
   Volume: ${trade['volume']/1e6:.1f}M

🛡️ Risk Management:
   Stop Loss: {trade['stop_loss']:.1f}%
   Take Profit: {trade['take_profit']:.1f}%

💼 Paper Portfolio:
   Balance: ${self.current_balance:.2f}
   Open Positions: {len(self.positions)}

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ This is a SIMULATED trade - testing the system!
No real money involved.
""".strip()
    
    
    def get_status(self) -> Dict:
        """Get paper trading status"""
        return {
            'starting_balance': self.starting_balance,
            'current_balance': self.current_balance,
            'total_pnl': self.current_balance - self.starting_balance,
            'open_positions': len(self.positions),
            'closed_trades': len(self.closed_trades),
            'total_trades': self.trade_count
        }
    
    
    def print_summary(self):
        """Print paper trading summary"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("📝 PAPER TRADING SUMMARY")
        print("="*60)
        print(f"Starting Balance: ${status['starting_balance']:.2f}")
        print(f"Current Balance: ${status['current_balance']:.2f}")
        print(f"P&L: ${status['total_pnl']:+.2f}")
        print(f"\nTrades:")
        print(f"  Total: {status['total_trades']}")
        print(f"  Open: {status['open_positions']}")
        print(f"  Closed: {status['closed_trades']}")
        print("="*60)


def demo_paper_trade():
    """Demo the paper trading system with fake data"""
    trader = PaperTrader(starting_balance=100.0)
    
    # Simulate a strong signal
    fake_market = {
        'name': 'Will Bitcoin hit $100k by March?',
        'price': 67.5,
        'volume': 2_400_000,
        'rvr': 3.5,
        'roc': 12.3
    }
    
    print("\n🔍 Evaluating opportunity...")
    trade = trader.evaluate_opportunity(fake_market)
    
    if trade:
        print("✅ Trade approved!")
        alert = trader.execute_paper_trade(trade)
        
        print("\n" + "="*60)
        print("TELEGRAM ALERT (WHAT YOU'D SEE):")
        print("="*60)
        print(alert)
        print("="*60)
    else:
        print("❌ Trade rejected - signals not strong enough")
    
    # Print summary
    trader.print_summary()
    
    print("\n💡 This is PAPER TRADING - no real money involved!")
    print("Once you're comfortable, we'll switch to real trading.")


if __name__ == "__main__":
    demo_paper_trade()
