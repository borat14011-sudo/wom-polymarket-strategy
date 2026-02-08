"""
Daily Reporter
Generates comprehensive P&L and performance reports
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict
import logging

logger = logging.getLogger(__name__)

DB_PATH = "polymarket_data.db"
STARTING_BANKROLL = 100.0


class DailyReporter:
    """Generates daily performance reports"""
    
    def __init__(self):
        """Initialize reporter"""
        pass
    
    def generate_daily_report(self):
        """Generate and send daily performance report"""
        logger.info("Generating daily report...")
        
        stats = self._get_portfolio_stats()
        
        if stats['total_trades'] == 0:
            logger.info("No trades yet, skipping report")
            return
        
        report = self._format_daily_report(stats)
        
        # Send via Telegram
        self._send_report(report)
        
        # Save to validation_metrics
        self._save_daily_metrics(stats)
        
        logger.info("Daily report sent successfully")
    
    def _get_portfolio_stats(self) -> Dict:
        """Calculate all portfolio statistics"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute("SELECT COUNT(*) FROM paper_trades")
        total_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status = 'OPEN'")
        open_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status != 'OPEN'")
        closed_trades = cursor.fetchone()[0]
        
        # P&L stats
        cursor.execute("SELECT SUM(pnl_dollars) FROM paper_trades WHERE status != 'OPEN'")
        total_pnl = cursor.fetchone()[0] or 0.0
        
        current_bankroll = STARTING_BANKROLL + total_pnl
        
        # Win rate (resolved only)
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE resolved = 1")
        resolved_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE trade_correct = 1")
        winning_trades = cursor.fetchone()[0]
        
        win_rate = (winning_trades / resolved_trades * 100) if resolved_trades > 0 else 0
        
        # ROI stats
        cursor.execute("""
            SELECT AVG(pnl_percent), MAX(pnl_percent), MIN(pnl_percent)
            FROM paper_trades
            WHERE status != 'OPEN' AND pnl_percent IS NOT NULL
        """)
        row = cursor.fetchone()
        avg_roi = row[0] or 0
        best_trade = row[1] or 0
        worst_trade = row[2] or 0
        
        # Side breakdown
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as wins
            FROM paper_trades
            WHERE side = 'YES' AND resolved = 1
        """)
        yes_total, yes_wins = cursor.fetchone()
        yes_win_rate = (yes_wins / yes_total * 100) if yes_total else 0
        
        cursor.execute("""
            SELECT COUNT(*) as total, 
                   SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as wins
            FROM paper_trades
            WHERE side = 'NO' AND resolved = 1
        """)
        no_total, no_wins = cursor.fetchone()
        no_win_rate = (no_wins / no_total * 100) if no_total else 0
        
        # Exposure
        cursor.execute("SELECT SUM(position_size) FROM paper_trades WHERE status = 'OPEN'")
        total_exposure = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            'total_trades': total_trades,
            'open_trades': open_trades,
            'closed_trades': closed_trades,
            'resolved_trades': resolved_trades,
            'total_pnl': total_pnl,
            'total_pnl_pct': (total_pnl / STARTING_BANKROLL * 100),
            'current_bankroll': current_bankroll,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'avg_roi': avg_roi,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'yes_win_rate': yes_win_rate,
            'no_win_rate': no_win_rate,
            'yes_total': yes_total or 0,
            'no_total': no_total or 0,
            'total_exposure': total_exposure,
            'exposure_pct': (total_exposure / current_bankroll * 100) if current_bankroll > 0 else 0
        }
    
    def _format_daily_report(self, stats: Dict) -> str:
        """Format daily report message"""
        
        # Calculate days running
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(entry_time) FROM paper_trades")
        first_trade_time = cursor.fetchone()[0]
        conn.close()
        
        if first_trade_time:
            days_running = (datetime.now().timestamp() - first_trade_time) / 86400
        else:
            days_running = 0
        
        # Win rate indicator
        if stats['win_rate'] >= 60:
            wr_indicator = "🔥"
        elif stats['win_rate'] >= 55:
            wr_indicator = "✅"
        elif stats['win_rate'] >= 50:
            wr_indicator = "⚠️"
        else:
            wr_indicator = "❌"
        
        # P&L indicator
        if stats['total_pnl'] > 0:
            pnl_indicator = "📈"
        else:
            pnl_indicator = "📉"
        
        report = f"""
📊 DAILY PAPER TRADING REPORT

💰 Portfolio Status:
   Starting: ${STARTING_BANKROLL:.2f}
   Current: ${stats['current_bankroll']:.2f}
   {pnl_indicator} Total P&L: ${stats['total_pnl']:+.2f} ({stats['total_pnl_pct']:+.1f}%)

