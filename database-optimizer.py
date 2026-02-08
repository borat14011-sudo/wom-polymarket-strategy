#!/usr/bin/env python3
"""
Database Optimizer for Polymarket Trading System
Provides indexing, batch operations, connection pooling, and performance analysis.
"""

import sqlite3
import argparse
import sys
import time
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime


class ConnectionPool:
    """Simple SQLite connection pool for reusing database connections."""
    
    def __init__(self, db_path: str, pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self._connections = []
        self._in_use = set()
        
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent access
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    @contextmanager
    def get_connection(self):
        """Get a connection from the pool (context manager)."""
        conn = None
        try:
            # Try to reuse an existing connection
            if self._connections:
                conn = self._connections.pop()
            else:
                conn = self._create_connection()
            
            self._in_use.add(id(conn))
            yield conn
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                self._in_use.discard(id(conn))
                # Return to pool if not at capacity
                if len(self._connections) < self.pool_size:
                    self._connections.append(conn)
                else:
                    conn.close()
    
    def close_all(self):
        """Close all pooled connections."""
        for conn in self._connections:
            conn.close()
        self._connections.clear()
        self._in_use.clear()


class DatabaseOptimizer:
    """Main database optimizer class."""
    
    # Default batch size for bulk operations
    BATCH_SIZE = 100
    
    # Index definitions: (table, columns, index_name)
    INDEXES = [
        ('snapshots', ['market_id', 'timestamp'], 'idx_snapshots_market_time'),
        ('snapshots', ['timestamp'], 'idx_snapshots_time'),
        ('tweets', ['market_id', 'timestamp'], 'idx_tweets_market_time'),
        ('tweets', ['timestamp'], 'idx_tweets_time'),
        ('hype_signals', ['market_id', 'timestamp'], 'idx_hype_signals_market_time'),
        ('markets', ['market_id'], 'idx_markets_market_id'),
    ]
    
    def __init__(self, db_path: str = 'polymarket_data.db', pool_size: int = 5):
        """Initialize optimizer with database path and connection pool."""
        self.db_path = db_path
        self.pool = ConnectionPool(db_path, pool_size)
        
    def add_indexes(self, force: bool = False) -> Dict[str, Any]:
        """
        Add performance indexes to database tables.
        
        Args:
            force: If True, drop and recreate existing indexes
            
        Returns:
            Dict with results of index creation
        """
        results = {
            'created': [],
            'skipped': [],
            'errors': [],
            'total_time': 0
        }
        
        start_time = time.time()
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            for table, columns, index_name in self.INDEXES:
                try:
                    # Check if table exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table,)
                    )
                    if not cursor.fetchone():
                        results['skipped'].append(f"{index_name} (table '{table}' not found)")
                        continue
                    
                    # Check if index already exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                        (index_name,)
                    )
                    exists = cursor.fetchone()
                    
                    if exists:
                        if force:
                            cursor.execute(f"DROP INDEX {index_name}")
                            print(f"Dropped existing index: {index_name}")
                        else:
                            results['skipped'].append(index_name)
                            continue
                    
                    # Create index
                    columns_str = ', '.join(columns)
                    create_sql = f"CREATE INDEX {index_name} ON {table} ({columns_str})"
                    
                    idx_start = time.time()
                    cursor.execute(create_sql)
                    idx_time = time.time() - idx_start
                    
                    conn.commit()
                    results['created'].append(f"{index_name} ({idx_time:.2f}s)")
                    print(f"✓ Created index: {index_name} on {table}({columns_str}) in {idx_time:.2f}s")
                    
                except sqlite3.Error as e:
                    results['errors'].append(f"{index_name}: {str(e)}")
                    print(f"✗ Error creating {index_name}: {e}")
        
        results['total_time'] = time.time() - start_time
        return results
    
    def batch_insert(self, table: str, records: List[Dict[str, Any]], 
                    batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Insert records in batches for better performance.
        
        Args:
            table: Target table name
            records: List of record dictionaries
            batch_size: Number of records per batch (default: 100)
            
        Returns:
            Dict with insertion statistics
        """
        if not records:
            return {'inserted': 0, 'batches': 0, 'time': 0}
        
        batch_size = batch_size or self.BATCH_SIZE
        start_time = time.time()
        
        # Get column names from first record
        columns = list(records[0].keys())
        placeholders = ','.join(['?' for _ in columns])
        column_names = ','.join(columns)
        
        insert_sql = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
        
        total_inserted = 0
        batch_count = 0
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                for i in range(0, len(records), batch_size):
                    batch = records[i:i + batch_size]
                    
                    # Convert dict records to tuples matching column order
                    batch_values = [
                        tuple(record[col] for col in columns)
                        for record in batch
                    ]
                    
                    cursor.executemany(insert_sql, batch_values)
                    total_inserted += len(batch)
                    batch_count += 1
                
                conn.commit()
                
            except sqlite3.Error as e:
                conn.rollback()
                raise Exception(f"Batch insert failed: {e}")
        
        return {
            'inserted': total_inserted,
            'batches': batch_count,
            'time': time.time() - start_time
        }
    
    def vacuum(self) -> Dict[str, Any]:
        """
        Run VACUUM to optimize database and reclaim space.
        
        Returns:
            Dict with vacuum statistics
        """
        print("Running VACUUM (this may take a while)...")
        
        # Get file size before
        import os
        size_before = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        start_time = time.time()
        
        with self.pool.get_connection() as conn:
            try:
                conn.execute("VACUUM")
                conn.commit()
            except sqlite3.Error as e:
                raise Exception(f"VACUUM failed: {e}")
        
        # Get file size after
        size_after = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        return {
            'time': time.time() - start_time,
            'size_before_mb': size_before / (1024 * 1024),
            'size_after_mb': size_after / (1024 * 1024),
            'space_saved_mb': (size_before - size_after) / (1024 * 1024)
        }
    
    def analyze(self) -> None:
        """Run ANALYZE to update query planner statistics."""
        print("Running ANALYZE...")
        start_time = time.time()
        
        with self.pool.get_connection() as conn:
            try:
                conn.execute("ANALYZE")
                conn.commit()
            except sqlite3.Error as e:
                raise Exception(f"ANALYZE failed: {e}")
        
        print(f"✓ ANALYZE completed in {time.time() - start_time:.2f}s")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Gather comprehensive database statistics.
        
        Returns:
            Dict with detailed statistics
        """
        stats = {
            'tables': {},
            'indexes': [],
            'database': {},
            'query_performance': {}
        }
        
        with self.pool.get_connection() as conn:
            cursor = conn.cursor()
            
            # Database-level stats
            import os
            if os.path.exists(self.db_path):
                stats['database']['size_mb'] = os.path.getsize(self.db_path) / (1024 * 1024)
            
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            stats['database']['page_count'] = page_count
            stats['database']['page_size'] = page_size
            stats['database']['total_pages_mb'] = (page_count * page_size) / (1024 * 1024)
            
            # Get all tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            # Table statistics
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    row_count = cursor.fetchone()[0]
                    
                    stats['tables'][table] = {
                        'rows': row_count,
                        'indexes': []
                    }
                except sqlite3.Error:
                    stats['tables'][table] = {
                        'rows': 'ERROR',
                        'indexes': []
                    }
            
            # Index information
            cursor.execute(
                "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'"
            )
            
            for row in cursor.fetchall():
                index_info = {
                    'name': row[0],
                    'table': row[1],
                    'sql': row[2] or 'AUTO'
                }
                stats['indexes'].append(index_info)
                
                # Add to table stats
                if row[1] in stats['tables']:
                    stats['tables'][row[1]]['indexes'].append(row[0])
            
            # Query performance check (sample queries)
            performance_tests = [
                ("snapshots by timestamp", "SELECT COUNT(*) FROM snapshots WHERE timestamp > ?", 
                 (int(time.time()) - 86400,)),
                ("tweets by market", "SELECT COUNT(*) FROM tweets WHERE market_id = ?", ('test_market',)),
            ]
            
            for test_name, query, params in performance_tests:
                try:
                    # Check if table exists
                    table_name = query.split('FROM')[1].split('WHERE')[0].strip()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table_name,)
                    )
                    if cursor.fetchone():
                        start = time.time()
                        cursor.execute(query, params)
                        cursor.fetchone()
                        duration = time.time() - start
                        stats['query_performance'][test_name] = f"{duration*1000:.2f}ms"
                except sqlite3.Error:
                    stats['query_performance'][test_name] = "N/A"
        
        return stats
    
    def print_statistics(self, stats: Dict[str, Any]) -> None:
        """Pretty print statistics."""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        # Database info
        db = stats['database']
        print(f"\n📊 Database Overview:")
        print(f"   Size: {db.get('size_mb', 0):.2f} MB")
        print(f"   Pages: {db.get('page_count', 0):,} × {db.get('page_size', 0)} bytes")
        
        # Tables
        print(f"\n📋 Tables ({len(stats['tables'])}):")
        for table, info in stats['tables'].items():
            row_count = info['rows'] if isinstance(info['rows'], int) else 'N/A'
            index_count = len(info['indexes'])
            if isinstance(row_count, int):
                print(f"   {table:20} {row_count:>10,} rows  {index_count} indexes")
            else:
                print(f"   {table:20} {row_count:>10}      {index_count} indexes")
        
        # Indexes
        print(f"\n🔍 Indexes ({len(stats['indexes'])}):")
        for idx in stats['indexes']:
            print(f"   {idx['name']:30} on {idx['table']}")
        
        # Performance
        if stats['query_performance']:
            print(f"\n⚡ Query Performance:")
            for test, duration in stats['query_performance'].items():
                print(f"   {test:30} {duration:>10}")
        
        print("\n" + "="*60 + "\n")
    
    def optimize_all(self) -> None:
        """Run all optimization steps."""
        print("="*60)
        print("FULL DATABASE OPTIMIZATION")
        print("="*60 + "\n")
        
        # Step 1: Add indexes
        print("Step 1: Adding indexes...")
        idx_results = self.add_indexes()
        print(f"   Created: {len(idx_results['created'])}")
        print(f"   Skipped: {len(idx_results['skipped'])}")
        print(f"   Errors: {len(idx_results['errors'])}\n")
        
        # Step 2: Analyze
        print("Step 2: Analyzing database...")
        self.analyze()
        print()
        
        # Step 3: Vacuum
        print("Step 3: Vacuuming database...")
        vac_results = self.vacuum()
        print(f"   Time: {vac_results['time']:.2f}s")
        print(f"   Size before: {vac_results['size_before_mb']:.2f} MB")
        print(f"   Size after: {vac_results['size_after_mb']:.2f} MB")
        print(f"   Space saved: {vac_results['space_saved_mb']:.2f} MB\n")
        
        print("✓ Optimization complete!")
    
    def close(self):
        """Clean up resources."""
        self.pool.close_all()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Database Optimizer for Polymarket Trading System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --optimize              Run full optimization
  %(prog)s --stats                 Show database statistics
  %(prog)s --vacuum                Vacuum database
  %(prog)s --add-indexes           Add missing indexes
  %(prog)s --add-indexes --force   Recreate all indexes
        """
    )
    
    parser.add_argument(
        '--db',
        default='polymarket_data.db',
        help='Database file path (default: polymarket_data.db)'
    )
    
    parser.add_argument(
        '--optimize',
        action='store_true',
        help='Run full optimization (indexes + analyze + vacuum)'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show database statistics'
    )
    
    parser.add_argument(
        '--vacuum',
        action='store_true',
        help='Run VACUUM to reclaim space'
    )
    
    parser.add_argument(
        '--add-indexes',
        action='store_true',
        help='Add missing performance indexes'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreate indexes (use with --add-indexes)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Run ANALYZE to update query statistics'
    )
    
    args = parser.parse_args()
    
    # Show help if no action specified
    if not any([args.optimize, args.stats, args.vacuum, args.add_indexes, args.analyze]):
        parser.print_help()
        return 0
    
    # Initialize optimizer
    try:
        optimizer = DatabaseOptimizer(args.db)
    except Exception as e:
        print(f"✗ Failed to initialize optimizer: {e}", file=sys.stderr)
        return 1
    
    try:
        # Execute requested actions
        if args.optimize:
            optimizer.optimize_all()
        
        if args.add_indexes:
            results = optimizer.add_indexes(force=args.force)
            print(f"\n✓ Index creation completed in {results['total_time']:.2f}s")
            if results['errors']:
                print(f"⚠ Errors encountered:")
                for error in results['errors']:
                    print(f"  - {error}")
        
        if args.analyze:
            optimizer.analyze()
        
        if args.vacuum:
            results = optimizer.vacuum()
            print(f"\n✓ VACUUM completed in {results['time']:.2f}s")
            print(f"  Size: {results['size_before_mb']:.2f} MB → {results['size_after_mb']:.2f} MB")
            print(f"  Saved: {results['space_saved_mb']:.2f} MB")
        
        if args.stats:
            stats = optimizer.get_statistics()
            optimizer.print_statistics(stats)
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        return 1
    
    finally:
        optimizer.close()


if __name__ == '__main__':
    sys.exit(main())
