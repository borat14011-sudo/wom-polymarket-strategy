#!/usr/bin/env python3
"""
Polymarket ROC Momentum Strategy Backtester
Tests different ROC thresholds and timeframes
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import time

class PolymarketROCBacktester:
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
        self.results = {}
        
    def fetch_top_markets(self, limit=20):
        """Fetch top markets by volume"""
        try:
            url = f"{self.base_url}/markets?limit={limit}&closed=false"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def fetch_market_prices(self, condition_id: str, limit=1000):
        """Fetch historical price data for a market"""
        try:
            url = f"{self.base_url}/prices?market={condition_id}&limit={limit}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching prices for {condition_id}: {e}")
            return []
    
    def calculate_roc(self, prices: List[float], timeframe_hours: int) -> float:
        """Calculate Rate of Change over timeframe"""
        if len(prices) < 2:
            return 0.0
        
        # Assuming prices are ordered chronologically
        current_price = prices[-1]
        past_price = prices[0] if len(prices) <= timeframe_hours else prices[-timeframe_hours]
        
        if past_price == 0:
            return 0.0
        
        roc = ((current_price - past_price) / past_price) * 100
        return roc
    
    def calculate_rvr(self, entry_price: float, current_price: float, stop_loss_pct=0.12):
        """Calculate Risk/Reward Ratio"""
        # Risk: distance to stop loss
        risk = entry_price * stop_loss_pct
        
        # Reward: potential to 1.0 (100%)
        reward = 1.0 - current_price
        
        if risk == 0:
            return 0.0
        
        rvr = reward / risk
        return rvr
    
    def simulate_trade(self, prices: List[Dict], entry_idx: int, entry_price: float):
        """Simulate a single trade with exit conditions"""
        stop_loss = entry_price * 0.88  # 12% stop loss
        
        # Tiered profit targets
        profit_targets = [
            (1.10, 0.33),  # 10% gain, exit 33%
            (1.20, 0.33),  # 20% gain, exit another 33%
            (1.30, 0.34),  # 30% gain, exit remainder
        ]
        
        position_size = 1.0
        total_pnl = 0.0
        exit_reason = "none"
        
        for i in range(entry_idx + 1, len(prices)):
            current_price = prices[i].get('price', entry_price)
            
            # Check stop loss
            if current_price <= stop_loss:
                pnl_pct = ((current_price - entry_price) / entry_price) * 100
                total_pnl = pnl_pct * position_size
                exit_reason = "stop_loss"
                return total_pnl, exit_reason
            
            # Check profit targets
            for target_multiplier, exit_fraction in profit_targets:
                target_price = entry_price * target_multiplier
                if current_price >= target_price and position_size > 0:
                    exit_amount = exit_fraction
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                    total_pnl += pnl_pct * exit_amount
                    position_size -= exit_amount
                    
                    if position_size <= 0.01:  # Fully exited
                        exit_reason = "profit_target"
                        return total_pnl, exit_reason
        
        # End of data - close remaining position
        if position_size > 0:
            final_price = prices[-1].get('price', entry_price)
            pnl_pct = ((final_price - entry_price) / entry_price) * 100
            total_pnl += pnl_pct * position_size
            exit_reason = "end_of_data"
        
        return total_pnl, exit_reason
    
    def backtest_configuration(self, roc_threshold: float, timeframe_hours: int, 
                              markets_data: List[Dict]) -> Dict:
        """Backtest a specific ROC threshold and timeframe combination"""
        
        trades = []
        total_trades = 0
        winning_trades = 0
        losing_trades = 0
        total_pnl = 0.0
        
        print(f"\n{'='*60}")
        print(f"Testing ROC {roc_threshold}% over {timeframe_hours}h timeframe")
        print(f"{'='*60}")
        
        for market in markets_data[:10]:  # Test on top 10 markets
            market_name = market.get('question', 'Unknown')
            condition_id = market.get('conditionId', '')
            
            if not condition_id:
                continue
            
            print(f"\nAnalyzing: {market_name[:60]}...")
            
            # Fetch price history
            price_data = self.fetch_market_prices(condition_id)
            time.sleep(0.5)  # Rate limiting
            
            if not price_data or len(price_data) < timeframe_hours + 10:
                print(f"  ⚠ Insufficient data ({len(price_data)} points)")
                continue
            
            # Process prices
            prices = []
            for p in price_data:
                if isinstance(p, dict) and 'price' in p:
                    prices.append({
                        'price': float(p['price']),
                        'timestamp': p.get('timestamp', 0)
                    })
            
            if len(prices) < timeframe_hours + 10:
                continue
            
            # Scan for entry signals
            for i in range(timeframe_hours, len(prices) - 10):
                lookback_prices = [prices[j]['price'] for j in range(i - timeframe_hours, i + 1)]
                current_price = prices[i]['price']
                
                # Calculate ROC
                roc = self.calculate_roc(lookback_prices, timeframe_hours)
                
                # Calculate RVR
                rvr = self.calculate_rvr(current_price, current_price)
                
                # Entry signal: ROC above threshold AND RVR > 2.5
                if roc >= roc_threshold and rvr > 2.5:
                    # Simulate trade
                    pnl, exit_reason = self.simulate_trade(prices, i, current_price)
                    
                    total_trades += 1
                    total_pnl += pnl
                    
                    if pnl > 0:
                        winning_trades += 1
                    else:
                        losing_trades += 1
                    
                    trades.append({
                        'market': market_name[:40],
                        'entry_price': current_price,
                        'roc': roc,
                        'rvr': rvr,
                        'pnl': pnl,
                        'exit_reason': exit_reason
                    })
                    
                    print(f"  📊 Trade #{total_trades}: Entry={current_price:.3f}, ROC={roc:.1f}%, RVR={rvr:.2f}x, PnL={pnl:+.2f}%, Exit={exit_reason}")
                    
                    # Skip ahead to avoid overlapping trades
                    i += 24
        
        # Calculate statistics
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        avg_pnl = (total_pnl / total_trades) if total_trades > 0 else 0
        
        return {
            'roc_threshold': roc_threshold,
            'timeframe_hours': timeframe_hours,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_pnl_per_trade': avg_pnl,
            'trades': trades
        }
    
    def run_backtest_suite(self):
        """Run comprehensive backtest across all configurations"""
        
        print("🚀 Starting Polymarket ROC Momentum Strategy Backtest")
        print("="*60)
        
        # Fetch markets
        print("\n📊 Fetching top markets...")
        markets = self.fetch_top_markets(limit=20)
        
        if not markets:
            print("❌ Failed to fetch markets")
            return
        
        print(f"✅ Loaded {len(markets)} markets")
        
        # Test configurations
        roc_thresholds = [5, 10, 15, 20]
        timeframes = [6, 12, 24]
        
        all_results = []
        
        for roc_threshold in roc_thresholds:
            for timeframe in timeframes:
                result = self.backtest_configuration(
                    roc_threshold, 
                    timeframe, 
                    markets
                )
                all_results.append(result)
                time.sleep(1)  # Rate limiting
        
        # Generate report
        self.generate_report(all_results)
        
        return all_results
    
    def generate_report(self, results: List[Dict]):
        """Generate markdown report with backtest results"""
        
        report = """# Polymarket ROC Momentum Strategy Backtest Results

