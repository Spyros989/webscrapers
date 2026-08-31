import time
import pandas as pd

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By


EVENT_URL = "https://www.facebook.com/events/1524752919146224/"


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
# SCRAPE
# =========================================================

driver = create_driver()

try:
    print("Opening:", EVENT_URL)

    driver.get(EVENT_URL)

    time.sleep(5)

    # Get only the visible text
    visible_text = driver.find_element(
        By.TAG_NAME,
        "body"
    ).text

    # -----------------------------------------------------
    # CREATE DATAFRAME
    # -----------------------------------------------------

    df = pd.DataFrame([{
        "event_url": EVENT_URL,
        "visible_text": visible_text
    }])

    # -----------------------------------------------------
    # SAVE TO CSV
    # -----------------------------------------------------

    df.to_csv(
        "facebook_events.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("\nSaved to facebook_events.csv")

finally:
    driver.quit()
