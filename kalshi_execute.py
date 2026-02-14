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

def place_order(ticker, side, count, limit_price):
    """Place a limit order. side='yes' or 'no', limit_price in cents."""
    path = "/trade-api/v2/portfolio/orders"
    h = auth("POST", path)
    order = {
        "ticker": ticker,
        "action": "buy",
        "side": side,
        "count": count,
        "type": "limit",
        "yes_price": limit_price if side == "yes" else None,
        "no_price": limit_price if side == "no" else None,
    }
    # Remove None values
    order = {k:v for k,v in order.items() if v is not None}
    print(f"\nPlacing order: {json.dumps(order, indent=2)}")
    r = requests.post(f"{BASE}/portfolio/orders", headers=h, json=order, timeout=15)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
    return r

# Check balance first
print("=== PRE-TRADE BALANCE ===")
h = auth("GET", "/trade-api/v2/portfolio/balance")
r = requests.get(f"{BASE}/portfolio/balance", headers=h, timeout=10)
bal = r.json()
print(f"Balance: ${bal.get('balance',0)/100:.2f}")

# TRADE 1: Greenland NO (May 2026) - near certainty
# Trump will NOT buy Greenland by May 2026
# YES at 4-5c means NO at 95-96c
# Buy 2 NO contracts at 96c = $1.92
print("\n\n=== TRADE 1: GREENLAND NO (May 2026) ===")
print("Thesis: Denmark will NOT sell Greenland in 3 months")
place_order("KXGREENLAND-29-26MAY", "no", 2, 96)

# TRADE 2: Greenland NO (during Trump's term) 
# YES at 31-32c means NO at 68-69c
# This is also very likely NO - Denmark won't sell
# Buy 2 NO contracts at 69c = $1.38
print("\n\n=== TRADE 2: GREENLAND NO (Trump's term) ===")
print("Thesis: Denmark will NOT sell Greenland during Trump's term")
place_order("KXGREENLAND-29", "no", 2, 69)

# TRADE 3: Tariff Supreme Court NO
# YES at 26-27c means NO at 73-74c
# SCOTUS likely to limit unilateral tariff power
# Buy 2 NO contracts at 74c = $1.48
print("\n\n=== TRADE 3: SCOTUS TARIFF NO ===")
print("Thesis: SCOTUS will NOT fully side with Trump on tariffs")
place_order("KXDJTVOSTARIFFS", "no", 2, 74)

# Check balance after
print("\n\n=== POST-TRADE BALANCE ===")
h2 = auth("GET", "/trade-api/v2/portfolio/balance")
r2 = requests.get(f"{BASE}/portfolio/balance", headers=h2, timeout=10)
bal2 = r2.json()
print(f"Balance: ${bal2.get('balance',0)/100:.2f}")
print(f"Portfolio value: ${bal2.get('portfolio_value',0)/100:.2f}")

# Check positions
print("\n\n=== POSITIONS ===")
h3 = auth("GET", "/trade-api/v2/portfolio/positions")
r3 = requests.get(f"{BASE}/portfolio/positions", headers=h3, timeout=10)
print(f"Status: {r3.status_code}")
if r3.status_code == 200:
    positions = r3.json()
    print(json.dumps(positions, indent=2)[:1000])
