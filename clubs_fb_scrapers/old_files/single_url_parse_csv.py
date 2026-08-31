import pandas as pd


INPUT_FILE = "facebook_events.csv"
OUTPUT_FILE = "facebook_events_clean.csv"


# =========================================================
# READ CSV
# =========================================================

df = pd.read_csv(INPUT_FILE)


# =========================================================
# EXTRACT EVENT DATA
# =========================================================

def extract_event(text):

    lines = text.splitlines()

    for i, line in enumerate(lines):

        if line.strip() == "Visual Arts":

            # Visual Arts
            #     ↓
            # 9
            # Sep 9, 2021 at 5:00 PM – Sep 11, 2021 at 5:00 PM CEST
            # Sweetsen Fest...
            # Sweetsen fest - Frýdek-Místek sobě!

            date = lines[i + 2]
            title = lines[i + 3]
            location = lines[i + 4]

            return date, title, location

    # If "Visual Arts" wasn't found
    return None, None, None


# =========================================================
# APPLY TO EVERY EVENT
# =========================================================

df[["date", "title", "location"]] = df["visible_text"].apply(
    lambda x: pd.Series(extract_event(x))
)


# =========================================================
# KEEP ONLY WHAT WE NEED
# =========================================================

result = df[
    [
        "event_url",
        "date",
        "title",
        "location"
    ]
]


# =========================================================
# SAVE
# =========================================================

result.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)


print(result)
print()
print(f"Saved to: {OUTPUT_FILE}")
