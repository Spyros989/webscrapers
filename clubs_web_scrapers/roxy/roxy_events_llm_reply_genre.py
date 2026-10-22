import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime
from pathlib import Path
import time
import os
from dotenv import load_dotenv
import subprocess
import re
import random
import requests
import json
import numpy as np

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
DATA_DIR = HOME / "data" / "scrapers" / "cz_clubs_web_events" / "roxy"
INPUT_FILE= DATA_DIR / "roxy_events_descriptions.csv"
OUTPUT_FILE = DATA_DIR / "roxy_events_ollama_genres.csv"
OUTPUT_FINAL = DATA_DIR / "roxy_events_entrance_fee.csv"

# ----------------------------
# LOAD ROXY EVENTS
# ----------------------------
keep_columns = ["description"]
df_events=pd.read_csv(INPUT_FILE, usecols=keep_columns, nrows=4)
#df_events["event_price"] = df_events["event_price"].str.lower()
#print(df_events)


# Store the model's answers here
results = []
start_time = time.perf_counter()

for index, row in df_events.iterrows():

    event_description = row["description"]

    prompt = f"""
Read this text

{event_description}

Can you make a short list, in English language, what genre of music is this event?
-Be simple.
-Use maximum three music genre labes.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen3:0.6b",
                "prompt": prompt,
                "stream": False,
                "Think": False,
                "options": {
                    "temperature": 0.0,
                    "seed": 42
                }
            },
            timeout=180
        )
        response.raise_for_status()

        answer = response.json()["response"].strip()

        results.append({
        "music_genre": answer
        })

        print(answer)

     except (requests.RequestException, ValueError, TypeError, KeyError) as e:
       print("Error:", e)

