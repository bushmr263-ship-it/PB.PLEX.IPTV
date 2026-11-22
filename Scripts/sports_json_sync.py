from datetime import datetime, timezone, timedelta
import json
import requests

SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/Upcoming-and-Live-Sports-Data/refs/heads/main/Sports_data.json"
OUTPUT_FILE = "Sports_data.json"

# শুধু LIVE ম্যাচ রাখতে True করুন; সব ম্যাচ রাখতে False রাখুন
ONLY_LIVE = False

def sync_sports_json():
    resp = requests.get(SOURCE_URL, timeout=25)
    resp.raise_for_status()
    data = resp.json()

    if ONLY_LIVE and isinstance(data, dict) and "matches" in data:
        data["matches"] = [
            m for m in data.get("matches", [])
            if str(m.get("status", "")).strip().upper() == "LIVE"
        ]
        data["live_match"] = len(data["matches"])

    bd_time = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(data, dict):
        data["synced_at_bd"] = bd_time

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {OUTPUT_FILE} at {bd_time}")

if __name__ == "__main__":
    sync_sports_json()
