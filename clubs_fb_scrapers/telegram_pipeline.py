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
    "run_pipeline.py",
    "get_attendance.py"
]


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



