"""
Processes CSV files of 2 types 
    - The first one contains the average link load between stations for each quarter hour of the day
        over the year. It doesn't represent much because it contains averages over the year 
        We won't get far just knowing that the average between station A and B at 17:00 is 678
    - The second one contains the number of entries/exits at each station for each day of the year
        This will be used to get an idea of the 'businness' of the station that day
    Combined together, we can get an idea of the link load between stations at a given time of the day
    for a particular day of the year
"""

import pandas as pd
from typing import Dict
from data import LinkLoadHandler, tapsHandler

class CSVProcesser():
    def __init__(self):
        self.LinkLoadHandler = LinkLoadHandler()
        self.tapsHandler = tapsHandler()

    def get_passenger_count(self, from_station: str, to_station: str, direction:str, date: str) -> Dict:
        """
        Returns the number of passengers that went from a station to another at a given time of the day
        """
        outputs = self.tapsHandler.get_entries_exits(from_station, date)['exits']
        inputs = self.tapsHandler.get_entries_exits(to_station, date)['entries']
        day_of_week = self.tapsHandler.get_day_of_week(date)
        time = self.tapsHandler.get_time_of_day(time)
        return self.LinkLoadHandler.get_passenger_count(from_station, to_station, day_of_week, time)