import pandas as pd

input_file ="/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_daily.csv"
#"cz_clubs_fb_events_responds_daily.csv"

df = pd.read_csv(input_file)

# Ensure string format <type(str)
df["extraction_datetime"] = df["extraction_datetime"].astype(str)

# Split into date and time parts
df["snapshot_date"] = pd.to_datetime(
    df["extraction_datetime"].str.split("_").str[0],
    format="%Y-%m-%d",
    errors="coerce"
).dt.date

df["snapshot_time"] = (
    df["extraction_datetime"]
    .str.split("_")
    .str[1]
    .str.replace(r"(\d{2})(\d{2})(\d{2})", r"\1:\2:\3", regex=True)
)

# ===== COLUMN ORDER CONFIG =====
# Put your preferred order here
column_order = [
    "club_name",
    "event_name",
    "event_url",
    "snapshot_date",
    "snapshot_time",
    "extraction_datetime"
]

# Add any missing columns automatically (so script won't break)
for col in df.columns:
    if col not in column_order:
        column_order.append(col)

df = df[column_order]
df = df.drop(columns=["extraction_datetime"])
# ===== SAVE =====
# Save output
output_file = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_daily_clean.csv"
df.to_csv(output_file, index=False)

print(f"Processed {len(df)} rows")
print(f"Saved to {output_file}")
