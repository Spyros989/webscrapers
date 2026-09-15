from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "mcfabrika"
OUTPUT_DIR=DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "mcfabrika_events.csv"

now = datetime.now() # current date and time
year = now.strftime("%Y")

BASE_URL = "https://www.mcfabrika.cz"
CALENDAR_URL = f"https://www.mcfabrika.cz/kalendar-akci/{year}"

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
                # ENTRANCE FEE

                info_label = card.find(
                    "span",
                    class_="info-label"
                )
                text_fee = info_label.get_text(strip=True) if info_label else "N/A"


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
                    "year": year,
                    "month": month,
                    "raw_date": raw_date,
                    "event_name": title,
                    "web_link": link,
		    "text_fee": text_fee,
                    "extraction_datetime": datetime.now().strftime("%Y-%m-%d_%H%M%S")
                })

        except Exception as e:

            print(f"ERROR on month {month}: {e}")

# CLOSE BROWSER
    browser.close()
# DATAFRAME
df = pd.DataFrame(results)

# REMOVE DUPLICATES
df = df.drop_duplicates()
# Extract digits (and optional digits after spaces/dots) right before 'Kč'
df['entrance_fee'] = df['text_fee'].str.extract(r'(\d[\d\s\.]*)\s*Kč', expand=False)

# Optional: Clean up spaces or dots inside the extracted number string (e.g., "1 450" -> "1450")
df['entrance_fee'] = df['entrance_fee'].str.replace(r'[\s\.]', '', regex=True)
# ===== COLUMN ORDER CONFIG =====
df.drop(columns=['text_fee'], inplace=True)
column_order = [
    "year",
    "month",
    "raw_date",
    "event_name",
    "entrance_fee",
    "web_link"
]
df = df[column_order]
# SAVE CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\nDONE")
print(f"Saved {len(df)} events an \n OUTPUT_FILE")
print(OUTPUT_FILE)
