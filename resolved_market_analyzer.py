#!/usr/bin/env python3
"""
DATA GATHERER 2 - Resolved Markets Historical Pattern Analysis
Analyzes resolved prediction markets from the last 3 months
"""

import json
import csv
import requests
import time
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import statistics

# API Configuration
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# Date range: Last 3 months (Nov 2025 - Feb 2026)
END_DATE = datetime(2026, 2, 8, tzinfo=timezone.utc)
START_DATE = END_DATE - timedelta(days=90)

class ResolvedMarketAnalyzer:
    def __init__(self):
        self.markets = []
        self.analysis = {
            'total_markets': 0,
            'extreme_high_confidence': [],  # >90%
            'extreme_low_confidence': [],   # <10%
            'favorites_won': 0,
            'underdogs_won': 0,
            'fifty_fifty_markets': 0,
            'initial_vs_final': [],
            'categories': defaultdict(lambda: {'total': 0, 'favorite_wins': 0}),
            'volume_analysis': [],
            'time_to_resolution': []
        }
    
    def fetch_resolved_markets(self, limit=1000):
        """Fetch resolved markets from Gamma API"""
        print(f"Fetching resolved markets from {START_DATE.date()} to {END_DATE.date()}...")
        
        all_markets = []
        offset = 0
        batch_size = 100
        
        while True:
            try:
                url = f"{GAMMA_API}/markets"
                params = {
                    'limit': batch_size,
                    'offset': offset,
                    'closed': 'true',
                    'order': 'desc',
                    'sort': 'volume'
                }
                
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                markets = response.json()
                
                if not markets:
                    break
                
                # Filter by date range
                for market in markets:
                    end_date_str = market.get('endDate') or market.get('end_date') or market.get('endDateISO')
                    if end_date_str:
                        try:
                            # Parse various date formats
                            if 'Z' in end_date_str:
                                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            elif '+' in end_date_str:
                                end_date = datetime.fromisoformat(end_date_str)
                            else:
                                end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            
                            # Check if within last 3 months
                            if START_DATE <= end_date <= END_DATE:
                                market['parsed_end_date'] = end_date.isoformat()
                                all_markets.append(market)
                        except:
                            continue
                
                offset += batch_size
                time.sleep(0.2)  # Rate limiting
                
                if offset >= limit:
                    break
                    
            except Exception as e:
                print(f"Error fetching markets: {e}")
                break
        
        print(f"Fetched {len(all_markets)} resolved markets from last 3 months")
        return all_markets
    
    def load_existing_data(self):
        """Load existing resolved markets from local files"""
        existing = []
        
        # Try to load from JSON file
        try:
            with open('polymarket_resolved_markets.json', 'r') as f:
                data = json.load(f)
                for item in data:
                    # Check if within date range
                    end_date_str = item.get('event_end_date')
                    if end_date_str:
                        try:
                            end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                            if START_DATE <= end_date <= END_DATE:
                                existing.append({
                                    'question': item.get('question'),
                                    'endDate': end_date_str,
                                    'outcome': item.get('winner'),
                                    'finalPrices': item.get('final_prices'),
                                    'volume': float(item.get('volume_usd', 0)),
                                    'event_title': item.get('event_title'),
                                    'market_id': item.get('market_id')
                                })
                        except:
                            continue
            print(f"Loaded {len(existing)} markets from existing JSON file")
        except Exception as e:
            print(f"Could not load existing JSON: {e}")
        
        # Also try CSV
        try:
            with open('resolved_markets_enriched.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        end_date_str = row.get('event_end_date', '')
                        if end_date_str:
                            end_date = datetime.fromisoformat(end_date_str.replace('+00:00', '+00:00'))
                            if START_DATE <= end_date <= END_DATE:
                                existing.append({
                                    'question': row.get('question'),
                                    'endDate': end_date_str,
                                    'outcome': row.get('winner'),
                                    'final_yes_price': float(row.get('final_yes_price', 0)),
                                    'volume': float(row.get('volume_usd', 0)),
                                    'event_title': row.get('event_title'),
                                    'market_id': row.get('market_id')
                                })
                    except:
                        continue
            print(f"Total markets after CSV: {len(existing)}")
        except Exception as e:
            print(f"Could not load CSV: {e}")
        
        return existing
    
    def analyze_market(self, market):
        """Analyze a single market for patterns"""
        # Extract final price (YES probability)
        final_price = None
        
        if 'final_yes_price' in market:
            final_price = market['final_yes_price']
        elif 'finalPrices' in market and market['finalPrices']:
            prices = market['finalPrices'].split('|')
            if len(prices) >= 1:
                try:
                    final_price = float(prices[0])
                except:
                    pass
        elif 'outcomePrices' in market:
            prices = market.get('outcomePrices', [])
            if prices and len(prices) > 0:
                try:
                    final_price = float(prices[0])
                except:
                    pass
        
        if final_price is None:
            return None
        
        outcome = market.get('outcome', market.get('winner', ''))
        volume = market.get('volume', market.get('volume_usd', 0))
        
        # Determine if favorite won (>50% = favorite)
        is_favorite = final_price > 0.5
        favorite_won = (is_favorite and outcome == 'Yes') or (not is_favorite and outcome == 'No')
        
        # Classify market type
        if final_price >= 0.9:
            market_type = 'extreme_high'
        elif final_price <= 0.1:
            market_type = 'extreme_low'
        elif 0.4 <= final_price <= 0.6:
            market_type = 'fifty_fifty'
        else:
            market_type = 'moderate'
        
        return {
            'question': market.get('question', market.get('event_title', '')),
            'market_id': market.get('market_id', ''),
            'final_price': final_price,
            'outcome': outcome,
            'volume': float(volume) if volume else 0,
            'is_favorite': is_favorite,
            'favorite_won': favorite_won,
            'market_type': market_type,
            'end_date': market.get('endDate', market.get('event_end_date', ''))
        }
    
    def run_analysis(self):
        """Run complete analysis on resolved markets"""
        print("=" * 60)
        print("RESOLVED MARKETS HISTORICAL ANALYSIS")
        print("=" * 60)
        print(f"Date Range: {START_DATE.date()} to {END_DATE.date()}")
        print()
        
        # Load existing data
        existing_markets = self.load_existing_data()
        
        # Fetch new data from API
        api_markets = self.fetch_resolved_markets(limit=500)
        
        # Combine and deduplicate
        all_markets = {}
        for m in existing_markets + api_markets:
            mid = m.get('market_id', '') or m.get('question', '')
            if mid:
                all_markets[mid] = m
        
        print(f"\nTotal unique markets to analyze: {len(all_markets)}")
        print()
        
        # Analyze each market
        analyzed = []
        for market in all_markets.values():
            result = self.analyze_market(market)
            if result:
                analyzed.append(result)
        
        self.analysis['total_markets'] = len(analyzed)
        
        # Calculate statistics
        extreme_high_wins = 0
        extreme_high_total = 0
        extreme_low_wins = 0
        extreme_low_total = 0
        favorites_won = 0
        underdogs_won = 0
        fifty_fifty = 0
        
        prices = []
        volumes = []
        
        for m in analyzed:
            prices.append(m['final_price'])
            volumes.append(m['volume'])
            
            if m['market_type'] == 'extreme_high':
                extreme_high_total += 1
                if m['favorite_won']:
                    extreme_high_wins += 1
            elif m['market_type'] == 'extreme_low':
                extreme_low_total += 1
                if m['favorite_won']:
                    extreme_low_wins += 1
            elif m['market_type'] == 'fifty_fifty':
                fifty_fifty += 1
            
            if m['is_favorite']:
                if m['favorite_won']:
                    favorites_won += 1
            else:
                if m['favorite_won']:
                    underdogs_won += 1
        
        # Calculate summary stats
        summary = {
            'analysis_date': datetime.now().isoformat(),
            'date_range': {
                'start': START_DATE.isoformat(),
                'end': END_DATE.isoformat()
            },
            'total_markets_analyzed': len(analyzed),
            'favorite_performance': {
                'favorites_won': favorites_won,
                'underdogs_won': underdogs_won,
                'favorite_win_rate': round(favorites_won / max(1, favorites_won + underdogs_won) * 100, 2),
                'underdog_win_rate': round(underdogs_won / max(1, favorites_won + underdogs_won) * 100, 2)
            },
            'extreme_probabilities': {
                'high_confidence_total': extreme_high_total,
                'high_confidence_correct': extreme_high_wins,
                'high_confidence_accuracy': round(extreme_high_wins / max(1, extreme_high_total) * 100, 2) if extreme_high_total > 0 else 0,
                'low_confidence_total': extreme_low_total,
                'low_confidence_correct': extreme_low_wins,
                'low_confidence_accuracy': round(extreme_low_wins / max(1, extreme_low_total) * 100, 2) if extreme_low_total > 0 else 0
            },
            'market_distribution': {
                'extreme_high': extreme_high_total,
                'extreme_low': extreme_low_total,
                'fifty_fifty': fifty_fifty,
                'moderate': len(analyzed) - extreme_high_total - extreme_low_total - fifty_fifty
            },
            'price_statistics': {
                'mean_final_price': round(statistics.mean(prices), 4) if prices else 0,
                'median_final_price': round(statistics.median(prices), 4) if prices else 0,
                'price_std_dev': round(statistics.stdev(prices), 4) if len(prices) > 1 else 0,
                'min_price': round(min(prices), 4) if prices else 0,
                'max_price': round(max(prices), 4) if prices else 0
            },
            'volume_statistics': {
                'total_volume': round(sum(volumes), 2),
                'mean_volume': round(statistics.mean(volumes), 2) if volumes else 0,
                'median_volume': round(statistics.median(volumes), 2) if volumes else 0
            },
            'key_insights': []
        }
        
        # Generate insights
        insights = []
        
        if summary['favorite_performance']['favorite_win_rate'] > 60:
            insights.append(f"Favorites win {summary['favorite_performance']['favorite_win_rate']}% of the time - market shows efficiency")
        elif summary['favorite_performance']['favorite_win_rate'] < 50:
            insights.append(f"Underdogs outperform with {summary['favorite_performance']['underdog_win_rate']}% win rate - potential value opportunity")
        
        if summary['extreme_probabilities']['high_confidence_accuracy'] > 90:
            insights.append("High confidence markets (>90%) are very accurate - reliable signals")
        
        if summary['extreme_probabilities']['low_confidence_accuracy'] < 50:
            insights.append("Low confidence markets (<10%) show high upset potential")
        
        if summary['price_statistics']['mean_final_price'] > 0.55:
            insights.append("Markets tend to be biased toward YES outcomes")
        elif summary['price_statistics']['mean_final_price'] < 0.45:
            insights.append("Markets tend to be biased toward NO outcomes")
        
        summary['key_insights'] = insights
        
        # Save detailed market list
        summary['market_details'] = analyzed[:100]  # Top 100 for reference
        
        return summary
    
    def save_results(self, summary, filename='resolved_analysis.json'):
        """Save analysis results to JSON"""
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n✓ Results saved to {filename}")
        
        # Also save a human-readable summary
        txt_filename = filename.replace('.json', '.txt')
        with open(txt_filename, 'w') as f:
            f.write("=" * 70 + "\n")
            f.write("RESOLVED MARKETS HISTORICAL ANALYSIS REPORT\n")
            f.write("=" * 70 + "\n\n")
            
            f.write(f"Analysis Date: {summary['analysis_date']}\n")
            f.write(f"Period: {summary['date_range']['start'][:10]} to {summary['date_range']['end'][:10]}\n")
            f.write(f"Total Markets Analyzed: {summary['total_markets_analyzed']}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("FAVORITE VS UNDERDOG PERFORMANCE\n")
            f.write("-" * 70 + "\n")
            f.write(f"  Favorites Won:     {summary['favorite_performance']['favorites_won']} ({summary['favorite_performance']['favorite_win_rate']}%)\n")
            f.write(f"  Underdogs Won:     {summary['favorite_performance']['underdogs_won']} ({summary['favorite_performance']['underdog_win_rate']}%)\n")
            f.write(f"  Total Decided:     {summary['favorite_performance']['favorites_won'] + summary['favorite_performance']['underdogs_won']}\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("EXTREME PROBABILITY MARKETS ACCURACY\n")
            f.write("-" * 70 + "\n")
            f.write(f"  High Confidence (>90%):\n")
            f.write(f"    Total:     {summary['extreme_probabilities']['high_confidence_total']}\n")
            f.write(f"    Correct:   {summary['extreme_probabilities']['high_confidence_correct']}\n")
            f.write(f"    Accuracy:  {summary['extreme_probabilities']['high_confidence_accuracy']}%\n\n")
            
            f.write(f"  Low Confidence (<10%):\n")
            f.write(f"    Total:     {summary['extreme_probabilities']['low_confidence_total']}\n")
            f.write(f"    Correct:   {summary['extreme_probabilities']['low_confidence_correct']}\n")
            f.write(f"    Accuracy:  {summary['extreme_probabilities']['low_confidence_accuracy']}%\n\n")
            
            f.write("-" * 70 + "\n")
            f.write("MARKET DISTRIBUTION\n")
            f.write("-" * 70 + "\n")
            for key, value in summary['market_distribution'].items():
                pct = round(value / max(1, summary['total_markets_analyzed']) * 100, 1)
                f.write(f"  {key.replace('_', ' ').title()}: {value} ({pct}%)\n")
            f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("PRICE STATISTICS\n")
            f.write("-" * 70 + "\n")
            for key, value in summary['price_statistics'].items():
                f.write(f"  {key.replace('_', ' ').title()}: {value}\n")
            f.write("\n")
            
            f.write("-" * 70 + "\n")
            f.write("KEY INSIGHTS\n")
            f.write("-" * 70 + "\n")
            for i, insight in enumerate(summary['key_insights'], 1):
                f.write(f"  {i}. {insight}\n")
            
            f.write("\n" + "=" * 70 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 70 + "\n")
        
        print(f"✓ Summary saved to {txt_filename}")


def main():
    analyzer = ResolvedMarketAnalyzer()
    summary = analyzer.run_analysis()
    analyzer.save_results(summary)
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\nTotal Markets: {summary['total_markets_analyzed']}")
    print(f"Favorite Win Rate: {summary['favorite_performance']['favorite_win_rate']}%")
    print(f"Extreme High Accuracy (>90%): {summary['extreme_probabilities']['high_confidence_accuracy']}%")
    print(f"Extreme Low Accuracy (<10%): {summary['extreme_probabilities']['low_confidence_accuracy']}%")
    print("\nKey Insights:")
    for insight in summary['key_insights']:
        print(f"  • {insight}")


if __name__ == "__main__":
    main()
