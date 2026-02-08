"""
DATA COLLECTION ORCHESTRATOR
Coordinates incremental scraping and snapshot collection
Runs on a schedule to build dataset over time
"""
import time
import schedule
from datetime import datetime
from incremental_scraper import IncrementalScraper
from snapshot_collector import SnapshotCollector

class DataCollectionOrchestrator:
    """Coordinates all data collection tasks"""
    
    def __init__(self):
        self.scraper = IncrementalScraper()
        self.collector = SnapshotCollector()
    
    def task_full_market_scan(self):
        """Task: Scan all active markets (every 6 hours)"""
        print(f"\n{'='*60}")
        print(f"[SCAN] FULL MARKET SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        self.scraper.run_full_collection(max_markets=5000)
    
    def task_snapshot_round(self):
        """Task: Snapshot top 100 markets (every 1 hour)"""
        print(f"\n{'='*60}")
        print(f"[SNAPSHOT] ROUND - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        self.collector.run_snapshot_round()
    
    def task_print_stats(self):
        """Task: Print database stats (every 12 hours)"""
        print(f"\n{'='*60}")
        print(f"[STATS] DATABASE STATS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print('='*60)
        
        self.scraper.print_stats()
    
    def run_scheduled(self):
        """Run on schedule (recommended for production)"""
        print("[START] Scheduled data collection...")
        print("\nSchedule:")
        print("  - Full market scan: Every 6 hours")
        print("  - Price snapshots: Every 1 hour")
        print("  - Stats report: Every 12 hours")
        print("\nPress Ctrl+C to stop\n")
        
        # Schedule tasks
        schedule.every(6).hours.do(self.task_full_market_scan)
        schedule.every(1).hours.do(self.task_snapshot_round)
        schedule.every(12).hours.do(self.task_print_stats)
        
        # Run initial tasks immediately
        print("Running initial scan...")
        self.task_full_market_scan()
        self.task_snapshot_round()
        
        # Run scheduled loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                print("\n⚠️ Stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in scheduler: {e}")
                time.sleep(300)  # Wait 5 min on error
    
    def run_aggressive(self):
        """Run aggressive collection (fast data acquisition)"""
        print("[START] AGGRESSIVE data collection...")
        print("\nSchedule:")
        print("  - Full market scan: Every 1 hour")
        print("  - Price snapshots: Every 15 minutes")
        print("\nPress Ctrl+C to stop\n")
        
        # More frequent schedule
        schedule.every(1).hours.do(self.task_full_market_scan)
        schedule.every(15).minutes.do(self.task_snapshot_round)
        schedule.every(6).hours.do(self.task_print_stats)
        
        # Run initial tasks
        print("Running initial aggressive scan...")
        self.task_full_market_scan()
        self.task_snapshot_round()
        
        # Run loop
        while True:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except KeyboardInterrupt:
                print("\n⚠️ Stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in scheduler: {e}")
                time.sleep(300)


def main():
    """Run orchestrator"""
    import sys
    
    orchestrator = DataCollectionOrchestrator()
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'scheduled'
    
    if mode == 'aggressive':
        orchestrator.run_aggressive()
    elif mode == 'once':
        # Run one round of each task
        orchestrator.task_full_market_scan()
        orchestrator.task_snapshot_round()
        orchestrator.task_print_stats()
    else:
        orchestrator.run_scheduled()


if __name__ == "__main__":
    # Recommended: python data_collection_orchestrator.py scheduled
    # Fast mode: python data_collection_orchestrator.py aggressive
    # One-time: python data_collection_orchestrator.py once
    main()
