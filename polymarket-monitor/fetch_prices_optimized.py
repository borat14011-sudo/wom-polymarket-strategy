#!/usr/bin/env python3
"""
OPTIMIZED PRICE FETCHER
- Parallel downloads (100 concurrent)
- Smart sampling (high volume markets only)
- Progress tracking with ETA
- Resume capability
"""
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
import time

# Config
MAX_CONCURRENT = 50  # Conservative start
MIN_VOLUME = 1000    # Only fetch markets with >$1K volume
OUTPUT_FILE = Path("historical-data-scraper/data/prices_optimized.json")
PROGRESS_FILE = Path("historical-data-scraper/data/fetch_progress.json")

async def fetch_price_history(session, token_id, market_question):
    """Fetch price history for one token"""
    url = f"https://clob.polymarket.com/prices-history?market={token_id}&interval=max&fidelity=1"
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                return {
                    'token_id': token_id,
                    'question': market_question,
                    'prices': data.get('history', []),
                    'success': True
                }
            else:
                return {'token_id': token_id, 'success': False, 'error': f'HTTP {resp.status}'}
    except Exception as e:
        return {'token_id': token_id, 'success': False, 'error': str(e)}

async def fetch_batch(tokens_batch):
    """Fetch a batch of price histories concurrently"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price_history(session, t['id'], t['question']) for t in tokens_batch]
        return await asyncio.gather(*tasks, return_exceptions=True)

def load_progress():
    """Load progress from previous run"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'completed_tokens': [], 'failed_tokens': [], 'last_index': 0}

def save_progress(progress):
    """Save progress for resume capability"""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f)

def main():
    print("Loading market data...")
    with open('historical-data-scraper/data/polymarket_complete.json') as f:
        data = json.load(f)
    
    print(f"Total events: {len(data):,}")
    
    # Extract all tokens with volume filter
    print(f"\nFiltering markets with volume > ${MIN_VOLUME:,}...")
    tokens = []
    
    for event in data:
        volume = float(event.get('volume', 0))
        if volume > MIN_VOLUME:
            for market in event.get('markets', []):
                token_ids = market.get('clob_token_ids', '[]')
                # Parse token IDs from string
                if isinstance(token_ids, str):
                    try:
                        token_ids = json.loads(token_ids)
                    except:
                        continue
                
                for token_id in token_ids:
                    tokens.append({
                        'id': token_id,
                        'question': market.get('question', 'Unknown'),
                        'volume': volume,
                        'event_id': event.get('event_id')
                    })
    
    print(f"Filtered to {len(tokens):,} high-volume tokens")
    
    # Load progress
    progress = load_progress()
    start_index = progress['last_index']
    
    if start_index > 0:
        print(f"Resuming from token {start_index:,}")
    
    # Process in batches
    batch_size = MAX_CONCURRENT
    total_batches = (len(tokens) - start_index) // batch_size + 1
    
    results = []
    start_time = time.time()
    
    print(f"\nStarting parallel fetch ({MAX_CONCURRENT} concurrent)...")
    print(f"Total batches: {total_batches:,}\n")
    
    for i in range(start_index, len(tokens), batch_size):
        batch_num = (i - start_index) // batch_size + 1
        batch = tokens[i:i+batch_size]
        
        # Fetch batch
        batch_results = asyncio.run(fetch_batch(batch))
        results.extend(batch_results)
        
        # Update progress
        progress['last_index'] = i + batch_size
        progress['completed_tokens'].extend([r['token_id'] for r in batch_results if r.get('success')])
        progress['failed_tokens'].extend([r['token_id'] for r in batch_results if not r.get('success')])
        save_progress(progress)
        
        # Calculate stats
        elapsed = time.time() - start_time
        rate = (i - start_index + len(batch)) / elapsed
        remaining = len(tokens) - (i + len(batch))
        eta_sec = remaining / rate if rate > 0 else 0
        
        success_count = len([r for r in batch_results if r.get('success')])
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Batch {batch_num}/{total_batches} | "
              f"{i+len(batch):,}/{len(tokens):,} tokens | "
              f"{success_count}/{len(batch)} success | "
              f"Rate: {rate:.1f}/sec | "
              f"ETA: {eta_sec/60:.1f} min")
        
        # Save incremental results every 10 batches
        if batch_num % 10 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(results, f)
            print(f"  → Saved {len(results):,} results to {OUTPUT_FILE}")
    
    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f)
    
    # Summary
    total_time = time.time() - start_time
    success_count = len([r for r in results if r.get('success')])
    
    print(f"\n{'='*60}")
    print(f"COMPLETE!")
    print(f"Total tokens processed: {len(results):,}")
    print(f"Successful fetches: {success_count:,} ({success_count/len(results)*100:.1f}%)")
    print(f"Failed: {len(results)-success_count:,}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average rate: {len(results)/total_time:.1f} tokens/sec")
    print(f"Output: {OUTPUT_FILE}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
