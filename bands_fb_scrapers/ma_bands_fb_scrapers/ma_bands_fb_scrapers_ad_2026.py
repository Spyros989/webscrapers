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

load_dotenv()

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

OUTPUT_DIR = Path("/home/deploy/data/scrapers/ma_cz_bands_ad_events")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

today = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = OUTPUT_DIR / f"ma_cz_bands_events_{today}.csv"

# ----------------------------
# LOAD BANDS FROM POSTGRES
# ----------------------------
query = text("""
    SELECT bandname, fb_link_events
    FROM cz_bands_ad_2026
    WHERE fb_link_events IS NOT NULL
""")

with engine.connect() as conn:
    df_bands = pd.read_sql(query, conn)

print(f"Loaded {len(df_bands)} bands from Postgres")

# ----------------------------
# SELENIUM SETUP
# ----------------------------
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

all_events = []
seen = set()

# ----------------------------
# SCRAPE EACH BAND PAGE
# ----------------------------
for _, row in df_bands.iterrows():
    bandname = row["bandname"]
    url = row["fb_link_events"]

    if not url:
        continue

    print(f"Scraping: {bandname}")

    try:
        driver.get(url)

        wait = WebDriverWait(driver, 15)
        wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@href, '/events/')]")
            )
        )

        event_elements = driver.find_elements(
            By.XPATH, "//a[contains(@href, '/events/')]"
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
                    "bandname": bandname,
                    "event_name": text,
                    "event_url": link,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            except Exception as ex:
                print("Event error:", ex)

    except Exception as ex:
        print(f"Failed band {bandname}: {ex}")

    time.sleep(2)  # small delay to avoid FB blocking

driver.quit()

# ----------------------------
# SAVE OUTPUT
# ----------------------------
df_events = pd.DataFrame(all_events)
df_events.to_csv(OUTPUT_FILE, index=False)

print(f"Done. Saved {len(df_events)} events → {OUTPUT_FILE}")
