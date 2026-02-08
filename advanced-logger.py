#!/usr/bin/env python3
"""
Advanced Logging System for Polymarket Trading System

A structured JSON logging module with rotation, compression, and search capabilities.

Example Usage:
    >>> from advanced_logger import get_logger
    >>> 
    >>> # Basic logging
    >>> logger = get_logger("data-collector")
    >>> logger.info("Fetched markets", metrics={"count": 15, "latency_ms": 234})
    >>> logger.error("API failed", exception=Exception("Connection timeout"))
    >>> 
    >>> # With performance tracking
    >>> import time
    >>> start = time.time()
    >>> # ... do work ...
    >>> latency_ms = (time.time() - start) * 1000
    >>> logger.info("Database query completed", metrics={"latency_ms": latency_ms, "rows": 42})
    >>> 
    >>> # Memory tracking
    >>> import psutil
    >>> process = psutil.Process()
    >>> memory_mb = process.memory_info().rss / 1024 / 1024
    >>> logger.info("Memory checkpoint", metrics={"memory_mb": memory_mb})

CLI Usage:
    # Search logs
    python advanced-logger.py --search "ERROR" --component "data-collector" --last 24h
    
    # Daily summary
    python advanced-logger.py --summary
    
    # Summary for specific date
    python advanced-logger.py --summary --date 2026-02-05
    
    # Search with custom time range
    python advanced-logger.py --search "API" --last 7d
"""

import logging
import json
import gzip
import os
import time
import threading
from datetime import datetime, timedelta
from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler
from pathlib import Path
from collections import defaultdict
import argparse
import glob
import re


# Global configuration
LOG_DIR = Path("logs")
MAX_BYTES = 100 * 1024 * 1024  # 100MB
BACKUP_COUNT = 30
LOG_FORMAT = "%(message)s"

