import pandas as pd
import re
from pathlib import Path
# =========================
# FILE PATHS
# =========================

INPUT_FILE = Path("/home/deploy/data/scrapers/bajkazylhk/bajkazylhk_events.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/bajkazylhk/bajkazylhk_events_edited.csv")

# =========================
# DATA RULES
# =========================

# Czech month names -> month numbers
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

# Load CSV
df = pd.read_csv(INPUT_FILE)

# Function to parse Czech dates
def parse_czech_date(text):

    # Example:
    # 7. června 202615:00Bajkazyl Hradec Králové

    # Keep only everything BEFORE the time
    cleaned = re.split(r"\d{1,2}:\d{2}", text)[0]

    # Extract:
    # day, month name, year
    match = re.search(
        r"(\d{1,2})\.\s+([^\s]+)\s+(\d{4})",
        cleaned
    )

    if not match:
        return None

    day = int(match.group(1))
    month_name = match.group(2).lower()
    year = int(match.group(3))

    month = MONTHS.get(month_name)

    if not month:
        return None

    return f"{year:04d}-{month:02d}-{day:02d}"

# Create SQL-friendly date column
df["sql_date"] = df["date"].apply(parse_czech_date)

# Keep only desired columns
df = df[["sql_date", "artist", "link"]]

# Save cleaned CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("Done.")
print(f"Saved to:\n{OUTPUT_FILE}")
