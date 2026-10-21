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
# LOAD ROXY EVENTS
# ----------------------------
keep_columns = ["event_price"]
df_events=pd.read_csv('/home/deploy/data/scrapers/cz_clubs_web_events/roxy/roxy_events.csv', usecols=keep_columns)
#print("\n--- EVENTS ---")
print(df_events)
# ----------------------------
# TEST OLLAMA WITH ONE EVENT
# ----------------------------
#events_text = "\n".join(
#    f"{i+1}. {event}"
#    for i, event in enumerate(df_events["event"])
#)

prompt = f"""Use this dataset

{df_events}

Read all len({df_events}) rows until the end of the text.
Each line is information on an event.
For each row, how much costs the ticket?
If there is a null value, mark it as N/A.
All amounts are above 100.
If you find more than one value, keep the smallest ticket price.
For each row, explain me how did you find the answer.
"""

start_time = time.perf_counter()
response = requests.post("http://localhost:11434/api/generate",json={
        	"model": "qwen3:0.6b",
        	"prompt": prompt,
        	"stream": False,
        	"think": False,
		"options": {"temperature": 0.0,"seed": 42}})

elapsed = time.perf_counter() - start_time

result = response.json()["response"].strip()
print("\n--- RAW OLLAMA RESPONSE ---")
print(result)
print(f"Processing time: {elapsed:.2f} seconds")
print(df_events)
