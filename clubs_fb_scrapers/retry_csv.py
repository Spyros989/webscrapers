import pandas as pd
from pathlib import Path

BASE_DIR = Path("/home/deploy/data/scrapers/cz_clubs_fb_events")

INPUT_FILE = BASE_DIR / "cz_clubs_fb_events_dates_additional_20260610.csv"
RETRY_FILE = BASE_DIR / "cz_clubs_fb_events_dates_additional_20260610_retry.csv"

df = pd.read_csv(INPUT_FILE)

retry_df = df[
    df["date"].isin(["About", "Privacy Center"])
]

retry_df.to_csv(RETRY_FILE, index=False)

print(f"Found {len(retry_df)} failed events")
print(f"Saved retry file -> {RETRY_FILE}")
