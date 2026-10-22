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
INPUT_FILE = DATA_DIR / "roxy_events.csv"
OUTPUT_FILE = DATA_DIR / "roxy_events_descriptions.csv"

df = pd.read_csv(INPUT_FILE)
df_links=df["web_link"].tolist()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    try:
        for idx, event_url in enumerate(df_links):
            print(f"Checking: {idx + 1}/{len(df_links)} - {event_url}")
            event_url = event_url.strip()  # Remove leading/trailing whitespace


            description = None

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


                for info in event_soup.find_all("div", class_="text-perex"):
                    if info:
                        p = info.find_all("p")
                        raw_text = [p.get_text(" ", strip=True) for p in p]
                        text = [raw_text.replace('\xa0', ' ').strip() for raw_text in raw_text]
                        description = text[0] if text else None
                        print(description)
                # -------------------------
                # SAVE RESULTS
                # -------------------------
                df.at[idx, "description"] = description


            except Exception as e:
                print(f"ERROR processing {event_url}: {e}")

            # Small delay between event pages
            time.sleep(1)

    finally:
        browser.close()
df.to_csv(OUTPUT_FILE, index=False)
