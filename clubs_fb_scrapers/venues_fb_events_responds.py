import time
import random
from sqlalchemy import create_engine, text
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
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
	/"webscrapers"
	/"bands_fb_scrapers"
	/"ma_bands_fb_scrapers"
	/".env"
)
load_dotenv()
OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"venues_fb_events_responds.csv"
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
# LOAD EVENT URLs FROM POSTGRES
# ----------------------------
query = text("""
select
dvfec.venue_id
,dvfec.event_url
from dim_venues_fb_events dvfe
inner join dim_venues_fb_events_contents dvfec
on dvfec.event_url = dvfe.event_url
and dvfec.venue_id = dvfe.venue_id
where  status ='ok'
and  cast(dvfec.event_date as date) >=date(now())
group by dvfec.venue_id,dvfec.event_url""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(f"Loaded {len(df)} urls from Postgres")


# =========================================================
# CHROME SETUP
# =========================================================
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
# STORAGE
# =========================================================
results = []

# =========================================================
# LOOP URLS
# =========================================================

for index, row in df.iterrows():

    url = row["event_url"]
    venue_id = row["venue_id"]
    counter = index +1
    print("\n" + "=" * 80)
    print(f"Processing: {url} , {counter} out of {len(df)}")

    attendance = None

    # Restart Chrome every 5 URLs
    if index % 5 == 0 and index != 0:

        print("Restarting Chrome to prevent freeze...")

        try:
            driver.quit()
        except Exception:
            pass

        driver = create_driver()

    try:

        driver.get(url)

        print("Page loaded")

        # Give Facebook a moment to finish rendering
        time.sleep(random.uniform(2, 5))

        print("Searching spans...")

        spans = driver.find_elements(By.TAG_NAME, "span")

        for s in spans:

            txt = s.text.strip()

            if "people responded" in txt.lower():

                attendance = txt
                break

        results.append({
            "venue_id": venue_id,
            "event_url": url,
            "attendance": attendance,
            "extraction_datetime": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        })

        print("✔ extracted:", attendance)

    except TimeoutException:

        print(f"Timeout loading {url}")

        results.append({
            "venue_id": venue_id,
            "event_url": url,
            "attendance": None,
            "extraction_datetime": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "error": "timeout"
        })

        continue

    except Exception as e:

        print("ERROR:", e)

        results.append({
            "venue_id": venue_id,
            "event_url": url,
            "attendance": None,
            "extraction_datetime": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "error": str(e)
        })

        continue
# =========================================================
# SAVE OUTPUT
# =========================================================
driver.quit()

out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
