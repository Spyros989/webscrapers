import pandas as pd
import re
from pathlib import Path

# =========================
# FILE PATHS
# =========================

INPUT_FILE = Path("/home/deploy/data/scrapers/kabinet_muz/kabinet_muz_events_daily.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/kabinet_muz/kabinet_muz_events_daily_clean.csv")

# =========================
# DATA RULES
# =========================

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

# =========================
# LOAD DATA
# =========================

df = pd.read_csv(INPUT_FILE)

# =========================
# DATE PARSER
# =========================

def parse_date(month_text, date_text):

    # extract year (e.g. "květen 2026")
    year_match = re.search(r"(\d{4})", month_text)
    year = int(year_match.group(1))

    # extract month name
    month_name = month_text.split()[0].lower()
    month = MONTHS[month_name]

    # extract day (e.g. "8.")
    day_match = re.search(r"(\d{1,2})\.", date_text)
    day = int(day_match.group(1))

    return f"{year:04d}-{month:02d}-{day:02d}"

# =========================
# TRANSFORM DATA
# =========================

df["sql_date"] = df.apply(
    lambda row: parse_date(row["month"], row["date"]),
    axis=1
)

df["sql_date"] = pd.to_datetime(df["sql_date"])

df = df[["sql_date", "artist", "link","extraction_datetime"]]

# =========================
# SAVE RESULT
# =========================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("Done.")
print(f"Saved cleaned file to:\n{OUTPUT_FILE}")
