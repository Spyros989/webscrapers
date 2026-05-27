from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime


URL = "https://bajkazylhk.cz/akce"
BASE_URL = "https://bajkazylhk.cz"

# safer path handling
OUTPUT_DIR = Path("/home/deploy/data/scrapers/bajkazylhk")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "bajkazylhk_events.csv"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "html.parser")

results = []

# Find all event links
events = soup.find_all("a", href=True)

for event in events:

    # Find title
    title = event.find("h3")

    # Find date
    date = event.find("p")

    # Skip invalid blocks
    if not title or not date:
        continue

    href = event.get("href", "")

    # Make full URL if relative
    if href.startswith("/"):
        link = BASE_URL + href
    else:
        link = href

    results.append({
        "date": date.get_text(strip=True),
        "artist": title.get_text(strip=True),
        "link": link,
        "extraction_datetime": datetime.now().strftime("%Y%m%d_%H%M%S")

    })

# Create dataframe
df = pd.DataFrame(results)

# Save CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved {len(df)} events")
print(OUTPUT_FILE)
