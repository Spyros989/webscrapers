from playwright.sync_api import sync_playwright
import json
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

BASE = (
    "https://www.metal-archives.com/"
    "browse/ajax-country/c/CZ/json/1"
)

# safer path handling
OUTPUT_DIR = Path("/home/deploy/data/scrapers/metal_archives")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "cz_metal_bands_raw.csv"

all_rows = []

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    # Establish trusted session
    page.goto("https://www.metal-archives.com")

    print("Waiting for Cloudflare/session...")
    page.wait_for_timeout(10000)

    start = 0
    length = 200

    while True:

        url = (
            f"{BASE}"
            f"?sEcho=1"
            f"&iDisplayStart={start}"
            f"&iDisplayLength={length}"
        )

        print(f"Fetching rows starting at {start}")

        page.goto(url)

        page.wait_for_timeout(3000)

        text = page.locator("body").inner_text()

        data = json.loads(text)

        rows = data["aaData"]

        if not rows:
            break

        all_rows.extend(rows)

        total = data["iTotalRecords"]

        print(f"Retrieved {len(rows)} rows")
        print(f"Total records: {total}")

        start += length

        time.sleep(3)

        if start >= total:
            break

    browser.close()

df = pd.DataFrame(
    all_rows,
    columns=["Band", "Genre", "Location", "Status"]
)

df.to_csv(OUTPUT_FILE, index=False)

print(df.head())
print("Done.")
