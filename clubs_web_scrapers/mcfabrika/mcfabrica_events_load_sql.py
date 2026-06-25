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
df = pd.read_csv("/home/deploy/data/scrapers/clubs_webscrapers/mcfabrika/mcfabrika_events_edited_fb_links.csv")
df['insert_date'] = pd.Timestamp.now()
df['club_name'] = "MC Fabrika"

column_order = [
    "club_name",
    "artist",
    "facebook_event",
    "sql_date",
    "event_time",
    "insert_date"
]
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

df.to_sql("cz_clubs_web_events_daily", engine, if_exists="append", index=False)

print("Import complete")
