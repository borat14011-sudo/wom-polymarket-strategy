"""
RVR Strategy Backtesting with Multiple Volume Spike Thresholds

Tests RVR strategy across different volume spike thresholds:
- 1.5x, 2.0x, 2.5x, 3.0x, 4.0x

Entry: RVR spike + ROC > 10%
Exit: 12% stop-loss OR tiered take-profits (+20%, +30%, +50%)
"""

import requests
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Trade:
    """Represents a single trade"""
    def __init__(self, market_id, market_name, entry_price, entry_time, rvr, roc, threshold):
        self.market_id = market_id
        self.market_name = market_name
        self.entry_price = entry_price
        self.entry_time = entry_time
        self.rvr = rvr
        self.roc = roc
        self.threshold = threshold
        self.exit_price = None
        self.exit_time = None
        self.exit_reason = None
        self.return_pct = None
        self.peak_price = entry_price
        self.lowest_price = entry_price
        
    def update_price(self, price):
        """Track peak and lowest prices for drawdown analysis"""
        self.peak_price = max(self.peak_price, price)
        self.lowest_price = min(self.lowest_price, price)
        
    def close(self, exit_price, exit_time, reason):
        """Close the trade"""
        self.exit_price = exit_price
        self.exit_time = exit_time
        self.exit_reason = reason
        
        # Calculate return percentage
        # For binary prediction markets, we assume buying "Yes" tokens
        # Return = (exit_price - entry_price) / entry_price * 100
        self.return_pct = ((exit_price - self.entry_price) / self.entry_price) * 100
        
    def is_profitable(self):
        """Check if trade is profitable"""
        return self.return_pct > 0 if self.return_pct is not None else False


