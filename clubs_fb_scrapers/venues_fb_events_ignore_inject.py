from sqlalchemy import create_engine
import pandas as pd
from pathlib import Path
import os
from dotenv import load_dotenv

HOME = Path.home()
env_path = (
	HOME
	/"webscrapers"
	/"bands_fb_scrapers"
	/"ma_bands_fb_scrapers"
	/".env"
)
load_dotenv()
load_dotenv(dotenv_path=env_path)

# ----------------------------
# PATH CONFIG
# ----------------------------
HOME = Path.home()
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_fb_events"
INPUT_FILE = DATA_DIR / "venues_fb_events_contents_details.csv"
df = pd.read_csv(INPUT_FILE)
null_df=df[df['date'].isnull()]
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
ignore_urls = null_df['event_url'].to_frame()
ignore_urls = ignore_urls.rename(columns={'event_url': 'url'})
ignore_urls.to_sql("venues_url_ignore", engine, if_exists="append", index=False)

print("Import complete")
