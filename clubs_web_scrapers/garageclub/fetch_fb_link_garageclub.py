from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
import pandas as pd

# Headless Chrome
options = Options()
options.add_argument("--headless=new")
driver = webdriver.Chrome(options=options)

url = "https://www.facebook.com/GarageClubMartinov/events?locale=cs_CZ"
driver.get(url)
output_path=r'C:\Users\Spyro\Desktop\test_scrappers\garageclub\garageclub_fb_links.csv'

time.sleep(10)  # wait for JS to load events

events = []
event_elements = driver.find_elements(By.CSS_SELECTOR, "a[role='link']")
for e in event_elements:
    text = e.text
    link = e.get_attribute("href")
    if text:  # ignore empty links
        events.append({"text": text, "link": link})

driver.quit()

# Suppose your string is called 'response_str'
# If you got it from requests: response_str = response.text



# Convert to DataFrame
df = pd.DataFrame(events)

# Optional: flatten nested place info
if 'place' in df.columns:
    df['place_name'] = df['place'].apply(lambda x: x.get('name') if isinstance(x, dict) else None)
    df['city'] = df['place'].apply(lambda x: x.get('location', {}).get('city') if isinstance(x, dict) else None)
    df.drop(columns=['place'], inplace=True)


df.to_csv(output_path)
print('done')
# Preview
#print(df.head())

#print(events[:10])
