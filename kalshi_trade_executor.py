"""
Kalshi Trade Executor
Usage: python kalshi_trade_executor.py TICKER side count price
Example: python kalshi_trade_executor.py TICKER no 5 74

Validates against risk rules, places order, logs trade.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import os
import time
import base64
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

# Import shared config from portfolio manager
API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
KEY_FILE = r"C:\Users\Borat\Downloads\KalshiAPI.txt"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
WORKSPACE = r"C:\Users\Borat\.openclaw\workspace"
TRADE_LOG = os.path.join(WORKSPACE, "kalshi_trade_log.json")
ASSUMED_PORTFOLIO = 100

MAX_SINGLE_TRADE_PCT = 0.05
MAX_TOTAL_EXPOSURE_PCT = 0.30
CIRCUIT_BREAKER_PCT = 0.20

def load_private_key():
    with open(KEY_FILE, "r") as f:
        content = f.read()
    lines = content.strip().split("\n")
    pem_lines = []
    in_pem = False
    for line in lines:
        if "BEGIN RSA PRIVATE KEY" in line:
            in_pem = True
        if in_pem:
            pem_lines.append(line)
        if "END RSA PRIVATE KEY" in line:
            break
    pem_str = "\n".join(pem_lines)
    return serialization.load_pem_private_key(pem_str.encode(), password=None)

PRIVATE_KEY = load_private_key()

def sign_request(method, path, timestamp_str):
    message = timestamp_str + method.upper() + path
    signature = PRIVATE_KEY.sign(
        message.encode(),
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()

def api_request(method, path, params=None, json_body=None):
    ts = str(int(time.time() * 1000))
    full_path = "/trade-api/v2" + path
    sig = sign_request(method, full_path, ts)
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": sig,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    url = BASE_URL + path
    if method.upper() == "GET":
        r = requests.get(url, headers=headers, params=params, timeout=15)
    elif method.upper() == "POST":
        r = requests.post(url, headers=headers, json=json_body, timeout=15)
    else:
        r = requests.request(method, url, headers=headers, json=json_body, timeout=15)
    r.raise_for_status()
    return r.json()

def get_balance():
    return api_request("GET", "/portfolio/balance")

def get_positions():
    results = []
    cursor = None
    while True:
        params = {"limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = api_request("GET", "/portfolio/positions", params=params)
        positions = data.get("market_positions", data.get("positions", []))
        if not positions:
            break
        results.extend(positions)
        cursor = data.get("cursor")
        if not cursor:
            break
    return results

def load_trade_log():
    if os.path.exists(TRADE_LOG):
        with open(TRADE_LOG, "r") as f:
            return json.load(f)
    return []

def save_trade_log(log):
    with open(TRADE_LOG, "w") as f:
        json.dump(log, f, indent=2)

def get_current_exposure(positions):
    total = 0
    for pos in positions:
        count = abs(pos.get("position", 0))
        total += count * 100  # cents, max $1 per contract
    return total / 100.0  # dollars

def validate_risk(ticker, side, count, price_cents):
    """Validate trade against risk rules. Returns (ok, reason)."""
    trade_cost = (count * price_cents) / 100.0  # dollars

    # Single trade limit
    max_single = ASSUMED_PORTFOLIO * MAX_SINGLE_TRADE_PCT
    if trade_cost > max_single:
        return False, f"Trade cost ${trade_cost:.2f} exceeds single trade limit ${max_single:.2f}"

    # Total exposure check
    positions = get_positions()
    current_exposure = get_current_exposure(positions)
    new_exposure = current_exposure + (count * 1.0)  # each contract = $1 max exposure
    max_exposure = ASSUMED_PORTFOLIO * MAX_TOTAL_EXPOSURE_PCT
    if new_exposure > max_exposure:
        return False, f"New exposure ${new_exposure:.2f} exceeds limit ${max_exposure:.2f}"

    # Drawdown check
    balance = get_balance()
    available = balance.get("balance", 0) / 100.0
    # Load history for peak
    history_file = os.path.join(WORKSPACE, "kalshi_portfolio_history.json")
    peak = available
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
        for snap in history:
            b = snap.get("available", 0)
            if b > peak:
                peak = b
    if peak > 0:
        dd = (peak - available) / peak * 100
        if dd >= CIRCUIT_BREAKER_PCT * 100:
            return False, f"Circuit breaker active. Drawdown {dd:.1f}% from peak ${peak:.2f}"

    return True, f"OK. Cost: ${trade_cost:.2f}, New exposure: ~${new_exposure:.2f}"

def place_order(ticker, side, count, price_cents):
    """Place an order via Kalshi API."""
    import uuid
    order_body = {
        "ticker": ticker,
        "action": "buy",
        "side": side,
        "count": count,
        "type": "limit",
        "yes_price" if side == "yes" else "no_price": price_cents,
        "client_order_id": str(uuid.uuid4()),
    }
    result = api_request("POST", "/portfolio/orders", json_body=order_body)
    return result

def main():
    if len(sys.argv) < 5:
        print("Usage: python kalshi_trade_executor.py TICKER side count price")
        print("  TICKER  - market ticker (e.g., KXBTC-25FEB14-T99049.99)")
        print("  side    - 'yes' or 'no'")
        print("  count   - number of contracts (integer)")
        print("  price   - price in cents (1-99)")
        print("")
        print("Example: python kalshi_trade_executor.py TICKER no 5 74")
        sys.exit(1)

    ticker = sys.argv[1]
    side = sys.argv[2].lower()
    count = int(sys.argv[3])
    price_cents = int(sys.argv[4])

    if side not in ("yes", "no"):
        print(f"ERROR: side must be 'yes' or 'no', got '{side}'")
        sys.exit(1)
    if count < 1:
        print("ERROR: count must be >= 1")
        sys.exit(1)
    if price_cents < 1 or price_cents > 99:
        print("ERROR: price must be 1-99 cents")
        sys.exit(1)

    trade_cost = (count * price_cents) / 100.0
    print(f"Trade: BUY {count}x {ticker} {side.upper()} @ {price_cents}c")
    print(f"Cost: ${trade_cost:.2f}")
    print("")

    # Risk validation
    print("Validating risk rules...")
    ok, reason = validate_risk(ticker, side, count, price_cents)
    if not ok:
        print(f"BLOCKED: {reason}")
        # Log blocked trade
        log = load_trade_log()
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker,
            "side": side,
            "count": count,
            "price_cents": price_cents,
            "cost_dollars": trade_cost,
            "status": "BLOCKED",
            "reason": reason,
        })
        save_trade_log(log)
        sys.exit(1)

    print(f"Risk check passed: {reason}")
    print("")

    # Place order
    print("Placing order...")
    try:
        result = api_request("POST", "/portfolio/orders", json_body={
            "ticker": ticker,
            "action": "buy",
            "side": side,
            "count": count,
            "type": "limit",
            "yes_price" if side == "yes" else "no_price": price_cents,
        })
        order = result.get("order", result)
        order_id = order.get("order_id", "unknown")
        status = order.get("status", "unknown")
        print(f"Order placed! ID: {order_id}, Status: {status}")

        # Log trade
        log = load_trade_log()
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker,
            "side": side,
            "count": count,
            "price_cents": price_cents,
            "cost_dollars": trade_cost,
            "status": "PLACED",
            "order_id": order_id,
            "order_status": status,
            "response": order,
        })
        save_trade_log(log)
        print(f"Trade logged to {TRADE_LOG}")

    except requests.exceptions.HTTPError as e:
        error_body = ""
        try:
            error_body = e.response.text
        except:
            pass
        print(f"ORDER FAILED: {e}")
        print(f"Response: {error_body}")

        log = load_trade_log()
        log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ticker": ticker,
            "side": side,
            "count": count,
            "price_cents": price_cents,
            "cost_dollars": trade_cost,
            "status": "FAILED",
            "error": str(e),
            "error_body": error_body,
        })
        save_trade_log(log)
        sys.exit(1)

if __name__ == "__main__":
    main()
