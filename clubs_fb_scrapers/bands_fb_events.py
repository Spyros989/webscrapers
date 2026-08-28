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

# =========================================================
# KILL CHROMEDRIVER
# =========================================================
os.system("pkill -f chromedriver")
os.system("pkill -f chrome")

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
OUTPUT_FILE = OUTPUT_DIR / f"bands_fb_events.csv"

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
    SELECT band_id,band_name, fb_url_events_current
    FROM dim_bands WHERE manual_check <>'X' ORDER BY band_id asc;
    """)

with engine.connect() as conn:
    df_bands = pd.read_sql(query, conn)

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
# RESULTS
# =========================================================

all_events = []
seen = set()

# ----------------------------
# SCRAPE EACH CLUB PAGE
# ----------------------------
for index, row in df_bands.iterrows():

    band_name = row["band_name"]
    url = row["fb_url_events_current"]
    band_id = row["band_id"]
    if not url:
        all_events.append({
	    "band_id": band_id,
            "band_name":band_name,
            "event_name": "n/a",
            "event_url": "n/a",
            "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
        })
        continue

    print(f"\nProcessing: {band_name}, id:{band_id}")

    if index % 5 == 0 and index != 0:
        print("Restarting Chrome to prevent freeze...")

        try:
            driver.quit()
        except:
            pass

        driver = create_driver()

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 15)

        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@href, '/events/')]")
            )
        )

        event_elements = driver.find_elements(
            By.XPATH,
            "//a[contains(@href, '/events/')]"
        )

        for e in event_elements:
            try:
                text = e.text.strip()
                link = e.get_attribute("href")

                if not text or not link:
                    continue

                if link in seen:
                    continue

                seen.add(link)

                all_events.append({
		    "band_id": band_id,
                    "band_name": band_name,
                    "event_name": text,
                    "event_url": link,
                    "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
                })

            except Exception as ex:
                print("Event error:", ex)

    except Exception as ex:

        print(f"Failed band {band_name}: {ex}")

        all_events.append({
	    "band_id": band_id,
            "band_name": band_name,
            "event_name": "n/a",
            "event_url": "n/a",
            "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
        })

    time.sleep(2)

try:
    driver.quit()
except Exception:
    pass

driver = create_driver()
# ----------------------------
# SAVE OUTPUT
# ----------------------------
df_events = pd.DataFrame(all_events)
df_events.to_csv(OUTPUT_FILE, index=False)

print(f"Done. Saved {len(df_events)} events → {OUTPUT_FILE}")
