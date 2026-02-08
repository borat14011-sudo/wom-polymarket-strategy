"""
Multi-Agent Validation System
6 specialized agents cross-check each trading opportunity
"""
import asyncio
from typing import Dict, List, Any, Optional
from decimal import Decimal
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging

from database import Signal, MarketData
from polymarket_client import PolymarketClient
from config import AGENT_CONFIG, TRADING_CONFIG

logger = logging.getLogger(__name__)

@dataclass
class AgentVote:
    """Individual agent vote"""
    agent_name: str
    approve: bool
    confidence: Decimal
    score: Decimal  # 0-100
    reasoning: str
    metadata: Dict[str, Any]

class BaseAgent(ABC):
    """Base class for all validation agents"""
    
    def __init__(self, name: str, weight: Decimal):
        self.name = name
        self.weight = weight
    
    @abstractmethod
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Analyze signal and return vote"""
        pass

class TechnicalAnalyst(BaseAgent):
    """Agent 1: Technical Analysis"""
    
    def __init__(self):
        super().__init__("TechnicalAnalyst", Decimal("1.0"))
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Analyze technical indicators"""
        try:
            # Get historical price data
            timeseries = await client.get_market_timeseries(signal.market_slug, "1h")
            
            if len(timeseries) < 10:
                return AgentVote(
                    agent_name=self.name,
                    approve=False,
                    confidence=Decimal("0"),
                    score=Decimal("0"),
                    reasoning="Insufficient historical data for technical analysis",
                    metadata={}
                )
            
            prices = [Decimal(str(p.get("probability", 0))) * 100 for p in timeseries]
            
            # Calculate indicators
            rsi = self._calculate_rsi(prices)
            trend = self._calculate_trend(prices)
            volatility = self._calculate_volatility(prices)
            support_resistance = self._find_support_resistance(prices)
            
            # Scoring logic
            score = Decimal("50")  # Neutral base
            
            # RSI analysis
            if signal.suggested_side == "yes":
                if rsi < 30:  # Oversold
                    score += Decimal("20")
                elif rsi > 70:  # Overbought
                    score -= Decimal("20")
            else:  # no
                if rsi > 70:  # Overbought
                    score += Decimal("20")
                elif rsi < 30:  # Oversold
                    score -= Decimal("20")
            
            # Trend analysis
            if trend == "up" and signal.suggested_side == "yes":
                score += Decimal("10")
            elif trend == "down" and signal.suggested_side == "no":
                score += Decimal("10")
            else:
                score -= Decimal("10")
            
            # Volatility check
            if volatility > Decimal("30"):  # High volatility
                score -= Decimal("10")
            
            # Support/Resistance
            current_price = prices[-1]
            if signal.suggested_side == "yes":
                if abs(current_price - support_resistance["support"]) < 5:
                    score += Decimal("15")  # Near support
            else:
                if abs(current_price - support_resistance["resistance"]) < 5:
                    score += Decimal("15")  # Near resistance
            
            score = max(Decimal("0"), min(Decimal("100"), score))
            approve = score >= Decimal("60")
            
            return AgentVote(
                agent_name=self.name,
                approve=approve,
                confidence=score,
                score=score,
                reasoning=f"RSI: {rsi:.1f}, Trend: {trend}, Volatility: {volatility:.1f}%",
                metadata={
                    "rsi": float(rsi),
                    "trend": trend,
                    "volatility": float(volatility),
                    "support": float(support_resistance["support"]),
                    "resistance": float(support_resistance["resistance"])
                }
            )
            
        except Exception as e:
            logger.error(f"Technical analysis failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=False,
                confidence=Decimal("0"),
                score=Decimal("0"),
                reasoning=f"Analysis failed: {str(e)}",
                metadata={}
            )
    
    def _calculate_rsi(self, prices: List[Decimal], period: int = 14) -> Decimal:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return Decimal("50")
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(Decimal("0"))
            else:
                gains.append(Decimal("0"))
                losses.append(abs(change))
        
        if len(gains) < period:
            return Decimal("50")
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return Decimal("100")
        
        rs = avg_gain / avg_loss
        rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
        
        return rsi
    
    def _calculate_trend(self, prices: List[Decimal]) -> str:
        """Determine trend direction"""
        if len(prices) < 20:
            return "neutral"
        
        # Simple moving average comparison
        short_ma = sum(prices[-5:]) / 5
        long_ma = sum(prices[-20:]) / 20
        
        if short_ma > long_ma * Decimal("1.02"):
            return "up"
        elif short_ma < long_ma * Decimal("0.98"):
            return "down"
        return "neutral"
    
    def _calculate_volatility(self, prices: List[Decimal]) -> Decimal:
        """Calculate price volatility"""
        if len(prices) < 2:
            return Decimal("0")
        
        mean = sum(prices) / len(prices)
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std_dev = variance.sqrt()
        
        return (std_dev / mean) * 100 if mean > 0 else Decimal("0")
    
    def _find_support_resistance(self, prices: List[Decimal]) -> Dict[str, Decimal]:
        """Find support and resistance levels"""
        if len(prices) < 10:
            return {"support": prices[-1] * Decimal("0.9"), "resistance": prices[-1] * Decimal("1.1")}
        
        recent_prices = prices[-20:]
        return {
            "support": min(recent_prices),
            "resistance": max(recent_prices)
        }

