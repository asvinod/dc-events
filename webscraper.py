import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

url = "https://www.csis.org/events"
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

title_tags = soup.find_all(
    ["h1", "h2", "h3", "h4"],
    class_=re.compile(r"(event.*title|title|headline)", re.I)
)
#print(title_tags)
# fallback: no class matches
if not title_tags:
    containers = soup.find_all("div", class_=re.compile(r"(event|listing|item|card)", re.I))
    for c in containers:
        h_tag = c.find(["h2","h3","h4"])
        if h_tag and h_tag not in title_tags:
            title_tags.append(h_tag)

# fallback: completely ignore class names
if not title_tags:
    for h in soup.find_all(["h2","h3","h4"]):
        # check if next sibling contains a month (likely a date)
        next_text = h.find_next(string=True)
        if next_text and re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)", next_text, re.I):
            title_tags.append(h)
seen = set()
blacklist = [
    "Upcoming Events", "Events", "Follow us", "Get Notified",
    "Event Series", "Virtual Briefing Series", "Past Events", "Filter by"
]

for t in title_tags:
    title = t.get_text(strip=True)
    if not title or title in seen or title in blacklist:
        continue
    seen.add(title)

    container = t.find_parent("div")

    date_tag = container.find(class_=re.compile("date", re.I))
    time_tag = container.find(class_=re.compile("time", re.I))
    location_tag = container.find(class_=re.compile("location|venue", re.I))
    time = None
    location = None
    date = date_tag.get_text(strip=True) if date_tag else None

    # Skip entries with no date
    if date is None:
        continue

    if date:
        # --- Extract time ---
        time_match = re.search(r'\b\d{1,2}(:\d{2})?\s?(AM|PM|am|pm)(\s?[A-Z]{1,3})?\b', date)
        if time_match:
            time = time_match.group().strip()

        # --- Extract date ---
        date_match = re.search(
            r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)?\,?\s*'
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)'
            r'\s+\d{1,2},\s+\d{4}',
            date,
            re.I
        )

        if date_match:
            date = date_match.group().strip()
            date = date.lstrip(", ").strip()
        else:
            date = None

    if time_tag:    
        time = time_tag.get_text(strip=True)
    else:
        if date:
            # Look for time patterns like "10:00 am", "8 PM", etc.
            match = re.search(r'\b\d{1,2}(:\d{2})?\s?(AM|PM|am|pm)\b', date)
            if match:
                time = match.group().strip()
                date = date.replace(time, "").strip()
                # Clean leftover separators
                date = re.sub(r'[•\-–|]+$', '', date).strip()
                date = re.sub(r'^[•\-–|]+', '', date).strip()

    if location_tag:
        location = location_tag.get_text(strip=True)
    else:
        link_tag = container.find("a", href=True)
        if link_tag:
            event_url = urljoin(url, link_tag["href"])
            try:
                event_res = requests.get(event_url, headers=headers)
                event_soup = BeautifulSoup(event_res.text, "html.parser")
                full_text = event_soup.get_text(" ", strip=True)

                # Detect virtual
                if re.search(r'\b(virtual|online)\b', full_text, re.I):
                    location = "Virtual Event"

                if not location:
                    loc_tag = event_soup.find(class_=re.compile("location|venue", re.I))
                    if loc_tag:
                        location = loc_tag.get_text(strip=True)

            except Exception:
                location = None

    print("Title:", title)
    print("Date:", date)
    print("Time:", time)
    print("Location:", location)
    print("-" * 40)