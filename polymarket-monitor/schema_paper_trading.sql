-- Forward Paper Trading System - Database Schema
-- Creates tables for live validation of trading strategies
-- Run: sqlite3 polymarket_data.db < schema_paper_trading.sql

-- Paper Trades Table
-- Records all simulated paper trades (no real money)
CREATE TABLE IF NOT EXISTS paper_trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Market info
    market_id TEXT NOT NULL,
    market_name TEXT NOT NULL,
    
    -- Entry details
    side TEXT NOT NULL CHECK(side IN ('YES', 'NO')),
    entry_price REAL NOT NULL CHECK(entry_price >= 0 AND entry_price <= 1),
    position_size REAL NOT NULL CHECK(position_size > 0),
    entry_time INTEGER NOT NULL,
    
    -- Risk management
    stop_loss REAL NOT NULL,
    take_profit_1 REAL,
    take_profit_2 REAL,
    take_profit_3 REAL,
    
    -- Signal metadata (from signal_detector_v2.py)
    rvr_ratio REAL,
    roc_24h_pct REAL,
    days_to_resolution INTEGER,
    orderbook_depth REAL,
    
    -- Exit tracking
    status TEXT DEFAULT 'OPEN' CHECK(status IN ('OPEN', 'CLOSED', 'RESOLVED')),
    exit_price REAL,
    exit_time INTEGER,
    exit_reason TEXT,  -- 'STOP_LOSS', 'TAKE_PROFIT_1', 'TAKE_PROFIT_2', 'TAKE_PROFIT_3', 'MARKET_RESOLVED'
    pnl_dollars REAL DEFAULT 0,
    pnl_percent REAL DEFAULT 0,
    
    -- Market resolution
    resolved INTEGER DEFAULT 0 CHECK(resolved IN (0, 1)),
    resolution_outcome TEXT CHECK(resolution_outcome IN ('YES', 'NO', NULL)),
    resolution_time INTEGER,
    
    -- Validation metrics
    trade_correct INTEGER CHECK(trade_correct IN (0, 1, NULL)),  -- 1 = won, 0 = lost, NULL = pending
    theoretical_edge REAL,  -- Expected edge from backtests (e.g., 0.60 = 60% win rate)
    actual_edge REAL        -- Actual edge realized (calculated after resolution)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_paper_trades_status ON paper_trades(status);
CREATE INDEX IF NOT EXISTS idx_paper_trades_market ON paper_trades(market_id);
CREATE INDEX IF NOT EXISTS idx_paper_trades_entry_time ON paper_trades(entry_time);
CREATE INDEX IF NOT EXISTS idx_paper_trades_resolved ON paper_trades(resolved);

-- Paper Position Ticks Table
-- Records tick-by-tick price movements for open positions
CREATE TABLE IF NOT EXISTS paper_position_ticks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_id INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    
    -- Price snapshot
    current_price REAL NOT NULL,
    pnl_unrealized REAL NOT NULL,
    pnl_pct REAL NOT NULL,
    
    -- Market conditions
    market_volume_24h REAL,
    orderbook_depth REAL,
    
    FOREIGN KEY (trade_id) REFERENCES paper_trades(id) ON DELETE CASCADE
);

-- Indexes for tick queries
CREATE INDEX IF NOT EXISTS idx_ticks_trade ON paper_position_ticks(trade_id);
CREATE INDEX IF NOT EXISTS idx_ticks_time ON paper_position_ticks(timestamp);

-- Market Resolutions Table
-- Records actual outcomes when markets resolve
CREATE TABLE IF NOT EXISTS market_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    market_id TEXT UNIQUE NOT NULL,
    market_name TEXT NOT NULL,
    
    -- Resolution details
    resolution_time INTEGER NOT NULL,
    resolution_outcome TEXT NOT NULL CHECK(resolution_outcome IN ('YES', 'NO')),
    final_yes_price REAL CHECK(final_yes_price IN (0.0, 1.0)),  -- Should be 0 or 1
    final_no_price REAL CHECK(final_no_price IN (0.0, 1.0)),
    total_volume REAL,
    resolution_source TEXT,  -- Metadata about how we detected resolution
    
    -- Statistics for this market
    num_paper_trades INTEGER DEFAULT 0,
    num_correct_trades INTEGER DEFAULT 0,
    avg_roi REAL
);

CREATE INDEX IF NOT EXISTS idx_resolutions_market ON market_resolutions(market_id);
CREATE INDEX IF NOT EXISTS idx_resolutions_time ON market_resolutions(resolution_time);

