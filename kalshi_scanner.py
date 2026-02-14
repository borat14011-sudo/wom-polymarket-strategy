#!/usr/bin/env python3
"""Kalshi Market Scanner and Opportunity Finder."""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

import traceback
import json
import time
import base64
import hashlib
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import requests

# === CONFIG ===
API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
RSA_KEY_PATH = r"C:\Users\Borat\Downloads\KalshiAPI.txt"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
WORKSPACE = Path(r"C:\Users\Borat\.openclaw\workspace")

OPPORTUNITIES_JSON = WORKSPACE / "kalshi_opportunities.json"
OPPORTUNITIES_MD = WORKSPACE / "kalshi_opportunities.md"
PRICE_HISTORY = WORKSPACE / "kalshi_price_history.json"
PREVIOUS_RUN = WORKSPACE / "kalshi_previous_run.json"


def load_private_key():
    raw = Path(RSA_KEY_PATH).read_text()
    # Extract just the PEM block
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


def sign_request(method, path, timestamp_str):
    message = timestamp_str + method.upper() + path
    signature = PRIVATE_KEY.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode()


def api_get(path, params=None):
    ts = str(int(time.time()))
    # Signature must include full path with /trade-api/v2 prefix
    full_path = "/trade-api/v2" + path
    sig = sign_request("GET", full_path, ts)
    headers = {
        "KALSHI-ACCESS-KEY": API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": sig,
        "Content-Type": "application/json",
    }
    url = BASE_URL + path
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_all_markets():
    """Fetch all open markets via pagination."""
    markets = []
    cursor = None
    page = 0
    while True:
        page += 1
        params = {"limit": 200, "status": "open"}
        if cursor:
            params["cursor"] = cursor
        print(f"[SCAN] Fetching markets page {page}...")
        try:
            data = api_get("/markets", params)
        except Exception as e:
            print(f"[ERROR] Failed to fetch markets: {e}")
            break
        batch = data.get("markets", [])
        markets.extend(batch)
        cursor = data.get("cursor")
        if not cursor or not batch:
            break
        time.sleep(0.3)  # rate limit
    print(f"[SCAN] Total markets fetched: {len(markets)}")
    return markets


def fetch_all_events():
    """Fetch all open events via pagination."""
    events = {}
    cursor = None
    page = 0
    while True:
        page += 1
        params = {"limit": 200, "status": "open"}
        if cursor:
            params["cursor"] = cursor
        print(f"[SCAN] Fetching events page {page}...")
        try:
            data = api_get("/events", params)
        except Exception as e:
            print(f"[ERROR] Failed to fetch events: {e}")
            break
        batch = data.get("events", [])
        for ev in batch:
            events[ev.get("event_ticker", "")] = ev
        cursor = data.get("cursor")
        if not cursor or not batch:
            break
        time.sleep(0.3)
    print(f"[SCAN] Total events fetched: {len(events)}")
    return events


def analyze_market(m, events):
    """Analyze a single market and return enriched data."""
    now = datetime.now(timezone.utc)
    ticker = m.get("ticker", "")
    title = m.get("title", "")
    subtitle = m.get("subtitle", "")
    event_ticker = m.get("event_ticker", "")
    category = m.get("category", "")
    
    # Prices (Kalshi uses cents: 1-99)
    yes_bid = m.get("yes_bid", 0) or 0
    yes_ask = m.get("yes_ask", 0) or 0
    no_bid = m.get("no_bid", 0) or 0
    no_ask = m.get("no_ask", 0) or 0
    last_price = m.get("last_price", 0) or 0
    
    # Use midpoint as best estimate of market price
    if yes_bid and yes_ask:
        mid_price = (yes_bid + yes_ask) / 2.0
    elif last_price:
        mid_price = last_price
    else:
        mid_price = 50  # default
    
    spread = (yes_ask - yes_bid) if (yes_ask and yes_bid) else 0
    
    volume = m.get("volume", 0) or 0
    open_interest = m.get("open_interest", 0) or 0
    
    # Expiration
    close_time_str = m.get("close_time") or m.get("expiration_time") or m.get("expected_expiration_time", "")
    days_to_expiry = None
    if close_time_str:
        try:
            close_time = datetime.fromisoformat(close_time_str.replace("Z", "+00:00"))
            days_to_expiry = max(0, (close_time - now).total_seconds() / 86400)
        except:
            pass
    
    # Annualized IRR calculation
    # If you buy YES at yes_ask, and it resolves YES, profit = 100 - yes_ask
    # IRR = (profit / cost) * (365 / days)
    irr_yes = None
    irr_no = None
    if yes_ask and yes_ask < 100 and days_to_expiry and days_to_expiry > 0:
        profit_pct = (100 - yes_ask) / yes_ask
        irr_yes = profit_pct * (365 / days_to_expiry) * 100
    if no_ask and no_ask < 100 and days_to_expiry and days_to_expiry > 0:
        profit_pct = (100 - no_ask) / no_ask
        irr_no = profit_pct * (365 / days_to_expiry) * 100
    
    # Event info
    event = events.get(event_ticker, {})
    event_title = event.get("title", "")
    
    return {
        "ticker": ticker,
        "title": title,
        "subtitle": subtitle,
        "event_ticker": event_ticker,
        "event_title": event_title,
        "category": category,
        "yes_bid": yes_bid,
        "yes_ask": yes_ask,
        "no_bid": no_bid,
        "no_ask": no_ask,
        "last_price": last_price,
        "mid_price": round(mid_price, 1),
        "spread": spread,
        "volume": volume,
        "open_interest": open_interest,
        "days_to_expiry": round(days_to_expiry, 1) if days_to_expiry is not None else None,
        "irr_yes_annualized": round(irr_yes, 1) if irr_yes is not None else None,
        "irr_no_annualized": round(irr_no, 1) if irr_no is not None else None,
    }


