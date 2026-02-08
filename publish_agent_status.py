#!/usr/bin/env python3
"""
Publish agent status to GitHub Pages every 30 seconds
"""
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

REPO_DIR = Path("agent-monitor-live")
SOURCE_JSON = Path("detailed_status.json")

def publish_status():
    """Copy latest status and push to GitHub"""
    try:
        # Copy latest JSON
        if SOURCE_JSON.exists():
            shutil.copy(SOURCE_JSON, REPO_DIR / "detailed_status.json")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Copied detailed_status.json")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Source JSON not found, skipping")
            return
        
        # Git add, commit, push
        subprocess.run(
            ["git", "add", "detailed_status.json"],
            cwd=REPO_DIR,
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            ["git", "commit", "-m", f"Update status {datetime.now().strftime('%H:%M:%S')}"],
            cwd=REPO_DIR,
            capture_output=True  # Don't check - commit might fail if no changes
        )
        
        result = subprocess.run(
            ["git", "push"],
            cwd=REPO_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✓ Pushed to GitHub")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Push result: {result.stderr[:100]}")
            
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")

def main():
    print("Starting GitHub Pages publisher...")
    print("Publishing agent status every 30 seconds\n")
    
    while True:
        try:
            publish_status()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nStopped by user")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == '__main__':
    main()
