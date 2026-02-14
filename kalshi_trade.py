import requests, time, base64, sys, json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

API_KEY = "63d25fe0-e138-4d22-9024-0ba4857f7604"
BASE = "https://api.elections.kalshi.com/trade-api/v2"

with open(r"C:\Users\Borat\Downloads\KalshiAPI.txt") as f:
    c = f.read(); pem = c[c.index("-----BEGIN"):].strip()
pk = serialization.load_pem_private_key(pem.encode(), password=None)

def auth(method, path):
    ts = str(int(time.time()*1000))
    sig = pk.sign(f"{ts}{method}{path}".encode(), padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return {"KALSHI-ACCESS-KEY":API_KEY,"KALSHI-ACCESS-TIMESTAMP":ts,"KALSHI-ACCESS-SIGNATURE":base64.b64encode(sig).decode(),"Content-Type":"application/json"}

sys.stdout.reconfigure(encoding='utf-8')

# Get tariff event details
print("=== TARIFF REVENUE EVENT ===")
p = "/trade-api/v2/events/KXTARIFFREVENUE-26DEC31"
h = auth("GET", p)
r = requests.get(f"{BASE}/events/KXTARIFFREVENUE-26DEC31", headers=h, timeout=10)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    event = data.get("event", {})
    print(f"Title: {event.get('title')}")
    markets = event.get("markets", data.get("markets", []))
    print(f"Markets: {len(markets)}")
    for m in markets:
        tk = m.get("ticker","")
        title = m.get("title","") + " " + m.get("subtitle","")
        ya = m.get("yes_ask",0)
        yb = m.get("yes_bid",0)
        na = m.get("no_ask",0)
        nb = m.get("no_bid",0)
        vol = m.get("volume",0)
        oi = m.get("open_interest",0)
        exp = m.get("close_time","")[:10] if m.get("close_time") else "?"
        print(f"\n  TICKER: {tk}")
        print(f"  {title}")
        print(f"  YES bid/ask: {yb}c / {ya}c | NO bid/ask: {nb}c / {na}c")
        print(f"  Volume: {vol} | Open Interest: {oi} | Expires: {exp}")
else:
    print(r.text[:500])

# Also check deportations
print("\n\n=== DEPORTATIONS EVENT ===")
p2 = "/trade-api/v2/events/KXDEPORTATIONS-27JAN01"
h2 = auth("GET", p2)
r2 = requests.get(f"{BASE}/events/KXDEPORTATIONS-27JAN01", headers=h2, timeout=10)
if r2.status_code == 200:
    data2 = r2.json()
    event2 = data2.get("event", {})
    print(f"Title: {event2.get('title')}")
    markets2 = event2.get("markets", data2.get("markets", []))
    for m in markets2:
        tk = m.get("ticker","")
        title = m.get("title","") + " " + m.get("subtitle","")
        ya = m.get("yes_ask",0)
        yb = m.get("yes_bid",0)
        print(f"  [{tk}] {title} | YES: {yb}/{ya}c")

# Check Greenland
print("\n\n=== GREENLAND EVENT ===")
p3 = "/trade-api/v2/events/KXGREENLAND-29"
h3 = auth("GET", p3)
r3 = requests.get(f"{BASE}/events/KXGREENLAND-29", headers=h3, timeout=10)
if r3.status_code == 200:
    data3 = r3.json()
    event3 = data3.get("event", {})
    print(f"Title: {event3.get('title')}")
    markets3 = event3.get("markets", data3.get("markets", []))
    for m in markets3:
        tk = m.get("ticker","")
        title = m.get("title","") + " " + m.get("subtitle","")
        ya = m.get("yes_ask",0)
        yb = m.get("yes_bid",0)
        print(f"  [{tk}] {title} | YES: {yb}/{ya}c")

# Check tariffs Supreme Court
print("\n\n=== TARIFF SUPREME COURT ===")
p4 = "/trade-api/v2/events/KXDJTVOSTARIFFS"
h4 = auth("GET", p4)
r4 = requests.get(f"{BASE}/events/KXDJTVOSTARIFFS", headers=h4, timeout=10)
if r4.status_code == 200:
    data4 = r4.json()
    event4 = data4.get("event", {})
    print(f"Title: {event4.get('title')}")
    markets4 = event4.get("markets", data4.get("markets", []))
    for m in markets4:
        tk = m.get("ticker","")
        title = m.get("title","") + " " + m.get("subtitle","")
        ya = m.get("yes_ask",0)
        yb = m.get("yes_bid",0)
        print(f"  [{tk}] {title} | YES: {yb}/{ya}c")

# Balance check
print("\n\n=== BALANCE ===")
p5 = "/trade-api/v2/portfolio/balance"
h5 = auth("GET", p5)
r5 = requests.get(f"{BASE}/portfolio/balance", headers=h5, timeout=10)
if r5.status_code == 200:
    bal = r5.json()
    print(f"Balance: ${bal.get('balance',0)/100:.2f}")
    print(f"Portfolio value: ${bal.get('portfolio_value',0)/100:.2f}")
