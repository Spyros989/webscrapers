import pandas as pd
import re
from pathlib import Path
from datetime import datetime,timedelta
# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "/home/deploy/data/scrapers/cz_clubs_fb_events/venues_fb_events_contents_clean.csv"
OUTPUT_FILE = "/home/deploy/data/scrapers/cz_clubs_fb_events/venues_fb_events_contents_clean_dates.csv"

# =========================================================
# LOAD CSV
# =========================================================

df = pd.read_csv(INPUT_FILE)

# =========================================================
# VALID WEEKDAYS
# =========================================================

weekdays = (
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
)

# =========================================================
# PARSER
# =========================================================

def parse_fb_date(value):

    if pd.isna(value) or str(value).strip() == "":
        return []

    text = str(value).strip()

    # Facebook sometimes uses special spaces
    text = text.replace("\u202f", " ")
    text = text.replace("\xa0", " ")

    current_year = pd.Timestamp.now().year

    # =========================================================
    # CASE 0
    # Relative Facebook dates
    # =========================================================

    today = pd.Timestamp.now().date()

    relative_days = {
        "today": 0,
        "tomorrow": 1,
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    m = re.search(
        r"^(Today|Tomorrow|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
        r"\s+at\s+"
        r"(.+?)"
        r"(?:\s+[–-]\s+(.+?))?"
        r"(?:\s+[A-Z]{3,5})?$",
        text,
        re.IGNORECASE
    )

    if m:

        relative_day = m.group(1).lower()
        start_time = m.group(2).strip()

        day_value = relative_days[relative_day]

        if relative_day in ("today", "tomorrow"):

            event_date = today + timedelta(days=day_value)

        else:

            current_weekday = today.weekday()

            target_weekday = day_value

            days_ahead = (
                target_weekday - current_weekday
            ) % 7

            event_date = today + timedelta(
                days=days_ahead
            )

        return [
            {
                "status": "ok",
                "event_date": event_date,
                "event_time": start_time
            }
        ]


    # =========================================================
    # CASE 1
    # Thursday, June 25, 2026 at 6:30 PM CEST
    # =========================================================

    m = re.search(
        r"^[A-Za-z]+,\s+"
        r"([A-Za-z]+\s+\d{1,2},\s+\d{4})"
        r"\s+at\s+"
        r"(.+?)"
        r"(?:\s+[A-Z]{3,5})?$",
        text,
        re.IGNORECASE
    )

    if m:

        date_part = m.group(1)
        time_part = m.group(2).strip()

        try:
            event_date = pd.to_datetime(
                date_part,
                format="%B %d, %Y"
            ).date()
        except Exception:
            return []

        return [
            {
                "status": "ok",
                "event_date": event_date,
                "event_time": time_part
            }
        ]

    # =========================================================
    # CASE 2
    # Aug 21 at 5:00 PM – Aug 22 at 6:00 AM CEST
    #
    # No year -> use running year.
    #
    # IMPORTANT:
    # We keep the START TIME (5:00 PM) for every date.
    # The final 6:00 AM is treated as END TIME and discarded.
    # =========================================================

    m = re.search(
        r"^"
        r"([A-Za-z]{3,9}\s+\d{1,2})"
        r"\s+at\s+"
        r"(.+?)"
        r"\s+[–-]\s+"
        r"([A-Za-z]{3,9}\s+\d{1,2})"
        r"\s+at\s+"
        r"(.+?)"
        r"(?:\s+[A-Z]{3,5})?"
        r"$",
        text,
        re.IGNORECASE
    )

    if m:

        start_date_text = m.group(1)
        start_time = m.group(2).strip()
        end_date_text = m.group(3)

        try:
            start_date = pd.to_datetime(
                f"{start_date_text} {current_year}",
                format="%b %d %Y"
            ).date()
        except Exception:

            try:
                start_date = pd.to_datetime(
                    f"{start_date_text} {current_year}",
                    format="%B %d %Y"
                ).date()
            except Exception:
                return []

        try:
            end_date = pd.to_datetime(
                f"{end_date_text} {current_year}",
                format="%b %d %Y"
            ).date()
        except Exception:

            try:
                end_date = pd.to_datetime(
                    f"{end_date_text} {current_year}",
                    format="%B %d %Y"
                ).date()
            except Exception:
                return []

        # Generate one row for every calendar day
        dates = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )

        return [
            {
                "status": "ok",
                "event_date": d.date(),
                "event_time": start_time
            }
            for d in dates
        ]

    # =========================================================
    # CASE 3
    # Nov 7, 2025 at 5:00 PM – Nov 9, 2025 at 3:00 PM CET
    #
    # Full dates.
    # Keep START TIME for every date.
    # =========================================================

    m = re.search(
        r"^"
        r"([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
        r"\s+at\s+"
        r"(.+?)"
        r"\s+[–-]\s+"
        r"([A-Za-z]{3,9}\s+\d{1,2},\s+\d{4})"
        r"\s+at\s+"
        r"(.+?)"
        r"(?:\s+[A-Z]{3,5})?"
        r"$",
        text,
        re.IGNORECASE
    )

    if m:

        start_date_text = m.group(1)
        start_time = m.group(2).strip()
        end_date_text = m.group(3)

        try:
            start_date = pd.to_datetime(
                start_date_text
            ).date()

            end_date = pd.to_datetime(
                end_date_text
            ).date()

        except Exception:
            return []

        dates = pd.date_range(
            start=start_date,
            end=end_date,
            freq="D"
        )

        return [
            {
                "status": "ok",
                "event_date": d.date(),
                "event_time": start_time
            }
            for d in dates
        ]

    # =========================================================
    # Everything else = error
    # Example:
    # 25
    # =========================================================

    return [
        {
            "status": "error",
            "event_date": None,
            "event_time": None
        }
    ]
# =========================================================
# PARSE / EXPAND EVENT DATES
# =========================================================

parsed_rows = []

for _, row in df.iterrows():

    results = parse_fb_date(row["date"])

    # Keep original row information
    for result in results:

        new_row = row.copy()

        new_row["status"] = result["status"]
        new_row["event_date"] = result["event_date"]
        new_row["event_time"] = result["event_time"]

        parsed_rows.append(new_row)

df = pd.DataFrame(parsed_rows)

# =========================================================
# SAVE
# =========================================================

df.to_csv(OUTPUT_FILE, index=False)

print(f"Saved: {OUTPUT_FILE}")

print("\nSummary:")
print(df["status"].value_counts(dropna=False))
