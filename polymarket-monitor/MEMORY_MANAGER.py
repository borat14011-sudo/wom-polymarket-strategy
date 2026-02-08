# MEMORY_MANAGER.py - Tier 3: State Persistence & Checkpoint System
# 💾 Automated Memory Management

import json
import datetime
import os

class MemoryManager:
    """
    Automated memory management system
    Updates MEMORY.md and daily logs at key checkpoints
    """
    
    def __init__(self):
        self.checkpoints = []
        self.checkpoint_triggers = {
            "trade_execution": True,
            "strategy_decision": True,
            "performance_milestone": True,
            "system_change": True,
            "error_event": True,
            "end_of_day": True,
            "user_session_end": True
        }
        
        print("="*60)
        print("MEMORY MANAGER DEPLOYED")
        print("="*60)
        print(f"Checkpoint Triggers: {len(self.checkpoint_triggers)}")
        print(f"Memory File: C:/Users/Borat/.openclaw/workspace/MEMORY.md")
        print(f"Daily Logs: C:/Users/Borat/.openclaw/workspace/memory/")
        print()
        
    def create_checkpoint(self, trigger_type, data):
        """Create a checkpoint at key events"""
        if not self.checkpoint_triggers.get(trigger_type, False):
            return None
            
        checkpoint = {
            "timestamp": datetime.datetime.now().isoformat(),
            "trigger": trigger_type,
            "data": data,
            "session_id": self.get_session_id()
        }
        
        self.checkpoints.append(checkpoint)
        
        # Update appropriate memory file
        if trigger_type == "trade_execution":
            self.update_memory_trades(data)
        elif trigger_type == "strategy_decision":
            self.update_memory_strategy(data)
        elif trigger_type == "performance_milestone":
            self.update_memory_milestone(data)
        elif trigger_type == "end_of_day":
            self.create_daily_log(data)
        elif trigger_type == "system_change":
            self.update_memory_system(data)
        elif trigger_type == "error_event":
            self.update_memory_errors(data)
            
        print(f"CHECKPOINT CREATED: {trigger_type}")
        
        return checkpoint
        
    def get_session_id(self):
        """Generate unique session ID"""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def update_memory_trades(self, trade_data):
        """Update MEMORY.md with trade execution"""
        memory_path = "C:/Users/Borat/.openclaw/workspace/MEMORY.md"
        
        trade_entry = f"""
### Trade Executed - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Market:** {trade_data.get('market', 'N/A')}
- **Position:** {trade_data.get('position', 'N/A')} at {trade_data.get('price', 'N/A')}
- **Size:** ${trade_data.get('size', 0)}
- **Expected ROI:** {trade_data.get('expected_roi', 'N/A')}
- **Strategy:** {trade_data.get('strategy', 'N/A')}
"""
        
        # Append to MEMORY.md
        with open(memory_path, "a") as f:
            f.write(trade_entry)
            
        print(f"  -> MEMORY.md updated with trade")
        
    def update_memory_strategy(self, strategy_data):
        """Update MEMORY.md with strategy decision"""
        memory_path = "C:/Users/Borat/.openclaw/workspace/MEMORY.md"
        
        strategy_entry = f"""
### Strategy Decision - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Decision:** {strategy_data.get('decision', 'N/A')}
- **Rationale:** {strategy_data.get('rationale', 'N/A')[:100]}...
- **Expected Outcome:** {strategy_data.get('expected_outcome', 'N/A')}
"""
        
        with open(memory_path, "a") as f:
            f.write(strategy_entry)
            
        print(f"  -> MEMORY.md updated with strategy")
        
    def update_memory_milestone(self, milestone_data):
        """Update MEMORY.md with performance milestone"""
        memory_path = "C:/Users/Borat/.openclaw/workspace/MEMORY.md"
        
        milestone_entry = f"""
### PERFORMANCE MILESTONE - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Achievement:** {milestone_data.get('achievement', 'N/A')}
- **Portfolio Value:** ${milestone_data.get('portfolio_value', 0)}
- **Return:** {milestone_data.get('return_pct', 0)}%
- **Trades:** {milestone_data.get('total_trades', 0)}
- **Win Rate:** {milestone_data.get('win_rate', 0)}%
"""
        
        with open(memory_path, "a") as f:
            f.write(milestone_entry)
            
        print(f"  -> MEMORY.md updated with milestone")
        
    def create_daily_log(self, day_data):
        """Create daily log file"""
        log_dir = "C:/Users/Borat/.openclaw/workspace/memory"
        os.makedirs(log_dir, exist_ok=True)
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        log_file = f"{log_dir}/{date_str}.md"
        
        log_entry = f"""# Daily Log - {date_str}

## Summary
- **Trades Executed:** {day_data.get('trades_count', 0)}
- **Portfolio Value:** ${day_data.get('portfolio_value', 0)}
- **Daily P&L:** ${day_data.get('daily_pnl', 0)} ({day_data.get('daily_return', 0)}%)
- **Active Positions:** {day_data.get('active_positions', 0)}

## Key Events
{chr(10).join(['- ' + event for event in day_data.get('events', [])])}

## Next Steps
{chr(10).join(['- ' + step for step in day_data.get('next_steps', [])])}
"""
        
        with open(log_file, "w") as f:
            f.write(log_entry)
            
        print(f"  -> Daily log created: {log_file}")
        
    def update_memory_system(self, system_data):
        """Update MEMORY.md with system changes"""
        memory_path = "C:/Users/Borat/.openclaw/workspace/MEMORY.md"
        
        system_entry = f"""
### System Update - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Change:** {system_data.get('change', 'N/A')}
- **Impact:** {system_data.get('impact', 'N/A')}
- **Files Modified:** {', '.join(system_data.get('files', []))}
"""
        
        with open(memory_path, "a") as f:
            f.write(system_entry)
            
        print(f"  -> MEMORY.md updated with system change")
        
    def update_memory_errors(self, error_data):
        """Update MEMORY.md with error events"""
        memory_path = "C:/Users/Borat/.openclaw/workspace/MEMORY.md"
        
        error_entry = f"""
### Error Event - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
- **Error:** {error_data.get('error', 'N/A')}
- **Source:** {error_data.get('source', 'N/A')}
- **Resolution:** {error_data.get('resolution', 'Pending')}
"""
        
        with open(memory_path, "a") as f:
            f.write(error_entry)
            
        print(f"  -> MEMORY.md updated with error")

# Singleton instance
memory_manager = MemoryManager()

if __name__ == "__main__":
    # Test the memory manager
    print("\n" + "="*60)
    print("TESTING MEMORY MANAGER")
    print("="*60)
    
    # Simulate trade execution checkpoint
    mm.create_checkpoint("trade_execution", {
        "market": "Musk tweet 800+",
        "position": "NO",
        "price": "0.08",
        "size": 2,
        "expected_roi": "+1,150%",
        "strategy": "MUSK_HYPE_FADE"
    })
    
    print(f"\nTotal Checkpoints: {len(mm.checkpoints)}")