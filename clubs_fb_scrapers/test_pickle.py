import time
import pickle
import undetected_chromedriver as uc

options = uc.ChromeOptions()

# REQUIRED for your server
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(
    options=options,
    version_main=149
)

driver.get("https://www.facebook.com")

input("Log in manually in HEADLESS??? (this won't work)")

cookies = driver.get_cookies()

with open("fb_cookies.pkl", "wb") as f:
    pickle.dump(cookies, f)

print("saved cookies")

driver.quit()
