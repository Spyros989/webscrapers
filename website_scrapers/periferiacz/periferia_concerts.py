import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

url="https://www.periferia.cz/koncerty/"
page = requests.get(url)
page.encoding = 'utf-8'  # Force UTF-8 encoding for proper decoding


# Check if connection was successful
if page.status_code != 200:
        print("Connection failed")
else:
# Parse the page with BeautifulSoup
        soup = BeautifulSoup(page.content, "lxml")
product_containers = soup.find_all('tr', class_='d-flex')

event_date = []
event_name=[]
event_location=[]
event_url=[]

for product in product_containers:
    date = product.find('td', class_='col-2').get_text(strip=True)
    name = product.find('td', class_='col-7').get_text(strip=True)
    location = product.find('td', class_='col-3').get_text(strip=True)
    url = product.find('td', class_='col-3').find('a')['href']

    event_date.append(date)
    event_name.append(name)
    event_location.append(location)
    event_url.append(url)

    df=pd.DataFrame({
        'event_date': event_date,
        'event_name': event_name,
        'event_location': event_location,
        'event_url': event_url,
        'extraction_datetime': datetime.now().strftime("%Y-%m-%d_%H%M%S")
    })
    #df.to_csv(r"C:\Users\Spyro\Desktop\Ubuntu_server\periferia_draft.csv", index=False, encoding='utf-8-sig')
temp = df['event_location'].str.split('-', n=1, expand=True)
df['city'] = temp[0].str.strip()
df['club_name'] = temp[1].str.split('Více informací', n=1).str[0].str.strip()
df['event_date'] = pd.to_datetime(df['event_date'], format='%d.%m.%Y').dt.strftime('%Y-%m-%d')
df = df.drop(columns=["event_location"])
column_order = [
    'club_name',
    'event_url',
    'event_name',
    'event_date',
    'city',
    'extraction_datetime'
]
df = df[column_order]
print(df)
#print("it is done!")
