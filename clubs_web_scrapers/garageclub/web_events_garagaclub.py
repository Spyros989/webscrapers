from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

URL = "https://www.garageclub.cz/"
BASE_URL = "https://www.garageclub.cz/"

# safer path handling
OUTPUT_DIR = Path("/home/deploy/data/scrapers/garageclub")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "garageclub.csv"
results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "html.parser")

container = soup.find("div", class_="full-program")

if not container:
    print("No full-program found")
    exit()

for h3 in container.find_all("h3"):

    text = h3.get_text(" ", strip=True)

    a = h3.find("a")

    href = ""

    if a and a.get("href"):

        link = a["href"]


    results.append({
        "raw": text,
        "link": link,
        "extraction_datetime": datetime.now().strftime("%Y%m%d_%H%M%S")
    })

# convert to dataframe
df = pd.DataFrame(results).drop_duplicates()

# save CSV (Excel-safe)
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved {len(df)} events")
print(f"File: {OUTPUT_FILE}")
