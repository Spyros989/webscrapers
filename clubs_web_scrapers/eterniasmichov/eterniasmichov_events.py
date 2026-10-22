import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from pathlib import Path
from dotenv import load_dotenv
import undetected_chromedriver as uc


HOME = Path.home()
env_path = (
	HOME
	/"webscrapers"
	/"bands_fb_scrapers"
	/"ma_bands_fb_scrapers"
	/".env"
)
load_dotenv(dotenv_path=env_path)
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "eternia_smichov"
OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_clubs_web_events/eternia_smichov/")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "eternia_smichov.html"

#today = datetime.now().strftime("%Y-%m-%d")

print("Loading .env from:", env_path)
load_dotenv(dotenv_path=env_path)


options = uc.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--disable-dev-shm-usage")

driver = uc.Chrome(options=options)
try:
    driver.get("https://www.eterniasmichov.com/akce")

    wait = WebDriverWait(driver, 20)

    # Wait for the document to finish loading.
    wait.until(
        lambda d: d.execute_script(
            "return document.readyState"
        ) == "complete"
    )

    # Inspect the rendered page, not just the initial response.
    wait.until(
        lambda d: len(d.find_element("tag name", "body").text) > 100
    )

# Capture the rendered HTML from Selenium
    html = driver.page_source
    print("Title:", driver.title)
#    print("Body text:", driver.find_element("tag name", "body").text)
    print("Rendered HTML length:", len(html))

# Save it next to your Python script
    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print(f"Saved HTML to: {OUTPUT_DIR}")
finally:
    driver.quit()
