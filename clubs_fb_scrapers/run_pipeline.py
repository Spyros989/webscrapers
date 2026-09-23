import subprocess
import sys
import time
from datetime import datetime
import os

import psycopg2
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT
# =========================================================
load_dotenv(
    "/home/deploy/webscrapers/clubs_fb_scrapers/.env"
)


# =========================================================
# PY SCRIPTS CONFIG
# =========================================================
scripts = [
    "venues_fb_events.py",
    "venues_fb_events_clean.py",
    "venues_fb_events_clean_inject.py",
    "venues_fb_events_contents.py",
    "venues_fb_events_contents_parsed.py",
    "venues_fb_events_contents_parsed_dates.py",
    "venues_fb_events_contents_parsed_dates_inject.py",
    "venues_fb_events_responds.py",
    "venues_fb_events_responds_clean.py",
    "venues_fb_events_responds_clean_inject.py",
    "venues_fb_events_errors.py",
]


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
print("\n" + "-" * 80)
print("Calling PostgreSQL procedure: refresh_prd_fb_events()")

procedure_start = time.time()

try:

    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute(
        "CALL refresh_prd_fb_events();"
    )

    cursor.close()
    conn.close()

    procedure_end = time.time()
    procedure_duration = procedure_end - procedure_start

    print(
        "Procedure completed successfully."
    )

    print(
        f"Procedure duration: {procedure_duration:.1f} seconds"
    )

except Exception as e:

    print(
        "\nERROR: refresh_prd_fb_events() failed."
    )

    print(e)

    sys.exit(1)


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
