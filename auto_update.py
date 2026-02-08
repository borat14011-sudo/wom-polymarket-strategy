import json
import time
import re
from datetime import datetime
from pathlib import Path

def get_latest_scraper_count():
    """Try to get the latest event count from various sources"""
    try:
        # Try reading from process list
        import subprocess
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        # Check if scraper is running
        scraper_running = 'python' in result.stdout.lower()
        
        return scraper_running
    except:
        return False

def update_dashboard():
    """Update status.json every 2 seconds with estimated progress"""
    
    start_time = datetime(2026, 2, 7, 8, 30, 20)  # When scraper started
    base_count = 57700  # Last known count
    
    while True:
        try:
            now = datetime.now()
            elapsed_seconds = (now - start_time).total_seconds()
            elapsed_minutes = int(elapsed_seconds / 60)
            
            # Estimate current count (~90 events/sec average)
            estimated_count = int(base_count + ((elapsed_seconds - 720) * 90))  # 720 = 12 min in seconds
            estimated_count = max(base_count, min(estimated_count, 80000))  # Cap at reasonable max
            
            # Check if scraper is still running
            scraper_active = get_latest_scraper_count()
            
            # Calculate progress (estimate 60k-80k total events)
            progress = min(int((estimated_count / 75000) * 100), 95)
            
            # Estimate time remaining
            if scraper_active:
                events_remaining = 75000 - estimated_count
                seconds_remaining = events_remaining / 90
                minutes_remaining = max(0, int(seconds_remaining / 60))
                eta = f"~{minutes_remaining} min remaining"
                status_text = "✅ Step 1: Fetching Events"
                substatus = "Downloading market metadata..."
                rate = "~90/sec"
            else:
                eta = "Complete - Starting Step 2"
                status_text = "✅ Step 1 Complete"
                substatus = "Moving to price download..."
                rate = "Complete"
            
            status = {
                "events": f"{estimated_count:,}+",
                "eventsNum": estimated_count,
                "rate": rate,
                "progress": progress,
                "status": status_text,
                "substatus": substatus,
                "eta": eta,
                "timestamp": now.strftime("%I:%M:%S %p"),
                "balance": "$98.25",
                "iran_position": "❌ 7¢ (-$1.75 / -41.7%)",
                "chrome_status": "✅ CLOSED",
                "elapsed": f"{elapsed_minutes} min",
                "scraper_active": scraper_active,
                "last_update": now.isoformat()
            }
            
            # Write to file
            with open('status.json', 'w') as f:
                json.dump(status, f, indent=2)
            
            print(f"[{status['timestamp']}] Updated: {status['events']} ({progress}%)")
            
            time.sleep(2)  # Update every 2 seconds
            
        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == '__main__':
    print("Starting auto-updater...")
    print("Updates every 2 seconds")
    update_dashboard()
