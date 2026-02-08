#!/usr/bin/env python3
"""
Correlation Analysis: Twitter Hype → Prediction Market Movements

Implements rigorous statistical testing to determine if social media hype
predicts market price movements, following the methodology in 
CORRELATION-ANALYSIS-FRAMEWORK.md

Requirements:
    pip install pandas numpy scipy statsmodels matplotlib seaborn

Usage:
    python correlation-analyzer.py --db polymarket_data.db --output report.json
    python correlation-analyzer.py --db polymarket_data.db --market-id 12345
    python correlation-analyzer.py --db polymarket_data.db --min-samples 50 --max-lag 24

Author: OpenClaw Agent
Date: 2026-02-06
"""

import argparse
import json
import sqlite3
import warnings
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.tsa.stattools import adfuller, grangercausalitytests

# Optional: matplotlib for visualizations
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    warnings.warn("matplotlib not available - visualizations disabled")

# Suppress statsmodels warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', category=FutureWarning)


# ============================================================================
# Data Models
# ============================================================================

@dataclass
class CorrelationResult:
    """Results from correlation analysis at a specific lag"""
    lag_hours: int
    correlation: float
    p_value: float
    sample_size: int


@dataclass
class GrangerResult:
    """Results from Granger causality test"""
    direction: str  # 'hype->price' or 'price->hype'
    best_lag: int
    p_value: float
    f_statistic: float
    is_significant: bool


@dataclass
class MarketAnalysis:
    """Complete analysis results for a single market"""
    market_id: str
    market_name: str
    data_points: int
    analysis_period_days: float
    
    # Time series properties
    price_stationary: bool
    hype_stationary: bool
    
    # Correlation results
    optimal_lag_hours: int
    max_correlation: float
    max_correlation_pvalue: float
    correlations_by_lag: List[CorrelationResult]
    
    # Granger causality
    granger_hype_to_price: GrangerResult
    granger_price_to_hype: GrangerResult
    
    # Warnings and flags
    warnings: List[str]
    reverse_causality_detected: bool
    common_cause_suspected: bool
    
    # Signal strength tier
    signal_tier: str  # 'STRONG', 'MODERATE', 'WEAK', 'NONE'
    tradeable: bool
    
    # Additional metrics
    mean_hype: float
    std_hype: float
    mean_price_change: float
    std_price_change: float


@dataclass
class AnalysisReport:
    """Complete analysis report for all markets"""
    timestamp: str
    database: str
    total_markets_analyzed: int
    markets_with_sufficient_data: int
    
    # Summary statistics
    strong_signals: int
    moderate_signals: int
    weak_signals: int
    no_signals: int
    
    # Market-level results
    market_results: List[MarketAnalysis]
    
    # Best opportunities
    top_markets: List[Dict]  # Sorted by signal strength
    
    # Configuration
    config: Dict


# ============================================================================
# Database Interface
# ============================================================================

class DataLoader:
    """Load and prepare data from SQLite database"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def get_markets(self, market_id: Optional[str] = None) -> pd.DataFrame:
        """Get list of markets to analyze"""
        query = "SELECT DISTINCT market_id, title, category FROM markets"
        if market_id:
            query += f" WHERE market_id = '{market_id}'"
        
        return pd.read_sql_query(query, self.conn)
    
    def get_market_data(self, market_id: str, min_date: Optional[str] = None) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Get price snapshots and hype signals for a market
        
        Returns:
            (price_df, hype_df) both indexed by timestamp
        """
        # Price data
        price_query = """
            SELECT timestamp, yes_price, no_price, volume, liquidity
            FROM snapshots
            WHERE market_id = ?
            ORDER BY timestamp
        """
        price_df = pd.read_sql_query(price_query, self.conn, params=(market_id,))
        price_df['timestamp'] = pd.to_datetime(price_df['timestamp'])
        price_df.set_index('timestamp', inplace=True)
        
        # Hype signals
        hype_query = """
            SELECT hour_timestamp, tweet_count, total_engagement, 
                   unique_authors, avg_sentiment, high_follower_count
            FROM hype_signals
            WHERE market_id = ?
            ORDER BY hour_timestamp
        """
        hype_df = pd.read_sql_query(hype_query, self.conn, params=(market_id,))
        hype_df['hour_timestamp'] = pd.to_datetime(hype_df['hour_timestamp'])
        hype_df.set_index('hour_timestamp', inplace=True)
        
        # Apply date filter if provided
        if min_date:
            min_dt = pd.to_datetime(min_date)
            price_df = price_df[price_df.index >= min_dt]
            hype_df = hype_df[hype_df.index >= min_dt]
        
        return price_df, hype_df
    
    def close(self):
        """Close database connection"""
        self.conn.close()