class BacktestEngine:
    """Backtesting engine for RVR strategy"""
    
    def __init__(self, threshold):
        self.threshold = threshold
        self.roc_threshold = 10.0  # ROC > 10%
        self.stop_loss = -12.0  # -12% stop loss
        self.take_profits = [20.0, 30.0, 50.0]  # Tiered take profits
        
        self.trades = []
        self.open_trades = {}  # market_id -> Trade
        self.max_drawdown = 0.0
        self.equity_curve = []
        self.initial_capital = 10000  # Starting with $10k
        self.current_capital = self.initial_capital
        
    def calculate_rvr(self, current_volume, historical_volumes):
        """Calculate Relative Volume Ratio"""
        if not historical_volumes or len(historical_volumes) == 0:
            return 0.0
        
        avg_volume = sum(historical_volumes) / len(historical_volumes)
        if avg_volume == 0:
            return 0.0
        
        return current_volume / avg_volume
    
    def calculate_roc(self, current_price, past_price):
        """Calculate Rate of Change"""
        if past_price == 0:
            return 0.0
        
        return ((current_price - past_price) / past_price) * 100
    
    def check_entry_signal(self, market_data, historical_data):
        """Check if entry conditions are met"""
        market_id = market_data['id']
        
        current_volume = market_data.get('volume24hr', 0)
        current_price = market_data.get('price', 0.5)
        
        # Need at least 12 hours of historical data
        if len(historical_data) < 12:
            return False, 0.0, 0.0
        
        # Don't open duplicate positions
        if market_id in self.open_trades:
            return False, 0.0, 0.0
        
        # Calculate RVR (using last 24 data points as historical baseline)
        historical_volumes = [d.get('volume24hr', 0) for d in historical_data[-24:]]
        rvr = self.calculate_rvr(current_volume, historical_volumes)
        
        # Calculate ROC (12 hours ago)
        price_12h_ago = historical_data[-12].get('price', current_price)
        roc = self.calculate_roc(current_price, price_12h_ago)
        
        # Entry signal: RVR >= threshold AND abs(ROC) >= 10%
        if rvr >= self.threshold and abs(roc) >= self.roc_threshold:
            return True, rvr, roc
        
        return False, rvr, roc
    
    def check_exit_signal(self, trade, current_price):
        """Check if exit conditions are met"""
        return_pct = ((current_price - trade.entry_price) / trade.entry_price) * 100
        
        # Stop loss
        if return_pct <= self.stop_loss:
            return True, "Stop Loss"
        
        # Tiered take profits
        for tp_level in self.take_profits:
            if return_pct >= tp_level:
                return True, f"Take Profit {tp_level}%"
        
        return False, None
    
    def open_trade(self, market_data, timestamp, rvr, roc):
        """Open a new trade"""
        market_id = market_data['id']
        market_name = market_data.get('question', 'Unknown')
        price = market_data.get('price', 0.5)
        
        trade = Trade(market_id, market_name, price, timestamp, rvr, roc, self.threshold)
        self.open_trades[market_id] = trade
        
        logger.info(f"[{self.threshold}x] ENTRY: {market_name[:40]}... @ {price:.3f} | RVR: {rvr:.2f} | ROC: {roc:+.1f}%")
        
    def close_trade(self, market_id, exit_price, timestamp, reason):
        """Close an open trade"""
        if market_id not in self.open_trades:
            return
        
        trade = self.open_trades[market_id]
        trade.close(exit_price, timestamp, reason)
        
        # Update capital
        position_size = 1000  # $1000 per trade
        pnl = position_size * (trade.return_pct / 100)
        self.current_capital += pnl
        
        # Track equity
        self.equity_curve.append({
            'timestamp': timestamp,
            'capital': self.current_capital
        })
        
        # Update max drawdown
        peak_capital = max([e['capital'] for e in self.equity_curve] + [self.initial_capital])
        drawdown = ((self.current_capital - peak_capital) / peak_capital) * 100
        self.max_drawdown = min(self.max_drawdown, drawdown)
        
        self.trades.append(trade)
        del self.open_trades[market_id]
        
        profit_emoji = "✅" if trade.is_profitable() else "❌"
        logger.info(f"[{self.threshold}x] EXIT: {trade.market_name[:40]}... @ {exit_price:.3f} | {trade.exit_reason} | Return: {trade.return_pct:+.1f}% {profit_emoji}")
    
    def update_open_trades(self, market_data, timestamp):
        """Update all open trades and check for exits"""
        market_id = market_data['id']
        
        if market_id not in self.open_trades:
            return
        
        trade = self.open_trades[market_id]
        current_price = market_data.get('price', trade.entry_price)
        
        # Update peak/lowest tracking
        trade.update_price(current_price)
        
        # Check exit conditions
        should_exit, exit_reason = self.check_exit_signal(trade, current_price)
        
        if should_exit:
            self.close_trade(market_id, current_price, timestamp, exit_reason)
    
    def get_statistics(self):
        """Calculate backtest statistics"""
        if not self.trades:
            return {
                'threshold': self.threshold,
                'total_trades': 0,
                'win_rate': 0.0,
                'avg_return': 0.0,
                'max_drawdown': 0.0,
                'total_return': 0.0,
                'profitable_trades': 0,
                'losing_trades': 0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'best_trade': None,
                'worst_trade': None
            }
        
        profitable_trades = [t for t in self.trades if t.is_profitable()]
        losing_trades = [t for t in self.trades if not t.is_profitable()]
        
        total_trades = len(self.trades)
        win_rate = (len(profitable_trades) / total_trades) * 100 if total_trades > 0 else 0.0
        
        avg_return = sum([t.return_pct for t in self.trades]) / total_trades
        
        avg_win = sum([t.return_pct for t in profitable_trades]) / len(profitable_trades) if profitable_trades else 0.0
        avg_loss = sum([t.return_pct for t in losing_trades]) / len(losing_trades) if losing_trades else 0.0
        
        best_trade = max(self.trades, key=lambda t: t.return_pct)
        worst_trade = min(self.trades, key=lambda t: t.return_pct)
        
        total_return = ((self.current_capital - self.initial_capital) / self.initial_capital) * 100
        
        return {
            'threshold': self.threshold,
            'total_trades': total_trades,
            'win_rate': win_rate,
            'avg_return': avg_return,
            'max_drawdown': self.max_drawdown,
            'total_return': total_return,
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'best_trade': best_trade,
            'worst_trade': worst_trade,
            'final_capital': self.current_capital
        }


def fetch_market_events(market_id, days_back=30):
    """
    Fetch historical market events from Polymarket Gamma API
    
    This is a simplified version - in production, you'd want to use
    the actual historical data endpoints if available
    """
    try:
        url = f"https://gamma-api.polymarket.com/markets/{market_id}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching market {market_id}: {e}")
        return None


