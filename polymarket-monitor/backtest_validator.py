#!/usr/bin/env python3
"""
Rolling Backtest Validator
==========================
Continuously validates strategy performance on NEW historical data.

Purpose:
- Re-runs backtests on markets from last 30 days
- Compares current win rates vs original baseline
- Detects strategy degradation (>10% win rate drop)
- Alerts if edge is fading
- Recommends strategy adjustments

Usage:
    python backtest_validator.py                    # Run validation
    python backtest_validator.py --alert            # Send alerts to Telegram
    python backtest_validator.py --days 60          # Check last 60 days
    python backtest_validator.py --baseline 95.0    # Custom baseline win rate
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

# Baseline metrics from original backtest (backtest_fixed.py 2026-02-07)
BASELINE_METRICS = {
    'win_rate': 94.98,      # % win rate from fixed backtest
    'avg_pnl': 0.352,       # Average P&L per trade
    'avg_win': 0.371,       # Average winning trade
    'avg_loss': -0.003,     # Average losing trade
    'sample_size': 5615,    # Number of trades in original backtest
    'date': '2026-02-07'    # Date of baseline backtest
}

# Degradation thresholds
DEGRADATION_THRESHOLD = 10.0    # % drop in win rate to trigger alert
MIN_SAMPLE_SIZE = 50            # Minimum trades needed for valid comparison

# Polymarket API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Output directory
OUTPUT_DIR = Path("validation-reports")
OUTPUT_DIR.mkdir(exist_ok=True)

# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Trade:
    """Individual trade record"""
    market_id: str
    market_question: str
    entry_price: float
    exit_price: float
    entry_idx: int
    exit_idx: int
    total_points: int
    bet_side: str
    outcome: str
    pnl: float
    win: bool
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None

@dataclass
class StrategyMetrics:
    """Strategy performance metrics"""
    total_trades: int
    wins: int
    losses: int
    win_rate: float
    avg_pnl: float
    avg_win: float
    avg_loss: float
    total_pnl: float
    sharpe_ratio: Optional[float] = None

@dataclass
class ValidationReport:
    """Validation report comparing current vs baseline"""
    timestamp: datetime
    period_days: int
    markets_analyzed: int
    baseline_metrics: Dict
    current_metrics: StrategyMetrics
    degradation_detected: bool
    win_rate_delta: float
    pnl_delta: float
    recommendations: List[str]
    trades: List[Trade]

# ============================================================
# POLYMARKET API CLIENT
# ============================================================

class PolymarketAPI:
    """Client for fetching Polymarket data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_closed_markets(self, days: int = 30, limit: int = 100) -> List[Dict]:
        """
        Fetch closed markets from the last N days
        
        Args:
            days: Number of days to look back
            limit: Max markets per request
            
        Returns:
            List of market data dictionaries
        """
        cutoff_time = datetime.now() - timedelta(days=days)
        cutoff_timestamp = int(cutoff_time.timestamp())
        
        logger.info(f"📡 Fetching closed markets from last {days} days...")
        
        markets = []
        offset = 0
        
        while True:
            try:
                # Fetch batch of markets
                response = self.session.get(
                    f"{GAMMA_API}/markets",
                    params={
                        'closed': 'true',
                        'limit': limit,
                        'offset': offset,
                        '_sort': 'endDate',
                        '_order': 'DESC'
                    },
                    timeout=30
                )
                response.raise_for_status()
                batch = response.json()
                
                if not batch:
                    break
                
                # Filter by time window
                for market in batch:
                    end_date = market.get('endDate')
                    if end_date:
                        end_ts = datetime.fromisoformat(end_date.replace('Z', '+00:00')).timestamp()
                        if end_ts >= cutoff_timestamp:
                            markets.append(market)
                        else:
                            # Reached markets older than cutoff
                            logger.info(f"✅ Fetched {len(markets)} closed markets")
                            return markets
                
                logger.info(f"   Fetched {len(markets)} markets so far...")
                offset += limit
                
                # Safety limit to avoid infinite loops
                if offset > 10000:
                    logger.warning("⚠️ Hit safety limit of 10,000 markets")
                    break
                    
            except Exception as e:
                logger.error(f"❌ Error fetching markets: {e}")
                break
        
        logger.info(f"✅ Fetched {len(markets)} closed markets")
        return markets
    
    def fetch_market_history(self, market_id: str) -> List[Dict]:
        """
        Fetch price history for a specific market
        
        Args:
            market_id: Polymarket market ID
            
        Returns:
            List of price snapshots [{t: timestamp, p: price}, ...]
        """
        try:
            # Try CLOB API first
            response = self.session.get(
                f"{CLOB_API}/prices-history",
                params={
                    'market': market_id,
                    'interval': 'max'  # Get full history
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data and 'history' in data:
                    return data['history']
            
            # Fallback: try to get from market snapshot data
            logger.debug(f"⚠️ No CLOB history for {market_id}, using snapshot")
            return []
            
        except Exception as e:
            logger.debug(f"⚠️ Error fetching history for {market_id}: {e}")
            return []

# ============================================================
# STRATEGY IMPLEMENTATION
# ============================================================

class TrendFilterStrategy:
    """
    Trend Filter Strategy (Exact replica from backtest_ACTUALLY_fixed.py)
    
    Entry: When price shows uptrend (3 consecutive rising points)
    Exit: At 70% of market lifetime
    Direction: ALWAYS bet YES on uptrend (no peeking!)
    P&L: Binary outcome ($1 or $0), not price difference
    """
    
    def __init__(self):
        self.name = "Trend Filter"
        self.min_history = 30
        self.exit_pct = 0.70
        self.trend_lookback = 3
    
    def backtest(self, markets: List[Dict]) -> Tuple[List[Trade], StrategyMetrics]:
        """
        Run backtest on market data
        
        Args:
            markets: List of closed market dictionaries
            
        Returns:
            Tuple of (trades list, metrics)
        """
        logger.info(f"🎯 Running {self.name} strategy...")
        
        trades = []
        skipped_ambiguous = 0
        skipped_no_history = 0
        skipped_no_signal = 0
        
        for i, market in enumerate(markets):
            if (i + 1) % 100 == 0:
                logger.info(f"   Processed {i+1}/{len(markets)} markets...")
            
            # Get market data
            market_id = market.get('id') or market.get('market_id')
            question = market.get('question') or market.get('name', 'Unknown')[:60]
            
            # Get price history (either pre-loaded or fetch)
            price_history = market.get('price_history', [])
            
            # Skip if insufficient history
            if len(price_history) < self.min_history:
                skipped_no_history += 1
                continue
            
            # Determine outcome from final price
            final_price = price_history[-1].get('p', 0)
            if final_price > 0.95:
                outcome = 'Yes'
            elif final_price < 0.05:
                outcome = 'No'
            else:
                skipped_ambiguous += 1
                continue
            
            # Walk forward through price history
            max_entry_idx = int(len(price_history) * self.exit_pct)
            
            for idx in range(5, max_entry_idx):
                # Only look at data UP TO this index
                current_price = price_history[idx].get('p', 0)
                prev_1 = price_history[idx-1].get('p', 0)
                prev_2 = price_history[idx-2].get('p', 0)
                prev_3 = price_history[idx-3].get('p', 0)
                
                # Trend signal: 3 consecutive rising prices
                if current_price > prev_1 > prev_2 > prev_3:
                    entry_price = current_price
                    
                    # Exit at 70% of lifetime
                    exit_idx = int(len(price_history) * self.exit_pct)
                    exit_price = price_history[exit_idx].get('p', 0)
                    
                    # ALWAYS bet YES on uptrend (no peeking!)
                    bet_side = 'Yes'
                    
                    # Binary P&L calculation
                    if outcome == 'Yes':
                        pnl = 1.0 - entry_price  # Win: get $1, paid entry_price
                    else:
                        pnl = 0.0 - entry_price  # Lose: get $0, paid entry_price
                    
                    win = pnl > 0
                    
                    # Extract timestamps if available
                    entry_time = None
                    exit_time = None
                    if 't' in price_history[idx]:
                        entry_time = datetime.fromtimestamp(price_history[idx]['t'])
                    if 't' in price_history[exit_idx]:
                        exit_time = datetime.fromtimestamp(price_history[exit_idx]['t'])
                    
                    trades.append(Trade(
                        market_id=market_id,
                        market_question=question,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        entry_idx=idx,
                        exit_idx=exit_idx,
                        total_points=len(price_history),
                        bet_side=bet_side,
                        outcome=outcome,
                        pnl=pnl,
                        win=win,
                        entry_time=entry_time,
                        exit_time=exit_time
                    ))
                    break  # One trade per market
            else:
                skipped_no_signal += 1
        
        logger.info(f"✅ Strategy complete:")
        logger.info(f"   Trades: {len(trades)}")
        logger.info(f"   Skipped (no history): {skipped_no_history}")
        logger.info(f"   Skipped (ambiguous): {skipped_ambiguous}")
        logger.info(f"   Skipped (no signal): {skipped_no_signal}")
        
        # Calculate metrics
        metrics = self._calculate_metrics(trades)
        
        return trades, metrics
    
    def _calculate_metrics(self, trades: List[Trade]) -> StrategyMetrics:
        """Calculate performance metrics from trades"""
        if not trades:
            return StrategyMetrics(
                total_trades=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                avg_pnl=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                total_pnl=0.0
            )
        
        total_trades = len(trades)
        wins = len([t for t in trades if t.win])
        losses = total_trades - wins
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        
        total_pnl = sum(t.pnl for t in trades)
        avg_pnl = total_pnl / total_trades
        
        winning_trades = [t for t in trades if t.win]
        losing_trades = [t for t in trades if not t.win]
        
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        # Calculate Sharpe ratio (simplified)
        if trades:
            import statistics
            pnls = [t.pnl for t in trades]
            if len(pnls) > 1:
                mean_pnl = statistics.mean(pnls)
                std_pnl = statistics.stdev(pnls)
                sharpe_ratio = mean_pnl / std_pnl if std_pnl > 0 else 0
            else:
                sharpe_ratio = None
        else:
            sharpe_ratio = None
        
        return StrategyMetrics(
            total_trades=total_trades,
            wins=wins,
            losses=losses,
            win_rate=win_rate,
            avg_pnl=avg_pnl,
            avg_win=avg_win,
            avg_loss=avg_loss,
            total_pnl=total_pnl,
            sharpe_ratio=sharpe_ratio
        )

# ============================================================
# VALIDATION ENGINE
# ============================================================

class BacktestValidator:
    """Main validation engine"""
    
    def __init__(self, baseline: Dict = BASELINE_METRICS):
        self.baseline = baseline
        self.api = PolymarketAPI()
        self.strategy = TrendFilterStrategy()
    
    def run_validation(self, days: int = 30) -> ValidationReport:
        """
        Run complete validation cycle
        
        Args:
            days: Number of days of historical data to validate
            
        Returns:
            ValidationReport with results
        """
        logger.info("=" * 70)
        logger.info("ROLLING BACKTEST VALIDATOR")
        logger.info("=" * 70)
        logger.info(f"Validation period: Last {days} days")
        logger.info(f"Baseline: {self.baseline['win_rate']:.2f}% win rate from {self.baseline['date']}")
        logger.info("=" * 70)
        
        # Step 1: Fetch closed markets
        markets = self.api.fetch_closed_markets(days=days)
        
        if not markets:
            logger.error("❌ No markets fetched, cannot validate")
            return self._create_empty_report(days, "No markets fetched")
        
        # Step 2: Enrich markets with price history
        logger.info(f"📊 Enriching {len(markets)} markets with price history...")
        enriched_markets = self._enrich_with_history(markets)
        logger.info(f"✅ Enriched {len(enriched_markets)} markets")
        
        if not enriched_markets:
            logger.error("❌ No markets with sufficient price history")
            return self._create_empty_report(days, "No markets with price history")
        
        # Step 3: Run strategy backtest
        trades, metrics = self.strategy.backtest(enriched_markets)
        
        # Step 4: Analyze results
        report = self._analyze_results(
            days=days,
            markets_analyzed=len(enriched_markets),
            trades=trades,
            metrics=metrics
        )
        
        # Step 5: Generate report
        self._print_report(report)
        
        return report
    
    def _enrich_with_history(self, markets: List[Dict]) -> List[Dict]:
        """Add price history to markets that don't have it"""
        enriched = []
        
        for i, market in enumerate(markets):
            if (i + 1) % 50 == 0:
                logger.info(f"   Processing {i+1}/{len(markets)}...")
            
            # Check if already has price history
            if 'price_history' in market and market['price_history']:
                enriched.append(market)
                continue
            
            # Try to fetch history
            market_id = market.get('id') or market.get('market_id')
            if not market_id:
                continue
            
            history = self.api.fetch_market_history(market_id)
            
            if history and len(history) >= self.strategy.min_history:
                market['price_history'] = history
                enriched.append(market)
        
        return enriched
    
    def _analyze_results(
        self,
        days: int,
        markets_analyzed: int,
        trades: List[Trade],
        metrics: StrategyMetrics
    ) -> ValidationReport:
        """Analyze backtest results and compare to baseline"""
        
        # Calculate degradation
        win_rate_delta = metrics.win_rate - self.baseline['win_rate']
        pnl_delta = metrics.avg_pnl - self.baseline['avg_pnl']
        
        # Check if degradation threshold exceeded
        degradation_detected = (
            metrics.total_trades >= MIN_SAMPLE_SIZE and
            win_rate_delta < -DEGRADATION_THRESHOLD
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            metrics=metrics,
            win_rate_delta=win_rate_delta,
            pnl_delta=pnl_delta,
            degradation_detected=degradation_detected
        )
        
        return ValidationReport(
            timestamp=datetime.now(),
            period_days=days,
            markets_analyzed=markets_analyzed,
            baseline_metrics=self.baseline,
            current_metrics=metrics,
            degradation_detected=degradation_detected,
            win_rate_delta=win_rate_delta,
            pnl_delta=pnl_delta,
            recommendations=recommendations,
            trades=trades
        )
    
    def _generate_recommendations(
        self,
        metrics: StrategyMetrics,
        win_rate_delta: float,
        pnl_delta: float,
        degradation_detected: bool
    ) -> List[str]:
        """Generate actionable recommendations based on results"""
        recs = []
        
        if metrics.total_trades < MIN_SAMPLE_SIZE:
            recs.append(
                f"⚠️ INSUFFICIENT DATA: Only {metrics.total_trades} trades "
                f"(need {MIN_SAMPLE_SIZE}+). Wait for more closed markets."
            )
            return recs
        
        if degradation_detected:
            recs.append(
                f"🚨 CRITICAL: Win rate dropped {abs(win_rate_delta):.1f}% "
                f"below baseline! Strategy edge may be fading."
            )
            recs.append(
                "💡 ACTION: Pause automated trading and investigate:"
            )
            recs.append("   • Market conditions changed?")
            recs.append("   • More sophisticated players?")
            recs.append("   • Strategy needs adjustment?")
        elif win_rate_delta < -5:
            recs.append(
                f"⚠️ WARNING: Win rate down {abs(win_rate_delta):.1f}%. "
                "Monitor closely."
            )
        elif win_rate_delta > 5:
            recs.append(
                f"✅ STRONG: Win rate up {win_rate_delta:.1f}%! "
                "Strategy performing well."
            )
        else:
            recs.append(
                "✅ STABLE: Win rate within normal range. "
                "Strategy edge intact."
            )
        
        # Check P&L changes
        if pnl_delta < -0.1:
            recs.append(
                f"📉 Avg P&L down {abs(pnl_delta):.3f}. "
                "Less profitable trades recently."
            )
        elif pnl_delta > 0.1:
            recs.append(
                f"📈 Avg P&L up {pnl_delta:.3f}. "
                "More profitable trades recently!"
            )
        
        # Check sample size
        if metrics.total_trades < self.baseline['sample_size'] * 0.1:
            recs.append(
                f"📊 Small sample ({metrics.total_trades} trades vs "
                f"{self.baseline['sample_size']} baseline). Results less reliable."
            )
        
        # Check Sharpe ratio if available
        if metrics.sharpe_ratio is not None:
            if metrics.sharpe_ratio < 1.0:
                recs.append(
                    f"📊 Low Sharpe ratio ({metrics.sharpe_ratio:.2f}). "
                    "High volatility in returns."
                )
            elif metrics.sharpe_ratio > 2.0:
                recs.append(
                    f"📊 Excellent Sharpe ratio ({metrics.sharpe_ratio:.2f}). "
                    "Consistent returns!"
                )
        
        return recs
    
    def _print_report(self, report: ValidationReport):
        """Print formatted validation report"""
        logger.info("\n" + "=" * 70)
        logger.info("VALIDATION REPORT")
        logger.info("=" * 70)
        
        logger.info(f"\n📅 Period: Last {report.period_days} days")
        logger.info(f"📊 Markets analyzed: {report.markets_analyzed:,}")
        logger.info(f"🎯 Trades generated: {report.current_metrics.total_trades:,}")
        
        logger.info("\n📈 BASELINE METRICS (Original Backtest):")
        logger.info(f"   Win Rate: {report.baseline_metrics['win_rate']:.2f}%")
        logger.info(f"   Avg P&L:  {report.baseline_metrics['avg_pnl']:+.3f}")
        logger.info(f"   Sample:   {report.baseline_metrics['sample_size']:,} trades")
        logger.info(f"   Date:     {report.baseline_metrics['date']}")
        
        logger.info("\n📊 CURRENT METRICS (Rolling Validation):")
        logger.info(f"   Win Rate: {report.current_metrics.win_rate:.2f}% "
                   f"({report.win_rate_delta:+.2f}%)")
        logger.info(f"   Avg P&L:  {report.current_metrics.avg_pnl:+.3f} "
                   f"({report.pnl_delta:+.3f})")
        logger.info(f"   Avg Win:  {report.current_metrics.avg_win:+.3f}")
        logger.info(f"   Avg Loss: {report.current_metrics.avg_loss:+.3f}")
        logger.info(f"   Total P&L: {report.current_metrics.total_pnl:+.2f}")
        if report.current_metrics.sharpe_ratio:
            logger.info(f"   Sharpe:   {report.current_metrics.sharpe_ratio:.2f}")
        
        logger.info("\n🔍 DEGRADATION ANALYSIS:")
        if report.degradation_detected:
            logger.info("   🚨 ALERT: Strategy degradation detected!")
        else:
            logger.info("   ✅ No significant degradation detected")
        
        logger.info("\n💡 RECOMMENDATIONS:")
        for rec in report.recommendations:
            logger.info(f"   {rec}")
        
        logger.info("\n" + "=" * 70)
    
    def _create_empty_report(self, days: int, reason: str) -> ValidationReport:
        """Create empty report when validation can't run"""
        return ValidationReport(
            timestamp=datetime.now(),
            period_days=days,
            markets_analyzed=0,
            baseline_metrics=self.baseline,
            current_metrics=StrategyMetrics(
                total_trades=0,
                wins=0,
                losses=0,
                win_rate=0.0,
                avg_pnl=0.0,
                avg_win=0.0,
                avg_loss=0.0,
                total_pnl=0.0
            ),
            degradation_detected=False,
            win_rate_delta=0.0,
            pnl_delta=0.0,
            recommendations=[f"❌ Validation failed: {reason}"],
            trades=[]
        )
    
    def save_report(self, report: ValidationReport, filename: Optional[str] = None):
        """Save validation report to JSON file"""
        if filename is None:
            timestamp = report.timestamp.strftime('%Y%m%d_%H%M%S')
            filename = f"validation_report_{timestamp}.json"
        
        filepath = OUTPUT_DIR / filename
        
        # Convert to JSON-serializable dict
        report_dict = {
            'timestamp': report.timestamp.isoformat(),
            'period_days': report.period_days,
            'markets_analyzed': report.markets_analyzed,
            'baseline_metrics': report.baseline_metrics,
            'current_metrics': asdict(report.current_metrics),
            'degradation_detected': report.degradation_detected,
            'win_rate_delta': report.win_rate_delta,
            'pnl_delta': report.pnl_delta,
            'recommendations': report.recommendations,
            'sample_trades': [asdict(t) for t in report.trades[:100]]  # First 100 trades
        }
        
        with open(filepath, 'w') as f:
            json.dump(report_dict, f, indent=2, default=str)
        
        logger.info(f"💾 Report saved: {filepath}")
        return filepath

# ============================================================
# TELEGRAM ALERTING
# ============================================================

def send_telegram_alert(report: ValidationReport):
    """Send alert to Telegram if degradation detected"""
    try:
        from message import message as send_message
        from config import TELEGRAM_TARGET
        
        if not report.degradation_detected:
            logger.info("ℹ️ No degradation detected, skipping alert")
            return
        
        # Format alert message
        message = (
            f"🚨 *STRATEGY DEGRADATION ALERT*\n\n"
            f"📅 Period: Last {report.period_days} days\n"
            f"📊 Sample: {report.current_metrics.total_trades:,} trades\n\n"
            f"*Current Performance:*\n"
            f"Win Rate: {report.current_metrics.win_rate:.1f}% "
            f"({report.win_rate_delta:+.1f}%)\n"
            f"Avg P&L: {report.current_metrics.avg_pnl:+.3f}\n\n"
            f"*Baseline:*\n"
            f"Win Rate: {report.baseline_metrics['win_rate']:.1f}%\n"
            f"Avg P&L: {report.baseline_metrics['avg_pnl']:+.3f}\n\n"
            f"💡 *Recommendations:*\n"
        )
        
        for rec in report.recommendations[:3]:  # Top 3 recommendations
            message += f"• {rec}\n"
        
        # Send via message tool
        send_message(
            action="send",
            target=TELEGRAM_TARGET,
            message=message
        )
        
        logger.info("✅ Alert sent to Telegram")
        
    except Exception as e:
        logger.error(f"❌ Failed to send Telegram alert: {e}")

# ============================================================
# MAIN ENTRY POINT
# ============================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Rolling Backtest Validator - Monitor strategy performance"
    )
    parser.add_argument(
        '--days',
        type=int,
        default=30,
        help='Number of days to validate (default: 30)'
    )
    parser.add_argument(
        '--baseline',
        type=float,
        help=f'Custom baseline win rate (default: {BASELINE_METRICS["win_rate"]:.2f}%%)'
    )
    parser.add_argument(
        '--alert',
        action='store_true',
        help='Send Telegram alert if degradation detected'
    )
    parser.add_argument(
        '--save',
        action='store_true',
        default=True,
        help='Save report to file (default: True)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output filename (default: auto-generated)'
    )
    
    args = parser.parse_args()
    
    # Override baseline if specified
    baseline = BASELINE_METRICS.copy()
    if args.baseline is not None:
        baseline['win_rate'] = args.baseline
    
    # Run validation
    validator = BacktestValidator(baseline=baseline)
    report = validator.run_validation(days=args.days)
    
    # Save report
    if args.save:
        validator.save_report(report, filename=args.output)
    
    # Send alert if requested
    if args.alert:
        send_telegram_alert(report)
    
    # Exit with status code
    if report.degradation_detected:
        logger.warning("⚠️ Exiting with status 1 (degradation detected)")
        sys.exit(1)
    else:
        logger.info("✅ Exiting with status 0 (validation passed)")
        sys.exit(0)

if __name__ == "__main__":
    main()