# Thread-safe logger cache
_logger_cache = {}
_cache_lock = threading.Lock()


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs structured JSON logs."""
    
    def format(self, record):
        """
        Format log record as JSON.
        
        Args:
            record: LogRecord instance
            
        Returns:
            JSON string with timestamp, level, component, message, and optional metrics
        """
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "component": getattr(record, 'component', 'unknown'),
            "message": record.getMessage(),
        }
        
        # Add metrics if present
        if hasattr(record, 'metrics') and record.metrics:
            log_data["metrics"] = record.metrics
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'created', 'filename', 'funcName', 
                          'levelname', 'levelno', 'lineno', 'module', 'msecs', 
                          'message', 'pathname', 'process', 'processName', 'relativeCreated',
                          'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                          'component', 'metrics']:
                log_data[key] = value
        
        return json.dumps(log_data)


class CompressingTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    TimedRotatingFileHandler that compresses rotated files with gzip.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namer = self._custom_namer
        self.rotator = self._custom_rotator
    
    def _custom_namer(self, default_name):
        """Add .gz extension to rotated files."""
        return default_name + ".gz"
    
    def _custom_rotator(self, source, dest):
        """Compress the rotated file with gzip."""
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                f_out.writelines(f_in)
        os.remove(source)


class SizeAwareTimedRotatingFileHandler(CompressingTimedRotatingFileHandler):
    """
    Combines timed rotation with size-based rotation.
    Rotates daily OR when file reaches max size.
    """
    
    def __init__(self, filename, when='midnight', interval=1, 
                 backupCount=0, maxBytes=0, **kwargs):
        super().__init__(filename, when=when, interval=interval, 
                        backupCount=backupCount, **kwargs)
        self.maxBytes = maxBytes
    
    def shouldRollover(self, record):
        """
        Check if rollover should occur.
        Returns True if time-based OR size-based threshold is exceeded.
        """
        # Check time-based rotation first
        if super().shouldRollover(record):
            return True
        
        # Check size-based rotation
        if self.maxBytes > 0:
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # Go to end of file
            if self.stream.tell() + len(msg.encode('utf-8')) >= self.maxBytes:
                return True
        
        return False


class ComponentLogger(logging.LoggerAdapter):
    """
    Logger adapter that adds component name and supports metrics.
    """
    
    def __init__(self, logger, component):
        super().__init__(logger, {'component': component})
        self.component = component
    
    def process(self, msg, kwargs):
        """Add component to extra fields."""
        extra = kwargs.get('extra', {})
        extra['component'] = self.component
        
        # Handle metrics parameter
        if 'metrics' in kwargs:
            extra['metrics'] = kwargs.pop('metrics')
        
        # Handle exception parameter
        if 'exception' in kwargs:
            exc = kwargs.pop('exception')
            kwargs['exc_info'] = (type(exc), exc, exc.__traceback__)
        
        kwargs['extra'] = extra
        return msg, kwargs


def setup_logging(log_dir=None):
    """
    Set up the logging infrastructure.
    
    Args:
        log_dir: Directory for log files (default: logs/)
    """
    if log_dir is None:
        log_dir = LOG_DIR
    
    # Create log directory if it doesn't exist
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True)
    
    # Create handler with rotation
    log_file = log_dir / "polymarket.log"
    handler = SizeAwareTimedRotatingFileHandler(
        filename=str(log_file),
        when='midnight',
        interval=1,
        backupCount=BACKUP_COUNT,
        maxBytes=MAX_BYTES,
        encoding='utf-8'
    )
    
    # Set formatter
    handler.setFormatter(JSONFormatter())
    
    return handler


def get_logger(component_name, level=logging.INFO, log_dir=None):
    """
    Get or create a logger for a specific component.
    
    Thread-safe logger creation with caching.
    
    Args:
        component_name: Name of the component (e.g., "data-collector", "strategy-engine")
        level: Logging level (default: INFO)
        log_dir: Custom log directory (default: logs/)
    
    Returns:
        ComponentLogger instance
    
    Example:
        >>> logger = get_logger("data-collector")
        >>> logger.info("Started data collection")
        >>> logger.info("Fetched markets", metrics={"count": 15, "latency_ms": 234})
        >>> logger.error("API request failed", exception=e)
    """
    cache_key = (component_name, log_dir or str(LOG_DIR))
    
    with _cache_lock:
        if cache_key in _logger_cache:
            return _logger_cache[cache_key]
        
        # Create base logger
        logger_name = f"polymarket.{component_name}"
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.propagate = False
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Add our custom handler
        handler = setup_logging(log_dir)
        logger.addHandler(handler)
        
        # Create component logger
        component_logger = ComponentLogger(logger, component_name)
        
        # Cache it
        _logger_cache[cache_key] = component_logger
        
        return component_logger


def parse_time_range(time_str):
    """
    Parse time range string like "24h", "7d", "30m".
    
    Args:
        time_str: Time range string (e.g., "24h", "7d", "30m")
    
    Returns:
        timedelta object
    """
    match = re.match(r'(\d+)([hdm])', time_str.lower())
    if not match:
        raise ValueError(f"Invalid time range: {time_str}. Use format like '24h', '7d', '30m'")
    
    value, unit = match.groups()
    value = int(value)
    
    if unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    elif unit == 'm':
        return timedelta(minutes=value)


def read_log_file(file_path):
    """
    Read and parse a log file (handles both plain and gzipped files).
    
    Args:
        file_path: Path to log file
    
    Yields:
        Parsed log entries (dict)
    """
    if file_path.endswith('.gz'):
        opener = gzip.open
    else:
        opener = open
    
    try:
        with opener(file_path, 'rt', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


def search_logs(search_term=None, component=None, level=None, time_range=None, log_dir=None):
    """
    Search through log files.
    
    Args:
        search_term: Text to search for in messages
        component: Filter by component name
        level: Filter by log level
        time_range: timedelta for how far back to search
        log_dir: Log directory (default: logs/)
    
    Returns:
        List of matching log entries
    """
    if log_dir is None:
        log_dir = LOG_DIR
    
    log_dir = Path(log_dir)
    if not log_dir.exists():
        return []
    
    # Get all log files
    log_files = []
    log_files.extend(glob.glob(str(log_dir / "*.log")))
    log_files.extend(glob.glob(str(log_dir / "*.log.*.gz")))
    
    # Sort by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # Calculate cutoff time if time_range specified
    cutoff_time = None
    if time_range:
        cutoff_time = datetime.now() - time_range
    
    results = []
    
    for log_file in log_files:
        for entry in read_log_file(log_file):
            # Filter by time range
            if cutoff_time:
                entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
                if entry_time < cutoff_time:
                    continue
            
            # Filter by component
            if component and entry.get('component') != component:
                continue
            
            # Filter by level
            if level and entry.get('level') != level.upper():
                continue
            
            # Filter by search term
            if search_term:
                message = entry.get('message', '').lower()
                if search_term.lower() not in message:
                    continue
            
            results.append(entry)
    
    return results


def generate_summary(date=None, log_dir=None):
    """
    Generate a daily summary of log activity.
    
    Args:
        date: Date to summarize (default: today)
        log_dir: Log directory (default: logs/)
    
    Returns:
        Dictionary with summary statistics
    """
    if date is None:
        date = datetime.now().date()
    elif isinstance(date, str):
        date = datetime.fromisoformat(date).date()
    
    # Search for logs from that day
    start_time = datetime.combine(date, datetime.min.time())
    end_time = datetime.combine(date, datetime.max.time())
    
    if log_dir is None:
        log_dir = LOG_DIR
    
    log_dir = Path(log_dir)
    if not log_dir.exists():
        return {}
    
    # Get all log files
    log_files = []
    log_files.extend(glob.glob(str(log_dir / "*.log")))
    log_files.extend(glob.glob(str(log_dir / "*.log.*.gz")))
    
    # Statistics
    stats = {
        'date': str(date),
        'total_logs': 0,
        'by_level': defaultdict(int),
        'by_component': defaultdict(int),
        'errors': [],
        'performance_metrics': {
            'api_latency_ms': [],
            'db_latency_ms': [],
            'memory_mb': []
        }
    }
    
    for log_file in log_files:
        for entry in read_log_file(log_file):
            # Check if entry is from target date
            entry_time = datetime.fromisoformat(entry.get('timestamp', ''))
            if not (start_time <= entry_time <= end_time):
                continue
            
            stats['total_logs'] += 1
            stats['by_level'][entry.get('level', 'UNKNOWN')] += 1
            stats['by_component'][entry.get('component', 'unknown')] += 1
            
            # Collect errors
            if entry.get('level') == 'ERROR' or entry.get('level') == 'CRITICAL':
                stats['errors'].append({
                    'timestamp': entry.get('timestamp'),
                    'component': entry.get('component'),
                    'message': entry.get('message')
                })
            
            # Collect performance metrics
            metrics = entry.get('metrics', {})
            if 'latency_ms' in metrics:
                if 'api' in entry.get('message', '').lower():
                    stats['performance_metrics']['api_latency_ms'].append(metrics['latency_ms'])
                elif 'db' in entry.get('message', '').lower() or 'database' in entry.get('message', '').lower():
                    stats['performance_metrics']['db_latency_ms'].append(metrics['latency_ms'])
            
            if 'memory_mb' in metrics:
                stats['performance_metrics']['memory_mb'].append(metrics['memory_mb'])
    
    # Calculate averages for performance metrics
    for metric_name, values in stats['performance_metrics'].items():
        if values:
            stats['performance_metrics'][metric_name] = {
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values)
            }
        else:
            stats['performance_metrics'][metric_name] = None
    
    # Convert defaultdicts to regular dicts
    stats['by_level'] = dict(stats['by_level'])
    stats['by_component'] = dict(stats['by_component'])
    
    return stats


def print_summary(stats):
    """Pretty print summary statistics."""
    print(f"\n{'='*60}")
    print(f"  Log Summary for {stats['date']}")
    print(f"{'='*60}\n")
    
    print(f"Total Logs: {stats['total_logs']}\n")
    
    print("By Level:")
    for level, count in sorted(stats['by_level'].items()):
        print(f"  {level:10s}: {count:5d}")
    print()
    
    print("By Component:")
    for component, count in sorted(stats['by_component'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {component:20s}: {count:5d}")
    print()
    
    if stats['errors']:
        print(f"Errors/Critical ({len(stats['errors'])}):")
        for error in stats['errors'][:10]:  # Show first 10
            print(f"  [{error['timestamp']}] {error['component']}: {error['message']}")
        if len(stats['errors']) > 10:
            print(f"  ... and {len(stats['errors']) - 10} more")
        print()
    
    print("Performance Metrics:")
    for metric_name, data in stats['performance_metrics'].items():
        if data:
            print(f"  {metric_name}:")
            print(f"    avg: {data['avg']:.2f}")
            print(f"    min: {data['min']:.2f}")
            print(f"    max: {data['max']:.2f}")
            print(f"    samples: {data['count']}")
        else:
            print(f"  {metric_name}: no data")
    
    print()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Advanced Logging System - Search and analyze Polymarket trading logs',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Search for errors in data-collector:
    python advanced-logger.py --search "ERROR" --component "data-collector"
  
  View today's summary:
    python advanced-logger.py --summary
  
  Search last 24 hours:
    python advanced-logger.py --search "API" --last 24h
  
  Summary for specific date:
    python advanced-logger.py --summary --date 2026-02-05
        """
    )
    
    parser.add_argument('--search', type=str, help='Search term to find in log messages')
    parser.add_argument('--component', type=str, help='Filter by component name')
    parser.add_argument('--level', type=str, help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--last', type=str, help='Time range to search (e.g., "24h", "7d", "30m")')
    parser.add_argument('--summary', action='store_true', help='Generate daily summary')
    parser.add_argument('--date', type=str, help='Date for summary (YYYY-MM-DD, default: today)')
    parser.add_argument('--log-dir', type=str, default=str(LOG_DIR), help=f'Log directory (default: {LOG_DIR})')
    
    args = parser.parse_args()
    
    if args.summary:
        # Generate summary
        date = args.date if args.date else None
        stats = generate_summary(date=date, log_dir=args.log_dir)
        print_summary(stats)
    
    else:
        # Search logs
        time_range = None
        if args.last:
            time_range = parse_time_range(args.last)
        
        results = search_logs(
            search_term=args.search,
            component=args.component,
            level=args.level,
            time_range=time_range,
            log_dir=args.log_dir
        )
        
        if not results:
            print("No matching logs found.")
        else:
            print(f"Found {len(results)} matching log entries:\n")
            for entry in results:
                print(json.dumps(entry, indent=2))
                print()


if __name__ == '__main__':
    main()
