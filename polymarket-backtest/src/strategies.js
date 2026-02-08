/**
 * POLYMARKET TRADING STRATEGIES - 6 STRATEGIES
 * 
 * Each strategy returns signals based on real market data
 */

export class TradingStrategies {
  
  /**
   * STRATEGY 1: NO-Side Bias
   * Entry: Price < 0.15 (15%) AND volume spike > 2x average
   * Exit: Price > 0.30 or 7 days
   */
  static noSideBias(marketData, currentIdx) {
    const current = marketData.priceHistory[currentIdx];
    const price = current.price;
    
    // Need at least 24 hours of history for volume calculation
    if (currentIdx < 24) return null;
    
    // Calculate volume spike (using price volatility as proxy)
    const recentVolatility = this.calculateVolatility(marketData.priceHistory, currentIdx, 24);
    const historicalVolatility = this.calculateVolatility(marketData.priceHistory, currentIdx - 24, 24);
    const volumeSpike = historicalVolatility > 0 ? recentVolatility / historicalVolatility : 0;
    
    // Entry signal
    if (price < 0.15 && volumeSpike > 2.0) {
      return {
        signal: 'BUY',
        strategy: 'NO-side-bias',
        entry: price,
        target: 0.30,
        stopLoss: 0.05,
        maxHoldDays: 7
      };
    }
    
    return null;
  }

  /**
   * STRATEGY 2: Contrarian Expert Fade
   * Entry: Consensus > 0.85 (85%) → bet against
   * Exit: Price reverts to 0.60-0.70 or 14 days
   */
  static contrarianExpertFade(marketData, currentIdx) {
    const current = marketData.priceHistory[currentIdx];
    const price = current.price;
    
    // Entry: Strong consensus, bet NO
    if (price > 0.85) {
      return {
        signal: 'SELL',  // Bet NO
        strategy: 'contrarian-expert-fade',
        entry: price,
        target: 0.70,
        stopLoss: 0.95,
        maxHoldDays: 14
      };
    }
    
    // Entry: Strong NO consensus, bet YES
    if (price < 0.15) {
      return {
        signal: 'BUY',  // Bet YES
        strategy: 'contrarian-expert-fade',
        entry: price,
        target: 0.30,
        stopLoss: 0.05,
        maxHoldDays: 14
      };
    }
    
    return null;
  }

  /**
   * STRATEGY 3: Pairs Trading
   * Entry: Divergence between correlated markets
   * This requires cross-market analysis (simplified for single-market backtest)
   */
  static pairsTrading(marketData, currentIdx, relatedMarkets = []) {
    // Simplified: Look for mean reversion opportunities
    const current = marketData.priceHistory[currentIdx];
    
    if (currentIdx < 48) return null;
    
    const sma48 = this.calculateSMA(marketData.priceHistory, currentIdx, 48);
    const deviation = (current.price - sma48) / sma48;
    
    // Entry on significant deviation from mean
    if (deviation > 0.20) {  // Price 20% above mean
      return {
        signal: 'SELL',
        strategy: 'pairs-trading',
        entry: current.price,
        target: sma48,
        stopLoss: current.price * 1.10,
        maxHoldDays: 5
      };
    }
    
    if (deviation < -0.20) {  // Price 20% below mean
      return {
        signal: 'BUY',
        strategy: 'pairs-trading',
        entry: current.price,
        target: sma48,
        stopLoss: current.price * 0.90,
        maxHoldDays: 5
      };
    }
    
    return null;
  }

  /**
   * STRATEGY 4: Trend Filter
   * Entry: Price > price 24h ago (uptrend)
   * Exit: Price < 24h SMA or 3 days
   */
  static trendFilter(marketData, currentIdx) {
    if (currentIdx < 24) return null;
    
    const current = marketData.priceHistory[currentIdx];
    const price24hAgo = marketData.priceHistory[currentIdx - 24];
    
    // Uptrend: current price > 24h ago
    if (current.price > price24hAgo.price * 1.05) {  // 5% threshold
      return {
        signal: 'BUY',
        strategy: 'trend-filter',
        entry: current.price,
        target: current.price * 1.15,
        stopLoss: price24hAgo.price,
        maxHoldDays: 3
      };
    }
    
    // Downtrend: current price < 24h ago
    if (current.price < price24hAgo.price * 0.95) {  // 5% threshold
      return {
        signal: 'SELL',
        strategy: 'trend-filter',
        entry: current.price,
        target: current.price * 0.85,
        stopLoss: price24hAgo.price,
        maxHoldDays: 3
      };
    }
    
    return null;
  }

