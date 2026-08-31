import time
import random
import pandas as pd

from sqlalchemy import create_engine, text

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import undetected_chromedriver as uc

from pathlib import Path
import os
from dotenv import load_dotenv

import subprocess
import re


# =========================================================
# KILL CHROMEDRIVER
# =========================================================

os.system("pkill -f chromedriver")
os.system("pkill -f chrome")


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

OUTPUT_DIR = Path(
    "/home/deploy/data/scrapers/cz_bands_fb_events"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_FILE = OUTPUT_DIR / "bands_fb_events_contents.csv"

print("Loading .env from:", env_path)

load_dotenv(dotenv_path=env_path)

print("DB_HOST after load:", os.getenv("DB_HOST"))


# =========================================================
# DATABASE CONFIG
# =========================================================

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")


engine = create_engine(
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# =========================================================
# TEST DATABASE CONNECTION
# =========================================================

with engine.connect() as conn:

    print(
        "DB NAME:",
        conn.execute(
            text("SELECT current_database()")
        ).fetchone()
    )

    print(
        "SCHEMA SEARCH PATH:",
        conn.execute(
            text("SHOW search_path")
        ).fetchone()
    )


# =========================================================
# LOAD EVENT URLs FROM POSTGRES
# =========================================================

query = text("""
    SELECT
        dbfed.band_id,
        dbfed.url
    FROM dim_bands_fb_events_dates dbfed
    WHERE dbfed.date IS NULL limit 100;
""")


with engine.connect() as conn:

    df = pd.read_sql(
        query,
        conn
    )


print(f"Loaded {len(df)} urls from Postgres")


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

    return driver


driver = create_driver()


# =========================================================
# STORAGE
# =========================================================

results = []


# =========================================================
# LOOP URLS
# =========================================================

for index, row in df.iterrows():

    url = row["url"]
    band_id = row["band_id"]

    print("\n" + "=" * 80)
    print(f"Processing: {url}")


    # Restart Chrome every 5 URLs
    if index % 5 == 0 and index != 0:

        print(
            "Restarting Chrome to prevent freeze..."
        )

        try:
            driver.quit()
        except:
            pass

        driver = create_driver()


    try:

        # -------------------------------------------------
        # OPEN PAGE
        # -------------------------------------------------

        driver.get(url)

        print("Page loaded")

        time.sleep(
            random.uniform(2, 5)
        )


        # -------------------------------------------------
        # GET ALL VISIBLE TEXT
        # -------------------------------------------------

        visible_text = driver.find_element(
            By.TAG_NAME,
            "body"
        ).text


        # -------------------------------------------------
        # STORE RESULT
        # -------------------------------------------------

        results.append({
            "band_id": band_id,
            "url": url,
            "visible_text": visible_text
        })


        print(
            "✔ extracted",
            len(visible_text),
            "characters"
        )


    except TimeoutException:

        print(
            f"Timeout loading {url}"
        )

        results.append({
            "band_id": band_id,
            "url": url,
            "visible_text": None
        })


    except Exception as e:

        print(
            "ERROR:",
            e
        )

        results.append({
            "band_id": band_id,
            "url": url,
            "visible_text": None
        })


# =========================================================
# SAVE OUTPUT
# =========================================================

driver.quit()


out_df = pd.DataFrame(results)


out_df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print("\nDONE")
print(
    f"Saved {len(out_df)} rows to:"
)
print(OUTPUT_FILE)
