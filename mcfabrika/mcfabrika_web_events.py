from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

BASE_URL = "https://www.mcfabrika.cz"
CALENDAR_URL = "https://www.mcfabrika.cz/kalendar-akci/2026"

# safer path handling
OUTPUT_DIR = Path("/home/deploy/data/scrapers/mcfabrika")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "mcfabrika_events.csv"
results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)

    page = browser.new_page()

    # LOOP ALL MONTHS
    for month in range(1, 13):

        url = f"{CALENDAR_URL}/{month}"

        print(f"\nScraping month {month}")
        print(url)

        try:

            page.goto(url, wait_until="networkidle", timeout=60000)

            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            # FIND ALL EVENT CARDS
            cards = soup.find_all("div", class_="event-card")

            print(f"Found {len(cards)} cards")

            for card in cards:

                # EVENT LINK
                a = card.find("a", href=True)

                if not a:
                    continue

                href = a.get("href", "")

                if href.startswith("/"):
                    link = BASE_URL + href
                else:
                    link = href

                # TITLE
                title = a.get_text(" ", strip=True)

                # RAW DATE
                datetime_div = card.find(
                    "div",
                    class_="event-datetime"
                )

                raw_date = ""

                if datetime_div:
                    raw_date = datetime_div.get_text(
                        " ",
                        strip=True
                    )

                results.append({
                    "year": 2026,
                    "month": month,
                    "raw_date": raw_date,
                    "artist": title,
                    "link": link,
                    "extraction_datetime": datetime.now().strftime("%Y%m%d_%H%M%S")
                })

        except Exception as e:

            print(f"ERROR on month {month}: {e}")

# CLOSE BROWSER
    browser.close()

# DATAFRAME
df = pd.DataFrame(results)

# REMOVE DUPLICATES
df = df.drop_duplicates()

# SAVE CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"Saved {len(df)} events")
print(OUTPUT_FILE)
