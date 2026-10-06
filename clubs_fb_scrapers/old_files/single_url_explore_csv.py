import time
import pandas as pd
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from pathlib import Path
import os
from dotenv import load_dotenv
import subprocess
import re
import random

# =========================================================
# CONFIG
# =========================================================

HOME = Path.home()

env_path = (
    HOME
    / "webscrapers"
    / "bands_fb_scrapers"
    / "ma_bands_fb_scrapers"
    / ".env"
)

load_dotenv()
load_dotenv(dotenv_path=env_path)
EVENT_URL = "https://www.facebook.com/events/1302513041345763/"


# =========================================================
# CHROME SETUP
# =========================================================

SCRAPER_PROFILE = (
    Path.home() / "fb_scraper_profile"
)
def get_chromium_major_version():

    output = subprocess.check_output(
        ["/snap/bin/chromium", "--version"],
        text=True
    )

    print("Chromium:", output.strip())

    match = re.search(
        r"(\d+)\.",
        output
    )

    if not match:

        raise RuntimeError(
            f"Could not determine Chromium version: {output}"
        )

    return int(match.group(1))

def create_driver():
    options = uc.ChromeOptions()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

     # Persistent scraper profile
    options.add_argument(
        f"--user-data-dir={SCRAPER_PROFILE}"
    )

    options.binary_location = "/snap/bin/chromium"

    chrome_version = get_chromium_major_version()

    print("Chrome profile:", SCRAPER_PROFILE)
    print("Chrome version:", chrome_version)

    driver = uc.Chrome(
        options=options,
        version_main=chrome_version
    )

    driver.set_page_load_timeout(30)

# =========================================================
# SCRAPE
# =========================================================
results = []
driver = create_driver()

try:
    print("Opening:", EVENT_URL)

    driver.get(EVENT_URL)

    time.sleep(5)

    # Get only the visible text
    visible_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    results.append({
            "event_url": url,
            "visible_text": visible_text
        })    
    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------
except Exception as e:
        print(
            "ERROR:",
            e
        )
    driver.quit()
    
    out_df = pd.DataFrame(results)
    # -----------------------------------------------------
    # SAVE TO CSV
    # -----------------------------------------------------

    out_df.to_csv(
        "facebook_events.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nSaved to facebook_events.csv")
