#!/usr/bin/env python3
"""
🚀 POLYMARKET HYPE TRADING SYSTEM - CLI
Beautiful command-line interface with colors and interactivity
"""

import sys
import os
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading


# ============================================================================
# COLOR UTILITIES - ANSI Escape Codes
# ============================================================================

class Colors:
    """ANSI color codes for cross-platform terminal colors"""
    # Basic colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    BG_CYAN = '\033[106m'
    
    # Reset
    RESET = '\033[0m'
    
    @staticmethod
    def strip(text: str) -> str:
        """Remove all ANSI codes from text"""
        import re
        return re.sub(r'\033\[[0-9;]+m', '', text)


def colorize(text: str, color: str, bold: bool = False) -> str:
    """Apply color to text"""
    prefix = Colors.BOLD if bold else ''
    return f"{prefix}{color}{text}{Colors.RESET}"


def success(text: str) -> str:
    return colorize(text, Colors.GREEN, bold=True)

def error(text: str) -> str:
    return colorize(text, Colors.RED, bold=True)

def warning(text: str) -> str:
    return colorize(text, Colors.YELLOW)

def info(text: str) -> str:
    return colorize(text, Colors.BLUE)

def header(text: str) -> str:
    return colorize(text, Colors.CYAN, bold=True)


# ============================================================================
# TERMINAL UTILITIES
# ============================================================================

def clear_screen():
    """Clear terminal screen (cross-platform)"""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_terminal_width() -> int:
    """Get terminal width"""
    try:
        return os.get_terminal_size().columns
    except:
        return 80


def print_separator(char='═', color=Colors.CYAN):
    """Print a horizontal separator"""
    width = get_terminal_width()
    print(colorize(char * width, color))


def print_box(title: str, content: List[str], width: int = 60):
    """Print content in a box"""
    print(colorize('┌' + '─' * (width - 2) + '┐', Colors.CYAN))
    print(colorize('│', Colors.CYAN) + header(f" {title} ".center(width - 2)) + colorize('│', Colors.CYAN))
    print(colorize('├' + '─' * (width - 2) + '┤', Colors.CYAN))
    for line in content:
        # Pad line to fit box
        stripped = Colors.strip(line)
        padding = width - 2 - len(stripped)
        print(colorize('│', Colors.CYAN) + line + ' ' * padding + colorize('│', Colors.CYAN))
    print(colorize('└' + '─' * (width - 2) + '┘', Colors.CYAN))


# ============================================================================
# PROGRESS BAR
# ============================================================================

class ProgressBar:
    """Beautiful progress bar with percentage"""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.current = 0
        self.prefix = prefix
        self.width = width
        self.start_time = time.time()
    
    def update(self, current: int):
        """Update progress"""
        self.current = current
        self.display()
    
    def increment(self):
        """Increment by 1"""
        self.current += 1
        self.display()
    
    def display(self):
        """Display the progress bar"""
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        bar = '█' * filled + '░' * (self.width - filled)
        
        # Color based on progress
        if percent < 0.5:
            bar_color = Colors.RED
        elif percent < 0.8:
            bar_color = Colors.YELLOW
        else:
            bar_color = Colors.GREEN
        
        # Calculate ETA
        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {int(eta)}s"
        else:
            eta_str = "ETA: --"
        
        # Print progress bar
        sys.stdout.write(f'\r{self.prefix} {colorize(bar, bar_color)} {percent*100:5.1f}% ({self.current}/{self.total}) {Colors.GRAY}{eta_str}{Colors.RESET}')
        sys.stdout.flush()
        
        if self.current >= self.total:
            print()  # New line when complete


# ============================================================================
# SPINNER
# ============================================================================

