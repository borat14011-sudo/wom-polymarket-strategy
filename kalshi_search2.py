import requests, time, base64, sys
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

# Scan ALL events
print("=== ALL OPEN EVENTS ===")
cursor = None
interesting = []
for page in range(20):
    p = "/trade-api/v2/events"
    h = auth("GET", p)
    params = {"limit":50,"status":"open"}
    if cursor: params["cursor"] = cursor
    r = requests.get(f"{BASE}/events", headers=h, params=params, timeout=10)
    if r.status_code != 200: break
    data = r.json()
    events = data.get("events",[])
    cursor = data.get("cursor")
    for e in events:
        t = e.get("title","")
        tl = t.lower()
        # Print ALL non-sports events
        if not any(x in tl for x in ["ncaa","nba","nhl","nfl","mlb","soccer","tennis","golf","cricket","rugby","boxing","ufc","mma","esport","formula","nascar","college","basketball game","hockey game","baseball game"]):
            cat = e.get("category","")
            ticker = e.get("event_ticker","")
            print(f"  [{cat}] {t} | {ticker}")
            interesting.append(e)
    if not cursor or not events: break

print(f"\nTotal non-sports events: {len(interesting)}")
