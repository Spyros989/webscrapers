import time
from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")

load_dotenv()
load_dotenv(dotenv_path=env_path)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df_events = pd.read_csv("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_ready.csv")
df_events['insert_date'] = pd.Timestamp.now()
df_contents = pd.read_csv("/home/deploy/data/scrapers/cz_clubs_web_events/mcfabrika/mcfabrika_events_contents_ready.csv")
df_contents['insert_date'] = pd.Timestamp.now()
events_column_order = [
    "venue_id",
    "event_name",
    "event_url",
    "snapshot_date",
    "insert_date"
]

df_events[events_column_order]
df_events.drop_duplicates()

contents_column_order = [
    "venue_id",
    "event_url",
    "date",
    "title",
    "location",
    "status",
    "event_date",
    "event_time",
    "insert_date",
    "entrance_fee",
    "web_link"
]

df_contents[contents_column_order]
df_contents.drop_duplicates()
# =========================================================
# CONFIG
# =========================================================
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

df_events.to_sql("dim_venues_fb_events", engine, if_exists="append", index=False)
df_contents.to_sql("dim_venues_fb_events_contents", engine, if_exists="append", index=False)
print("Import complete")
