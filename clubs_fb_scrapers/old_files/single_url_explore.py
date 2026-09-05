import time
from pathlib import Path
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# =========================================================
# KILL CHROMEDRIVER
# =========================================================
os.system("pkill -f chromedriver")
os.system("pkill -f chrome")

EVENT_URL = "https://www.facebook.com/events/1316059683990672/"


# =========================================================
# CHROME SETUP
# =========================================================

def create_driver():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    options.binary_location = "/snap/bin/chromium"

    driver = uc.Chrome(
        options=options,
        version_main=151
    )

    driver.set_page_load_timeout(30)

    return driver


# =========================================================
# MAIN
# =========================================================

driver = create_driver()

try:
    print(f"Opening:\n{EVENT_URL}\n")

    driver.get(EVENT_URL)

    time.sleep(5)

    # -----------------------------------------------------
    # BASIC PAGE INFORMATION
    # -----------------------------------------------------

    print("=" * 60)
    print("BASIC PAGE INFO")
    print("=" * 60)

    print("Title:", driver.title)
    print("Current URL:", driver.current_url)

    # -----------------------------------------------------
    # VISIBLE TEXT
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("VISIBLE TEXT")
    print("=" * 60)

    body_text = driver.find_element(By.TAG_NAME, "body").text

    print(body_text)

    # -----------------------------------------------------
    # LINKS
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("LINKS")
    print("=" * 60)

    links = driver.find_elements(By.TAG_NAME, "a")

    print(f"Found {len(links)} links\n")

    for link in links:
        try:
            text = link.text.strip()
            href = link.get_attribute("href")

            if text or href:
                print("TEXT:", text)
                print("HREF:", href)
                print("-" * 40)

        except Exception:
            continue

    # -----------------------------------------------------
    # SPANS
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("SPAN TEXT")
    print("=" * 60)

    spans = driver.find_elements(By.TAG_NAME, "span")

    print(f"Found {len(spans)} spans\n")

    for span in spans:
        try:
            text = span.text.strip()

            if text:
                print(text)

        except Exception:
            continue

    # -----------------------------------------------------
    # PAGE SOURCE
    # -----------------------------------------------------

    print("\n" + "=" * 60)
    print("PAGE SOURCE")
    print("=" * 60)

    source = driver.page_source

    print("Page source length:", len(source))

    # Save it so we can inspect it later
    output_file = Path("facebook_event_source.html")

    output_file.write_text(
        source,
        encoding="utf-8"
    )

    print("Saved page source to:", output_file.resolve())

finally:
    driver.quit()
