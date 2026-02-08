# Trading System Dashboard

![Dashboard Status](https://img.shields.io/badge/status-MVP-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

**Simple web dashboard for monitoring prediction market trading system**

## 📋 Overview

This dashboard provides real-time visualization of your trading system's performance, including:

- **Home**: System status, database stats, last collection times
- **Markets**: All tracked markets with prices, 24h changes, and hype scores
- **Signals**: Recent trading signals with performance tracking
- **Performance**: Equity curve, win rate, P&L metrics
- **Top Hype**: Live leaderboard of markets with highest hype scores

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Data collection scripts running (`polymarket-data-collector.py` and `twitter-hype-monitor.py`)
- SQLite database (`polymarket_data.db`) with collected data

### Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the dashboard:**
   
   **Linux/Mac:**
   ```bash
   ./start-dashboard.sh
   ```
   
   **Windows:**
   ```cmd
   start-dashboard.bat
   ```
   
   Or manually:
   ```bash
   # Start API server
   python api.py
   
   # Open dashboard.html in your browser
   ```

3. **Access the dashboard:**
   - The launcher script will automatically open `dashboard.html` in your browser
   - API runs on: `http://localhost:5000`
   - Dashboard auto-refreshes every 60 seconds

## 📁 Files

```
.
├── dashboard.html          # Frontend (HTML + CSS + JS)
├── api.py                  # Flask backend API
├── requirements.txt        # Python dependencies
├── start-dashboard.sh      # Linux/Mac launcher
├── start-dashboard.bat     # Windows launcher
├── DASHBOARD-README.md     # This file
└── polymarket_data.db      # SQLite database (created by data collectors)
```

## 🎯 Features

### Home View
- **System Status**: Total markets, snapshots, tweets tracked
- **Database Stats**: Size and record counts
- **Last Updates**: When data was last collected

### Markets View
- **Market List**: All tracked markets with current data
- **Price Information**: Current price, 24h change percentage
- **Volume Stats**: 24-hour trading volume
- **Hype Scores**: Twitter sentiment/engagement scores
- **Click to Expand**: Detailed view with price chart and top tweets

### Signals View
- **Recent Signals**: Latest BUY/SELL/NEUTRAL signals
- **Performance Tracking**: Current P&L for each signal
- **Win/Loss Status**: Visual indicators of signal correctness
- **Color Coding**: Green for profitable, red for losing

### Performance View
- **Equity Curve**: Cumulative P&L over time
- **Key Metrics**:
  - Total trades executed
  - Win rate percentage
  - Total P&L
  - Maximum drawdown

### Top Hype View
- **Live Leaderboard**: Markets ranked by hype score
- **Tweet Metrics**: Tweet count and velocity (rate of change)
- **Category Breakdown**: Markets organized by category
- **Real-time Updates**: Auto-refresh every 60 seconds

## 🔧 Configuration

### API Settings

Edit `api.py` to configure:

```python
# Database path
DB_PATH = "polymarket_data.db"

# Rate limiting (requests per minute)
@rate_limit(60)  # Change to your preferred limit
```

### Frontend Settings

Edit `dashboard.html` JavaScript section:

```javascript
// API base URL
const API_BASE = 'http://localhost:5000/api';

// Auto-refresh interval (milliseconds)
const REFRESH_INTERVAL = 60000; // 60 seconds
```

## 📊 API Endpoints

The Flask backend exposes these REST API endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | System status and database stats |
| `GET /api/markets` | List all tracked markets |
| `GET /api/markets/<id>` | Detailed market data with price history |
| `GET /api/signals` | Recent trading signals |
| `GET /api/performance` | Performance metrics and equity curve |
| `GET /api/top-hype` | Markets with highest hype scores |

**Example API Call:**
```bash
curl http://localhost:5000/api/status
```

**Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "timestamp": "2026-02-06T10:30:00",
  "database": {
    "path": "polymarket_data.db",
    "size_mb": 12.45,
    "markets": 15,
    "snapshots": 4320,
    "tweets": 8542,
    "signals": 123
  },
  "last_collection": {
    "market_data": "2026-02-06T10:25:00",
    "twitter_data": "2026-02-06T10:20:00"
  }
}
```

## 🎨 Customization

### Dark Theme Colors

The dashboard uses CSS variables for easy color customization. Edit `dashboard.html`:

```css
:root {
    --bg-primary: #0a0e27;      /* Main background */
    --bg-secondary: #131829;    /* Secondary background */
    --bg-card: #1a1f3a;         /* Card background */
    --accent-blue: #4da3ff;     /* Primary accent */
    --accent-green: #00c851;    /* Positive/buy */
    --accent-red: #ff4444;      /* Negative/sell */
    --accent-yellow: #ffbb33;   /* Warning/hype */
}
```

### Adding Custom Views

1. Add HTML section:
```html
<div id="my-view" class="view">
    <!-- Your content here -->
