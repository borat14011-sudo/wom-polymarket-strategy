#!/usr/bin/env python3
"""
Data Quality Checker for Polymarket Trading System
Validates data integrity, detects anomalies, and generates quality reports.
"""

import sqlite3
import json
import argparse
import sys
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Any, Tuple


class DataQualityChecker:
    """Comprehensive data quality validation for Polymarket data."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.issues = {
            'critical': [],
            'warning': [],
            'info': []
        }
        self.stats = {}
        
    def connect(self):
        """Establish database connection."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            return True
        except sqlite3.Error as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def add_issue(self, severity: str, category: str, description: str, 
                  count: int = 1, recommendation: str = None, details: Any = None):
        """Add an issue to the report."""
        issue = {
            'category': category,
            'description': description,
            'count': count,
            'timestamp': datetime.now().isoformat()
        }
        if recommendation:
            issue['recommendation'] = recommendation
        if details:
            issue['details'] = details
        
        self.issues[severity].append(issue)
    
    # ============================================================================
    # ANOMALY DETECTION
    # ============================================================================
    
    def check_anomalies(self) -> bool:
        """Run all anomaly detection checks."""
        print("\n🔍 Running Anomaly Detection...")
        
        success = True
        success &= self._check_price_jumps()
        success &= self._check_negative_values()
        success &= self._check_future_timestamps()
        success &= self._check_duplicate_records()
        
        return success
    
    def _check_price_jumps(self) -> bool:
        """Detect price jumps >50% between consecutive snapshots."""
        try:
            cursor = self.conn.cursor()
            
            # Get table name (try common variants)
            tables = self._get_tables()
            price_table = None
            for table in ['market_snapshots', 'prices', 'snapshots', 'market_data']:
                if table in tables:
                    price_table = table
                    break
            
            if not price_table:
                self.add_issue('info', 'anomalies', 
                             'No price snapshot table found',
                             recommendation='Verify table schema')
                return True
            
            # Find price jumps using window function
            query = f"""
            WITH price_changes AS (
                SELECT 
                    market_id,
                    timestamp,
                    price,
                    LAG(price) OVER (PARTITION BY market_id ORDER BY timestamp) as prev_price,
                    ABS(price - LAG(price) OVER (PARTITION BY market_id ORDER BY timestamp)) / 
                        NULLIF(LAG(price) OVER (PARTITION BY market_id ORDER BY timestamp), 0) as pct_change
                FROM {price_table}
                WHERE price IS NOT NULL
            )
            SELECT market_id, timestamp, price, prev_price, pct_change
            FROM price_changes
            WHERE pct_change > 0.5
            ORDER BY pct_change DESC
            LIMIT 100
            """
            
            cursor.execute(query)
            jumps = cursor.fetchall()
            
            if jumps:
                jump_details = [{
                    'market_id': row['market_id'],
                    'timestamp': row['timestamp'],
                    'price': row['price'],
                    'prev_price': row['prev_price'],
                    'change_pct': f"{row['pct_change']*100:.1f}%"
                } for row in jumps[:10]]  # Top 10
                
                self.add_issue('warning', 'anomalies',
                             f'Found {len(jumps)} price jumps >50%',
                             count=len(jumps),
                             recommendation='Review these snapshots for data collection errors',
                             details=jump_details)
            else:
                print("  ✓ No abnormal price jumps detected")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking price jumps: {e}")
            return False
    
    def _check_negative_values(self) -> bool:
        """Check for negative prices or volumes."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            # Check prices
            for table in ['market_snapshots', 'prices', 'snapshots', 'market_data']:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE price < 0")
                    neg_prices = cursor.fetchone()['cnt']
                    
                    if neg_prices > 0:
                        self.add_issue('critical', 'anomalies',
                                     f'Found {neg_prices} negative prices in {table}',
                                     count=neg_prices,
                                     recommendation='Delete or correct negative price records')
            
            # Check volumes
            for table in ['market_snapshots', 'volumes', 'snapshots', 'market_data']:
                if table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) as cnt FROM {table} WHERE volume < 0")
                        neg_volumes = cursor.fetchone()['cnt']
                        
                        if neg_volumes > 0:
                            self.add_issue('critical', 'anomalies',
                                         f'Found {neg_volumes} negative volumes in {table}',
                                         count=neg_volumes,
                                         recommendation='Delete or correct negative volume records')
                    except sqlite3.Error:
                        pass  # Volume column doesn't exist
            
            print("  ✓ Negative value check complete")
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking negative values: {e}")
            return False
    
    def _check_future_timestamps(self) -> bool:
        """Detect timestamps in the future."""
        try:
            cursor = self.conn.cursor()
            now = datetime.now().timestamp()
            tables = self._get_tables()
            
            future_count = 0
            for table in tables:
                # Check if table has timestamp column
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col['name'] for col in cursor.fetchall()]
                
                if 'timestamp' in columns:
                    cursor.execute(f"""
                        SELECT COUNT(*) as cnt 
                        FROM {table} 
                        WHERE timestamp > ?
                    """, (now,))
                    
                    cnt = cursor.fetchone()['cnt']
                    if cnt > 0:
                        future_count += cnt
                        self.add_issue('warning', 'anomalies',
                                     f'Found {cnt} future timestamps in {table}',
                                     count=cnt,
                                     recommendation='Check system clock or data source timestamps')
            
            if future_count == 0:
                print("  ✓ No future timestamps detected")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking timestamps: {e}")
            return False
    
    def _check_duplicate_records(self) -> bool:
        """Find duplicate records."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in tables:
                # Get column info
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col['name'] for col in cursor.fetchall()]
                
                # Find likely unique key combination
                key_cols = []
                if 'market_id' in columns:
                    key_cols.append('market_id')
                if 'timestamp' in columns:
                    key_cols.append('timestamp')
                
                if len(key_cols) >= 2:
                    key_str = ', '.join(key_cols)
                    cursor.execute(f"""
                        SELECT {key_str}, COUNT(*) as cnt
                        FROM {table}
                        GROUP BY {key_str}
                        HAVING cnt > 1
                        LIMIT 100
                    """)
                    
                    duplicates = cursor.fetchall()
                    if duplicates:
                        total_dupes = sum(row['cnt'] - 1 for row in duplicates)
                        self.add_issue('warning', 'anomalies',
                                     f'Found {len(duplicates)} duplicate key groups in {table} ({total_dupes} excess records)',
                                     count=total_dupes,
                                     recommendation='Remove duplicate records keeping the most recent')
            
            print("  ✓ Duplicate check complete")
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking duplicates: {e}")
            return False
    
    # ============================================================================
    # COMPLETENESS CHECKS
    # ============================================================================
    
    def check_completeness(self) -> bool:
        """Run all completeness checks."""
        print("\n📊 Running Completeness Checks...")
        
        success = True
        success &= self._check_timestamp_gaps()
        success &= self._check_stale_markets()
        success &= self._check_snapshot_counts()
        
        return success
    
    def _check_timestamp_gaps(self) -> bool:
        """Find gaps >30 minutes in data collection."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in ['market_snapshots', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                # Find gaps using LAG
                cursor.execute(f"""
                    WITH gaps AS (
                        SELECT 
                            market_id,
                            timestamp,
                            LAG(timestamp) OVER (PARTITION BY market_id ORDER BY timestamp) as prev_timestamp,
                            timestamp - LAG(timestamp) OVER (PARTITION BY market_id ORDER BY timestamp) as gap_seconds
                        FROM {table}
                    )
                    SELECT market_id, prev_timestamp, timestamp, gap_seconds
                    FROM gaps
                    WHERE gap_seconds > 1800  -- 30 minutes
                    ORDER BY gap_seconds DESC
                    LIMIT 50
                """)
                
                gaps = cursor.fetchall()
                if gaps:
                    gap_details = [{
                        'market_id': row['market_id'],
                        'gap_start': datetime.fromtimestamp(row['prev_timestamp']).isoformat(),
                        'gap_end': datetime.fromtimestamp(row['timestamp']).isoformat(),
                        'gap_minutes': round(row['gap_seconds'] / 60, 1)
                    } for row in gaps[:10]]
                    
                    self.add_issue('warning', 'completeness',
                                 f'Found {len(gaps)} gaps >30min in {table}',
                                 count=len(gaps),
                                 recommendation='Check data collector uptime and error logs',
                                 details=gap_details)
                else:
                    print(f"  ✓ No significant gaps in {table}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking gaps: {e}")
            return False
    
    def _check_stale_markets(self) -> bool:
        """Find markets with no recent data."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            # Find appropriate table
            for table in ['market_snapshots', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                # Get cutoff (24 hours ago)
                cutoff = (datetime.now() - timedelta(hours=24)).timestamp()
                
                cursor.execute(f"""
                    SELECT market_id, MAX(timestamp) as last_seen
                    FROM {table}
                    GROUP BY market_id
                    HAVING MAX(timestamp) < ?
                    ORDER BY last_seen DESC
                    LIMIT 100
                """, (cutoff,))
                
                stale = cursor.fetchall()
                if stale:
                    stale_details = [{
                        'market_id': row['market_id'],
                        'last_seen': datetime.fromtimestamp(row['last_seen']).isoformat(),
                        'hours_ago': round((datetime.now().timestamp() - row['last_seen']) / 3600, 1)
                    } for row in stale[:10]]
                    
                    self.add_issue('info', 'completeness',
                                 f'Found {len(stale)} markets with no data in last 24h',
                                 count=len(stale),
                                 recommendation='Markets may be closed or collector needs restart',
                                 details=stale_details)
                else:
                    print(f"  ✓ All markets have recent data in {table}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking stale markets: {e}")
            return False
    
    def _check_snapshot_counts(self) -> bool:
        """Compare expected vs actual snapshot counts."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in ['market_snapshots', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                # Get time range
                cursor.execute(f"""
                    SELECT 
                        MIN(timestamp) as first_ts,
                        MAX(timestamp) as last_ts,
                        COUNT(DISTINCT market_id) as market_count,
                        COUNT(*) as snapshot_count
                    FROM {table}
                """)
                
                row = cursor.fetchone()
                if row['first_ts'] and row['last_ts']:
                    duration_hours = (row['last_ts'] - row['first_ts']) / 3600
                    markets = row['market_count']
                    actual_snapshots = row['snapshot_count']
                    
                    # Assume 5-minute intervals as baseline
                    expected_per_market = int(duration_hours * 12)  # 12 per hour
                    expected_total = expected_per_market * markets
                    
                    coverage = (actual_snapshots / expected_total * 100) if expected_total > 0 else 0
                    
                    self.stats[table] = {
                        'duration_hours': round(duration_hours, 1),
                        'markets': markets,
                        'actual_snapshots': actual_snapshots,
                        'expected_snapshots': expected_total,
                        'coverage_pct': round(coverage, 1)
                    }
                    
                    if coverage < 80:
                        self.add_issue('warning', 'completeness',
                                     f'{table} has {coverage:.1f}% data coverage (expected ~100%)',
                                     recommendation='Check for collection failures or adjust expected interval')
                    else:
                        print(f"  ✓ {table}: {coverage:.1f}% coverage")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking snapshot counts: {e}")
            return False
    
    # ============================================================================
    # CONSISTENCY CHECKS
    # ============================================================================
    
    def check_consistency(self) -> bool:
        """Run all consistency checks."""
        print("\n🔗 Running Consistency Checks...")
        
        success = True
        success &= self._check_price_ranges()
        success &= self._check_volume_monotonicity()
        success &= self._check_referential_integrity()
        
        return success
    
    def _check_price_ranges(self) -> bool:
        """Ensure prices are within valid range (0-1 for binary markets)."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in ['market_snapshots', 'prices', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                cursor.execute(f"""
                    SELECT COUNT(*) as cnt
                    FROM {table}
                    WHERE price NOT BETWEEN 0 AND 1
                """)
                
                invalid = cursor.fetchone()['cnt']
                if invalid > 0:
                    self.add_issue('critical', 'consistency',
                                 f'Found {invalid} prices outside [0,1] range in {table}',
                                 count=invalid,
                                 recommendation='Prices should be normalized probabilities between 0 and 1')
                else:
                    print(f"  ✓ All prices in valid range in {table}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking price ranges: {e}")
            return False
    
    def _check_volume_monotonicity(self) -> bool:
        """Check that cumulative volume never decreases."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in ['market_snapshots', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                # Check if volume column exists
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col['name'] for col in cursor.fetchall()]
                
                if 'volume' not in columns:
                    continue
                
                cursor.execute(f"""
                    WITH volume_changes AS (
                        SELECT 
                            market_id,
                            timestamp,
                            volume,
                            LAG(volume) OVER (PARTITION BY market_id ORDER BY timestamp) as prev_volume
                        FROM {table}
                        WHERE volume IS NOT NULL
                    )
                    SELECT market_id, timestamp, volume, prev_volume
                    FROM volume_changes
                    WHERE volume < prev_volume
                    LIMIT 100
                """)
                
                decreases = cursor.fetchall()
                if decreases:
                    details = [{
                        'market_id': row['market_id'],
                        'timestamp': datetime.fromtimestamp(row['timestamp']).isoformat(),
                        'volume': row['volume'],
                        'prev_volume': row['prev_volume']
                    } for row in decreases[:10]]
                    
                    self.add_issue('warning', 'consistency',
                                 f'Found {len(decreases)} volume decreases in {table}',
                                 count=len(decreases),
                                 recommendation='Volume should be cumulative and never decrease',
                                 details=details)
                else:
                    print(f"  ✓ Volume is monotonically increasing in {table}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking volume monotonicity: {e}")
            return False
    
    def _check_referential_integrity(self) -> bool:
        """Check that market IDs match between related tables."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            # Common table relationships
            relationships = [
                ('market_snapshots', 'markets', 'market_id'),
                ('tweets', 'markets', 'market_id'),
                ('market_data', 'markets', 'market_id'),
            ]
            
            for child_table, parent_table, key_col in relationships:
                if child_table not in tables or parent_table not in tables:
                    continue
                
                cursor.execute(f"""
                    SELECT COUNT(DISTINCT c.{key_col}) as orphaned
                    FROM {child_table} c
                    LEFT JOIN {parent_table} p ON c.{key_col} = p.{key_col}
                    WHERE p.{key_col} IS NULL
                """)
                
                orphaned = cursor.fetchone()['orphaned']
                if orphaned > 0:
                    self.add_issue('warning', 'consistency',
                                 f'Found {orphaned} orphaned market_ids in {child_table}',
                                 count=orphaned,
                                 recommendation=f'Add missing markets to {parent_table} or clean orphaned records')
                else:
                    print(f"  ✓ Referential integrity OK: {child_table} -> {parent_table}")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking referential integrity: {e}")
            return False
    
    # ============================================================================
    # TWITTER DATA QUALITY
    # ============================================================================
    
    def check_twitter_quality(self) -> bool:
        """Run all Twitter data quality checks."""
        print("\n🐦 Running Twitter Data Quality Checks...")
        
        tables = self._get_tables()
        if 'tweets' not in tables and 'twitter' not in tables:
            print("  ℹ️  No Twitter table found, skipping")
            return True
        
        success = True
        success &= self._check_duplicate_tweets()
        success &= self._check_bot_detection()
        success &= self._check_spam_patterns()
        
        return success
    
    def _check_duplicate_tweets(self) -> bool:
        """Find duplicate tweets (exact text match)."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            table = 'tweets' if 'tweets' in tables else 'twitter'
            
            cursor.execute(f"""
                SELECT text, COUNT(*) as cnt
                FROM {table}
                GROUP BY text
                HAVING cnt > 1
                ORDER BY cnt DESC
                LIMIT 50
            """)
            
            duplicates = cursor.fetchall()
            if duplicates:
                total_dupes = sum(row['cnt'] - 1 for row in duplicates)
                dup_details = [{
                    'text': row['text'][:100] + '...' if len(row['text']) > 100 else row['text'],
                    'count': row['cnt']
                } for row in duplicates[:10]]
                
                self.add_issue('warning', 'twitter',
                             f'Found {len(duplicates)} duplicate tweet texts ({total_dupes} duplicates)',
                             count=total_dupes,
                             recommendation='Keep only unique tweets or add deduplication logic',
                             details=dup_details)
            else:
                print("  ✓ No duplicate tweets found")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking duplicate tweets: {e}")
            return False
    
    def _check_bot_detection(self) -> bool:
        """Detect potential bots (same text from multiple accounts)."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            table = 'tweets' if 'tweets' in tables else 'twitter'
            
            # Check if user/author column exists
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col['name'] for col in cursor.fetchall()]
            
            user_col = None
            for col in ['user', 'author', 'username', 'screen_name']:
                if col in columns:
                    user_col = col
                    break
            
            if not user_col:
                print("  ℹ️  No user column found, skipping bot detection")
                return True
            
            cursor.execute(f"""
                SELECT text, COUNT(DISTINCT {user_col}) as user_count
                FROM {table}
                GROUP BY text
                HAVING user_count > 3
                ORDER BY user_count DESC
                LIMIT 50
            """)
            
            bot_patterns = cursor.fetchall()
            if bot_patterns:
                bot_details = [{
                    'text': row['text'][:100] + '...' if len(row['text']) > 100 else row['text'],
                    'unique_users': row['user_count']
                } for row in bot_patterns[:10]]
                
                self.add_issue('warning', 'twitter',
                             f'Found {len(bot_patterns)} potential bot patterns (same text, multiple users)',
                             count=len(bot_patterns),
                             recommendation='Review accounts posting identical content',
                             details=bot_details)
            else:
                print("  ✓ No obvious bot patterns detected")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking bot patterns: {e}")
            return False
    
    def _check_spam_patterns(self) -> bool:
        """Detect spam (excessive hashtags, links)."""
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            table = 'tweets' if 'tweets' in tables else 'twitter'
            
            # Count hashtags and links
            cursor.execute(f"""
                SELECT 
                    text,
                    LENGTH(text) - LENGTH(REPLACE(text, '#', '')) as hashtag_count,
                    LENGTH(text) - LENGTH(REPLACE(REPLACE(text, 'http://', ''), 'https://', '')) as link_indicator
                FROM {table}
            """)
            
            spam_count = 0
            spam_examples = []
            
            for row in cursor.fetchall():
                hashtags = row['hashtag_count']
                text = row['text']
                
                # Spam criteria: >5 hashtags or very short with multiple links
                is_spam = hashtags > 5 or (len(text) < 50 and 'http' in text.lower())
                
                if is_spam:
                    spam_count += 1
                    if len(spam_examples) < 10:
                        spam_examples.append({
                            'text': text[:100] + '...' if len(text) > 100 else text,
                            'hashtags': hashtags
                        })
            
            if spam_count > 0:
                self.add_issue('info', 'twitter',
                             f'Found {spam_count} potential spam tweets',
                             count=spam_count,
                             recommendation='Consider filtering tweets with excessive hashtags or links',
                             details=spam_examples)
            else:
                print("  ✓ No obvious spam patterns detected")
            
            return True
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error checking spam patterns: {e}")
            return False
    
    # ============================================================================
    # AUTO-FIX FUNCTIONALITY
    # ============================================================================
    
    def auto_fix(self) -> bool:
        """Automatically fix issues where possible."""
        print("\n🔧 Running Auto-Fix...")
        
        fixes_applied = 0
        
        # Fix 1: Remove negative prices
        try:
            cursor = self.conn.cursor()
            tables = self._get_tables()
            
            for table in ['market_snapshots', 'prices', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                cursor.execute(f"DELETE FROM {table} WHERE price < 0")
                deleted = cursor.rowcount
                if deleted > 0:
                    print(f"  ✓ Removed {deleted} negative prices from {table}")
                    fixes_applied += deleted
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error removing negative prices: {e}")
        
        # Fix 2: Remove future timestamps
        try:
            now = datetime.now().timestamp()
            
            for table in self._get_tables():
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col['name'] for col in cursor.fetchall()]
                
                if 'timestamp' in columns:
                    cursor.execute(f"DELETE FROM {table} WHERE timestamp > ?", (now,))
                    deleted = cursor.rowcount
                    if deleted > 0:
                        print(f"  ✓ Removed {deleted} future timestamps from {table}")
                        fixes_applied += deleted
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error removing future timestamps: {e}")
        
        # Fix 3: Remove exact duplicates (keep first occurrence)
        try:
            for table in self._get_tables():
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [col['name'] for col in cursor.fetchall()]
                
                # Find likely unique key
                key_cols = []
                if 'market_id' in columns:
                    key_cols.append('market_id')
                if 'timestamp' in columns:
                    key_cols.append('timestamp')
                
                if len(key_cols) >= 2 and 'rowid' in [c.lower() for c in columns] or True:
                    key_str = ', '.join(key_cols)
                    
                    # SQLite rowid-based deduplication
                    cursor.execute(f"""
                        DELETE FROM {table}
                        WHERE rowid NOT IN (
                            SELECT MIN(rowid)
                            FROM {table}
                            GROUP BY {key_str}
                        )
                    """)
                    deleted = cursor.rowcount
                    if deleted > 0:
                        print(f"  ✓ Removed {deleted} duplicate records from {table}")
                        fixes_applied += deleted
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error removing duplicates: {e}")
        
        # Fix 4: Remove prices outside [0,1]
        try:
            for table in ['market_snapshots', 'prices', 'snapshots', 'market_data']:
                if table not in tables:
                    continue
                
                cursor.execute(f"DELETE FROM {table} WHERE price NOT BETWEEN 0 AND 1")
                deleted = cursor.rowcount
                if deleted > 0:
                    print(f"  ✓ Removed {deleted} invalid prices from {table}")
                    fixes_applied += deleted
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            print(f"  ⚠️  Error removing invalid prices: {e}")
        
        print(f"\n✅ Applied {fixes_applied} fixes")
        return True
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _get_tables(self) -> List[str]:
        """Get list of all tables in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row['name'] for row in cursor.fetchall()]
    
    def generate_report(self, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive quality report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'database': self.db_path,
            'summary': {
                'critical_issues': len(self.issues['critical']),
                'warnings': len(self.issues['warning']),
                'info': len(self.issues['info']),
                'total_issues': sum(len(v) for v in self.issues.values())
            },
            'issues': self.issues,
            'statistics': self.stats
        }
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n📄 Report saved to: {output_file}")
        
        return report
    
    def print_summary(self):
        """Print a human-readable summary."""
        print("\n" + "="*70)
        print("DATA QUALITY REPORT SUMMARY")
        print("="*70)
        
        total_critical = len(self.issues['critical'])
        total_warnings = len(self.issues['warning'])
        total_info = len(self.issues['info'])
        
        print(f"\n🔴 Critical Issues: {total_critical}")
        for issue in self.issues['critical']:
            print(f"   • {issue['description']}")
        
        print(f"\n🟡 Warnings: {total_warnings}")
        for issue in self.issues['warning'][:5]:  # Top 5
            print(f"   • {issue['description']}")
        if total_warnings > 5:
            print(f"   ... and {total_warnings - 5} more")
        
        print(f"\n🔵 Info: {total_info}")
        for issue in self.issues['info'][:3]:  # Top 3
            print(f"   • {issue['description']}")
        if total_info > 3:
            print(f"   ... and {total_info - 3} more")
        
        # Overall health score
        score = 100
        score -= total_critical * 10
        score -= total_warnings * 3
        score -= total_info * 1
        score = max(0, score)
        
        print(f"\n📊 Overall Data Quality Score: {score}/100")
        
        if score >= 90:
            print("   ✅ Excellent - Data quality is very good")
        elif score >= 70:
            print("   🟡 Good - Some issues need attention")
        elif score >= 50:
            print("   🟠 Fair - Multiple issues require fixes")
        else:
            print("   🔴 Poor - Significant data quality problems detected")
        
        print("\n" + "="*70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Data Quality Checker for Polymarket Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python data-quality-checker.py                    # Full check
  python data-quality-checker.py --anomalies       # Just anomalies
  python data-quality-checker.py --completeness    # Just completeness
  python data-quality-checker.py --fix             # Auto-fix issues
  python data-quality-checker.py --report report.json
        """
    )
    
    parser.add_argument('--db', default='polymarket_data.db',
                       help='Path to SQLite database (default: polymarket_data.db)')
    parser.add_argument('--anomalies', action='store_true',
                       help='Run only anomaly detection checks')
    parser.add_argument('--completeness', action='store_true',
                       help='Run only completeness checks')
    parser.add_argument('--consistency', action='store_true',
                       help='Run only consistency checks')
    parser.add_argument('--twitter', action='store_true',
                       help='Run only Twitter quality checks')
    parser.add_argument('--fix', action='store_true',
                       help='Automatically fix issues where possible')
    parser.add_argument('--report', metavar='FILE',
                       help='Save JSON report to file')
    
    args = parser.parse_args()
    
    # Create checker
    checker = DataQualityChecker(args.db)
    
    if not checker.connect():
        sys.exit(1)
    
    try:
        print(f"\n🔍 Data Quality Checker for Polymarket")
        print(f"📁 Database: {args.db}\n")
        
        # Determine what to run
        run_all = not any([args.anomalies, args.completeness, 
                          args.consistency, args.twitter, args.fix])
        
        if args.fix:
            checker.auto_fix()
        else:
            if run_all or args.anomalies:
                checker.check_anomalies()
            
            if run_all or args.completeness:
                checker.check_completeness()
            
            if run_all or args.consistency:
                checker.check_consistency()
            
            if run_all or args.twitter:
                checker.check_twitter_quality()
        
        # Generate report
        report = checker.generate_report(args.report)
        
        # Print summary
        checker.print_summary()
        
        # Exit code based on severity
        if len(checker.issues['critical']) > 0:
            sys.exit(2)
        elif len(checker.issues['warning']) > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    finally:
        checker.close()


if __name__ == '__main__':
    main()