def classify_opportunities(analyzed):
    """Classify markets into opportunity buckets."""
    near_certainties = []
    hype_fades = []
    high_irr = []
    
    # Keywords suggesting hype/unlikely events
    HYPE_KEYWORDS = [
        "greenland", "stimulus", "alien", "ufo", "martial law",
        "resign", "impeach", "abolish", "annex", "declare war",
        "moon landing", "zombie", "elvis"
    ]
    
    for m in analyzed:
        mid = m["mid_price"]
        days = m["days_to_expiry"]
        irr_yes = m["irr_yes_annualized"]
        irr_no = m["irr_no_annualized"]
        spread = m["spread"]
        title_lower = (m["title"] + " " + m["subtitle"] + " " + m["event_title"]).lower()
        
        # Skip illiquid markets
        if m["volume"] < 10 and m["open_interest"] < 5:
            continue
        # Skip huge spreads
        if spread > 15:
            continue
        
        # A. NEAR-CERTAINTIES: market price 60-85 but true prob likely >90%
        # Heuristic: high volume, price 60-85, short time to expiry, stable
        if 60 <= mid <= 85 and days is not None and days <= 30:
            # These look underpriced for near-certain outcomes
            near_certainties.append({**m, "strategy": "NEAR-CERTAINTY", "side": "YES",
                                      "rationale": f"Price {mid}c with {days:.0f} days left - potential info edge"})
        
        # Also check NO side near-certainties (yes price 15-40, meaning NO is 60-85)
        if 15 <= mid <= 40 and days is not None and days <= 30:
            near_certainties.append({**m, "strategy": "NEAR-CERTAINTY", "side": "NO",
                                      "rationale": f"YES price {mid}c (NO ~{100-mid:.0f}c) with {days:.0f} days left"})
        
        # B. HYPE FADE: bet NO on unlikely hyped events
        is_hype = any(kw in title_lower for kw in HYPE_KEYWORDS)
        if is_hype and mid > 5 and mid < 50:
            hype_fades.append({**m, "strategy": "HYPE-FADE", "side": "NO",
                                "rationale": f"Hype keyword detected, YES at {mid}c - likely overpriced"})
        
        # C. HIGH IRR SHORT-TERM
        if days is not None and days <= 30:
            if irr_yes is not None and irr_yes > 20 and mid >= 70:
                high_irr.append({**m, "strategy": "HIGH-IRR", "side": "YES",
                                  "rationale": f"YES IRR {irr_yes:.0f}% ann., {days:.0f} days, price {mid}c"})
            if irr_no is not None and irr_no > 20 and mid <= 30:
                high_irr.append({**m, "strategy": "HIGH-IRR", "side": "NO",
                                  "rationale": f"NO IRR {irr_no:.0f}% ann., {days:.0f} days, YES price {mid}c"})
    
    return near_certainties, hype_fades, high_irr


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except:
            pass
    return None


def save_json(path, data):
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


def update_price_history(analyzed):
    """Append current prices to history file."""
    history = load_json(PRICE_HISTORY) or {}
    ts = datetime.now(timezone.utc).isoformat()
    for m in analyzed:
        ticker = m["ticker"]
        if ticker not in history:
            history[ticker] = []
        history[ticker].append({
            "timestamp": ts,
            "mid_price": m["mid_price"],
            "yes_bid": m["yes_bid"],
            "yes_ask": m["yes_ask"],
            "volume": m["volume"],
        })
        # Keep last 100 entries per ticker
        history[ticker] = history[ticker][-100:]
    save_json(PRICE_HISTORY, history)
    print(f"[HISTORY] Updated price history for {len(analyzed)} markets")


def compare_with_previous(opportunities):
    """Compare current opportunities with previous run."""
    previous = load_json(PREVIOUS_RUN)
    if not previous:
        return [], []
    
    prev_tickers = {o["ticker"] for o in previous}
    curr_tickers = {o["ticker"] for o in opportunities}
    
    new_opps = [o for o in opportunities if o["ticker"] not in prev_tickers]
    
    price_changes = []
    prev_by_ticker = {o["ticker"]: o for o in previous}
    for o in opportunities:
        if o["ticker"] in prev_by_ticker:
            prev = prev_by_ticker[o["ticker"]]
            delta = o["mid_price"] - prev["mid_price"]
            if abs(delta) >= 3:  # 3 cent threshold
                price_changes.append({
                    **o,
                    "prev_price": prev["mid_price"],
                    "price_delta": round(delta, 1),
                })
    
    return new_opps, price_changes


