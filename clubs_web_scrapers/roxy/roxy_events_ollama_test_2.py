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
INPUT_FILE= DATA_DIR / "roxy_events.csv"
OUTPUT_FILE = DATA_DIR / "roxy_events_ollama_answers.csv"
OUTPUT_FINAL = DATA_DIR / "roxy_events_entrance_fee.csv"

# ----------------------------
# LOAD ROXY EVENTS
# ----------------------------
keep_columns = ["event_price"]
df_events=pd.read_csv(INPUT_FILE, usecols=keep_columns)
df_events["event_price"] = df_events["event_price"].str.lower()
#print(df_events)


# Store the model's answers here
results = []
start_time = time.perf_counter()

for index, row in df_events.iterrows():

    event_price = row["event_price"]

    prompt = f"""
You are extracting ticket prices.

Here is the event_price data:
{event_price}

Rules:
1. Find the ticket price.
2. If the value is null or missing, return "N/A".
3. All valid ticket prices are above 100.
4. If multiple valid ticket prices exist, choose the smallest.
5. Do not invent prices.

Return ONLY a JSON object:
{{
    "ticket_price": "price or N/A",
    "explanation": "brief explanation"
}}
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

        response.raise_for_status()
        answer = json.loads(response.json()["response"])

        results.append({
            "original_value": event_price,
            "ticket_price": answer.get("ticket_price", "N/A"),
            "explanation": answer.get("explanation", "")
        })

    except (requests.RequestException, ValueError, TypeError) as e:
        results.append({
            "original_value": event_price,
            "ticket_price": "N/A",
            "explanation": f"Error: {e}"
        })

    print(f"Processed row {index + 1}/{len(df_events)}")

df_results = pd.DataFrame(results)
df_results["ticket_price"] = df_results["ticket_price"].replace(["N/A", "null", ""], np.nan)
df_results["entrance_fee"] = (df_results["ticket_price"].str.replace(r"\D", "", regex=True).astype(float)
)

print(f"\nElapsed time: {time.perf_counter() - start_time:.2f} seconds")
df_original=pd.read_csv(INPUT_FILE)

# Safety check: both files must have the same number of rows
if len(df_original) != len(df_results):
    raise ValueError(
        f"Row count mismatch: original={len(df_original)}, "
        f"results={len(df_results)}"
    )

# Attach the result columns by row position
df_original["entrance_fee"] = df_results["entrance_fee"].to_numpy()

# Save the merged file
df_original.to_csv(OUTPUT_FINAL, index=False)
print(f"\nMerged file saved: {OUTPUT_FINAL}")
