import requests
from bs4 import BeautifulSoup

url = "https://mei.edu/events/"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')
list_events = soup.find_all('div', class_="card-holder__inner pattern__inner")
events = list_events[0].find_all("article", class_="event-card")
for e in events:
    name_tag = e.find("span", class_="screen-reader-only")
    name = name_tag.get_text(strip=True) if name_tag else None

    date_tag = e.find("p", class_="meta-list__item--event-date")
    date = date_tag.get_text(strip=True) if date_tag else None

    loc_tag = e.find("p", class_="meta-list__item--location")
    location = loc_tag.get_text(strip=True) if loc_tag else None

    time_tag = e.find("p", class_="meta-list__item--time")
    time = time_tag.get_text(strip=True) if time_tag else None

    print(name)
    print(date)
    print(location)
    print(time)
    print()