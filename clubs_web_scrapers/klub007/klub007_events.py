from bs4 import BeautifulSoup
import pandas as pd
from playwright.sync_api import sync_playwright
import re
from datetime import datetime
from pathlib import Path

# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "klub007"
OUTPUT_DIR=DATA_DIR
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTPUT_DIR / "klub007_events.csv"

# =========================
# DATA RULES
# =========================

timestamp = datetime.now().strftime("%Y-%m-%d")

MONTHS = {
    "leden": 1,
    "únor": 2,
    "březen": 3,
    "duben": 4,
    "květen": 5,
    "červen": 6,
    "červenec": 7,
    "srpen": 8,
    "září": 9,
    "říjen": 10,
    "listopad": 11,
    "prosinec": 12,
}
def duration_column(start_time, end_time):
    if pd.isna(start_time) or pd.isna(end_time):
        return pd.NA

    try:
        start_dt = datetime.strptime(start_time, "%H:%M")
        end_dt = datetime.strptime(end_time, "%H:%M")

        # Handle cases where the event goes past midnight
        if end_dt < start_dt:
            end_dt += pd.Timedelta(days=1)

        duration = end_dt - start_dt
        total_seconds = int(duration.total_seconds())
        # 2. Extract hours and remaining minutes
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        # 3. Format the output string
        formatted_duration = f"{hours} hr {minutes} min"
        return formatted_duration
    except ValueError:
        return pd.NA

def parse_date_time(date_time_text, year):
    if pd.isna(date_time_text) or pd.isna(year):
        return pd.Series([pd.NaT, pd.NA, pd.NA])

    # Extract day, Czech month, and event times
    match = re.search(
        r"(\d{1,2})\.?\s+([^\s]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})",
        str(date_time_text).strip(),
        re.IGNORECASE,
    )

    if not match:
        return pd.Series([pd.NaT, pd.NA, pd.NA])

    day = int(match.group(1))
    month_name = match.group(2).lower()
    start_time = match.group(3)
    end_time = match.group(4)

    month = MONTHS.get(month_name)

    if month is None:
        return pd.Series([pd.NaT, start_time, end_time])

    try:
        event_date = pd.Timestamp(
            year=int(year),
            month=month,
            day=day,
        )
    except (ValueError, TypeError):
        event_date = pd.NaT

    return pd.Series([event_date, start_time, end_time])

def split_title(title):
    if pd.isna(title):
        return pd.Series([title, pd.NA])

    # Split after the last :00 or :59 followed by a space
    matches = list(re.finditer(r":(?:00|59)\s+", str(title)))

    if matches:
        match = matches[-1]
        date_time = title[:match.end()].strip()
        event_title = title[match.end():].strip()
        return pd.Series([date_time, event_title])

    return pd.Series([title, pd.NA])

