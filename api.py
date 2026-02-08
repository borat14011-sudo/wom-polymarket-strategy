#!/usr/bin/env python3
"""
Dashboard API - Flask backend for trading system dashboard
Serves data from SQLite database to web frontend
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
from datetime import datetime, timedelta
from functools import wraps
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Configuration
DB_PATH = "polymarket_data.db"
API_VERSION = "1.0.0"

# Rate limiting decorator (simple in-memory)
request_timestamps = {}

def rate_limit(requests_per_minute=60):
    """Simple rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            now = time.time()
            client_ip = request.remote_addr
            
            if client_ip not in request_timestamps:
                request_timestamps[client_ip] = []
            
            # Remove timestamps older than 1 minute
            request_timestamps[client_ip] = [
                ts for ts in request_timestamps[client_ip] 
                if now - ts < 60
            ]
            
            # Check rate limit
            if len(request_timestamps[client_ip]) >= requests_per_minute:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'limit': requests_per_minute,
                    'retry_after': 60
                }), 429
            
            request_timestamps[client_ip].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

def get_db():
    """Get database connection"""
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def dict_from_row(row):
    """Convert sqlite3.Row to dict"""
    return dict(zip(row.keys(), row))

# ============================================================================
# SYSTEM STATUS ENDPOINTS
# ============================================================================

@app.route('/api/status')
@rate_limit(60)
def get_status():
    """Get system status overview"""
    conn = get_db()
    if not conn:
        return jsonify({
            'status': 'error',
            'message': 'Database not found. Run data collectors first.'
        }), 404
    
    cursor = conn.cursor()
    
    # Get database stats
    cursor.execute('SELECT COUNT(*) as count FROM markets')
    market_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM snapshots')
    snapshot_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM tweets')
    tweet_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) as count FROM hype_signals')
    signal_count = cursor.fetchone()[0]
    
    # Get last collection time
    cursor.execute('SELECT MAX(timestamp) as last_time FROM snapshots')
    last_snapshot = cursor.fetchone()[0]
    
    cursor.execute('SELECT MAX(timestamp) as last_time FROM tweets')
    last_tweet = cursor.fetchone()[0]
    
    # Get database size
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    
    conn.close()
    
    return jsonify({
        'status': 'ok',
        'version': API_VERSION,
        'timestamp': datetime.utcnow().isoformat(),
        'database': {
            'path': DB_PATH,
            'size_mb': round(db_size / (1024 * 1024), 2),
            'markets': market_count,
            'snapshots': snapshot_count,
            'tweets': tweet_count,
            'signals': signal_count
        },
        'last_collection': {
            'market_data': last_snapshot,
            'twitter_data': last_tweet
        }
    })

# ============================================================================
# MARKET ENDPOINTS
# ============================================================================

