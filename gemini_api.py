from google import genai
import os
from dotenv import load_dotenv
from scrape_contents import scrape_page, prune_to_markdown
from datetime import datetime

today = datetime.now().strftime("%Y-%m-%d")
load_dotenv()

url = "https://carnegieendowment.org/events"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

html = scrape_page(url, headless=True)
cleaned_markdown = prune_to_markdown(html)

prompt = f"""
Extract event information from the following webpage content.

Return ONLY valid CSV with this exact header:
Organization,Event Title,Date,Time,Location

Rules:
- Do NOT include explanations or extra text
- If a field is missing, leave it blank
- Normalize dates to YYYY-MM-DD if possible
- Keep time as written if unclear
- ONLY include events with a date on or after {today}
- Exclude past events

Source URL: {url}

Content:
\"\"\"
{cleaned_markdown}
\"\"\"
"""

resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

csv_output = resp.text
print(csv_output)
with open("events.csv", "w", encoding="utf-8") as f:
    f.write(csv_output)