from gemini_api import call_api
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import gspread
from google.oauth2.service_account import Credentials
import time

INPUT_FILE = "events_only.csv"
SPREADSHEET_ID = "1kbiZgtnUAIUKgrOU_NIQI1uEzF7QFPcijna0sxvhuPw"
CREDENTIALS_FILE = "dc-events-494919-1734826fd24a.json"
FIELDNAMES = ["Organization", "Event Title", "Date", "Time", "Location", "Event URL"]
MAX_WORKERS = 100
MAX_ORGS = None

def fetch_events(org, retries=3, backoff=2):
    name = org["Organization Name"]
    url = org["Events URL"]
    for attempt in range(retries):
        try:
            rows = call_api(url) # the API call is in a retry loop in case of 503 error - high demand
            print(f"{name}: {len(rows)} events")
            return rows
        except Exception as e:
            if attempt < retries - 1:
                wait = backoff ** attempt
                time.sleep(wait)
            else:
                return []

def update_google_sheet(rows):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # all google authentication to open spreadsheet by ID and write events too 
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

if __name__ == "__main__":
    with open(INPUT_FILE, newline="", encoding="utf-8") as f:
        orgs = list(csv.DictReader(f))

    if MAX_ORGS is not None:
        orgs = orgs[:MAX_ORGS]

    all_rows = []
    # each organization is scheduled to be scraped, up to 100
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_events, org): org for org in orgs}
        for future in as_completed(futures):
            all_rows.extend(future.result())

    # Sort by date 
    all_rows.sort(key=lambda x: x.get("Date", ""))
    # Update spreadsheet 
    update_google_sheet(all_rows)