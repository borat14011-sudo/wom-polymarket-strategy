#!/usr/bin/env python3
"""
Polymarket Continuous Background Optimizer
20-minute session for live trading monitoring
Tasks:
1. Monitor active positions every 5 minutes
2. Scan for extreme probability opportunities (<10% or >90%)
3. Update live tracker data
4. Look for new 2026 markets
5. Track price movements
6. Log all activities
"""

import json
import sqlite3
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('optimization_session.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Agent Stack Configuration
AGENT_STACK = {
    "strategic_orchestrator": {"model": "Kimi 2.5", "role": "decisions"},
    "market_scanner": {"model": "Kimi 2.5", "role": "live_data"},
    "data_validator": {"model": "Kimi 2.5", "role": "accuracy"},
    "communication_hub": {"model": "Kimi 2.5", "role": "logging"},
    "memory_manager": {"model": "Kimi 2.5", "role": "checkpoints"}
}

@dataclass
class Position:
    """Active trading position"""
    market_id: str
    market_name: str
    entry_price: float
    current_price: float
    size: float
    entry_time: str
    sector: str
    
    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.size
    
    @property
    def unrealized_pnl_pct(self) -> float:
        if self.entry_price == 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100

class PolymarketOptimizer:
    """Continuous optimization agent for Polymarket trading"""
    
    def __init__(self, session_duration_minutes: int = 20, check_interval_minutes: int = 5):
        self.session_duration = session_duration_minutes
        self.check_interval = check_interval_minutes
        self.start_time = datetime.now()
        self.check_count = 0
        self.findings = []
        self.price_history = {}  # Track price movements
        
        # Load active positions (simulated - in real system, load from DB)
        self.active_positions = self._load_active_positions()
        
        logger.info(f"🚀 Optimization Session Started")
        logger.info(f"   Duration: {session_duration_minutes} minutes")
        logger.info(f"   Check Interval: {check_interval_minutes} minutes")
        logger.info(f"   Active Positions: {len(self.active_positions)}")
        logger.info(f"   Agent Stack: {len(AGENT_STACK)} agents ready")
    
    def _load_active_positions(self) -> List[Position]:
        """Load active positions from tracker or config"""
        # Check for Elon positions in existing data
        positions = []
        
        # Load from position tracker if exists
        try:
            conn = sqlite3.connect("positions.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM positions WHERE market_id LIKE '%elon%' OR market_id LIKE '%musk%'")
            rows = cursor.fetchall()
            for row in rows:
                positions.append(Position(
                    market_id=row[1],
                    market_name=row[1],
                    entry_price=row[2],
                    current_price=row[3],
                    size=row[4],
                    entry_time=row[5],
                    sector="Elon"
                ))
            conn.close()
        except:
            pass
        
        # If no Elon positions found, scan active markets for Elon-related
        if not positions:
            logger.info("   [Memory Manager] No existing Elon positions found - will scan markets")
        
        return positions
    
    def fetch_polymarket_data(self) -> List[Dict]:
        """Fetch live market data from Polymarket CLOB API"""
        try:
            # Primary endpoint
            response = requests.get(
                "https://clob.polymarket.com/markets",
                timeout=30,
                headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
        except Exception as e:
            logger.error(f"   [Market Scanner] API fetch failed: {e}")
        
        # Fallback: try gamma API
        try:
            response = requests.get(
                "https://gamma-api.polymarket.com/markets",
                timeout=30,
                headers={"Accept": "application/json"}
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"   [Market Scanner] Gamma API fetch failed: {e}")
        
        return []
    
    def scan_extreme_probabilities(self, markets: List[Dict]) -> List[Dict]:
        """Scan for markets with extreme probabilities (<10% or >90%)"""
        opportunities = []
        
        for market in markets:
            try:
                # Get price/outcome data
                outcomes = market.get("outcomes", "[]")
                prices = market.get("outcomePrices", "[]")
                
                if isinstance(outcomes, str):
                    import ast
                    try:
                        outcomes = ast.literal_eval(outcomes)
                        prices = ast.literal_eval(prices)
                    except:
                        continue
                
                # Check each outcome
                for i, (outcome, price_str) in enumerate(zip(outcomes, prices)):
                    try:
                        price = float(price_str)
                        
                        # Extreme probability detection
                        if price <= 0.10:  # < 10%
                            opportunities.append({
                                "type": "EXTREME_LOW",
                                "market_id": market.get("id"),
                                "question": market.get("question", "")[:80],
                                "outcome": outcome,
                                "probability": price,
                                "end_date": market.get("endDateIso", "N/A"),
                                "liquidity": market.get("liquidityNum", 0),
                                "opportunity": "Potential NO position if mispriced"
                            })
                        elif price >= 0.90:  # > 90%
                            opportunities.append({
                                "type": "EXTREME_HIGH",
                                "market_id": market.get("id"),
                                "question": market.get("question", "")[:80],
                                "outcome": outcome,
                                "probability": price,
                                "end_date": market.get("endDateIso", "N/A"),
                                "liquidity": market.get("liquidityNum", 0),
                                "opportunity": "Potential YES position if certain"
                            })
                    except:
                        continue
                        
            except Exception as e:
                continue
        
        return sorted(opportunities, key=lambda x: x["probability"])
    
    def find_2026_markets(self, markets: List[Dict]) -> List[Dict]:
        """Find markets with 2026 end dates"""
        markets_2026 = []
        
        for market in markets:
            end_date = market.get("endDateIso", "") or market.get("endDate", "")
            if end_date and "2026" in str(end_date):
                markets_2026.append({
                    "market_id": market.get("id"),
                    "question": market.get("question", "")[:80],
                    "end_date": end_date,
                    "liquidity": market.get("liquidityNum", 0),
                    "volume_24h": market.get("volume24hr", 0),
                    "active": market.get("active", False)
                })
        
        return sorted(markets_2026, key=lambda x: x.get("liquidity", 0), reverse=True)
    
    def find_elon_markets(self, markets: List[Dict]) -> List[Dict]:
        """Find Elon Musk related markets"""
        elon_keywords = ["elon", "musk", "tesla", "spacex", "twitter", "x.com"]
        elon_markets = []
        
        for market in markets:
            question = market.get("question", "").lower()
            if any(keyword in question for keyword in elon_keywords):
                elon_markets.append({
                    "market_id": market.get("id"),
                    "question": market.get("question", ""),
                    "end_date": market.get("endDateIso", "N/A"),
                    "liquidity": market.get("liquidityNum", 0),
                    "outcomes": market.get("outcomes", "[]"),
                    "prices": market.get("outcomePrices", "[]")
                })
        
        return elon_markets
    
    def track_price_movements(self, markets: List[Dict]):
        """Track price movements for active positions"""
        movements = []
        
        for position in self.active_positions:
            for market in markets:
                if market.get("id") == position.market_id:
                    try:
                        prices_str = market.get("outcomePrices", "[]")
                        if isinstance(prices_str, str):
                            import ast
                            prices = ast.literal_eval(prices_str)
                        else:
                            prices = prices_str
                        
                        current_price = float(prices[0]) if prices else position.current_price
                        
                        # Calculate movement
                        price_change = current_price - position.current_price
                        price_change_pct = (price_change / position.current_price) * 100 if position.current_price else 0
                        
                        if abs(price_change_pct) > 1:  # Log if > 1% change
                            movements.append({
                                "market_id": position.market_id,
                                "old_price": position.current_price,
                                "new_price": current_price,
                                "change_pct": price_change_pct,
                                "unrealized_pnl": (current_price - position.entry_price) * position.size
                            })
                            
                            # Update position
                            position.current_price = current_price
                    except:
                        continue
        
        return movements
    
    def create_checkpoint(self, check_num: int, data: Dict):
        """Create memory checkpoint"""
        checkpoint = {
            "timestamp": datetime.now().isoformat(),
            "check_number": check_num,
            "session_elapsed_minutes": (datetime.now() - self.start_time).total_seconds() / 60,
            "data": data
        }
        
        # Save to memory file
        try:
            with open(f"optimization_checkpoint_{check_num}.json", "w") as f:
                json.dump(checkpoint, f, indent=2)
        except Exception as e:
            logger.error(f"   [Memory Manager] Checkpoint save failed: {e}")
        
        return checkpoint
    
    def run_check(self) -> Dict:
        """Execute one optimization check cycle"""
        self.check_count += 1
        check_start = datetime.now()
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🔍 CHECK #{self.check_count} - {check_start.strftime('%H:%M:%S')}")
        logger.info(f"{'='*60}")
        
        # 1. Fetch live data
        logger.info("📡 [Market Scanner] Fetching live market data...")
        markets = self.fetch_polymarket_data()
        logger.info(f"   ✓ Retrieved {len(markets)} markets")
        
        results = {
            "check_number": self.check_count,
            "timestamp": check_start.isoformat(),
            "markets_scanned": len(markets)
        }
        
        # 2. Monitor active positions
        logger.info("💼 [Data Validator] Monitoring active positions...")
        if self.active_positions:
            for pos in self.active_positions:
                logger.info(f"   📊 {pos.market_name[:50]}: ${pos.current_price:.4f} "
                          f"(P&L: ${pos.unrealized_pnl:+.2f}, {pos.unrealized_pnl_pct:+.2f}%)")
        else:
            logger.info("   ⚠ No active Elon positions to monitor")
        
        # Track price movements
        movements = self.track_price_movements(markets)
        if movements:
            logger.info(f"   🔄 Price movements detected: {len(movements)}")
            for m in movements:
                logger.info(f"      {m['market_id'][:40]}: {m['change_pct']:+.2f}%")
        results["price_movements"] = movements
        
        # 3. Scan for extreme probabilities
        logger.info("🎯 [Strategic Orchestrator] Scanning for extreme opportunities...")
        extreme_opps = self.scan_extreme_probabilities(markets)
        high_confidence = [o for o in extreme_opps if o["probability"] <= 0.05 or o["probability"] >= 0.95]
        
        logger.info(f"   ✓ Found {len(extreme_opps)} extreme probability markets")
        logger.info(f"   ✓ {len(high_confidence)} high-confidence opportunities (>95% or <5%)")
        
        if high_confidence[:3]:  # Show top 3
            for opp in high_confidence[:3]:
                emoji = "🔴" if opp["type"] == "EXTREME_LOW" else "🟢"
                logger.info(f"   {emoji} {opp['probability']:.1%} - {opp['question'][:60]}")
        
        results["extreme_opportunities"] = extreme_opps
        results["high_confidence_count"] = len(high_confidence)
        
        # 4. Find 2026 markets
        logger.info("📅 [Market Scanner] Looking for 2026 markets...")
        markets_2026 = self.find_2026_markets(markets)
        logger.info(f"   ✓ Found {len(markets_2026)} markets ending in 2026")
        
        if markets_2026[:5]:  # Show top 5 by liquidity
            for m in markets_2026[:5]:
                logger.info(f"   📆 {m['question'][:50]}... (Liquidity: ${m['liquidity']:,.0f})")
        
        results["markets_2026"] = markets_2026[:10]  # Store top 10
        
        # 5. Find Elon markets (for potential new positions)
        logger.info("🚀 [Market Scanner] Scanning for Elon-related markets...")
        elon_markets = self.find_elon_markets(markets)
        logger.info(f"   ✓ Found {len(elon_markets)} Elon-related markets")
        
        if elon_markets[:3]:
            for m in elon_markets[:3]:
                logger.info(f"   🚀 {m['question'][:60]}")
        
        results["elon_markets"] = elon_markets[:5]
        
        # 6. Create checkpoint
        logger.info("💾 [Memory Manager] Creating checkpoint...")
        checkpoint = self.create_checkpoint(self.check_count, results)
        logger.info(f"   ✓ Checkpoint #{self.check_count} saved")
        
        # 7. Log summary
        check_duration = (datetime.now() - check_start).total_seconds()
        logger.info(f"\n✅ Check #{self.check_count} complete in {check_duration:.1f}s")
        
        return results
    
    def generate_final_report(self, all_results: List[Dict]) -> Dict:
        """Generate final optimization report"""
        logger.info(f"\n{'='*60}")
        logger.info("📊 FINAL OPTIMIZATION REPORT")
        logger.info(f"{'='*60}")
        
        total_opportunities = sum(len(r.get("extreme_opportunities", [])) for r in all_results)
        total_movements = sum(len(r.get("price_movements", [])) for r in all_results)
        all_2026_markets = []
        for r in all_results:
            all_2026_markets.extend(r.get("markets_2026", []))
        
        # Unique 2026 markets
        unique_2026 = {m["market_id"]: m for m in all_2026_markets}
        
        report = {
            "session_summary": {
                "duration_minutes": self.session_duration,
                "checks_completed": self.check_count,
                "start_time": self.start_time.isoformat(),
                "end_time": datetime.now().isoformat()
            },
            "statistics": {
                "total_opportunities_scanned": total_opportunities,
                "total_price_movements": total_movements,
                "unique_2026_markets": len(unique_2026),
                "active_positions_monitored": len(self.active_positions)
            },
            "key_findings": {
                "top_2026_markets": list(unique_2026.values())[:10],
                "session_highlights": self.findings
            },
            "recommendations": self._generate_recommendations(all_results)
        }
        
        # Log summary
        logger.info(f"\n📈 Session Statistics:")
        logger.info(f"   ⏱️  Duration: {self.session_duration} minutes")
        logger.info(f"   🔍 Checks: {self.check_count}")
        logger.info(f"   🎯 Opportunities: {total_opportunities}")
        logger.info(f"   🔄 Price Movements: {total_movements}")
        logger.info(f"   📅 2026 Markets: {len(unique_2026)}")
        
        logger.info(f"\n💡 Agent Performance:")
        for agent, config in AGENT_STACK.items():
            logger.info(f"   ✓ {agent.replace('_', ' ').title()}: {config['role']} ready")
        
        # Save report
        with open("optimization_final_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n✅ Report saved to optimization_final_report.json")
        
        return report
    
    def _generate_recommendations(self, all_results: List[Dict]) -> List[str]:
        """Generate trading recommendations based on findings"""
        recommendations = []
        
        # Find high-confidence opportunities
        high_conf = []
        for r in all_results:
            for opp in r.get("extreme_opportunities", []):
                if opp["probability"] <= 0.05 or opp["probability"] >= 0.95:
                    high_conf.append(opp)
        
        if high_conf:
            recommendations.append(f"Found {len(high_conf)} high-confidence opportunities (>95% or <5%)")
        
        # Check 2026 markets
        markets_2026 = set()
        for r in all_results:
            for m in r.get("markets_2026", []):
                markets_2026.add(m["market_id"])
        
        if markets_2026:
            recommendations.append(f"{len(markets_2026)} unique 2026 markets available for future positioning")
        
        # Price movement alerts
        movements = []
        for r in all_results:
            movements.extend(r.get("price_movements", []))
        
        if movements:
            avg_change = sum(m["change_pct"] for m in movements) / len(movements)
            recommendations.append(f"Average position movement: {avg_change:+.2f}%")
        
        if not recommendations:
            recommendations.append("Markets stable - no immediate action required")
        
        return recommendations
    
    def run(self):
        """Run the full optimization session"""
        all_results = []
        
        logger.info(f"\n{'='*60}")
        logger.info("🚀 STARTING POLYMARKET OPTIMIZATION SESSION")
        logger.info(f"{'='*60}")
        
        # Calculate number of checks
        num_checks = self.session_duration // self.check_interval
        
        for i in range(num_checks):
            # Run check
            result = self.run_check()
            all_results.append(result)
            
            # Check if session complete
            elapsed = (datetime.now() - self.start_time).total_seconds() / 60
            if elapsed >= self.session_duration:
                logger.info("⏰ Session duration reached")
                break
            
            # Wait for next check
            if i < num_checks - 1:
                wait_time = self.check_interval * 60
                logger.info(f"\n⏳ Waiting {self.check_interval} minutes until next check...")
                time.sleep(wait_time)
        
        # Generate final report
        report = self.generate_final_report(all_results)
        
        logger.info(f"\n{'='*60}")
        logger.info("🏁 OPTIMIZATION SESSION COMPLETE")
        logger.info(f"{'='*60}")
        
        return report

if __name__ == "__main__":
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=int, default=20, help="Session duration in minutes")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in minutes")
    args = parser.parse_args()
    
    # Run optimizer
    optimizer = PolymarketOptimizer(
        session_duration_minutes=args.duration,
        check_interval_minutes=args.interval
    )
    
    try:
        report = optimizer.run()
        print(f"\n✅ Optimization complete! Report saved to optimization_final_report.json")
    except KeyboardInterrupt:
        print("\n\n⚠️ Session interrupted by user")
    except Exception as e:
        logger.error(f"Session error: {e}")
        raise
