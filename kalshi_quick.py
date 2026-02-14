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

# Get events with search
print("Searching events...")
for term in ["tariff","trump tariff","deportation","bitcoin","gta"]:
    p = f"/trade-api/v2/events"
    h = auth("GET", p)
    try:
        r = requests.get(f"{BASE}/events", headers=h, params={"limit":20,"status":"open","series_ticker":""}, timeout=10)
        if r.status_code == 200:
            for e in r.json().get("events",[]):
                t = e.get("title","").lower()
                if any(x in t for x in ["tariff","deport","bitcoin","btc","gta","spacex","musk","greenland","stimulus"]):
                    print(f"EVENT: {e.get('title')} | {e.get('event_ticker')}")
    except Exception as ex:
        print(f"Error: {ex}")
    break  # events endpoint doesn't take search param, just scan once

# Get markets with pagination
print("\nScanning markets...")
cursor = None
count = 0
for page in range(10):
    p = "/trade-api/v2/markets"
    h = auth("GET", p)
    params = {"limit":100,"status":"open"}
    if cursor:
        params["cursor"] = cursor
    try:
        r = requests.get(f"{BASE}/markets", headers=h, params=params, timeout=10)
        if r.status_code != 200:
            print(f"Error {r.status_code}: {r.text[:200]}")
            break
        data = r.json()
        markets = data.get("markets",[])
        cursor = data.get("cursor")
        for m in markets:
            count += 1
            t = (m.get("title","") + " " + m.get("subtitle","")).lower()
            if any(x in t for x in ["tariff","deport","bitcoin","btc","gta","spacex","musk","greenland","stimulus","fed rate","interest rate"]):
                ya = m.get("yes_ask",0)
                na = m.get("no_ask",0)
                v = m.get("volume",0)
                tk = m.get("ticker","")
                exp = m.get("close_time",m.get("expiration_time",""))[:10] if m.get("close_time") or m.get("expiration_time") else "?"
                print(f"  {m.get('title','')} | YES:{ya}c NO:{na}c | Vol:{v} | Exp:{exp} | {tk}")
        if not cursor or not markets:
            break
    except Exception as ex:
        print(f"Error: {ex}")
        break

print(f"\nScanned {count} markets total")
