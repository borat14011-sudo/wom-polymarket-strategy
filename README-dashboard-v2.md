# 🚀 Polymarket Trading Dashboard v2 - Real-Time Edition

Professional dark-themed trading dashboard with WebSocket real-time updates for Polymarket trading system.

## 🎯 Features

### Real-Time Updates (WebSocket)
- **Live market prices** - Updates every 30 seconds
- **New signal alerts** - Instant notifications
- **Portfolio tracking** - Real-time P&L updates
- **System health monitoring** - Component status

### Dashboard Sections
1. **Overview** - Complete system view with all key metrics
2. **Portfolio** - Detailed positions and P&L breakdown
3. **Performance** - Charts and trading statistics

### Key Components
- 📊 **Active Signals** - BUY/SELL recommendations with confidence scores
- 📈 **Market Watchlist** - Top markets with prices, volume, hype scores
- 💼 **Portfolio Summary** - Total value, P&L, open positions
- 📉 **Performance Charts** - Equity curve, win/loss distribution, correlations
- 📝 **Recent Trades** - Trade history log
- 🏥 **System Health** - Component monitoring

### Interactive Features
- ✅ Search markets
- ✅ Filter by category (Politics, Crypto, Sports, Economics)
- ✅ Click markets for details
- ✅ Toggle between views (Overview, Portfolio, Performance)
- ✅ Real-time status indicators
- ✅ Responsive design (mobile-friendly)

## 🛠️ Installation

### 1. Install Python Dependencies
```bash
pip install -r requirements-dashboard-v2.txt
```

### 2. Start the Backend Server
```bash
python api-v2.py
```

You should see:
```
🚀 Polymarket Dashboard API v2 - Real-Time WebSocket Server
Server starting at: http://localhost:5000
📊 Updates pushed every 30 seconds via WebSocket
```

### 3. Open the Dashboard
Simply open `dashboard-v2.html` in your browser:
- **Chrome/Edge** (recommended): Better WebSocket support
- **Firefox**: Also works great
- **Safari**: Works but may have slight differences

Or serve it with a simple HTTP server:
```bash
# Python 3
python -m http.server 8080

# Then visit: http://localhost:8080/dashboard-v2.html
```

## 🎨 Design

### Dark Theme
- Professional trading terminal aesthetic
- Dark blue/grey palette with accent colors
- Green (BUY) / Red (SELL) signal indicators
- Smooth animations and transitions

### Responsive Layout
- Grid-based responsive design
- Mobile-friendly (works on phones/tablets)
- Auto-adjusting card layouts
- Touch-friendly interactions

## 📡 API Endpoints

### REST API
- `GET /api/status` - System status
- `GET /api/markets` - All markets (with search/filter params)
- `GET /api/signals` - Active signals
- `GET /api/portfolio` - Portfolio summary
- `GET /api/performance` - Performance metrics
- `GET /api/market/<id>` - Market details

### WebSocket Events

**Client → Server:**
- `connect` - Initial connection
- `subscribe` - Subscribe to specific updates

**Server → Client:**
- `connection_status` - Connection confirmation
- `market_update` - Market price updates (every 30s)
- `portfolio_update` - Portfolio updates (every 30s)
- `new_signal` - New trading signal generated
- `system_status` - System health updates (every 30s)

## 🔧 Configuration

### Backend (api-v2.py)
- **Port**: 5000 (change in `socketio.run()`)
- **Update interval**: 30 seconds (change in `push_updates()`)
- **CORS**: Enabled for all origins (change in `CORS(app)`)

### Frontend (dashboard-v2.html)
- **API_BASE**: `http://localhost:5000` (change at top of script)
- **Charts**: Chart.js via CDN
- **WebSocket**: Socket.IO client via CDN

## 📊 Data Flow

1. **Backend** generates mock trading data
2. **Flask** serves REST API endpoints
3. **Flask-SocketIO** manages WebSocket connections
4. **Background thread** pushes updates every 30 seconds
5. **Frontend** receives updates and renders in real-time
6. **Charts** update dynamically with new data

## 🎭 Mock Data

The current implementation uses **mock data** for demonstration. To integrate with real Polymarket data:

1. Replace mock data generation in `api-v2.py`
2. Connect to Polymarket API
3. Integrate with your trading signals engine
4. Add real portfolio data source

## 🚀 Next Steps

**Integration:**
- [ ] Connect to real Polymarket API
- [ ] Integrate with signal generation engine
- [ ] Add order execution functionality
- [ ] Implement user authentication

**Features:**
- [ ] Price alerts and notifications
- [ ] Trade history export (CSV/Excel)
- [ ] Advanced charting (candlesticks, indicators)
- [ ] Risk management controls
- [ ] Multi-user support

**UI Enhancements:**
- [ ] Dark/light theme toggle
- [ ] Customizable dashboard layout
- [ ] Market detail modal with order book
- [ ] Settings panel

## 🐛 Troubleshooting

**WebSocket not connecting:**
- Check if backend is running (`python api-v2.py`)
- Verify port 5000 is available
- Check browser console for errors
- Try disabling browser extensions

**No data showing:**
- Open browser DevTools (F12) → Console
- Check for CORS errors
- Verify API endpoints are responding (visit http://localhost:5000/api/status)

**Charts not rendering:**
- Ensure Chart.js CDN is accessible
- Check browser console for errors
- Try hard refresh (Ctrl+Shift+R)

## 📝 License

Great success! 🎉

---

**Built with:**
- Flask + Flask-SocketIO (Backend)
- HTML5 + CSS3 + Vanilla JavaScript (Frontend)
- Chart.js (Visualizations)
- Socket.IO (Real-time updates)
