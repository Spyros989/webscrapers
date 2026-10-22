from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
from pathlib import Path

#page_path =  '/home/deploy/data/scrapers/cz_clubs_web_events/eternia_smichov/eternia_smichov.html'
# ----------------------------
# PATH CONFIG
# ----------------------------
timestamp = datetime.now().strftime("%Y-%m-%d")
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "eternia_smichov"
OUTPUT_DIR=DATA_DIR
INPUT_FILE= OUTPUT_DIR / "eternia_smichov.html"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "eternia_smichov_events_clean.csv"


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

def clean_facebook_url(url):
    match = re.search(r"facebook\.com/events/(?:s/[^/]+/)?(\d+)", url)

    if match:
        event_id = match.group(1)
        return f"https://www.facebook.com/events/{event_id}/"

    return url  # Keep the original URL if no event ID is found

def extract_date(text):
    match = re.search(r'(\d{1,2})\.\s*(\d{1,2})\.\s*(\d{4})', text)

    if match:
        day, month, year = map(int, match.groups())
        return datetime(year, month, day).strftime("%Y-%m-%d")

    return None


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# -------------------------
# EVENT DATES
# -------------------------
dates = [
    extract_date(element.get_text(" ", strip=True))
    for element in soup.find_all("span", class_="akceInfo css-1fnsnam")
]

# -------------------------
# EVENT TITLES
# -------------------------
titles = [
    remove_emojis(element.get_text(" ", strip=True))
    for element in soup.find_all("div", class_="css-1b5jlsj")
]

# -------------------------
# FACEBOOK EVENT LINKS
# -------------------------
fb_links = [
    clean_facebook_url(element["href"])
    for element in soup.find_all(
        "a",
        href=lambda href: href and "facebook.com/events/" in href
    )
]

# -------------------------
# VENUE SELECTION
# -------------------------
venues = []
venue_mapping = {
    "subzero": "73",
    "půda": "72",
}
venue_labels = soup.find_all("span", class_="css-f8d40o")

for label in venue_labels:
    venue_element = label.find_next_sibling("span")

    if venue_element:
        venue_name = venue_element.get_text(strip=True).lower()
        venue_code = venue_mapping.get(venue_name, venue_name)
        venues.append(venue_code)
    else:
        venues.append(None)
# Temporary approach: pair by position
# Only valid if each list has the same order and number of items.
# -------------------------
# BUILD DATAFRAME
# -------------------------
count = max(
    len(titles),
    len(dates),
    len(fb_links),
    len(venues)
)
df = pd.DataFrame([
    {
        "event_name": titles[i] if i < len(titles) else None,
        "event_date": dates[i] if i < len(dates) else None,
        "event_url": fb_links[i] if i < len(fb_links) else None,
        "venue_id": venues[i] if i < len(venues) else None,
	"snapshot_date":timestamp,
    }
    for i in range(count)
])

print(df.to_string(index=False))
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\nSaved to: {OUTPUT_FILE}")
# Save the results
#df.to_csv("eternia_events.csv", index=False, encoding="utf-8-sig")