</div>
```

2. Add navigation button:
```html
<button class="nav-btn" onclick="showView('my-view')">My View</button>
```

3. Add data loading function:
```javascript
function loadMyView() {
    fetchAPI('/my-endpoint').then(data => {
        // Render your data
    });
}
```

## 🐛 Troubleshooting

### Database Not Found

**Problem:** Dashboard shows "Database not found" error

**Solution:**
1. Run data collectors first:
   ```bash
   python polymarket-data-collector.py
   python twitter-hype-monitor.py
   ```
2. Verify `polymarket_data.db` exists in the same directory
3. Check database permissions (should be readable)

### API Connection Failed

**Problem:** Dashboard shows "Disconnected" status

**Solutions:**
1. **API not running:**
   ```bash
   python api.py
   ```

2. **Port already in use:**
   ```bash
   # Kill process on port 5000
   lsof -ti:5000 | xargs kill -9  # Mac/Linux
   netstat -ano | findstr :5000   # Windows (find PID, then kill)
   ```

3. **CORS issues:** 
   - Make sure `flask-cors` is installed: `pip install flask-cors`
   - Check browser console for CORS errors

### No Data Showing

**Problem:** Dashboard loads but shows no markets/signals

**Solution:**
1. **Check data collection:**
   ```bash
   sqlite3 polymarket_data.db "SELECT COUNT(*) FROM markets;"
   sqlite3 polymarket_data.db "SELECT COUNT(*) FROM snapshots;"
   ```

2. **Run collectors:**
   ```bash
   # Collect market data
   python polymarket-data-collector.py
   
   # Collect Twitter data
   python twitter-hype-monitor.py
   ```

3. **Check logs:**
   - Look for errors in API console output
   - Check browser developer tools console

### Chart Not Rendering

**Problem:** Equity curve or other charts don't display

**Solution:**
1. **Internet connection:** Chart.js loads from CDN
2. **Browser compatibility:** Use modern browser (Chrome, Firefox, Safari, Edge)
3. **Console errors:** Check browser dev tools for JavaScript errors

### Slow Performance

**Problem:** Dashboard is slow or unresponsive

**Solutions:**
1. **Large database:** 
   - Archive old data: `sqlite3 polymarket_data.db "DELETE FROM snapshots WHERE timestamp < datetime('now', '-30 days');"`
   - Vacuum database: `sqlite3 polymarket_data.db "VACUUM;"`

2. **Reduce refresh rate:**
   ```javascript
   // In dashboard.html
   const REFRESH_INTERVAL = 120000; // 2 minutes instead of 1
   ```

3. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 api:app
   ```

## 📈 Production Deployment

For production use (accessible from other devices):

### Option 1: Gunicorn (Linux/Mac)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

### Option 2: Waitress (Windows-friendly)

```bash
pip install waitress
waitress-serve --host 0.0.0.0 --port 5000 api:app
```