# ============================================================================
# Data Preprocessing
# ============================================================================

class TimeSeriesPreprocessor:
    """Prepare time series data for analysis"""
    
    @staticmethod
    def resample_to_hourly(price_df: pd.DataFrame, hype_df: pd.DataFrame) -> pd.DataFrame:
        """
        Align price data (15-min) and hype data (hourly) to common hourly timeline
        
        Returns:
            DataFrame with columns: price, price_change, hype_score, tweet_count, etc.
        """
        # Resample price to hourly (use mean for 15-min intervals)
        price_hourly = price_df[['yes_price']].resample('1H').mean()
        price_hourly['price_change'] = price_hourly['yes_price'].diff()
        
        # Merge with hype data
        merged = price_hourly.join(hype_df, how='inner')
        
        # Create composite hype score (weighted combination of metrics)
        # Formula: log(tweet_count + 1) + 0.5 * log(engagement + 1) + 0.3 * unique_authors
        merged['hype_score'] = (
            np.log1p(merged['tweet_count']) + 
            0.5 * np.log1p(merged['total_engagement']) + 
            0.3 * merged['unique_authors']
        )
        
        # Drop rows with missing values
        merged = merged.dropna()
        
        return merged
    
    @staticmethod
    def test_stationarity(series: pd.Series, name: str = "Series") -> Tuple[bool, float]:
        """
        Test if time series is stationary using Augmented Dickey-Fuller test
        
        Returns:
            (is_stationary, p_value)
        """
        if len(series) < 10:
            return False, 1.0
        
        try:
            result = adfuller(series.dropna(), autolag='AIC')
            p_value = result[1]
            is_stationary = p_value < 0.05
            return is_stationary, p_value
        except Exception as e:
            warnings.warn(f"Stationarity test failed for {name}: {e}")
            return False, 1.0
    
    @staticmethod
    def make_stationary(series: pd.Series) -> pd.Series:
        """Convert non-stationary series to stationary (first difference)"""
        return series.diff().dropna()
    
    @staticmethod
    def normalize_series(series: pd.Series) -> pd.Series:
        """Normalize to z-scores (mean=0, std=1)"""
        return (series - series.mean()) / series.std()


# ============================================================================
# Statistical Analysis
# ============================================================================

