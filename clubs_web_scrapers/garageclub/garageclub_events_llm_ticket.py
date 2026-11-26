import pandas as pd
from datetime import datetime
from pathlib import Path
import time
import os
from dotenv import load_dotenv
import subprocess
import re
import requests
import json
# ----------------------------
# VENV CONFIG
# ----------------------------
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
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "garageclub"
INPUT_FILE= DATA_DIR / "garageclub_events.csv"
OUTPUT_FILE = DATA_DIR / "garageclub_events_ollama_answers.csv"
#OUTPUT_FINAL = DATA_DIR / "roxy_events_entrance_fee.csv"

# ----------------------------
# LOAD ROXY EVENTS
# ----------------------------
keep_columns = ["event_name","event_date"]
df_events=pd.read_csv(INPUT_FILE, usecols=keep_columns)

# Website events
website_events = (
    df_events[["event_name", "event_date"]]
    .reset_index(drop=True)
    .copy()
)

website_events["id"] = website_events.index

# Store the model's answers here
results = []
start_time = time.perf_counter()

for index, row in df_events.iterrows():

    event_name = row["event_name"]
    event_date = row["event_date"]
    prompt = f"""
You are reading event names.

Here is the event info:
{event_name} , {event_date}
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.0,
                    "seed": 42
                }
            },
            timeout=180
        )

    except (requests.RequestException, ValueError, TypeError) as e:
        results.append({
            "original_value": event_price,
            "ticket_price": "N/A",
            "explanation": f"Error: {e}"
        })

    
