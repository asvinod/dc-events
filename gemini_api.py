from google import genai
import os
from dotenv import load_dotenv
from scrape_contents import scrape_page, clean_html
from datetime import datetime
import re
import json

def call_api(url):
    today = datetime.now().strftime("%Y-%m-%d")
    load_dotenv()
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    html = clean_html(scrape_page(url, headless=True))
    prompt = f"""
    Extract event information from the following webpage content.
    Return ONLY a valid JSON array of objects with these exact keys:
    Organization, Event Title, Date, Time, Location, Event URL

    Rules:
    - Do NOT include explanations or extra text, only the JSON array
    - If a field is missing, use an empty string ""
    - Normalize dates to YYYY-MM-DD format
    - Keep time as written if unclear
    - ONLY include events where the date is strictly on or after {today}
    - If the date is before {today}, do NOT include it — today is {today}
    - Exclude past events entirely, even if they seem recent
    - For Event URL: extract the href from the event's anchor tag.
      If it's a relative path (starts with /), prepend the base URL: {url}
      If no URL is found, use an empty string ""
    Source URL: {url}
    Content:
    \"\"\"{html}\"\"\"
    """
    resp = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=prompt
    )
    text = resp.text.strip()
    text = re.sub(r"^```[a-z]*\n?", "", text)
    text = re.sub(r"\n?```$", "", text)

    events = json.loads(text)

    # Double-check dates in Python as a safety net
    today_dt = datetime.now().date()
    rows = []
    for event in events:
        date_str = event.get("Date", "")
        try:
            event_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            if event_date < today_dt:
                continue
        except ValueError:
            pass  # If date can't be parsed, include it anyway
        rows.append({
            "Organization": event.get("Organization", ""),
            "Event Title": event.get("Event Title", ""),
            "Date": date_str,
            "Time": event.get("Time", ""),
            "Location": event.get("Location", ""),
            "Event URL": event.get("Event URL", "")
        })
    return rows