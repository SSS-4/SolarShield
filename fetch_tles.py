#!/usr/bin/env python3
"""
fetch_tles.py — Daily TLE snapshot fetcher for SolarShield.

Run by GitHub Actions once per day. Downloads each satellite group from
CelesTrak ONCE (respecting their one-download-per-update policy) and saves
them to data/<group>.tle. SolarShield then reads these local files instead
of hitting CelesTrak from Streamlit's (rate-limited) cloud IP.
"""

import os
import time
import requests

GROUPS = ["stations", "starlink", "weather", "gps-ops", "galileo"]
OUT_DIR = "data"

def fetch_group(group):
    url = f"https://celestrak.org/NORAD/elements/gp.php?GROUP={group}&FORMAT=tle"
    headers = {"User-Agent": "SolarShield-DailyFetch/1.0 (educational project)"}
    r = requests.get(url, timeout=60, headers=headers)
    r.raise_for_status()
    if len(r.text) < 100:
        raise ValueError(f"Suspiciously short response for {group}")
    return r.text

def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for group in GROUPS:
        try:
            text = fetch_group(group)
            path = os.path.join(OUT_DIR, f"{group}.tle")
            with open(path, "w") as f:
                f.write(text)
            print(f"Saved {group}: {len(text.splitlines())} lines")
        except Exception as e:
            print(f"WARNING: failed to fetch {group}: {e}")
        # Be polite — small pause between requests so we never look like a flood
        time.sleep(5)

    # Write a timestamp so the app can show data freshness honestly
    with open(os.path.join(OUT_DIR, "last_updated.txt"), "w") as f:
        f.write(time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
    print("Done.")

if __name__ == "__main__":
    main()
