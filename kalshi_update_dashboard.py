"""Kalshi Dashboard Updater - pulls live data and publishes to GitHub Pages."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import json
import time
import base64
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

# --- Config ---
API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
RSA_KEY_PATH = r"C:\Users\Borat\Downloads\KalshiAPI.txt"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
WORKSPACE = r"C:\Users\Borat\.openclaw\workspace"
DOCS = os.path.join(WORKSPACE, "docs")

# --- Auth ---
def load_private_key():
    raw = Path(RSA_KEY_PATH).read_text()
    lines = raw.strip().split('\n')
    pem_lines = []
    in_pem = False
    for line in lines:
        if '-----BEGIN RSA PRIVATE KEY-----' in line:
            in_pem = True
        if in_pem:
            pem_lines.append(line.strip())
        if '-----END RSA PRIVATE KEY-----' in line:
            break
    pem_str = '\n'.join(pem_lines)
    return serialization.load_pem_private_key(pem_str.encode(), password=None)

PRIVATE_KEY = load_private_key()

def sign_request(method, path):
    ts = str(int(time.time()))
    message = ts + method.upper() + path
    sig = PRIVATE_KEY.sign(
        message.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return ts, base64.b64encode(sig).decode()

def api_get(path, params=None):
    url = BASE_URL + path
    # Sign with full path including /trade-api/v2 prefix
    full_path = "/trade-api/v2" + path
    ts, sig = sign_request("GET", full_path)
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": sig,
        "Content-Type": "application/json",
    }
    r = requests.get(url, headers=headers, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

# --- Data fetchers ---
def get_balance():
    try:
        data = api_get("/portfolio/balance")
        bal = data.get("balance", 0)
        # Kalshi returns cents
        return bal / 100.0 if bal > 100 else bal
    except Exception as e:
        print(f"[WARN] Balance fetch failed: {e}")
        return 0.0

def get_positions():
    try:
        data = api_get("/portfolio/positions")
        positions = data.get("market_positions", data.get("positions", []))
        result = []
        for p in positions:
            qty = abs(p.get("position", p.get("quantity", 0)))
            if qty == 0:
                continue
            side = "yes" if p.get("position", p.get("quantity", 0)) > 0 else "no"
            ticker = p.get("ticker", p.get("market_ticker", ""))
            result.append({
                "ticker": ticker,
                "side": side,
                "quantity": qty,
                "entry_price": p.get("average_price", p.get("entry_price", 0)),
                "current_price": p.get("market_price", p.get("current_price", 0)),
                "pnl": p.get("realized_pnl", 0) / 100.0 if p.get("realized_pnl", 0) > 10 else p.get("realized_pnl", 0),
                "expiry": p.get("expiration_time", p.get("expiry", "")),
            })
        return result
    except Exception as e:
        print(f"[WARN] Positions fetch failed: {e}")
        return []

def get_fills():
    try:
        data = api_get("/portfolio/fills", params={"limit": 20})
        fills = data.get("fills", [])
        result = []
        for f in fills:
            result.append({
                "ticker": f.get("ticker", ""),
                "side": f.get("side", ""),
                "action": f.get("action", f.get("type", "buy")),
                "quantity": f.get("count", f.get("quantity", 0)),
                "price": f.get("yes_price", f.get("price", 0)),
                "time": f.get("created_time", ""),
            })
        return result
    except Exception as e:
        print(f"[WARN] Fills fetch failed: {e}")
        return []

def get_market_price(ticker):
    try:
        data = api_get(f"/markets/{ticker}")
        m = data.get("market", data)
        return m.get("yes_price", m.get("last_price", 0))
    except:
        return 0

def load_json_file(name):
    path = os.path.join(WORKSPACE, name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return []

def compute_risk(positions, balance):
    total_exposure = sum(p.get("quantity", 0) * p.get("current_price", 0) / 100.0 for p in positions)
    total_value = balance + total_exposure
    exposure_pct = (total_exposure / total_value * 100) if total_value > 0 else 0
    pnls = [p.get("pnl", 0) for p in positions]
    max_dd = min(pnls) if pnls else 0
    max_dd_pct = (max_dd / total_value * 100) if total_value > 0 else 0
    unique_tickers = len(set(p.get("ticker", "").split("-")[0] for p in positions))
    div_score = min(unique_tickers * 20, 100)
    return {
        "exposure_pct": round(exposure_pct, 1),
        "max_drawdown_pct": round(max_dd_pct, 1),
        "diversification_score": div_score,
    }

def build_price_history(positions):
    """Build simple current snapshot for chart (real history would need time-series storage)."""
    if not positions:
        return []
    now = datetime.now(timezone.utc).strftime("%H:%M")
    entry = {"date": now}
    for p in positions[:6]:
        entry[p["ticker"][:20]] = p.get("current_price", 0)
    # Load existing history and append
    hist_path = os.path.join(WORKSPACE, "kalshi_price_history.json")
    history = []
    if os.path.exists(hist_path):
        try:
            with open(hist_path, "r", encoding="utf-8") as f:
                history = json.load(f)
        except:
            pass
    history.append(entry)
    history = history[-50:]  # keep last 50 points
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(history, f)
    return history

def main():
    print("[INFO] Fetching Kalshi data...")
    balance = get_balance()
    positions = get_positions()
    fills = get_fills()

    # Update current prices for positions
    for p in positions:
        if p["ticker"]:
            price = get_market_price(p["ticker"])
            if price:
                p["current_price"] = price
                entry = p.get("entry_price", 0)
                qty = p.get("quantity", 1)
                if p["side"] == "yes":
                    p["pnl"] = round((price - entry) * qty / 100.0, 2)
                else:
                    p["pnl"] = round((entry - price) * qty / 100.0, 2)

    portfolio_value = sum(p.get("quantity", 0) * p.get("current_price", 0) / 100.0 for p in positions)
    total_pnl = sum(p.get("pnl", 0) for p in positions)

    opps = load_json_file("kalshi_opportunities.json")
    if isinstance(opps, dict):
        opps = opps.get("opportunities", opps.get("results", []))
    news = load_json_file("kalshi_news_signals.json")
    if isinstance(news, dict):
        news = news.get("signals", news.get("news", []))

    risk = compute_risk(positions, balance)
    price_history = build_price_history(positions)

    dashboard_data = {
        "last_updated": datetime.now(timezone.utc).isoformat() + "Z",
        "account": {
            "balance": round(balance, 2),
            "portfolio_value": round(portfolio_value, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl / max(balance, 1) * 100, 1),
        },
        "positions": positions,
        "recent_trades": fills,
        "risk": risk,
        "opportunities": opps if isinstance(opps, list) else [],
        "news_signals": news if isinstance(news, list) else [],
        "price_history": price_history,
    }

    # Write JSON
    out_path = os.path.join(WORKSPACE, "kalshi_dashboard_data.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2, default=str)
    print(f"[INFO] Wrote {out_path}")

    # Copy to docs/ AND root (Pages serves from root on gh-pages branch)
    os.makedirs(DOCS, exist_ok=True)
    shutil.copy2(os.path.join(WORKSPACE, "kalshi_dashboard_web.html"), os.path.join(DOCS, "index.html"))
    shutil.copy2(out_path, os.path.join(DOCS, "kalshi_dashboard_data.json"))
    # Also copy to root for GitHub Pages
    shutil.copy2(os.path.join(WORKSPACE, "kalshi_dashboard_web.html"), os.path.join(WORKSPACE, "index.html"))
    print(f"[INFO] Copied to docs/ and root")

    # Git commit and push
    try:
        os.chdir(WORKSPACE)
        subprocess.run(["git", "add", "docs/", "index.html", "kalshi_dashboard_data.json", "kalshi_dashboard_web.html"], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", f"Dashboard update {datetime.now().strftime('%Y-%m-%d %H:%M')}"], check=True, capture_output=True)
        subprocess.run(["git", "push", "--set-upstream", "origin", "gh-pages"], check=True, capture_output=True)
        print("[INFO] Pushed to GitHub")
    except subprocess.CalledProcessError as e:
        print(f"[WARN] Git push: {e.stderr.decode('utf-8','replace') if e.stderr else e}")

    print("[DONE] Dashboard updated successfully")

if __name__ == "__main__":
    main()