  /**
   * STRATEGY 5: Time Horizon Filter
   * Entry: Only markets closing < 3 days
   * Exit: Market close or profit target
   */
  static timeHorizonFilter(marketData, currentIdx) {
    const current = marketData.priceHistory[currentIdx];
    const marketEndTime = new Date(marketData.market.endDate).getTime();
    const currentTime = current.timestamp * 1000;
    const daysUntilClose = (marketEndTime - currentTime) / (1000 * 60 * 60 * 24);
    
    // Only trade if < 3 days to close
    if (daysUntilClose > 3 || daysUntilClose < 0) return null;
    
    // Simple momentum play near expiry
    if (currentIdx < 6) return null;
    
    const priceChange6h = current.price - marketData.priceHistory[currentIdx - 6].price;
    
    if (priceChange6h > 0.05) {
      return {
        signal: 'BUY',
        strategy: 'time-horizon-filter',
        entry: current.price,
        target: 0.95,  // Near-certain outcome
        stopLoss: current.price * 0.90,
        maxHoldDays: Math.min(3, daysUntilClose)
      };
    }
    
    if (priceChange6h < -0.05) {
      return {
        signal: 'SELL',
        strategy: 'time-horizon-filter',
        entry: current.price,
        target: 0.05,  // Near-certain NO
        stopLoss: current.price * 1.10,
        maxHoldDays: Math.min(3, daysUntilClose)
      };
    }
    
    return null;
  }

  /**
   * STRATEGY 6: News Mean Reversion
   * Entry: Rapid price change (>10% in 30 min)
   * Exit: Reversion to pre-spike level or 2 hours
   */
  static newsMeanReversion(marketData, currentIdx) {
    // Need at least 30 data points (30 hours for hourly data)
    if (currentIdx < 30) return null;
    
    const current = marketData.priceHistory[currentIdx];
    
    // Look for sharp moves in last 6 hours (proxy for 30-min with hourly data)
    const price6hAgo = marketData.priceHistory[currentIdx - 6];
    const priceChange = current.price - price6hAgo.price;
    const percentChange = Math.abs(priceChange / price6hAgo.price);
    
    // Entry on rapid spike (>15% move in 6h)
    if (percentChange > 0.15) {
      const preSpikeSMA = this.calculateSMA(marketData.priceHistory, currentIdx - 6, 24);
      
      if (priceChange > 0) {
        // Price spiked up, bet on reversion down
        return {
          signal: 'SELL',
          strategy: 'news-mean-reversion',
          entry: current.price,
          target: preSpikeSMA,
          stopLoss: current.price * 1.05,
          maxHoldHours: 24  // Quick trade
        };
      } else {
        // Price spiked down, bet on reversion up
        return {
          signal: 'BUY',
          strategy: 'news-mean-reversion',
          entry: current.price,
          target: preSpikeSMA,
          stopLoss: current.price * 0.95,
          maxHoldHours: 24
        };
      }
    }
    
    return null;
  }

  // Helper functions
  static calculateSMA(priceHistory, endIdx, period) {
    let sum = 0;
    for (let i = endIdx - period + 1; i <= endIdx; i++) {
      if (i >= 0 && i < priceHistory.length) {
        sum += priceHistory[i].price;
      }
    }
    return sum / period;
  }

  static calculateVolatility(priceHistory, endIdx, period) {
    if (endIdx < period) return 0;
    
    const prices = [];
    for (let i = endIdx - period + 1; i <= endIdx; i++) {
      if (i >= 0 && i < priceHistory.length) {
        prices.push(priceHistory[i].price);
      }
    }
    
    const mean = prices.reduce((a, b) => a + b, 0) / prices.length;
    const variance = prices.reduce((sum, price) => sum + Math.pow(price - mean, 2), 0) / prices.length;
    return Math.sqrt(variance);
  }

  static getAllStrategies() {
    return [
      { name: 'NO-side-bias', fn: this.noSideBias },
      { name: 'contrarian-expert-fade', fn: this.contrarianExpertFade },
      { name: 'pairs-trading', fn: this.pairsTrading },
      { name: 'trend-filter', fn: this.trendFilter },
      { name: 'time-horizon-filter', fn: this.timeHorizonFilter },
      { name: 'news-mean-reversion', fn: this.newsMeanReversion }
    ];
  }
}
