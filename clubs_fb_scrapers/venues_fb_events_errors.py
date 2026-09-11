import os
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine,text

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")
load_dotenv()
load_dotenv(dotenv_path=env_path)

df=pd.read_csv('~/data/scrapers/cz_clubs_fb_events/venues_fb_events_clean.csv')
venue_ids=df.loc[df['event_name'].isna(),'venue_id'].tolist()

missing_events = df.loc[
    df["event_name"].isna(),
    ["venue_id"]
].copy()

missing_events["extraction_date"] = datetime.now().strftime("%Y-%m-%d")
missing_events["extraction_time"] = datetime.now().strftime("%H:%M:%S")

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

missing_events.to_sql("venues_fb_events_errors", engine, if_exists="append", index=False)
print("completed")
