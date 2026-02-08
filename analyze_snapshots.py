#!/usr/bin/env python3
"""
Quick analysis script to explore Wayback Machine snapshot structure
"""

import requests
import json
from datetime import datetime
import time

def fetch_sample_snapshots():
    """Fetch a few sample snapshots to understand the data structure"""
    
    # Key dates around 2024 election
    sample_dates = [
        "20240601",  # Early 2024
        "20240901",  # Pre-election
        "20241105",  # Election day
        "20241106",  # Day after
        "20250101",  # Start of 2025
    ]
    
    results = []
    
    for date in sample_dates:
        # Try to fetch homepage snapshot
        url = f"https://web.archive.org/web/{date}120000/https://polymarket.com/"
        print(f"\nFetching snapshot from {date}...")
        
        try:
            time.sleep(2)
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                # Save a sample of the HTML
                sample_file = f"sample_{date}.html"
                with open(sample_file, 'w', encoding='utf-8') as f:
                    f.write(response.text[:50000])  # First 50KB
                
                print(f"  ✓ Saved to {sample_file}")
                
                # Look for __NEXT_DATA__
                if '__NEXT_DATA__' in response.text:
                    print("  ✓ Found __NEXT_DATA__ (Next.js app)")
                    start = response.text.find('__NEXT_DATA__')
                    end = response.text.find('</script>', start)
                    if end > start:
                        script_content = response.text[start:end]
                        json_start = script_content.find('{')
                        if json_start > 0:
                            try:
                                json_str = script_content[json_start:]
                                data = json.loads(json_str)
                                # Save the JSON structure
                                with open(f"nextdata_{date}.json", 'w') as f:
                                    json.dump(data, f, indent=2)
                                print(f"  ✓ Saved Next.js data to nextdata_{date}.json")
                            except Exception as e:
                                print(f"  ⚠ Could not parse Next.js JSON: {e}")
                
                results.append({
                    'date': date,
                    'status': 'success',
                    'size': len(response.text)
                })
            else:
                print(f"  ✗ Status {response.status_code}")
                results.append({
                    'date': date,
                    'status': f'error_{response.status_code}'
                })
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append({
                'date': date,
                'status': 'error',
                'error': str(e)
            })
    
    # Save summary
    with open('snapshot_summary.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*60)
    print("Analysis complete. Check the sample_*.html and nextdata_*.json files")
    print("to understand the page structure.")
    print("="*60)

if __name__ == "__main__":
    fetch_sample_snapshots()
