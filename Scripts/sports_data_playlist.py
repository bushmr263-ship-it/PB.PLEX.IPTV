from datetime import datetime, timezone, timedelta
import requests

SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/Upcoming-and-Live-Sports-Data/refs/heads/main/Sports_data.json"
OUTPUT_FILE = "Sports_Live.m3u"

# শুধু LIVE ম্যাচ রাখতে True করুন; সব ম্যাচ রাখতে False রাখুন
ONLY_LIVE = True

# নির্দিষ্ট ক্যাটাগরি রাখতে চাইলে যেমন ["Cricket", "Football"]; সব ক্যাটাগরি চাইলে []
ONLY_CATEGORIES = []

def build_sports_playlist():
    resp = requests.get(SOURCE_URL, timeout=25)
    resp.raise_for_status()
    data = resp.json()

    matches = data.get("matches", [])
    entries = []

    for match in matches:
        status = str(match.get("status", "")).strip()
        category = str(match.get("Category", "Sports")).strip() or "Sports"
        event_name = str(match.get("event_name", "Live Match")).strip()
        event_info = match.get("eventInfo") or {}
        logo = str(event_info.get("event_logo") or event_info.get("teamAFlag") or "").strip()

        if ONLY_LIVE and status.upper() != "LIVE":
            continue

        if ONLY_CATEGORIES:
            allowed = {c.lower() for c in ONLY_CATEGORIES}
            if category.lower() not in allowed:
                continue

        for stream in match.get("streams") or []:
            stream_url = str(stream.get("stream_url", "")).strip()
            if not stream_url:
                continue

            ch_name = str(stream.get("channel_name", "Live Stream")).strip()
            kid = str(stream.get("kid", "")).strip()
            key = str(stream.get("key", "")).strip()

            display_title = f"{event_name} - {ch_name}" if event_name else ch_name
            extinf = f'#EXTINF:-1 tvg-name="{display_title}" tvg-logo="{logo}" group-title="{category}",{display_title}'

            entries.append({
                "extinf": extinf,
                "url": stream_url,
                "kid": kid,
                "key": key,
            })

    if not entries:
        raise ValueError("No matching sports streams found in JSON.")

    bd_time = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d %H:%M:%S")
    out_lines = [
        "#EXTM3U",
        "# Live & Upcoming Sports Streams (Auto Synced)",
        f"# Last Updated: {bd_time}",
        ""
    ]

    for item in entries:
        out_lines.append(item["extinf"])
        if item["kid"] and item["key"]:
            out_lines.append("#KODIPROP:inputstream.adaptive.license_type=clearkey")
            out_lines.append(f'#KODIPROP:inputstream.adaptive.license_key={item["kid"]}:{item["key"]}')
        out_lines.append(item["url"])
        out_lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"Updated {OUTPUT_FILE} with {len(entries)} streams at {bd_time}")

if __name__ == "__main__":
    build_sports_playlist()
