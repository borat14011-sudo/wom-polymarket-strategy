#!/usr/bin/env python3
"""Extract recent file activity for dashboard"""
import json
from pathlib import Path
from datetime import datetime

def get_recent_activity(limit=10):
    """Get last N file activities from log"""
    try:
        log_file = Path("file_activity.log")
        
        if not log_file.exists():
            return []
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        activities = []
        for line in lines:
            line = line.strip()
            if line.startswith('[') and ']' in line:
                # Parse timestamp and message
                timestamp = line[1:line.index(']')]
                message = line[line.index(']')+2:]
                
                # Determine activity type
                activity_type = 'info'
                if 'CREATED' in message:
                    activity_type = 'created'
                elif 'MODIFIED' in message:
                    activity_type = 'modified'
                elif 'DELETED' in message:
                    activity_type = 'deleted'
                elif 'ERROR' in message or 'FAILED' in message:
                    activity_type = 'error'
                
                activities.append({
                    'timestamp': timestamp,
                    'message': message,
                    'type': activity_type
                })
        
        # Return last N activities
        return activities[-limit:]
    
    except Exception as e:
        return [{'timestamp': 'Error', 'message': str(e), 'type': 'error'}]

if __name__ == '__main__':
    # Generate file_activity.json for dashboard
    while True:
        import time
        
        activities = get_recent_activity(15)
        
        with open('file_activity.json', 'w') as f:
            json.dump(activities, f, indent=2)
        
        time.sleep(3)  # Update every 3 seconds
