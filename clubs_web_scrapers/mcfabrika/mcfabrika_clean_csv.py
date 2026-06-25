import pandas as pd
import re
from pathlib import Path

# =========================
# FILE PATHS
# =========================

INPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_daily.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_daily_clean.csv")

# =========================
# DATA RULES
# =========================
# LOAD CSV
df = pd.read_csv(INPUT_FILE)

def process_raw_date(row):

    raw = str(row["raw_date"])

    # -------------------------
    # EXTRACT TIME
    # -------------------------

    time_match = re.search(r"(\d{1,2}:\d{2})", raw)

    event_time = ""

    if time_match:
        event_time = time_match.group(1)

        # remove time from raw text
        raw = raw.replace(event_time, "").strip()

    # -------------------------
    # EXTRACT DAY
    # -------------------------

    numbers = re.findall(r"\d+", raw)

    day = None

    if numbers:
        day = int(numbers[0])

    # -------------------------
    # BUILD SQL DATE
    # -------------------------

    sql_date = None

    if day:

        year = int(row["year"])
        month = int(row["month"])

        sql_date = f"{year}-{month:02d}-{day:02d}"

    return pd.Series([sql_date, event_time])

# CREATE NEW COLUMNS
df[["sql_date", "event_time"]] = df.apply(
    process_raw_date,
    axis=1
)

# KEEP FINAL COLUMNS
df = df[[
    "sql_date",
    "event_time",
    "event_name",
    "web_link",
    "extraction_datetime"
]]

# SAVE CLEAN CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("DONE")
print(f"Saved to:\n{OUTPUT_FILE}")
