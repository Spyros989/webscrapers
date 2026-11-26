import time
from sqlalchemy import create_engine,text
import pandas as pd
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv
import requests
import json


env_path = Path("/home/deploy/webscrapers/bands_fb_scrapers/ma_bands_fb_scrapers/.env")

load_dotenv()
load_dotenv(dotenv_path=env_path)

csv_path = (
    "/home/deploy/data/scrapers/cz_clubs_web_events/"
    "garageclub/garageclub_events.csv"
)


df_events = pd.read_csv(csv_path, encoding="utf-8-sig")
# Website events
website_events = (
    df_events[["event_name", "event_date"]]
    .reset_index(drop=True)
    .copy()
)

website_events["id"] = website_events.index


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

query = text("""
    SELECT title as event_name,event_date from dim_venues_fb_events_contents WHERE venue_id=51;""")

with engine.connect() as conn:
    df_urls = pd.read_sql(query, conn)

db_urls = set(
    df_urls[["event_name","event_date"]]
    .dropna()
)

# Facebook events
facebook_events = (
    df_urls[["event_name", "event_date"]]
    .reset_index(drop=True)
    .copy()
)

facebook_events["id"] = facebook_events.index

# Convert dates to strings
for df in [website_events, facebook_events]:
    df["event_date"] = pd.to_datetime(
        df["event_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

# Prepare numbered lists
website_list = website_events.to_dict("records")
facebook_list = facebook_events.to_dict("records")

print(website_list)
print(facebook_list)
# Join by date
date_candidates = website_events.merge(
    facebook_events,
    on="event_date",
    how="inner",
    suffixes=("_website", "_facebook")
)

print(date_candidates[
    ["event_name_website", "event_name_facebook", "event_date"]
])

# 2. Prepare candidate pairs for Ollama
candidate_events = date_candidates[
    ["id_website", "event_name_website",
     "id_facebook", "event_name_facebook"]
].rename(columns={
    "id_website": "id_a",
    "id_facebook": "id_b"
}).to_dict("records")

# 3. Send all candidates to Ollama in ONE request
# Use the simplified prompt from above.

matches = []

prompt = f"""
You compare event titles.

For EACH candidate pair below, independently decide whether
the two titles describe the SAME event.

CANDIDATE PAIRS:
{json.dumps(candidate_events, ensure_ascii=False)}

Rules:
- Different capitalization does not matter.
- Czech diacritics do not matter.
- Punctuation does not matter.
- Minor spelling mistakes are acceptable.
- Additional words like KONCERT or BESEDA are acceptable.
- Shortened titles are acceptable.
- Completely different event titles are NOT a match.

IMPORTANT:
Evaluate every single pair.
Do not skip any pair.
Do not stop after finding a match.
Use the original IDs exactly as provided.

Return one result for EVERY candidate pair.

Return ONLY valid JSON in this structure:
{{
    "results": [
        {{
            "id_a": "original website ID",
            "id_b": "original Facebook ID",
            "match": true
        }}
    ]
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
        timeout=300
    )

    response.raise_for_status()

    answer = json.loads(response.json()["response"])

    print("Ollama response:")
    print(json.dumps(answer, indent=4, ensure_ascii=False))

    results = answer.get("results", [])
    print("Number of results:", len(results))

    for item in results:
        print(
            "ID A:", item.get("id_a"),
            "| ID B:", item.get("id_b"),
            "| Match:", repr(item.get("match")),
            "| Type:", type(item.get("match"))
        )


    matches = [
        m for m in answer.get("results", [])
        if m.get("match") is True
    ]

    print("Extracted matches:")
    print(matches)

except (requests.RequestException, ValueError, TypeError, KeyError) as e:
    print(f"Ollama matching error: {e}")
    matches = []

# Create mapping DataFrame
df_mapping = pd.DataFrame(
    matches,
    columns=["id_a", "id_b", "match"]
)

print("\nMatched event IDs:")
print(df_mapping)

# Get original records using the IDs
website_matched = website_events.iloc[
    df_mapping["id_a"].values
].reset_index(drop=True)

facebook_matched = facebook_events.iloc[
    df_mapping["id_b"].values
].reset_index(drop=True)

# Combine the matched records
df_final = pd.concat(
    [
        website_matched.add_prefix("website_"),
        facebook_matched.add_prefix("facebook_")
    ],
    axis=1
)

print(df_final)