@app.route('/api/markets')
@rate_limit(60)
def get_markets():
    """Get list of tracked markets with current stats"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database not found'}), 404
    
    cursor = conn.cursor()
    
    # Get markets with latest snapshot data
    query = '''
        SELECT 
            m.market_id,
            m.slug,
            m.question,
            m.category,
            m.resolved,
            m.resolution_outcome,
            s.price_yes as current_price,
            s.volume_24h,
            s.timestamp as last_update,
            h.hype_score,
            h.tweet_count
        FROM markets m
        LEFT JOIN (
            SELECT market_id, price_yes, volume_24h, timestamp
            FROM snapshots s1
            WHERE timestamp = (
                SELECT MAX(timestamp) FROM snapshots s2 
                WHERE s2.market_id = s1.market_id
            )
        ) s ON m.market_id = s.market_id
        LEFT JOIN (
            SELECT market_id, hype_score, tweet_count
            FROM hype_signals h1
            WHERE timestamp = (
                SELECT MAX(timestamp) FROM hype_signals h2
                WHERE h2.market_id = h1.market_id
            )
        ) h ON m.market_id = h.market_id
        ORDER BY s.volume_24h DESC NULLS LAST
    '''
    
    cursor.execute(query)
    markets = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Calculate 24h price change for each market
    for market in markets:
        market_id = market['market_id']
        
        # Get price from 24h ago
        cursor.execute('''
            SELECT price_yes FROM snapshots
            WHERE market_id = ?
              AND timestamp <= datetime('now', '-1 day')
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        old_price_row = cursor.fetchone()
        if old_price_row and market['current_price']:
            old_price = old_price_row[0]
            market['price_change_24h'] = market['current_price'] - old_price
            market['price_change_pct'] = (market['price_change_24h'] / old_price * 100) if old_price > 0 else 0
        else:
            market['price_change_24h'] = None
            market['price_change_pct'] = None
    
    conn.close()
    
    return jsonify({
        'markets': markets,
        'count': len(markets),
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/markets/<market_id>')
@rate_limit(60)
def get_market_detail(market_id):
    """Get detailed data for a specific market"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database not found'}), 404
    
    cursor = conn.cursor()
    
    # Get market info
    cursor.execute('SELECT * FROM markets WHERE market_id = ?', (market_id,))
    market_row = cursor.fetchone()
    
    if not market_row:
        conn.close()
        return jsonify({'error': 'Market not found'}), 404
    
    market = dict_from_row(market_row)
    
    # Get recent price history (last 7 days, hourly)
    cursor.execute('''
        SELECT timestamp, price_yes, volume_24h, spread
        FROM snapshots
        WHERE market_id = ?
          AND timestamp > datetime('now', '-7 days')
        ORDER BY timestamp ASC
    ''', (market_id,))
    
    price_history = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Get recent tweets (top 20 by engagement)
    cursor.execute('''
        SELECT tweet_id, timestamp, text, author_username,
               likes, retweets, replies, engagement_score
        FROM tweets
        WHERE market_id = ?
        ORDER BY engagement_score DESC
        LIMIT 20
    ''', (market_id,))
    
    top_tweets = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Get hype signals history
    cursor.execute('''
        SELECT timestamp, hype_score, tweet_count, velocity, avg_sentiment
        FROM hype_signals
        WHERE market_id = ?
          AND timestamp > datetime('now', '-7 days')
        ORDER BY timestamp ASC
    ''', (market_id,))
    
    hype_history = [dict_from_row(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'market': market,
        'price_history': price_history,
        'top_tweets': top_tweets,
        'hype_history': hype_history,
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# SIGNALS ENDPOINTS
# ============================================================================

@app.route('/api/signals')
@rate_limit(60)
def get_signals():
    """Get recent trading signals"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database not found'}), 404
    
    cursor = conn.cursor()
    
    # For MVP, we'll generate signals from hype spikes
    # Real version would have dedicated signals table
    query = '''
        SELECT 
            h.market_id,
            m.question,
            h.timestamp,
            h.hype_score,
            h.tweet_count,
            h.velocity,
            s.price_yes as price_at_signal,
            CASE 
                WHEN h.hype_score > 50 THEN 'BUY'
                WHEN h.hype_score < 20 THEN 'SELL'
                ELSE 'NEUTRAL'
            END as signal_type
        FROM hype_signals h
        JOIN markets m ON h.market_id = m.market_id
        LEFT JOIN snapshots s ON h.market_id = s.market_id 
            AND ABS(strftime('%s', h.timestamp) - strftime('%s', s.timestamp)) < 900
        WHERE h.timestamp > datetime('now', '-7 days')
          AND (h.hype_score > 50 OR h.hype_score < 20)
        ORDER BY h.timestamp DESC
        LIMIT 50
    '''
    
    cursor.execute(query)
    signals = [dict_from_row(row) for row in cursor.fetchall()]
    
    # Calculate signal performance (compare price at signal to current price)
    for signal in signals:
        market_id = signal['market_id']
        
        # Get current price
        cursor.execute('''
            SELECT price_yes FROM snapshots
            WHERE market_id = ?
            ORDER BY timestamp DESC
            LIMIT 1
        ''', (market_id,))
        
        current_price_row = cursor.fetchone()
        if current_price_row and signal['price_at_signal']:
            current_price = current_price_row[0]
            signal['current_price'] = current_price
            signal['price_change'] = current_price - signal['price_at_signal']
            signal['pnl_pct'] = (signal['price_change'] / signal['price_at_signal'] * 100) if signal['price_at_signal'] > 0 else 0
            
            # Determine if signal was correct
            if signal['signal_type'] == 'BUY':
                signal['correct'] = signal['price_change'] > 0
            elif signal['signal_type'] == 'SELL':
                signal['correct'] = signal['price_change'] < 0
            else:
                signal['correct'] = None
        else:
            signal['current_price'] = None
            signal['price_change'] = None
            signal['pnl_pct'] = None
            signal['correct'] = None
    
    conn.close()
    
    return jsonify({
        'signals': signals,
        'count': len(signals),
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# PERFORMANCE ENDPOINTS
# ============================================================================

@app.route('/api/performance')
@rate_limit(60)
def get_performance():
    """Get overall system performance metrics"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database not found'}), 404
    
    cursor = conn.cursor()
    
    # Get signals with performance data (simplified)
    # In real implementation, this would come from a trades table
    query = '''
        SELECT 
            h.timestamp,
            h.market_id,
            h.hype_score,
            s1.price_yes as entry_price,
            (
                SELECT s2.price_yes FROM snapshots s2
                WHERE s2.market_id = h.market_id
                  AND s2.timestamp > h.timestamp
                ORDER BY s2.timestamp ASC
                LIMIT 1
            ) as exit_price
        FROM hype_signals h
        JOIN snapshots s1 ON h.market_id = s1.market_id
            AND ABS(strftime('%s', h.timestamp) - strftime('%s', s1.timestamp)) < 900
        WHERE h.timestamp > datetime('now', '-30 days')
          AND h.hype_score > 50
        ORDER BY h.timestamp ASC
    '''
    
    cursor.execute(query)
    trades = cursor.fetchall()
    
    # Calculate equity curve
    equity_curve = []
    cumulative_pnl = 0
    wins = 0
    losses = 0
    
    for trade in trades:
        timestamp, market_id, hype_score, entry_price, exit_price = trade
        
        if entry_price and exit_price:
            pnl = exit_price - entry_price
            cumulative_pnl += pnl
            
            if pnl > 0:
                wins += 1
            else:
                losses += 1
            
            equity_curve.append({
                'timestamp': timestamp,
                'cumulative_pnl': cumulative_pnl,
                'pnl': pnl
            })
    
    # Calculate metrics
    total_trades = wins + losses
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    
    # Calculate max drawdown
    max_equity = 0
    max_drawdown = 0
    for point in equity_curve:
        equity = point['cumulative_pnl']
        max_equity = max(max_equity, equity)
        drawdown = max_equity - equity
        max_drawdown = max(max_drawdown, drawdown)
    
    conn.close()
    
    return jsonify({
        'equity_curve': equity_curve,
        'metrics': {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 1),
            'total_pnl': round(cumulative_pnl, 4),
            'max_drawdown': round(max_drawdown, 4)
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# TOP HYPE ENDPOINT
# ============================================================================

@app.route('/api/top-hype')
@rate_limit(60)
def get_top_hype():
    """Get markets with highest current hype scores"""
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database not found'}), 404
    
    cursor = conn.cursor()
    
    query = '''
        SELECT 
            m.market_id,
            m.question,
            m.category,
            h.hype_score,
            h.tweet_count,
            h.velocity,
            h.avg_sentiment,
            h.timestamp,
            s.price_yes as current_price
        FROM hype_signals h
        JOIN markets m ON h.market_id = m.market_id
        LEFT JOIN (
            SELECT market_id, price_yes
            FROM snapshots s1
            WHERE timestamp = (
                SELECT MAX(timestamp) FROM snapshots s2
                WHERE s2.market_id = s1.market_id
            )
        ) s ON m.market_id = s.market_id
        WHERE h.timestamp = (
            SELECT MAX(timestamp) FROM hype_signals h2
            WHERE h2.market_id = h.market_id
        )
        ORDER BY h.hype_score DESC
        LIMIT 20
    '''
    
    cursor.execute(query)
    top_markets = [dict_from_row(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'markets': top_markets,
        'count': len(top_markets),
        'timestamp': datetime.utcnow().isoformat()
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Dashboard API Server")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Version: {API_VERSION}")
    print()
    
    if not os.path.exists(DB_PATH):
        print("⚠️  WARNING: Database not found!")
        print(f"   Expected: {DB_PATH}")
        print("   Run data collectors first:")
        print("   - python polymarket-data-collector.py")
        print("   - python twitter-hype-monitor.py")
        print()
    
    print("Starting server on http://localhost:5000")
    print("API endpoints:")
    print("  GET /api/status         - System status")
    print("  GET /api/markets        - All markets")
    print("  GET /api/markets/<id>   - Market details")
    print("  GET /api/signals        - Trading signals")
    print("  GET /api/performance    - Performance metrics")
    print("  GET /api/top-hype       - Top hype markets")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
