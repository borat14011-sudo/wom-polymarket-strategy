# Multi-Agent Trading System Architecture

## Proposed Agent Deployment (5 Agents)

### Agent 1: Market Monitor
**Purpose:** Real-time price tracking and alerts
**Tasks:**
- Fetch fresh market data every 5 minutes
- Alert on price movements >3%
- Track Tariff market specifically (Feb 27 resolution)
- Report unusual volume spikes
**Spawn Command:** "Monitor Polymarket markets for price movements and opportunities"

### Agent 2: Opportunity Researcher
**Purpose:** Discover and analyze new trades
**Tasks:**
- Scan all 200 markets for mispricings
- Run slippage-aware analysis on new markets
- Generate investment theses like Tariff report
- Update opportunity rankings daily
**Spawn Command:** "Research Polymarket markets for high-EV opportunities with full analysis"

### Agent 3: Data Validator
**Purpose:** Ensure data quality and consistency
**Tasks:**
- Cross-check API vs website prices
- Validate market resolution status
- Check for stale data (>30 min)
- Verify order book depth
**Spawn Command:** "Validate Polymarket data quality and cross-reference sources"

### Agent 4: Risk Manager
**Purpose:** Portfolio tracking and risk oversight
**Tasks:**
- Track all positions and P&L
- Monitor exposure limits (25% max)
- Calculate real-time Kelly sizing
- Alert if circuit breakers triggered
**Spawn Command:** "Monitor trading risk, position sizing, and portfolio exposure"

### Agent 5: Trade Executor
**Purpose:** Prepare and monitor trade execution
**Tasks:**
- Build order specifications
- Calculate optimal entry prices
- Monitor for best execution timing
- Track open orders and fills
**Spawn Command:** "Prepare trade execution plans and monitor order fills"

## Coordination Protocol

Each agent reports to MAIN session with:
- Findings/conclusions
- Data updates
- Alerts requiring action
- End-of-cycle summary

Agents work independently but coordinate through:
1. Shared files (active-markets.json, positions.json)
2. Scheduled updates to main session
3. Urgent alerts via immediate message

## Spawn Priority

**Immediate:**
1. Market Monitor (most critical - need price alerts)
2. Data Validator (ensure data quality)

**Short-term:**
3. Opportunity Researcher (find next Tariff-like bet)

**Ongoing:**
4. Risk Manager (track once we have positions)
5. Trade Executor (when ready to execute)