### Option 3: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "api:app"]
```

Build and run:
```bash
docker build -t trading-dashboard .
docker run -p 5000:5000 -v $(pwd)/polymarket_data.db:/app/polymarket_data.db trading-dashboard
```

### Security Considerations

For production deployment:

1. **Enable authentication:**
   ```python
   # In api.py
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   
   @auth.verify_password
   def verify_password(username, password):
       return username == 'admin' and password == 'your_password'
   
   @app.route('/api/status')
   @auth.login_required
   def get_status():
       ...
   ```

2. **Use HTTPS:** Deploy behind nginx with SSL certificate

3. **Rate limiting:** Already implemented, adjust limits as needed

4. **Database backups:** Regular backups of `polymarket_data.db`

## 📸 Screenshots

### Home View
```
┌─────────────────────────────────────────────────────────────┐
│ 📊 Trading System Dashboard              🟢 Connected       │
├─────────────────────────────────────────────────────────────┤
│ [Home] [Markets] [Signals] [Performance] [Top Hype]         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ TOTAL MARKETS│ │   SNAPSHOTS  │ │    TWEETS    │        │
│  │      15      │ │     4,320    │ │    8,542     │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Markets View
```
┌─────────────────────────────────────────────────────────────┐
│ Market                    | Price   | 24h Change | Hype     │
├─────────────────────────────────────────────────────────────┤
│ Bitcoin >$100K by 2026?   | $0.652  | +12.5% ↑   | 78.3    │
│ Trump wins 2024 election? | $0.441  | -3.2% ↓    | 65.1    │
│ Lakers NBA Champions?     | $0.123  | +8.7% ↑    | 42.6    │
└─────────────────────────────────────────────────────────────┘
```

### Performance View
```
┌─────────────────────────────────────────────────────────────┐
│ Total Trades: 45  |  Win Rate: 62.2%  |  Max DD: -0.08     │
│                                                              │
│  Equity Curve:                                              │
│  │                                     ╱──╲                 │
│  │                    ╱──╲           ╱      ╲               │
│  │         ╱────╲   ╱      ╲       ╱          ╲             │
│  │      ╱         ─╯          ─────              ────       │
│  └──────────────────────────────────────────────────────────│
│     Day 1      Day 15       Day 30                          │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Development

### Running in Development Mode

```bash
# Enable Flask debug mode
export FLASK_ENV=development
python api.py
```

### Testing API Endpoints

```bash
# Install httpie
pip install httpie

# Test endpoints
http GET localhost:5000/api/status
http GET localhost:5000/api/markets
http GET localhost:5000/api/signals
```

### Database Schema

The dashboard expects these tables:

- `markets` - Market metadata
- `snapshots` - Price/volume snapshots
- `tweets` - Individual tweets
- `hype_signals` - Aggregated Twitter metrics

See `DATA-COLLECTION-PIPELINE.md` for detailed schema.

## 📝 TODO / Future Enhancements

- [ ] Real-time WebSocket updates (instead of polling)
- [ ] User authentication and multi-user support
- [ ] Customizable alerts (email/SMS when signals trigger)
- [ ] Export data to CSV/Excel
- [ ] Advanced filtering and search
- [ ] Dark/light theme toggle
- [ ] Mobile app (React Native wrapper)
- [ ] Integration with trading execution
- [ ] Backtesting simulator in UI
- [ ] Portfolio tracking and risk metrics

## 🤝 Contributing

This is an MVP dashboard. Improvements welcome!

**Ideas for contribution:**
- Add new chart types (candlestick, scatter plots)
- Implement user preferences/settings
- Add more performance metrics (Sharpe ratio, Sortino, etc.)
- Create alerts/notifications system
- Build trading execution interface
- Add market comparison tools

## 📄 License

MIT License - do whatever you want with this code!

## 🆘 Support

If you run into issues:

1. Check this README's troubleshooting section
2. Check API logs: Look at console output from `python api.py`
3. Check browser console: Open Developer Tools (F12) and look for errors
4. Verify database: `sqlite3 polymarket_data.db .tables`
5. Test API manually: `curl http://localhost:5000/api/status`

---

**Built with:** Flask, Chart.js, vanilla JavaScript, lots of caffeine ☕

**Version:** 1.0.0 MVP  
**Last Updated:** 2026-02-06