class Spinner:
    """Loading spinner for async operations"""
    
    def __init__(self, message: str = "Loading"):
        self.message = message
        self.spinning = False
        self.thread = None
        self.frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.frame_index = 0
    
    def spin(self):
        """Spin animation"""
        while self.spinning:
            frame = self.frames[self.frame_index % len(self.frames)]
            sys.stdout.write(f'\r{colorize(frame, Colors.CYAN)} {self.message}...')
            sys.stdout.flush()
            self.frame_index += 1
            time.sleep(0.1)
    
    def start(self):
        """Start spinner"""
        self.spinning = True
        self.thread = threading.Thread(target=self.spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, final_message: Optional[str] = None):
        """Stop spinner"""
        self.spinning = False
        if self.thread:
            self.thread.join()
        sys.stdout.write('\r' + ' ' * (len(self.message) + 20) + '\r')
        if final_message:
            print(final_message)
        sys.stdout.flush()


# ============================================================================
# ASCII CHARTS
# ============================================================================

def ascii_line_chart(data: List[float], width: int = 60, height: int = 10) -> List[str]:
    """Generate ASCII line chart"""
    if not data:
        return ["No data"]
    
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val if max_val > min_val else 1
    
    # Normalize data to height
    normalized = [int((v - min_val) / range_val * (height - 1)) for v in data]
    
    # Sample data to fit width
    if len(normalized) > width:
        step = len(normalized) / width
        normalized = [normalized[int(i * step)] for i in range(width)]
    
    # Build chart
    chart = []
    for row in range(height - 1, -1, -1):
        line = ""
        for val in normalized:
            if val == row:
                line += colorize('●', Colors.CYAN)
            elif val > row:
                line += colorize('│', Colors.BLUE)
            else:
                line += ' '
        
        # Add value scale
        value = min_val + (row / (height - 1)) * range_val
        line = f"{value:6.2f} {colorize('┤', Colors.GRAY)}{line}"
        chart.append(line)
    
    # Add bottom axis
    chart.append("       " + colorize('└' + '─' * len(normalized), Colors.GRAY))
    
    return chart


def ascii_sparkline(data: List[float], width: int = 20) -> str:
    """Generate compact ASCII sparkline"""
    if not data:
        return "─" * width
    
    chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
    min_val = min(data)
    max_val = max(data)
    range_val = max_val - min_val if max_val > min_val else 1
    
    # Sample data to fit width
    if len(data) > width:
        step = len(data) / width
        data = [data[int(i * step)] for i in range(width)]
    
    sparkline = ""
    for val in data:
        normalized = (val - min_val) / range_val
        char_index = min(int(normalized * len(chars)), len(chars) - 1)
        
        # Color based on trend
        if val > (min_val + max_val) / 2:
            sparkline += colorize(chars[char_index], Colors.GREEN)
        else:
            sparkline += colorize(chars[char_index], Colors.RED)
    
    return sparkline


# ============================================================================
# TABLE FORMATTER
# ============================================================================

def format_table(headers: List[str], rows: List[List[str]], align: Optional[List[str]] = None) -> List[str]:
    """Format data as a table"""
    if not align:
        align = ['left'] * len(headers)
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            # Strip ANSI codes for width calculation
            cell_len = len(Colors.strip(str(cell)))
            col_widths[i] = max(col_widths[i], cell_len)
    
    # Add padding
    col_widths = [w + 2 for w in col_widths]
    
    # Build table
    table = []
    
    # Header
    header_row = colorize('│', Colors.CYAN)
    for i, h in enumerate(headers):
        header_row += ' ' + colorize(h.ljust(col_widths[i] - 1), Colors.CYAN, bold=True) + colorize('│', Colors.CYAN)
    table.append(header_row)
    
    # Top border
    top_border = colorize('┌', Colors.CYAN)
    for w in col_widths:
        top_border += colorize('─' * w + '┬', Colors.CYAN)
    top_border = top_border[:-len('┬')] + colorize('┐', Colors.CYAN)
    table.insert(0, top_border)
    
    # Separator
    separator = colorize('├', Colors.CYAN)
    for w in col_widths:
        separator += colorize('─' * w + '┼', Colors.CYAN)
    separator = separator[:-len('┼')] + colorize('┤', Colors.CYAN)
    table.append(separator)
    
    # Rows
    for row in rows:
        row_str = colorize('│', Colors.CYAN)
        for i, cell in enumerate(row):
            cell_str = str(cell)
            stripped = Colors.strip(cell_str)
            padding = col_widths[i] - 1 - len(stripped)
            
            if align[i] == 'right':
                row_str += ' ' * padding + ' ' + cell_str + colorize('│', Colors.CYAN)
            else:
                row_str += ' ' + cell_str + ' ' * padding + colorize('│', Colors.CYAN)
        table.append(row_str)
    
    # Bottom border
    bottom_border = colorize('└', Colors.CYAN)
    for w in col_widths:
        bottom_border += colorize('─' * w + '┴', Colors.CYAN)
    bottom_border = bottom_border[:-len('┴')] + colorize('┘', Colors.CYAN)
    table.append(bottom_border)
    
    return table