def fetch_top_markets(limit=20):
    """Fetch top markets by volume"""
    try:
        url = "https://gamma-api.polymarket.com/markets"
        params = {
            "limit": limit,
            "closed": "false",
            "order": "volume24hr",
            "ascending": "false"
        }
        headers = {"User-Agent": "Mozilla/5.0"}
        
        logger.info(f"Fetching top {limit} markets...")
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        markets = response.json()
        logger.info(f"Fetched {len(markets)} markets")
        
        return markets
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        return []


def simulate_historical_data(market, days=30):
    """
    Simulate historical price/volume data for backtesting
    
    In a real implementation, you would:
    1. Use Polymarket's historical data API
    2. Or collect real data over time
    3. Or use cached historical data
    
    This creates synthetic but realistic data based on current market state
    """
    import random
    
    # Parse outcome prices - can be string or list
    outcome_prices = market.get('outcomePrices', ['0.5'])
    if isinstance(outcome_prices, str):
        # If it's a JSON string, parse it
        import json
        try:
            outcome_prices = json.loads(outcome_prices)
        except:
            outcome_prices = ['0.5']
    
    # Get first outcome price
    if isinstance(outcome_prices, list) and len(outcome_prices) > 0:
        try:
            current_price = float(outcome_prices[0])
        except (ValueError, TypeError):
            current_price = 0.5
    else:
        current_price = 0.5
    
    # Parse volume
    try:
        current_volume = float(market.get('volume24hr', 0))
    except (ValueError, TypeError):
        current_volume = 1000.0  # Default volume
    
    # Generate hourly data for the past N days
    hours = days * 24
    historical_data = []
    
    timestamp = datetime.now() - timedelta(days=days)
    
    # Start with a random price in the past
    price = max(0.1, min(0.9, current_price + random.uniform(-0.2, 0.2)))
    volume = current_volume * random.uniform(0.5, 1.5)
    
    for hour in range(hours):
        # Simulate price movement (random walk with mean reversion)
        price_change = random.gauss(0, 0.02)  # 2% std dev
        price = max(0.05, min(0.95, price + price_change))
        
        # Simulate volume (with occasional spikes)
        if random.random() < 0.05:  # 5% chance of volume spike
            volume = volume * random.uniform(2.0, 5.0)
        else:
            volume = max(0, volume * random.uniform(0.8, 1.2))
        
        historical_data.append({
            'timestamp': timestamp + timedelta(hours=hour),
            'price': price,
            'volume24hr': volume,
            'id': market.get('conditionId', market.get('id'))
        })
    
    # Ensure the last data point matches current state
    historical_data[-1]['price'] = current_price
    historical_data[-1]['volume24hr'] = current_volume
    
    return historical_data


def run_backtest(thresholds=[1.5, 2.0, 2.5, 3.0, 4.0], days_back=30):
    """
    Run backtests for multiple RVR thresholds
    """
    logger.info("=" * 80)
    logger.info("STARTING RVR STRATEGY BACKTEST")
    logger.info(f"Testing thresholds: {thresholds}")
    logger.info(f"Lookback period: {days_back} days")
    logger.info("=" * 80)
    
    # Fetch top markets
    markets = fetch_top_markets(limit=20)
    
    if not markets:
        logger.error("Failed to fetch markets")
        return {}
    
    # Initialize backtest engines for each threshold
    engines = {threshold: BacktestEngine(threshold) for threshold in thresholds}
    
    # For each market, simulate historical data and run strategy
    for idx, market in enumerate(markets, 1):
        market_id = market.get('conditionId', market.get('id'))
        market_name = market.get('question', 'Unknown')
        
        logger.info(f"\n[{idx}/{len(markets)}] Processing: {market_name[:60]}...")
        
        # Generate/simulate historical data
        historical_data = simulate_historical_data(market, days=days_back)
        
        # Run strategy for each threshold
        for threshold, engine in engines.items():
            # Process historical data hour by hour
            for i in range(24, len(historical_data)):  # Start after 24 hours of history
                current_data = historical_data[i]
                current_data['question'] = market_name
                past_data = historical_data[:i]
                
                timestamp = current_data['timestamp']
                
                # Update existing open trades
                engine.update_open_trades(current_data, timestamp)
                
                # Check for new entry signals
                signal, rvr, roc = engine.check_entry_signal(current_data, past_data)
                
                if signal:
                    engine.open_trade(current_data, timestamp, rvr, roc)
        
        # Small delay to be respectful to API
        time.sleep(0.1)
    
    # Close any remaining open trades at final prices
    for threshold, engine in engines.items():
        for market_id in list(engine.open_trades.keys()):
            trade = engine.open_trades[market_id]
            engine.close_trade(market_id, trade.entry_price, datetime.now(), "End of Backtest")
    
    # Collect results
    results = {}
    for threshold, engine in engines.items():
        results[threshold] = engine.get_statistics()
    
    return results, engines


