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
from data.Taps.taps import tapsHandler
from data.NUMBAT.linkload import LinkLoadHandler

class CSVProcesser():
    def __init__(self):
        self.LinkLoadHandler = LinkLoadHandler()
        self.tapsHandler = tapsHandler()

    def get_passenger_count(self, from_station: str, to_station: str, date: str) -> Dict:
        """
        Returns the number of passengers that went from a station to another at a given time of the day

        This function is the most important one for this model, because it will be used to obtain the number
        of passengers on a link (by summing), so it must be simple but realistic.
        
        Here, we consider that the number of passengers exiting to_station from from_station is 
        proportional to the number of passengers exiting to_station from all different stations.
        """
        # The outputs in the end station
        outputs = self.tapsHandler.get_entries_exits(from_station, date)['exits']

        # The inputs in the start station
        inputs = self.tapsHandler.get_entries_exits(to_station, date)['entries']
        
        # We want all the stations other than from station (londoners don't make mistakes.)
        all_stations = self.LinkLoadHandler.get_all_stations()
        different_stations = [station for station in all_stations if station != from_station]

        output_sum = self.tapsHandler.get_outputs_sum(different_stations, date)

        estimated_outputs = inputs * outputs / output_sum

        return estimated_outputs
        
        #day_of_week = self.tapsHandler.get_day_of_week(date)
        #time = self.tapsHandler.get_time_of_day(time)
        #return self.LinkLoadHandler.get_passenger_count(from_station, to_station, day_of_week, time)

