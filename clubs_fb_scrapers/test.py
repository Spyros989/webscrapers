import time
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from dotenv import load_dotenv

load_dotenv()

# =========================================================
# CONFIG
# =========================================================
EVENT_URL = "https://www.facebook.com/events/2714463358928687"

# =========================================================
# CHROME SETUP (IMPORTANT: headless fixed your issue)
# =========================================================
options = uc.ChromeOptions()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=149)

# =========================================================
# FETCH PAGE
# =========================================================
print(f"Opening: {EVENT_URL}")
driver.get(EVENT_URL)

time.sleep(random.uniform(5, 8))

# =========================================================
# BASIC BLOCK CHECK
# =========================================================
page_text = driver.page_source.lower()

if "log in" in page_text or "create new account" in page_text:
    print("⚠️ Facebook login wall detected")
elif "event" not in page_text:
    print("⚠️ Page may be blocked or incomplete")
else:
    print("✅ Page loaded")

# =========================================================
# EXTRACTION HELPERS
# =========================================================

def safe_find_text(by, value):
    try:
        return driver.find_element(by, value).text.strip()
    except:
        return None

# ---------------------------------------------------------
# TITLE (usually reliable)
# ---------------------------------------------------------
title = safe_find_text(By.TAG_NAME, "h1")

# ---------------------------------------------------------
# DATE (Facebook often puts it in spans; heuristic search)
# ---------------------------------------------------------
date = None
spans = driver.find_elements(By.TAG_NAME, "span")

for s in spans:
    txt = s.text.strip()
    if any(month in txt.lower() for month in [
        "january","february","march","april","may","june",
        "july","august","september","october","november","december",
        "jan","feb","mar","apr","jun","jul","aug","sep","oct","nov","dec"
    ]):
        date = txt
        break

# ---------------------------------------------------------
# LOCATION (heuristic again)
# ---------------------------------------------------------
location = None

for s in spans:
    txt = s.text.strip()
    if "·" in txt and len(txt) < 80:
        location = txt
        break

# =========================================================
# OUTPUT
# =========================================================
print("\n===== FACEBOOK EVENT DATA =====")
print("Title    :", title)
print("Date     :", date)
print("Location :", location)

# =========================================================
# CLEANUP
# =========================================================
driver.quit()
