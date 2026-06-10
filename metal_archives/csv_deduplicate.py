import pandas as pd
from pathlib import Path

INPUT_FILE = Path("/home/deploy/data/scrapers/metal_archives/cz_metal_bands_edited_20260607.csv")
OUTPUT_FILE = Path("/home/deploy/data/scrapers/metal_archives/cz_metal_bands_edited_dedup_20260607.csv")

df = pd.read_csv(INPUT_FILE)
df=df.drop_duplicates(subset=['BandURL'], keep='first')
df.to_csv(OUTPUT_FILE, index=False)
print('done')