def scrape_klub007():
    url = "https://klub007strahov.cz/program/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Navigating to page...")
        page.goto(url, wait_until="networkidle", timeout=60000)

        # Find all clickable event boxes
        boxes = page.query_selector_all(".evoet_in")
        print(f"Found {len(boxes)} events. Clicking to expand details...")

        for index, box in enumerate(boxes, 1):
            try:
                box.click()
                page.wait_for_timeout(400)
            except Exception as e:
                print(f"Could not click box {index}: {e}")

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")
    events_data = []

    # Track the year associated with each month heading
    current_year = None

    # Process month headings and event cards in document order
    elements = soup.select(".evcal_month_line, .eventon_list_event")

    for element in elements:

        # Update the year when we encounter a month heading
        if "evcal_month_line" in element.get("class", []):
            data_d = element.get("data-d", "")
            match = re.search(r"eml_\d+_(\d{4})", data_d)

            if match:
                current_year = int(match.group(1))
            else:
                current_year = None

            continue

        # Skip anything that isn't an event card
        if "eventon_list_event" not in element.get("class", []):
            continue

        card = element

        # 1. Title
        title_el = card.find(class_="evo_glance_title") or card.find(
            ["h2", "h3", "span"]
        )
        title = title_el.get_text(" ", strip=True) if title_el else "N/A"

        # 2. Date & Time
        day = card.find(class_="evo_day")
        month = card.find(class_="evo_month")
        time_el = card.find(class_="evo_time")

        date_str = (
            f"{day.get_text(strip=True) if day else ''} "
            f"{month.get_text(strip=True) if month else ''}"
        ).strip()

        # 3. Price
        price = "N/A"
        card_text = card.get_text(" ", strip=True)

        price_match = card.find(class_=lambda c: c and "cost" in c)

        if price_match:
            price = price_match.get_text(" ", strip=True)

        else:
            match = re.search(
                r"(\d[\d\s]*(?:,-|Kč|CZK))",
                card_text,
                re.IGNORECASE
            )
            if match:
                price = match.group(1).strip()

        # 4. Facebook Link
        fb_link = card.find(
            "a",
            href=lambda h: h and (
                "facebook.com/events" in h or "fb.me" in h
            )
        )
        fb_url = fb_link["href"] if fb_link else "N/A"

        # 5. Year
        year = current_year if current_year is not None else pd.NA

        events_data.append({
            "Title": title,
            "Date": date_str,
            "Year": year,
            "Price": price,
            "event_url": fb_url,
        })

    df = pd.DataFrame(events_data)
    return df

# Execute
df = scrape_klub007()
df[["Date_Time", "event_name"]] = df["Title"].apply(split_title)

def parse_date_time(date_time_text, year):
    if pd.isna(date_time_text) or pd.isna(year):
        return pd.Series([pd.NaT, pd.NA, pd.NA])

    # Extract day, Czech month, and event times
    match = re.search(
        r"(\d{1,2})\.?\s+([^\s]+)\s+(\d{1,2}:\d{2})\s+(\d{1,2}:\d{2})",
        str(date_time_text).strip(),
        re.IGNORECASE,
    )

    if not match:
        return pd.Series([pd.NaT, pd.NA, pd.NA])

    day = int(match.group(1))
    month_name = match.group(2).lower()
    start_time = match.group(3)
    end_time = match.group(4)

    month = MONTHS.get(month_name)

    if month is None:
        return pd.Series([pd.NaT, start_time, end_time])

    try:
        event_date = pd.Timestamp(
            year=int(year),
            month=month,
            day=day,
        )
    except (ValueError, TypeError):
        event_date = pd.NaT

    return pd.Series([event_date, start_time, end_time])


# Create Date, Start_Time, and End_Time columns
df[["event_date", "Start_Time", "End_Time"]] = df.apply(
    lambda row: parse_date_time(row["Date_Time"], row["Year"]),
    axis=1,
)

# Format the date as DD.MM.YYYY
df["event_date"] = pd.to_datetime(df["event_date"]).dt.strftime("%Y-%m-%d")
df["duration"] = df.apply(lambda row: duration_column(row["Start_Time"], row["End_Time"]), axis=1)
df['entrance_fee'] = df['Price'].str.extract(r'([\d.,]+)')
df['entrance_fee'] = df['entrance_fee'].str.replace(' ', '').str.replace(',', '').astype(float)
df['venue_id']=68
df['location']="Chaloupeckého 1903/6, 169 00"
df['status']="ok"
df['snapshot_date']=timestamp
df['date']=df["event_date"] 
df['web_link']=''
df['title']=df["event_name"]
df['event_time']=df["Start_Time"]
df = df[df['event_url'] != 'N/A']

df["event_url"] = df["event_url"].apply(
    lambda url: url.rstrip("/") + "/"
    if pd.notna(url) and url != "N/A" and url.strip()
    else url
)

# ===== COLUMN ORDER CONFIG =====
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

# Reorder the DataFrame columns
df = df[column_order]

print(df.to_string(index=False))

# Export to CSV

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"\nSaved to: {OUTPUT_FILE}")
