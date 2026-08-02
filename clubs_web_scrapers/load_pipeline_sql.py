import subprocess
import sys
import time
from datetime import datetime
from turtle import pd
from sqlalchemy import create_engine
import pandas as pd
# =========================================================
# CONFIG
# =========================================================
files = [
"/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_clean_fb_links.csv"
,"/home/deploy/data/scrapers/cz_clubs_web_events/bajkazylhk/bajkazylhk_events_edited_fb_links.csv"
,"/home/deploy/data/scrapers/cz_clubs_web_events/kabinet_muz/kabinet_nuz_events_daily_clean_fb_links.csv"
]


# Create engine once
engine = create_engine(
    "postgresql+psycopg2://postgres:2102232094@localhost:5432/postgres"
)

print("=" * 80)
print("PIPELINE START")
print("Started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

pipeline_start = time.time()

for file in files:

    print("\n" + "-" * 80)
    print(f"Loading: {file}")

    script_start = time.time()

    print("Started:",
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    try:
        df = pd.read_csv(file)
        df.to_sql(
            "events_web_scrapers",
            engine,
            if_exists="append",
            index=False
        )

    except Exception as e:
        print(f"ERROR loading {file}")
        print(e)
        sys.exit(1)

    duration = time.time() - script_start

    print("Finished:",
          datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Duration: {duration:.1f} seconds")

# Pipeline summary
total = time.time() - pipeline_start

hours = int(total // 3600)
minutes = int((total % 3600) // 60)
seconds = int(total % 60)

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print("Finished:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print(f"Total runtime: {hours:02d}:{minutes:02d}:{seconds:02d}")
print("=" * 80)
