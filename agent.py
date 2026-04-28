import os
import sys
import requests
import hashlib
import base64
from datetime import datetime
from ecdsa import SigningKey, SECP256k1

# Secrets from GitHub
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
MNEMONIC = os.getenv("MNEMONIC")

def get_iso_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def sign_simple(message, mnemonic):
    """Signs a message using the raw derived key from the mnemonic."""
    # Derive a key directly from the mnemonic hash (stable for this session)
    seed = hashlib.sha256(mnemonic.encode()).digest()
    sk = SigningKey.from_string(seed, curve=SECP256k1)
    
    # Bitcoin message hashing standard
    prefix = b"\x18Bitcoin Signed Message:\n"
    msg_bytes = message.encode('utf-8')
    full_msg = prefix + bytes([len(msg_bytes)]) + msg_bytes
    
    # Double SHA256
    msg_hash = hashlib.sha256(hashlib.sha256(full_msg).digest()).digest()
    
    # Sign and encode
    signature = sk.sign_deterministic(msg_hash, hashfunc=hashlib.sha256)
    return base64.b64encode(signature).decode('utf-8')

def send_heartbeat():
    print(f"[{datetime.utcnow()}] Heartbeat started...")
    timestamp = get_iso_timestamp()
    message = f"AIBTC Check-In | {timestamp}"
    
    try:
        signature = sign_simple(message, MNEMONIC)
        
        payload = {
            "btcAddress": BTC_ADDRESS,
            "message": message,
            "signature": signature,
            "timestamp": timestamp,
            "agent": "Sage Spoke (GitHub Automation)"
        }
        
        # We try the heartbeat endpoint
        r = requests.post("https://aibtc.com/api/heartbeat", json=payload, timeout=15)
        print(f"Server Response: {r.status_code} - {r.text}")
        
    except Exception as e:
        print(f"Execution Error: {e}")

if __name__ == "__main__":
    if not MNEMONIC or not BTC_ADDRESS:
        print("CRITICAL: Missing MNEMONIC or BTC_ADDRESS in Secrets.")
        sys.exit(1)

    print(f"Sage Spoke Booting... (Hour: {datetime.utcnow().hour})")
    send_heartbeat()