class CorrelationAnalyzer:
    """Perform correlation and causality analysis"""
    
    def __init__(self, max_lag: int = 48, significance_level: float = 0.05):
        self.max_lag = max_lag
        self.significance_level = significance_level
    
    def cross_correlation(self, hype: pd.Series, price: pd.Series) -> List[CorrelationResult]:
        """
        Calculate cross-correlation at different lags
        
        Positive lag: hype(t) vs price(t+lag) - hype leads price
        Negative lag: hype(t) vs price(t-lag) - price leads hype
        """
        results = []
        
        for lag in range(-self.max_lag, self.max_lag + 1):
            if lag == 0:
                # Contemporaneous correlation
                shifted_price = price
                shifted_hype = hype
            elif lag > 0:
                # Hype leads price
                shifted_price = price.shift(-lag)
                shifted_hype = hype
            else:
                # Price leads hype (reverse causality check)
                shifted_price = price
                shifted_hype = hype.shift(lag)
            
            # Align series and drop NaN
            aligned = pd.DataFrame({'hype': shifted_hype, 'price': shifted_price}).dropna()
            
            if len(aligned) < 10:
                continue
            
            # Calculate correlation
            corr, p_val = stats.pearsonr(aligned['hype'], aligned['price'])
            
            results.append(CorrelationResult(
                lag_hours=lag,
                correlation=corr,
                p_value=p_val,
                sample_size=len(aligned)
            ))
        
        return results
    
    def find_optimal_lag(self, correlations: List[CorrelationResult]) -> Tuple[int, float, float]:
        """
        Find lag with maximum positive correlation (hype leading price)
        
        Returns:
            (optimal_lag, max_correlation, p_value)
        """
        # Only consider positive lags (hype leads price)
        positive_lags = [c for c in correlations if c.lag_hours > 0]
        
        if not positive_lags:
            return 0, 0.0, 1.0
        
        # Find max correlation
        best = max(positive_lags, key=lambda x: abs(x.correlation))
        return best.lag_hours, best.correlation, best.p_value
    
    def granger_causality_test(
        self, 
        cause: pd.Series, 
        effect: pd.Series, 
        max_lag: int = 24
    ) -> GrangerResult:
        """
        Test if 'cause' Granger-causes 'effect'
        
        Returns best lag and significance
        """
        # Prepare data
        data = pd.DataFrame({'effect': effect, 'cause': cause}).dropna()
        
        if len(data) < 30:
            return GrangerResult(
                direction=f"{cause.name}->{effect.name}",
                best_lag=0,
                p_value=1.0,
                f_statistic=0.0,
                is_significant=False
            )
        
        # Limit max_lag based on data availability
        actual_max_lag = min(max_lag, len(data) // 3)
        
        if actual_max_lag < 1:
            return GrangerResult(
                direction=f"{cause.name}->{effect.name}",
                best_lag=0,
                p_value=1.0,
                f_statistic=0.0,
                is_significant=False
            )
        
        try:
            # Run Granger causality test
            test_result = grangercausalitytests(
                data[['effect', 'cause']], 
                maxlag=actual_max_lag,
                verbose=False
            )
            
            # Extract best lag (minimum p-value)
            best_lag = 1
            best_p = 1.0
            best_f = 0.0
            
            for lag in range(1, actual_max_lag + 1):
                ssr_f_test = test_result[lag][0]['ssr_ftest']
                p_val = ssr_f_test[1]
                f_stat = ssr_f_test[0]
                
                if p_val < best_p:
                    best_lag = lag
                    best_p = p_val
                    best_f = f_stat
            
            return GrangerResult(
                direction=f"{cause.name}->{effect.name}",
                best_lag=best_lag,
                p_value=best_p,
                f_statistic=best_f,
                is_significant=(best_p < self.significance_level)
            )
        
        except Exception as e:
            warnings.warn(f"Granger causality test failed: {e}")
            return GrangerResult(
                direction=f"{cause.name}->{effect.name}",
                best_lag=0,
                p_value=1.0,
                f_statistic=0.0,
                is_significant=False
            )
    
    def check_reverse_causality(
        self,
        hype: pd.Series,
        price: pd.Series
    ) -> Tuple[bool, str]:
        """
        Check for reverse causality (price -> hype instead of hype -> price)
        
        Returns:
            (reverse_detected, warning_message)
        """
        # Test both directions
        hype_to_price = self.granger_causality_test(hype, price)
        price_to_hype = self.granger_causality_test(price, hype)
        
        # Reverse causality if price->hype is significant but hype->price is not
        if price_to_hype.is_significant and not hype_to_price.is_significant:
            return True, "DANGER: Price appears to drive hype (reverse causality)"
        
        # Warning if both are significant (bidirectional feedback)
        if price_to_hype.is_significant and hype_to_price.is_significant:
            return False, "INFO: Bidirectional relationship detected (feedback loop)"
        
        return False, ""
    
    def check_common_cause(self, correlations: List[CorrelationResult]) -> Tuple[bool, str]:
        """
        Check if contemporaneous correlation is strongest (suggests common cause)
        
        Returns:
            (common_cause_suspected, warning_message)
        """
        # Find lag-0 correlation
        lag_0 = next((c for c in correlations if c.lag_hours == 0), None)
        if not lag_0:
            return False, ""
        
        # Find max correlation at non-zero lags
        non_zero = [c for c in correlations if c.lag_hours != 0]
        if not non_zero:
            return False, ""
        
        max_other = max(non_zero, key=lambda x: abs(x.correlation))
        
        # If lag-0 correlation is much stronger, suspect common cause
        if abs(lag_0.correlation) > abs(max_other.correlation) * 1.5:
            return True, "WARNING: Contemporaneous correlation strongest (common cause suspected)"
        
        return False, ""


# ============================================================================
# Signal Classification
# ============================================================================

class SignalClassifier:
    """Classify signal strength and tradeability"""
    
    TIER_CRITERIA = {
        'STRONG': {
            'min_correlation': 0.5,
            'max_granger_p': 0.001,
            'min_lag': 1,
            'no_reverse_causality': True
        },
        'MODERATE': {
            'min_correlation': 0.3,
            'max_granger_p': 0.01,
            'min_lag': 1,
            'no_reverse_causality': True
        },
        'WEAK': {
            'min_correlation': 0.2,
            'max_granger_p': 0.05,
            'min_lag': 0,
            'no_reverse_causality': False
        }
    }
    
    @staticmethod
    def classify_signal(
        max_correlation: float,
        granger_p_value: float,
        optimal_lag: int,
        reverse_causality: bool,
        common_cause: bool,
        sample_size: int
    ) -> Tuple[str, bool]:
        """
        Classify signal strength and determine if tradeable
        
        Returns:
            (tier, tradeable)
        """
        # Insufficient data
        if sample_size < 30:
            return 'NONE', False
        
        # Check STRONG criteria
        if (abs(max_correlation) >= 0.5 and 
            granger_p_value < 0.001 and 
            optimal_lag > 0 and 
            not reverse_causality and
            not common_cause):
            return 'STRONG', True
        
        # Check MODERATE criteria
        if (abs(max_correlation) >= 0.3 and 
            granger_p_value < 0.01 and 
            optimal_lag > 0 and 
            not reverse_causality):
            return 'MODERATE', True
        
        # Check WEAK criteria
        if abs(max_correlation) >= 0.2 and granger_p_value < 0.05:
            return 'WEAK', False
        
        return 'NONE', False


# ============================================================================
# Visualization
# ============================================================================

class Visualizer:
    """Generate visualizations for analysis results"""
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        if not HAS_MATPLOTLIB:
            warnings.warn("Matplotlib not available - visualizations disabled")
    
    def plot_correlation_by_lag(
        self, 
        correlations: List[CorrelationResult],
        market_name: str,
        output_file: str
    ):
        """Plot correlation coefficient vs lag"""
        if not HAS_MATPLOTLIB:
            return
        
        lags = [c.lag_hours for c in correlations]
        corrs = [c.correlation for c in correlations]
        
        plt.figure(figsize=(12, 6))
        plt.plot(lags, corrs, marker='o', linewidth=2, markersize=4)
        plt.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        plt.axvline(x=0, color='gray', linestyle='--', alpha=0.5)
        plt.xlabel('Lag (hours)', fontsize=12)
        plt.ylabel('Correlation Coefficient', fontsize=12)
        plt.title(f'Cross-Correlation Analysis: {market_name}', fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        # Highlight optimal lag
        optimal = max(correlations, key=lambda x: abs(x.correlation) if x.lag_hours > 0 else 0)
        plt.scatter([optimal.lag_hours], [optimal.correlation], 
                   color='red', s=100, zorder=5, label=f'Optimal lag: {optimal.lag_hours}h')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(self.output_dir / output_file, dpi=150)
        plt.close()
    
    def plot_signal_distribution(
        self,
        report: AnalysisReport,
        output_file: str = "signal_distribution.png"
    ):
        """Plot distribution of signal tiers"""
        if not HAS_MATPLOTLIB:
            return
        
        tiers = ['STRONG', 'MODERATE', 'WEAK', 'NONE']
        counts = [report.strong_signals, report.moderate_signals, 
                 report.weak_signals, report.no_signals]
        
        colors = ['#2ecc71', '#f39c12', '#e74c3c', '#95a5a6']
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(tiers, counts, color=colors, alpha=0.8, edgecolor='black')
        plt.xlabel('Signal Tier', fontsize=12)
        plt.ylabel('Number of Markets', fontsize=12)
        plt.title('Signal Strength Distribution Across Markets', fontsize=14, fontweight='bold')
        
        # Add count labels on bars
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{count}', ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / output_file, dpi=150)
        plt.close()
    
    def plot_top_markets(
        self,
        top_markets: List[Dict],
        output_file: str = "top_markets.png"
    ):
        """Plot top tradeable markets by correlation"""
        if not HAS_MATPLOTLIB or not top_markets:
            return
        
        # Take top 10
        top_10 = top_markets[:10]
        names = [m['market_name'][:40] + '...' if len(m['market_name']) > 40 
                else m['market_name'] for m in top_10]
        corrs = [m['max_correlation'] for m in top_10]
        tiers = [m['signal_tier'] for m in top_10]
        
        # Color by tier
        colors = []
        for tier in tiers:
            if tier == 'STRONG':
                colors.append('#2ecc71')
            elif tier == 'MODERATE':
                colors.append('#f39c12')
            else:
                colors.append('#e74c3c')
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(range(len(names)), corrs, color=colors, alpha=0.8, edgecolor='black')
        plt.yticks(range(len(names)), names, fontsize=10)
        plt.xlabel('Correlation Coefficient', fontsize=12)
        plt.title('Top Markets by Hype→Price Correlation', fontsize=14, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        # Add tier labels
        for i, (bar, tier) in enumerate(zip(bars, tiers)):
            width = bar.get_width()
            plt.text(width + 0.01, bar.get_y() + bar.get_height()/2.,
                    tier, ha='left', va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / output_file, dpi=150, bbox_inches='tight')
        plt.close()


# ============================================================================
# Main Analysis Pipeline
# ============================================================================

class CorrelationAnalysisPipeline:
    """Main pipeline orchestrating the entire analysis"""
    
    def __init__(
        self,
        db_path: str,
        min_samples: int = 30,
        max_lag: int = 48,
        significance_level: float = 0.05,
        output_dir: str = "output"
    ):
        self.db_path = db_path
        self.min_samples = min_samples
        self.max_lag = max_lag
        self.significance_level = significance_level
        self.output_dir = output_dir
        
        self.loader = DataLoader(db_path)
        self.preprocessor = TimeSeriesPreprocessor()
        self.analyzer = CorrelationAnalyzer(max_lag, significance_level)
        self.classifier = SignalClassifier()
        self.visualizer = Visualizer(output_dir)
    
    def analyze_market(self, market_id: str, market_name: str) -> Optional[MarketAnalysis]:
        """
        Analyze a single market
        
        Returns None if insufficient data
        """
        print(f"\n{'='*80}")
        print(f"Analyzing: {market_name}")
        print(f"Market ID: {market_id}")
        print(f"{'='*80}")
        
        # Load data
        try:
            price_df, hype_df = self.loader.get_market_data(market_id)
        except Exception as e:
            warnings.warn(f"Failed to load data for {market_id}: {e}")
            return None
        
        # Check data availability
        if len(price_df) == 0 or len(hype_df) == 0:
            print(f"❌ No data available")
            return None
        
        # Align to hourly
        merged = self.preprocessor.resample_to_hourly(price_df, hype_df)
        
        if len(merged) < self.min_samples:
            print(f"❌ Insufficient data: {len(merged)} samples (minimum: {self.min_samples})")
            return None
        
        print(f"✓ Data points: {len(merged)}")
        print(f"✓ Period: {merged.index[0]} to {merged.index[-1]}")
        
        # Extract series
        price_series = merged['yes_price']
        price_change = merged['price_change'].dropna()
        hype_series = merged['hype_score']
        
        # Test stationarity
        price_stationary, price_adf_p = self.preprocessor.test_stationarity(price_change, "price_change")
        hype_stationary, hype_adf_p = self.preprocessor.test_stationarity(hype_series, "hype")
        
        print(f"✓ Price stationarity: {price_stationary} (ADF p-value: {price_adf_p:.4f})")
        print(f"✓ Hype stationarity: {hype_stationary} (ADF p-value: {hype_adf_p:.4f})")
        
        # Make stationary if needed
        if not price_stationary:
            price_analysis = self.preprocessor.make_stationary(price_change)
        else:
            price_analysis = price_change
        
        if not hype_stationary:
            hype_analysis = self.preprocessor.make_stationary(hype_series)
        else:
            hype_analysis = hype_series
        
        # Normalize
        price_norm = self.preprocessor.normalize_series(price_analysis)
        hype_norm = self.preprocessor.normalize_series(hype_analysis)
        
        # Name series for Granger test
        price_norm.name = 'price'
        hype_norm.name = 'hype'
        
        # Cross-correlation analysis
        print("\n📊 Running cross-correlation analysis...")
        correlations = self.analyzer.cross_correlation(hype_norm, price_norm)
        optimal_lag, max_corr, max_corr_p = self.analyzer.find_optimal_lag(correlations)
        
        print(f"✓ Optimal lag: {optimal_lag} hours")
        print(f"✓ Max correlation: {max_corr:.4f} (p-value: {max_corr_p:.4f})")
        
        # Granger causality tests
        print("\n🔬 Running Granger causality tests...")
        granger_h2p = self.analyzer.granger_causality_test(hype_norm, price_norm)
        granger_p2h = self.analyzer.granger_causality_test(price_norm, hype_norm)
        
        print(f"✓ Hype→Price: lag={granger_h2p.best_lag}, p={granger_h2p.p_value:.4f}, "
              f"significant={granger_h2p.is_significant}")
        print(f"✓ Price→Hype: lag={granger_p2h.best_lag}, p={granger_p2h.p_value:.4f}, "
              f"significant={granger_p2h.is_significant}")
        
        # Check for problems
        print("\n⚠️  Checking for false positive patterns...")
        reverse_causality, reverse_msg = self.analyzer.check_reverse_causality(hype_norm, price_norm)
        common_cause, common_msg = self.analyzer.check_common_cause(correlations)
        
        warnings_list = []
        if reverse_msg:
            warnings_list.append(reverse_msg)
            print(f"  {reverse_msg}")
        if common_msg:
            warnings_list.append(common_msg)
            print(f"  {common_msg}")
        if not warnings_list:
            print("  ✓ No major issues detected")
        
        # Classify signal
        signal_tier, tradeable = self.classifier.classify_signal(
            max_corr,
            granger_h2p.p_value,
            optimal_lag,
            reverse_causality,
            common_cause,
            len(merged)
        )
        
        print(f"\n{'='*80}")
        print(f"SIGNAL TIER: {signal_tier}")
        print(f"TRADEABLE: {'YES' if tradeable else 'NO'}")
        print(f"{'='*80}")
        
        # Generate visualization
        safe_name = "".join(c for c in market_name if c.isalnum() or c in (' ', '-', '_'))[:50]
        viz_file = f"{market_id}_{safe_name}_correlation.png"
        self.visualizer.plot_correlation_by_lag(correlations, market_name, viz_file)
        
        # Calculate period
        period_days = (merged.index[-1] - merged.index[0]).total_seconds() / 86400
        
        # Return analysis
        return MarketAnalysis(
            market_id=market_id,
            market_name=market_name,
            data_points=len(merged),
            analysis_period_days=period_days,
            price_stationary=price_stationary,
            hype_stationary=hype_stationary,
            optimal_lag_hours=optimal_lag,
            max_correlation=max_corr,
            max_correlation_pvalue=max_corr_p,
            correlations_by_lag=correlations,
            granger_hype_to_price=granger_h2p,
            granger_price_to_hype=granger_p2h,
            warnings=warnings_list,
            reverse_causality_detected=reverse_causality,
            common_cause_suspected=common_cause,
            signal_tier=signal_tier,
            tradeable=tradeable,
            mean_hype=float(hype_series.mean()),
            std_hype=float(hype_series.std()),
            mean_price_change=float(price_change.mean()),
            std_price_change=float(price_change.std())
        )
    
    def analyze_all(self, market_id: Optional[str] = None) -> AnalysisReport:
        """
        Run analysis on all markets (or specific market if provided)
        """
        print("\n" + "="*80)
        print("TWITTER HYPE → PREDICTION MARKET CORRELATION ANALYSIS")
        print("="*80)
        print(f"Database: {self.db_path}")
        print(f"Min samples: {self.min_samples}")
        print(f"Max lag: {self.max_lag} hours")
        print(f"Significance level: {self.significance_level}")
        
        # Get markets to analyze
        markets_df = self.loader.get_markets(market_id)
        print(f"\nFound {len(markets_df)} market(s) to analyze")
        
        # Analyze each market
        results = []
        for _, row in markets_df.iterrows():
            result = self.analyze_market(row['market_id'], row['title'])
            if result:
                results.append(result)
        
        # Generate summary statistics
        strong = sum(1 for r in results if r.signal_tier == 'STRONG')
        moderate = sum(1 for r in results if r.signal_tier == 'MODERATE')
        weak = sum(1 for r in results if r.signal_tier == 'WEAK')
        none = sum(1 for r in results if r.signal_tier == 'NONE')
        
        # Sort markets by signal strength
        def tier_score(tier):
            return {'STRONG': 4, 'MODERATE': 3, 'WEAK': 2, 'NONE': 1}.get(tier, 0)
        
        top_markets = [
            {
                'market_id': r.market_id,
                'market_name': r.market_name,
                'signal_tier': r.signal_tier,
                'max_correlation': r.max_correlation,
                'optimal_lag_hours': r.optimal_lag_hours,
                'granger_p_value': r.granger_hype_to_price.p_value,
                'tradeable': r.tradeable,
                'data_points': r.data_points
            }
            for r in results
        ]
        top_markets.sort(key=lambda x: (tier_score(x['signal_tier']), abs(x['max_correlation'])), reverse=True)
        
        # Create report
        report = AnalysisReport(
            timestamp=datetime.now().isoformat(),
            database=self.db_path,
            total_markets_analyzed=len(markets_df),
            markets_with_sufficient_data=len(results),
            strong_signals=strong,
            moderate_signals=moderate,
            weak_signals=weak,
            no_signals=none,
            market_results=results,
            top_markets=top_markets,
            config={
                'min_samples': self.min_samples,
                'max_lag': self.max_lag,
                'significance_level': self.significance_level
            }
        )
        
        # Generate summary visualizations
        if HAS_MATPLOTLIB:
            self.visualizer.plot_signal_distribution(report)
            self.visualizer.plot_top_markets(top_markets)
        
        return report
    
    def save_report(self, report: AnalysisReport, output_file: str):
        """Save report to JSON file"""
        # Convert to dict (handle dataclasses and special types)
        def to_serializable(obj):
            if isinstance(obj, (MarketAnalysis, CorrelationResult, GrangerResult)):
                return asdict(obj)
            return obj
        
        report_dict = asdict(report)
        
        # Write JSON
        output_path = Path(self.output_dir) / output_file
        with open(output_path, 'w') as f:
            json.dump(report_dict, f, indent=2, default=to_serializable)
        
        print(f"\n✓ Report saved to: {output_path}")
    
    def print_summary(self, report: AnalysisReport):
        """Print executive summary to console"""
        print("\n" + "="*80)
        print("ANALYSIS SUMMARY")
        print("="*80)
        print(f"Total markets analyzed: {report.total_markets_analyzed}")
        print(f"Markets with sufficient data: {report.markets_with_sufficient_data}")
        print(f"\nSignal Distribution:")
        print(f"  🟢 STRONG signals: {report.strong_signals}")
        print(f"  🟡 MODERATE signals: {report.moderate_signals}")
        print(f"  🟠 WEAK signals: {report.weak_signals}")
        print(f"  ⚪ NO signals: {report.no_signals}")
        
        if report.top_markets:
            print(f"\n{'='*80}")
            print("TOP OPPORTUNITIES (Tradeable Markets)")
            print(f"{'='*80}")
            
            tradeable = [m for m in report.top_markets if m['tradeable']]
            if tradeable:
                for i, market in enumerate(tradeable[:5], 1):
                    print(f"\n{i}. {market['market_name'][:60]}")
                    print(f"   Tier: {market['signal_tier']}")
                    print(f"   Correlation: {market['max_correlation']:.4f}")
                    print(f"   Optimal lag: {market['optimal_lag_hours']} hours")
                    print(f"   Granger p-value: {market['granger_p_value']:.4f}")
            else:
                print("\n  No tradeable markets found.")
        
        print(f"\n{'='*80}")
    
    def close(self):
        """Clean up resources"""
        self.loader.close()


# ============================================================================
# Command-Line Interface
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Correlation Analysis: Twitter Hype → Prediction Market Movements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze all markets
  python correlation-analyzer.py --db polymarket_data.db
  
  # Analyze specific market
  python correlation-analyzer.py --db polymarket_data.db --market-id 12345
  
  # Custom parameters
  python correlation-analyzer.py --db polymarket_data.db --min-samples 50 --max-lag 24
  
  # Custom output
  python correlation-analyzer.py --db polymarket_data.db --output my_report.json --output-dir results/
        """
    )
    
    parser.add_argument('--db', required=True, help='Path to SQLite database')
    parser.add_argument('--market-id', help='Analyze specific market only')
    parser.add_argument('--min-samples', type=int, default=30, 
                       help='Minimum data points required (default: 30)')
    parser.add_argument('--max-lag', type=int, default=48,
                       help='Maximum lag in hours to test (default: 48)')
    parser.add_argument('--significance', type=float, default=0.05,
                       help='Statistical significance level (default: 0.05)')
    parser.add_argument('--output', default='correlation_report.json',
                       help='Output JSON filename (default: correlation_report.json)')
    parser.add_argument('--output-dir', default='output',
                       help='Output directory for reports and plots (default: output)')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization generation')
    
    args = parser.parse_args()
    
    # Validate database exists
    if not Path(args.db).exists():
        print(f"❌ Error: Database not found: {args.db}")
        return 1
    
    # Create output directory
    Path(args.output_dir).mkdir(exist_ok=True)
    
    # Run analysis
    try:
        pipeline = CorrelationAnalysisPipeline(
            db_path=args.db,
            min_samples=args.min_samples,
            max_lag=args.max_lag,
            significance_level=args.significance,
            output_dir=args.output_dir
        )
        
        # Analyze
        report = pipeline.analyze_all(market_id=args.market_id)
        
        # Save report
        pipeline.save_report(report, args.output)
        
        # Print summary
        pipeline.print_summary(report)
        
        # Cleanup
        pipeline.close()
        
        print(f"\n✓ Analysis complete!")
        print(f"✓ Results saved to: {args.output_dir}/")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
