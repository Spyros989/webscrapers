import pandas as pd
import re
from pathlib import Path
from datetime import date,datetime
# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "mcfabrika"
INPUT_FILE = DATA_DIR / "mcfabrika_events.csv"
OUTPUT_FILE = DATA_DIR / "mcfabrika_events_clean.csv"

## Normalize today's date to midnight for an accurate comparison
today = pd.Timestamp.now().normalize()
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

    event_date = None

    if day:

        year = int(row["year"])
        month = int(row["month"])

        event_date = f"{year}-{month:02d}-{day:02d}"

    return pd.Series([event_date, event_time])

# CREATE NEW COLUMNS
df[["event_date", "event_time"]] = df.apply(
    process_raw_date,
    axis=1
)
df["venue_id"]=13
# KEEP FINAL COLUMNS
df = df[[
    "venue_id",
    "event_date",
    "event_name",
    "entrance_fee",
    "web_link",
    "event_time"
]]
# Ensure event_date is in datetime format before filtering
df["event_date"] = pd.to_datetime(df["event_date"],format="mixed")
df_filtered = df[df["event_date"] >= today]

# SAVE CLEAN CSV
df_filtered.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("DONE")
print(f"Saved to:\n{OUTPUT_FILE}")
