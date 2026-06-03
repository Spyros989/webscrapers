import pandas as pd
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from pathlib import Path
from datetime import datetime
from urllib.parse import quote_plus

# =========================================================
# CONFIG
# =========================================================
today = datetime.today().strftime("%Y-%m-%d")

BASE_DIR = Path("/home/deploy/data/scrapers/ma_cz_bands_ad_events")
INPUT_FILE = BASE_DIR / "ma_cz_bands_events_2026-06-03.csv"

OUTPUT_DIR = BASE_DIR / "google_search_events"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_PATH = OUTPUT_DIR / f"ma_cz_bands_google_search_{today}.csv"

df = pd.read_csv(INPUT_FILE)

# =========================================================
# CHROME SETUP
# =========================================================
options = uc.ChromeOptions()
options.add_argument("--window-size=1920,1080")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--headless=new")

driver = uc.Chrome(version_main=148,options=options)

# =========================================================
# STORAGE
# =========================================================
results = []

# =========================================================
# SAVE FUNCTION
# =========================================================
def save_checkpoint():
    pd.DataFrame(results).to_csv(OUTPUT_PATH, index=False)
    print(f"💾 Saved {len(results)} rows")

# =========================================================
# MAIN LOOP
# =========================================================
for index, row in df.iterrows():

    bandname = row["bandname"]
    event_name = row["event_name"]

    print(f"\n🔎 Searching: {event_name}")

    try:
        # ----------------------------
        # Build query
        # ----------------------------
        query = f'{bandname} "{event_name}"'
        url = f"https://www.google.com/search?q={quote_plus(query)}"

        driver.get(url)
        time.sleep(random.uniform(8, 15))

        # ----------------------------
        # Detect blocking pages
        # ----------------------------
        page_text = driver.page_source.lower()

        if any(x in page_text for x in [
            "unusual traffic",
            "before you continue",
            "consent",
            "verify"
        ]):
            print("⚠️ Block / consent page detected")

            results.append({
                "bandname": bandname,
                "event_name": event_name,
                "status": "blocked",
                "results": None,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            })

            continue

        # ----------------------------
        # Extract SERP results
        # ----------------------------
        blocks = driver.find_elements(By.CSS_SELECTOR, "div.g")

        if not blocks:
            print("⚠️ No SERP results found")

            results.append({
                "bandname": bandname,
                "event_name": event_name,
                "status": "no_results",
                "results": None,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
            })

            continue

        extracted = []

        for b in blocks[:5]:
            try:
                title = b.text.split("\n")[0]
                snippet = "\n".join(b.text.split("\n")[1:3])

                extracted.append({
                    "title": title,
                    "snippet": snippet
                })

            except:
                continue

        results.append({
            "bandname": bandname,
            "event_name": event_name,
            "status": "ok",
            "results": extracted,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        })

        print("✔ Captured")

    except Exception as ex:

        print(f"❌ Error: {ex}")

        results.append({
            "bandname": bandname,
            "event_name": event_name,
            "status": "error",
            "results": None,
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S")
        })

    # ----------------------------
    # checkpoint save
    # ----------------------------
    if len(results) % 25 == 0:
        save_checkpoint()

# =========================================================
# FINAL SAVE
# =========================================================
save_checkpoint()

driver.quit()

print("\nDONE")