## Executive Summary

This backtest evaluates a momentum-based trading strategy on Polymarket markets using Rate of Change (ROC) indicators combined with Risk/Reward Ratio (RVR) filters.

### Strategy Parameters
- **Entry Conditions**: ROC ≥ threshold AND RVR > 2.5x
- **Exit Conditions**: 
  - Stop Loss: 12% below entry
  - Tiered Profit Targets: 10% (exit 33%), 20% (exit 33%), 30% (exit 34%)

### ROC Thresholds Tested
- 5%, 10%, 15%, 20%

### Timeframes Tested
- 6 hours, 12 hours, 24 hours

---

## Results by Configuration

"""
        
        # Sort by total PnL
        sorted_results = sorted(results, key=lambda x: x['total_pnl'], reverse=True)
        
        for result in sorted_results:
            report += f"""
### Configuration: {result['roc_threshold']}% ROC over {result['timeframe_hours']}h

| Metric | Value |
|--------|-------|
| **Total Trades** | {result['total_trades']} |
| **Winning Trades** | {result['winning_trades']} |
| **Losing Trades** | {result['losing_trades']} |
| **Win Rate** | {result['win_rate']:.2f}% |
| **Total PnL** | {result['total_pnl']:+.2f}% |
| **Avg PnL/Trade** | {result['avg_pnl_per_trade']:+.2f}% |

"""
        
        # Performance ranking
        report += """
---

## Performance Ranking

