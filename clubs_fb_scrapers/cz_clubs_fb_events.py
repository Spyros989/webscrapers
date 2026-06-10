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

today = datetime.now().strftime("%Y-%m-%d")
OUTPUT_FILE = OUTPUT_DIR / f"cz_clubs_fb_events_{today}.csv"

with engine.connect() as conn:
    print("DB NAME:", conn.execute(text("SELECT current_database()")).fetchone())
    print("SCHEMA SEARCH PATH:", conn.execute(text("SHOW search_path")).fetchone())
# ----------------------------
# LOAD BANDS FROM POSTGRES
# ----------------------------
query = text("""
    SELECT club_name, facebook_events_current
    FROM cz_clubs_fb_links WHERE facebook_events_current IS NOT NULL;
    """)

with engine.connect() as conn:
    df_clubs = pd.read_sql(query, conn)

print(f"Loaded {len(df_clubs)} clubs from Postgres")

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
for _, row in df_clubs.iterrows():
    club_name = row["club_name"]
    url = row["facebook_events_current"]

    if not url:
        continue

    print(f"Scraping: {club_name}")

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
                    "club_name": club_name,
                    "event_name": text,
                    "event_url": link,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            except Exception as ex:
                print("Event error:", ex)

    except Exception as ex:
        print(f"Failed club {club_name}: {ex}")

    time.sleep(2)  # small delay to avoid FB blocking

driver.quit()

# ----------------------------
# SAVE OUTPUT
# ----------------------------
df_events = pd.DataFrame(all_events)
df_events.to_csv(OUTPUT_FILE, index=False)

print(f"Done. Saved {len(df_events)} events → {OUTPUT_FILE}")
