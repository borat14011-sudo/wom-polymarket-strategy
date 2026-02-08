"""
Simple Web Dashboard for Paper Trading
Lightweight monitoring interface
"""

import sqlite3
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import json

DB_PATH = "polymarket_data.db"
STARTING_BANKROLL = 100.0


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for dashboard"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.serve_html()
        elif self.path == '/api/stats':
            self.serve_stats()
        elif self.path == '/api/trades':
            self.serve_trades()
        else:
            self.send_error(404)
    
    def serve_html(self):
        """Serve dashboard HTML"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <title>Paper Trading Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0f0f0f;
            color: #e0e0e0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        h1 {
            color: #00ff88;
            border-bottom: 2px solid #00ff88;
            padding-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 20px;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #00ff88;
        }
        .stat-label {
            font-size: 14px;
            color: #888;
            margin-top: 5px;
        }
        .trades-table {
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 8px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #333;
        }
        th {
            background: #252525;
            color: #00ff88;
            font-weight: 600;
        }
        .status-open { color: #ffa500; }
        .status-closed { color: #888; }
        .status-resolved { color: #00ff88; }
        .pnl-positive { color: #00ff88; }
        .pnl-negative { color: #ff4444; }
        .refresh-btn {
            background: #00ff88;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .refresh-btn:hover {
            background: #00dd77;
        }
        .last-updated {
            color: #666;
            font-size: 12px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Paper Trading Dashboard</h1>
        
        <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
        
        <div class="stats-grid" id="stats"></div>
        
        <h2>Recent Trades</h2>
        <div class="trades-table">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Market</th>
                        <th>Side</th>
                        <th>Entry</th>
                        <th>Exit</th>
                        <th>Size</th>
                        <th>P&L</th>
                        <th>Status</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody id="trades"></tbody>
            </table>
        </div>
        
        <div class="last-updated" id="lastUpdated"></div>
    </div>
    
    <script>
        function loadData() {
            // Load stats
            fetch('/api/stats')
                .then(r => r.json())
                .then(data => {
                    const statsHtml = `
                        <div class="stat-card">
                            <div class="stat-value">$${data.current_bankroll.toFixed(2)}</div>
                            <div class="stat-label">Current Bankroll</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value ${data.total_pnl >= 0 ? 'pnl-positive' : 'pnl-negative'}">
                                $${data.total_pnl >= 0 ? '+' : ''}${data.total_pnl.toFixed(2)}
                            </div>
                            <div class="stat-label">Total P&L (${data.total_pnl_pct.toFixed(1)}%)</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.win_rate.toFixed(1)}%</div>
                            <div class="stat-label">Win Rate (${data.winning_trades}/${data.resolved_trades})</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.open_trades}</div>
                            <div class="stat-label">Open Positions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.total_trades}</div>
                            <div class="stat-label">Total Trades</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">${data.avg_roi.toFixed(1)}%</div>
                            <div class="stat-label">Avg ROI</div>
                        </div>
                    `;
                    document.getElementById('stats').innerHTML = statsHtml;
                });
            
            // Load trades
            fetch('/api/trades')
                .then(r => r.json())
                .then(data => {
                    const tradesHtml = data.map(t => `
                        <tr>
                            <td>${t.id}</td>
                            <td>${t.market_name.substring(0, 40)}...</td>
                            <td><strong>${t.side}</strong></td>
                            <td>${(t.entry_price * 100).toFixed(1)}%</td>
                            <td>${t.exit_price ? (t.exit_price * 100).toFixed(1) + '%' : '-'}</td>
                            <td>$${t.position_size.toFixed(2)}</td>
                            <td class="${t.pnl_dollars >= 0 ? 'pnl-positive' : 'pnl-negative'}">
                                ${t.pnl_dollars >= 0 ? '+' : ''}$${t.pnl_dollars.toFixed(2)}
                            </td>
                            <td class="status-${t.status.toLowerCase()}">${t.status}</td>
                            <td>${new Date(t.entry_time * 1000).toLocaleString()}</td>
                        </tr>
                    `).join('');
                    document.getElementById('trades').innerHTML = tradesHtml;
                    
                    document.getElementById('lastUpdated').textContent = 
                        `Last updated: ${new Date().toLocaleString()}`;
                });
        }
        
        // Load data on page load
        loadData();
        
        // Auto-refresh every 60 seconds
        setInterval(loadData, 60000);
    </script>
</body>
</html>
        """.strip()
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def serve_stats(self):
        """Serve portfolio statistics as JSON"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Get stats
            cursor.execute("SELECT COUNT(*) FROM paper_trades")
            total_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE status = 'OPEN'")
            open_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(pnl_dollars) FROM paper_trades WHERE status != 'OPEN'")
            total_pnl = cursor.fetchone()[0] or 0.0
            
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE resolved = 1")
            resolved_trades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM paper_trades WHERE trade_correct = 1")
            winning_trades = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT AVG(pnl_percent) FROM paper_trades 
                WHERE status != 'OPEN' AND pnl_percent IS NOT NULL
            """)
            avg_roi = cursor.fetchone()[0] or 0
            
            conn.close()
            
            win_rate = (winning_trades / resolved_trades * 100) if resolved_trades > 0 else 0
            current_bankroll = STARTING_BANKROLL + total_pnl
            
            stats = {
                'total_trades': total_trades,
                'open_trades': open_trades,
                'resolved_trades': resolved_trades,
                'winning_trades': winning_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_pnl_pct': (total_pnl / STARTING_BANKROLL * 100),
                'current_bankroll': current_bankroll,
                'avg_roi': avg_roi
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def serve_trades(self):
        """Serve recent trades as JSON"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, market_name, side, entry_price, exit_price, 
                       position_size, pnl_dollars, status, entry_time
                FROM paper_trades
                ORDER BY entry_time DESC
                LIMIT 50
            """)
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'id': row[0],
                    'market_name': row[1],
                    'side': row[2],
                    'entry_price': row[3],
                    'exit_price': row[4],
                    'position_size': row[5],
                    'pnl_dollars': row[6],
                    'status': row[7],
                    'entry_time': row[8]
                })
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(trades).encode())
            
        except Exception as e:
            self.send_error(500, str(e))
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_dashboard(port=8080):
    """Run dashboard server"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"📊 Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard stopped")
        server.shutdown()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080, help='Port to run dashboard on')
    args = parser.parse_args()
    
    run_dashboard(args.port)
