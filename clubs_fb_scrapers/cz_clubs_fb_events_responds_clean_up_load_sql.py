import time
from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")
load_dotenv()

load_dotenv()
load_dotenv(dotenv_path=env_path)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
df = pd.read_csv("/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_responds_daily_clean.csv")
df['insert_date'] = pd.Timestamp.now()
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

df.to_sql("cz_clubs_fb_events_responds", engine, if_exists="append", index=False)

print("Import complete")
