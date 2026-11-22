from datetime import datetime, timezone, timedelta
import re
import requests

SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/SonyLiv_Event_Playlist/refs/heads/main/sonyLiv.m3u"
OUTPUT_FILE = "SonyLiv.m3u"

# সব ভাষা রাখতে চাইলে [] ফাঁকা রাখুন; নির্দিষ্ট ভাষা চাইলে যেমন ["ENG", "HIN"] দিন
ONLY_LANGUAGES = []

def keep_entry(extinf: str) -> bool:
    if not ONLY_LANGUAGES:
        return True
    upper_extinf = extinf.upper()
    return any(f"[{lang.upper()}]" in upper_extinf for lang in ONLY_LANGUAGES)

def build_sonyliv_playlist():
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
            if keep_entry(current_extinf):
                name_match = re.search(r'tvg-name="([^"]*)"', current_extinf)
                logo_match = re.search(r'tvg-logo="([^"]*)"', current_extinf)
                group_match = re.search(r'group-title="([^"]*)"', current_extinf)

                ch_title = current_extinf.split(",")[-1].strip() if "," in current_extinf else "SonyLiv Event"
                tvg_name = name_match.group(1) if name_match else ch_title
                logo = logo_match.group(1) if logo_match else ""
                group = group_match.group(1) if group_match else "Cricket"

                extinf = f'#EXTINF:-1 tvg-name="{tvg_name}" tvg-logo="{logo}" group-title="{group}",{ch_title}'
                entries.append((extinf, line))
            current_extinf = None

    if not entries:
        raise ValueError("No SonyLiv stream entries found.")

    bd_time = datetime.now(timezone(timedelta(hours=6))).strftime("%Y-%m-%d %H:%M:%S")
    out_lines = [
        "#EXTM3U",
        "# SonyLiv Event Channels (Auto Synced)",
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
    build_sonyliv_playlist()
