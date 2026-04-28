import os
import sys
import requests
from datetime import datetime
from aibtc_sdk.wallet import AISigner
from aibtc_sdk.network import AIBTCNetwork

# Configuration from GitHub Secrets
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
STX_ADDRESS = os.getenv("STX_ADDRESS")
MNEMONIC = os.getenv("MNEMONIC")

# Initialize SDK
signer = AISigner(mnemonic=MNEMONIC)
network = AIBTCNetwork()

def get_iso_timestamp():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")

def send_heartbeat():
    print(f"[{datetime.utcnow()}] Sending real heartbeat...")
    timestamp = get_iso_timestamp()
    message = f"AIBTC Check-In | {timestamp}"
    
    # Sign with BTC key (BIP-322/137 handled by SDK)
    signature = signer.sign_bitcoin_message(message)
    
    payload = {
        "btcAddress": BTC_ADDRESS,
        "message": message,
        "signature": signature,
        "timestamp": timestamp
    }
    
    response = requests.post("https://aibtc.com/api/heartbeat", json=payload)
    print(f"Heartbeat Result: {response.status_code} - {response.text}")

def file_arxiv_signal():
    print(f"[{datetime.utcnow()}] Fetching fresh arXiv research...")
    # Get top relevant paper from arXiv
    papers = network.arxiv_search(categories="cs.MA,cs.AI", limit=1)
    
    if not papers:
        print("No new relevant papers found.")
        return

    paper = papers[0]
    headline = f"ArXiv Research: {paper['title'][:100]}"
    body = f"New research published: {paper['abstract'][:500]}..."
    
    print(f"Filing signal: {headline}")
    
    # File via news API
    result = network.file_news_signal(
        beat_slug="aibtc-network",
        headline=headline,
        body=body,
        sources=[{"url": paper['abs_url'], "title": paper['title']}],
        tags=["arxiv", "ai-agents", "research"],
        disclosure="Autonomous Sage Spoke Agent, aibtc-sdk"
    )
    print(f"News Signal Result: {result}")

if __name__ == "__main__":
    if not MNEMONIC or not BTC_ADDRESS:
        print("CRITICAL: Missing secrets.")
        sys.exit(1)

    current_hour = datetime.utcnow().hour
    print(f"Agent Active. UTC Hour: {current_hour}")

    # Always send heartbeat
    send_heartbeat()

    # File news during scheduled windows
    if current_hour == 6:
        file_arxiv_signal()
    elif current_hour in [13, 20]:
        # You can add Tenero/Scout logic here later
        print("Scheduled news window. Logic pending for this slot.")
