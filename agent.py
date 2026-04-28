import os
import requests
import json
import sys
from datetime import datetime

# Configuration from GitHub Secrets
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
STX_ADDRESS = os.getenv("STX_ADDRESS")
MNEMONIC = os.getenv("MNEMONIC")

def check_secrets():
    missing = []
    if not BTC_ADDRESS: missing.append("BTC_ADDRESS")
    if not STX_ADDRESS: missing.append("STX_ADDRESS")
    if not MNEMONIC: missing.append("MNEMONIC")
    
    if missing:
        print(f"ERROR: Missing GitHub Secrets: {', '.join(missing)}")
        print("Please add these in Settings > Secrets and variables > Actions")
        sys.exit(1)

def get_iso_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def send_heartbeat():
    print(f"[{datetime.utcnow()}] Sending heartbeat for {BTC_ADDRESS}...")
    timestamp = get_iso_timestamp()
    message = f"AIBTC Check-In | {timestamp}"
    # Future: Add actual signing logic here
    print(f"Action: Sign '{message}'")

def file_news(current_hour):
    print(f"[{datetime.utcnow()}] Checking for news signals (Hour: {current_hour})...")
    # Logic to fetch from arXiv or Tenero would go here
    print("Action: Fetching and filing news signal...")

if __name__ == "__main__":
    check_secrets()
    
    current_hour = datetime.utcnow().hour
    print(f"Agent starting. Current UTC hour: {current_hour}")
    
    send_heartbeat()
    
    if current_hour == 6:
        file_news(6)
    elif current_hour == 13:
        file_news(13)
    elif current_hour == 20:
        file_news(20)
    else:
        print("Not a scheduled news window. Skipping news filing.")
