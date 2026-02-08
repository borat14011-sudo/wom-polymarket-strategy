#!/usr/bin/env python3
"""
Polymarket Trading Report Generator
====================================
Automated report generation system for trading performance analysis.

Usage:
    python report-generator.py --daily
    python report-generator.py --weekly
    python report-generator.py --monthly
    python report-generator.py --market BTC
    python report-generator.py --output report.html --email
"""

import argparse
import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import statistics
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Try to import optional dependencies
try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️  matplotlib not available, using ASCII charts")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    print("⚠️  reportlab not available, PDF generation disabled")


class TradingDataLoader:
    """Load trading data from database and logs"""
    
    def __init__(self, db_path: str = "polymarket_trading.db"):
        self.db_path = Path(db_path)
        
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def load_trades(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Load trades within date range"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM trades WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
            
        query += " ORDER BY timestamp ASC"
        
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            trades = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            # Table might not exist yet
            trades = []
        finally:
            conn.close()
            
        return trades
    
    def load_signals(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict]:
        """Load trading signals"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM signals WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())
            
        query += " ORDER BY timestamp ASC"
        
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            signals = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            signals = []
        finally:
            conn.close()
            
        return signals
    
    def load_positions(self) -> List[Dict]:
        """Load current positions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT * FROM positions WHERE quantity > 0")
            columns = [desc[0] for desc in cursor.description]
            positions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            positions = []
        finally:
            conn.close()
            
        return positions
    
    def load_market_data(self, market_slug: Optional[str] = None) -> List[Dict]:
        """Load market data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM market_snapshots WHERE 1=1"
        params = []
        
        if market_slug:
            query += " AND market_slug = ?"
            params.append(market_slug)
            
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            data = []
        finally:
            conn.close()
            
        return data


class PerformanceCalculator:
    """Calculate trading performance metrics"""
    
    @staticmethod
    def calculate_pnl(trades: List[Dict]) -> float:
        """Calculate total profit/loss"""
        return sum(trade.get('pnl', 0) for trade in trades)
    
    @staticmethod
    def calculate_returns(trades: List[Dict]) -> List[float]:
        """Calculate returns series"""
        if not trades:
            return []
        
        equity = 10000  # Starting equity
        returns = []
        
        for trade in trades:
            pnl = trade.get('pnl', 0)
            ret = pnl / equity if equity > 0 else 0
            returns.append(ret)
            equity += pnl
            
        return returns
    
    @staticmethod
    def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
        """Calculate Sharpe ratio (annualized)"""
        if not returns or len(returns) < 2:
            return 0.0
        
        mean_return = statistics.mean(returns)
        std_return = statistics.stdev(returns)
        
        if std_return == 0:
            return 0.0
        
        # Annualize (assume daily returns)
        sharpe = (mean_return - risk_free_rate) / std_return * math.sqrt(252)
        return sharpe
    
    @staticmethod
    def calculate_max_drawdown(trades: List[Dict]) -> Tuple[float, float]:
        """Calculate maximum drawdown (absolute and percentage)"""
        if not trades:
            return 0.0, 0.0
        
        equity = 10000
        peak = equity
        max_dd = 0.0
        max_dd_pct = 0.0
        
        for trade in trades:
            equity += trade.get('pnl', 0)
            if equity > peak:
                peak = equity
            
            dd = peak - equity
            dd_pct = (dd / peak * 100) if peak > 0 else 0
            
            if dd > max_dd:
                max_dd = dd
                max_dd_pct = dd_pct
        
        return max_dd, max_dd_pct
    
    @staticmethod
    def calculate_win_rate(trades: List[Dict]) -> Tuple[float, int, int]:
        """Calculate win rate and win/loss counts"""
        if not trades:
            return 0.0, 0, 0
        
        wins = sum(1 for t in trades if t.get('pnl', 0) > 0)
        losses = sum(1 for t in trades if t.get('pnl', 0) < 0)
        total = wins + losses
        
        win_rate = (wins / total * 100) if total > 0 else 0
        return win_rate, wins, losses
    
    @staticmethod
    def calculate_profit_factor(trades: List[Dict]) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        if not trades:
            return 0.0
        
        gross_profit = sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) > 0)
        gross_loss = abs(sum(t.get('pnl', 0) for t in trades if t.get('pnl', 0) < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss


class ChartGenerator:
    """Generate charts for reports"""
    
    def __init__(self, output_dir: Path = Path("reports/charts")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_equity_curve(self, trades: List[Dict], filename: str = "equity_curve.png") -> str:
        """Generate equity curve chart"""
        if HAS_MATPLOTLIB:
            return self._generate_equity_curve_mpl(trades, filename)
        else:
            return self._generate_equity_curve_ascii(trades)
    
    def _generate_equity_curve_mpl(self, trades: List[Dict], filename: str) -> str:
        """Generate equity curve using matplotlib"""
        equity = 10000
        equity_curve = [equity]
        timestamps = [datetime.now() - timedelta(days=len(trades))]
        
        for trade in trades:
            equity += trade.get('pnl', 0)
            equity_curve.append(equity)
            ts = trade.get('timestamp', '')
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts)
            timestamps.append(ts)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(timestamps, equity_curve, linewidth=2, color='#2E86AB')
        ax.fill_between(timestamps, equity_curve, 10000, alpha=0.3, color='#2E86AB')
        ax.axhline(y=10000, color='gray', linestyle='--', alpha=0.5, label='Starting Equity')
        
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Equity ($)', fontsize=12)
        ax.set_title('Equity Curve', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _generate_equity_curve_ascii(self, trades: List[Dict]) -> str:
        """Generate ASCII equity curve"""
        equity = 10000
        equity_points = [equity]
        
        for trade in trades:
            equity += trade.get('pnl', 0)
            equity_points.append(equity)
        
        # Simple ASCII chart
        min_eq = min(equity_points)
        max_eq = max(equity_points)
        height = 10
        
        chart = []
        chart.append("Equity Curve (ASCII)")
        chart.append("=" * 50)
        
        for i in range(height, -1, -1):
            line = f"{min_eq + (max_eq - min_eq) * i / height:>8.0f} |"
            for eq in equity_points:
                normalized = (eq - min_eq) / (max_eq - min_eq) * height if max_eq > min_eq else 0
                if abs(normalized - i) < 0.5:
                    line += "█"
                else:
                    line += " "
            chart.append(line)
        
        chart.append(" " * 9 + "+" + "-" * len(equity_points))
        return "\n".join(chart)
    
    def generate_pnl_by_market(self, trades: List[Dict], filename: str = "pnl_by_market.png") -> str:
        """Generate P&L by market chart"""
        if HAS_MATPLOTLIB:
            return self._generate_pnl_by_market_mpl(trades, filename)
        else:
            return self._generate_pnl_by_market_ascii(trades)
    
    def _generate_pnl_by_market_mpl(self, trades: List[Dict], filename: str) -> str:
        """Generate P&L by market using matplotlib"""
        # Aggregate P&L by market
        pnl_by_market = {}
        for trade in trades:
            market = trade.get('market_slug', 'Unknown')[:30]  # Truncate long names
            pnl = trade.get('pnl', 0)
            pnl_by_market[market] = pnl_by_market.get(market, 0) + pnl
        
        if not pnl_by_market:
            return ""
        
        # Sort by P&L
        sorted_markets = sorted(pnl_by_market.items(), key=lambda x: x[1], reverse=True)
        markets = [m[0] for m in sorted_markets[:15]]  # Top 15
        pnls = [m[1] for m in sorted_markets[:15]]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        colors = ['#06A77D' if p > 0 else '#D00000' for p in pnls]
        bars = ax.barh(markets, pnls, color=colors)
        
        ax.set_xlabel('P&L ($)', fontsize=12)
        ax.set_title('P&L by Market (Top 15)', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _generate_pnl_by_market_ascii(self, trades: List[Dict]) -> str:
        """Generate ASCII P&L by market"""
        pnl_by_market = {}
        for trade in trades:
            market = trade.get('market_slug', 'Unknown')[:20]
            pnl = trade.get('pnl', 0)
            pnl_by_market[market] = pnl_by_market.get(market, 0) + pnl
        
        chart = ["P&L by Market", "=" * 50]
        sorted_markets = sorted(pnl_by_market.items(), key=lambda x: x[1], reverse=True)[:10]
        
        for market, pnl in sorted_markets:
            bar_length = int(abs(pnl) / 10)
            bar = "█" * min(bar_length, 30)
            symbol = "+" if pnl > 0 else "-"
            chart.append(f"{market:20s} {symbol}{bar} ${pnl:>8.2f}")
        
        return "\n".join(chart)
    
    def generate_signal_distribution(self, signals: List[Dict], filename: str = "signal_distribution.png") -> str:
        """Generate signal distribution chart"""
        if HAS_MATPLOTLIB:
            return self._generate_signal_distribution_mpl(signals, filename)
        else:
            return self._generate_signal_distribution_ascii(signals)
    
    def _generate_signal_distribution_mpl(self, signals: List[Dict], filename: str) -> str:
        """Generate signal distribution using matplotlib"""
        signal_counts = {}
        for signal in signals:
            sig_type = signal.get('signal_type', 'Unknown')
            signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
        
        if not signal_counts:
            return ""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        labels = list(signal_counts.keys())
        sizes = list(signal_counts.values())
        colors = plt.cm.Set3(range(len(labels)))
        
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                            colors=colors, startangle=90)
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Signal Distribution', fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _generate_signal_distribution_ascii(self, signals: List[Dict]) -> str:
        """Generate ASCII signal distribution"""
        signal_counts = {}
        for signal in signals:
            sig_type = signal.get('signal_type', 'Unknown')
            signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
        
        total = sum(signal_counts.values())
        chart = ["Signal Distribution", "=" * 50]
        
        for sig_type, count in sorted(signal_counts.items(), key=lambda x: x[1], reverse=True):
            pct = count / total * 100 if total > 0 else 0
            bar = "█" * int(pct / 2)
            chart.append(f"{sig_type:20s} {bar} {count:>4d} ({pct:>5.1f}%)")
        
        return "\n".join(chart)
    
    def generate_hype_vs_price(self, market_data: List[Dict], filename: str = "hype_vs_price.png") -> str:
        """Generate hype vs price scatter plot"""
        if HAS_MATPLOTLIB:
            return self._generate_hype_vs_price_mpl(market_data, filename)
        else:
            return ""
    
    def _generate_hype_vs_price_mpl(self, market_data: List[Dict], filename: str) -> str:
        """Generate hype vs price scatter using matplotlib"""
        hype_scores = []
        prices = []
        
        for market in market_data:
            hype = market.get('hype_score', 0)
            price = market.get('price', 0)
            if hype > 0 and price > 0:
                hype_scores.append(hype)
                prices.append(price)
        
        if not hype_scores:
            return ""
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(hype_scores, prices, alpha=0.6, s=100, c='#FF6B35', edgecolors='black', linewidth=0.5)
        
        ax.set_xlabel('Hype Score', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.set_title('Hype vs Price', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filepath = self.output_dir / filename
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(filepath)


class ReportGenerator:
    """Main report generator class"""
    
    def __init__(self, db_path: str = "polymarket_trading.db"):
        self.data_loader = TradingDataLoader(db_path)
        self.calc = PerformanceCalculator()
        self.chart_gen = ChartGenerator()
        self.report_dir = Path("reports")
        self.report_dir.mkdir(exist_ok=True)
        
    def generate_daily(self, output_format: str = "html") -> str:
        """Generate daily report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        trades = self.data_loader.load_trades(start_date, end_date)
        signals = self.data_loader.load_signals(start_date, end_date)
        positions = self.data_loader.load_positions()
        
        report_data = self._build_report_data(trades, signals, positions, "Daily Report")
        
        return self._format_output(report_data, output_format, "daily_report")
    
    def generate_weekly(self, output_format: str = "html") -> str:
        """Generate weekly report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        trades = self.data_loader.load_trades(start_date, end_date)
        signals = self.data_loader.load_signals(start_date, end_date)
        positions = self.data_loader.load_positions()
        
        report_data = self._build_report_data(trades, signals, positions, "Weekly Report")
        
        return self._format_output(report_data, output_format, "weekly_report")
    
    def generate_monthly(self, output_format: str = "html") -> str:
        """Generate monthly report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        trades = self.data_loader.load_trades(start_date, end_date)
        signals = self.data_loader.load_signals(start_date, end_date)
        positions = self.data_loader.load_positions()
        
        report_data = self._build_report_data(trades, signals, positions, "Monthly Report")
        
        return self._format_output(report_data, output_format, "monthly_report")
    
    def generate_market_deepdive(self, market_slug: str, output_format: str = "html") -> str:
        """Generate market deep-dive report"""
        trades = [t for t in self.data_loader.load_trades() if t.get('market_slug') == market_slug]
        signals = [s for s in self.data_loader.load_signals() if s.get('market_slug') == market_slug]
        market_data = self.data_loader.load_market_data(market_slug)
        
        report_data = self._build_market_report_data(market_slug, trades, signals, market_data)
        
        return self._format_output(report_data, output_format, f"market_{market_slug}")
    
    def _build_report_data(self, trades: List[Dict], signals: List[Dict], 
                          positions: List[Dict], title: str) -> Dict:
        """Build report data structure"""
        # Performance metrics
        pnl = self.calc.calculate_pnl(trades)
        returns = self.calc.calculate_returns(trades)
        sharpe = self.calc.calculate_sharpe_ratio(returns)
        max_dd, max_dd_pct = self.calc.calculate_max_drawdown(trades)
        win_rate, wins, losses = self.calc.calculate_win_rate(trades)
        profit_factor = self.calc.calculate_profit_factor(trades)
        
        # Signal analysis
        signal_counts = {}
        for signal in signals:
            sig_type = signal.get('signal_type', 'Unknown')
            signal_counts[sig_type] = signal_counts.get(sig_type, 0) + 1
        
        # Market rankings
        market_pnl = {}
        for trade in trades:
            market = trade.get('market_slug', 'Unknown')
            market_pnl[market] = market_pnl.get(market, 0) + trade.get('pnl', 0)
        
        top_markets = sorted(market_pnl.items(), key=lambda x: x[1], reverse=True)[:10]
        worst_markets = sorted(market_pnl.items(), key=lambda x: x[1])[:10]
        
        # Risk assessment
        total_exposure = sum(pos.get('quantity', 0) * pos.get('avg_price', 0) for pos in positions)
        num_positions = len(positions)
        
        # Generate charts
        equity_chart = self.chart_gen.generate_equity_curve(trades)
        pnl_chart = self.chart_gen.generate_pnl_by_market(trades)
        signal_chart = self.chart_gen.generate_signal_distribution(signals)
        
        return {
            'title': title,
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_trades': len(trades),
                'total_signals': len(signals),
                'pnl': pnl,
                'win_rate': win_rate,
                'sharpe_ratio': sharpe
            },
            'performance': {
                'pnl': pnl,
                'returns': returns,
                'sharpe_ratio': sharpe,
                'max_drawdown': max_dd,
                'max_drawdown_pct': max_dd_pct,
                'win_rate': win_rate,
                'wins': wins,
                'losses': losses,
                'profit_factor': profit_factor,
                'total_trades': len(trades)
            },
            'signals': {
                'total': len(signals),
                'by_type': signal_counts,
                'chart': signal_chart
            },
            'markets': {
                'top_performers': top_markets,
                'worst_performers': worst_markets,
                'chart': pnl_chart
            },
            'risk': {
                'total_exposure': total_exposure,
                'num_positions': num_positions,
                'positions': positions
            },
            'charts': {
                'equity_curve': equity_chart,
                'pnl_by_market': pnl_chart,
                'signal_distribution': signal_chart
            },
            'recommendations': self._generate_recommendations(trades, signals, positions)
        }
    
    def _build_market_report_data(self, market_slug: str, trades: List[Dict], 
                                  signals: List[Dict], market_data: List[Dict]) -> Dict:
        """Build market deep-dive report data"""
        pnl = self.calc.calculate_pnl(trades)
        win_rate, wins, losses = self.calc.calculate_win_rate(trades)
        
        return {
            'title': f'Market Deep-Dive: {market_slug}',
            'timestamp': datetime.now().isoformat(),
            'market_slug': market_slug,
            'performance': {
                'pnl': pnl,
                'total_trades': len(trades),
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate
            },
            'signals': {
                'total': len(signals),
                'recent': signals[-10:] if signals else []
            },
            'market_data': market_data[-50:] if market_data else [],
            'recommendations': self._generate_market_recommendations(market_slug, trades, signals)
        }
    
    def _generate_recommendations(self, trades: List[Dict], signals: List[Dict], 
                                 positions: List[Dict]) -> List[str]:
        """Generate trading recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        pnl = self.calc.calculate_pnl(trades)
        if pnl < 0:
            recommendations.append("⚠️ Negative P&L - Review trading strategy and risk management")
        
        win_rate, _, _ = self.calc.calculate_win_rate(trades)
        if win_rate < 40:
            recommendations.append("📉 Low win rate - Consider tightening entry criteria")
        elif win_rate > 70:
            recommendations.append("✅ High win rate - Current strategy performing well")
        
        # Position-based recommendations
        if len(positions) > 20:
            recommendations.append("⚠️ High number of positions - Consider consolidation")
        elif len(positions) == 0:
            recommendations.append("💡 No open positions - Look for entry opportunities")
        
        # Signal-based recommendations
        if len(signals) < 5:
            recommendations.append("📊 Low signal activity - Market conditions may be unfavorable")
        
        if not recommendations:
            recommendations.append("✅ All systems nominal - Continue current strategy")
        
        return recommendations
    
    def _generate_market_recommendations(self, market_slug: str, trades: List[Dict], 
                                        signals: List[Dict]) -> List[str]:
        """Generate market-specific recommendations"""
        recommendations = []
        
        pnl = self.calc.calculate_pnl(trades)
        if pnl > 100:
            recommendations.append("✅ Strong performer - Consider increasing position size")
        elif pnl < -100:
            recommendations.append("⚠️ Poor performer - Reduce exposure or avoid")
        
        if len(trades) < 3:
            recommendations.append("📊 Limited trade history - Monitor for more data")
        
        return recommendations
    
    def _format_output(self, report_data: Dict, output_format: str, filename_base: str) -> str:
        """Format report in specified output format"""
        if output_format == "html":
            return self._format_html(report_data, filename_base)
        elif output_format == "json":
            return self._format_json(report_data, filename_base)
        elif output_format == "markdown":
            return self._format_markdown(report_data, filename_base)
        elif output_format == "pdf":
            return self._format_pdf(report_data, filename_base)
        else:
            raise ValueError(f"Unsupported format: {output_format}")
    
    def _format_html(self, report_data: Dict, filename_base: str) -> str:
        """Format report as HTML"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2E86AB 0%, #1B5C7A 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header .timestamp {{
            opacity: 0.9;
            font-size: 1rem;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .metric-label {{
            font-size: 0.85rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2rem;
            font-weight: 700;
            color: #2E86AB;
        }}
        .metric-value.positive {{ color: #06A77D; }}
        .metric-value.negative {{ color: #D00000; }}
        .section {{
            padding: 40px;
            border-bottom: 1px solid #eee;
        }}
        .section:last-child {{
            border-bottom: none;
        }}
        .section h2 {{
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: #2E86AB;
            border-left: 4px solid #2E86AB;
            padding-left: 15px;
        }}
        .chart-container {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .table th {{
            background: #2E86AB;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        .table td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        .table tr:hover {{
            background: #f8f9fa;
        }}
        .recommendations {{
            background: #FFF4E6;
            border-left: 4px solid #FF6B35;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .recommendations ul {{
            list-style: none;
            padding-left: 0;
        }}
        .recommendations li {{
            padding: 10px 0;
            font-size: 1.05rem;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
            font-size: 0.9rem;
        }}
        .positive {{ color: #06A77D; }}
        .negative {{ color: #D00000; }}
        .neutral {{ color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {report_data['title']}</h1>
            <div class="timestamp">Generated: {timestamp}</div>
        </div>
        
        <div class="summary">
            <div class="metric-card">
                <div class="metric-label">Total P&L</div>
                <div class="metric-value {'positive' if report_data['summary']['pnl'] > 0 else 'negative'}">
                    ${report_data['summary']['pnl']:.2f}
                </div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">{report_data['summary']['total_trades']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{report_data['summary']['win_rate']:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sharpe Ratio</div>
                <div class="metric-value">{report_data['summary']['sharpe_ratio']:.2f}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Performance Metrics</h2>
            <table class="table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total P&L</td>
                    <td class="{'positive' if report_data['performance']['pnl'] > 0 else 'negative'}">
                        ${report_data['performance']['pnl']:.2f}
                    </td>
                </tr>
                <tr>
                    <td>Sharpe Ratio</td>
                    <td>{report_data['performance']['sharpe_ratio']:.3f}</td>
                </tr>
                <tr>
                    <td>Max Drawdown</td>
                    <td class="negative">${report_data['performance']['max_drawdown']:.2f} ({report_data['performance']['max_drawdown_pct']:.1f}%)</td>
                </tr>
                <tr>
                    <td>Win Rate</td>
                    <td>{report_data['performance']['win_rate']:.1f}% ({report_data['performance']['wins']}W / {report_data['performance']['losses']}L)</td>
                </tr>
                <tr>
                    <td>Profit Factor</td>
                    <td>{report_data['performance']['profit_factor']:.2f}</td>
                </tr>
            </table>
            
            <div class="chart-container">
                {'<img src="' + report_data['charts']['equity_curve'] + '" alt="Equity Curve">' if report_data['charts']['equity_curve'] and HAS_MATPLOTLIB else '<pre>' + report_data['charts']['equity_curve'] + '</pre>'}
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Signal Analysis</h2>
            <p>Total Signals: <strong>{report_data['signals']['total']}</strong></p>
            <table class="table">
                <tr>
                    <th>Signal Type</th>
                    <th>Count</th>
                </tr>
"""
        
        for sig_type, count in report_data['signals']['by_type'].items():
            html += f"""
                <tr>
                    <td>{sig_type}</td>
                    <td>{count}</td>
                </tr>
"""
        
        html += """
            </table>
        </div>
        
        <div class="section">
            <h2>🏆 Market Rankings</h2>
            <h3>Top Performers</h3>
            <table class="table">
                <tr>
                    <th>Market</th>
                    <th>P&L</th>
                </tr>
"""
        
        for market, pnl in report_data['markets']['top_performers']:
            html += f"""
                <tr>
                    <td>{market}</td>
                    <td class="{'positive' if pnl > 0 else 'negative'}">${pnl:.2f}</td>
                </tr>
"""
        
        html += """
            </table>
            
            <div class="chart-container">
"""
        
        if report_data['charts']['pnl_by_market'] and HAS_MATPLOTLIB:
            html += f'<img src="{report_data["charts"]["pnl_by_market"]}" alt="P&L by Market">'
        
        html += """
            </div>
        </div>
        
        <div class="section">
            <h2>⚠️ Risk Assessment</h2>
            <table class="table">
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Total Exposure</td>
                    <td>${:.2f}</td>
                </tr>
                <tr>
                    <td>Open Positions</td>
                    <td>{}</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>💡 Recommendations</h2>
            <div class="recommendations">
                <ul>
""".format(report_data['risk']['total_exposure'], report_data['risk']['num_positions'])
        
        for rec in report_data['recommendations']:
            html += f"                    <li>{rec}</li>\n"
        
        html += """
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by Polymarket Trading Report Generator</p>
            <p>Great success! 🚀</p>
        </div>
    </div>
</body>
</html>"""
        
        filepath = self.report_dir / f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return str(filepath)
    
    def _format_json(self, report_data: Dict, filename_base: str) -> str:
        """Format report as JSON"""
        filepath = self.report_dir / f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Remove chart paths for JSON (not serializable in useful way)
        clean_data = report_data.copy()
        clean_data.pop('charts', None)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(clean_data, f, indent=2)
        
        return str(filepath)
    
    def _format_markdown(self, report_data: Dict, filename_base: str) -> str:
        """Format report as Markdown"""
        md = f"""# {report_data['title']}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Executive Summary

- **Total P&L:** ${report_data['summary']['pnl']:.2f}
- **Total Trades:** {report_data['summary']['total_trades']}
- **Win Rate:** {report_data['summary']['win_rate']:.1f}%
- **Sharpe Ratio:** {report_data['summary']['sharpe_ratio']:.2f}

---

## 📈 Performance Metrics

| Metric | Value |
|--------|-------|
| Total P&L | ${report_data['performance']['pnl']:.2f} |
| Sharpe Ratio | {report_data['performance']['sharpe_ratio']:.3f} |
| Max Drawdown | ${report_data['performance']['max_drawdown']:.2f} ({report_data['performance']['max_drawdown_pct']:.1f}%) |
| Win Rate | {report_data['performance']['win_rate']:.1f}% ({report_data['performance']['wins']}W / {report_data['performance']['losses']}L) |
| Profit Factor | {report_data['performance']['profit_factor']:.2f} |

---

## 🎯 Signal Analysis

**Total Signals:** {report_data['signals']['total']}

### Signal Distribution

"""
        
        for sig_type, count in report_data['signals']['by_type'].items():
            md += f"- **{sig_type}:** {count}\n"
        
        md += f"""
---

## 🏆 Top Performing Markets

"""
        
        for market, pnl in report_data['markets']['top_performers']:
            symbol = "+" if pnl > 0 else ""
            md += f"- **{market}:** {symbol}${pnl:.2f}\n"
        
        md += f"""
---

## ⚠️ Risk Assessment

- **Total Exposure:** ${report_data['risk']['total_exposure']:.2f}
- **Open Positions:** {report_data['risk']['num_positions']}

---

## 💡 Recommendations

"""
        
        for rec in report_data['recommendations']:
            md += f"- {rec}\n"
        
        md += "\n---\n\n*Generated by Polymarket Trading Report Generator - Great success! 🚀*\n"
        
        filepath = self.report_dir / f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
        
        return str(filepath)
    
    def _format_pdf(self, report_data: Dict, filename_base: str) -> str:
        """Format report as PDF"""
        if not HAS_REPORTLAB:
            print("⚠️  PDF generation requires reportlab. Install with: pip install reportlab")
            return ""
        
        filepath = self.report_dir / f"{filename_base}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(report_data['title'], title_style))
        story.append(Spacer(1, 12))
        
        # Timestamp
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                              styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total P&L', f"${report_data['summary']['pnl']:.2f}"],
            ['Total Trades', str(report_data['summary']['total_trades'])],
            ['Win Rate', f"{report_data['summary']['win_rate']:.1f}%"],
            ['Sharpe Ratio', f"{report_data['summary']['sharpe_ratio']:.2f}"]
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Add charts if available
        if report_data['charts']['equity_curve'] and HAS_MATPLOTLIB:
            story.append(Paragraph("Equity Curve", styles['Heading2']))
            story.append(Image(report_data['charts']['equity_curve'], width=6*inch, height=3*inch))
            story.append(Spacer(1, 20))
        
        # Recommendations
        story.append(Paragraph("Recommendations", styles['Heading2']))
        for rec in report_data['recommendations']:
            story.append(Paragraph(f"• {rec}", styles['Normal']))
            story.append(Spacer(1, 6))
        
        doc.build(story)
        return str(filepath)
    
    def save(self, filepath: str, content: str = None):
        """Save report to file"""
        if content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        print(f"✅ Report saved to: {filepath}")
    
    def email_report(self, filepath: str, to: str, subject: str = None):
        """Email report (requires SMTP configuration)"""
        # This is a placeholder - you'll need to configure SMTP settings
        print(f"📧 Email functionality requires SMTP configuration")
        print(f"   Would send {filepath} to {to}")
        print(f"   Configure SMTP settings in config.json or environment variables")
        
        # Example implementation:
        # smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        # smtp_port = int(os.getenv('SMTP_PORT', '587'))
        # smtp_user = os.getenv('SMTP_USER')
        # smtp_pass = os.getenv('SMTP_PASS')
        # 
        # msg = MIMEMultipart()
        # msg['From'] = smtp_user
        # msg['To'] = to
        # msg['Subject'] = subject or f"Trading Report - {datetime.now().strftime('%Y-%m-%d')}"
        # 
        # with open(filepath, 'rb') as f:
        #     attachment = MIMEBase('application', 'octet-stream')
        #     attachment.set_payload(f.read())
        #     encoders.encode_base64(attachment)
        #     attachment.add_header('Content-Disposition', f'attachment; filename={Path(filepath).name}')
        #     msg.attach(attachment)
        # 
        # server = smtplib.SMTP(smtp_server, smtp_port)
        # server.starttls()
        # server.login(smtp_user, smtp_pass)
        # server.send_message(msg)
        # server.quit()


def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description='Polymarket Trading Report Generator')
    
    # Report types
    parser.add_argument('--daily', action='store_true', help='Generate daily report')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly report')
    parser.add_argument('--monthly', action='store_true', help='Generate monthly report')
    parser.add_argument('--market', type=str, help='Generate market deep-dive for specified market')
    
    # Output options
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--format', type=str, choices=['html', 'pdf', 'markdown', 'json'], 
                       default='html', help='Output format (default: html)')
    parser.add_argument('--email', type=str, help='Email address to send report to')
    
    # Database
    parser.add_argument('--db', type=str, default='polymarket_trading.db', 
                       help='Database path (default: polymarket_trading.db)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.daily, args.weekly, args.monthly, args.market]):
        parser.error("Must specify report type: --daily, --weekly, --monthly, or --market")
    
    # Initialize generator
    generator = ReportGenerator(db_path=args.db)
    
    # Generate report
    try:
        if args.daily:
            print("📊 Generating daily report...")
            output_path = generator.generate_daily(output_format=args.format)
        elif args.weekly:
            print("📊 Generating weekly report...")
            output_path = generator.generate_weekly(output_format=args.format)
        elif args.monthly:
            print("📊 Generating monthly report...")
            output_path = generator.generate_monthly(output_format=args.format)
        elif args.market:
            print(f"📊 Generating market deep-dive for {args.market}...")
            output_path = generator.generate_market_deepdive(args.market, output_format=args.format)
        
        print(f"✅ Report generated: {output_path}")
        
        # Copy to specified output if provided
        if args.output:
            import shutil
            shutil.copy(output_path, args.output)
            print(f"✅ Report copied to: {args.output}")
        
        # Email if requested
        if args.email:
            generator.email_report(output_path, args.email)
        
        print("\n🚀 Great success!")
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
