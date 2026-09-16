import pandas as pd
from sqlalchemy import create_engine

# load CSV
df=pd.read_csv("/home/deploy/data/scrapers/cz_clubs_web_events/kabinet_muz/kabinet_nuz_events_daily_clean_fb_links.csv")
# connect to postgres
engine = create_engine("postgresql+psycopg2://postgres:2102232094@localhost:5432/postgres")

# write to table
df.to_sql("kabinetmuz_test", engine, if_exists="append", index=False)

print("Import complete")
