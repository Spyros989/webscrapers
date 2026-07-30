from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "bajkazylhk"
OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_clubs_web_events/bajkazylhk")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "bajkazylhk_events.csv"

# ----------------------------
# PROJECT CONFIG
# ----------------------------
URL = "https://bajkazylhk.cz/akce"
BASE_URL = "https://bajkazylhk.cz"
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
        "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
    })

# Create dataframe
df = pd.DataFrame(results)

# ----------------------------
# EXPORT FILE (CSV)
# ----------------------------
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)
# ----------------------------
# END MESSAGE
# ----------------------------
print(f"Saved {len(df)} events from bajkazylhk.cz")
print(OUTPUT_FILE)