class SentimentAnalyzer(BaseAgent):
    """Agent 2: Sentiment Analysis"""
    
    def __init__(self):
        super().__init__("SentimentAnalyzer", Decimal("1.0"))
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Analyze market sentiment"""
        try:
            # Get orderbook to analyze bid/ask ratio
            orderbook = await client.get_market_orderbook(signal.market_slug)
            
            if not orderbook:
                return AgentVote(
                    agent_name=self.name,
                    approve=True,  # Neutral if no data
                    confidence=Decimal("50"),
                    score=Decimal("50"),
                    reasoning="No orderbook data available",
                    metadata={}
                )
            
            bids = orderbook.get("bids", [])
            asks = orderbook.get("asks", [])
            
            # Calculate bid/ask volume ratio
            bid_volume = sum(Decimal(str(b.get("size", 0))) for b in bids)
            ask_volume = sum(Decimal(str(a.get("size", 0))) for a in asks)
            
            ratio = bid_volume / ask_volume if ask_volume > 0 else Decimal("1")
            
            # Analyze sentiment based on ratio and signal direction
            score = Decimal("50")
            
            if signal.suggested_side == "yes":
                if ratio > Decimal("1.5"):  # More bids = bullish sentiment
                    score += Decimal("20")
                elif ratio < Decimal("0.67"):  # More asks = bearish
                    score -= Decimal("10")  # Contrarian opportunity
            else:  # no
                if ratio < Decimal("0.67"):  # More asks = bearish sentiment
                    score += Decimal("20")
                elif ratio > Decimal("1.5"):  # More bids = bullish
                    score -= Decimal("10")  # Contrarian opportunity
            
            # Check market description for sentiment clues
            market = await client.get_market(signal.market_slug)
            description = market.get("description", "").lower()
            
            # Simple keyword analysis
            positive_keywords = ["likely", "expected", "projected", "forecast"]
            negative_keywords = ["unlikely", "doubt", "uncertain", "risk"]
            
            pos_count = sum(1 for kw in positive_keywords if kw in description)
            neg_count = sum(1 for kw in negative_keywords if kw in description)
            
            if pos_count > neg_count:
                if signal.suggested_side == "no":  # Fade positive sentiment
                    score += Decimal("10")
                else:
                    score -= Decimal("5")
            elif neg_count > pos_count:
                if signal.suggested_side == "yes":  # Value opportunity
                    score += Decimal("10")
                else:
                    score -= Decimal("5")
            
            score = max(Decimal("0"), min(Decimal("100"), score))
            approve = score >= Decimal("55")
            
            return AgentVote(
                agent_name=self.name,
                approve=approve,
                confidence=score,
                score=score,
                reasoning=f"Bid/Ask ratio: {ratio:.2f}, Sentiment indicators: +{pos_count}/-{neg_count}",
                metadata={
                    "bid_volume": float(bid_volume),
                    "ask_volume": float(ask_volume),
                    "ratio": float(ratio),
                    "positive_clues": pos_count,
                    "negative_clues": neg_count
                }
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=False,
                confidence=Decimal("0"),
                score=Decimal("0"),
                reasoning=f"Analysis failed: {str(e)}",
                metadata={}
            )

class WhaleTracker(BaseAgent):
    """Agent 3: Whale Activity Tracking"""
    
    def __init__(self):
        super().__init__("WhaleTracker", Decimal("1.2"))  # Higher weight
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Analyze whale activity"""
        try:
            whale_data = await client.get_whale_activity(signal.market_slug)
            
            whale_score = whale_data.get("whale_score", Decimal("0"))
            whale_trades = whale_data.get("whale_trades", [])
            
            # Analyze whale direction
            whale_buy_volume = Decimal("0")
            whale_sell_volume = Decimal("0")
            
            for trade in whale_trades:
                size = Decimal(str(trade.get("size", 0)))
                side = trade.get("side", "").lower()
                if side == "buy" or side == "yes":
                    whale_buy_volume += size
                else:
                    whale_sell_volume += size
            
            whale_direction = "neutral"
            if whale_buy_volume > whale_sell_volume * Decimal("1.5"):
                whale_direction = "bullish"
            elif whale_sell_volume > whale_buy_volume * Decimal("1.5"):
                whale_direction = "bearish"
            
            # Scoring
            score = Decimal("50")
            
            # High whale activity is interesting
            if whale_score > Decimal("30"):
                score += Decimal("10")
            
            # Check if signal aligns with whale direction
            if signal.suggested_side == "yes" and whale_direction == "bullish":
                score += Decimal("25")
            elif signal.suggested_side == "no" and whale_direction == "bearish":
                score += Decimal("25")
            elif signal.suggested_side == "yes" and whale_direction == "bearish":
                score -= Decimal("15")  # Whales disagree
            elif signal.suggested_side == "no" and whale_direction == "bullish":
                score -= Decimal("15")  # Whales disagree
            
            score = max(Decimal("0"), min(Decimal("100"), score))
            approve = score >= Decimal("60")
            
            return AgentVote(
                agent_name=self.name,
                approve=approve,
                confidence=score,
                score=score,
                reasoning=f"Whale score: {whale_score:.1f}, Whale direction: {whale_direction}",
                metadata={
                    "whale_score": float(whale_score),
                    "whale_direction": whale_direction,
                    "whale_buy_volume": float(whale_buy_volume),
                    "whale_sell_volume": float(whale_sell_volume),
                    "whale_trade_count": len(whale_trades)
                }
            )
            
        except Exception as e:
            logger.error(f"Whale tracking failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=False,
                confidence=Decimal("0"),
                score=Decimal("0"),
                reasoning=f"Analysis failed: {str(e)}",
                metadata={}
            )

