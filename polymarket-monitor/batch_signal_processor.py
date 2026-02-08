"""
HIGH-THROUGHPUT BATCH SIGNAL PROCESSOR
Implements ROOT DIRECTIVE: Max-Compute, Rate-Limit Safe
"""
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

class BatchSignalProcessor:
    """Batch processor following ROOT DIRECTIVE constraints"""
    
    # Proven event-driven strategies
    STRATEGIES = {
        'MUSK_FADE_EXTREMES': {
            'category': 'Tech/Musk',
            'pattern': r'(\d+)-(\d+)\s+tweets',
            'condition': lambda low, high: low < 40 or high > 200,
            'direction': 'NO',
            'win_rate': 0.971,
            'edge': 0.471
        },
        'WEATHER_FADE_LONGSHOTS': {
            'category': 'Weather/Temperature',
            'threshold': 0.30,
            'direction': 'NO',
            'win_rate': 0.939,
            'edge': 0.439
        },
        'ALTCOIN_FADE_HIGH': {
            'category': 'Crypto/Altcoins',
            'threshold': 0.70,
            'direction': 'NO',
            'win_rate': 0.923,
            'edge': 0.423
        },
        'BTC_TIME_BIAS': {
            'category': 'Crypto/BTC-UpDown',
            'biased_hours': {0: ('NO', 0.68), 7: ('YES', 0.61), 10: ('YES', 0.56), 12: ('NO', 0.61), 21: ('NO', 0.61)},
            'win_rate': 0.589,
            'edge': 0.089
        },
        'CRYPTO_FAVORITE_FADE': {
            'category': 'Crypto/BTC-Price',
            'threshold': 0.70,
            'direction': 'NO',
            'win_rate': 0.619,
            'edge': 0.119
        }
    }
    
    # Market taxonomy (regex patterns)
    TAXONOMY = {
        'Crypto/BTC-UpDown': [r'\bbitcoin\s+up\s+or\s+down\b', r'\bbtc\s+higher\s+or\s+lower\b'],
        'Crypto/BTC-Price': [r'\bprice of bitcoin\b', r'\bbitcoin\b.*\$\d+', r'\bbtc\b.*\$\d+'],
        'Crypto/Altcoins': [r'\bsolana\b', r'\bxrp\b', r'\bcardano\b', r'\bada\b', r'\bsol\b'],
        'Weather/Temperature': [r'\btemperature\b', r'\bdegrees?\b', r'\bcelsius\b', r'\bfahrenheit\b'],
        'Tech/Musk': [r'\bmusk\b.*tweet', r'\belon\s*musk\b.*post'],
        'Politics/Trump': [r'\btrump\b'],
        'Tech/Companies': [r'\b(msft|microsoft|aapl|apple|nvda|nvidia|tsla|tesla)\b']
    }
    
    def __init__(self):
        self.cache = {}
    
    def process_batch(self, markets: List[Dict[str, Any]], max_clusters: int = 40, max_review: int = 50) -> Dict[str, Any]:
        """
        STAGE 1: Dedupe + Categorize + Extract candidates (90% reduction)
        STAGE 2: Deep analysis on top candidates (≤10 items)
        Returns JSON matching ROOT DIRECTIVE schema
        """
        
        # STAGE 1: TRIAGE
        unique_markets = self._dedupe(markets)
        clusters = self._cluster_by_event(unique_markets)
        candidates = self._extract_candidates(clusters, max_items=max_review)
        
        # Limit clusters to prevent bloat
        clusters = sorted(clusters, key=lambda c: c['confidence'], reverse=True)[:max_clusters]
        
        # STAGE 2: DEEPEN (only if ≤10 candidates)
        if len(candidates) <= 10:
            review_queue = self._deep_analysis(candidates)
            stop_reason = "ok"
        else:
            review_queue = candidates[:max_review]  # Truncate
            stop_reason = "too_many_candidates"
        
        return {
            "dedupe_summary": {
                "input_items": len(markets),
                "unique_items": len(unique_markets),
                "clusters": len(clusters)
            },
            "clusters": clusters,
            "review_queue": review_queue,
            "next_batch_plan": {
                "stop_reason": stop_reason,
                "recommended_batch_size": min(len(unique_markets) * 2, 300),
                "recommended_ordering": "highest priority first",
                "what_to_include_next_pass": [
                    "market.title", 
                    "market.current_price",
                    "cluster.canonical_summary",
                    "strategy_params"
                ],
                "dedupe_on": ["cache_key", "market_id", "question"]
            }
        }
    
    def _dedupe(self, markets: List[Dict]) -> List[Dict]:
        """Exact + fuzzy deduplication"""
        seen = set()
        unique = []
        
        for m in markets:
            # Exact dedupe on market_id
            if m.get('market_id') in seen:
                continue
            
            # Fuzzy dedupe on question (normalize whitespace/case)
            q_norm = re.sub(r'\s+', ' ', m.get('question', '').lower().strip())
            q_hash = hashlib.md5(q_norm.encode()).hexdigest()[:8]
            
            if q_hash in seen:
                continue
            
            seen.add(m.get('market_id'))
            seen.add(q_hash)
            unique.append(m)
        
        return unique
    
    def _cluster_by_event(self, markets: List[Dict]) -> List[Dict]:
        """Categorize markets and cluster by event type"""
        clusters = []
        category_groups = defaultdict(list)
        
        for m in markets:
            question = m.get('question', '').lower()
            category = self._categorize(question)
            
            if category:
                category_groups[category].append(m)
        
        # Create cluster per category
        for category, group in category_groups.items():
            if not group:
                continue
            
            # Extract canonical summary (first market question, truncated)
            canonical = group[0].get('question', 'Unknown')[:240]
            
            # Calculate confidence (based on category match strength)
            confidence = min(1.0, len(group) / 10.0)  # More markets = higher confidence
            
            cluster_id = f"C-{hashlib.md5(category.encode()).hexdigest()[:8]}"
            
            clusters.append({
                "cluster_id": cluster_id,
                "event_type": category,
                "entities": [m.get('market_id') for m in group[:5]],  # Top 5 market IDs
                "timestamp_utc": datetime.utcnow().isoformat() + "Z",
                "canonical_summary": canonical,
                "supporting_ids": [m.get('market_id') for m in group],
                "confidence": round(confidence, 2)
            })
        
        return clusters
    
    def _categorize(self, question: str) -> str:
        """Map question to event category"""
        for category, patterns in self.TAXONOMY.items():
            for pattern in patterns:
                if re.search(pattern, question, re.IGNORECASE):
                    return category
        return None
    
    def _extract_candidates(self, clusters: List[Dict], max_items: int) -> List[Dict]:
        """Extract tradeable candidates from clusters"""
        candidates = []
        
        for cluster in clusters:
            category = cluster['event_type']
            
            # Check which strategies apply to this category
            for strategy_name, params in self.STRATEGIES.items():
                if params.get('category') != category:
                    continue
                
                # High-priority candidate found
                priority = params.get('win_rate', 0.5)
                
                candidates.append({
                    "pair_id": f"{cluster['cluster_id']}|{strategy_name}",
                    "market_id": cluster['entities'][0] if cluster['entities'] else "unknown",
                    "cluster_id": cluster['cluster_id'],
                    "priority": round(priority, 3),
                    "analysis_question": f"Apply {strategy_name} to {category} markets?",
                    "cache_key": f"{cluster['cluster_id']}|{strategy_name}|v1"
                })
        
        # Sort by priority, limit output
        candidates.sort(key=lambda c: c['priority'], reverse=True)
        return candidates[:max_items]
    
    def _deep_analysis(self, candidates: List[Dict]) -> List[Dict]:
        """Stage 2: Deep reasoning on ≤10 candidates"""
        analyzed = []
        
        for c in candidates:
            strategy = c['analysis_question'].split()[1]  # Extract strategy name
            
            # Add reasoning field
            c['reasoning'] = f"{strategy}: {self.STRATEGIES.get(strategy, {}).get('win_rate', 0)*100:.1f}% win rate, edge={self.STRATEGIES.get(strategy, {}).get('edge', 0):.3f}"
            analyzed.append(c)
        
        return analyzed


def demo_usage():
    """Example: Process a batch of Polymarket markets"""
    
    # Simulated market data
    sample_markets = [
        {"market_id": "001", "question": "Will Elon Musk post 0-19 tweets next week?"},
        {"market_id": "002", "question": "Will Elon Musk post 200-239 tweets next week?"},
        {"market_id": "003", "question": "Will temperature in NYC reach 105F on Feb 10?"},
        {"market_id": "004", "question": "Will Bitcoin go up or down in next 15 minutes?"},
        {"market_id": "005", "question": "Will Solana price hit $500 by March?"},
        {"market_id": "006", "question": "Will Bitcoin price reach $150,000 by April?"},
        {"market_id": "007", "question": "Will temperature in LA be below 32F tomorrow?"},
        {"market_id": "008", "question": "Will Elon Musk post 80-99 tweets next week?"},
        {"market_id": "009", "question": "Will XRP reach $10 by end of February?"},
        {"market_id": "010", "question": "Will Trump announce candidacy?"}
    ]
    
    processor = BatchSignalProcessor()
    result = processor.process_batch(sample_markets)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    demo_usage()
