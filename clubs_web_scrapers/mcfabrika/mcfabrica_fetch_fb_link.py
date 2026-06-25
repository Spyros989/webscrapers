from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path


# =========================
# FILE PATHS
# =========================

INPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_daily_clean.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_daily_clean_fb_links.csv")

# LOAD CSV
df = pd.read_csv(INPUT_FILE)

# NEW COLUMN
df["event_url"] = ""

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    for idx, row in df.iterrows():

        url = row["web_link"]

        print(f"\nChecking: {url}")

        try:

            page.goto(
                url,
                wait_until="networkidle",
                timeout=60000
            )

            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            fb_link = ""

            # FIND TARGET DIV
            action_div = soup.find(
                "div",
                class_="action-component my-3"
            )

            if action_div:

                # FIND FACEBOOK LINK INSIDE
                links = action_div.find_all("a", href=True)

                for a in links:

                    href = a.get("href", "")

                    if "facebook.com" in href:

                        fb_link = href
                        break

            df.at[idx, "event_url"] = fb_link

            if fb_link:
                print("FOUND FB EVENT!")
            else:
                print("NO FB EVENT..")

            # small delay
            time.sleep(1)

        except Exception as e:

            print(f"ERROR: {e}")

    browser.close()

# SAVE FINAL CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"Saved to:\n{OUTPUT_FILE}")
