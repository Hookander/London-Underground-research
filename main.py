from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
from events import WeatherHandler
import time
import requests

print("Starting...")

#wh = WeatherHandler()
#wh.plot_diff_rainy_days('01/01/2019', '31/01/2019', test=True)
#print(wh.station_weather_influence('Queensway', '01/01/2019', '31/12/2019'))
#print(wh.get_best_threshold('Queensway', '01/01/2019', '31/12/2019'))
#wh.plot_best_thresholds('01/01/2019', '31/12/2019')
#wh.plot_threshold_influence('Queensway', '01/01/2019', '31/12/2019')
#wh.plot_best_thresholds('01/01/2019', '31/12/2019', test=True)

# Replace with your actual Ticketmaster API Key
with open('data/api_ticketmaster.txt') as f:
    API_KEY = f.read().strip()

from datetime import datetime, timedelta

# Define search parameters
CITY = "London"
YEAR = 2024
MONTH = 4  # March

# Calculate start and end dates
start_date = datetime(YEAR, MONTH, 1).strftime("%Y-%m-%dT00:00:00Z")
end_date = (datetime(YEAR, MONTH + 1, 1) - timedelta(days=1)).strftime("%Y-%m-%dT23:59:59Z")

# Ticketmaster API endpoint
url = "https://app.ticketmaster.com/discovery/v2/events.json"

# API request parameters
params = {
    "apikey": API_KEY,
    "city": CITY,
    "size": 2,  # Maximum per page
    "page": 0    # Start from first page
}

# Fetch data
all_events = []
while True:
    response = requests.get(url, params=params)
    print(response.json())
    break
    if response.status_code == 200:
        data = response.json()
        events = data.get("_embedded", {}).get("events", [])
        
        if not events:
            break  # No more events to fetch
        
        all_events.extend(events)
        params["page"] += 1  # Move to the next page
        
        # Stop if there are no more pages
        if params["page"] >= data["page"]["totalPages"]:
            break
    else:
        print(f"Error: {response.status_code}, {response.text}")
        break

# Display results
if all_events:
    print(f"🎟️ Events in {CITY} for {datetime(YEAR, MONTH, 1).strftime('%B %Y')}:\n")
    for event in all_events:
        name = event["name"]
        venue = event["_embedded"]["venues"][0]["name"]
        event_date = event["dates"]["start"]["localDate"]
        print(f"- {name} at {venue} ({event_date})")
else:
    print(f"No events found in {CITY} for {datetime(YEAR, MONTH, 1).strftime('%B %Y')} 😞")
