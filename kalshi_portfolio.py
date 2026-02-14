"""
Kalshi Portfolio Manager and Risk Dashboard
Fetches balance, positions, orders. Calculates P&L, risk, generates dashboard.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import time
import json
import os
import base64
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

# --- Config ---
API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
KEY_FILE = r"C:\Users\Borat\Downloads\KalshiAPI.txt"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
WORKSPACE = r"C:\Users\Borat\.openclaw\workspace"
DASHBOARD_FILE = os.path.join(WORKSPACE, "kalshi_dashboard.md")
HISTORY_FILE = os.path.join(WORKSPACE, "kalshi_portfolio_history.json")
ASSUMED_PORTFOLIO = 100  # $100 assumed total portfolio for risk calcs

# Risk rules
MAX_SINGLE_TRADE_PCT = 0.05   # 5% = $5
MAX_TOTAL_EXPOSURE_PCT = 0.30  # 30% = $30
CONCENTRATION_ALERT_PCT = 0.10 # 10%
CIRCUIT_BREAKER_PCT = 0.20     # 20% drawdown

def load_private_key():
    with open(KEY_FILE, "r") as f:
        content = f.read()
    # Extract just the PEM block
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
    data = api_request("GET", "/portfolio/balance")
    # Balance is in cents
    return data

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

def get_fills():
    results = []
    cursor = None
    while True:
        params = {"limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = api_request("GET", "/portfolio/fills", params=params)
        fills = data.get("fills", [])
        if not fills:
            break
        results.extend(fills)
        cursor = data.get("cursor")
        if not cursor:
            break
    return results

def get_orders():
    results = []
    cursor = None
    while True:
        params = {"limit": 200}
        if cursor:
            params["cursor"] = cursor
        data = api_request("GET", "/portfolio/orders", params=params)
        orders = data.get("orders", [])
        if not orders:
            break
        results.extend(orders)
        cursor = data.get("cursor")
        if not cursor:
            break
    return results

def get_market(ticker):
    try:
        data = api_request("GET", f"/markets/{ticker}")
        return data.get("market", data)
    except Exception as e:
        print(f"  [WARN] Could not fetch market {ticker}: {e}")
        return None

def get_event(event_ticker):
    try:
        data = api_request("GET", f"/events/{event_ticker}")
        return data.get("event", data)
    except:
        return None

def cents_to_dollars(c):
    if c is None:
        return 0.0
    return c / 100.0

def compute_portfolio_metrics(balance_data, positions, fills):
    # Balance
    balance_cents = balance_data.get("balance", 0)
    available = cents_to_dollars(balance_cents)
    payout = cents_to_dollars(balance_data.get("payout", 0))

    # Build fill-based cost basis per ticker+side
    cost_basis = {}  # ticker -> {yes_cost_cents, no_cost_cents, yes_count, no_count}
    for f in fills:
        ticker = f.get("ticker", "")
        side = f.get("side", "")
        count = f.get("count", 0)
        # Use yes_price/no_price (in cents) from fill data
        yes_price = f.get("yes_price", 0)
        no_price = f.get("no_price", 0)
        action = f.get("action", "buy")
        if action == "buy":
            if ticker not in cost_basis:
                cost_basis[ticker] = {"yes_cost": 0, "no_cost": 0, "yes_count": 0, "no_count": 0}
            if side == "yes":
                cost_basis[ticker]["yes_cost"] += count * yes_price  # cents
                cost_basis[ticker]["yes_count"] += count
            else:
                cost_basis[ticker]["no_cost"] += count * no_price  # cents
                cost_basis[ticker]["no_count"] += count

    # Analyze positions
    pos_details = []
    total_invested_cents = 0
    total_exposure_cents = 0
    categories = {}
    now = datetime.now(timezone.utc)

    for pos in positions:
        ticker = pos.get("ticker", "unknown")
        yes_count = pos.get("total_traded", 0)
        # Different API versions have different field names
        position_count = pos.get("position", 0)
        market_exposure = pos.get("market_exposure", 0)
        resting_orders_count = pos.get("resting_orders_count", 0)

        if position_count == 0:
            continue

        side = "yes" if position_count > 0 else "no"
        abs_count = abs(position_count)

        # Fetch market data
        market = get_market(ticker)
        if not market:
            continue

        yes_price = market.get("yes_bid", market.get("last_price", 50))
        no_price = market.get("no_bid", 100 - yes_price if yes_price else 50)
        title = market.get("title", ticker)
        category = market.get("category", market.get("event_ticker", "unknown"))
        close_time_str = market.get("close_time", market.get("expiration_time", ""))

        # Days until expiration
        days_left = None
        if close_time_str:
            try:
                close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
                days_left = max(0, (close_time - now).days)
            except:
                pass

        # Cost basis
        cb = cost_basis.get(ticker, {})
        if side == "yes":
            avg_entry = cb.get("yes_cost", 0) / max(cb.get("yes_count", 1), 1)  # cents
            current_price = yes_price
            invested_cents = cb.get("yes_cost", abs_count * 50)
        else:
            avg_entry = cb.get("no_cost", 0) / max(cb.get("no_count", 1), 1)  # cents
            current_price = no_price
            invested_cents = cb.get("no_cost", abs_count * 50)

        # P&L
        current_value_cents = abs_count * current_price
        unrealized_pnl_cents = current_value_cents - invested_cents
        risk_exposure_cents = abs_count * 100  # max loss = count * $1

        total_invested_cents += invested_cents
        total_exposure_cents += risk_exposure_cents

        # Category tracking
        categories[category] = categories.get(category, 0) + abs_count

        pos_details.append({
            "ticker": ticker,
            "title": title[:60],
            "side": side,
            "count": abs_count,
            "avg_entry": round(avg_entry, 1),
            "current_price": current_price,
            "unrealized_pnl": round(cents_to_dollars(unrealized_pnl_cents), 2),
            "days_left": days_left,
            "risk_exposure": round(cents_to_dollars(risk_exposure_cents), 2),
            "category": category,
            "invested": round(cents_to_dollars(invested_cents), 2),
        })

    # Win/loss from settled fills
    # (Simplified: count fills where settlement happened)
    wins = 0
    losses = 0
    for f in fills:
        if f.get("action") == "settlement":
            if f.get("count", 0) > 0:
                wins += 1
            # Could check revenue vs cost but simplified

    total_invested = cents_to_dollars(total_invested_cents)
    total_exposure = cents_to_dollars(total_exposure_cents)

    # Diversification: 1 - HHI (Herfindahl index)
    total_contracts = sum(categories.values()) if categories else 1
    hhi = sum((c / total_contracts) ** 2 for c in categories.values()) if categories else 1
    diversification = round((1 - hhi) * 100, 1)

    # Risk alerts
    alerts = []
    portfolio_val = ASSUMED_PORTFOLIO
    if total_exposure > portfolio_val * MAX_TOTAL_EXPOSURE_PCT:
        alerts.append(f"[ALERT] Total exposure ${total_exposure:.2f} exceeds {MAX_TOTAL_EXPOSURE_PCT*100:.0f}% limit (${portfolio_val * MAX_TOTAL_EXPOSURE_PCT:.2f})")
    for p in pos_details:
        if p["invested"] > portfolio_val * CONCENTRATION_ALERT_PCT:
            alerts.append(f"[ALERT] {p['ticker']} investment ${p['invested']:.2f} exceeds {CONCENTRATION_ALERT_PCT*100:.0f}% concentration limit")

    # Check drawdown from history
    peak_balance = available
    history = load_history()
    for snap in history:
        b = snap.get("available", 0)
        if b > peak_balance:
            peak_balance = b
    drawdown_pct = (peak_balance - available) / peak_balance * 100 if peak_balance > 0 else 0
    if drawdown_pct >= CIRCUIT_BREAKER_PCT * 100:
        alerts.append(f"[CIRCUIT BREAKER] Drawdown {drawdown_pct:.1f}% from peak ${peak_balance:.2f}. STOP TRADING.")

    return {
        "available": available,
        "payout": payout,
        "total_invested": total_invested,
        "total_exposure": total_exposure,
        "positions": pos_details,
        "categories": categories,
        "diversification": diversification,
        "wins": wins,
        "losses": losses,
        "alerts": alerts,
        "drawdown_pct": round(drawdown_pct, 1),
        "peak_balance": peak_balance,
    }

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(snapshot):
    history = load_history()
    history.append(snapshot)
    # Keep last 1000 snapshots
    if len(history) > 1000:
        history = history[-1000:]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def generate_dashboard(metrics):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("# Kalshi Portfolio Dashboard")
    lines.append(f"Generated: {now_str}")
    lines.append("")

    # Summary
    lines.append("## Account Summary")
    lines.append(f"- Available Balance: ${metrics['available']:.2f}")
    lines.append(f"- Pending Payout: ${metrics['payout']:.2f}")
    lines.append(f"- Total Invested: ${metrics['total_invested']:.2f}")
    lines.append(f"- Total Exposure: ${metrics['total_exposure']:.2f}")
    lines.append(f"- Diversification Score: {metrics['diversification']}%")
    lines.append(f"- Drawdown from Peak: {metrics['drawdown_pct']}% (peak ${metrics['peak_balance']:.2f})")
    lines.append(f"- Settled Wins: {metrics['wins']} | Losses: {metrics['losses']}")
    lines.append("")

    # Risk Rules
    lines.append("## Risk Rules")
    lines.append(f"- Max Single Trade: ${ASSUMED_PORTFOLIO * MAX_SINGLE_TRADE_PCT:.2f} (5%)")
    lines.append(f"- Max Total Exposure: ${ASSUMED_PORTFOLIO * MAX_TOTAL_EXPOSURE_PCT:.2f} (30%)")
    lines.append(f"- Concentration Alert: >{CONCENTRATION_ALERT_PCT*100:.0f}% per position")
    lines.append(f"- Circuit Breaker: {CIRCUIT_BREAKER_PCT*100:.0f}% drawdown")
    lines.append("")

    # Alerts
    if metrics["alerts"]:
        lines.append("## ALERTS")
        for a in metrics["alerts"]:
            lines.append(f"- {a}")
        lines.append("")

    # Positions
    lines.append("## Open Positions")
    if not metrics["positions"]:
        lines.append("No open positions.")
    else:
        lines.append("")
        lines.append("| Ticker | Side | Qty | Entry | Current | P&L | Days Left | Exposure |")
        lines.append("|--------|------|-----|-------|---------|-----|-----------|----------|")
        for p in metrics["positions"]:
            days = str(p["days_left"]) if p["days_left"] is not None else "?"
            pnl_str = f"${p['unrealized_pnl']:+.2f}"
            lines.append(f"| {p['ticker'][:25]} | {p['side']} | {p['count']} | {p['avg_entry']:.0f}c | {p['current_price']}c | {pnl_str} | {days} | ${p['risk_exposure']:.2f} |")
    lines.append("")

    # Categories
    if metrics["categories"]:
        lines.append("## Category Breakdown")
        for cat, count in sorted(metrics["categories"].items(), key=lambda x: -x[1]):
            lines.append(f"- {cat}: {count} contracts")
        lines.append("")

    return "\n".join(lines)

def check_risk_rules(trade_cost_dollars, metrics):
    """Returns (allowed, reason)"""
    portfolio_val = ASSUMED_PORTFOLIO
    if trade_cost_dollars > portfolio_val * MAX_SINGLE_TRADE_PCT:
        return False, f"Trade cost ${trade_cost_dollars:.2f} exceeds single trade limit ${portfolio_val * MAX_SINGLE_TRADE_PCT:.2f}"
    new_exposure = metrics["total_exposure"] + trade_cost_dollars
    if new_exposure > portfolio_val * MAX_TOTAL_EXPOSURE_PCT:
        return False, f"New exposure ${new_exposure:.2f} would exceed limit ${portfolio_val * MAX_TOTAL_EXPOSURE_PCT:.2f}"
    if metrics["drawdown_pct"] >= CIRCUIT_BREAKER_PCT * 100:
        return False, f"Circuit breaker active. Drawdown at {metrics['drawdown_pct']}%"
    return True, "OK"

def main():
    print("Kalshi Portfolio Manager")
    print("=" * 40)

    print("Fetching balance...")
    balance = get_balance()
    print(f"  Balance: {balance}")

    print("Fetching positions...")
    positions = get_positions()
    print(f"  Found {len(positions)} position entries")

    print("Fetching fills...")
    fills = get_fills()
    print(f"  Found {len(fills)} fills")

    print("Computing metrics...")
    metrics = compute_portfolio_metrics(balance, positions, fills)

    print("Generating dashboard...")
    dashboard = generate_dashboard(metrics)
    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(dashboard)
    print(f"  Saved to {DASHBOARD_FILE}")

    # Save snapshot
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "available": metrics["available"],
        "total_invested": metrics["total_invested"],
        "total_exposure": metrics["total_exposure"],
        "position_count": len(metrics["positions"]),
        "diversification": metrics["diversification"],
        "drawdown_pct": metrics["drawdown_pct"],
    }
    save_history(snapshot)
    print(f"  Snapshot saved to {HISTORY_FILE}")

    # Print dashboard
    print("")
    print(dashboard)

    # Print alerts
    if metrics["alerts"]:
        print("")
        print("*** RISK ALERTS ***")
        for a in metrics["alerts"]:
            print(f"  {a}")

    return metrics

if __name__ == "__main__":
    main()
