"""
AUTOMATED PATTERN MINING ENGINE
Continuously scans markets for profitable patterns
Runs autonomously, logs discoveries
"""
import json
import random
from collections import Counter, defaultdict
from datetime import datetime

class PatternMiningEngine:
    """
    Automated pattern discovery system
    
    Scans for:
    - Time patterns (hour, day, week)
    - Category patterns (fade overconfident categories)
    - Sentiment patterns (question wording)
    - Price movement patterns
    """
    
    def __init__(self, data_file='historical-data-scraper/data/polymarket_complete.json'):
        self.data_file = data_file
        self.patterns_found = []
    
    def load_sample(self, sample_size=10000):
        """Load random sample of markets"""
        print(f"[LOAD] Loading sample of {sample_size} markets...")
        
        with open(self.data_file, 'r') as f:
            events = json.load(f)
        
        # Flatten to markets
        all_markets = []
        for event in events:
            if not event.get('closed'):
                continue
            
            for market in event.get('markets', []):
                outcome_prices = market.get('outcome_prices', [])
                if outcome_prices and "1" in outcome_prices:
                    all_markets.append(market)
        
        # Random sample
        if len(all_markets) > sample_size:
            sample = random.sample(all_markets, sample_size)
        else:
            sample = all_markets
        
        print(f"[OK] Loaded {len(sample)} resolved markets")
        return sample
    
    def analyze_high_confidence_fade(self, markets):
        """
        Pattern: Markets with >90% YES often fail
        Theory: Overconfidence, small events cause collapse
        """
        print("\n[PATTERN 1] High Confidence Fade (>90% YES)")
        
        high_conf_markets = []
        
        for m in markets:
            outcome_prices = m.get('outcome_prices', [])
            if not outcome_prices or len(outcome_prices) < 2:
                continue
            
            # Check if outcome resolved
            yes_won = outcome_prices[0] == "1"
            no_won = outcome_prices[1] == "1"
            
            if not (yes_won or no_won):
                continue
            
            # Get price history
            price_histories = m.get('price_histories', {})
            if not price_histories:
                continue
            
            # Get first token (YES)
            token_ids = m.get('clob_token_ids', [])
            if not token_ids:
                continue
            
            prices = price_histories.get(token_ids[0], [])
            if not prices or len(prices) < 5:
                continue
            
            # Check if ever above 90%
            price_values = [p['p'] for p in prices if 'p' in p]
            if not price_values:
                continue
            
            max_yes_price = max(price_values)
            
            if max_yes_price > 0.90:
                # This was a high-confidence market!
                high_conf_markets.append({
                    'question': m.get('question', 'Unknown'),
                    'max_yes_price': max_yes_price,
                    'yes_won': yes_won,
                    'no_won': no_won
                })
        
        # Calculate win rate if we bet NO
        total = len(high_conf_markets)
        if total == 0:
            print("  No high-confidence markets found")
            return None
        
        no_wins = sum(1 for m in high_conf_markets if m['no_won'])
        win_rate = no_wins / total * 100
        
        print(f"  Markets analyzed: {total}")
        print(f"  Bet NO, won: {no_wins}")
        print(f"  Win rate: {win_rate:.1f}%")
        print(f"  Sample questions:")
        for m in high_conf_markets[:3]:
            result = "WIN" if m['no_won'] else "LOSS"
            print(f"    [{result}] {m['question'][:60]} (max: {m['max_yes_price']*100:.0f}%)")
        
        pattern = {
            'name': 'HIGH_CONFIDENCE_FADE',
            'description': 'Bet NO on markets that reach >90% YES',
            'markets_tested': total,
            'win_rate': win_rate,
            'edge': win_rate - 50,  # vs coin flip
            'status': 'VALIDATED' if win_rate > 60 else 'FAILED'
        }
        
        self.patterns_found.append(pattern)
        return pattern
    
    def analyze_question_length(self, markets):
        """
        Pattern: Very long questions = more uncertainty
        Theory: Complex questions harder to price accurately
        """
        print("\n[PATTERN 2] Question Length Analysis")
        
        short_markets = []  # <50 chars
        long_markets = []   # >100 chars
        
        for m in markets:
            question = m.get('question', '')
            outcome_prices = m.get('outcome_prices', [])
            
            if not outcome_prices or len(outcome_prices) < 2:
                continue
            
            yes_won = outcome_prices[0] == "1"
            no_won = outcome_prices[1] == "1"
            
            if not (yes_won or no_won):
                continue
            
            q_len = len(question)
            
            if q_len < 50:
                short_markets.append({'yes_won': yes_won, 'no_won': no_won})
            elif q_len > 100:
                long_markets.append({'yes_won': yes_won, 'no_won': no_won})
        
        # Compare YES win rates
        short_yes_rate = sum(m['yes_won'] for m in short_markets) / len(short_markets) * 100 if short_markets else 0
        long_yes_rate = sum(m['yes_won'] for m in long_markets) / len(long_markets) * 100 if long_markets else 0
        
        print(f"  Short questions (<50 chars): {len(short_markets)} markets, YES wins {short_yes_rate:.1f}%")
        print(f"  Long questions (>100 chars): {len(long_markets)} markets, YES wins {long_yes_rate:.1f}%")
        print(f"  Difference: {abs(short_yes_rate - long_yes_rate):.1f}%")
        
        # If long questions have lower YES win rate, bet NO on them
        if long_yes_rate < 45:
            print(f"  PATTERN FOUND: Long questions favor NO ({100-long_yes_rate:.1f}% win rate)")
            
            pattern = {
                'name': 'LONG_QUESTION_FADE',
                'description': 'Bet NO on questions >100 characters',
                'markets_tested': len(long_markets),
                'win_rate': 100 - long_yes_rate,
                'edge': (100 - long_yes_rate) - 50,
                'status': 'VALIDATED' if (100 - long_yes_rate) > 55 else 'WEAK'
            }
            
            self.patterns_found.append(pattern)
            return pattern
        
        return None
    
    def analyze_round_numbers(self, markets):
        """
        Pattern: Markets with round number targets (e.g., $100K, 100 tweets) = anchoring bias
        Theory: Round numbers are psychological anchors, not fundamental
        """
        print("\n[PATTERN 3] Round Number Bias")
        
        import re
        
        round_number_markets = []
        
        for m in markets:
            question = m.get('question', '')
            outcome_prices = m.get('outcome_prices', [])
            
            if not outcome_prices or len(outcome_prices) < 2:
                continue
            
            yes_won = outcome_prices[0] == "1"
            no_won = outcome_prices[1] == "1"
            
            if not (yes_won or no_won):
                continue
            
            # Check for round numbers
            round_patterns = [
                r'\b100\b', r'\b1000\b', r'\b10000\b',
                r'\$100K', r'\$100,000', r'\$1M',
                r'\b50\b', r'\b200\b', r'\b500\b'
            ]
            
            has_round_number = any(re.search(pattern, question, re.I) for pattern in round_patterns)
            
            if has_round_number:
                round_number_markets.append({'yes_won': yes_won, 'no_won': no_won, 'question': question})
        
        if not round_number_markets:
            print("  No round number markets found")
            return None
        
        # Win rate if we bet NO
        no_wins = sum(m['no_won'] for m in round_number_markets)
        win_rate = no_wins / len(round_number_markets) * 100
        
        print(f"  Markets with round numbers: {len(round_number_markets)}")
        print(f"  Bet NO, win rate: {win_rate:.1f}%")
        print(f"  Sample:")
        for m in round_number_markets[:3]:
            result = "WIN" if m['no_won'] else "LOSS"
            print(f"    [{result}] {m['question'][:60]}")
        
        if win_rate > 55:
            pattern = {
                'name': 'ROUND_NUMBER_FADE',
                'description': 'Bet NO on markets with round number targets',
                'markets_tested': len(round_number_markets),
                'win_rate': win_rate,
                'edge': win_rate - 50,
                'status': 'VALIDATED' if win_rate > 60 else 'WEAK'
            }
            
            self.patterns_found.append(pattern)
            return pattern
        
        return None
    
    def run_full_scan(self, sample_size=10000):
        """Run all pattern analyses"""
        print("="*80)
        print("AUTOMATED PATTERN MINING")
        print("="*80)
        
        markets = self.load_sample(sample_size)
        
        # Run all pattern analyses
        self.analyze_high_confidence_fade(markets)
        self.analyze_question_length(markets)
        self.analyze_round_numbers(markets)
        
        # Summary
        print("\n" + "="*80)
        print("PATTERNS DISCOVERED")
        print("="*80)
        
        if not self.patterns_found:
            print("  No significant patterns found in this sample")
        else:
            for pattern in self.patterns_found:
                print(f"\n  [OK] {pattern['name']}")
                print(f"    {pattern['description']}")
                print(f"    Win rate: {pattern['win_rate']:.1f}%")
                print(f"    Edge: {pattern['edge']:.1f}%")
                print(f"    Status: {pattern['status']}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f'pattern_mining_{timestamp}.json'
        
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'sample_size': len(markets),
                'patterns_found': self.patterns_found
            }, f, indent=2)
        
        print(f"\n[SAVED] {output_file}")


if __name__ == "__main__":
    engine = PatternMiningEngine()
    engine.run_full_scan(sample_size=5000)  # Start with 5K for speed
