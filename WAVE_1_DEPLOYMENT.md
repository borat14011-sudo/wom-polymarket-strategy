# AGENT SWARM - Wave 1 Deployment

## Wave 1A: Data Gatherers (Parallel Spawn)

### Agent: data_harvester_1
**Role:** Multi-exchange data collector  
**Task:** 
- Connect to Binance, Bybit, OKX APIs
- Collect 1-hour OHLCV data for top 50 pairs
- Build data_snapshot_1.json
**Output:** data_snapshot_1.json  
**TTL:** 15 minutes  
**Priority:** CRITICAL

### Agent: orderbook_scanner_1
**Role:** Order book analyzer  
**Task:**
- Scan BTC, ETH order books across 5 exchanges
- Calculate spread, depth, slippage metrics
- Identify liquidity imbalances
**Output:** orderbook_analysis.json  
**TTL:** 10 minutes  
**Priority:** HIGH

### Agent: funding_rate_tracker_1
**Role:** Derivatives data collector  
**Task:**
- Track funding rates across perpetual markets
- Identify funding arbitrage opportunities
- Build resolved_analysis.json with rate differentials
**Output:** resolved_analysis.json  
**TTL:** 10 minutes  
**Priority:** HIGH

---

## Wave 1B: Strategy Architects (Spawn after data ready)

### Agent: strategy_architect_1
**Role:** Momentum strategy designer  
**Focus:** Breakout/momentum systems  
**Input:** data_snapshot_1.json  
**Output:** strategy_architect_1.md

### Agent: strategy_architect_2
**Role:** Mean reversion designer  
**Focus:** Statistical arbitrage, pairs trading  
**Input:** data_snapshot_1.json, orderbook_analysis.json  
**Output:** strategy_architect_2.md

### Agent: strategy_architect_3
**Role:** Market maker / Liquidity strategy  
**Focus:** Order book imbalance, flow toxicity  
**Input:** orderbook_analysis.json, resolved_analysis.json  
**Output:** strategy_architect_3.md

---

## Wave 1C: Master Integrator (Spawn after architects complete)

### Agent: master_strategist_1
**Role:** Strategy integrator & optimizer  
**Task:**
- Read all strategy_architect_*.md files
- Score and rank strategies by edge, robustness, feasibility
- Build MASTER_STRATEGY_REPORT.md
**Input:** All strategy and data files  
**Output:** MASTER_STRATEGY_REPORT.md

---

## Spawn Commands

```bash
# Wave 1A - Data Gatherers
openclaw agent spawn --name data_harvester_1 --task "Collect OHLCV data from Binance, Bybit, OKX for top 50 pairs. Build data_snapshot_1.json with 1h candles." --output data_snapshot_1.json

openclaw agent spawn --name orderbook_scanner_1 --task "Analyze order books for BTC, ETH across 5 exchanges. Calculate spreads, depth, slippage. Output orderbook_analysis.json" --output orderbook_analysis.json

openclaw agent spawn --name funding_rate_tracker_1 --task "Track funding rates across perpetual markets. Identify arbitrage opportunities. Build resolved_analysis.json" --output resolved_analysis.json
```

---

**Wave 1 Deployment Time:** 2026-02-08 12:53 PST  
**Expected Completion:** 2026-02-08 13:10 PST
