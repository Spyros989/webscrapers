from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from datetime import datetime
import time
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

FACEBOOK_EVENTS_URL = "https://www.facebook.com/profile.php?id=100063452266786&sk=events"

OUTPUT_FILE = "facebook_events_output.csv"

# =========================================================
# SELENIUM SETUP
# =========================================================

options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=options)

# =========================================================
# STATE DETECTION
# =========================================================

def classify_page(html: str):

    html = html.lower()

    if "log in" in html or "login" in html:
        return "LOGIN_WALL"

    if "content isn't available" in html:
        return "BLOCKED"

    if "/events" not in html and "event" not in html:
        return "NO_EVENTS_RENDERED"

    return "OK"

# =========================================================
# SCRAPE LOGIC
# =========================================================

events = []
seen = set()

try:

    print("Opening:", FACEBOOK_EVENTS_URL)

    driver.get(FACEBOOK_EVENTS_URL)

    time.sleep(8)

    print("\nCURRENT URL:", driver.current_url)
    print("TITLE:", driver.title)

    # Save debug snapshot (VERY IMPORTANT for FB debugging)
    with open("fb_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source[:200000])

    driver.save_screenshot("fb_debug.png")

    # -----------------------------------------------------
    # CLASSIFY PAGE
    # -----------------------------------------------------

    page_state = classify_page(driver.page_source)

    print("\nPAGE STATE:", page_state)

    # -----------------------------------------------------
    # HANDLE NON-SCRAPEABLE PAGES
    # -----------------------------------------------------

    if page_state in ["LOGIN_WALL", "BLOCKED", "NO_EVENTS_RENDERED"]:

        print(f"\nNo scrapeable events → {page_state}")

        result = {
            "source_url": FACEBOOK_EVENTS_URL,
            "status": page_state,
            "event_name": None,
            "event_url": None,
            "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        events.append(result)

    else:

        # -------------------------------------------------
        # EXTRACT EVENTS
        # -------------------------------------------------

        event_elements = driver.find_elements(
            By.XPATH,
            "//a[contains(@href,'/events')]"
        )

        print(f"\nFound event elements: {len(event_elements)}")

        for e in event_elements:

            try:

                title = e.text.strip()
                url = e.get_attribute("href")

                if not title or not url:
                    continue

                if url in seen:
                    continue

                seen.add(url)

                events.append({
                    "source_url": FACEBOOK_EVENTS_URL,
                    "status": "OK",
                    "event_name": title,
                    "event_url": url,
                    "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

                print(title)
                print(url)
                print("-" * 40)

            except Exception as ex:
                print("Event parse error:", ex)

finally:
    driver.quit()

# =========================================================
# SAVE OUTPUT
# =========================================================

df = pd.DataFrame(events)
df.to_csv(OUTPUT_FILE, index=False)

print("\nDONE")
print(f"Saved {len(df)} rows → {OUTPUT_FILE}")
