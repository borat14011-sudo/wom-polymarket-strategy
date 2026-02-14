"""
Main Trading Bot for Polymarket
Simple loop: scan → evaluate → trade → log
"""

import time
import schedule
from datetime import datetime
from typing import List, Optional

# Import bot components
from config import validate_config, PRIVATE_KEY, FUNDER_ADDRESS, INITIAL_CAPITAL
from config import MAX_POSITION_SIZE, MAX_TOTAL_EXPOSURE, MAX_CONCURRENT_POSITIONS
from market_scanner import MarketScanner, MarketOpportunity
from order_manager import OrderManager, Position
from risk_manager import RiskManager, RiskParameters
from trade_logger import TradeLogger, create_trade_record_from_order

# Import Polymarket client
try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import OrderArgs, OrderType
    from py_clob_client.order_builder.constants import BUY, SELL
    print("OK: Successfully imported py-clob-client")
except ImportError as e:
    print(f"ERROR: Failed to import py-clob-client: {e}")
    print("Install with: pip install py-clob-client==0.34.5 web3==6.14.0")
    exit(1)

class PolymarketTradingBot:
    """Main trading bot class"""
    
    def __init__(self):
        # Validate configuration
        try:
            validate_config()
            print("OK: Configuration validated")
        except ValueError as e:
            print(f"ERROR: Configuration error: {e}")
            exit(1)
        
        # Initialize components
        self.init_components()
        
        # State
        self.starting_capital = INITIAL_CAPITAL
        self.current_capital = INITIAL_CAPITAL
        self.cycle_count = 0
        self.total_trades = 0
        
        print("\n" + "="*70)
        print("POLYMARKET TRADING BOT INITIALIZED")
        print("="*70)
        print(f"Wallet: {FUNDER_ADDRESS[:10]}...")
        print(f"Capital: ${self.current_capital:.2f}")
        print(f"Max Position: ${MAX_POSITION_SIZE}")
        print(f"Max Exposure: ${MAX_TOTAL_EXPOSURE}")
        print(f"Max Positions: {MAX_CONCURRENT_POSITIONS}")
        print("="*70)
    
    def init_components(self):
        """Initialize all bot components"""
        print("\nInitializing components...")
        
        # Initialize Polymarket client
        print("  Initializing Polymarket client...")
        try:
            self.client = ClobClient(
                host="https://clob.polymarket.com",
                key=PRIVATE_KEY,
                chain_id=137,  # Polygon mainnet
                signature_type=1,  # Magic/email login
                funder=FUNDER_ADDRESS
            )
            
            # Generate API credentials
            self.client.set_api_creds(self.client.create_or_derive_api_creds())
            print("    OK: Client initialized")
            
            # Test connection
            server_time = self.client.get_server_time()
            print(f"    OK: Server time: {server_time}")
            
        except Exception as e:
            print(f"    ERROR: Client initialization failed: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure you've made at least one manual trade on polymarket.com")
            print("2. Verify private key from https://reveal.magic.link/polymarket")
            print("3. Check funder address at polymarket.com/settings")
            exit(1)
        
        # Initialize other components
        print("  Initializing Market Scanner...")
        self.scanner = MarketScanner(min_daily_volume=1000, scan_limit=50)
        
        print("  Initializing Order Manager...")
        self.order_manager = OrderManager(self.client)
        
        print("  Initializing Risk Manager...")
        risk_params = RiskParameters(
            max_position_size=MAX_POSITION_SIZE,
            max_total_exposure=MAX_TOTAL_EXPOSURE,
            max_concurrent_positions=MAX_CONCURRENT_POSITIONS
        )
        self.risk_manager = RiskManager(risk_params)
        
        print("  Initializing Trade Logger...")
        self.trade_logger = TradeLogger()
        
        print("OK: All components initialized")
    
    def get_current_positions(self) -> List[Position]:
        """Get current positions from order manager"""
        return self.order_manager.get_positions()
    
    def get_current_balance(self) -> Optional[float]:
        """Get current USDC balance"""
        return self.order_manager.get_balance()
    
    def update_capital(self):
        """Update current capital from balance and positions"""
        balance = self.get_current_balance()
        if balance is not None:
            self.current_capital = balance
            return True
        return False
    
    def scan_and_evaluate(self) -> List[MarketOpportunity]:
        """
        Scan for markets and evaluate opportunities
        Returns filtered list of tradeable opportunities
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Scanning markets...")
        
        # Scan for opportunities
        opportunities = self.scanner.scan_opportunities()
        
        if not opportunities:
            print("  No tradeable markets found")
            return []
        
        # Filter opportunities (simple strategy: high volume, recent activity)
        filtered_opps = []
        for opp in opportunities[:10]:  # Look at top 10 by liquidity
            # Add simple evaluation logic here
            # For now, just take top 3 by volume
            if len(filtered_opps) < 3:
                filtered_opps.append(opp)
        
        print(f"  Found {len(filtered_opps)} potential opportunities")
        return filtered_opps
    
    def execute_trade_cycle(self):
        """Execute one complete trade cycle"""
        self.cycle_count += 1
        print(f"\n{'='*70}")
        print(f"TRADE CYCLE #{self.cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")
        
        # Update capital
        if not self.update_capital():
            print("WARNING:  Could not update capital, using last known value")
        
        print(f"Current Capital: ${self.current_capital:.4f}")
        
        # Get current positions
        positions = self.get_current_positions()
        print(f"Current Positions: {len(positions)}")
        
        # Generate risk report
        self.risk_manager.print_risk_report(
            positions, self.current_capital, self.starting_capital
        )
        
        # Check circuit breaker
        circuit_triggered, _ = self.risk_manager.check_circuit_breaker(
            self.starting_capital, self.current_capital
        )
        
        if circuit_triggered:
            print("\nALERT: CIRCUIT BREAKER TRIGGERED - Stopping trading")
            # Cancel all open orders
            self.order_manager.cancel_all_orders()
            return
        
        # Scan for opportunities
        opportunities = self.scan_and_evaluate()
        
        if not opportunities:
            print("\nNo trade opportunities found")
            return
        
        # Evaluate each opportunity
        for opp in opportunities:
            print(f"\nEvaluating: {opp.question[:60]}...")
            
            # Simple strategy: Buy NO on high-probability markets (>80%)
            # This is just an example - replace with your actual strategy
            
            # Get midpoint price
            midpoint = self.order_manager.get_midpoint(opp.no_token_id)
            if midpoint is None:
                print("  Skipping: Could not get midpoint price")
                continue
            
            print(f"  NO Midpoint: ${midpoint:.4f} ({midpoint*100:.1f}%)")
            
            # Simple strategy: Buy NO if price < 0.20 (20%)
            if midpoint > 0.20:
                print(f"  Skipping: Price too high for NO position")
                continue
            
            # Calculate position size
            # For demo: use fixed $0.20 size
            trade_size = 0.20 / midpoint  # Number of shares for $0.20
            
            # Check if we can trade
            allowed, reason = self.risk_manager.can_trade(positions, 0.20)
            
            if not allowed:
                print(f"  Skipping: {reason}")
                continue
            
            # Place order
            print(f"  Placing order: BUY NO ${0.20:.4f} at ${midpoint:.4f}")
            
            result = self.order_manager.place_limit_order(
                token_id=opp.no_token_id,
                side="BUY",
                price=midpoint,
                size=trade_size
            )
            
            if result.success:
                print(f"  OK: Order placed: {result.order_id}")
                
                # Log the trade
                trade_record = create_trade_record_from_order(
                    market=opp.question,
                    token_id=opp.no_token_id,
                    side="BUY",
                    price=midpoint,
                    size=trade_size,
                    order_id=result.order_id
                )
                
                trade_id = self.trade_logger.log_trade(trade_record)
                self.total_trades += 1
                
                # Update positions list
                new_position = Position(
                    token_id=opp.no_token_id,
                    side="BUY",
                    price=midpoint,
                    size=trade_size,
                    cost=0.20,
                    order_id=result.order_id,
                    timestamp=time.time()
                )
                positions.append(new_position)
                
            else:
                print(f"  ERROR: Order failed: {result.error}")
        
        # Print trade statistics
        self.print_trade_stats()
    
    def print_trade_stats(self):
        """Print trading statistics"""
        stats = self.trade_logger.get_trade_stats()
        
        print(f"\n{'='*70}")
        print("TRADING STATISTICS")
        print(f"{'='*70}")
        
        print(f"\nTotal Trades: {stats['total_trades']}")
        print(f"Open Trades: {stats['open_trades']}")
        print(f"Closed Trades: {stats['closed_trades']}")
        
        if stats['closed_trades'] > 0:
            print(f"\nTotal P&L: ${stats['total_pnl']:.4f}")
            print(f"Average P&L: ${stats['avg_pnl']:.4f}")
            print(f"Win Rate: {stats['win_rate']:.1f}%")
        
        print(f"\nCycle Complete. Next cycle in 30 minutes.")
        print(f"{'='*70}")
    
    def run_once(self):
        """Run one trade cycle immediately"""
        try:
            self.execute_trade_cycle()
        except Exception as e:
            print(f"\nERROR: Error in trade cycle: {e}")
            import traceback
            traceback.print_exc()
    
    def run_scheduled(self, interval_minutes: int = 30):
        """
        Run bot on a schedule
        
        Args:
            interval_minutes: Minutes between trade cycles
        """
        print(f"\nStarting scheduled trading every {interval_minutes} minutes")
        print("Press Ctrl+C to stop\n")
        
        # Schedule the trade cycle
        schedule.every(interval_minutes).minutes.do(self.run_once)
        
        # Run immediately once
        self.run_once()
        
        # Main loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\nBot stopped by user")
        finally:
            print("\nFinal Statistics:")
            self.print_trade_stats()

def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("POLYMARKET TRADING BOT")
    print("="*70)
    print("\nOptions:")
    print("  1. Run once (immediate)")
    print("  2. Run scheduled (every 30 minutes)")
    print("  3. Test components only")
    print("  4. Exit")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    bot = PolymarketTradingBot()
    
    if choice == "1":
        bot.run_once()
    elif choice == "2":
        bot.run_scheduled(interval_minutes=30)
    elif choice == "3":
        # Test components
        print("\nTesting components...")
        
        # Test scanner
        print("\n1. Testing Market Scanner...")
        opportunities = bot.scanner.scan_opportunities()
        bot.scanner.print_opportunities(opportunities, limit=3)
        
        # Test order manager balance
        print("\n2. Testing Order Manager...")
        balance = bot.order_manager.get_balance()
        if balance:
            print(f"  Balance: ${balance:.4f}")
        else:
            print("  Could not fetch balance")
        
        # Test risk manager
        print("\n3. Testing Risk Manager...")
        test_positions = bot.get_current_positions()
        bot.risk_manager.print_risk_report(
            test_positions, bot.current_capital, bot.starting_capital
        )
        
        # Test trade logger
        print("\n4. Testing Trade Logger...")
        bot.trade_logger.print_stats()
        
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()