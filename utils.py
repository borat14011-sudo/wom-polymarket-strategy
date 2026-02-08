import logging
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import asyncio
import aiofiles
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows
init(autoreset=True)

class Logger:
    """Enhanced logging system with colored output and file logging"""
    
    def __init__(self, name: str, log_file: str = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler with colors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(ColoredFormatter())
        self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA + Style.BRIGHT
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname}{Style.RESET_ALL}"
        return super().format(record)

class DataStorage:
    """Utility class for data storage and retrieval"""
    
    @staticmethod
    async def save_market_data(markets: List[Dict], filename: str = None):
        """Save market data to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"market_data_{timestamp}.json"
        
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(markets, indent=2, default=str))
            return filepath
        except Exception as e:
            logging.error(f"Error saving market data: {str(e)}")
            return None
    
    @staticmethod
    async def load_market_data(filename: str) -> List[Dict]:
        """Load market data from JSON file"""
        filepath = os.path.join(DATA_DIR, filename)
        
        try:
            async with aiofiles.open(filepath, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
        except Exception as e:
            logging.error(f"Error loading market data: {str(e)}")
            return []
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """Format amount as currency"""
        if amount >= 1000000:
            return f"${amount/1000000:.1f}M"
        elif amount >= 1000:
            return f"${amount/1000:.1f}K"
        else:
            return f"${amount:.2f}"
    
    @staticmethod
    def format_percentage(value: float) -> str:
        """Format value as percentage"""
        return f"{value:.2f}%"
    
    @staticmethod
    def format_price(price: float) -> str:
        """Format price (0-1) as percentage"""
        return f"{price*100:.1f}%"

class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(self):
        self.logger = Logger(__name__).logger
        self.alerts = []
    
    def add_price_alert(self, market_id: str, market_title: str, 
                       old_price: float, new_price: float, threshold: float):
        """Add price change alert"""
        price_change = abs(new_price - old_price) / old_price if old_price > 0 else 0
        
        if price_change >= threshold:
            alert = {
                'type': 'price_change',
                'market_id': market_id,
                'market_title': market_title,
                'old_price': old_price,
                'new_price': new_price,
                'price_change': price_change,
                'timestamp': datetime.now().isoformat(),
                'message': f"Price change of {price_change*100:.2f}% detected for '{market_title}'"
            }
            
            self.alerts.append(alert)
            self.logger.warning(f"🚨 PRICE ALERT: {alert['message']}")
    
    def add_volume_alert(self, market_id: str, market_title: str, 
                        old_volume: float, new_volume: float):
        """Add volume spike alert"""
        volume_change = abs(new_volume - old_volume) / old_volume if old_volume > 0 else 0
        
        if volume_change >= 0.5:  # 50% volume change
            alert = {
                'type': 'volume_spike',
                'market_id': market_id,
                'market_title': market_title,
                'old_volume': old_volume,
                'new_volume': new_volume,
                'volume_change': volume_change,
                'timestamp': datetime.now().isoformat(),
                'message': f"Volume spike of {volume_change*100:.1f}% detected for '{market_title}'"
            }
            
            self.alerts.append(alert)
            self.logger.warning(f"📈 VOLUME ALERT: {alert['message']}")
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict]:
        """Get alerts from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_alerts = []
        
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time >= cutoff_time:
                recent_alerts.append(alert)
        
        return recent_alerts
    
    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than N days"""
        cutoff_time = datetime.now() - timedelta(days=days)
        self.alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert['timestamp']) >= cutoff_time
        ]

class PerformanceTracker:
    """Track system performance metrics"""
    
    def __init__(self):
        self.metrics = {
            'api_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'markets_processed': 0,
            'alerts_generated': 0,
            'start_time': datetime.now(),
            'last_update': datetime.now()
        }
    
    def record_api_call(self, success: bool):
        """Record API call result"""
        self.metrics['api_calls'] += 1
        if success:
            self.metrics['successful_calls'] += 1
        else:
            self.metrics['failed_calls'] += 1
        self.metrics['last_update'] = datetime.now()
    
    def record_markets_processed(self, count: int):
        """Record number of markets processed"""
        self.metrics['markets_processed'] += count
        self.metrics['last_update'] = datetime.now()
    
    def record_alert(self):
        """Record alert generation"""
        self.metrics['alerts_generated'] += 1
        self.metrics['last_update'] = datetime.now()
    
    def get_metrics(self) -> Dict:
        """Get current metrics"""
        runtime = datetime.now() - self.metrics['start_time']
        return {
            **self.metrics,
            'runtime_seconds': runtime.total_seconds(),
            'success_rate': (
                self.metrics['successful_calls'] / self.metrics['api_calls'] * 100
                if self.metrics['api_calls'] > 0 else 0
            )
        }

# Import at the end to avoid circular imports
from config import *