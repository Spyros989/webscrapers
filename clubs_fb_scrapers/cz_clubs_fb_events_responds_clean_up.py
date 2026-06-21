import pandas as pd

input_file ="/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_responds_daily.csv"
#"cz_clubs_fb_events_responds_daily.csv"

df = pd.read_csv(input_file)

# Ensure string format
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

# (optional) attendance extraction if still needed
df["attendance_count"] = (
    df["attendance"]
    .astype(str)
    .str.extract(r"(\d+)", expand=False)
    .astype("Int64")
)

# ===== Extract attendance number =====
def parse_attendance(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip().upper()

    # Match: 23, 1.1K, 2K, 3.5M, etc.
    match = pd.Series([text]).str.extract(
        r'(\d+(?:\.\d+)?)\s*([KM]?)',
        expand=True
    ).iloc[0]

    if pd.isna(match[0]):
        return pd.NA

    number = float(match[0])
    suffix = match[1]

    if suffix == "K":
        number *= 1_000
    elif suffix == "M":
        number *= 1_000_000

    return int(round(number))

df["attendance_count"] = (
    df["attendance"]
    .apply(parse_attendance)
    .astype("Int64")
)
# ===== COLUMN ORDER CONFIG =====
# Put your preferred order here
column_order = [
    "url",
    "attendance",
    "attendance_count",
    "snapshot_date",
    "snapshot_time"
]

# Add any missing columns automatically (so script won't break)
for col in df.columns:
    if col not in column_order:
        column_order.append(col)

df = df[column_order]
df = df.drop(columns=["extraction_datetime"])
# ===== SAVE =====
# Save output
output_file = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_responds_daily_clean.csv"
df.to_csv(output_file, index=False)

print(f"Processed {len(df)} rows")
print(f"Saved to {output_file}")
