import time
from sqlalchemy import create_engine,text
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")

load_dotenv()
load_dotenv(dotenv_path=env_path)

timestamp = pd.Timestamp.now()

csv_path = (
    "/home/deploy/data/scrapers/cz_clubs_web_events/"
    "klub007/klub007_events.csv"
)

df_events = pd.read_csv(csv_path, encoding="utf-8-sig")
df_contents = pd.read_csv(csv_path, encoding="utf-8-sig")

df_events["insert_date"] = timestamp
df_contents["insert_date"] = timestamp

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

events_column_order = [
    "venue_id",
    "event_name",
    "event_url",
    "snapshot_date",
    "insert_date"
]
df_events["event_name"]=df_events["title"]
df_events = df_events.drop(columns=[col for col in df_events if col not in events_column_order])
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
    "web_link",
    "duration"
]

df_contents[contents_column_order]
df_contents = df_contents.drop(columns=[col for col in df_contents if col not in contents_column_order])
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

query = text("""
    SELECT event_url from dim_venues_fb_events_contents WHERE venue_id=68;""")

with engine.connect() as conn:
    df_urls = pd.read_sql(query, conn)
print('existing events')
print(df_urls)

# Normalize URLs to avoid whitespace mismatches
db_urls = set(
    df_urls["event_url"]
    .dropna()
    .astype(str)
    .str.strip()
)

with engine.connect() as conn:
    df_urls = pd.read_sql(query, conn)
print('existing events')
print(df_urls)

# Normalize URLs to avoid whitespace mismatches
db_urls = set(
    df_urls["event_url"]
    .dropna()
    .astype(str)
    .str.strip()
)
# Keep only URLs not already in the database
df_events_filtered = df_events[
    ~df_events["event_url"].astype("string").str.strip().isin(db_urls)].copy()

df_contents_filtered = df_events[
    ~df_events["event_url"].astype("string").str.strip().isin(db_urls)].copy()

#df_contents.to_sql("dim_venues_fb_events_contents", engine, if_exists="append", index=False)
#df_events.to_sql("venues_fb_events_raw", engine, if_exists="append", index=False)

#with engine.begin() as conn:
#    conn.execute(text("CALL refresh_dim_venues_fb_events()"))

#print("Import and refresh complete")

