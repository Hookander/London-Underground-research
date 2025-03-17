from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from typing import Optional, Dict

class FootballData:
    def __init__(self):
        self.LONDON_TEAMS = [
    "Arsenal",
    "Chelsea",
    "Tottenham",
    "West Ham",
    "Crystal Palace",
    "Fulham",
    "Brentford",
    "Queens Park Rangers",
    "Millwall",
    "Charlton Athletic",
    "AFC Wimbledon",
    "Leyton Orient",
    "Sutton United",
    "Barnet",
    "Dagenham & Redbridge",
    "Bromley",
    "Wealdstone",
    "Dulwich Hamlet",
    "Welling United",
    "Hampton & Richmond Borough",
    "Wingate & Finchley"
]
        self.stadiums = {
            "Arsenal": {"stadium": "Emirates Stadium", "latitude": 51.554867, "longitude": -0.109112},
            "Chelsea": {"stadium": "Stamford Bridge", "latitude": 51.47285, "longitude": -0.1935},
            "Tottenham": {"stadium": "Tottenham Hotspur Stadium", "latitude": 51.6043, "longitude": -0.0665},
            "West Ham": {"stadium": "London Stadium", "latitude": 51.538611, "longitude": -0.016389},
            "Crystal Palace": {"stadium": "Selhurst Park", "latitude": 51.3983, "longitude": -0.0855},
            "Fulham": {"stadium": "Craven Cottage", "latitude": 51.4749, "longitude": -0.2216},
            "Brentford": {"stadium": "Gtech Community Stadium", "latitude": 51.4907, "longitude": -0.2886},
            "Queens Park Rangers": {"stadium": "Kiyan Prince Foundation Stadium", "latitude": 51.5091, "longitude": -0.2321},
            "Millwall": {"stadium": "The Den", "latitude": 51.4854, "longitude": -0.0501},
            "Charlton Athletic": {"stadium": "The Valley", "latitude": 51.486, "longitude": 0.0365},
            "AFC Wimbledon": {"stadium": "Plough Lane", "latitude": 51.4319, "longitude": -0.1874},
            "Leyton Orient": {"stadium": "Brisbane Road", "latitude": 51.5606, "longitude": -0.0126},
            "Sutton United": {"stadium": "Gander Green Lane", "latitude": 51.3613, "longitude": -0.2035},
            "Barnet": {"stadium": "The Hive Stadium", "latitude": 51.6, "longitude": -0.2969},
            "Dagenham & Redbridge": {"stadium": "Victoria Road", "latitude": 51.5531, "longitude": 0.1555},
            "Bromley": {"stadium": "Hayes Lane", "latitude": 51.3903, "longitude": 0.0202},
            "Wealdstone": {"stadium": "Grosvenor Vale", "latitude": 51.5683, "longitude": -0.3559},
            "Dulwich Hamlet": {"stadium": "Champion Hill", "latitude": 51.453, "longitude": -0.0849},
            "Welling United": {"stadium": "Park View Road", "latitude": 51.4564, "longitude": 0.1054},
            "Hampton & Richmond Borough": {"stadium": "The Beveree Stadium", "latitude": 51.4213, "longitude": -0.3617},
            "Wingate & Finchley": {"stadium": "The Maurice Rebak Stadium", "latitude": 51.5994, "longitude": -0.1924}
        }
        try:
            self.full_df = pd.read_csv('data/football/premier_league_london_matches.csv')
        except:
            print("File not found, creating new CSV")
            self.clean_csvs()
            self.full_df = pd.read_csv('data/football/premier_league_london_matches.csv')
        self.pl_teams = self.full_df['HomeTeam'].unique()
        self.taps = tapsHandler()
        self.llh = LinkLoadHandler()

    
    def get_closest_team(self, station: str) -> Dict[str, Optional[float]]:
        """
        Returns the closest London team to a given London Underground station (Central Line)
        """
        station_lat, station_lon = station_coordinates(station)
        distances = {}
        for team in self.pl_teams:
            team_lat = self.stadiums[team]['latitude']
            team_lon = self.stadiums[team]['longitude']
            distance = haversine(station_lat, station_lon, team_lat, team_lon)
            distances[team] = round(distance, 3)
        return min(distances, key=distances.get), distances[min(distances, key=distances.get)]

    def get_match_influence(self, station: str, start_date: str, end_date: str) -> Dict[str, int]:
        """
        Returns the avg entries/exits at a given station on match days and non-match days for a given date range
        """
        closest_team, distance = self.get_closest_team(station)

        self.full_df['Date'] = pd.to_datetime(self.full_df['Date'], format='%d/%m/%Y')
        match_days = self.full_df[(self.full_df['Date'] >= start_date) & (self.full_df['Date'] <= end_date)]
        match_days = match_days[match_days['HomeTeam'] == closest_team]
        match_days = match_days['Date'].dt.strftime('%d/%m/%Y').tolist()

        full_dates = get_dates_between(start_date, end_date)
        non_match_days = [date for date in full_dates if date not in match_days]
        print(len(match_days), len(non_match_days))

        entries_avg = {'match': 0, 'non_match': 0}
        exits_avg = {'match': 0, 'non_match': 0}
        got_data = 0
        if len(non_match_days) > 0:
            for date in non_match_days:
                avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
                if not_missing:
                    entries_avg['non_match'] += avg['entries']
                    exits_avg['non_match'] += avg['exits']
                    got_data += 1
            if got_data > 0:
                entries_avg['non_match'] /= got_data
                exits_avg['non_match'] /= got_data

        got_data = 0
        if len(match_days) > 0:
            for date in match_days:
                avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
                if not_missing:
                    entries_avg['match'] += avg['entries']
                    exits_avg['match'] += avg['exits']
                    got_data += 1
            if got_data > 0:
                entries_avg['match'] /= got_data
                exits_avg['match'] /= got_data

        return entries_avg, exits_avg
    
    def get_closest_station(self, stadium = None, team = None) -> Tuple[str, float]:
        """
        Returns the closest London Underground station (Central Line) to a given stadium (or stadium of a given team)
        """
        if team is None:
            team = [key for key, value in self.stadiums.items() if value['stadium'] == stadium][0]
        lat = self.stadiums[team]['latitude']
        lon = self.stadiums[team]['longitude']
        stations = get_all_stations()
        distances = {}
        for station in stations:
            station_lat, station_lon = station_coordinates(station)
            distance = haversine(lat, lon, station_lat, station_lon)
            distances[station] = distance
        return min(distances, key=distances.get), round(distances[min(distances, key=distances.get)], 3)
        
    def plot_match_influence(self, start_date: str, end_date: str):
        """
            Plots the % augmentation of entries/exits on match days compared to non-match days
            with respect to the distance to the closest station
        """
        distances = {}
        for team in self.pl_teams:
            station, distance = self.get_closest_station(team=team)
            entries_avg, exits_avg = self.get_match_influence(station, start_date, end_date)
            entries_diff = (entries_avg['match'] - entries_avg['non_match']) / entries_avg['non_match'] * 100
            exits_diff = (exits_avg['match'] - exits_avg['non_match']) / exits_avg['non_match'] * 100
            distances[team] = {'distance': distance, 'entries_diff': entries_diff, 'exits_diff': exits_diff}
        distances = pd.DataFrame(distances).T
        distances = distances.sort_values(by='distance')
        plt.figure(figsize=(10, 5))
        plt.plot(distances['distance'], distances['entries_diff'], label='Entries')
        plt.plot(distances['distance'], distances['exits_diff'], label='Exits')
        plt.xlabel('Distance to the closest station (km)')
        plt.ylabel('% Augmentation')
        plt.title('Match Influence on Entries/Exits of the closest station')
        plt.legend()
        plt.show()

    def clean_csvs(self):
        """
        Processes CSV files containing football match data for London teams in the Premier League.
        """
        seasons = ['2015-16', '2016-17', '2017-18', '2018-19', '2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
        full_df = pd.DataFrame(columns = ['Date', 'HomeTeam', 'AwayTeam', 'Stadium', 'Latitude', 'Longitude'])
        for season in seasons:
            df = pd.read_csv(f'data/football/{season}.csv')
            filtered_df = df[df['HomeTeam'].isin(self.LONDON_TEAMS)]
            filtered_df = filtered_df.copy()
            filtered_df['Stadium'] = filtered_df['HomeTeam'].apply(lambda x: self.stadiums[x]['stadium'])
            filtered_df['Latitude'] = filtered_df['HomeTeam'].apply(lambda x: self.stadiums[x]['latitude'])
            filtered_df['Longitude'] = filtered_df['HomeTeam'].apply(lambda x: self.stadiums[x]['longitude'])
            filtered_df = filtered_df[['Date', 'HomeTeam', 'AwayTeam', 'Stadium', 'Latitude', 'Longitude']]
            # Correct the Date that is sometimes in the format 'dd/mm/yyyy' or 'dd/mm/yy'
            filtered_df['Date'] = filtered_df['Date'].apply(lambda x: x if len(x) == 10 else x[:-2] + '20' + x[-2:])
            full_df = pd.concat([full_df, filtered_df], ignore_index=True)

        full_df.to_csv('data/football/premier_league_london_matches.csv', index=False)

