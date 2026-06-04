import undetected_chromedriver as uc

options = uc.ChromeOptions()

options.add_argument("--headless=new")  # 🔥 critical fix
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = uc.Chrome(options=options, version_main=149)

driver.get("https://example.com")
print(driver.title)

driver.quit()
