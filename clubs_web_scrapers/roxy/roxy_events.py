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
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "roxy"
OUTPUT_DIR=DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "roxy_events.csv"


# Define the tags you want to exclude
exclude_tags = ["#techno", "#dj","#electro","#hip-hop","#house","#drum&bass","#free mondays","#grime"]
# Create an "OR" regex pattern: '#techno|#dj'
pattern = "|".join(exclude_tags)

def expand_short_url(short_url):
    try:
        # Send a HEAD request and follow all redirects to the final destination
        response = requests.head(short_url, allow_redirects=True, timeout=5)
        return response.url
    except requests.exceptions.RequestException as e:
        return f"Error resolving URL: {e}"


# =========================
# CONFIGURATION
# =========================
timestamp = datetime.now().strftime("%Y-%m-%d")
base_url = "https://www.roxy.cz/en/#program"

# =========================
# GET EVENT URLS
# =========================

print("Fetching event list...")

response = requests.get(base_url, timeout=30)
response.encoding = "utf-8"
response.raise_for_status()

soup = BeautifulSoup(response.text, "lxml")

product_containers = soup.find_all("a", class_="item")

event_urls = []

for product in product_containers:
    href = product.get("href")

    if "/en/events/detail/" in href:
        event_urls.append(urljoin(base_url, href))

# Remove duplicate URLs while preserving order
event_urls = list(dict.fromkeys(event_urls))

df = pd.DataFrame({"web_link": event_urls})
counts = len(df)

print(f"Found {counts} event URLs.")


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        for idx, row in df.iterrows():
            event_url = row["web_link"]

            print(f"Checking: {idx + 1}/{counts} - {event_url}")

            fb_link = None
            title = None
            tags=None
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

                fb_button = event_soup.find("a", class_="button-fb")

                if fb_button and fb_button.get("href"):
                    socials = fb_button["href"]
                    print(socials)
                else:
                    socials = None
                    print("No Facebook link found.")

                # -------------------------
                # TAGS
                # -------------------------

                for info in event_soup.find_all("div", class_="bottom"):
                    if info:
                        tags = info.find_all("div", class_="tags")
                        if tags:
                            tags_text = [tag.get_text(" ", strip=True) for tag in tags]
                            tags = ", ".join(tags_text)
                            print(f"Tags found: {tags}")
                            break
                # -------------------------
                # TICKETS AND PRICES
                # -------------------------

                info = event_soup.find("div", class_="top")
                if info:
                    p = info.find_all("p")
                    raw_price = [p.get_text(" ", strip=True) for p in p]
                    print(raw_price)
                    price = next((item for item in raw_price if "czk" in item.lower()), None)
                    print(price)

                # -------------------------
                # EVENT TITLE
                # -------------------------
                title = event_soup.title.get_text(strip=True) if event_soup.title else None
                title = title.removesuffix(" | ROXY PRAGUE")
                print(title)

                # -------------------------
                # EVENT TIME AND DATE
                # -------------------------

                for info in event_soup.find_all("time", class_="datetime"):
                    if info:
        # 1. Get the raw text directly as a string (no brackets)
                        raw_datetime = info.get_text(" ", strip=True) # e.g., "Tue 16/02/2027 17:30"

        # 2. Split from the right side at the last space to isolate the time
                        date_part, event_time = raw_datetime.rsplit(" ", 1)

        # 3. If you want to drop the day of the week (e.g., "Tue ") from the date:
        # split at the first space from the left
                        _, event_date = date_part.split(" ", 1)

                        print(f"Date found: {event_date}")  # Output: 16/02/2027
                        print(f"Time found: {event_time}")  # Output: 17:30
                        break

                # -------------------------
                # SAVE RESULTS
                # -------------------------
                df.at[idx, "event_url"] = socials
                df.at[idx, "tags"] = tags
                df.at[idx, "event_name"] = title
                df.at[idx, "event_date"] = event_date
                df.at[idx, "event_time"] = event_time
                df.at[idx, "event_price"] = price


            except Exception as e:
                print(f"ERROR processing {event_url}: {e}")

            # Small delay between event pages
            time.sleep(1)

    finally:
        browser.close()
df["event_date"] = pd.to_datetime(df["event_date"]).dt.strftime("%Y-%m-%d")
df_filtered = df[df["event_url"].notnull()]
df_filtered["event_url"] = df_filtered["event_url"].apply(expand_short_url)
df_filtered["event_url"] = df_filtered["event_url"].str.split("?").str[0]

# Filter the DataFrame to exclude those tags
# (~ negates the condition, meaning "does NOT contain")
df_filtered = df_filtered[~df_filtered["tags"].str.contains(pattern, na=False)]
print(df_filtered)
df_filtered.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
