"""
RVR Calculator - Calculates Risk-Volume-ROI signals
"""
import logging
from datetime import datetime
from database import get_market_history, insert_signal, check_recent_signal
import sqlite3

logger = logging.getLogger(__name__)

# Import thresholds from config
try:
    from config import RVR_THRESHOLD, ROC_THRESHOLD
except ImportError:
    # Fallback defaults if config not found
    RVR_THRESHOLD = 2.5
    ROC_THRESHOLD = 8.0

DB_PATH = "polymarket_data.db"


def calculate_rvr(current_volume, historical_volumes):
    """
    Calculate RVR: current_volume / avg_24h_volume
    """
    if not historical_volumes:
        return 0.0
    
    avg_volume = sum(historical_volumes) / len(historical_volumes)
    
    if avg_volume == 0:
        return 0.0
    
    rvr = current_volume / avg_volume
    return rvr


def calculate_roc(current_price, price_12h_ago):
    """
    Calculate ROC (Rate of Change): (current - old) / old * 100
    """
    if price_12h_ago == 0:
        return 0.0
    
    roc = ((current_price - price_12h_ago) / price_12h_ago) * 100
    return roc


def get_all_active_markets():
    """
    Get all markets that have recent data
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get markets with data in the last 2 hours
    cursor.execute("""
        SELECT DISTINCT market_id, name
        FROM market_snapshots
        WHERE timestamp >= strftime('%s', 'now', '-2 hours')
        ORDER BY timestamp DESC
    """)
    
    markets = cursor.fetchall()
    conn.close()
    
    return markets


def analyze_market(market_id, market_name):
    """
    Analyze a single market for signals
    Returns signal dict if found, None otherwise
    """
    # Get 24h history
    history = get_market_history(market_id, hours=24)
    
    if len(history) < 2:
        logger.debug(f"Not enough history for {market_name[:30]}...")
        return None
    
    # Current values (most recent snapshot)
    current_price = history[-1][0]
    current_volume = history[-1][1]
    current_time = history[-1][2]
    
    # Calculate RVR
    historical_volumes = [row[1] for row in history[:-1]]  # Exclude current
    rvr = calculate_rvr(current_volume, historical_volumes)
    
    # Calculate ROC (12 hours ago)
    # Find snapshot closest to 12 hours ago
    target_time = current_time - (12 * 3600)
    
    # Find closest historical point to 12h ago
    price_12h_ago = None
    min_diff = float('inf')
    
    for price, volume, timestamp in history[:-1]:
        diff = abs(timestamp - target_time)
        if diff < min_diff:
            min_diff = diff
            price_12h_ago = price
    
    if price_12h_ago is None:
        price_12h_ago = history[0][0]  # Use oldest if we can't find 12h ago
    
    roc = calculate_roc(current_price, price_12h_ago)
    
    # Check if signal criteria met
    if rvr >= RVR_THRESHOLD and abs(roc) >= ROC_THRESHOLD:
        logger.info(f"🚨 SIGNAL FOUND: {market_name[:40]}... | RVR: {rvr:.2f} | ROC: {roc:+.1f}%")
        
        return {
            "market_id": market_id,
            "market_name": market_name,
            "rvr": rvr,
            "roc": roc,
            "price": current_price,
            "volume": current_volume
        }
    
    return None


def calculate_signals():
    """
    Main function to calculate signals for all markets
    Returns list of new signals
    """
    logger.info("=" * 60)
    logger.info(f"Starting signal calculation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    markets = get_all_active_markets()
    logger.info(f"Analyzing {len(markets)} markets")
    
    new_signals = []
    
    for market_id, market_name in markets:
        # Check if we recently alerted for this market (avoid spam)
        if check_recent_signal(market_id, hours=6):
            logger.debug(f"Skipping {market_name[:30]}... (recently alerted)")
            continue
        
        signal = analyze_market(market_id, market_name)
        
        if signal:
            # Store signal in database
            try:
                signal_id = insert_signal(
                    signal["market_id"],
                    signal["market_name"],
                    signal["rvr"],
                    signal["roc"],
                    signal["price"],
                    signal["volume"]
                )
                signal["id"] = signal_id
                new_signals.append(signal)
            except Exception as e:
                logger.error(f"Error storing signal: {e}")
    
    logger.info(f"Found {len(new_signals)} new signals")
    logger.info("=" * 60)
    
    return new_signals


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run calculator
    signals = calculate_signals()
    
    if signals:
        print("\nSignals found:")
        for sig in signals:
            print(f"  - {sig['market_name'][:50]}")
            print(f"    RVR: {sig['rvr']:.2f} | ROC: {sig['roc']:+.1f}% | Price: {sig['price']:.2f}")
    else:
        print("\nNo signals found")
