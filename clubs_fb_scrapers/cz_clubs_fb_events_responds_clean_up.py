import pandas as pd

input_file = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_responds_daily.csv"

df = pd.read_csv(input_file)

# =========================================================
# SAFETY: normalize key column first
# =========================================================
df["extraction_datetime"] = df["extraction_datetime"].fillna("").astype(str)

# Anything over 50 characters is almost certainly not a valid attendance string
df.loc[df["attendance"].str.len() > 50, "attendance"] = "ERROR"
# =========================================================
# SPLIT DATE / TIME (SAFE)
# =========================================================
dt_split = df["extraction_datetime"].str.split("_", expand=True)


# ensure both columns exist
if dt_split.shape[1] < 2:
    dt_split[1] = ""

df["snapshot_date"] = pd.to_datetime(
    dt_split[0],
    format="%Y-%m-%d",
    errors="coerce"
).dt.date

df["snapshot_time"] = (
    dt_split[1]
    .fillna("")
    .astype(str)
    .str.replace(r"(\d{2})(\d{2})(\d{2})", r"\1:\2:\3", regex=True)
)

# =========================================================
# ATTENDANCE PARSER
# =========================================================
def parse_attendance(value):
    if pd.isna(value):
        return pd.NA

    text = str(value).strip().upper()

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

df["attendance_count"] = df["attendance"].apply(parse_attendance).astype("Int64")

# =========================================================
# COLUMN ORDER
# =========================================================
column_order = [
    "url",
    "attendance",
    "attendance_count",
    "snapshot_date",
    "snapshot_time"
]

for col in df.columns:
    if col not in column_order:
        column_order.append(col)

df = df[column_order]
df = df.drop(columns=["error"], errors="ignore")
# drop only if exists (safer)
if "extraction_datetime" in df.columns:
    df = df.drop(columns=["extraction_datetime"])

# =========================================================
# SAVE
# =========================================================
output_file = "/home/deploy/data/scrapers/cz_clubs_fb_events/cz_clubs_fb_events_responds_daily_clean.csv"
df.to_csv(output_file, index=False)

print(f"Processed {len(df)} rows")
print(f"Saved to {output_file}")
