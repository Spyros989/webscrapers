import time
import random
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import os

os.system("pkill -f chromedriver")
os.system("pkill -f chrome")

# =========================================================
# CONFIG
# =========================================================
EVENT_URL = "https://www.facebook.com/events/877761904631563/"

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
DATE_INDEX = 31
NAME_INDEX = 50
LOCATION_INDEX = 52
ATTENDANCE_INDEX = 70

#print("\n===== KEY SPANS (BY INDEX) =====\n")
#print(f"Date: {DATE_INDEX}")
#print(f"Name: {NAME_INDEX}")
#print(f"Location: {LOCATION_INDEX}")
#print(f"Attendance: {ATTENDANCE_INDEX}")

#spans = driver.find_elements(By.TAG_NAME, "span")

def get(i):
    try:
        return spans[i].text.strip()
    except:
        return None

event_datetime = get(DATE_INDEX)
event_name = get(NAME_INDEX)
location = get(LOCATION_INDEX)
attendance = get(ATTENDANCE_INDEX)

# =========================================================
# OUTPUT
# =========================================================
print("\n===== FINAL RESULT =====")
print("Date:", event_datetime)
print("Name:", event_name)
print("Location:", location)
print("Attendance:", attendance)

driver.quit()
