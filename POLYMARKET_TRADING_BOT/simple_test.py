#!/usr/bin/env python3
"""
Simple API test - just try to connect
"""
import os
import json
import hmac
import hashlib
import base64
import time
import requests
from dotenv import load_dotenv

load_dotenv('.env.api')

API_KEY = os.getenv('POLYMARKET_API_KEY')
API_SECRET = os.getenv('POLYMARKET_API_SECRET')
PASSPHRASE = os.getenv('POLYMARKET_PASSPHRASE')
WALLET = os.getenv('POLY_WALLET_ADDRESS', '').lower()

def build_sig(secret, timestamp, method, path, body=None):
    try:
        secret_bytes = base64.urlsafe_b64decode(secret)
    except:
        padded = secret + '=' * (4 - len(secret) % 4)
        secret_bytes = base64.urlsafe_b64decode(padded)
    
    msg = str(timestamp) + str(method) + str(path)
    if body:
        msg += json.dumps(body, separators=(',', ':'))
    
    h = hmac.new(secret_bytes, msg.encode('utf-8'), hashlib.sha256)
    return base64.urlsafe_b64encode(h.digest()).decode('utf-8')

timestamp = str(int(time.time()))
sig = build_sig(API_SECRET, timestamp, "GET", "/balance-allowance")

headers = {
    "POLY_ADDRESS": WALLET,
    "POLY_SIGNATURE": sig,
    "POLY_TIMESTAMP": timestamp,
    "POLY_API_KEY": API_KEY,
    "POLY_PASSPHRASE": PASSPHRASE,
    "Content-Type": "application/json",
    "Accept": "*/*"
}

print("Testing connection to https://clob.polymarket.com/balance-allowance")
print(f"Wallet: {WALLET}")
print(f"API Key: {API_KEY[:20]}...")
print(f"Timestamp: {timestamp}")
print(f"Signature: {sig[:30]}...")
print()

try:
    response = requests.get(
        "https://clob.polymarket.com/balance-allowance",
        headers=headers,
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
