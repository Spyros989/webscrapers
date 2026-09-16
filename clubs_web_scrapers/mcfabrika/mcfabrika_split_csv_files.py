import pandas as pd
import re
from pathlib import Path
from datetime import date,datetime
# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "mcfabrika"
INPUT_FILE = DATA_DIR / "mcfabrika_events_clean_fb_links.csv"
OUTPUT_FILE_CONTENTS = DATA_DIR / "mcfabrika_events_contents_ready.csv"
OUTPUT_FILE_EVENTS = DATA_DIR / "mcfabrika_events_ready.csv"
## Normalize today's date to midnight for an accurate comparison
today = pd.Timestamp.now().normalize()
# LOAD CSV
df = pd.read_csv(INPUT_FILE)
df_copy=df.copy()
# Adding additional columns
df["date"]=''
df["status"] = 'ok'
df["title"] = df["event_name"]
df["location"] = 'Jeronýmova 6 37001 Ceske Budejovice, Czech Republic'

# Convert the text column to a datetime format
temp_time = pd.to_datetime(df['event_time'], format='%H:%M')

# Re-format it to a 12-hour clock with AM/PM
df["event_time"] = temp_time.dt.strftime('%I:%M %p')

df = df[[
    "venue_id",
    "event_url",
    "date",
    "title",
    "location",
    "status",
    "event_date",
    "event_time",
    "entrance_fee",
    "web_link"
]]
df_copy["snapshot_date"] = today.strftime('%Y-%m-%d')
df_copy = df_copy[[
    "venue_id",
    "event_name",
    "event_url",
    "snapshot_date"
]]

# SAVE CLEAN CSV
df.to_csv(
    OUTPUT_FILE_CONTENTS,
    index=False,
    encoding="utf-8-sig"
)

df_copy.to_csv(
    OUTPUT_FILE_EVENTS,
    index=False,
    encoding="utf-8-sig"
)

print("DONE")
print(f"Saved events csv to:\n{OUTPUT_FILE_EVENTS}")
print(f"Saved contents csv to:\n{OUTPUT_FILE_CONTENTS}")
