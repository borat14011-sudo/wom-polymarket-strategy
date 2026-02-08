#!/usr/bin/env python3
"""
File Activity Monitor for Borat
Logs all file operations in the workspace
"""
import os
import time
from datetime import datetime
from pathlib import Path
import hashlib

LOG_FILE = "file_activity.log"
WORKSPACE = Path("C:/Users/Borat/.openclaw/workspace")
CHECK_INTERVAL = 5  # seconds

def get_file_hash(filepath):
    """Get MD5 hash of file for change detection"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except:
        return None

def get_file_size(filepath):
    """Get human-readable file size"""
    try:
        size = os.path.getsize(filepath)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def log_activity(message):
    """Append to activity log with timestamp"""
    timestamp = datetime.now().strftime("%I:%M:%S %p")
    line = f"[{timestamp}] {message}\n"
    
    with open(LOG_FILE, 'a') as f:
        f.write(line)
    
    print(line.strip())

def scan_directory(path, known_files):
    """Recursively scan directory for changes"""
    changes = []
    current_files = {}
    
    try:
        for root, dirs, files in os.walk(path):
            # Skip git, node_modules, etc
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__']]
            
            for filename in files:
                filepath = Path(root) / filename
                relative_path = filepath.relative_to(WORKSPACE)
                
                # Skip log files and temp files
                if filename.endswith('.log') or filename.startswith('~'):
                    continue
                
                try:
                    stat = filepath.stat()
                    file_info = {
                        'size': stat.st_size,
                        'mtime': stat.st_mtime,
                        'hash': get_file_hash(filepath)
                    }
                    
                    current_files[str(relative_path)] = file_info
                    
                    # Check for changes
                    if str(relative_path) not in known_files:
                        # New file
                        size = get_file_size(filepath)
                        changes.append(f"CREATED: {relative_path} ({size})")
                    
                    elif known_files[str(relative_path)]['hash'] != file_info['hash']:
                        # Modified file
                        size = get_file_size(filepath)
                        changes.append(f"MODIFIED: {relative_path} ({size})")
                
                except Exception as e:
                    pass
    
    except Exception as e:
        log_activity(f"ERROR scanning directory: {e}")
    
    # Check for deleted files
    for filepath in known_files:
        if filepath not in current_files:
            changes.append(f"DELETED: {filepath}")
    
    return current_files, changes

def monitor_workspace():
    """Main monitoring loop"""
    log_activity("=== FILE MONITOR STARTED ===")
    log_activity(f"Monitoring: {WORKSPACE}")
    log_activity(f"Check interval: {CHECK_INTERVAL} seconds")
    log_activity("")
    
    known_files = {}
    
    # Initial scan
    known_files, _ = scan_directory(WORKSPACE, {})
    log_activity(f"Initial scan: {len(known_files)} files tracked")
    log_activity("")
    
    while True:
        try:
            time.sleep(CHECK_INTERVAL)
            
            known_files, changes = scan_directory(WORKSPACE, known_files)
            
            if changes:
                log_activity("--- FILE CHANGES DETECTED ---")
                for change in changes:
                    log_activity(change)
                log_activity("")
        
        except KeyboardInterrupt:
            log_activity("=== FILE MONITOR STOPPED ===")
            break
        
        except Exception as e:
            log_activity(f"ERROR: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    print("Starting file activity monitor...")
    print(f"Monitoring: {WORKSPACE}")
    print(f"Log file: {LOG_FILE}")
    print("Press Ctrl+C to stop\n")
    
    monitor_workspace()
