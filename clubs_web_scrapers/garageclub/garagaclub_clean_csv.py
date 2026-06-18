import pandas as pd
import re
from pathlib import Path

INPUT_FILE = Path("/home/deploy/data/scrapers/garageclub/garageclub.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/garageclub/garageclub_events_edited.csv")

# load CSV
df = pd.read_csv(INPUT_FILE)

def split_raw(text):

    # Example:
    # 16.5.2026 SOBOTNÍ diskotéka s DJ Danem Svobodou

    # extract date at beginning
    match = re.match(
        r"(\d{1,2}\.\d{1,2}\.\d{4})\s+(.*)",
        str(text)
    )

    if not match:
        return pd.Series([None, text])

    raw_date = match.group(1)
    title = match.group(2).strip()

    # convert to SQL format
    day, month, year = raw_date.split(".")

    sql_date = f"{year}-{int(month):02d}-{int(day):02d}"

    return pd.Series([sql_date, title])

# create new columns
df[["sql_date", "artist"]] = df["raw"].apply(split_raw)

# keep only clean columns
df = df[["sql_date", "artist", "link","extraction_datetime"]]

# save cleaned CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("Done")
print(f"Saved to:\n{OUTPUT_FILE}")
