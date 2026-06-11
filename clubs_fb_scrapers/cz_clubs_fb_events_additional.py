import os
import time
import random
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from pathlib import Path
from datetime import datetime
import subprocess

# =========================================================
# KILL OLD CHROME SESSIONS
# =========================================================
def kill_chrome():
    subprocess.run(["pkill", "-f", "chromedriver"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "chrome"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

kill_chrome()

# =========================================================
# CONFIG
# =========================================================
timestamp = datetime.now().strftime("%Y%m%d")
BASE_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")
INPUT_FILE = BASE_DIR / "cz_clubs_fb_events_2026-06-10.csv"
OUTPUT_FILE = BASE_DIR / f"cz_clubs_fb_events_dates_additional_{timestamp}.csv"

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

results = []

# =========================================================
# HELPERS
# =========================================================
def safe(span_list, i):
    try:
        return span_list[i].text.strip()
    except:
        return None

# =========================================================
# LOOP
# =========================================================
for index, row in df.iterrows():

    url = row["event_url"]
    print(f"\nProcessing: {url}")

    try:
        driver.get(url)
        time.sleep(random.uniform(5, 8))

        spans = driver.find_elements(By.TAG_NAME, "span")

        # =====================================================
        # INDEX BASED EXTRACTION
        # =====================================================
        DATE_INDEX = 31
        NAME_INDEX = 50
        LOCATION_INDEX = 52
        ATTENDANCE_INDEX = 73

        event_date = safe(spans, DATE_INDEX)
        event_name = safe(spans, NAME_INDEX)
        event_location = safe(spans, LOCATION_INDEX)
        event_attendance = safe(spans, ATTENDANCE_INDEX)

        # =====================================================
        # FALLBACK DATE
        # =====================================================
        if not event_date or "log in" in (event_date or "").lower():
            for s in spans:
                txt = s.text.strip()
                low = txt.lower()
                if any(month in low for month in [
                    "january","february","march","april","may","june",
                    "july","august","september","october","november","december"
                ]) and ("pm" in low or "am" in low or "–" in txt):
                    event_date = txt
                    break

        # =====================================================
        # FALLBACK ATTENDANCE
        # =====================================================
        if not event_attendance:
            for s in spans:
                txt = s.text.strip().lower()
                if "people responded" in txt:
                    event_attendance = txt
                    break

        results.append({
            "url": url,
            "date": event_date,
            "name": event_name,
            "location": event_location,
            "attendance": event_attendance
        })

        print("✔ extracted:", event_name, "|", event_date)

    except Exception as e:
        print("ERROR:", e)
        results.append({
            "url": url,
            "date": None,
            "name": None,
            "location": None,
            "attendance": None
        })

# =========================================================
# CLEANUP
# =========================================================
driver.quit()

out_df = pd.DataFrame(results)
out_df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
