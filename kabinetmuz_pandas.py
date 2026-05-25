from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://www.kabinetmuz.cz/program"
BASE_URL = "https://www.kabinetmuz.cz"

OUTPUT_FILE = r"C:\Users\Spyro\Desktop\test_scrappers\kabinet_muz\kabinet_muz_events.csv"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    page.goto(URL, wait_until="networkidle")

    html = page.content()

    browser.close()

soup = BeautifulSoup(html, "html.parser")

results = []
current_month = None

# Walk through elements in order
for element in soup.find_all(["h2", "a"]):

    # Month headings
    if element.name == "h2":
        current_month = element.get_text(strip=True)

    # Event items
    elif element.name == "a" and "program__item" in element.get("class", []):

        title = element.find("h3", class_="program__title")
        date = element.find("span", class_="program__date")

        if title and date:

            relative_link = element.get("href", "")
            full_link = BASE_URL + relative_link

            results.append({
                "month": current_month,
                "date": date.get_text(strip=True),
                "artist": title.get_text(strip=True),
                "link": full_link
            })

# Create dataframe
df = pd.DataFrame(results)

# Save CSV
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved {len(df)} events")
print(f"CSV saved to:\n{OUTPUT_FILE}")