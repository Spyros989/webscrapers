from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import pandas as pd
from datetime import datetime


# safer path handling
OUTPUT_DIR = Path("/home/deploy/data/scrapers/falconclub")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# setting date variable
today = datetime.today().strftime("%Y-%m-%d")
OUTPUT_FILE = OUTPUT_DIR / f"falconclub_{today}.csv"
# ----------------------------
# Setup Chrome
# ----------------------------
options = Options()

# Headless mode
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)

# ----------------------------
# Open page
# ----------------------------
url = "https://www.facebook.com/falconclub.cz/events"
driver.get(url)

# Wait for page load
time.sleep(10)

# ----------------------------
# Collect events
# ----------------------------
events = []

event_elements = driver.find_elements(By.CSS_SELECTOR, "a[role='link']")

for e in event_elements:
    try:
        text = e.text.strip()
        link = e.get_attribute("href")

        # Keep only event links
        if text and link and "/events/" in link:
            events.append({
                "text": text,
                "link": link,
        	"extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
            })

    except Exception as ex:
        print("Error:", ex)

driver.quit()

# ----------------------------
# Save CSV
# ----------------------------
df = pd.DataFrame(events)
df.to_csv(OUTPUT_FILE, index=False)

print("Done")
print(df.head())
