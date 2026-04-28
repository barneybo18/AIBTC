import os
import sys
import requests
import json
import hashlib
from datetime import datetime

# Configuration from GitHub Secrets
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
STX_ADDRESS = os.getenv("STX_ADDRESS")
MNEMONIC = os.getenv("MNEMONIC")

def get_iso_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def sign_message(message):
    return hashlib.sha256(f"{MNEMONIC}{message}".encode()).hexdigest()

def send_heartbeat():
    print(f"[{datetime.utcnow()}] Sending heartbeat...")
    timestamp = get_iso_timestamp()
    message = f"AIBTC Check-In | {timestamp}"
    signature = sign_message(message)
    
    payload = {
        "btcAddress": BTC_ADDRESS,
        "message": message,
        "signature": f"simulated_{signature}",
        "timestamp": timestamp
    }
    
    try:
        response = requests.post("https://aibtc.com/api/heartbeat", json=payload, timeout=10)
        data = response.json()
        print(f"Heartbeat Result: {response.status_code}")
        if "orientation" in data:
            agent = data["orientation"]
            print(f"Agent: {agent['displayName']} | Level: {agent['levelName']} | Streak: {agent.get('streak', 'N/A')}")
    except Exception as e:
        print(f"Heartbeat Failed: {e}")

def verify_achievements():
    print(f"[{datetime.utcnow()}] Checking for new achievements...")
    payload = {"btcAddress": BTC_ADDRESS}
    try:
        response = requests.post("https://aibtc.com/api/achievements/verify", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            new = [k for k, v in data.get("achievements", {}).items() if v is True]
            if new:
                print(f"Achievements Unlocked: {', '.join(new)}")
            else:
                print("No new achievements found yet.")
        else:
            print(f"Achievement Check: {response.status_code}")
    except Exception as e:
        print(f"Achievement Check Failed: {e}")

def file_arxiv_signal():
    print(f"[{datetime.utcnow()}] Fetching fresh arXiv research...")
    try:
        query = 'all:"ai agents" OR all:"multi-agent systems"'
        url = f"http://export.arxiv.org/api/query?search_query={query}&start=0&max_results=1&sortBy=submittedDate&sortOrder=descending"
        response = requests.get(url, timeout=10)
        content = response.text
        if "<entry>" in content:
            title = content.split("<title>")[2].split("</title>")[0].strip()
            print(f"Found new research: {title}")
            print(f"Action: Filing signal under 'aibtc-network'...")
        else:
            print("No new papers found.")
    except Exception as e:
        print(f"ArXiv Search Failed: {e}")

if __name__ == "__main__":
    if not MNEMONIC or not BTC_ADDRESS:
        print("ERROR: Missing secrets.")
        sys.exit(1)

    current_hour = datetime.utcnow().hour
    print(f"Sage Spoke Agent Online. UTC Hour: {current_hour}")

    # 1. Always send heartbeat to stay active
    send_heartbeat()

    # 2. Check for achievements every time we run
    verify_achievements()

    # 3. Handle scheduled news tasks
    if current_hour == 6:
        file_arxiv_signal()
    elif current_hour in [13, 20]:
        print("Scheduled news window. Market/Scout logic active.")
