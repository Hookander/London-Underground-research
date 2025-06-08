import requests
from math import radians, sin, cos, sqrt, atan2
from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
from events import WeatherHandler
import time
import requests


class TickemasterHandler():
    def __init__(self):
        with open('data/api_ticketmaster.txt') as f:
            self.API_KEY = f.read().strip()

    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Calculate the great-circle distance between two points 
        on the Earth (in kilometers)
        """
        R = 6371  # Earth radius in kilometers
        dLat = radians(lat2 - lat1)
        dLon = radians(lon2 - lon1)
        a = (sin(dLat/2) ** 2 +
            cos(radians(lat1)) * cos(radians(lat2)) *
            sin(dLon/2) ** 2)
        return R * 2 * atan2(sqrt(a), sqrt(1-a))

    def get_events_near_station(self, station_name, radius_km, start_date, end_date, max_results=200):
        """
        Get events near a Central Line station with distance and event details
        
        Args:
            api_key (str): Ticketmaster API key
            station_name (str): Name of Central Line station
            radius_km (int): Search radius in kilometers
            date (str): Date in YYYY-MM-DD format
            max_results (int): Max events to return (1-200)
        
        Returns:
            list: List of event dictionaries with details
        """
        # Get station coordinates
        station_coords = station_coordinates(station_name)
        if not station_coords:
            raise ValueError(f"Station '{station_name}' not found in Central Line database")
        

        url = "https://app.ticketmaster.com/discovery/v2/events.json"
        params = {
            "apikey": self.API_KEY,
            "latlong": f"{station_coords[0]},{station_coords[1]}",
            "radius": radius_km,
            "unit": "km",
            "startDateTime": f"{start_date}T00:00:00Z",
            "endDateTime": f"{end_date}T23:59:59Z",
            "size": min(max_results, 200),
            "sort": "date,asc"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            events = data.get("_embedded", {}).get("events", [])
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            return []
        print(len(events), "events found")
        processed_events = []
        for event in events:
            try:
                # venue coordinates
                venue = event.get("_embedded", {}).get("venues", [{}])[0]
                venue_lat = float(venue.get("location", {}).get("latitude", 0))
                venue_lon = float(venue.get("location", {}).get("longitude", 0))
                
                # distance
                distance_km = haversine(
                    station_coords[0], station_coords[1],
                    venue_lat, venue_lon
                ) if venue_lat and venue_lon else None
                
                # event details
                processed_event = {
                    "name": event.get("name"),
                    "url": event.get("url"),
                    "date": event.get("dates", {}).get("start", {}).get("localDate"),
                    "time": event.get("dates", {}).get("start", {}).get("localTime"),
                    "event_type": {
                        "main": event.get('classifications', [{}])[0].get('segment', {}).get('name', 'Event'),
                        "genre": event.get('classifications', [{}])[0].get('genre', {}).get('name', ''),
                        "subtype": event.get('classifications', [{}])[0].get('subGenre', {}).get('name', '')
                    },
                    "venue": {
                        "name": venue.get("name"),
                        "address": venue.get("address", {}).get("line1"),
                        "city": venue.get("city", {}).get("name"),
                        "location": (venue_lat, venue_lon)
                    },
                    "distance_km": round(distance_km, 2) if distance_km else None,
                    "ticket_info": {
                        "price_min": event.get("priceRanges", [{}])[0].get("min"),
                        "price_max": event.get("priceRanges", [{}])[0].get("max")
                    },
                    "attendance": event.get("promoter", {}).get("name")  # Proxy for size
                }
                processed_events.append(processed_event)
                
            except Exception as e:
                print(f"Error processing event: {e}")
                continue
        
        return processed_events

