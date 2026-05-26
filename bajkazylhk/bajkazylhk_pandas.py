from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://bajkazylhk.cz/akce"
BASE_URL = "https://bajkazylhk.cz"

OUTPUT_FILE = r"C:\Users\Spyro\Desktop\test_scrappers\bajkazylhk\bajkazyl_events.csv"

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
        "link": link
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