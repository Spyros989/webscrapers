import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")
load_dotenv()
# =========================================================
# CONFIG
# =========================================================
timestamp = datetime.now().strftime("%Y%m%d")
BASE_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")
INPUT_FILE = BASE_DIR / "cz_clubs_fb_events_daily_deltas_20260619.csv"
OUTPUT_FILE = BASE_DIR / f"cz_clubs_fb_events_dates_{timestamp}.csv"
# CSV must have a column like: "url"
df = pd.read_csv(INPUT_FILE)

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
        time.sleep(random.uniform(5, 8))

        # =====================================================
        # DATE EXTRACTION ONLY
        # =====================================================
        date = None
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

        print("✔ extracted, date")

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
