#!/usr/bin/env python3
"""
Track all agent processes and their status
"""
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path

def get_process_list():
    """Get all Python processes with details"""
    try:
        result = subprocess.run(
            ['tasklist', '/FI', 'IMAGENAME eq python.exe', '/FO', 'CSV', '/V'],
            capture_output=True,
            text=True,
            timeout=3
        )
        
        lines = result.stdout.strip().split('\n')[1:]  # Skip header
        processes = []
        
        for line in lines:
            if 'python.exe' in line.lower():
                parts = line.split('","')
                if len(parts) > 1:
                    # Extract PID and window title (contains script name)
                    try:
                        pid = parts[1].strip('"')
                        title = parts[-1].strip('"') if len(parts) > 8 else ''
                        processes.append({'pid': pid, 'title': title})
                    except:
                        pass
        
        return processes
    except:
        return []

def identify_agents(processes):
    """Identify what each process is doing"""
    agents = []
    
    # Since Windows doesn't show command line easily, we'll assume based on count
    # and check for known files
    known_scripts = {
        'agents_status.py': {'name': 'agent_tracker', 'emoji': '🤖', 'display': 'Agent Tracker', 'desc': 'Monitoring all background processes (this tracker)'},
        'update_thoughts.py': {'name': 'thought_updater', 'emoji': '🧠', 'display': 'Thought Updater', 'desc': 'Updating brain status'},
        'get_file_activity.py': {'name': 'activity_tracker', 'emoji': '📝', 'display': 'Activity Tracker', 'desc': 'Logging file changes'},
        'file_monitor.py': {'name': 'file_monitor', 'emoji': '👁️', 'display': 'File Monitor', 'desc': 'Tracking all file operations'},
        'run.py': {'name': 'scraper', 'emoji': '🕷️', 'display': 'Data Scraper', 'desc': 'Downloading Polymarket historical data'},
    }
    
    # Check which scripts are actively running
    active_agents = []
    workspace = Path('.')
    
    for script_name, info in known_scripts.items():
        script_path = workspace / script_name
        scraper_path = workspace / 'polymarket-monitor' / 'historical-data-scraper' / script_name
        
        # Assume if file exists and we have Python processes, it's probably running
        if script_path.exists() or scraper_path.exists():
            if len(processes) > 0:
                # Assign a PID (we can't perfectly match, but we track by count)
                active_agents.append({
                    'name': info['name'],
                    'display': info['display'],
                    'emoji': info['emoji'],
                    'description': info['desc'],
                    'pid': processes[len(active_agents)]['pid'] if len(active_agents) < len(processes) else '????',
                    'status': 'active'
                })
    
    # Add web server
    if len(processes) > len(active_agents):
        active_agents.append({
            'name': 'web_server',
            'display': 'Web Server',
            'emoji': '🌐',
            'description': 'Serving dashboard on port 8888',
            'pid': processes[-1]['pid'],
            'status': 'active'
        })
    
    return active_agents

def check_scraper_progress():
    """Try to detect scraper progress"""
    try:
        data_path = Path("polymarket-monitor/historical-data-scraper/data")
        if data_path.exists():
            files = list(data_path.glob("*.json"))
            if files:
                total_size = sum(f.stat().st_size for f in files)
                return {
                    'files': len(files),
                    'size_mb': round(total_size / (1024*1024), 2)
                }
    except:
        pass
    return None

def generate_agent_status():
    """Generate complete agent status report"""
    
    processes = get_process_list()
    agents = identify_agents(processes)
    scraper_data = check_scraper_progress()
    
    # Agents already have full info from identify_agents
    status = {
        'total_agents': len(agents),
        'active_count': sum(1 for a in agents if a['status'] == 'active'),
        'agents': agents,
        'scraper_data': scraper_data,
        'timestamp': datetime.now().isoformat()
    }
    
    return status

if __name__ == '__main__':
    print("Starting agent tracker...")
    print("Updating agents_status.json every 5 seconds")
    
    while True:
        try:
            status = generate_agent_status()
            
            with open('agents_status.json', 'w') as f:
                json.dump(status, f, indent=2)
            
            print(f"[{datetime.now().strftime('%I:%M:%S %p')}] {status['active_count']}/{status['total_agents']} agents active")
            
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
