import pandas as pd
from sqlalchemy import create_engine, text
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from pathlib import Path
import time
import os
from dotenv import load_dotenv
import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
import subprocess
import re

HOME = Path.home()
env_path = (
	HOME
	/"webscrapers"
	/"bands_fb_scrapers"
	/"ma_bands_fb_scrapers"
	/".env"
)
load_dotenv()
OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_bands_fb_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"bands_fb_events_deltas.csv"

print("Loading .env from:", env_path)
load_dotenv(dotenv_path=env_path)

print("DB_HOST after load:", os.getenv("DB_HOST"))

# ----------------------------
# ENVIRONMENT VARIABLES CONFIG
# ----------------------------
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
# ----------------------------
# CREATE ENGINE TO CONNECT TO POSTGRES
# ----------------------------
with engine.connect() as conn:
    print("DB NAME:", conn.execute(text("SELECT current_database()")).fetchone())
    print("SCHEMA SEARCH PATH:", conn.execute(text("SHOW search_path")).fetchone())
# ----------------------------
# LOAD BANDS FROM POSTGRES
# ----------------------------
query = text("""
select
db.band_id
,db.band_name
,db.fb_url_events_current
from dim_bands db
inner join bands_fb_events_errors bfee on db.band_id = bfee.band_id limit 1""")

with engine.connect() as conn:
    df_bands = pd.read_sql(query, conn)
df_bands= df_bands.sample(frac=1).reset_index(drop=True)
print(f"Loaded {len(df_bands)} bands from Postgres")

# =========================================================
# CHROME SETUP
# =========================================================

SCRAPER_PROFILE = Path.home() / "fb_scraper_profile"


def get_chromium_major_version():

    output = subprocess.check_output(
        ["/snap/bin/chromium", "--version"],
        text=True
    )

    print("Chromium:", output.strip())

    match = re.search(r"(\d+)\.", output)

    if not match:
        raise RuntimeError(
            f"Could not determine Chromium version: {output}"
        )

    return int(match.group(1))


def create_driver():

    options = uc.ChromeOptions()

#    options.add_argument("--headless=new")
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
# RESULTS
# =========================================================

all_events = []
seen = set()
# =========================================================
# DEBUG — TEST ONE URL
# =========================================================

test_url = "https://www.facebook.com/Melodka.cz/events?locale=cs_CZ"

print("\n" + "=" * 80)
print("TESTING URL")
print("=" * 80)
print("URL:", test_url)
try:

    driver.get(test_url)

    time.sleep(5)

    print("\n--- PAGE INFO ---")
    print("Requested URL:", repr(test_url))
    print("Current URL  :", repr(driver.current_url))
    print("Title        :", repr(driver.title))

    # -----------------------------------------------------
    # BODY TEXT
    # -----------------------------------------------------

    body = driver.find_element(By.TAG_NAME, "body").text

    print("\n--- BODY TEXT ---")
    print("Length:", len(body))
    print(body[:3000])

    # -----------------------------------------------------
    # EVENT LINKS
    # -----------------------------------------------------

    print("\n--- EVENT LINKS ---")

    event_elements = driver.find_elements(
        By.XPATH,
        "//a[contains(@href, '/events/')]"
    )

    print("Event elements found:", len(event_elements))

    for i, e in enumerate(event_elements, start=1):

        try:
            text = e.text.strip()
            link = e.get_attribute("href")

            print(f"\nEVENT #{i}")
            print("TEXT:", repr(text))
            print("LINK:", repr(link))

        except Exception as ex:
            print("Error reading event:", ex)

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("Requested :", repr(test_url))
    print("Current   :", repr(driver.current_url))
    print("Title     :", repr(driver.title))
    print("Body len  :", len(body))
    print("Events    :", len(event_elements))

except Exception as ex:

    print("\n" + "=" * 80)
    print("FAILED")
    print("=" * 80)

    print("Exception type:", type(ex).__name__)
    print("Exception:", str(ex))

    try:
        print("\n--- PAGE AFTER FAILURE ---")
        print("Current URL:", repr(driver.current_url))
        print("Title:", repr(driver.title))

        body = driver.find_element(By.TAG_NAME, "body").text

        print("Body length:", len(body))
        print("\nBODY:")
        print(body[:3000])

    except Exception as inner_ex:
        print("Could not inspect page:", inner_ex)

finally:

    try:
        driver.quit()
    except Exception:
        pass
