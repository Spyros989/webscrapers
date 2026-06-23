from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path


# =========================
# FILE PATHS
# =========================

INPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/bajkazylhk/bajkazylhk_events_clean.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/bajkazylhk/bajkazylhk_events_clean_fb_links.csv")

# =========================
# Load CSV
df = pd.read_csv(INPUT_FILE)
# ========================

# New column
df["facebook_event"] = ""

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for idx, row in df.iterrows():

        url = row["link"]

        print(f"Checking: {url}")

        try:

            page.goto(url, wait_until="networkidle", timeout=30000)

            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            fb_link = ""

            # Find all links
            for a in soup.find_all("a", href=True):

                href = a["href"]

                # Facebook event/page detection
                if "facebook.com" in href:
                    fb_link = href
                    break

            df.at[idx, "facebook_event"] = fb_link

            print("FOUND" if fb_link else "NO FB LINK")

            # small delay
            time.sleep(1)

        except Exception as e:

            print(f"ERROR: {e}")

    browser.close()

# Save final CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"Saved to:\n{OUTPUT_FILE}")