# ============================================================================
# MOCK DATA GENERATORS (for demonstration)
# ============================================================================

def get_system_status() -> Dict:
    """Get mock system status"""
    return {
        'running': True,
        'uptime': 3600 * 12 + 1234,
        'components': {
            'Data Collector': 'healthy',
            'Signal Generator': 'healthy',
            'Risk Manager': 'healthy',
            'Order Executor': 'warning',
            'API Connection': 'healthy'
        },
        'last_update': datetime.now()
    }


def get_active_signals() -> List[Dict]:
    """Get mock active signals"""
    return [
        {
            'market': 'Trump wins 2024',
            'signal': 'BUY',
            'confidence': 0.82,
            'price': 0.45,
            'target': 0.55,
            'trend': 'up',
            'volume_surge': 245
        },
        {
            'market': 'Bitcoin $100k by EOY',
            'signal': 'SELL',
            'confidence': 0.67,
            'price': 0.72,
            'target': 0.65,
            'trend': 'down',
            'volume_surge': 180
        },
        {
            'market': 'AI discovers cure',
            'signal': 'HOLD',
            'confidence': 0.45,
            'price': 0.33,
            'target': 0.35,
            'trend': 'sideways',
            'volume_surge': 95
        }
    ]


def get_portfolio() -> Dict:
    """Get mock portfolio data"""
    return {
        'balance': 10000.00,
        'positions': [
            {'market': 'Trump wins 2024', 'shares': 100, 'avg_price': 0.42, 'current_price': 0.45, 'pnl': 300},
            {'market': 'ETH above $4k', 'shares': 200, 'avg_price': 0.58, 'current_price': 0.55, 'pnl': -600},
        ],
        'total_pnl': -300,
        'day_pnl': 150,
        'win_rate': 0.58
    }


def get_recent_trades() -> List[Dict]:
    """Get mock recent trades"""
    base_time = datetime.now()
    return [
        {
            'time': base_time - timedelta(minutes=5),
            'market': 'Trump wins 2024',
            'action': 'BUY',
            'shares': 50,
            'price': 0.44,
            'pnl': 0
        },
        {
            'time': base_time - timedelta(minutes=15),
            'market': 'Bitcoin $100k',
            'action': 'SELL',
            'shares': 75,
            'price': 0.71,
            'pnl': 450
        },
        {
            'time': base_time - timedelta(hours=1),
            'market': 'ETH above $4k',
            'action': 'BUY',
            'shares': 100,
            'price': 0.59,
            'pnl': 0
        }
    ]


def get_performance_data() -> Dict:
    """Get mock performance data"""
    # Generate price history
    import random
    base_value = 10000
    prices = [base_value]
    for _ in range(100):
        change = random.uniform(-200, 250)
        prices.append(prices[-1] + change)
    
    return {
        'prices': prices,
        'total_return': (prices[-1] - prices[0]) / prices[0],
        'sharpe_ratio': 1.85,
        'max_drawdown': -0.12,
        'win_rate': 0.62,
        'total_trades': 247,
        'avg_profit': 125.50
    }


