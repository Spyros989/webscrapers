import time
import random
from sqlalchemy import create_engine, text
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
import os 
from dotenv import load_dotenv

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
OUTPUT_FILE = OUTPUT_DIR / f"cz_clubs_fb_events_responds_daily.csv"


with engine.connect() as conn:
    print("DB NAME:", conn.execute(text("SELECT current_database()")).fetchone())
    print("SCHEMA SEARCH PATH:", conn.execute(text("SHOW search_path")).fetchone())
# ----------------------------
# LOAD EVENT URLs FROM POSTGRES
# ----------------------------
query = text("""
    select distinct event_url from cz_clubs_fb_events_daily ccfed
join cz_clubs_fb_events_dates_clean ccfedc on ccfed.event_url=ccfedc.url
where ccfedc.status = 'ok' and cast(ccfedc.event_date as date) >=date(now())  
    """)

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

print(f"Loaded {len(df)} urls from Postgres")


# =========================================================
# CHROME SETUP
# =========================================================
options = uc.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=149)

# =========================================================
# STORAGE
# =========================================================
results = []

# =========================================================
# LOOP URLS
# =========================================================
for index, row in df.iterrows():
    url = row["event_url"]

    print(f"\nProcessing: {url}")

    try:
        driver.get(url)
    except Exception as e:
        print("ERROR:", e)
        
        results.append({
            "url": url,
            "attendance": None,
            "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
        })

        continue

    time.sleep(random.uniform(10,25))

    attendance = None
    spans = driver.find_elements(By.TAG_NAME, "span")

    for s in spans:
        txt = s.text.strip()

        if "people responded" in txt.lower():
            attendance = txt
            break

    results.append({
        "url": url,
        "attendance": attendance,
        "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
    })

    print("✔ extracted:", attendance)

# =========================================================
# SAVE OUTPUT
# =========================================================
driver.quit()

out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