📈 Trade Statistics ({int(days_running)} days):
   Total Trades: {stats['total_trades']}
   Resolved: {stats['resolved_trades']}
   Open: {stats['open_trades']}
   
   {wr_indicator} Win Rate: {stats['win_rate']:.1f}% ({stats['winning_trades']}/{stats['resolved_trades']})
   Avg ROI: {stats['avg_roi']:+.1f}%
   Best: {stats['best_trade']:+.1f}%
   Worst: {stats['worst_trade']:+.1f}%

🎯 Strategy Breakdown:
   YES Side: {stats['yes_win_rate']:.1f}% ({stats['yes_total']} trades)
   NO Side: {stats['no_win_rate']:.1f}% ({stats['no_total']} trades)

💼 Current Exposure:
   Open Positions: {stats['open_trades']}
   Total Exposure: ${stats['total_exposure']:.2f} ({stats['exposure_pct']:.1f}%)

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ PAPER TRADING - Validating strategy before real money!
""".strip()
        
        # Add go-live assessment if enough data
        if stats['resolved_trades'] >= 20 and days_running >= 30:
            report += "\n\n" + self._generate_golive_assessment(stats)
        
        return report
    
    def _generate_golive_assessment(self, stats: Dict) -> str:
        """Generate go-live recommendation"""
        
        passed = 0
        total = 5
        
        criteria = []
        
        # 1. Win rate >= 55%
        if stats['win_rate'] >= 55:
            criteria.append("✅ Win Rate >= 55%")
            passed += 1
        else:
            criteria.append(f"❌ Win Rate: {stats['win_rate']:.1f}% (need 55%+)")
        
        # 2. Positive P&L
        if stats['total_pnl'] > 0:
            criteria.append("✅ Positive Total P&L")
            passed += 1
        else:
            criteria.append(f"❌ Negative P&L: ${stats['total_pnl']:.2f}")
        
        # 3. 20+ resolved trades
        if stats['resolved_trades'] >= 20:
            criteria.append("✅ 20+ Resolved Trades")
            passed += 1
        else:
            criteria.append(f"❌ Only {stats['resolved_trades']} resolved (need 20+)")
        
        # 4. 30+ days
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT MIN(entry_time) FROM paper_trades")
        first_trade_time = cursor.fetchone()[0]
        conn.close()
        
        if first_trade_time:
            days_running = (datetime.now().timestamp() - first_trade_time) / 86400
            if days_running >= 30:
                criteria.append("✅ 30+ Days Testing")
                passed += 1
            else:
                criteria.append(f"❌ Only {int(days_running)} days (need 30+)")
        else:
            criteria.append("❌ No trading history")
        
        # 5. Consistent performance (no extreme drawdowns)
        if stats['worst_trade'] > -20:
            criteria.append("✅ No Extreme Losses")
            passed += 1
        else:
            criteria.append(f"⚠️ Worst trade: {stats['worst_trade']:.1f}%")
        
        # Generate recommendation
        if passed == total:
            recommendation = "🚀 APPROVED FOR GO-LIVE"
        elif passed >= 4:
            recommendation = "⚠️ PROCEED WITH CAUTION"
        else:
            recommendation = "❌ NOT READY - Continue Testing"
        
        assessment = f"""
🚦 GO-LIVE ASSESSMENT

Criteria ({passed}/{total} passed):
{chr(10).join(criteria)}

Recommendation: {recommendation}
"""
        
        return assessment
    
    def _send_report(self, report: str):
        """Send report via Telegram"""
        try:
            from telegram_alerter import send_alert
            send_alert(report)
        except Exception as e:
            logger.error(f"Error sending report: {e}")
            print(report)  # Print to console as fallback
    
    def _save_daily_metrics(self, stats: Dict):
        """Save daily metrics snapshot"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute("""
            INSERT OR REPLACE INTO validation_metrics
            (snapshot_date, total_trades, total_resolved, total_open,
             win_rate, avg_roi, total_pnl,
             yes_side_win_rate, no_side_win_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            today,
            stats['total_trades'],
            stats['resolved_trades'],
            stats['open_trades'],
            stats['win_rate'],
            stats['avg_roi'],
            stats['total_pnl'],
            stats['yes_win_rate'],
            stats['no_win_rate']
        ))
        
        conn.commit()
        conn.close()


def main():
    """Generate and send daily report"""
    logging.basicConfig(level=logging.INFO)
    
    reporter = DailyReporter()
    reporter.generate_daily_report()


if __name__ == "__main__":
    main()