# ============================================================================
# DASHBOARD
# ============================================================================

def display_dashboard():
    """Display the main dashboard"""
    clear_screen()
    
    # Header
    print()
    print(colorize('  🚀 POLYMARKET HYPE TRADING SYSTEM  ', Colors.BG_CYAN + Colors.BOLD))
    print_separator()
    print()
    
    # Get data
    status = get_system_status()
    portfolio = get_portfolio()
    signals = get_active_signals()
    perf = get_performance_data()
    
    # System Status Section
    uptime_hours = status['uptime'] // 3600
    uptime_mins = (status['uptime'] % 3600) // 60
    
    status_emoji = success('✓ RUNNING') if status['running'] else error('✗ STOPPED')
    
    print(header('  SYSTEM STATUS'))
    print(f"  Status: {status_emoji}")
    print(f"  Uptime: {colorize(f'{uptime_hours}h {uptime_mins}m', Colors.CYAN)}")
    print(f"  Updated: {colorize(status['last_update'].strftime('%H:%M:%S'), Colors.GRAY)}")
    print()
    
    # Components Health
    print(header('  COMPONENTS'))
    for component, health in status['components'].items():
        if health == 'healthy':
            icon = success('●')
        elif health == 'warning':
            icon = warning('●')
        else:
            icon = error('●')
        print(f"  {icon} {component.ljust(20)} {health}")
    print()
    
    # Portfolio Summary
    pnl_color = Colors.GREEN if portfolio['total_pnl'] >= 0 else Colors.RED
    day_pnl_color = Colors.GREEN if portfolio['day_pnl'] >= 0 else Colors.RED
    
    print(header('  PORTFOLIO'))
    print(f"  Balance:      ${portfolio['balance']:,.2f}")
    print(f"  Total P&L:    {colorize(f'${portfolio["total_pnl"]:+,.2f}', pnl_color, bold=True)}")
    print(f"  Today P&L:    {colorize(f'${portfolio["day_pnl"]:+,.2f}', day_pnl_color)}")
    print(f"  Win Rate:     {colorize(f'{portfolio["win_rate"]*100:.1f}%', Colors.CYAN)}")
    print()
    
    # Active Signals
    print(header('  ACTIVE SIGNALS'))
    for signal in signals[:3]:
        signal_color = Colors.GREEN if signal['signal'] == 'BUY' else Colors.RED if signal['signal'] == 'SELL' else Colors.YELLOW
        confidence_bar = '█' * int(signal['confidence'] * 10)
        
        print(f"  {colorize(signal['signal'].ljust(4), signal_color, bold=True)} {signal['market'][:30].ljust(30)}")
        print(f"       Confidence: {colorize(confidence_bar, signal_color)} {signal['confidence']*100:.0f}%")
        print(f"       Price: ${signal['price']:.2f} → Target: ${signal['target']:.2f} | Volume: +{signal['volume_surge']}%")
    print()
    
    # Performance Chart
    print(header('  PORTFOLIO VALUE (Last 100 Updates)'))
    chart = ascii_line_chart(perf['prices'][-50:], width=70, height=8)
    for line in chart:
        print(f"  {line}")
    print()
    
    # Quick Stats
    return_color = Colors.GREEN if perf['total_return'] >= 0 else Colors.RED
    print(header('  PERFORMANCE METRICS'))
    print(f"  Total Return:   {colorize(f'{perf["total_return"]*100:+.2f}%', return_color, bold=True)}")
    print(f"  Sharpe Ratio:   {colorize(f'{perf["sharpe_ratio"]:.2f}', Colors.CYAN)}")
    print(f"  Max Drawdown:   {colorize(f'{perf["max_drawdown"]*100:.1f}%', Colors.RED)}")
    print(f"  Total Trades:   {colorize(str(perf['total_trades']), Colors.BLUE)}")
    print()
    
    print_separator('─', Colors.GRAY)
    print(colorize(f'  Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', Colors.GRAY))
    print()


