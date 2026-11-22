from datetime import datetime, timezone, timedelta
import re
import requests

SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/Toffee-Auto-Update/refs/heads/main/toffee_playlist.m3u"
OUTPUT_FILE = "Toffee.m3u"

def build_playlist():
    resp = requests.get(SOURCE_URL, timeout=20)
    resp.raise_for_status()
    lines = resp.text.splitlines()

    entries = []
    current_extinf = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            current_extinf = line
        elif not line.startswith("#") and current_extinf:
            # চ্যানেলের নাম বের করা (কমার পরের অংশ)
            name = current_extinf.split(",")[-1].strip() if "," in current_extinf else "Toffee Channel"
            logo_match = re.search(r'tvg-logo="([^"]*)"', current_extinf)
            group_match = re.search(r'group-title="([^"]*)"', current_extinf)

            logo = logo_match.group(1) if logo_match else ""
            group = group_match.group(1) if group_match else "Toffee"

            extinf = f'#EXTINF:-1 tvg-name="{name}" tvg-logo="{logo}" group-title="{group}",{name}'
            entries.append((extinf, line))
            current_extinf = None

    if not entries:
        raise ValueError("No stream entries found from source playlist.")

    bd_time = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d %H:%M:%S")
    out_lines = [
        "#EXTM3U",
        "# Toffee Live Channels (Auto Synced)",
        f"# Last Updated: {bd_time}",
        ""
    ]

    for extinf, url in entries:
        out_lines.append(extinf)
        out_lines.append(url)
        out_lines.append("")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(out_lines).strip() + "\n")

    print(f"Updated {OUTPUT_FILE} with {len(entries)} channels at {bd_time}")

if __name__ == "__main__":
    build_playlist()
