"""
Real-Time Dashboard API v2 - Backend with WebSocket
Flask + Flask-SocketIO for real-time updates
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'polymarket-dashboard-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Mock data storage
markets_data = []
signals_data = []
portfolio_data = {
    "total_value": 10000.0,
    "cash": 5000.0,
    "positions_value": 5000.0,
    "total_pnl": 234.56,
    "positions": []
}
performance_data = {
    "equity_curve": [],
    "trades": [],
    "stats": {}
}
system_status = {
    "overall": "healthy",
    "components": {}
}

# Initialize mock data
def init_mock_data():
    global markets_data, signals_data, portfolio_data, performance_data
    
    # Mock markets
    categories = ["Politics", "Crypto", "Sports", "Economics"]
    markets_data = [
        {
            "id": f"market_{i}",
            "title": f"{random.choice(['Biden wins', 'Trump wins', 'BTC above', 'ETH reaches', 'Lakers win', 'Inflation hits'])} {random.randint(50, 100)}%",
            "category": random.choice(categories),
            "current_price": round(random.uniform(0.3, 0.7), 3),
            "volume_24h": random.randint(10000, 500000),
            "hype_score": round(random.uniform(0.1, 0.9), 2),
            "last_update": datetime.now().isoformat()
        }
        for i in range(20)
    ]
    
    # Mock signals
    signals_data = [
        {
            "id": f"signal_{i}",
            "market_id": f"market_{random.randint(0, 19)}",
            "market_title": markets_data[random.randint(0, 19)]["title"],
            "signal_type": random.choice(["BUY", "SELL"]),
            "confidence": round(random.uniform(0.6, 0.95), 2),
            "price": round(random.uniform(0.3, 0.7), 3),
            "size": random.randint(10, 100),
            "reason": random.choice([
                "High hype correlation detected",
                "Volume surge + price momentum",
                "Sentiment shift positive",
                "Technical breakout pattern",
                "News catalyst identified"
            ]),
            "timestamp": datetime.now().isoformat()
        }
        for i in range(5)
    ]
    
    # Mock portfolio positions
    portfolio_data["positions"] = [
        {
            "market_id": f"market_{i}",
            "market_title": markets_data[i]["title"],
            "side": random.choice(["LONG", "SHORT"]),
            "entry_price": round(random.uniform(0.3, 0.7), 3),
            "current_price": markets_data[i]["current_price"],
            "quantity": random.randint(10, 100),
            "pnl": round(random.uniform(-50, 150), 2),
            "pnl_percent": round(random.uniform(-10, 25), 2)
        }
        for i in range(8)
    ]
    
    # Mock equity curve (last 30 days)
    base_equity = 10000
    performance_data["equity_curve"] = [
        {
            "date": (datetime.now() - timedelta(days=30-i)).strftime("%Y-%m-%d"),
            "equity": round(base_equity + random.uniform(-500, 1000) * (i/30), 2)
        }
        for i in range(31)
    ]
    
    # Mock recent trades
    performance_data["trades"] = [
        {
            "id": f"trade_{i}",
            "market_title": markets_data[random.randint(0, 19)]["title"][:40] + "...",
            "side": random.choice(["BUY", "SELL"]),
            "entry_price": round(random.uniform(0.3, 0.7), 3),
            "exit_price": round(random.uniform(0.3, 0.7), 3),
            "pnl": round(random.uniform(-50, 100), 2),
            "timestamp": (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
        }
        for i in range(15)
    ]
    
    # Calculate stats
    winning_trades = [t for t in performance_data["trades"] if t["pnl"] > 0]
    performance_data["stats"] = {
        "total_trades": len(performance_data["trades"]),
        "winning_trades": len(winning_trades),
        "losing_trades": len(performance_data["trades"]) - len(winning_trades),
        "win_rate": round(len(winning_trades) / len(performance_data["trades"]) * 100, 1) if performance_data["trades"] else 0,
        "avg_win": round(sum(t["pnl"] for t in winning_trades) / len(winning_trades), 2) if winning_trades else 0,
        "avg_loss": round(sum(t["pnl"] for t in performance_data["trades"] if t["pnl"] < 0) / (len(performance_data["trades"]) - len(winning_trades)), 2) if len(performance_data["trades"]) > len(winning_trades) else 0
    }
    
    # System status
    system_status["components"] = {
        "data_feed": {"status": "healthy", "latency_ms": random.randint(50, 200)},
        "signal_engine": {"status": "healthy", "last_run": datetime.now().isoformat()},
        "order_manager": {"status": "healthy", "pending_orders": random.randint(0, 3)},
        "risk_monitor": {"status": "healthy", "alerts": 0},
        "database": {"status": "healthy", "connections": random.randint(5, 15)}
    }

init_mock_data()

# REST API Endpoints

@app.route('/api/status', methods=['GET'])
def get_status():
    """System status"""
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "system": system_status
    })

@app.route('/api/markets', methods=['GET'])
def get_markets():
    """Get all markets"""
    category = request.args.get('category')
    search = request.args.get('search', '').lower()
    
    filtered = markets_data
    if category and category != 'all':
        filtered = [m for m in filtered if m['category'] == category]
    if search:
        filtered = [m for m in filtered if search in m['title'].lower()]
    
    return jsonify({
        "markets": filtered,
        "total": len(filtered),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/signals', methods=['GET'])
def get_signals():
    """Get active signals"""
    return jsonify({
        "signals": signals_data,
        "total": len(signals_data),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get portfolio summary"""
    return jsonify({
        "portfolio": portfolio_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    return jsonify({
        "performance": performance_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/market/<market_id>', methods=['GET'])
def get_market_detail(market_id):
    """Get detailed market info"""
    market = next((m for m in markets_data if m['id'] == market_id), None)
    if not market:
        return jsonify({"error": "Market not found"}), 404
    
    # Add extra details
    market_detail = market.copy()
    market_detail["price_history"] = [
        {"time": (datetime.now() - timedelta(minutes=30-i)).isoformat(), 
         "price": round(market["current_price"] + random.uniform(-0.1, 0.1), 3)}
        for i in range(30)
    ]
    market_detail["order_book"] = {
        "bids": [[round(market["current_price"] - i*0.01, 3), random.randint(10, 100)] for i in range(1, 6)],
        "asks": [[round(market["current_price"] + i*0.01, 3), random.randint(10, 100)] for i in range(1, 6)]
    }
    
    return jsonify({
        "market": market_detail,
        "timestamp": datetime.now().isoformat()
    })

# WebSocket handlers

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.now().isoformat()})

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('subscribe')
def handle_subscribe(data):
    """Client subscribes to specific updates"""
    print(f"Client {request.sid} subscribed to: {data}")
    emit('subscription_confirmed', data)

# Background task to push updates
def push_updates():
    """Push updates every 30 seconds"""
    while True:
        time.sleep(30)
        
        # Update market prices
        for market in markets_data:
            market["current_price"] = round(
                max(0.01, min(0.99, market["current_price"] + random.uniform(-0.05, 0.05))),
                3
            )
            market["volume_24h"] += random.randint(-1000, 5000)
            market["hype_score"] = round(
                max(0.0, min(1.0, market["hype_score"] + random.uniform(-0.1, 0.1))),
                2
            )
            market["last_update"] = datetime.now().isoformat()
        
        # Update portfolio P&L
        total_pnl = sum(pos["pnl"] for pos in portfolio_data["positions"])
        portfolio_data["total_pnl"] = round(total_pnl, 2)
        portfolio_data["total_value"] = portfolio_data["cash"] + portfolio_data["positions_value"]
        
        # Randomly generate new signal
        if random.random() > 0.7:
            new_signal = {
                "id": f"signal_{len(signals_data)}",
                "market_id": f"market_{random.randint(0, 19)}",
                "market_title": markets_data[random.randint(0, 19)]["title"],
                "signal_type": random.choice(["BUY", "SELL"]),
                "confidence": round(random.uniform(0.6, 0.95), 2),
                "price": round(random.uniform(0.3, 0.7), 3),
                "size": random.randint(10, 100),
                "reason": random.choice([
                    "High hype correlation detected",
                    "Volume surge + price momentum",
                    "Sentiment shift positive"
                ]),
                "timestamp": datetime.now().isoformat()
            }
            signals_data.insert(0, new_signal)
            if len(signals_data) > 10:
                signals_data.pop()
            
            socketio.emit('new_signal', new_signal)
        
        # Update system status
        system_status["components"]["data_feed"]["latency_ms"] = random.randint(50, 300)
        system_status["components"]["order_manager"]["pending_orders"] = random.randint(0, 5)
        
        # Broadcast updates
        socketio.emit('market_update', {
            "markets": markets_data[:10],  # Send top 10 for efficiency
            "timestamp": datetime.now().isoformat()
        })
        
        socketio.emit('portfolio_update', {
            "portfolio": portfolio_data,
            "timestamp": datetime.now().isoformat()
        })
        
        socketio.emit('system_status', {
            "status": system_status,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Pushed updates to clients")

# Start background thread
update_thread = threading.Thread(target=push_updates, daemon=True)
update_thread.start()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Polymarket Dashboard API v2 - Real-Time WebSocket Server")
    print("=" * 60)
    print(f"Server starting at: http://localhost:5000")
    print(f"WebSocket endpoint: ws://localhost:5000/socket.io/")
    print("\nEndpoints:")
    print("  GET /api/status       - System status")
    print("  GET /api/markets      - All markets")
    print("  GET /api/signals      - Active signals")
    print("  GET /api/portfolio    - Portfolio summary")
    print("  GET /api/performance  - Performance metrics")
    print("  WS  /socket.io/       - Real-time updates")
    print("\n📊 Updates pushed every 30 seconds via WebSocket")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
