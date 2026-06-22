import pandas as pd
import re
from pathlib import Path

# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_fetch_dates.csv"
OUTPUT_FILE = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_fetch_dates_clean.csv"

# =========================================================
# LOAD CSV
# =========================================================

df = pd.read_csv(INPUT_FILE)

# =========================================================
# VALID WEEKDAYS
# =========================================================

weekdays = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

# =========================================================
# PARSER
# =========================================================

def parse_fb_date(value):

    if pd.isna(value) or str(value).strip() == "":
        return pd.Series([
            None,   # status
            None,   # event_date
            None    # event_time
        ])

    text = str(value).strip()

    if not text.lower().startswith(weekdays):
        return pd.Series([
            "error",
            None,
            None
        ])

    # Example:
    # Thursday, June 25, 2026 at 6:30 PM CEST

    m = re.search(
        r"^[A-Za-z]+,\s+([A-Za-z]+\s+\d{1,2},\s+\d{4})\s+at\s+(.+?)(?:\s+[A-Z]{3,5})?$",
        text,
        re.IGNORECASE
    )

    if not m:
        return pd.Series([
            "error",
            None,
            None
        ])

    date_part = m.group(1)
    time_part = m.group(2)

    try:
        event_date = pd.to_datetime(
            date_part,
            format="%B %d, %Y"
        ).date()
    except:
        event_date = None

    return pd.Series([
        "ok",
        event_date,
        time_part
    ])

# =========================================================
# APPLY
# =========================================================

df[["status", "event_date", "event_time"]] = df["date"].apply(parse_fb_date)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved: {OUTPUT_FILE}")

print("\nSummary:")
print(df["status"].value_counts(dropna=False))
