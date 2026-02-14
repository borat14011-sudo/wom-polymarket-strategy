#!/usr/bin/env python3
"""
Simple Trade Logger - Forward testing with real data
Records: entry price, exit price, fees, slippage, resolution, time held
"""

import json
import csv
from datetime import datetime
from pathlib import Path

class TradeLogger:
    def __init__(self, log_file="trades.csv", journal_file="trading_journal.json"):
        self.log_file = Path(log_file)
        self.journal_file = Path(journal_file)
        
        # Initialize CSV if doesn't exist
        if not self.log_file.exists():
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'trade_id', 'market', 'position', 
                    'entry_price', 'exit_price', 'size_usd', 'size_shares',
                    'fees_paid', 'slippage_pct', 'resolution', 'pnl_usd',
                    'pnl_pct', 'time_held_days', 'notes'
                ])
        
        # Initialize journal if doesn't exist
        if not self.journal_file.exists():
            with open(self.journal_file, 'w') as f:
                json.dump({"trades": [], "summary": {}}, f, indent=2)
    
    def log_trade(self, **kwargs):
        """Log a new trade"""
        trade_data = {
            'timestamp': datetime.now().isoformat(),
            'trade_id': kwargs.get('trade_id', f"trade_{datetime.now().strftime('%Y%m%d_%H%M%S')}"),
            'market': kwargs.get('market', ''),
            'position': kwargs.get('position', ''),  # BUY/SELL, YES/NO
            'entry_price': float(kwargs.get('entry_price', 0)),
            'exit_price': float(kwargs.get('exit_price', 0)),
            'size_usd': float(kwargs.get('size_usd', 0)),
            'size_shares': float(kwargs.get('size_shares', 0)),
            'fees_paid': float(kwargs.get('fees_paid', 0)),
            'slippage_pct': float(kwargs.get('slippage_pct', 0)),
            'resolution': kwargs.get('resolution', 'open'),  # win/lose/open
            'pnl_usd': float(kwargs.get('pnl_usd', 0)),
            'pnl_pct': float(kwargs.get('pnl_pct', 0)),
            'time_held_days': float(kwargs.get('time_held_days', 0)),
            'notes': kwargs.get('notes', '')
        }
        
        # Append to CSV
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                trade_data['timestamp'],
                trade_data['trade_id'],
                trade_data['market'],
                trade_data['position'],
                trade_data['entry_price'],
                trade_data['exit_price'],
                trade_data['size_usd'],
                trade_data['size_shares'],
                trade_data['fees_paid'],
                trade_data['slippage_pct'],
                trade_data['resolution'],
                trade_data['pnl_usd'],
                trade_data['pnl_pct'],
                trade_data['time_held_days'],
                trade_data['notes']
            ])
        
        # Update journal
        with open(self.journal_file, 'r') as f:
            journal = json.load(f)
        
        journal['trades'].append(trade_data)
        
        # Update summary stats
        closed_trades = [t for t in journal['trades'] if t['resolution'] in ['win', 'lose']]
        if closed_trades:
            journal['summary'] = {
                'total_trades': len(closed_trades),
                'wins': len([t for t in closed_trades if t['pnl_usd'] > 0]),
                'losses': len([t for t in closed_trades if t['pnl_usd'] <= 0]),
                'win_rate': len([t for t in closed_trades if t['pnl_usd'] > 0]) / len(closed_trades) * 100,
                'total_pnl': sum(t['pnl_usd'] for t in closed_trades),
                'avg_win': sum(t['pnl_usd'] for t in closed_trades if t['pnl_usd'] > 0) / max(1, len([t for t in closed_trades if t['pnl_usd'] > 0])),
                'avg_loss': sum(t['pnl_usd'] for t in closed_trades if t['pnl_usd'] <= 0) / max(1, len([t for t in closed_trades if t['pnl_usd'] <= 0])),
                'largest_win': max([t['pnl_usd'] for t in closed_trades], default=0),
                'largest_loss': min([t['pnl_usd'] for t in closed_trades], default=0)
            }
        
        with open(self.journal_file, 'w') as f:
            json.dump(journal, f, indent=2)
        
        return trade_data
    
    def get_summary(self):
        """Get trading summary"""
        with open(self.journal_file, 'r') as f:
            journal = json.load(f)
        return journal['summary']
    
    def get_recent_trades(self, n=10):
        """Get recent trades"""
        with open(self.journal_file, 'r') as f:
            journal = json.load(f)
        return journal['trades'][-n:]

# Example usage
if __name__ == "__main__":
    logger = TradeLogger()
    
    # Example: Log a test trade
    test_trade = logger.log_trade(
        market="Will the U.S. collect less than $100b in revenue in 2025?",
        position="BUY NO",
        entry_price=0.137,
        size_usd=0.20,
        size_shares=1.46,
        fees_paid=0.004,  # 2% of $0.20
        slippage_pct=0.001,  # 0.1%
        notes="Manual test trade - API Cloudflare blocked"
    )
    
    print("Test trade logged:")
    print(json.dumps(test_trade, indent=2))
    
    print("\nCurrent summary:")
    print(json.dumps(logger.get_summary(), indent=2))