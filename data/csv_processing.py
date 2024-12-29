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
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from data.Taps.taps import tapsHandler
from data.NUMBAT.linkload import LinkLoadHandler
from tools.utils import *

class CSVProcesser():
    def __init__(self):
        self.LinkLoadHandler = LinkLoadHandler()
        self.tapsHandler = tapsHandler()

    def passenger_flow_from(self, from_station: str, direction: str, date: str) -> Dict[str, float]:
        """
        Returns the number of passengers that went from a station to another at a given time of the day
        
        This function is the most important one for this model, because it will be used to obtain the number
        of passengers on a link (by summing), so it must be simple but realistic.
        
        Here, we consider that the number of passengers exiting to_station from from_station is 
        proportional to the number of passengers exiting to_station from all different stations.
        """
        next_stations = self.LinkLoadHandler.get_inbetween_stations(direction = direction, start_station = from_station)
        # Remove from_station from the list
        next_stations = [station for station in next_stations if station != from_station]

        # We want all the stations other than from station (londoners don't make mistakes.)
        all_stations = self.LinkLoadHandler.get_all_stations()
        different_stations = [station for station in all_stations if station != from_station]
        total_output = self.tapsHandler.get_total_output(different_stations, date)

        # The entries at from_station
        inputs = self.tapsHandler.get_entries_exits(from_station, date)['entries']

        estimated_outputs = {}

        for station in next_stations:
            estimated_outputs[station] = inputs * self.tapsHandler.get_entries_exits(station, date)['exits'] / total_output
       

        return estimated_outputs
    
    def estimate_flow_between_stations(self, from_station: str, to_station: str, date: str, direction:str) -> int:
        """
        Returns the estimated link load between 2 stations at a given time of the day
        To do so, we consider every possible path a passenger could have taken, so coming from 
        a staion before from_station and going to a station after to_station

        This is very inefficient, because a lot of the calculations will be made twice or more, 
        but we don't care because the goal is to create a csv
        """

        previous_stations = self.LinkLoadHandler.get_inbetween_stations(direction, end_station = from_station)
        next_stations = self.LinkLoadHandler.get_inbetween_stations(direction, start_station = to_station)

        link_load = 0
        for start_station in previous_stations:
            #print(start_station)
            # We get the estimated outputs for each station (passengers exiting from start_station)
            estimated_outputs = self.passenger_flow_from(start_station, direction, date)
            for end_station in next_stations:
                # We sum the estimated outputs for each station (passengers exiting from start_station)
                link_load += estimated_outputs[end_station]

        return link_load
    
    def estimate_flow__line(self, date:str, direction: str) -> List[Tuple[str, str, int]]:
        """
        Returns the estimated link load between all consecutives stations for a given time of the day
        This function is quiker than just running estimate_flow_between_stations for each pair of stations
        because it uses the results of the previous calculations (the estimated outputs)

        Returns [(from_station, to_station, estimated_link_load), ...]

        """
        stations = self.LinkLoadHandler.get_all_stations()
        estimated_flows = []
        estimated_outputs = {}
        for station in stations: 

            link_load = 0
            next_stations = self.LinkLoadHandler.get_inbetween_stations(direction, start_station = station)
            # Remove station from the list
            next_stations = [s for s in next_stations if s != station]
            previous_stations = self.LinkLoadHandler.get_inbetween_stations(direction, end_station = station)
            for start_station in previous_stations:
                if start_station not in estimated_outputs:
                    estimated_outputs[start_station] = self.passenger_flow_from(start_station, direction, date)
                for end_station in next_stations:
                    link_load += estimated_outputs[start_station][end_station]
            if len(next_stations) > 0:
                estimated_flows.append((station, next_stations[0], link_load))
                print(station, next_stations[0], link_load)
            
        return estimated_flows
    
    def plot_dist_to_daily_mean(self, date:str, direction:str):
        """
        Plots the distribution of the link load between stations for a given time of the day
        compared to the daily mean
        """
        estimated_flows = self.estimate_flow__line(date, direction)
        type_of_day = get_type_of_day(get_day_of_week(date))
        errors = []
        link_data = []
        for station, next_station, link_load in estimated_flows:
            # Get the average daily link load between station and next_station
            #! need to adapt the type of day to the date ! (really easy)
            daily_mean = self.LinkLoadHandler.get_avg_daily_link_load(station, next_station, type_of_day)
            # Calculate the relative error to the average
            error = abs(link_load - daily_mean) / daily_mean * 100
            errors.append(error)
            link_data.append((station, next_station, link_load, daily_mean, error))
            print(station, next_station, link_load, daily_mean, error)
        print(link_data)
        plt.scatter(range(len(errors)), errors)
        plt.show()