# ============================================================================
# MENU SYSTEM
# ============================================================================

def show_menu():
    """Display main menu"""
    clear_screen()
    print()
    print(colorize('  ' + '=' * 60, Colors.CYAN))
    print(header('        🚀 POLYMARKET HYPE TRADING SYSTEM'))
    print(colorize('  ' + '=' * 60, Colors.CYAN))
    print()
    print(f"  {colorize('[1]', Colors.CYAN, bold=True)} 📊 System Status")
    print(f"  {colorize('[2]', Colors.CYAN, bold=True)} 🚀 Start System")
    print(f"  {colorize('[3]', Colors.CYAN, bold=True)} 🛑 Stop System")
    print(f"  {colorize('[4]', Colors.CYAN, bold=True)} 📈 View Signals")
    print(f"  {colorize('[5]', Colors.CYAN, bold=True)} 💰 Portfolio")
    print(f"  {colorize('[6]', Colors.CYAN, bold=True)} 📉 Performance")
    print(f"  {colorize('[7]', Colors.CYAN, bold=True)} ⚙️  Settings")
    print(f"  {colorize('[8]', Colors.CYAN, bold=True)} 📝 Logs")
    print(f"  {colorize('[9]', Colors.CYAN, bold=True)} ❓ Help")
    print(f"  {colorize('[0]', Colors.CYAN, bold=True)} 🚪 Exit")
    print()
    print(colorize('  ' + '─' * 60, Colors.GRAY))
    print()


def handle_status():
    """Handle status command"""
    spinner = Spinner("Loading system status")
    spinner.start()
    time.sleep(1.5)
    spinner.stop()
    
    display_dashboard()
    input(colorize("\n  Press Enter to continue...", Colors.GRAY))


