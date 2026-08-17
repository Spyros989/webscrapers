from email.mime import text
import time
import random
import pandas as pd
from sqlalchemy import create_engine, text
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
import os 
from dotenv import load_dotenv

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")
load_dotenv()
# =========================================================
# CONFIG
# =========================================================
os.system("pkill -f chromedriver")
os.system("pkill -f chrome")
# =========================================================
# CONFIG
# =========================================================
timestamp = datetime.now().strftime("%Y-%m-%d")
env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")
load_dotenv()

print("Loading .env from:", env_path)

load_dotenv(dotenv_path=env_path)

print("DB_HOST after load:", os.getenv("DB_HOST"))

# ----------------------------
# CONFIG
# ----------------------------
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / f"cz_clubs_fb_events_fetch_dates.csv"

with engine.connect() as conn:
    print("DB NAME:", conn.execute(text("SELECT current_database()")).fetchone())
    print("SCHEMA SEARCH PATH:", conn.execute(text("SHOW search_path")).fetchone())
# ----------------------------
# LOAD EVENTS URLs FROM POSTGRES
# ----------------------------
query = text("""
        select distinct ccfed.event_url ,ccfedc.status,ccfedc.event_date  
        from cz_clubs_fb_events_daily ccfed 
        left join cz_clubs_fb_events_dates_clean ccfedc on ccfed.event_url=ccfedc.url 
        where ccfedc.event_date is null and ccfedc.status is null
        """)

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(f"Loaded {len(df)} urls from Postgres")

# =========================================================
# CHROME SETUP
# =========================================================
def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.binary_location = "/snap/bin/chromium"
    driver = uc.Chrome(options=options, version_main=151)
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
    print("\n" + "=" * 80)
    print(f"\nProcessing: {url}")
    if index % 5 == 0 and index != 0:
        print("Restarting Chrome to prevent freeze...")
        try:
            driver.quit()
        except:
            pass
        driver = create_driver()
    try:
        driver.get(url)
        print("Page loaded")
        time.sleep(random.uniform(2, 5))
        # =====================================================
        # DATE EXTRACTION ONLY
        # =====================================================
        date = None
        print("Searching spans...")
        spans = driver.find_elements(By.TAG_NAME, "span")

        for s in spans:
            txt = s.text.strip()

            if any(month in txt.lower() for month in [
                "january","february","march","april","may","june",
                "july","august","september","october","november","december"
            ]) and ("pm" in txt.lower() or "am" in txt.lower() or "–" in txt):
                date = txt
                break

        # fallback
        if not date:
            for s in spans:
                txt = s.text.strip()
                if "2026" in txt:
                    date = txt
                    break

        results.append({
            "url": url,
            "date": date
        })

        print("✔ extracted ", date)
    except TimeoutException:
        print(f"Timeout loading {url}")
    except Exception as e:
        print("ERROR:", e)

        results.append({
            "url": url,
            "date": None
        })

# =========================================================
# SAVE OUTPUT
# =========================================================
driver.quit()

out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
