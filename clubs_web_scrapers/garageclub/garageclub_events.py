from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

URL = "https://www.woodmanproduction.cz/"
BASE_URL="https://www.woodmanproduction.cz"



# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "garageclub"
OUTPUT_DIR=DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "garageclub_events.csv"


results = []

with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(URL, wait_until="networkidle")
    html = page.content()
    browser.close()

soup = BeautifulSoup(html, "html.parser")
event_urls=[]
url =None
title=None
event_info=None
web_link =None
music_genre=None
product_containers  = soup.find_all("div", class_="event")
for product in product_containers:
    title=product.find("h2", class_="event-name").get_text(" ",strip=True)
    web_link=product.find("a").get("href")
    web_link=BASE_URL+web_link
    music_genre=product.find("h3", class_="event-genre").get_text(" ",strip=True)
    meta_list = product.find("ul", class_="event-meta")
    if meta_list:
    # 2. Extract the text from all li tags inside it, stripping out extra whitespace
    # This creates a list: ['16.4.2027 — 19:30', 'RnR GARAGE Martinov', 'od 690,- Kč']
        items = [li.text.strip() for li in meta_list.find_all("li")]
    # 3. Ensure we got exactly 3 items, then unpack them safely
        if len(items) == 3:
            date_time, venue, price = items
        # Further processing: Separate the Date and Time if needed
        # Splits '16.4.2027 — 19:30' by the dash
            date, time = [part.strip() for part in date_time.split("—")]
        # Clean up the price (e.g., removing 'od ' and ',- Kč' to get just numbers if needed)
            clean_price = price.replace("od", "").replace(",- Kč", "").strip()
        # Display the broken down variables

    event_urls.append({
        "event_name":title,
        "event_date":date,
        "event_time":time,
        "web_link": web_link,
        "music_genre":music_genre,
        "entrance_fee":clean_price
    })

df = pd.DataFrame(event_urls)
#df["event_date"] = pd.to_datetime(df["event_date"]).dt.strftime("%Y-%m-%d")
df["event_date"] = pd.to_datetime(df["event_date"], format="%d.%m.%Y", errors="coerce").dt.strftime("%Y-%m-%d")

# save CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved {len(df)} events")
print(f"File: {OUTPUT_FILE}")
