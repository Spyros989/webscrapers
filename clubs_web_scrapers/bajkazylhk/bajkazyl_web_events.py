from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
from datetime import datetime
from pathlib import Path
# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "bajkazylhk"
OUTPUT_DIR = Path("/home/deploy/data/scrapers/cz_clubs_web_events/bajkazylhk")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "bajkazylhk_events_description.csv"

URL = "https://bajkazylhk.cz/akce"
BASE_URL = "https://bajkazylhk.cz"

# Regex pattern breakdown:
# \b             : Ensures the match starts at a word boundary (prevents matching things like "myfacebook.com")
# [a-zA-Z0-9.-]+ : Matches the domain name (letters, numbers, dots, dashes)
# \.             : Matches the literal dot before the domain extension
# [a-zA-Z]{2,6}  : Matches the domain extension (like com, org, co.uk) between 2 and 6 letters long
# \b             : Ensures the match ends at a word boundary
#pattern = r"\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}\b"
#pattern = r"(fb\.com/events(?:/[a-zA-Z0-9_-]+)*)\b"
MONTHS = {
    "ledna": 1,
    "února": 2,
    "března": 3,
    "dubna": 4,
    "května": 5,
    "června": 6,
    "července": 7,
    "srpna": 8,
    "září": 9,
    "října": 10,
    "listopadu": 11,
    "prosince": 12,
}
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F000-\U0001FAFF"
        "\U00002600-\U000027BF"
        "\U0000FE00-\U0000FE0F"
        "\U0001F1E6-\U0001F1FF"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub("", text).strip()

def parse_event(text):

    text = str(text)

    # -----------------------------
    # 1. EXTRACT TIME FIRST
    # -----------------------------
    time_match = re.search(r"(\d{1,2}:\d{2})", text)

    event_time = time_match.group(1) if time_match else ""

    # remove time from string
    text_no_time = re.sub(r"\d{1,2}:\d{2}", "", text)

    # -----------------------------
    # 2. EXTRACT DATE PART
    # -----------------------------
    match = re.search(
        r"(\d{1,2})\.\s*([^\s]+)\s*(\d{4})",
        text_no_time
    )

    if not match:
        return pd.Series([None, event_time])

    day = int(match.group(1))
    month_name = match.group(2).lower().strip()
    year = int(match.group(3))

    month = MONTHS.get(month_name)

    if not month:
        return pd.Series([None, event_time])

    sql_date = f"{year}-{month:02d}-{day:02d}"

    return pd.Series([sql_date, event_time])

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
        "event_name": title.get_text(strip=True),
        "web_link": link
    })

# Create dataframe
df = pd.DataFrame(results)
# APPLY
df[["event_date", "event_time"]] = df["date"].apply(parse_event)
df["event_name"]=df["event_name"].apply(remove_emojis)


# FINAL OUTPUT
df = df[[
    "event_date",
    "event_time",
    "event_name",
    "web_link"
]]
with sync_playwright() as p:

    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    for idx, row in df.iterrows():

        url = row["web_link"]

        print(f"Checking: {url}")

        try:

            page.goto(url, wait_until="networkidle", timeout=30000)

            html = page.content()

            soup = BeautifulSoup(html, "html.parser")

            fb_link = None
            description=None
            # Find all links
            for a in soup.find_all("a", href=True):

                href = a["href"]

                # Facebook event/page detection
                if "facebook.com/events" in href:
                    fb_link = href
                    break
            df.at[idx, "event_url"] = fb_link

            print("FOUND" if fb_link else "NO FB LINK")
                    # Get the whole description
            description = soup.get_text(strip=True)

            df.at[idx, "description"] = description

            # small delay
            time.sleep(1)

        except Exception as e:

            print(f"ERROR: {e}")

    browser.close()

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved {len(df)} events")
print(OUTPUT_FILE)
