# WALLET FUNDING GUIDE

## CRITICAL: Fund Wallet Before Trading

The trading system is 100% ready, but the wallet has **NO USDC**. You must fund it before any trades can execute.

## Wallet Details

**Wallet Address:** `0xb354e25623617a24164639F63D8b731250AC92d8`  
**Network:** Polygon (NOT Ethereum Mainnet)  
**Token:** USDC (Polygon USDC)  
**Amount Needed:** $10 USDC minimum

## How to Fund

### Option 1: From Exchange (Recommended)
1. Log into your exchange (Coinbase, Binance, etc.)
2. Withdraw USDC to Polygon network
3. Send to: `0xb354e25623617a24164639F63D8b731250AC92d8`
4. Network: **Polygon** (MATIC)
5. Amount: $10 USDC

### Option 2: From Another Wallet
1. Open wallet (MetaMask, etc.)
2. Ensure you have USDC on Polygon
3. Send to: `0xb354e25623617a24164639F63d8b731250AC92d8`
4. Network: Polygon

### Option 3: Bridge from Ethereum
1. Use Polygon Bridge: https://wallet.polygon.technology/bridge
2. Bridge USDC from Ethereum to Polygon
3. Send to target wallet

## Verification Steps

After sending funds:

1. **Wait 5-10 minutes** for transaction to confirm
2. **Go to https://polymarket.com**
3. **Connect wallet** (Magic Link/Google)
4. **Check USDC balance** - should show ~$10
5. **Send screenshot** confirmation

## Once Funded

Run this command to execute test trade:
```bash
python execute_pending_trade.py
```

## Trade Details (Ready to Execute)

**Market:** Will Trump deport less than 250,000?  
**Position:** BUY YES  
**Amount:** $0.20  
**Price:** ~50%  

## Risk Management

- Initial test: $0.20 (2% of $10)
- Max position: $2.00 (20% of capital)
- Stop loss: 12% per trade
- Circuit breaker: 15% total drawdown

## Support

If funding issues:
1. Check transaction on Polygonscan
2. Verify network is Polygon
3. Confirm USDC token address on Polygon

**Polygonscan:** https://polygonscan.com/address/0xb354e25623617a24164639F63D8b731250AC92d8