def generate_report(results, engines):
    """Generate markdown report with backtest results"""
    
    report = "# Polymarket RVR Strategy Backtest Results\n\n"
    report += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    report += "## Strategy Overview\n\n"
    report += "**Entry Criteria:**\n"
    report += "- RVR (Relative Volume Ratio) >= Threshold\n"
    report += "- ROC (Rate of Change, 12h) >= 10%\n\n"
    
    report += "**Exit Criteria:**\n"
    report += "- Stop Loss: -12%\n"
    report += "- Take Profit Levels: +20%, +30%, +50%\n\n"
    
    report += "---\n\n"
    
    # Summary table
    report += "## Performance Comparison by Threshold\n\n"
    report += "| Threshold | Total Trades | Win Rate | Avg Return | Max Drawdown | Total Return | Final Capital |\n"
    report += "|-----------|--------------|----------|------------|--------------|--------------|---------------|\n"
    
    for threshold in sorted(results.keys()):
        stats = results[threshold]
        report += f"| **{threshold}x** | {stats['total_trades']} | "
        report += f"{stats['win_rate']:.1f}% | {stats['avg_return']:+.2f}% | "
        report += f"{stats['max_drawdown']:.2f}% | {stats['total_return']:+.2f}% | "
        report += f"${stats['final_capital']:,.2f} |\n"
    
    report += "\n---\n\n"
    
    # Detailed analysis for each threshold
    report += "## Detailed Analysis by Threshold\n\n"
    
    for threshold in sorted(results.keys()):
        stats = results[threshold]
        engine = engines[threshold]
        
        report += f"### {threshold}x Volume Spike Threshold\n\n"
        
        report += f"**Performance Metrics:**\n"
        report += f"- Total Trades: {stats['total_trades']}\n"
        report += f"- Profitable Trades: {stats['profitable_trades']} ({stats['win_rate']:.1f}%)\n"
        report += f"- Losing Trades: {stats['losing_trades']}\n"
        report += f"- Average Return per Trade: {stats['avg_return']:+.2f}%\n"
        report += f"- Average Win: {stats['avg_win']:+.2f}%\n"
        report += f"- Average Loss: {stats['avg_loss']:+.2f}%\n"
        report += f"- Maximum Drawdown: {stats['max_drawdown']:.2f}%\n"
        report += f"- Total Return: {stats['total_return']:+.2f}%\n"
        report += f"- Final Capital: ${stats['final_capital']:,.2f}\n\n"
        
        # Best and worst trades
        if stats['best_trade']:
            best = stats['best_trade']
            report += f"**Best Trade:**\n"
            report += f"- Market: {best.market_name}\n"
            report += f"- Entry: {best.entry_price:.3f} | Exit: {best.exit_price:.3f}\n"
            report += f"- Return: {best.return_pct:+.2f}%\n"
            report += f"- Exit Reason: {best.exit_reason}\n\n"
        
        if stats['worst_trade']:
            worst = stats['worst_trade']
            report += f"**Worst Trade:**\n"
            report += f"- Market: {worst.market_name}\n"
            report += f"- Entry: {worst.entry_price:.3f} | Exit: {worst.exit_price:.3f}\n"
            report += f"- Return: {worst.return_pct:+.2f}%\n"
            report += f"- Exit Reason: {worst.exit_reason}\n\n"
        
        # Sample trades (first 5)
        if engine.trades:
            report += f"**Sample Trades (first 5):**\n\n"
            for i, trade in enumerate(engine.trades[:5], 1):
                emoji = "✅" if trade.is_profitable() else "❌"
                report += f"{i}. {emoji} **{trade.market_name[:50]}**\n"
                report += f"   - Entry: {trade.entry_price:.3f} @ {trade.entry_time.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"   - Exit: {trade.exit_price:.3f} @ {trade.exit_time.strftime('%Y-%m-%d %H:%M')}\n"
                report += f"   - RVR: {trade.rvr:.2f} | ROC: {trade.roc:+.1f}%\n"
                report += f"   - Return: {trade.return_pct:+.2f}% | Exit: {trade.exit_reason}\n\n"
        
        report += "---\n\n"
    
    # Recommendations
    report += "## Recommendations\n\n"
    
    # Find best threshold by total return
    best_threshold = max(results.keys(), key=lambda k: results[k]['total_return'])
    best_stats = results[best_threshold]
    
    report += f"**Optimal Threshold: {best_threshold}x**\n\n"
    report += f"Based on total return ({best_stats['total_return']:+.2f}%), "
    report += f"the {best_threshold}x threshold provides the best risk-adjusted performance with:\n"
    report += f"- Win Rate: {best_stats['win_rate']:.1f}%\n"
    report += f"- Average Return: {best_stats['avg_return']:+.2f}%\n"
    report += f"- Max Drawdown: {best_stats['max_drawdown']:.2f}%\n\n"
    
    # Analysis notes
    report += "**Key Insights:**\n\n"
    
    # Compare trade frequency
    trade_counts = {k: v['total_trades'] for k, v in results.items()}
    lowest_threshold = min(trade_counts.keys())
    highest_threshold = max(trade_counts.keys())
    
    report += f"1. **Trade Frequency:** Lower thresholds ({lowest_threshold}x) generate more signals "
    report += f"({trade_counts[lowest_threshold]} trades) but may have more false positives. "
    report += f"Higher thresholds ({highest_threshold}x) are more selective "
    report += f"({trade_counts[highest_threshold]} trades) but may miss opportunities.\n\n"
    
    # Win rate analysis
    win_rates = {k: v['win_rate'] for k, v in results.items()}
    best_wr_threshold = max(win_rates.keys(), key=lambda k: win_rates[k])
    
    report += f"2. **Win Rate:** The {best_wr_threshold}x threshold achieved the highest win rate "
    report += f"({win_rates[best_wr_threshold]:.1f}%), suggesting stronger signal quality at this level.\n\n"
    
    # Drawdown analysis
    drawdowns = {k: v['max_drawdown'] for k, v in results.items()}
    safest_threshold = max(drawdowns.keys(), key=lambda k: drawdowns[k])  # Closest to 0
    
    report += f"3. **Risk Management:** The {safest_threshold}x threshold showed the lowest maximum drawdown "
    report += f"({drawdowns[safest_threshold]:.2f}%), indicating better risk control.\n\n"
    
    report += "\n---\n\n"
    report += "*Note: This backtest uses simulated historical data. Real results may vary. "
    report += "Always conduct forward testing before live trading.*\n"
    
    return report


