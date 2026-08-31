import pandas as pd


# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "/home/deploy/data/scrapers/cz_bands_fb_events/bands_fb_events_contents.csv"

OUTPUT_FILE = "/home/deploy/data/scrapers/cz_bands_fb_events/bands_fb_events_parsed.csv"


# =========================================================
# LOAD SCRAPED DATA
# =========================================================

df = pd.read_csv(INPUT_FILE)

print(f"Loaded {len(df)} events")


# =========================================================
# PARSE EVENT CONTENT
# =========================================================

def parse_event(text):

    if pd.isna(text):
        return None, None, None

    lines = text.splitlines()

    for i, line in enumerate(lines):

        if line.strip() == "Visual Arts":

            try:
                date = lines[i + 2].strip()
                title = lines[i + 3].strip()
                location = lines[i + 4].strip()

                return date, title, location

            except IndexError:
                return None, None, None

    return None, None, None


# =========================================================
# APPLY PARSER
# =========================================================

df[["date", "title", "location"]] = df["visible_text"].apply(
    lambda x: pd.Series(parse_event(x))
)


# =========================================================
# SELECT FINAL COLUMNS
# =========================================================

result = df[
    [
        "band_id",
        "url",
        "date",
        "title",
        "location"
    ]
].copy()


# Rename URL column

result = result.rename(
    columns={
        "url": "event_url"
    }
)


# =========================================================
# SAVE
# =========================================================

result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


# =========================================================
# SHOW RESULTS
# =========================================================

print("\nResults:")
print(result)

print("\nSaved to:")
print(OUTPUT_FILE)
