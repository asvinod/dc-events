from gemini_api import call_api

csv_output = call_api("http://carnegieendowment.org/events")
print(csv_output)