| Rank | Configuration | Total PnL | Win Rate | Trades | Avg PnL/Trade |
|------|---------------|-----------|----------|--------|---------------|
"""
        
        for idx, result in enumerate(sorted_results, 1):
            config = f"{result['roc_threshold']}% / {result['timeframe_hours']}h"
            report += f"| {idx} | {config} | {result['total_pnl']:+.2f}% | {result['win_rate']:.1f}% | {result['total_trades']} | {result['avg_pnl_per_trade']:+.2f}% |\n"
        
        # Optimal configuration
        best = sorted_results[0]
        report += f"""
---

## Optimal Configuration

**🏆 Best Performer: {best['roc_threshold']}% ROC over {best['timeframe_hours']}h timeframe**

- **Total Return**: {best['total_pnl']:+.2f}%
- **Win Rate**: {best['win_rate']:.2f}%
- **Total Trades**: {best['total_trades']}
- **Average PnL per Trade**: {best['avg_pnl_per_trade']:+.2f}%

### Key Insights

"""
        
        # Analysis
        high_threshold_results = [r for r in results if r['roc_threshold'] >= 15]
        low_threshold_results = [r for r in results if r['roc_threshold'] < 15]
        
        avg_high_wr = sum(r['win_rate'] for r in high_threshold_results) / len(high_threshold_results) if high_threshold_results else 0
        avg_low_wr = sum(r['win_rate'] for r in low_threshold_results) / len(low_threshold_results) if low_threshold_results else 0
        
        report += f"""
1. **Threshold Analysis**:
   - High ROC thresholds (15-20%): Avg win rate {avg_high_wr:.1f}%
   - Low ROC thresholds (5-10%): Avg win rate {avg_low_wr:.1f}%

2. **Timeframe Analysis**:
"""
        
        for tf in [6, 12, 24]:
            tf_results = [r for r in results if r['timeframe_hours'] == tf]
            avg_pnl = sum(r['total_pnl'] for r in tf_results) / len(tf_results) if tf_results else 0
            report += f"   - {tf}h timeframe: Avg total PnL {avg_pnl:+.2f}%\n"
        
        report += """
3. **Trade Frequency**:
"""
        
        for result in sorted_results[:3]:
            report += f"   - {result['roc_threshold']}% / {result['timeframe_hours']}h: {result['total_trades']} trades\n"
        
        report += """
---

## Sample Trades (Top Configuration)

"""
        
        # Show sample trades from best configuration
        sample_trades = best['trades'][:10] if best['trades'] else []
        
        if sample_trades:
            report += "| Market | Entry Price | ROC | RVR | PnL | Exit Reason |\n"
            report += "|--------|-------------|-----|-----|-----|-------------|\n"
            
            for trade in sample_trades:
                report += f"| {trade['market'][:30]} | {trade['entry_price']:.3f} | {trade['roc']:.1f}% | {trade['rvr']:.2f}x | {trade['pnl']:+.2f}% | {trade['exit_reason']} |\n"
        
        report += """
---

## Methodology

1. **Data Source**: Gamma API historical price data for top 10 Polymarket markets
2. **Entry Signal**: When ROC over specified timeframe exceeds threshold AND RVR > 2.5x
3. **Position Sizing**: Equal position sizes for all trades
4. **Exit Logic**: 
   - Hit 12% stop loss → full exit
   - Hit 10% profit → exit 33% of position
   - Hit 20% profit → exit another 33%
   - Hit 30% profit → exit remainder
5. **Lookback Period**: Varies by timeframe (6h, 12h, or 24h)

## Limitations

- Historical data may be limited for some markets
- Does not account for liquidity constraints or slippage
- Past performance does not guarantee future results
- Market conditions on Polymarket can change rapidly
- Does not include transaction fees

## Recommendations

Based on this backtest:

1. **Optimal Setup**: Use **{best['roc_threshold']}% ROC threshold** with **{best['timeframe_hours']}h timeframe**
2. **Risk Management**: The 12% stop loss is critical - do not override
3. **Position Sizing**: Consider reducing position size for lower ROC signals
4. **Market Selection**: Focus on high-volume, liquid markets
5. **Monitoring**: Re-run backtest monthly to validate strategy performance

---

*Backtest completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        # Write report
        with open('BACKTEST_ROC_RESULTS.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n" + "="*60)
        print("✅ Backtest complete! Results saved to BACKTEST_ROC_RESULTS.md")
        print("="*60)

if __name__ == "__main__":
    backtester = PolymarketROCBacktester()
    results = backtester.run_backtest_suite()
