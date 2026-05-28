from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime

# =========================
# FILE PATHS
# =========================
BASE_DIR = Path("/home/deploy/data/scrapers/metal_archives")

INPUT_FILE = BASE_DIR / "cz_metal_bands_raw.csv"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

OUTPUT_FILE = BASE_DIR / f"cz_metal_bands_edited_{timestamp}.csv"
# ----------------------------
# Extract band name + URL
# ----------------------------
df=pd.read_csv(INPUT_FILE)
band_names = []
band_urls = []

for html in df["Band"]:

    soup = BeautifulSoup(html, "html.parser")

    a = soup.find("a")

    if a:
        band_names.append(a.text.strip())
        band_urls.append(a.get("href"))
    else:
        band_names.append(None)
        band_urls.append(None)

# ----------------------------
# Clean status column
# ----------------------------

statuses = []

for html in df["Status"]:

    soup = BeautifulSoup(str(html), "html.parser")

    text = soup.get_text(strip=True)

    statuses.append(text)

df["BandName"] = band_names
df["BandURL"] = band_urls
df["CleanStatus"] = statuses

# ----------------------------
# Keep only active bands
# ----------------------------

active_df = df[df["CleanStatus"] == "Active"].copy()

# ----------------------------
# Optional: keep only useful columns
# ----------------------------

active_df = active_df[
    [
        "BandName",
        "BandURL",
        "Genre",
        "Location",
        "CleanStatus"
    ]
]

# ----------------------------
# Save cleaned dataset
# ----------------------------

active_df.to_csv(OUTPUT_FILE,index=False)
print(f"\nTotal active bands: {len(active_df)}")
print("Saved to czech_active_metal_bands_cleaned.csv")
