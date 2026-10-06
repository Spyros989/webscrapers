from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import time
from pathlib import Path
import re

# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "kabinet_muz"

INPUT_FILE = DATA_DIR / "kabinet_muz_events_daily_clean.csv"
OUTPUT_FILE = DATA_DIR / "kabinet_nuz_events_daily_clean_fb_links.csv"

# ----------------------------
# Load CSV
# ----------------------------
df = pd.read_csv(INPUT_FILE)

# New column
df["event_url"] = ""

# ----------------------------
# PLAYWRIGHT
# ----------------------------
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
                timeout=30000
            )

            html = page.content()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            # -------------------------
            # 1. FIND FACEBOOK EVENT LINK
            # -------------------------

            fb_link = ""

            links = soup.find_all("a", href=True)

            for link in links:

                href = link["href"]

                if "facebook.com/events" in href:

                    fb_link = href

                    break

            # -------------------------
            # 2. DATE + TIME
            # -------------------------

            date_time = ""

            detail_block = soup.find(
                "div",
                class_="detail__info"
            )

            if detail_block:

                raw_text = detail_block.get_text(
                    " ",
                    strip=True
                )

                # Example:
                # středa 16. 9. 2026 začátek 20:00

                time_match = re.search(
                    r"začátek\s+(\d{1,2}):(\d{2})",
                    raw_text,
                    re.IGNORECASE
                )

                if time_match:

                    hour = int(time_match.group(1))
                    minute = int(time_match.group(2))

                    # Convert to AM / PM
                    am_pm = "AM" if hour < 12 else "PM"

                    hour_12 = hour % 12

                    if hour_12 == 0:
                        hour_12 = 12

                    date_time = f"{hour_12}:{minute:02d} {am_pm}"

            # -------------------------
            # 3. SAVE RESULTS
            # -------------------------

            df.at[idx, "event_url"] = (
                fb_link.rstrip("/") + "/"
                if fb_link
                else ""
            )

            df.at[idx, "date_time"] = date_time

            print(
                "FB:",
                "FOUND" if fb_link else "NONE"
            )

            print(
                "DATE/TIME:",
                date_time if date_time else "NONE"
            )

            # Small delay
            time.sleep(1)

        except Exception as e:

            print(f"ERROR: {e}")

    browser.close()


# ----------------------------
# SAVE CSV
# ----------------------------

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"Saved to:\n{OUTPUT_FILE}")