def generate_markdown(near_cert, hype, high_irr, new_opps, price_changes):
    """Generate human-readable markdown report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"# Kalshi Market Scanner Report",
        f"Generated: {now}",
        "",
    ]
    
    def fmt_opp(opp_list, header):
        lines.append(f"## {header} ({len(opp_list)})")
        lines.append("")
        if not opp_list:
            lines.append("No opportunities found.")
            lines.append("")
            return
        for o in sorted(opp_list, key=lambda x: x.get("irr_yes_annualized") or 0, reverse=True):
            lines.append(f"### {o['title']}")
            if o.get("subtitle"):
                lines.append(f"*{o['subtitle']}*")
            lines.append(f"- **Ticker:** {o['ticker']}")
            lines.append(f"- **Side:** {o.get('side', 'N/A')}")
            lines.append(f"- **Mid Price:** {o['mid_price']}c | Spread: {o['spread']}c")
            lines.append(f"- **Volume:** {o['volume']} | Open Interest: {o['open_interest']}")
            if o['days_to_expiry'] is not None:
                lines.append(f"- **Days to Expiry:** {o['days_to_expiry']:.0f}")
            if o['irr_yes_annualized'] is not None:
                lines.append(f"- **YES IRR (ann.):** {o['irr_yes_annualized']:.0f}%")
            if o['irr_no_annualized'] is not None:
                lines.append(f"- **NO IRR (ann.):** {o['irr_no_annualized']:.0f}%")
            lines.append(f"- **Rationale:** {o.get('rationale', 'N/A')}")
            lines.append("")
    
    fmt_opp(near_cert, "NEAR-CERTAINTIES (Info Edge)")
    fmt_opp(hype, "HYPE FADE (Bet NO)")
    fmt_opp(high_irr, "HIGH IRR SHORT-TERM")
    
    if new_opps:
        lines.append(f"## NEW OPPORTUNITIES (since last run): {len(new_opps)}")
        lines.append("")
        for o in new_opps:
            lines.append(f"- **[NEW]** {o['ticker']}: {o['title']} @ {o['mid_price']}c ({o.get('strategy', '')})")
        lines.append("")
    
    if price_changes:
        lines.append(f"## PRICE CHANGES (since last run): {len(price_changes)}")
        lines.append("")
        for o in price_changes:
            direction = "UP" if o["price_delta"] > 0 else "DOWN"
            lines.append(f"- **[{direction} {abs(o['price_delta']):.0f}c]** {o['ticker']}: {o['title']} "
                         f"({o['prev_price']}c -> {o['mid_price']}c)")
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("=" * 60)
    print(f"KALSHI MARKET SCANNER - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Fetch data
    events = fetch_all_events()
    markets = fetch_all_markets()
    
    if not markets:
        print("[WARN] No markets fetched. Exiting.")
        return
    
    # Analyze
    print("[ANALYZE] Processing markets...")
    analyzed = [analyze_market(m, events) for m in markets]
    
    # Classify
    near_cert, hype, high_irr = classify_opportunities(analyzed)
    all_opportunities = near_cert + hype + high_irr
    
    print(f"[RESULTS] Near-certainties: {len(near_cert)}")
    print(f"[RESULTS] Hype fades: {len(hype)}")
    print(f"[RESULTS] High IRR: {len(high_irr)}")
    print(f"[RESULTS] Total opportunities: {len(all_opportunities)}")
    
    # Compare with previous
    new_opps, price_changes = compare_with_previous(all_opportunities)
    if new_opps:
        print(f"[DELTA] {len(new_opps)} NEW opportunities since last run")
    if price_changes:
        print(f"[DELTA] {len(price_changes)} significant price changes")
    
    # Save
    save_json(OPPORTUNITIES_JSON, all_opportunities)
    print(f"[SAVE] Wrote {OPPORTUNITIES_JSON}")
    
    md = generate_markdown(near_cert, hype, high_irr, new_opps, price_changes)
    OPPORTUNITIES_MD.write_text(md, encoding="utf-8")
    print(f"[SAVE] Wrote {OPPORTUNITIES_MD}")
    
    # Update history
    update_price_history(analyzed)
    
    # Save current as previous for next comparison
    save_json(PREVIOUS_RUN, all_opportunities)
    
    # Print top opportunities
    print("")
    print("--- TOP OPPORTUNITIES ---")
    for o in all_opportunities[:15]:
        print(f"  [{o.get('strategy','')}] {o['ticker']}: {o['title'][:60]} "
              f"| {o.get('side','')} @ {o['mid_price']}c | {o.get('rationale','')[:50]}")
    
    print("")
    print("[DONE] Scan complete.")


if __name__ == "__main__":
    main()
