"""Kalshi API Client - RSA-PSS Authentication"""
import requests
import time
import base64
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
    sig = private_key.sign(
        msg.encode(),
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return {
        "KALSHI-ACCESS-KEY": API_KEY,
        "KALSHI-ACCESS-TIMESTAMP": ts,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(sig).decode(),
        "Content-Type": "application/json",
    }

def get(endpoint, params=None):
    path = f"/trade-api/v2{endpoint}"
    headers = sign_request("GET", path)
    r = requests.get(f"{BASE_URL}{endpoint}", headers=headers, params=params, timeout=15)
    return r

def post(endpoint, data=None):
    path = f"/trade-api/v2{endpoint}"
    headers = sign_request("POST", path)
    r = requests.post(f"{BASE_URL}{endpoint}", headers=headers, json=data, timeout=15)
    return r

# Test 1: Exchange status
print("=== EXCHANGE STATUS ===")
r = get("/exchange/status")
print(f"Status: {r.status_code}")
print(r.json())

# Test 2: Portfolio/balance
print("\n=== PORTFOLIO ===")
r = get("/portfolio/balance")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    print(r.json())
else:
    print(r.text[:300])

# Test 3: Get markets (short-term, high volume)
print("\n=== ACTIVE MARKETS ===")
r = get("/markets", params={"limit": 20, "status": "open"})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    markets = data.get("markets", [])
    print(f"Found {len(markets)} markets")
    for m in markets[:10]:
        title = m.get("title", "?")
        ticker = m.get("ticker", "?")
        yes_price = m.get("yes_ask", m.get("last_price", "?"))
        volume = m.get("volume", 0)
        print(f"  [{ticker}] {title} | YES: {yes_price} | Vol: {volume}")
else:
    print(r.text[:300])
