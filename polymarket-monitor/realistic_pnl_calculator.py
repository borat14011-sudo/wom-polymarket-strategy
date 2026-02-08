"""
REALISTIC P&L CALCULATOR
Accounts for Polymarket fees, slippage, and real execution costs
"""

class RealisticPnLCalculator:
    """
    Calculate actual profit after all costs
    
    Polymarket fees:
    - 2% maker fee (if you provide liquidity)
    - 2% taker fee (if you take liquidity)
    - Total: ~4% round-trip
    
    Additional costs:
    - Slippage: 0.5-2% on large orders
    - Gas: ~$0.01-0.50 on Polygon (negligible)
    """
    
    MAKER_FEE = 0.02  # 2%
    TAKER_FEE = 0.02  # 2%
    TYPICAL_SLIPPAGE = 0.01  # 1% typical
    
    def calculate_no_bet_pnl(self, bet_size, yes_price, assume_taker=True):
        """
        Calculate P&L for betting NO
        
        Args:
            bet_size: Amount to bet (e.g., $6)
            yes_price: Current YES price (e.g., 0.825 = 82.5%)
            assume_taker: If True, pay taker fee (worst case)
        
        Returns:
            dict with breakdown
        """
        no_price = 1 - yes_price
        
        # Entry cost
        entry_fee_rate = self.TAKER_FEE if assume_taker else self.MAKER_FEE
        shares_before_fee = bet_size / no_price
        entry_fee = shares_before_fee * no_price * entry_fee_rate
        actual_shares = shares_before_fee - (entry_fee / no_price)
        actual_cost = bet_size + entry_fee
        
        # Win scenario
        gross_payout = actual_shares * 1.0  # NO wins, each share = $1
        exit_fee = gross_payout * self.TAKER_FEE
        net_payout = gross_payout - exit_fee
        
        gross_profit = net_payout - actual_cost
        roi = (gross_profit / actual_cost) * 100
        
        # Slippage adjustment (on entry)
        slippage_cost = bet_size * self.TYPICAL_SLIPPAGE
        net_profit = gross_profit - slippage_cost
        net_roi = (net_profit / actual_cost) * 100
        
        return {
            'bet_size': bet_size,
            'yes_price': yes_price * 100,
            'no_price': no_price * 100,
            'shares_bought': actual_shares,
            'entry_fee': entry_fee,
            'actual_cost': actual_cost,
            'gross_payout_if_win': gross_payout,
            'exit_fee': exit_fee,
            'net_payout_if_win': net_payout,
            'gross_profit': gross_profit,
            'gross_roi': roi,
            'slippage_cost': slippage_cost,
            'net_profit': net_profit,
            'net_roi': net_roi
        }
    
    def expected_value(self, bet_size, yes_price, win_probability, assume_taker=True):
        """
        Calculate expected value of a bet
        
        Returns:
            dict with EV analysis
        """
        pnl = self.calculate_no_bet_pnl(bet_size, yes_price, assume_taker)
        
        # Expected value = (win_prob * profit) - (lose_prob * cost)
        win_ev = win_probability * pnl['net_profit']
        lose_ev = (1 - win_probability) * (-pnl['actual_cost'])
        total_ev = win_ev + lose_ev
        ev_percent = (total_ev / pnl['actual_cost']) * 100
        
        return {
            **pnl,
            'win_probability': win_probability * 100,
            'win_ev': win_ev,
            'lose_ev': lose_ev,
            'expected_value': total_ev,
            'ev_percent': ev_percent,
            'kelly_fraction': self._kelly_criterion(win_probability, yes_price)
        }
    
    def _kelly_criterion(self, win_prob, yes_price):
        """
        Calculate Kelly Criterion optimal bet size
        
        Kelly = (p*b - q) / b
        Where:
        - p = win probability
        - q = 1 - p (lose probability)
        - b = odds (profit per dollar risked)
        
        For NO bets:
        - b = yes_price / (1 - yes_price)
        """
        q = 1 - win_prob
        no_price = 1 - yes_price
        b = yes_price / no_price  # Profit per dollar when betting NO
        
        kelly = (win_prob * b - q) / b
        
        # Quarter-Kelly for safety
        quarter_kelly = kelly / 4
        
        return {
            'full_kelly': max(0, kelly * 100),  # As percentage
            'quarter_kelly': max(0, quarter_kelly * 100),
            'recommended': 'quarter_kelly'
        }