class BotDetector(BaseAgent):
    """Agent 4: Bot Activity Detection"""
    
    def __init__(self):
        super().__init__("BotDetector", Decimal("0.9"))
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Detect and analyze bot activity"""
        try:
            bot_data = await client.get_bot_activity_indicators(signal.market_slug)
            
            bot_score = bot_data.get("bot_score", Decimal("0"))
            indicators = bot_data.get("indicators", {})
            
            # Scoring - high bot activity is concerning
            score = Decimal("70")  # Start optimistic
            
            # Reduce score based on bot indicators
            score -= bot_score * Decimal("0.4")
            
            # Specific concerns
            if indicators.get("rapid_fire_trades", 0) > 50:
                score -= Decimal("10")
            if indicators.get("identical_sizes", 0) > 50:
                score -= Decimal("10")
            
            # Bot activity can create opportunities if we're faster
            if bot_score > Decimal("50") and signal.strategy == "extreme_high_fade":
                # Bots may be artificially inflating - good fade opportunity
                score += Decimal("15")
            
            score = max(Decimal("0"), min(Decimal("100"), score))
            approve = score >= Decimal("60")
            
            return AgentVote(
                agent_name=self.name,
                approve=approve,
                confidence=score,
                score=score,
                reasoning=f"Bot score: {bot_score:.1f}/100, Indicators: {indicators}",
                metadata={
                    "bot_score": float(bot_score),
                    "indicators": indicators,
                    "trades_analyzed": bot_data.get("trades_analyzed", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"Bot detection failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=True,  # Don't block on bot detection failure
                confidence=Decimal("50"),
                score=Decimal("50"),
                reasoning=f"Detection failed: {str(e)}",
                metadata={}
            )

class NewsValidator(BaseAgent):
    """Agent 5: News and Event Validation"""
    
    def __init__(self):
        super().__init__("NewsValidator", Decimal("1.0"))
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Validate against recent news/events"""
        try:
            # Get market details
            market = await client.get_market(signal.market_slug)
            
            # Check market end date
            end_date_str = market.get("endDate")
            if end_date_str:
                from datetime import datetime
                try:
                    end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
                    days_to_resolution = (end_date - datetime.utcnow()).days
                    
                    # Markets close to resolution are riskier for fade strategies
                    score = Decimal("60")
                    
                    if days_to_resolution < 3:
                        if signal.strategy in ["extreme_high_fade", "musk_hype_fade"]:
                            score -= Decimal("25")  # Too risky
                    elif days_to_resolution < 7:
                        score -= Decimal("10")
                    
                    # Check if there's been recent significant volume (news event)
                    volume_24h = Decimal(str(market.get("volume24hr", 0)))
                    total_volume = Decimal(str(market.get("volume", 0)))
                    
                    if total_volume > 0:
                        volume_ratio = volume_24h / (total_volume / 30)  # vs avg daily
                        
                        if volume_ratio > 5:  # Major news event
                            if signal.strategy == "extreme_high_fade":
                                # Could be informed trading - be careful
                                score -= Decimal("15")
                            score += Decimal("10")  # But also more opportunity
                    
                    score = max(Decimal("0"), min(Decimal("100"), score))
                    approve = score >= Decimal("55")
                    
                    return AgentVote(
                        agent_name=self.name,
                        approve=approve,
                        confidence=score,
                        score=score,
                        reasoning=f"Days to resolution: {days_to_resolution}, Volume spike: {volume_ratio:.1f}x" if total_volume > 0 else f"Days to resolution: {days_to_resolution}",
                        metadata={
                            "days_to_resolution": days_to_resolution,
                            "volume_24h": float(volume_24h),
                            "volume_ratio": float(volume_ratio) if total_volume > 0 else 0
                        }
                    )
                    
                except Exception:
                    pass
            
            # If no end date, neutral vote
            return AgentVote(
                agent_name=self.name,
                approve=True,
                confidence=Decimal("50"),
                score=Decimal("50"),
                reasoning="No resolution date available for analysis",
                metadata={}
            )
            
        except Exception as e:
            logger.error(f"News validation failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=True,
                confidence=Decimal("50"),
                score=Decimal("50"),
                reasoning=f"Validation failed: {str(e)}",
                metadata={}
            )

