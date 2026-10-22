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
df_events=pd.read_csv(INPUT_FILE, usecols=keep_columns)
results = []

for i, sample_text in enumerate(df_events["description"], start=1):

    prompt = f"""Read this text

{sample_text}

Can you make a short list, in English language, what genre of music is this event?
- Be simple.
- Use maximum three music genre labels.
"""

    start_time = time.perf_counter()

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen3:0.6b",
            "prompt": prompt,
            "stream": False,
            "think": False,
            "options": {"temperature": 0.0, "seed": 42},
        },
        timeout=300,
    )
    response.raise_for_status()

    elapsed = time.perf_counter() - start_time
    result = response.json()["response"].strip()

    results.append(result)

    print(f"\n--- EVENT {i} ---")
    print(result)
    print(f"Processing time: {elapsed:.2f} seconds")

print(f"\nFinished! Processed {len(results)} events.")
