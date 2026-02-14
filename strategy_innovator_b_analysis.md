# Strategy Innovator B - Behavioral Focus Analysis

## Core Challenge
Develop novel Polymarket trading strategies with $10 capital, 4% round-trip fees (2% entry + 2% exit).

## Key Behavioral Phenomena in Prediction Markets

### 1. Attention Dynamics
- **News-driven overreaction**: Markets overshoot on breaking news, then mean-revert
- **Attention decay**: After initial spike, attention fades faster than information justifies
- **Celebrity endorsement**: Irrational price moves from celebrity tweets/endorsements

### 2. Cognitive Biases
- **Availability heuristic**: Recent dramatic events overweighted in probability estimates
- **Anchoring**: Prices cluster around round numbers (0.25, 0.50, 0.75)
- **Overconfidence**: Markets underprice uncertainty around complex events

### 3. Event Timeline Patterns
- **Pre-event hype**: Excitement builds, prices inflate beyond rational expectations
- **Post-event certainty collapse**: After resolution, uncertainty premium disappears rapidly
- **Deadline compression**: Last-minute trading amplifies volatility

### 4. Social Dynamics
- **Herding**: Traders follow others without independent analysis
- **Contrarian opportunities**: When consensus becomes extreme
- **Groupthink reversal**: Markets slow to update when consensus is wrong

### 5. Information Flow
- **Asymmetric detection**: Early signs of insider knowledge
- **Information cascades**: Small signals trigger disproportionate reactions

## Strategy Design Constraints
- Edge must exceed 4% + slippage (0.5-3%)
- Position sizing: max 2% per trade ($0.20), 25% total exposure ($2.50)
- Must be automatable
- Use available data: 93,949 historical markets, 2,600+ resolved outcomes

## Behavioral Edge Hypotheses

### H1: Attention Arbitrage
**Core insight**: Attention decays exponentially, but market prices adjust linearly. The gap creates mean-reversion opportunities.

### H2: Anchoring Exploitation  
**Core insight**: Prices cluster at psychological anchors, creating temporary inefficiencies when new information arrives.

### H3: Overconfidence Premium
**Core insight**: Complex events have higher uncertainty than markets price, creating option-like value in contrarian positions.

## Initial Strategy Sketches

1. **Attention Decay Mean-Reversion**
   - Identify markets with recent attention spikes (>24h old)
   - Bet against extreme moves that exceeded information value
   - Exit as attention normalizes (3-7 days)

2. **Anchoring Breakout Fade**
   - Detect prices stuck at round numbers (0.50, 0.75)
   - When they break due to minor news, fade the move
   - Target return to anchor zone

3. **Complex Event Uncertainty Arbitrage**
   - Find multi-outcome markets with complex resolution criteria
   - Identify where market underestimates tail risks
   - Take positions that benefit from resolution uncertainty

Need to refine into 3 fully developed strategies.