class RiskManager(BaseAgent):
    """Agent 6: Risk Management"""
    
    def __init__(self):
        super().__init__("RiskManager", Decimal("1.5"))  # Highest weight
    
    async def analyze(self, signal: Signal, client: PolymarketClient) -> AgentVote:
        """Perform risk assessment"""
        try:
            score = Decimal("70")  # Start from optimism
            concerns = []
            
            # 1. Check current exposure
            from database import db_manager
            open_trades = db_manager.get_open_trades()
            
            current_exposure = sum(t.size for t in open_trades)
            exposure_pct = (current_exposure / TRADING_CONFIG.INITIAL_BANKROLL) * 100
            
            if exposure_pct > Decimal("50"):
                score -= Decimal("20")
                concerns.append("High portfolio exposure")
            elif exposure_pct > Decimal("30"):
                score -= Decimal("10")
            
            # 2. Check correlation with existing positions
            correlated_exposure = sum(
                t.size for t in open_trades 
                if self._is_correlated(t.market_slug, signal.market_slug)
            )
            
            if correlated_exposure > 0:
                correlated_pct = (correlated_exposure / TRADING_CONFIG.INITIAL_BANKROLL) * 100
                if correlated_pct > TRADING_CONFIG.MAX_CORRELATED_EXPOSURE:
                    score -= Decimal("25")
                    concerns.append("Max correlated exposure reached")
                else:
                    score -= Decimal("10")
                    concerns.append("Correlation with existing positions")
            
            # 3. Position size check
            position_pct = (signal.suggested_size / TRADING_CONFIG.INITIAL_BANKROLL) * 100
            if position_pct > TRADING_CONFIG.MAX_POSITION_SIZE_PCT:
                score -= Decimal("20")
                concerns.append("Position size exceeds limit")
            
            # 4. Signal confidence check
            if signal.confidence < TRADING_CONFIG.MIN_CONFIDENCE_SCORE:
                score -= Decimal("15")
                concerns.append("Low signal confidence")
            
            # 5. Check market liquidity
            market = await client.get_market(signal.market_slug)
            liquidity = Decimal(str(market.get("liquidity", 0)))
            
            if liquidity < TRADING_CONFIG.MIN_LIQUIDITY_USD * 2:
                score -= Decimal("15")
                concerns.append("Low liquidity")
            
            # 6. Strategy-specific risk checks
            if signal.strategy == "musk_hype_fade":
                # Extra caution for Musk markets
                score -= Decimal("5")
            
            score = max(Decimal("0"), min(Decimal("100"), score))
            approve = score >= Decimal("65") and len(concerns) < 3
            
            return AgentVote(
                agent_name=self.name,
                approve=approve,
                confidence=score,
                score=score,
                reasoning=f"Exposure: {exposure_pct:.1f}%, Concerns: {len(concerns)} - {', '.join(concerns[:2])}" if concerns else "Risk acceptable",
                metadata={
                    "portfolio_exposure_pct": float(exposure_pct),
                    "correlated_exposure": float(correlated_exposure),
                    "position_pct": float(position_pct),
                    "liquidity": float(liquidity),
                    "concerns": concerns
                }
            )
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            return AgentVote(
                agent_name=self.name,
                approve=False,
                confidence=Decimal("0"),
                score=Decimal("0"),
                reasoning=f"Risk analysis failed: {str(e)}",
                metadata={}
            )
    
    def _is_correlated(self, market1: str, market2: str) -> bool:
        """Check if two markets are correlated"""
        # Simple keyword-based correlation check
        m1_lower = market1.lower()
        m2_lower = market2.lower()
        
        # Extract common keywords
        keywords = ["musk", "trump", "biden", "election", "btc", "eth", "crypto"]
        
        for kw in keywords:
            if kw in m1_lower and kw in m2_lower:
                return True
        
        return False

