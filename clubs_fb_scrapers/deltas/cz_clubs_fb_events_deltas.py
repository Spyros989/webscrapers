from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from pathlib import Path
import time

# =========================================================
# CONFIG
# =========================================================

FACEBOOK_EVENTS_URL = "https://www.facebook.com/profile.php?id=100063452266786&sk=events"

OUTPUT_HTML = "fb_debug.html"
OUTPUT_SCREENSHOT = "fb_debug.png"

# =========================================================
# SELENIUM SETUP
# =========================================================

options = Options()

# IMPORTANT: comment this out if debugging visually on server with GUI

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")

service = Service()

driver = webdriver.Chrome(service=service, options=options)
try:

    print("Opening:", FACEBOOK_EVENTS_URL)

    driver.get(FACEBOOK_EVENTS_URL)

    time.sleep(8)  # give Facebook time to render

    print("\nCURRENT URL:")
    print(driver.current_url)

    print("\nPAGE TITLE:")
    print(driver.title)

    # =====================================================
    # SCREENSHOT DEBUG
    # =====================================================

    driver.save_screenshot(OUTPUT_SCREENSHOT)
    print(f"\nScreenshot saved → {OUTPUT_SCREENSHOT}")

    # =====================================================
    # HTML DEBUG
    # =====================================================

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(driver.page_source[:200000])

    print(f"HTML saved → {OUTPUT_HTML}")

    # =====================================================
    # OPTIONAL: wait for manual inspection
    # =====================================================

    input("\nPress ENTER to close browser...")

except Exception as e:

    print("\nERROR:")
    print(e)

print("EVENT LINKS IN HTML:")
print("events/" in driver.page_source.lower())

print("event keyword count:")
print(driver.page_source.lower().count("event"))

finally:

    driver.quit()

