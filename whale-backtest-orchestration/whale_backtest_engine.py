"""
Whale Copy Trading Backtest Engine
===================================
Shared backtest infrastructure for all sub-agents.

Methodology:
- "Whale activity" = large price movements (proxy, since wallet data unavailable)
- Simulates detecting whale trade and copying with slippage
- Calculates true P&L accounting for full position risk
"""

import json
import random
from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path
import math

@dataclass
class Market:
    """Represents a resolved Polymarket market"""
    market_id: str
    question: str
    winner: str  # "Yes" or "No"
    volume_usd: float
    event_end_date: str
    category: str = "unknown"
    
@dataclass
class WhaleSignal:
    """A detected whale signal (proxy: large price movement)"""
    market_id: str
    signal_type: str  # "LARGE_BUY", "LARGE_SELL", "VOLUME_SPIKE"
    direction: str    # "YES" or "NO"
    strength: float   # 0-1, how strong the signal is
    detected_price: float  # Price when signal detected
    
@dataclass
class Trade:
    """A copy trade we executed"""
    market_id: str
    question: str
    entry_price: float
    position_side: str  # "YES" or "NO"
    position_size: float  # USD amount
    outcome: str  # "WIN" or "LOSS"
    pnl: float  # Actual profit/loss in USD
    pnl_pct: float  # Percentage return
    slippage_cost: float
    whale_strength: float
    category: str

