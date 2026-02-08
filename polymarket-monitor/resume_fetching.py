#!/usr/bin/env python3
"""
Resume price fetching from checkpoint 40K
Windows-safe (no Unicode emojis)
"""
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
import time
import sys

# ============================================================
# CONFIGURATION
# ============================================================
MIN_VOLUME = 100000  # $100K+ minimum
MAX_CONCURRENT = 25  # Slower to avoid rate limits
DATA_DIR = Path("historical-data-scraper/data")
OUTPUT_DIR = Path("backtest-results")
OUTPUT_DIR.mkdir(exist_ok=True)

CHECKPOINT_FILE = DATA_DIR / "prices_checkpoint_40000.json"
RESUME_OUTPUT = DATA_DIR / "prices_complete.json"

# ============================================================
# FETCH PRICES
# ============================================================
async def fetch_price(session, token_id, semaphore):
    """Fetch single token price history with rate limiting"""
    async with semaphore:
        url = f"https://clob.polymarket.com/prices-history?market={token_id}&interval=max&fidelity=1"
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {'token_id': token_id, 'prices': data.get('history', []), 'success': True}
                elif resp.status == 429:
                    return {'token_id': token_id, 'success': False, 'error': 'RATE_LIMITED'}
                else:
                    return {'token_id': token_id, 'success': False, 'error': f'HTTP {resp.status}'}
        except asyncio.TimeoutError:
            return {'token_id': token_id, 'success': False, 'error': 'TIMEOUT'}
        except Exception as e:
            return {'token_id': token_id, 'success': False, 'error': str(e)[:100]}

async def fetch_remaining(tokens_to_fetch, existing_results):
    """Fetch remaining prices with progress tracking"""
    print(f"\n{'='*70}")
    print(f"RESUMING PRICE FETCH FROM CHECKPOINT 40K")
    print(f"{'='*70}")
    print(f"Already fetched: {len(existing_results):,}")
    print(f"Remaining tokens: {len(tokens_to_fetch):,}")
    print(f"Concurrent requests: {MAX_CONCURRENT} (rate-limit safe)")
    print(f"Estimated time: {len(tokens_to_fetch) / (MAX_CONCURRENT * 1.5) / 60:.1f} minutes\n")
    
    results = list(existing_results)  # Start with what we have
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_price(session, token_id, semaphore) for token_id in tokens_to_fetch]
        
        # Process in smaller batches to save more frequently
        batch_size = 500
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i+batch_size]
            batch_results = await asyncio.gather(*batch, return_exceptions=True)
            
            # Filter out exceptions
            valid_results = [r for r in batch_results if isinstance(r, dict)]
            results.extend(valid_results)
            
            # Progress
            elapsed = time.time() - start_time
            new_fetched = len(results) - len(existing_results)
            rate = new_fetched / elapsed if elapsed > 0 else 0
            remaining = len(tokens_to_fetch) - new_fetched
            eta_min = (remaining / rate / 60) if rate > 0 else 0
            success_count = len([r for r in valid_results if r.get('success')])
            rate_limited = len([r for r in valid_results if r.get('error') == 'RATE_LIMITED'])
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"{len(results):,} total | "
                  f"+{new_fetched} new | "
                  f"{success_count}/{len(valid_results)} OK | "
                  f"{rate_limited} rate-limited | "
                  f"{rate:.1f}/sec | "
                  f"ETA {eta_min:.1f}min")
            
            # Save checkpoint every 1000 tokens
            if new_fetched > 0 and new_fetched % 1000 == 0:
                checkpoint_file = DATA_DIR / f"prices_checkpoint_{len(results)}.json"
                with open(checkpoint_file, 'w') as f:
                    json.dump(results, f)
                print(f"    [SAVED] Checkpoint at {len(results):,} tokens")
            
            # Slow down if we're getting rate limited
            if rate_limited > 10:
                print(f"    [THROTTLE] Rate limiting detected, pausing 30s...")
                await asyncio.sleep(30)
    
    # Final save
    with open(RESUME_OUTPUT, 'w') as f:
        json.dump(results, f)
    
    new_fetched = len(results) - len(existing_results)
    success_count = len([r for r in results if r.get('success')])
    print(f"\n[COMPLETE] Price fetch finished!")
    print(f"  Total tokens: {len(results):,}")
    print(f"  Newly fetched: {new_fetched:,}")
    print(f"  Total success: {success_count:,} ({success_count/len(results)*100:.1f}%)")
    print(f"  Time: {(time.time()-start_time)/60:.1f} min")
    print(f"  Output: {RESUME_OUTPUT}\n")
    
    return results

# ============================================================
# MAIN
# ============================================================
def main():
    print(f"\n{'='*70}")
    print(f"POLYMARKET PRICE FETCHER - RESUME MODE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}\n")
    
    # Load checkpoint
    print(f"Loading checkpoint: {CHECKPOINT_FILE}")
    with open(CHECKPOINT_FILE) as f:
        existing_results = json.load(f)
    print(f"[OK] Loaded {len(existing_results):,} existing results")
    
    # Load event data to get all tokens
    print(f"Loading event data...")
    with open(DATA_DIR / 'polymarket_complete.json') as f:
        events_data = json.load(f)
    print(f"[OK] Loaded {len(events_data):,} events")
    
    # Extract all tokens that need fetching
    print(f"\nExtracting tokens with volume >= ${MIN_VOLUME:,}...")
    all_tokens = set()
    for event in events_data:
        volume = event.get('volume')
        if volume and volume >= MIN_VOLUME:
            for market in event.get('markets', []):
                token_ids = market.get('clob_token_ids', '[]')
                if isinstance(token_ids, str):
                    try:
                        token_ids = json.loads(token_ids)
                        for tid in token_ids:
                            all_tokens.add(tid)
                    except:
                        pass
    
    print(f"[OK] Found {len(all_tokens):,} total tokens")
    
    # Find which tokens we already have
    existing_token_ids = {r['token_id'] for r in existing_results}
    tokens_to_fetch = list(all_tokens - existing_token_ids)
    
    print(f"\nAlready have: {len(existing_token_ids):,}")
    print(f"Need to fetch: {len(tokens_to_fetch):,}")
    
    if not tokens_to_fetch:
        print("\n[COMPLETE] All tokens already fetched!")
        return
    
    # Fetch remaining
    final_results = asyncio.run(fetch_remaining(tokens_to_fetch, existing_results))
    
    print(f"\n{'='*70}")
    print(f"FETCH COMPLETE!")
    print(f"{'='*70}")
    print(f"Total tokens: {len(final_results):,}")
    print(f"Output: {RESUME_OUTPUT}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
