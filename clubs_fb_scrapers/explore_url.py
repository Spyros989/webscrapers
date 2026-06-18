import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from dotenv import load_dotenv
import os
# ... your other imports ...

# Add these BEFORE initializing uc.Chrome() to clear the ghost processes
os.system("pkill -f chromedriver")
os.system("pkill -f chrome")

load_dotenv()

EVENT_URL = "https://www.facebook.com/events/1018364380704878/"

# =========================================================
# CHROME SETUP (Optimized for undetected)
# =========================================================
options = uc.ChromeOptions()

# WARNING: Headless mode often triggers FB's bot detection.
# If you get blocked, comment out the headless line to debug headfully.
options.add_argument("--headless=new") 
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")

#driver = uc.Chrome(options=options)
driver = uc.Chrome(options=options, version_main=149)
try:
    print(f"\nOpening: {EVENT_URL}")
    driver.get(EVENT_URL)
    
    # Wait for the main content to actually load (up to 15 seconds)
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(random.uniform(3, 7))

    # =========================================================
    # CHECK PAGE STATUS
    # =========================================================
    page_text = driver.page_source.lower()

    if "log in" in page_text or "login_form" in page_text:
        print("⚠️ Login wall detected. Facebook is blocking public view.")
    elif "event" not in page_text:
        print("⚠️ Page may be blocked or incomplete.")
    else:
        print("✅ Page loaded successfully.")

    # =========================================================
    # TARGETED DATE EXTRACTION
    # =========================================================
    # Instead of pulling *all* spans, we fetch all visible text blocks.
    # This is significantly faster than calling .text on hundreds of individual elements.
    all_text_elements = driver.find_elements(By.XPATH, "//span | //div")
    
    print("\n===== SCANNING CANDIDATES =====")
    
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
              "january", "february", "march", "april", "june", "july", "august", "september", "october", "november", "december"]
    
    date_candidates = []

    for element in all_text_elements:
        try:
            txt = element.text.strip()
            if not txt or len(txt) > 100:  # Skip empty or massive paragraphs
                continue
                
            txt_lower = txt.lower()
            
            # Look for structured elements containing a month AND time indicators
            if any(m in txt_lower for m in months) and ("am" in txt_lower or "pm" in txt_lower or "–" in txt or "2026" in txt):
                if txt not in date_candidates:
                    date_candidates.append(txt)
                    print(f"Candidate found: {txt}")
        except Exception:
            continue

    # =========================================================
    # FINAL EXTRACTION LOGIC
    # =========================================================
    print("\n===== FINAL RESULT =====")
    if date_candidates:
        # Usually, the longest, most descriptive string that hits our criteria is the real event date
        # (e.g., "FRIDAY, JUNE 19, 2026 AT 7:00 PM")
        best_match = max(date_candidates, key=len)
        print("Date Found:", best_match)
    else:
        print("Date Found: None (Could not isolate the event date reliably)")

finally:
    driver.quit()
