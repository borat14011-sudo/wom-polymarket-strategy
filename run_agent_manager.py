#!/usr/bin/env python3
"""
Wrapper script for cron jobs to run the agent manager
"""

import subprocess
import sys
import os

print("="*60)
print("RUNNING POLYMARKET AGENT MANAGER")
print("="*60)

# Run the fixed agent manager
try:
    result = subprocess.run(
        [sys.executable, "agent_manager_fixed.py"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print(result.stdout)
    
    if result.stderr:
        print("\nSTDERR:")
        print(result.stderr)
    
    print(f"\nReturn code: {result.returncode}")
    
    # Exit with same code
    sys.exit(result.returncode)
    
except subprocess.TimeoutExpired:
    print("[ERROR] Agent manager timed out after 30 seconds")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Failed to run agent manager: {e}")
    sys.exit(1)