"""Find best Kalshi trades - tariffs, politics, near-certainties"""
import requests, time, base64, json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"

with open(r"C:\Users\Borat\Downloads\KalshiAPI.txt", "r") as f:
    content = f.read()
    pem_start = content.index("-----BEGIN RSA PRIVATE KEY-----")
    pem_data = content[pem_start:].strip()

private_key = serialization.load_pem_private_key(pem_data.encode(), password=None)

def sign_request(method, path):
    ts = str(int(time.time() * 1000))
    msg = f"{ts}{method}{path}"
    sig = private_key.sign(msg.encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY": API_KEY, "KALSHI-ACCESS-TIMESTAMP": ts, "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(), "Content-Type": "application/json"}

def get(endpoint, params=None):
    path = f"/trade-api/v2{endpoint}"
    headers = sign_request("GET", path)
    return requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=15)

# Search for tariff markets
searches = ["tariff", "trump", "fed", "bitcoin", "deportation", "gta"]
all_markets = []

for term in searches:
    print(f"\n--- Searching: {term} ---")
    r = get("/markets", params={"limit": 50, "status": "open"})
    if r.status_code == 200:
        markets = r.json().get("markets", [])
        for m in markets:
            title = m.get("title", "").lower()
            subtitle = m.get("subtitle", "").lower()
            if term.lower() in title or term.lower() in subtitle:
                all_markets.append(m)
                yes_ask = m.get("yes_ask", 0)
                no_ask = m.get("no_ask", 0) 
                vol = m.get("volume", 0)
                ticker = m.get("ticker", "?")
                print(f"  [{ticker}] {m.get('title','')} | YES: {yes_ask}c | NO: {no_ask}c | Vol: {vol}")

# Also get events
print("\n\n--- Searching Events ---")
for term in ["tariff", "trump", "deportation"]:
    r = get("/events", params={"limit": 20, "status": "open"})
    if r.status_code == 200:
        events = r.json().get("events", [])
        for e in events:
            title = e.get("title", "").lower()
            if term in title:
                print(f"  EVENT: {e.get('title','')} | ticker: {e.get('event_ticker','')}")
                # Get markets for this event
                evt_ticker = e.get("event_ticker", "")
                if evt_ticker:
                    r2 = get(f"/events/{evt_ticker}")
                    if r2.status_code == 200:
                        evt_data = r2.json()
                        evt_markets = evt_data.get("event", {}).get("markets", [])
                        if not evt_markets:
                            evt_markets = evt_data.get("markets", [])
                        for em in evt_markets[:5]:
                            print(f"    Market: {em.get('title','')} | YES: {em.get('yes_ask',0)}c | ticker: {em.get('ticker','')}")

# Get ALL markets with cursor pagination to find tariff
print("\n\n--- Full market scan (first 200) ---")
cursor = None
found = []
for page in range(4):
    params = {"limit": 50, "status": "open"}
    if cursor:
        params["cursor"] = cursor
    r = get("/markets", params=params)
    if r.status_code == 200:
        data = r.json()
        markets = data.get("markets", [])
        cursor = data.get("cursor")
        for m in markets:
            title = (m.get("title", "") + " " + m.get("subtitle", "")).lower()
            if any(t in title for t in ["tariff", "deportat", "bitcoin", "btc", "gta", "spacex", "musk", "greenland"]):
                yes_ask = m.get("yes_ask", 0)
                no_ask = m.get("no_ask", 0)
                vol = m.get("volume", 0)
                ticker = m.get("ticker", "?")
                end = m.get("close_time", m.get("expiration_time", "?"))
                found.append(m)
                print(f"  [{ticker}] {m.get('title','')} | YES:{yes_ask}c NO:{no_ask}c | Vol:{vol} | Exp:{end}")
        if not cursor:
            break

print(f"\n\nTotal interesting markets found: {len(found)}")