class WhaleBacktestEngine:
    """
    Core backtest engine for whale copy trading simulation.
    
    Usage:
        engine = WhaleBacktestEngine(initial_capital=10000)
        engine.load_markets("polymarket_resolved_markets.json")
        engine.run_backtest(strategy_params)
        results = engine.get_results()
    """
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.markets: List[Market] = []
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        
    def load_markets(self, filepath: str) -> int:
        """Load resolved markets from JSON file"""
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        
        for m in data:
            try:
                volume = float(m.get('volume_usd', 0) or 0)
                winner = m.get('winner', '')
                if winner in ['Yes', 'No'] and volume > 0:
                    # Categorize by question content
                    question = m.get('question', '').lower()
                    category = self._categorize_market(question)
                    
                    self.markets.append(Market(
                        market_id=str(m.get('market_id', '')),
                        question=m.get('question', ''),
                        winner=winner,
                        volume_usd=volume,
                        event_end_date=m.get('event_end_date', ''),
                        category=category
                    ))
            except (ValueError, TypeError):
                continue
                
        return len(self.markets)
    
    def _categorize_market(self, question: str) -> str:
        """Categorize market by question content"""
        question = question.lower()
        
        if any(w in question for w in ['trump', 'biden', 'election', 'president', 'senate', 'governor', 'democrat', 'republican', 'vote']):
            return 'politics'
        elif any(w in question for w in ['bitcoin', 'eth', 'crypto', 'btc', 'solana', 'price']):
            return 'crypto'
        elif any(w in question for w in ['nba', 'nfl', 'tennis', 'soccer', 'game', 'match', 'vs', 'winner', 'score']):
            return 'sports'
        elif any(w in question for w in ['fed', 'interest rate', 'inflation', 'gdp', 'unemployment']):
            return 'economics'
        elif any(w in question for w in ['tweet', 'elon', 'musk', 'celebrity']):
            return 'entertainment'
        else:
            return 'other'
    
    def generate_whale_signal(self, market: Market, params: dict) -> Optional[WhaleSignal]:
        """
        Simulate detecting a whale signal.
        Since we don't have real whale data, we proxy via:
        - High volume markets (whales active)
        - Random signal generation based on outcome (simulating info edge)
        """
        min_volume = params.get('min_volume', 10000)
        whale_accuracy = params.get('whale_accuracy', 0.60)  # Base whale win rate
        
        if market.volume_usd < min_volume:
            return None
            
        # Simulate whale having information edge
        # Higher volume markets = more whale interest = potentially better signals
        volume_factor = min(1.0, math.log10(market.volume_usd) / 6)  # Scales up to $1M
        
        # Whale signal accuracy (do they pick the winner?)
        if random.random() < whale_accuracy * (0.8 + 0.2 * volume_factor):
            # Whale is correct - signal matches outcome
            direction = market.winner
            signal_type = "LARGE_BUY" if direction == "YES" else "LARGE_SELL"
        else:
            # Whale is wrong - signal opposite of outcome
            direction = "NO" if market.winner == "YES" else "YES"
            signal_type = "LARGE_BUY" if direction == "YES" else "LARGE_SELL"
        
        # Signal strength based on volume (louder signal = bigger whale)
        strength = min(1.0, volume_factor + random.uniform(-0.1, 0.1))
        
        # Simulated entry price (what we'd pay to copy)
        # If direction matches winner, we're buying something that goes to 1.0
        # If direction opposes winner, we're buying something that goes to 0.0
        base_price = random.uniform(0.30, 0.70)
        
        return WhaleSignal(
            market_id=market.market_id,
            signal_type=signal_type,
            direction=direction,
            strength=strength,
            detected_price=base_price
        )
    
    def execute_copy_trade(self, market: Market, signal: WhaleSignal, 
                          params: dict) -> Optional[Trade]:
        """Execute a copy trade based on whale signal"""
        
        # Position sizing
        sizing_method = params.get('sizing_method', 'fixed')
        base_size = params.get('base_position_size', 100)
        max_position_pct = params.get('max_position_pct', 0.10)
        
        if sizing_method == 'fixed':
            position_size = base_size
        elif sizing_method == 'signal_scaled':
            position_size = base_size * (0.5 + signal.strength)
        elif sizing_method == 'kelly':
            # Simplified Kelly: f = (bp - q) / b where b=odds, p=win prob, q=1-p
            est_win_rate = params.get('whale_accuracy', 0.60)
            avg_odds = 1.0  # Simplified
            kelly_fraction = max(0, (avg_odds * est_win_rate - (1 - est_win_rate)) / avg_odds)
            position_size = self.capital * kelly_fraction * 0.5  # Half Kelly for safety
            position_size = min(position_size, base_size * 3)  # Cap at 3x base
        elif sizing_method == 'volatility_scaled':
            # Less on high-volume (whale-crowded), more on medium
            vol_factor = 1.0 - 0.5 * min(1.0, market.volume_usd / 500000)
            position_size = base_size * (0.5 + vol_factor)
        else:
            position_size = base_size
        
        # Apply maximum position constraint
        position_size = min(position_size, self.capital * max_position_pct)
        
        # Slippage simulation
        slippage_pct = params.get('slippage_pct', 0.02)  # 2% default
        slippage_cost = position_size * slippage_pct
        
        # Determine outcome
        is_winner = (signal.direction == market.winner)
        
        if is_winner:
            # We bought correct side, it goes to 1.0
            # Profit = (1.0 - entry_price) * size - slippage
            gross_profit = (1.0 - signal.detected_price) * position_size
            pnl = gross_profit - slippage_cost
            outcome = "WIN"
        else:
            # We bought wrong side, it goes to 0.0
            # Loss = entry_price * size + slippage
            pnl = -signal.detected_price * position_size - slippage_cost
            outcome = "LOSS"
        
        pnl_pct = pnl / position_size if position_size > 0 else 0
        
        # Update capital
        self.capital += pnl
        self.equity_curve.append(self.capital)
        
        return Trade(
            market_id=market.market_id,
            question=market.question,
            entry_price=signal.detected_price,
            position_side=signal.direction,
            position_size=position_size,
            outcome=outcome,
            pnl=pnl,
            pnl_pct=pnl_pct,
            slippage_cost=slippage_cost,
            whale_strength=signal.strength,
            category=market.category
        )
    
    def run_backtest(self, params: dict = None) -> Dict:
        """
        Run full backtest with given parameters.
        
        params:
            - whale_accuracy: Base probability whale signal is correct (0.5-0.8)
            - min_volume: Minimum market volume to trade
            - slippage_pct: Slippage as % of position
            - sizing_method: 'fixed', 'signal_scaled', 'kelly', 'volatility_scaled'
            - base_position_size: Base $ per trade
            - max_position_pct: Max % of capital per trade
            - category_filter: List of categories to trade, or None for all
            - signal_threshold: Minimum signal strength to trade (0-1)
        """
        if params is None:
            params = {}
        
        # Reset state
        self.capital = self.initial_capital
        self.trades = []
        self.equity_curve = [self.initial_capital]
        
        # Default params
        params.setdefault('whale_accuracy', 0.58)
        params.setdefault('min_volume', 10000)
        params.setdefault('slippage_pct', 0.02)
        params.setdefault('sizing_method', 'fixed')
        params.setdefault('base_position_size', 100)
        params.setdefault('max_position_pct', 0.10)
        params.setdefault('category_filter', None)
        params.setdefault('signal_threshold', 0.3)
        
        # Set random seed for reproducibility (can be varied)
        random.seed(params.get('random_seed', 42))
        
        tradeable_markets = self.markets.copy()
        random.shuffle(tradeable_markets)  # Simulate random discovery order
        
        for market in tradeable_markets:
            # Check capital
            if self.capital <= 0:
                break
                
            # Category filter
            if params['category_filter'] and market.category not in params['category_filter']:
                continue
            
            # Generate whale signal
            signal = self.generate_whale_signal(market, params)
            if signal is None:
                continue
                
            # Signal strength filter
            if signal.strength < params['signal_threshold']:
                continue
            
            # Execute trade
            trade = self.execute_copy_trade(market, signal, params)
            if trade:
                self.trades.append(trade)
        
        return self.get_results()
    
    def get_results(self) -> Dict:
        """Calculate comprehensive backtest results"""
        if not self.trades:
            return {'error': 'No trades executed'}
        
        wins = [t for t in self.trades if t.outcome == "WIN"]
        losses = [t for t in self.trades if t.outcome == "LOSS"]
        
        total_pnl = sum(t.pnl for t in self.trades)
        total_return = (self.capital - self.initial_capital) / self.initial_capital
        
        # Returns for Sharpe calculation
        returns = [t.pnl_pct for t in self.trades]
        avg_return = sum(returns) / len(returns) if returns else 0
        
        # Standard deviation of returns
        if len(returns) > 1:
            variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
            std_return = math.sqrt(variance)
        else:
            std_return = 0
        
        # Sharpe Ratio (assume risk-free = 0)
        sharpe = avg_return / std_return if std_return > 0 else 0
        
        # Sortino (downside deviation)
        negative_returns = [r for r in returns if r < 0]
        if len(negative_returns) > 1:
            downside_var = sum(r ** 2 for r in negative_returns) / len(negative_returns)
            downside_std = math.sqrt(downside_var)
            sortino = avg_return / downside_std if downside_std > 0 else 0
        else:
            sortino = 0
        
        # Max Drawdown
        peak = self.equity_curve[0]
        max_dd = 0
        for equity in self.equity_curve:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
        
        # Category breakdown
        category_stats = {}
        for cat in set(t.category for t in self.trades):
            cat_trades = [t for t in self.trades if t.category == cat]
            cat_wins = len([t for t in cat_trades if t.outcome == "WIN"])
            cat_pnl = sum(t.pnl for t in cat_trades)
            category_stats[cat] = {
                'trades': len(cat_trades),
                'wins': cat_wins,
                'win_rate': cat_wins / len(cat_trades) if cat_trades else 0,
                'total_pnl': cat_pnl,
                'avg_pnl': cat_pnl / len(cat_trades) if cat_trades else 0
            }
        
        # Slippage impact
        total_slippage = sum(t.slippage_cost for t in self.trades)
        
        return {
            'total_trades': len(self.trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': len(wins) / len(self.trades),
            'total_pnl': total_pnl,
            'total_return_pct': total_return * 100,
            'avg_return_pct': avg_return * 100,
            'std_return_pct': std_return * 100,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_pct': max_dd * 100,
            'final_capital': self.capital,
            'total_slippage': total_slippage,
            'slippage_pct_of_pnl': abs(total_slippage / total_pnl) * 100 if total_pnl != 0 else 0,
            'category_breakdown': category_stats,
            'avg_win': sum(t.pnl for t in wins) / len(wins) if wins else 0,
            'avg_loss': sum(t.pnl for t in losses) / len(losses) if losses else 0,
            'profit_factor': abs(sum(t.pnl for t in wins)) / abs(sum(t.pnl for t in losses)) if losses else float('inf'),
            'trades': [
                {
                    'market_id': t.market_id,
                    'question': t.question[:50] + '...' if len(t.question) > 50 else t.question,
                    'outcome': t.outcome,
                    'pnl': round(t.pnl, 2),
                    'pnl_pct': round(t.pnl_pct * 100, 2),
                    'category': t.category
                }
                for t in self.trades[:50]  # First 50 trades as sample
            ]
        }


def run_parameter_sweep(engine: WhaleBacktestEngine, 
                        param_ranges: dict,
                        n_iterations: int = 100) -> List[Dict]:
    """
    Run parameter sweep to find optimal configuration.
    
    param_ranges example:
    {
        'whale_accuracy': [0.55, 0.60, 0.65, 0.70],
        'slippage_pct': [0.01, 0.02, 0.03],
        'sizing_method': ['fixed', 'kelly', 'signal_scaled']
    }
    """
    results = []
    
    for i in range(n_iterations):
        params = {}
        for key, values in param_ranges.items():
            if isinstance(values, list):
                params[key] = random.choice(values)
            elif isinstance(values, tuple) and len(values) == 2:
                params[key] = random.uniform(values[0], values[1])
        
        params['random_seed'] = i  # Different seed each iteration
        
        result = engine.run_backtest(params)
        result['params'] = params.copy()
        results.append(result)
    
    return sorted(results, key=lambda x: x.get('sharpe_ratio', -999), reverse=True)


if __name__ == "__main__":
    # Quick test
    engine = WhaleBacktestEngine(initial_capital=10000)
    
    # Try to load markets
    market_file = Path("../polymarket_resolved_markets.json")
    if market_file.exists():
        n_markets = engine.load_markets(str(market_file))
        print(f"Loaded {n_markets} markets")
        
        # Run baseline backtest
        results = engine.run_backtest({
            'whale_accuracy': 0.58,
            'slippage_pct': 0.02,
            'sizing_method': 'fixed',
            'base_position_size': 100
        })
        
        print(f"\n=== BACKTEST RESULTS ===")
        print(f"Total Trades: {results['total_trades']}")
        print(f"Win Rate: {results['win_rate']:.1%}")
        print(f"Total Return: {results['total_return_pct']:.1f}%")
        print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {results['max_drawdown_pct']:.1f}%")
    else:
        print("Market file not found. Run from workspace root.")
