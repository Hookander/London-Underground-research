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
import time

class CSVProcesser():
    def __init__(self):
        self.LinkLoadHandler = LinkLoadHandler()
        self.tapsHandler = tapsHandler()


    def passenger_flow_from(self, from_station: str, direction: str, date: str) -> Dict[str, float]:
        """
        Returns the number of passengers that went from a station to another on a gievn day
        
        This function is the most important one for this model, because it will be used to obtain the number
        of passengers on a link (by summing), so it must be simple but realistic.
        
        Here, we consider that the number of passengers exiting to_station from from_station is 
        proportional to the number of passengers exiting to_station from all different stations.
        """
        
        next_stations = self.LinkLoadHandler.get_inbetween_stations(direction = direction, start_station = from_station)
        # Remove from_station from the list
        next_stations = [station for station in next_stations if station != from_station]

        # We want all the stations other than from station (londoners don't make mistakes.)
        total_output = self.total_outputs - self.tapsHandler.get_entries_exits(from_station, date)['exits']

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
         + we can use the results of the previous calculations (the estimated outputs)
         #! -------
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
            
    
    def flow_time_day(self, start_station, end_station, direction, date, quarter_hour):
        """
        Returns the estimated link load between 2 stations for a given quarter of the day
        To do that :
            We have the link load for each quarter of the day, averaged across the year.
            Thanks the to to the taps_handler, we have an approximation of the total load between 2 stations that
            day (using the model in passenger_flow_from)
            To combine the 2, we just need to multiply the total link load of the day 
            by the proportion of the quarter of the day in the total day
        """
        begin = time.time()
        day_of_week = get_day_of_week(date)
        type_of_day = get_type_of_day(day_of_week)
        linkload_day = self.estimate_flow_between_stations(start_station, end_station, date, direction)
        print(f"Time to get link load between stations: {time.time() - begin}")
        linkload_quarter = self.LinkLoadHandler.get_avg_link_load(start_station, end_station, quarter_hour, type_of_day)
        print(f"Time to get link load for the quarter of the day: {time.time() - begin}")
        total_linkload = self.LinkLoadHandler.get_avg_daily_link_load(start_station, end_station, type_of_day)
        print(f"Time to get total link load for the day: {time.time() - begin}")

        proportion = linkload_quarter / total_linkload

        return linkload_day * proportion


    def estimate_flow__line(self, date:str, direction: str) -> List[Tuple[str, str, int]]:
        """
        Returns the estimated link load between all consecutives stations for a given day
        This function is quiker than just running estimate_flow_between_stations for each pair of stations
        because it uses the results of the previous calculations (the estimated outputs)

        Returns [(from_station, to_station, estimated_link_load), ...]

        """
        stations = self.LinkLoadHandler.get_all_stations()

        # Calculate it here to pass it to the passenger_flow_from function
        # This way, we don't have to run the same calculation multiple times (access to a df is slow)
        self.total_outputs = self.tapsHandler.get_total_output(stations, date)
        estimated_flows = []
        estimated_outputs = {}
        for station in stations: 

            # get the stricly next stations (we'll use those for the farther stations, rather than the current station,
            # because otherwise the stations in a other branch might be considered as next stations, but we don't want that)
            # For example, with this, we won't consider Wanstead, ... when we are at Leytonstone going to Snaresbrook

            next_consecutive_stations = self.LinkLoadHandler.get_next_consecutive_stations(station, direction)
            #print(station, next_consecutive_stations)
            for next_consecutive in next_consecutive_stations:

                link_load = 0

                next_stations = self.LinkLoadHandler.get_inbetween_stations(direction, start_station = next_consecutive)

                previous_stations = self.LinkLoadHandler.get_inbetween_stations(direction, end_station = station)

                for start_station in previous_stations:
                    if start_station not in estimated_outputs:
                        estimated_outputs[start_station] = self.passenger_flow_from(start_station, direction, date)
                    for end_station in next_stations:
                        link_load += estimated_outputs[start_station][end_station]

                estimated_flows.append((station, next_consecutive, link_load))
            
        return estimated_flows
    
    def flow_time_day_csv(self, date:str) -> pd.DataFrame:
        """
        Creates a csv file containing the estimated link load between stations for a given day and quater_hour
        """
        begin = time.time()

        # Reset it to clear the cache
        self.tapsHandler = tapsHandler()

        directions = ['EB', 'WB'] #! for now to test
        df = pd.DataFrame(columns=['date', 'quarterhour', 'from_station', 'to_station', 'direction', 'link_load'])
        quater_hours = [f'{h:02d}{m:02d}' for h in range(24) for m in range(0, 60, 15)]
        for direction in directions:
            day_link_load_distribution = self.estimate_flow__line(date, direction)
            for start_station, end_station, day_link_load in day_link_load_distribution:
                total_linkload = self.LinkLoadHandler.get_avg_daily_link_load(start_station, end_station, get_type_of_day(get_day_of_week(date)))
                for quater_hour in quater_hours:
                    quarter_link_load = self.LinkLoadHandler.get_avg_link_load(start_station, end_station, quater_hour, get_type_of_day(get_day_of_week(date)))
                    proportion = quarter_link_load / total_linkload
                    link_load = day_link_load * proportion
                    df = df._append({'date': date, 'quarterhour': quater_hour, 'from_station': start_station, 'to_station': end_station, 'direction': direction, 'link_load': link_load}, ignore_index=True)

        print(f"Time to create the csv at date {date}: {time.time() - begin}")
        return df
    
    def creates_flow_time_day_csv_all(self, start_date:str, end_date:str, path) -> None:
        """
        Creates csv files containing the estimated link load between stations for a given day and quater_hour
        for all days between start_date and end_date
        """
        begin = time.time()
        dates = get_dates_between(start_date, end_date)
        full_df = pd.DataFrame(columns=['date', 'quarterhour', 'from_station', 'to_station', 'direction', 'link_load'])
        for date in dates:
            df = self.flow_time_day_csv(date)
            full_df = pd.concat([full_df, df], ignore_index=True)
            print(f"Done with {date}, {time.time() - begin}")
            full_df.to_csv(path, index=False)
        
    def get_linkload_error_to_daily_mean(self, date:str, direction:str) -> Dict[Tuple[str, str], float]:
        """
        Returns the error (in %) between : 
            - the estimated link load between stations for a given day (see estimate_flow__line), this is the model
            - the average daily link load between stations, obtained by summing over all the quarter hours of the day, 
                there is no model here, it is the real data
        
        Returns {(from_station, to_station) : error, ...}
        """
        estimated_flows = self.estimate_flow__line(date, direction)
        type_of_day = get_type_of_day(get_day_of_week(date))
        errors = {}
        for station, next_station, link_load in estimated_flows:
            # Get the average daily link load between station and next_station
            #! need to adapt the type of day to the date ! (really easy)
            daily_mean = self.LinkLoadHandler.get_avg_daily_link_load(station, next_station, type_of_day)
            # Calculate the relative error to the average
            error = abs(link_load - daily_mean) / daily_mean * 100
            errors[(station, next_station)] = error
        return errors

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
    

