from gemini_api import call_api
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import gspread
from google.oauth2.service_account import Credentials

INPUT_FILE = "events_only.csv"
SPREADSHEET_ID = "1kbiZgtnUAIUKgrOU_NIQI1uEzF7QFPcijna0sxvhuPw"
CREDENTIALS_FILE = "dc-events-494919-1734826fd24a.json"
FIELDNAMES = ["Organization", "Event Title", "Date", "Time", "Location", "Event URL"]
MAX_WORKERS = 25
MAX_ORGS = None

def fetch_events(org):
    name = org["Organization Name"]
    url = org["Events URL"]
    try:
        rows = call_api(url)
        print(f"✓ {name}: {len(rows)} events")
        return rows
    except Exception as e:
        print(f"✗ {name}: Failed — {e}")
        return []

def update_google_sheet(rows):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    sheet.clear()
    sheet.append_row(FIELDNAMES)
    if rows:
        sheet.append_rows([
            [row.get(field, "") for field in FIELDNAMES]
            for row in rows
        ])
    print(f"Updated Google Sheet with {len(rows)} events!")

# Load orgs
with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    orgs = list(csv.DictReader(f))

if MAX_ORGS is not None:
    orgs = orgs[:MAX_ORGS]

# Fetch in parallel
all_rows = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(fetch_events, org): org for org in orgs}
    for future in as_completed(futures):
        all_rows.extend(future.result())

all_rows.sort(key=lambda x: x.get("Date", ""))
# Push to Google Sheets
update_google_sheet(all_rows)

# Also save locally
with open("all_events.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nDone! {len(all_rows)} total events.")