import asyncio
import aiohttp
import json

async def check_api():
    async with aiohttp.ClientSession() as session:
        # Check CLOB API
        async with session.get('https://clob.polymarket.com/markets?active=true&limit=5') as resp:
            print(f"Status: {resp.status}")
            if resp.status == 200:
                data = await resp.json()
                print(f"Data type: {type(data)}")
                print(f"Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                print(f"Count: {data.get('count')}")
                print(f"Limit: {data.get('limit')}")
                
                # Get markets list
                markets = data.get('data', [])
                print(f"Markets count: {len(markets)}")
                
                if markets:
                    first = markets[0]
                    print(f"\nFirst market type: {type(first)}")
                    if isinstance(first, dict):
                        print(f"Keys: {list(first.keys())}")
                        print(f"\nSample market:")
                        print(json.dumps(first, indent=2)[:800])

asyncio.run(check_api())