-- Validation Metrics Table
-- Daily snapshots of paper trading performance
CREATE TABLE IF NOT EXISTS validation_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_date TEXT NOT NULL UNIQUE,  -- YYYY-MM-DD format
    
    -- Overall statistics
    total_trades INTEGER DEFAULT 0,
    total_resolved INTEGER DEFAULT 0,
    total_open INTEGER DEFAULT 0,
    
    -- Performance metrics
    win_rate REAL,        -- Percentage of winning trades
    avg_roi REAL,         -- Average ROI per trade
    total_pnl REAL,       -- Total P&L in dollars
    total_pnl_pct REAL,   -- Total P&L as percentage
    
    -- Strategy breakdown
    yes_side_trades INTEGER DEFAULT 0,
    yes_side_wins INTEGER DEFAULT 0,
    yes_side_win_rate REAL,
    
    no_side_trades INTEGER DEFAULT 0,
    no_side_wins INTEGER DEFAULT 0,
    no_side_win_rate REAL,
    
    politics_trades INTEGER DEFAULT 0,
    politics_wins INTEGER DEFAULT 0,
    politics_win_rate REAL,
    
    crypto_trades INTEGER DEFAULT 0,
    crypto_wins INTEGER DEFAULT 0,
    crypto_win_rate REAL,
    
    -- Filter validation (does the filter actually help?)
    depth_filter_trades INTEGER DEFAULT 0,
    depth_filter_wins INTEGER DEFAULT 0,
    depth_filter_win_rate REAL,
    
    trend_filter_trades INTEGER DEFAULT 0,
    trend_filter_wins INTEGER DEFAULT 0,
    trend_filter_win_rate REAL,
    
    rvr_filter_trades INTEGER DEFAULT 0,
    rvr_filter_wins INTEGER DEFAULT 0,
    rvr_filter_win_rate REAL,
    
    -- Edge measurement
    theoretical_edge REAL,  -- From backtests (e.g., 0.60)
    realized_edge REAL,     -- From forward testing (e.g., 0.61)
    edge_gap REAL,          -- Difference (should be small, <0.05)
    
    -- Risk metrics
    max_drawdown_pct REAL,
    sharpe_ratio REAL,
    
    -- Sample size context
    min_sample_reached INTEGER DEFAULT 0 CHECK(min_sample_reached IN (0, 1)),  -- 1 if >= 20 resolved trades
    validation_complete INTEGER DEFAULT 0 CHECK(validation_complete IN (0, 1))  -- 1 if ready for go-live decision
);

CREATE INDEX IF NOT EXISTS idx_validation_date ON validation_metrics(snapshot_date);

-- Initial data check view
CREATE VIEW IF NOT EXISTS v_paper_trading_summary AS
SELECT 
    COUNT(*) as total_paper_trades,
    SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as open_positions,
    SUM(CASE WHEN status != 'OPEN' THEN 1 ELSE 0 END) as closed_positions,
    SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN trade_correct = 0 THEN 1 ELSE 0 END) as losing_trades,
    ROUND(AVG(CASE WHEN trade_correct IS NOT NULL THEN trade_correct END) * 100, 1) as win_rate_pct,
    ROUND(SUM(pnl_dollars), 2) as total_pnl,
    ROUND(AVG(pnl_percent), 1) as avg_pnl_pct
FROM paper_trades;

-- Trade performance by side
CREATE VIEW IF NOT EXISTS v_paper_trades_by_side AS
SELECT 
    side,
    COUNT(*) as total_trades,
    SUM(CASE WHEN trade_correct = 1 THEN 1 ELSE 0 END) as wins,
    SUM(CASE WHEN trade_correct = 0 THEN 1 ELSE 0 END) as losses,
    ROUND(AVG(CASE WHEN trade_correct IS NOT NULL THEN trade_correct END) * 100, 1) as win_rate_pct,
    ROUND(AVG(pnl_percent), 1) as avg_roi_pct,
    ROUND(SUM(pnl_dollars), 2) as total_pnl
FROM paper_trades
WHERE trade_correct IS NOT NULL
GROUP BY side;

-- Recent paper trades
CREATE VIEW IF NOT EXISTS v_recent_paper_trades AS
SELECT 
    id,
    substr(market_name, 1, 50) || '...' as market,
    side,
    ROUND(entry_price * 100, 1) || '%' as entry,
    '$' || ROUND(position_size, 2) as size,
    status,
    CASE 
        WHEN pnl_dollars > 0 THEN '+$' || ROUND(pnl_dollars, 2)
        WHEN pnl_dollars < 0 THEN '-$' || ROUND(ABS(pnl_dollars), 2)
        ELSE '$0.00'
    END as pnl,
    datetime(entry_time, 'unixepoch') as entry_date
FROM paper_trades
ORDER BY entry_time DESC
LIMIT 10;

-- Validation status check
CREATE VIEW IF NOT EXISTS v_go_live_readiness AS
SELECT
    (SELECT COUNT(DISTINCT DATE(entry_time, 'unixepoch')) FROM paper_trades) as days_running,
    (SELECT COUNT(*) FROM paper_trades WHERE trade_correct IS NOT NULL) as resolved_trades,
    (SELECT ROUND(AVG(trade_correct) * 100, 1) FROM paper_trades WHERE trade_correct IS NOT NULL) as win_rate,
    (SELECT ROUND(SUM(pnl_dollars), 2) FROM paper_trades) as total_pnl,
    CASE 
        WHEN (SELECT COUNT(DISTINCT DATE(entry_time, 'unixepoch')) FROM paper_trades) >= 30 THEN 1 
        ELSE 0 
    END as days_requirement_met,
    CASE 
        WHEN (SELECT COUNT(*) FROM paper_trades WHERE trade_correct IS NOT NULL) >= 20 THEN 1 
        ELSE 0 
    END as trades_requirement_met,
    CASE 
        WHEN (SELECT AVG(trade_correct) FROM paper_trades WHERE trade_correct IS NOT NULL) >= 0.55 THEN 1 
        ELSE 0 
    END as winrate_requirement_met,
    CASE 
        WHEN (SELECT SUM(pnl_dollars) FROM paper_trades) > 0 THEN 1 
        ELSE 0 
    END as pnl_requirement_met;

-- Success message
SELECT '✅ Forward paper trading schema created successfully!' as message;
SELECT 'Tables created: paper_trades, paper_position_ticks, market_resolutions, validation_metrics' as tables;
SELECT 'Views created: v_paper_trading_summary, v_paper_trades_by_side, v_recent_paper_trades, v_go_live_readiness' as views;
