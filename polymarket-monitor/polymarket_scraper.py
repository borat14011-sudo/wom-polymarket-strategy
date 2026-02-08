"""
Polymarket scraper - fetches market data from Polymarket's public API
"""
import requests
import logging
import time
from datetime import datetime
from database import insert_market_snapshot, init_database

logger = logging.getLogger(__name__)

# Import API settings from config
try:
    from config import GAMMA_API, CLOB_API, API_TIMEOUT, USER_AGENT, MARKETS_LIMIT
except ImportError:
    # Fallback defaults
    GAMMA_API = "https://gamma-api.polymarket.com"
    CLOB_API = "https://clob.polymarket.com"
    API_TIMEOUT = 30
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    MARKETS_LIMIT = 50

def fetch_trending_markets(limit=None):
    """
    Fetch trending markets from Polymarket
    Returns list of market data dictionaries
    """
    try:
        # Get markets sorted by volume
        if limit is None:
            limit = MARKETS_LIMIT
        url = f"{GAMMA_API}/markets"
        params = {
            "limit": limit,
            "closed": "false",  # Only active markets
            "order": "volume24hr",  # Sort by 24h volume
            "ascending": "false"
        }
        
        headers = {
            "User-Agent": USER_AGENT
        }
        
        logger.info(f"Fetching markets from {url}")
        response = requests.get(url, params=params, headers=headers, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        markets = response.json()
        logger.info(f"Successfully fetched {len(markets)} markets")
        
        return markets
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching markets: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return []


def parse_market_data(market):
    """
    Parse raw market data into our format
    """
    try:
        market_id = market.get("conditionId", market.get("id", "unknown"))
        name = market.get("question", "Unknown Market")
        
        # Get the outcome tokens (usually Yes/No for binary markets)
        tokens = market.get("tokens", [])
        
        # For binary markets, we typically track the "Yes" token price
        if tokens and len(tokens) > 0:
            # Usually the first token is "Yes"
            outcome_prices = market.get("outcomePrices", ["0.5", "0.5"])
            price = float(outcome_prices[0]) if outcome_prices else 0.5
        else:
            price = 0.5
        
        # Volume in USD
        volume = float(market.get("volume24hr", 0))
        
        # Liquidity
        liquidity = float(market.get("liquidity", 0))
        
        return {
            "market_id": market_id,
            "name": name,
            "price": price,
            "volume": volume,
            "liquidity": liquidity
        }
        
    except Exception as e:
        logger.error(f"Error parsing market data: {e}")
        return None


def scrape_and_store():
    """
    Main scraping function - fetch markets and store in database
    """
    logger.info("=" * 60)
    logger.info(f"Starting scrape at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    markets = fetch_trending_markets()  # Uses MARKETS_LIMIT from config
    
    if not markets:
        logger.warning("No markets fetched")
        return 0
    
    stored_count = 0
    
    for market_raw in markets:
        market = parse_market_data(market_raw)
        
        if market:
            try:
                insert_market_snapshot(
                    market["market_id"],
                    market["name"],
                    market["price"],
                    market["volume"],
                    market["liquidity"]
                )
                stored_count += 1
                logger.debug(f"Stored: {market['name'][:50]}... (${market['volume']:,.0f})")
            except Exception as e:
                logger.error(f"Error storing market: {e}")
    
    logger.info(f"Scrape complete: stored {stored_count} markets")
    logger.info("=" * 60)
    
    return stored_count


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    init_database()
    
    # Run scraper
    scrape_and_store()
