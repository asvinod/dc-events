from google import genai
import os
from dotenv import load_dotenv
from scrape_contents import scrape_page, clean_html
from datetime import datetime
import re 

def call_api(url):
    today = datetime.now().strftime("%Y-%m-%d")
    load_dotenv()

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

    html = clean_html(scrape_page(url, headless=True))

    prompt = f"""
    Extract event information from the following webpage content.
    Return ONLY valid CSV with this exact header:
    Organization,Event Title,Date,Time,Location,Event URL

    Rules:
    - Do NOT include explanations or extra text
    - If a field is missing, leave it blank
    - Normalize dates to YYYY-MM-DD if possible
    - Keep time as written if unclear
    - ONLY include events with a date on or after {today}
    - Exclude past events
    - For Event URL: extract the href from the event's anchor tag.
    If it's a relative path (starts with /), prepend the base URL: {url}
    If no URL is found, leave blank.

    Source URL: {url}
    Content:
    \"\"\"
    {html}
    \"\"\"
    """

    resp = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    csv_output = resp.text.strip()
    if csv_output.startswith("```"):
        csv_output = re.sub(r"^```[a-z]*\n?", "", csv_output)
        csv_output = re.sub(r"\n?```$", "", csv_output)
    return csv_output