class MultiAgentSystem:
    """Orchestrates all validation agents"""
    
    def __init__(self):
        self.agents: List[BaseAgent] = [
            TechnicalAnalyst(),
            SentimentAnalyzer(),
            WhaleTracker(),
            BotDetector(),
            NewsValidator(),
            RiskManager()
        ]
    
    async def validate_signal(self, signal: Signal, client: PolymarketClient) -> Tuple[bool, List[AgentVote], Decimal]:
        """
        Run signal through all agents
        Returns: (approved, votes, weighted_confidence)
        """
        logger.info(f"Validating signal for {signal.market_slug}...")
        
        # Run all agents concurrently
        votes = await asyncio.gather(*[
            agent.analyze(signal, client) 
            for agent in self.agents
        ])
        
        # Calculate weighted consensus
        total_weight = sum(agent.weight for agent in self.agents)
        weighted_score = Decimal("0")
        approval_count = 0
        
        for agent, vote in zip(self.agents, votes):
            weighted_score += vote.score * agent.weight
            if vote.approve:
                approval_count += 1
        
        weighted_confidence = weighted_score / total_weight
        
        # Consensus requirements
        min_approvals = TRADING_CONFIG.MIN_AGENT_CONSENSUS
        min_confidence = TRADING_CONFIG.MIN_CONFIDENCE_SCORE
        
        approved = approval_count >= min_approvals and weighted_confidence >= min_confidence
        
        logger.info(f"Validation result: {approval_count}/6 agents approve, confidence: {weighted_confidence:.1f}%")
        
        return approved, votes, weighted_confidence
    
    def get_agent_scores(self, votes: List[AgentVote]) -> Dict[str, Decimal]:
        """Extract individual agent scores"""
        return {vote.agent_name: vote.score for vote in votes}

# Singleton instance
multi_agent_system = MultiAgentSystem()
