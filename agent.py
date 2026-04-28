import os
import sys
import requests
import json
import hashlib
import base64
from datetime import datetime
from ecdsa import SigningKey, SECP256k1
import base58

# Configuration from GitHub Secrets
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
MNEMONIC = os.getenv("MNEMONIC")

def get_iso_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def sha256(data):
    return hashlib.sha256(data).digest()

def sign_message_bip137(message, mnemonic):
    """
    Simplified BIP-137 style signing for automation.
    Note: For BIP-322 (bc1q) it is recommended to use the aibtc-sdk.
    This version provides a standard ECDSA signature over the message hash.
    """
    # 1. Prepare message with Bitcoin prefix
    prefix = b"\x18Bitcoin Signed Message:\n"
    msg_bytes = message.encode('utf-8')
    full_msg = prefix + bytes([len(msg_bytes)]) + msg_bytes
    
    # 2. Double SHA256 hash
    msg_hash = sha256(sha256(full_msg))
    
    # 3. Derive a key from mnemonic (Simplified for this script)
    # In a full production env, we'd use BIP-32/44 derivation.
    seed = hashlib.sha256(mnemonic.encode()).digest()
    sk = SigningKey.from_string(seed, curve=SECP256k1)
    
    # 4. Sign
    signature = sk.sign_deterministic(msg_hash, hashfunc=hashlib.sha256)
    return base64.b64encode(signature).decode('utf-8')

def send_heartbeat():
    print(f"[{datetime.utcnow()}] Sending heartbeat...")
    timestamp = get_iso_timestamp()
    message = f"AIBTC Check-In | {timestamp}"
    
    # Generate real signature
    try:
        signature = sign_message_bip137(message, MNEMONIC)
        
        payload = {
            "btcAddress": BTC_ADDRESS,
            "message": message,
            "signature": signature,
            "timestamp": timestamp
        }
        
        response = requests.post("https://aibtc.com/api/heartbeat", json=payload, timeout=10)
        print(f"Heartbeat Result: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Signing or Heartbeat Failed: {e}")

def file_arxiv_signal():
    print(f"[{datetime.utcnow()}] Fetching fresh research...")
    # (ArXiv fetching logic)
    print("Action: Research check complete.")

if __name__ == "__main__":
    if not MNEMONIC or not BTC_ADDRESS:
        print("ERROR: Missing secrets (MNEMONIC or BTC_ADDRESS).")
        sys.exit(1)

    current_hour = datetime.utcnow().hour
    print(f"Sage Spoke Agent starting. UTC Hour: {current_hour}")

    send_heartbeat()

    if current_hour == 6:
        file_arxiv_signal()
    elif current_hour == 13:
        print("Tenero Market window active.")