def handle_signals():
    """Handle signals command"""
    clear_screen()
    print()
    print(header('  📈 ACTIVE TRADING SIGNALS'))
    print_separator()
    print()
    
    signals = get_active_signals()
    
    # Create table
    headers = ['Market', 'Signal', 'Conf%', 'Price', 'Target', 'Volume', 'Trend']
    rows = []
    
    for sig in signals:
        signal_text = sig['signal']
        if sig['signal'] == 'BUY':
            signal_text = success(signal_text)
        elif sig['signal'] == 'SELL':
            signal_text = error(signal_text)
        else:
            signal_text = warning(signal_text)
        
        confidence = f"{sig['confidence']*100:.0f}%"
        if sig['confidence'] > 0.7:
            confidence = success(confidence)
        elif sig['confidence'] < 0.5:
            confidence = warning(confidence)
        
        trend = sig['trend']
        if trend == 'up':
            trend = colorize('↗ UP', Colors.GREEN)
        elif trend == 'down':
            trend = colorize('↘ DOWN', Colors.RED)
        else:
            trend = colorize('→ FLAT', Colors.YELLOW)
        
        rows.append([
            sig['market'][:25],
            signal_text,
            confidence,
            f"${sig['price']:.2f}",
            f"${sig['target']:.2f}",
            colorize(f"+{sig['volume_surge']}%", Colors.CYAN),
            trend
        ])
    
    table = format_table(headers, rows, align=['left', 'left', 'right', 'right', 'right', 'right', 'left'])
    for line in table:
        print(f"  {line}")
    
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_portfolio():
    """Handle portfolio command"""
    clear_screen()
    print()
    print(header('  💰 PORTFOLIO'))
    print_separator()
    print()
    
    portfolio = get_portfolio()
    
    # Summary
    pnl_color = Colors.GREEN if portfolio['total_pnl'] >= 0 else Colors.RED
    day_pnl_color = Colors.GREEN if portfolio['day_pnl'] >= 0 else Colors.RED
    
    print(f"  Balance:        ${portfolio['balance']:,.2f}")
    print(f"  Total P&L:      {colorize(f'${portfolio["total_pnl"]:+,.2f}', pnl_color, bold=True)}")
    print(f"  Today P&L:      {colorize(f'${portfolio["day_pnl"]:+,.2f}', day_pnl_color)}")
    print(f"  Win Rate:       {colorize(f'{portfolio["win_rate"]*100:.1f}%', Colors.CYAN)}")
    print()
    print(header('  POSITIONS'))
    print()
    
    # Positions table
    headers = ['Market', 'Shares', 'Avg Price', 'Current', 'P&L', 'Return%']
    rows = []
    
    for pos in portfolio['positions']:
        pnl = pos['pnl']
        pnl_pct = (pos['current_price'] - pos['avg_price']) / pos['avg_price'] * 100
        
        pnl_text = f"${pnl:+,.0f}"
        pnl_pct_text = f"{pnl_pct:+.1f}%"
        
        if pnl >= 0:
            pnl_text = success(pnl_text)
            pnl_pct_text = success(pnl_pct_text)
        else:
            pnl_text = error(pnl_text)
            pnl_pct_text = error(pnl_pct_text)
        
        rows.append([
            pos['market'][:25],
            str(pos['shares']),
            f"${pos['avg_price']:.2f}",
            f"${pos['current_price']:.2f}",
            pnl_text,
            pnl_pct_text
        ])
    
    table = format_table(headers, rows, align=['left', 'right', 'right', 'right', 'right', 'right'])
    for line in table:
        print(f"  {line}")
    
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_trades():
    """Handle recent trades command"""
    clear_screen()
    print()
    print(header('  📊 RECENT TRADES'))
    print_separator()
    print()
    
    trades = get_recent_trades()
    
    headers = ['Time', 'Market', 'Action', 'Shares', 'Price', 'P&L']
    rows = []
    
    for trade in trades:
        action = trade['action']
        if action == 'BUY':
            action_text = success(action)
        else:
            action_text = error(action)
        
        pnl = trade['pnl']
        if pnl > 0:
            pnl_text = success(f"${pnl:+,.0f}")
        elif pnl < 0:
            pnl_text = error(f"${pnl:+,.0f}")
        else:
            pnl_text = colorize('--', Colors.GRAY)
        
        rows.append([
            trade['time'].strftime('%H:%M:%S'),
            trade['market'][:25],
            action_text,
            str(trade['shares']),
            f"${trade['price']:.2f}",
            pnl_text
        ])
    
    table = format_table(headers, rows, align=['left', 'left', 'left', 'right', 'right', 'right'])
    for line in table:
        print(f"  {line}")
    
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_performance():
    """Handle performance command"""
    clear_screen()
    print()
    print(header('  📉 PERFORMANCE ANALYSIS'))
    print_separator()
    print()
    
    perf = get_performance_data()
    
    # Metrics
    return_color = Colors.GREEN if perf['total_return'] >= 0 else Colors.RED
    
    print(header('  KEY METRICS'))
    print(f"  Total Return:      {colorize(f'{perf["total_return"]*100:+.2f}%', return_color, bold=True)}")
    print(f"  Sharpe Ratio:      {colorize(f'{perf["sharpe_ratio"]:.2f}', Colors.CYAN)}")
    print(f"  Max Drawdown:      {colorize(f'{perf["max_drawdown"]*100:.1f}%', Colors.RED)}")
    print(f"  Win Rate:          {colorize(f'{perf["win_rate"]*100:.1f}%', Colors.GREEN)}")
    print(f"  Total Trades:      {colorize(str(perf['total_trades']), Colors.BLUE)}")
    print(f"  Avg Profit/Trade:  {colorize(f'${perf["avg_profit"]:.2f}', Colors.GREEN)}")
    print()
    
    # Portfolio value chart
    print(header('  PORTFOLIO VALUE OVER TIME'))
    print()
    chart = ascii_line_chart(perf['prices'], width=70, height=12)
    for line in chart:
        print(f"  {line}")
    print()
    
    # Sparkline summary
    print(header('  QUICK TREND'))
    sparkline = ascii_sparkline(perf['prices'], width=60)
    print(f"  {sparkline}")
    print()
    
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_start():
    """Handle start system command"""
    clear_screen()
    print()
    print(header('  🚀 STARTING TRADING SYSTEM'))
    print_separator()
    print()
    
    components = [
        'Initializing API connection',
        'Loading market data',
        'Starting signal generator',
        'Activating risk manager',
        'Launching order executor',
        'System ready'
    ]
    
    for i, component in enumerate(components, 1):
        spinner = Spinner(component)
        spinner.start()
        time.sleep(1.2)
        spinner.stop(success(f'  ✓ {component}'))
    
    print()
    print(success('  🎉 Trading system started successfully!'))
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_stop():
    """Handle stop system command"""
    clear_screen()
    print()
    print(header('  🛑 STOPPING TRADING SYSTEM'))
    print_separator()
    print()
    
    print(warning('  ⚠ This will close all positions and stop trading.'))
    confirm = input(colorize('  Are you sure? (yes/no): ', Colors.YELLOW))
    
    if confirm.lower() != 'yes':
        print(info('  Operation cancelled.'))
        time.sleep(1)
        return
    
    print()
    components = [
        'Closing open positions',
        'Stopping order executor',
        'Shutting down signal generator',
        'Saving state',
        'System stopped'
    ]
    
    progress = ProgressBar(len(components), prefix='  Shutting down')
    for i, component in enumerate(components):
        time.sleep(0.8)
        progress.update(i + 1)
    
    print()
    print(success('  ✓ Trading system stopped successfully.'))
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_settings():
    """Handle settings command"""
    clear_screen()
    print()
    print(header('  ⚙️  SYSTEM SETTINGS'))
    print_separator()
    print()
    
    settings = {
        'Max Position Size': '$2,500',
        'Risk Per Trade': '2.5%',
        'Stop Loss': '15%',
        'Take Profit': '25%',
        'Min Confidence': '65%',
        'Auto-Trade': 'Enabled',
        'Notifications': 'Enabled'
    }
    
    for key, value in settings.items():
        print(f"  {key.ljust(20)}: {colorize(value, Colors.CYAN)}")
    
    print()
    print(info('  💡 Use config file to modify settings: config.json'))
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_logs():
    """Handle logs command"""
    clear_screen()
    print()
    print(header('  📝 SYSTEM LOGS'))
    print_separator()
    print()
    
    logs = [
        ('2024-02-06 05:45:23', 'INFO', 'System started successfully'),
        ('2024-02-06 05:46:15', 'INFO', 'Connected to Polymarket API'),
        ('2024-02-06 05:47:02', 'SUCCESS', 'BUY signal: Trump wins 2024 @ $0.44'),
        ('2024-02-06 05:47:05', 'SUCCESS', 'Order filled: 50 shares @ $0.44'),
        ('2024-02-06 05:50:12', 'WARNING', 'High volatility detected on Bitcoin $100k'),
        ('2024-02-06 05:51:30', 'INFO', 'Portfolio rebalanced'),
        ('2024-02-06 05:52:00', 'INFO', 'Heartbeat: All systems operational'),
    ]
    
    for timestamp, level, message in logs:
        if level == 'INFO':
            level_text = info('[INFO]')
        elif level == 'SUCCESS':
            level_text = success('[SUCCESS]')
        elif level == 'WARNING':
            level_text = warning('[WARNING]')
        else:
            level_text = error('[ERROR]')
        
        print(f"  {colorize(timestamp, Colors.GRAY)} {level_text} {message}")
    
    print()
    print(info('  💡 Full logs: trading-system.log'))
    print()
    input(colorize("  Press Enter to continue...", Colors.GRAY))


