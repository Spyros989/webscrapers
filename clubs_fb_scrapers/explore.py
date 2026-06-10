import time
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

# =========================================================
# CONFIG
# =========================================================
EVENT_URL = "https://www.facebook.com/events/1234140511804108/"

# =========================================================
# CHROME SETUP
# =========================================================
options = uc.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options)  # IMPORTANT: no version pin

# =========================================================
# LOAD PAGE
# =========================================================
print(f"\nOpening: {EVENT_URL}")
driver.get(EVENT_URL)

time.sleep(random.uniform(5, 8))

# =========================================================
# CHECK PAGE STATUS
# =========================================================
page_text = driver.page_source.lower()

if "log in" in page_text:
    print("⚠️ Login wall detected")
elif "event" not in page_text:
    print("⚠️ Page may be blocked or incomplete")
else:
    print("✅ Page loaded")

# =========================================================
# SPANS
# =========================================================
spans = driver.find_elements(By.TAG_NAME, "span")

print("\n===== ALL SPANS (LIVE VIEW) =====\n")

for i, s in enumerate(spans):
    txt = s.text.strip()
    if txt:
        print(f"{i:03d} | {txt}")

# =========================================================
# DATE CANDIDATES
# =========================================================
print("\n===== DATE CANDIDATES =====\n")

for s in spans:
    txt = s.text.strip()
    if not txt:
        continue

    if (
        "2026" in txt
        or "pm" in txt.lower()
        or "am" in txt.lower()
        or "–" in txt
    ):
        print(">>", txt)

# =========================================================
# FINAL EXTRACTION
# =========================================================
date = None

for s in spans:
    txt = s.text.strip()

    if any(month in txt.lower() for month in [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december",
        "jan","feb","mar","apr","jun","jul","aug","sep","oct","nov","dec"
    ]) and ("pm" in txt.lower() or "am" in txt.lower() or "–" in txt):
        date = txt
        break

if not date:
    for s in spans:
        txt = s.text.strip()
        if "2026" in txt:
            date = txt
            break

# =========================================================
# OUTPUT
# =========================================================
print("\n===== FINAL RESULT =====")
print("Date:", date)

driver.quit()