def analyze_paper_trades():
    """Analyze our 2 active paper trades with realistic costs"""
    
    calc = RealisticPnLCalculator()
    
    print("="*80)
    print("REALISTIC P&L ANALYSIS - ACTIVE PAPER TRADES")
    print("="*80)
    
    trades = [
        {
            'name': 'BTC >$68K on Feb 8',
            'bet_size': 6.0,
            'yes_price': 0.825,
            'win_prob': 0.619
        },
        {
            'name': 'BTC >$68K on Feb 9',
            'bet_size': 6.0,
            'yes_price': 0.715,
            'win_prob': 0.619
        }
    ]
    
    total_cost = 0
    total_ev = 0
    
    for i, trade in enumerate(trades, 1):
        print(f"\n{'='*80}")
        print(f"TRADE {i}: {trade['name']}")
        print('='*80)
        
        result = calc.expected_value(
            trade['bet_size'],
            trade['yes_price'],
            trade['win_prob']
        )
        
        print(f"\n[ENTRY]")
        print(f"  Bet size: ${result['bet_size']:.2f}")
        print(f"  YES price: {result['yes_price']:.1f}%")
        print(f"  NO price: {result['no_price']:.1f}%")
        print(f"  Entry fee (2%): ${result['entry_fee']:.2f}")
        print(f"  Actual cost: ${result['actual_cost']:.2f}")
        print(f"  Shares bought: {result['shares_bought']:.2f}")
        
        print(f"\n[IF WE WIN]")
        print(f"  Gross payout: ${result['gross_payout_if_win']:.2f}")
        print(f"  Exit fee (2%): ${result['exit_fee']:.2f}")
        print(f"  Net payout: ${result['net_payout_if_win']:.2f}")
        print(f"  Slippage cost: ${result['slippage_cost']:.2f}")
        print(f"  Net profit: ${result['net_profit']:.2f}")
        print(f"  Net ROI: {result['net_roi']:.1f}%")
        
        print(f"\n[EXPECTED VALUE]")
        print(f"  Win probability: {result['win_probability']:.1f}%")
        print(f"  Expected value: ${result['expected_value']:.2f}")
        print(f"  EV%: {result['ev_percent']:.1f}%")
        
        print(f"\n[KELLY CRITERION]")
        print(f"  Full Kelly: {result['kelly_fraction']['full_kelly']:.1f}%")
        print(f"  Quarter Kelly: {result['kelly_fraction']['quarter_kelly']:.1f}%")
        print(f"  Recommended: {result['kelly_fraction']['recommended']}")
        
        total_cost += result['actual_cost']
        total_ev += result['expected_value']
    
    print(f"\n{'='*80}")
    print("PORTFOLIO SUMMARY")
    print('='*80)
    print(f"  Total cost: ${total_cost:.2f}")
    print(f"  Expected value: ${total_ev:.2f}")
    print(f"  Portfolio EV%: {total_ev/total_cost*100:.1f}%")
    
    # Compare to original naive calculation
    print(f"\n{'='*80}")
    print("COMPARISON: NAIVE vs REALISTIC")
    print('='*80)
    print(f"  Naive (no fees):  $28.29 + $15.02 = $43.31 profit")
    print(f"  Realistic (fees): ${total_ev:.2f} expected profit")
    print(f"  Difference: ${43.31 - total_ev:.2f} lost to fees/slippage")
    print(f"  Percentage impact: {(43.31 - total_ev)/43.31*100:.1f}% reduction")


if __name__ == "__main__":
    analyze_paper_trades()
