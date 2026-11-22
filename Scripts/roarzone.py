import requests

CANDIDATE_URLS = [
    "https://raw.githubusercontent.com/sm-monirulislam/RoarZone-Auto-Update-playlist/refs/heads/main/RoarZone.m3u",
    "https://raw.githubusercontent.com/sm-monirulislam/RoarZone-Auto-Update-playlist/main/RoarZone.m3u",
]

OUTPUT_FILE = "RoarZone.m3u"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def sync_roarzone():
    content = None
    last_error = None

    for url in CANDIDATE_URLS:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            text = resp.text.strip()
            if text:
                content = resp.text
                print(f"Fetched successfully from: {url}")
                break
        except Exception as exc:
            last_error = exc
            print(f"Failed URL ({url}): {exc}")

    if not content:
        raise RuntimeError(f"Could not fetch RoarZone playlist. Last error: {last_error}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content if content.endswith("\n") else content + "\n")

    print(f"Updated {OUTPUT_FILE}")

if __name__ == "__main__":
    sync_roarzone()
