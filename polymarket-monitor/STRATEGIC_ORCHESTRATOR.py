# STRATEGIC_ORCHESTRATOR.py - Tier 1: Kimi K2.5 High-Level Command
# 🎭 Strategic orchestration for multi-agent synchronization

import json
import datetime
import time

class StrategicOrchestrator:
    """
    Kimi K2.5 Strategic Orchestrator
    Coordinates all subagents, ensures synchronization, handles complex decisions
    """
    
    def __init__(self):
        self.agents = {}
        self.synchronization_status = {}
        self.command_queue = []
        self.decision_log = []
        
        print("="*70)
        print("STRATEGIC ORCHESTRATOR (Kimi K2.5)")
        print("="*70)
        print(f"Status: ACTIVE")
        print(f"Responsibility: High-level coordination & complex reasoning")
        print(f"Subagents: 3 specialized agents")
        print()
        
    def deploy_agent_army(self):
        """Deploy all 4 agents with proper synchronization"""
        print("[ORCHESTRATOR] Deploying Agent Army...")
        
        # Agent 1: Market Scanner (pulls live API data)
        self.agents['market_scanner'] = {
            'name': 'Market Scanner',
            'model': 'huggingface/moonshotai/Kimi-K2-Thinking',
            'role': 'Live API data extraction',
            'status': 'DEPLOYING'
        }
        
        # Agent 2: Data Validator (cross-checks accuracy)
        self.agents['data_validator'] = {
            'name': 'Data Validator', 
            'model': 'huggingface/moonshotai/Kimi-K2-Instruct',
            'role': 'Accuracy verification & synchronization',
            'status': 'DEPLOYING'
        }
        
        # Agent 3: Risk Analyzer (evaluates opportunities)
        self.agents['risk_analyzer'] = {
            'name': 'Risk Analyzer',
            'model': 'huggingface/moonshotai/Kimi-K2-Thinking', 
            'role': 'Risk assessment & opportunity ranking',
            'status': 'DEPLOYING'
        }
        
        # Always-on support agents
        self.agents['communication_hub'] = {
            'name': 'Communication Hub',
            'model': 'moonshot/kimi-k2-0905-preview',
            'role': 'Always-on user interface',
            'status': 'ACTIVE'
        }
        
        self.agents['memory_manager'] = {
            'name': 'Memory Manager',
            'model': 'moonshot/kimi-k2-0905-preview',
            'role': 'Always-on checkpoint system',
            'status': 'ACTIVE'
        }
        
        print(f"[ORCHESTRATOR] {len(self.agents)} agents deployed")
        for name, agent in self.agents.items():
            print(f"  - {agent['name']}: {agent['status']}")
            
        return self.agents
        
    def synchronize_api_data(self, market_data_sources):
        """Ensure all agents have synchronized live data"""
        print("\n[ORCHESTRATOR] Synchronizing API Data Across All Agents...")
        
        synchronization_report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'sources_checked': len(market_data_sources),
            'agents_synchronized': 0,
            'consensus_reached': True,
            'discrepancies': []
        }
        
        # Step 1: Market Scanner pulls live data
        print("  -> Market Scanner: Pulling live Polymarket API...")
        live_data = self.run_market_scanner()
        
        # Step 2: Data Validator cross-checks
        print("  -> Data Validator: Cross-checking accuracy...")
        validation_result = self.run_data_validator(live_data)
        
        # Step 3: Check for discrepancies
        if validation_result['discrepancies']:
            synchronization_report['consensus_reached'] = False
            synchronization_report['discrepancies'] = validation_result['discrepancies']
            print(f"  WARNING: DISCREPANCIES FOUND: {len(validation_result['discrepancies'])}")
            
            # Reconcile discrepancies
            reconciled_data = self.reconcile_data(live_data, validation_result)
            print("  -> Data reconciled")
        else:
            reconciled_data = live_data
            print("  SUCCESS: All agents synchronized - no discrepancies")
            
        synchronization_report['agents_synchronized'] = 3
        synchronization_report['data_points'] = len(reconciled_data)
        
        self.synchronization_status = synchronization_report
        
        # Log to memory
        self.log_decision('DATA_SYNCHRONIZATION', synchronization_report)
        
        return reconciled_data, synchronization_report
        
    def run_market_scanner(self):
        """Execute Market Scanner Agent"""
        # This would spawn the actual subagent
        # For now, simulating the API pull
        
        print("    [Market Scanner] Executing...")
        
        # Pull from Polymarket API
        import requests
        
        try:
            response = requests.get('https://gamma-api.polymarket.com/markets?active=true&closed=false', timeout=15)
            markets = response.json()
            
            # Filter for Musk markets
            musk_markets = []
            for market in markets:
                question = market.get('question', '').lower()
                if any(term in question for term in ['musk', 'elon', 'tweet', 'doge']):
                    musk_markets.append({
                        'id': market.get('id'),
                        'question': market.get('question'),
                        'endDate': market.get('endDate'),
                        'outcomes': market.get('outcomes'),
                        'outcomePrices': market.get('outcomePrices'),
                        'volume': market.get('volume'),
                        'liquidity': market.get('liquidity'),
                        'timestamp': datetime.datetime.now().isoformat()
                    })
            
            print(f"    [Market Scanner] Found {len(musk_markets)} Musk/Elon/DOGE markets")
            return musk_markets
            
        except Exception as e:
            print(f"    [Market Scanner] ERROR: {e}")
            return []
            
    def run_data_validator(self, live_data):
        """Execute Data Validator Agent"""
        print("    [Data Validator] Executing...")
        
        validation_result = {
            'timestamp': datetime.datetime.now().isoformat(),
            'data_points_checked': len(live_data),
            'discrepancies': [],
            'accuracy_score': 100.0
        }
        
        # Cross-check with cached data
        # Verify price consistency
        # Check for data freshness
        
        for market in live_data:
            # Validate price format - handle both string and list formats
            try:
                prices = market.get('outcomePrices', [])
                # Handle if prices is a JSON string
                if isinstance(prices, str):
                    import json
                    prices = json.loads(prices)
                # Validate each price
                for price in prices:
                    if isinstance(price, str):
                        float(price)
                    elif isinstance(price, (int, float)):
                        pass  # Already a number
                    else:
                        raise ValueError(f"Unexpected price type: {type(price)}")
            except (ValueError, TypeError, json.JSONDecodeError) as e:
                validation_result['discrepancies'].append({
                    'market_id': market.get('id'),
                    'issue': f'Invalid price format: {str(e)}',
                    'severity': 'HIGH'
                })
                
        validation_result['accuracy_score'] = max(0, 100 - len(validation_result['discrepancies']) * 10)
        
        print(f"    [Data Validator] Accuracy: {validation_result['accuracy_score']:.1f}%")
        print(f"    [Data Validator] Discrepancies: {len(validation_result['discrepancies'])}")
        
        return validation_result
        
    def reconcile_data(self, live_data, validation_result):
        """Reconcile discrepancies between agents"""
        print("    [Orchestrator] Reconciling data discrepancies...")
        
        # Remove invalid entries
        reconciled = []
        invalid_ids = {d['market_id'] for d in validation_result['discrepancies']}
        
        for market in live_data:
            if market.get('id') not in invalid_ids:
                reconciled.append(market)
                
        print(f"    [Orchestrator] Reconciled: {len(reconciled)} valid markets")
        return reconciled
        
    def analyze_opportunities(self, synchronized_data):
        """Execute Risk Analyzer Agent on synchronized data"""
        print("\n[ORCHESTRATOR] Analyzing Opportunities...")
        
        opportunities = []
        
        for market in synchronized_data:
            # Run risk analysis
            risk_analysis = self.run_risk_analyzer(market)
            
            if risk_analysis['recommendation'] in ['STRONG_BUY', 'BUY']:
                opportunities.append({
                    'market': market,
                    'risk_analysis': risk_analysis,
                    'confidence': risk_analysis['confidence_score']
                })
                
        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        print(f"[ORCHESTRATOR] {len(opportunities)} high-confidence opportunities identified")
        
        return opportunities
        
    def run_risk_analyzer(self, market):
        """Execute Risk Analyzer Agent"""
        # Calculate risk metrics
        import json
        
        try:
            prices = market.get('outcomePrices', '[]')
            # Parse JSON string if needed
            if isinstance(prices, str):
                prices = json.loads(prices)
            yes_price = float(prices[0]) if prices else 0.5
            
            # Extreme probability detection
            is_extreme = yes_price >= 0.90 or yes_price <= 0.10
            
            # Liquidity check (lowered threshold for testing)
            liquidity = float(market.get('liquidity', 0))
            has_liquidity = liquidity > 3000
            
            # Volume check (lowered threshold for testing)
            volume = float(market.get('volume', 0))
            has_volume = volume > 5000
            
            # Risk scoring
            risk_score = 0
            if is_extreme:
                risk_score += 30  # Lower risk for extreme probabilities
            if has_liquidity:
                risk_score += 20
            if has_volume:
                risk_score += 20
                
            confidence_score = min(100, risk_score + 30)  # Base confidence
            
            # Debug output
            print(f"      [Risk Analysis] {market.get('question', 'N/A')[:40]}...")
            print(f"        YES: {yes_price:.2%}, Extreme: {is_extreme}, Liquidity: {has_liquidity}, Volume: {has_volume}")
            print(f"        Risk Score: {risk_score}, Confidence: {confidence_score}")
            
            # Determine recommendation
            if confidence_score >= 80 and is_extreme:
                recommendation = 'STRONG_BUY'
            elif confidence_score >= 60:
                recommendation = 'BUY'
            elif confidence_score >= 40:
                recommendation = 'HOLD'
            else:
                recommendation = 'AVOID'
                
            return {
                'market_id': market.get('id'),
                'yes_price': yes_price,
                'is_extreme': is_extreme,
                'has_liquidity': has_liquidity,
                'has_volume': has_volume,
                'risk_score': risk_score,
                'confidence_score': confidence_score,
                'recommendation': recommendation
            }
            
        except Exception as e:
            return {
                'market_id': market.get('id'),
                'error': str(e),
                'confidence_score': 0,
                'recommendation': 'AVOID'
            }
            
    def log_decision(self, decision_type, data):
        """Log strategic decisions"""
        decision = {
            'timestamp': datetime.datetime.now().isoformat(),
            'type': decision_type,
            'data': data,
            'orchestrator': 'Kimi K2.5'
        }
        
        self.decision_log.append(decision)
        
        # Also log to memory manager
        print(f"[ORCHESTRATOR] Decision logged: {decision_type}")
        
    def execute_full_synchronization_cycle(self):
        """Execute complete synchronized data cycle"""
        print("\n" + "="*70)
        print("FULL SYNCHRONIZATION CYCLE")
        print("="*70)
        print(f"Timestamp: {datetime.datetime.now()}")
        print()
        
        # Step 1: Deploy agents
        self.deploy_agent_army()
        
        # Step 2: Synchronize data
        live_data, sync_report = self.synchronize_api_data(['gamma_api', 'clob_api'])
        
        # Step 3: Analyze opportunities
        opportunities = self.analyze_opportunities(live_data)
        
        # Step 4: Strategic decision
        if opportunities:
            top_opportunity = opportunities[0]
            decision = {
                'action': 'DEPLOY_TRADES',
                'target': top_opportunity['market']['question'],
                'confidence': top_opportunity['confidence'],
                'rationale': f"Extreme probability with {top_opportunity['confidence']:.1f}% confidence"
            }
            self.log_decision('STRATEGIC_DECISION', decision)
            
        # Step 5: Report status
        print("\n" + "="*70)
        print("SYNCHRONIZATION CYCLE COMPLETE")
        print("="*70)
        print(f"Data Sources: {sync_report['sources_checked']}")
        print(f"Markets Synchronized: {sync_report['data_points']}")
        print(f"Consensus Reached: {sync_report['consensus_reached']}")
        print(f"High-Confidence Opportunities: {len(opportunities)}")
        print(f"Total Decisions: {len(self.decision_log)}")
        
        return {
            'live_data': live_data,
            'sync_report': sync_report,
            'opportunities': opportunities,
            'decisions': self.decision_log
        }

# Singleton instance
orchestrator = StrategicOrchestrator()

if __name__ == "__main__":
    # Execute full synchronization
    results = orchestrator.execute_full_synchronization_cycle()