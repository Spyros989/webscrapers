from bs4 import BeautifulSoup
import pandas as pd
import requests
from playwright.sync_api import sync_playwright
import time
from urllib.parse import urljoin
from datetime import datetime
from pathlib import Path

# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "podlampou"
OUTPUT_DIR=DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "podlampou_events.csv"

# =========================
# CONFIGURATION
# =========================
timestamp = datetime.now().strftime("%Y-%m-%d")
base_url = "https://podlampou.cz/events/"

# =========================
# GET EVENT URLS
# =========================

print("Fetching event list...")

response = requests.get(base_url, timeout=30)
response.encoding = "utf-8"
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

product_containers = soup.find_all("a", class_="list-item")

event_urls = []

for product in product_containers:
    href = product.get("href")

    if href:
        event_urls.append(urljoin(base_url, href))

# Remove duplicate URLs while preserving order
event_urls = list(dict.fromkeys(event_urls))

df = pd.DataFrame({"web_link": event_urls})
counts = len(df)

print(f"Found {counts} event URLs.")

# =========================
# SCRAPE EVENT PAGES
# =========================

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        for idx, row in df.iterrows():
            event_url = row["web_link"]

            print(f"Checking: {idx + 1}/{counts} - {event_url}")

            fb_link = None
            title = None
            event_date = None
            start_time = None
            price = None

            try:
                page.goto(
                    event_url,
                    wait_until="domcontentloaded",
                    timeout=30000,
                )

                # Allow the page's client-side content to render
                page.wait_for_timeout(500)

                html = page.content()
                event_soup = BeautifulSoup(html, "lxml")

                # -------------------------
                # FACEBOOK EVENT LINK
                # -------------------------

                for a in event_soup.find_all("a", href=True):
                    href = a["href"]

                    if "facebook.com/events/" in href:
                        fb_link = href
                        break

                # -------------------------
                # EVENT TITLE, DATE, TIME
                # -------------------------

                heading = event_soup.find(
                    "h1",
                    attrs={"goout-data-title": True},
                )

                if heading:
                    title = heading.get(
                        "goout-data-title", ""
                    ).strip() or None

                    datetime_start = heading.get(
                        "goout-data-datetime-start", ""
                    )

                    if datetime_start and datetime_start != "NONE":
                        dt = pd.to_datetime(
                            datetime_start,
                            errors="coerce",
                        )

                        if pd.notna(dt):
                            event_date = dt.strftime("%Y-%m-%d")
                            start_time = dt.strftime("%H:%M")

                    # Fallback: displayed date if datetime is missing
                    if not event_date:
                        date_el = heading.find("small")

                        if date_el:
                            displayed_date = date_el.get_text(
                                " ", strip=True
                            )
                            print(
                                f"Displayed date only: {displayed_date}"
                            )
                # -------------------------
                # EVENT PRICE
                # -------------------------

                price = None

                for info in event_soup.find_all("div", class_="event-info"):
                    pricing = info.find("span", id="pricing")

                    if pricing:
                        price = pricing.get_text(" ", strip=True)
                        break



                # -------------------------
                # SAVE RESULTS
                # -------------------------
                df.at[idx, "event_url"] = fb_link
                df.at[idx, "title"] = title
                df.at[idx, "event_date"] = event_date
                df.at[idx, "event_time"] = start_time
                df.at[idx, "price"] = price

                print("FB LINK FOUND" if fb_link else "NO FB LINK")
                print(f"TITLE: {title or 'NOT FOUND'}")
                print(f"DATE: {event_date or 'NOT FOUND'}")
                print(f"START: {start_time or 'NOT FOUND'}")
                print(f"PRICE: {price or 'NOT FOUND'}")
                print("-" * 50)

            except Exception as e:
                print(f"ERROR processing {event_url}: {e}")

            # Small delay between event pages
            time.sleep(1)

    finally:
        browser.close()

# =========================
# EXPORT RESULTS
# =========================
df = df.dropna(subset=["event_url"])
df['entrance_fee'] = df['price'].str.split('/ ').str[-1].str.strip()
df["event_url"] = df["event_url"].apply(
    lambda url: url.rstrip("/") + "/"
    if pd.notna(url) and url != "N/A" and url.strip()
    else url
)
df["event_date"] = pd.to_datetime(df["event_date"]).dt.strftime("%Y-%m-%d")
df["date"]=df["event_date"]
df['snapshot_date']=timestamp
df['venue_id']=65
df['status']="ok"
df['duration']=None
df['location']="Havířská 933/11 30100 Plzen, Czech Republic"
df['snapshot_date']=timestamp

column_order = [
    "venue_id",
    "event_url",
    "date",
    "title",
    "location",
    "status",
    "event_date",
    "event_time",
    "entrance_fee",
    "web_link",
    "duration",
    "snapshot_date"
]
df=df[column_order]
df = df.drop(columns=[col for col in df if col not in column_order])
df.drop_duplicates()

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\nFinished. Processed {counts} event URLs saved {len(df)} entries.")
print(f"Saved to: {OUTPUT_FILE}")