if __name__ == "__main__":
    # Run backtests
    thresholds = [1.5, 2.0, 2.5, 3.0, 4.0]
    results, engines = run_backtest(thresholds=thresholds, days_back=30)
    
    # Generate report
    report = generate_report(results, engines)
    
    # Save report
    with open("BACKTEST_RVR_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info("\n" + "=" * 80)
    logger.info("BACKTEST COMPLETE!")
    logger.info("Report saved to: BACKTEST_RVR_RESULTS.md")
    logger.info("=" * 80)
    
    # Print summary to console
    print("\n" + "=" * 80)
    print("BACKTEST SUMMARY")
    print("=" * 80)
    print(f"\n{'Threshold':<12} {'Trades':<10} {'Win Rate':<12} {'Avg Return':<14} {'Total Return':<14}")
    print("-" * 80)
    
    for threshold in sorted(results.keys()):
        stats = results[threshold]
        print(f"{threshold}x{'':<10} {stats['total_trades']:<10} "
              f"{stats['win_rate']:>6.1f}%{'':<5} {stats['avg_return']:>+7.2f}%{'':<6} "
              f"{stats['total_return']:>+7.2f}%")
    
    print("=" * 80)
    print(f"\nFull report saved to: BACKTEST_RVR_RESULTS.md\n")
