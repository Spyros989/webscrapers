from playwright.sync_api import sync_playwright
import pandas as pd
import time
import random
from pathlib import Path
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================
timestamp = datetime.now().strftime("%Y%m%d")
BASE_DIR = Path("/home/deploy/data/scrapers/metal_archives")
INPUT_FILE = BASE_DIR / "cz_metal_bands_edited_dedup_20260607.csv"
# Change these however you want
START_INDEX = 0
END_INDEX = 1111

SAVE_EVERY = 25
OUTPUT_FILE = BASE_DIR / f"cz_metal_bands_fb_links_{timestamp}.csv"

# =========================================================
# LOAD DATA
# =========================================================

df = pd.read_csv(INPUT_FILE)

# Keep only desired range
df = df.iloc[START_INDEX:END_INDEX].copy()

# Add Facebook column if missing
if "Facebook" not in df.columns:
    df["Facebook"] = None

print(f"Loaded rows {START_INDEX} -> {END_INDEX}")
print(f"Total rows to scrape: {len(df)}")

# =========================================================
# PLAYWRIGHT
# =========================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    # -----------------------------------------------------
    # Establish trusted session
    # -----------------------------------------------------

    page.goto("https://www.metal-archives.com")

    print("Waiting for Cloudflare/session...")
    page.wait_for_timeout(10000)

    # =====================================================
    # MAIN LOOP
    # =====================================================

    for idx, row in df.iterrows():

        band_name = row["BandName"]
        band_url = row["BandURL"]

        print("\n================================================")
        print(f"[{idx}] {band_name}")
        print(band_url)

        try:

            # -------------------------------------------------
            # Open band page
            # -------------------------------------------------

            page.goto(
                band_url,
                timeout=60000
            )

            page.wait_for_load_state(
                "networkidle"
            )

            # -------------------------------------------------
            # Open "Related links" tab
            # -------------------------------------------------

            page.get_by_role(
                "link",
                name="Related links"
            ).click()

            # Wait for links table
            page.wait_for_selector(
                "table#linksTablemain",
                timeout=10000
            )

            # -------------------------------------------------
            # Extract Facebook
            # -------------------------------------------------

            facebook_url = None

            locator = page.locator(
                "table#linksTablemain "
                "a[title='Go to: Facebook']"
            )

            if locator.count() > 0:

                facebook_url = locator.first.get_attribute(
                    "href"
                )

            df.at[idx, "Facebook"] = facebook_url

            print("Facebook:")
            print(facebook_url)

        except Exception as e:

            print("ERROR:")
            print(e)

        # -------------------------------------------------
        # Checkpoint save
        # -------------------------------------------------

        if (idx + 1) % SAVE_EVERY == 0:

            df.to_csv(
                OUTPUT_FILE,
                index=False
            )

            print("\nCheckpoint saved.")

        # -------------------------------------------------
        # Polite delay
        # -------------------------------------------------

        time.sleep(
            random.uniform(3, 6)
        )

    browser.close()

# =========================================================
# FINAL SAVE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nDONE")
print(f"Saved to: {OUTPUT_FILE}")
