import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
import os

os.system("pkill -f chromedriver")
os.system("pkill -f chrome")
# =========================================================
# CONFIG
# =========================================================
timestamp = datetime.now().strftime("%Y%m%d")
BASE_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")
INPUT_FILE = BASE_DIR / "cz_clubs_fb_events_dates_20260615_future.csv"
OUTPUT_FILE = BASE_DIR / f"cz_clubs_fb_events_responds_daily.csv"
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
    url = row["url"]

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
        "extraction_datetime": datetime.now().strftime("%Y%m%d_%H%M%S")
    })

    print("✔ extracted:", attendance)

# =========================================================
# SAVE OUTPUT
# =========================================================
driver.quit()

out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