def handle_help():
    """Handle help command"""
    clear_screen()
    print()
    print(header('  ❓ HELP & DOCUMENTATION'))
    print_separator()
    print()
    
    print(header('  COMMAND LINE USAGE'))
    print()
    print(f"  {colorize('python trading-cli.py', Colors.CYAN)}")
    print(f"    Interactive mode with main menu")
    print()
    print(f"  {colorize('python trading-cli.py status', Colors.CYAN)}")
    print(f"    Show system status dashboard")
    print()
    print(f"  {colorize('python trading-cli.py signals', Colors.CYAN)}")
    print(f"    Show active trading signals")
    print()
    print(f"  {colorize('python trading-cli.py portfolio', Colors.CYAN)}")
    print(f"    Show portfolio positions")
    print()
    print(f"  {colorize('python trading-cli.py trades', Colors.CYAN)}")
    print(f"    Show recent trades")
    print()
    print(f"  {colorize('python trading-cli.py pnl', Colors.CYAN)}")
    print(f"    Show P&L and performance")
    print()
    
    print(header('  KEY FEATURES'))
    print()
    print(f"  • {success('Real-time')} market signal detection")
    print(f"  • {success('Automated')} position management")
    print(f"  • {success('Risk controls')} with stop-loss")
    print(f"  • {success('Performance')} tracking & analytics")
    print()
    
    print(header('  SIGNAL TYPES'))
    print()
    print(f"  {success('BUY')}  - Strong upward momentum detected")
    print(f"  {error('SELL')} - Strong downward momentum detected")
    print(f"  {warning('HOLD')} - No clear signal, maintain position")
    print()
    
    input(colorize("  Press Enter to continue...", Colors.GRAY))


