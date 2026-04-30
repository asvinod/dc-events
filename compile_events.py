from gemini_api import call_api
import csv
import io
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "events_only.csv"
OUTPUT_FILE = "all_events.csv"
FIELDNAMES = ["Organization", "Event Title", "Date", "Time", "Location", "Event URL"]
MAX_WORKERS = 70
MAX_ORGS = None

def fetch_events(org):
    name = org["Organization Name"]
    url = org["Events URL"]
    try:
        csv_output = call_api(url)
        reader = csv.DictReader(io.StringIO(csv_output))
        rows = list(reader)
        print(f"✓ {name}: {len(rows)} events")
        return rows
    except Exception as e:
        print(f"✗ {name}: Failed — {e}")
        return []

# Load orgs
with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    orgs = list(csv.DictReader(f))

if MAX_ORGS is not None:
    orgs = orgs[2]

# Fetch in parallel
all_rows = []
with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(fetch_events, org): org for org in orgs}
    for future in as_completed(futures):
        all_rows.extend(future.result())

# Write output
with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nDone! {len(all_rows)} total events saved to {OUTPUT_FILE}")