# COMMUNICATION_HUB.py - Tier 2: User Interface & Logger
# 📡 Always-On Communication System

import json
import datetime
import os

class CommunicationHub:
    """
    Always-on communication hub
    Logs all activities, coordinates agents, responds to user
    """
    
    def __init__(self):
        self.activity_log = []
        self.start_time = datetime.datetime.now()
        self.status = "ACTIVE"
        
        print("="*60)
        print("COMMUNICATION HUB DEPLOYED")
        print("="*60)
        print(f"Start Time: {self.start_time}")
        print(f"Status: {self.status}")
        print(f"Log File: communication_hub.log")
        print()
        
    def log_activity(self, source, action, details, importance="NORMAL"):
        """Log all agent activities"""
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "source": source,
            "action": action,
            "details": details,
            "importance": importance
        }
        
        self.activity_log.append(entry)
        
        # Write to file
        with open("communication_hub.log", "a") as f:
            f.write(f"[{entry['timestamp']}] [{source}] [{importance}] {action}: {details}\n")
            
        print(f"LOGGED: [{source}] {action}")
        
    def receive_user_request(self, request, complexity="MEDIUM"):
        """Receive and route user requests"""
        self.log_activity("USER", "REQUEST_RECEIVED", request, "HIGH")
        
        # Route based on complexity
        if complexity == "HIGH":
            route_to = "STRATEGIC_ORCHESTRATOR (Kimi K2.5)"
        elif complexity == "MEDIUM":
            route_to = "EXECUTION_ARMY (Specialized Agent)"
        else:
            route_to = "DIRECT_RESPONSE"
            
        self.log_activity("COMMUNICATION_HUB", "REQUEST_ROUTED", f"To: {route_to}", "NORMAL")
        
        return {
            "request": request,
            "complexity": complexity,
            "routed_to": route_to,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
    def aggregate_results(self, agent_results, user_request):
        """Aggregate results from multiple agents"""
        self.log_activity("COMMUNICATION_HUB", "AGGREGATING_RESULTS", f"From {len(agent_results)} agents", "NORMAL")
        
        aggregated = {
            "timestamp": datetime.datetime.now().isoformat(),
            "original_request": user_request,
            "agent_count": len(agent_results),
            "results": agent_results,
            "summary": self.generate_summary(agent_results)
        }
        
        self.log_activity("COMMUNICATION_HUB", "RESULTS_AGGREGATED", f"Summary: {aggregated['summary'][:100]}", "NORMAL")
        
        return aggregated
        
    def generate_summary(self, results):
        """Generate summary of agent results"""
        summary_parts = []
        for agent, result in results.items():
            status = result.get('status', 'UNKNOWN')
            summary_parts.append(f"{agent}: {status}")
        return " | ".join(summary_parts)
        
    def get_status_dashboard(self):
        """Generate real-time status dashboard"""
        uptime = datetime.datetime.now() - self.start_time
        recent_logs = [log for log in self.activity_log if 
                      (datetime.datetime.now() - datetime.datetime.fromisoformat(log['timestamp'])).seconds < 3600]
        
        dashboard = {
            "status": self.status,
            "uptime": str(uptime),
            "total_logs": len(self.activity_log),
            "recent_activity_1h": len(recent_logs),
            "last_activity": self.activity_log[-1] if self.activity_log else None
        }
        
        return dashboard
        
    def respond_to_user(self, message, data=None):
        """Format and send response to user"""
        self.log_activity("COMMUNICATION_HUB", "RESPONSE_SENT", message[:50], "NORMAL")
        
        response = {
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
            "data": data,
            "hub_status": self.status
        }
        
        return response

# Singleton instance
communication_hub = CommunicationHub()

if __name__ == "__main__":
    # Test the hub
    print("\n" + "="*60)
    print("TESTING COMMUNICATION HUB")
    print("="*60)
    
    # Simulate user request
    request = hub.receive_user_request("Find Musk markets", complexity="MEDIUM")
    print(f"Routed to: {request['routed_to']}")
    
    # Simulate agent response
    hub.log_activity("MARKET_SCANNER", "SCAN_COMPLETE", "Found 8 Musk markets", "HIGH")
    
    # Get status
    status = hub.get_status_dashboard()
    print(f"\nHub Status: {status}")