# ============================================================================
# MAIN INTERACTIVE LOOP
# ============================================================================

def interactive_mode():
    """Run interactive menu loop"""
    while True:
        show_menu()
        choice = input(colorize('  Select option: ', Colors.CYAN, bold=True))
        
        if choice == '1':
            handle_status()
        elif choice == '2':
            handle_start()
        elif choice == '3':
            handle_stop()
        elif choice == '4':
            handle_signals()
        elif choice == '5':
            handle_portfolio()
        elif choice == '6':
            handle_performance()
        elif choice == '7':
            handle_settings()
        elif choice == '8':
            handle_logs()
        elif choice == '9':
            handle_help()
        elif choice == '0':
            clear_screen()
            print()
            print(success('  👋 Thanks for using Polymarket Hype Trading System!'))
            print()
            sys.exit(0)
        else:
            print()
            print(error('  ✗ Invalid option. Please try again.'))
            time.sleep(1.5)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='🚀 Polymarket Hype Trading System CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python trading-cli.py              # Interactive mode
  python trading-cli.py status       # Show status
  python trading-cli.py signals      # Show signals
  python trading-cli.py trades       # Show trades
  python trading-cli.py pnl          # Show performance
        '''
    )
    
    parser.add_argument('command', nargs='?', choices=['status', 'signals', 'portfolio', 'trades', 'pnl', 'start', 'stop'],
                        help='Command to execute')
    
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'status':
        display_dashboard()
    elif args.command == 'signals':
        handle_signals()
    elif args.command == 'portfolio':
        handle_portfolio()
    elif args.command == 'trades':
        handle_trades()
    elif args.command == 'pnl':
        handle_performance()
    elif args.command == 'start':
        handle_start()
    elif args.command == 'stop':
        handle_stop()
    else:
        # No command = interactive mode
        interactive_mode()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print()
        print()
        print(warning('  ⚠ Interrupted by user'))
        print()
        sys.exit(0)
    except Exception as e:
        print()
        print(error(f'  ✗ Error: {str(e)}'))
        print()
        sys.exit(1)
