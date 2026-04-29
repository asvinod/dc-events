from gemini_api import call_api
import csv
import io
import time

INPUT_FILE = "events_only.csv"
OUTPUT_FILE = "all_events.csv"

FIELDNAMES = ["Organization", "Event Title", "Date", "Time", "Location", "Event URL"]

all_rows = []

with open(INPUT_FILE, newline="", encoding="utf-8") as f:
    orgs = list(csv.DictReader(f))

num_orgs = 5
for org in orgs:
    name = org["Organization Name"]
    url = org["Events URL"]
    print(f"Fetching: {name}...", end=" ", flush=True)
    try:
        csv_output = call_api(url)
        reader = csv.DictReader(io.StringIO(csv_output))
        rows = list(reader)
        all_rows.extend(rows)
        print(f"{len(rows)} events")
    except Exception as e:
        print(f"Failed: {e}")
    time.sleep(1)
    if num_orgs == 0:
        break
    else:
        num_orgs-=1

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\nDone! {len(all_rows)} total events saved to {OUTPUT_FILE}")