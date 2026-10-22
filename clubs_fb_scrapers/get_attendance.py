import subprocess
import sys
import time
from datetime import datetime
import os
from pathlib import Path
from sqlalchemy import create_engine,text
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================
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


# =========================================================
# PY SCRIPTS CONFIG
# =========================================================
scripts = [
    "venues_fb_events_responds.py",
    "venues_fb_events_responds_clean.py",
    "venues_fb_events_responds_clean_inject.py"]

print("=" * 80)
print("PIPELINE START")
print(
    "Started:",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
print("=" * 80)

pipeline_start = time.time()


# =========================================================
# RUN PYTHON SCRIPTS
# =========================================================
for script in scripts:

    print("\n" + "-" * 80)
    print(f"Running {script}")

    script_start = time.time()

    print(
        "Started:",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    result = subprocess.run(
        [sys.executable, script],
        cwd="/home/deploy/webscrapers/clubs_fb_scrapers",
    )

    script_end = time.time()
    duration = script_end - script_start

    print(
        "Finished:",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    print(f"Duration: {duration:.1f} seconds")

    if result.returncode != 0:

        print(f"\nERROR: {script} failed.")

        sys.exit(1)


# =========================================================
# CALL DATABASE PROCEDURE
# =========================================================

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

print("\n" + "-" * 80)
print("Calling PostgreSQL procedure: refresh_prd_fb_events()")


engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
with engine.begin() as conn:
    conn.execute(text("CALL refresh_prd_fb_events()"))

print("Procedure call completed successfully.")


# =========================================================
# SUMMARY
# =========================================================
pipeline_end = time.time()
total = pipeline_end - pipeline_start

hours = int(total // 3600)
minutes = int((total % 3600) // 60)
seconds = int(total % 60)

print("\n" + "=" * 80)
print("PIPELINE COMPLETE")
print(
    "Finished:",
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
)
print(
    f"Total runtime: {hours:02d}:{minutes:02d}:{seconds:02d}"
)
print("=" * 80)
