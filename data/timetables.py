import pandas as pd
from typing import Tuple, List
import matplotlib.pyplot as plt
from sklearn.neighbors import KernelDensity
import numpy as np
from tools import *


class TimetablesHandler():
    def __init__(self):
        self.actual_timetable = pd.read_csv('./data/scraped_timetables.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
        self.ideal_timetable = pd.read_csv('./data/ideal_timetable.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
        

    def get_times(self, arg_dict):
        """
            Returns the times for the given arguments
        """
        filtered_df = self.scraped_timetable
        for key, value in arg_dict.items():
            filtered_df = filtered_df[filtered_df[key] == value]
        # Sort the results by timestamp
        filtered_df = filtered_df.sort_values(by=['arrival_year', 'arrival_month', 'arrival_day', 'arrival_hour', 'arrival_min', 'arrival_sec'])
        return filtered_df[['vehicleId', 'direction', 'stationName', 'arrival_hour', 'arrival_min', 'arrival_sec']]

    def get_closest_train(self, time: Tuple[int, int, int], station_name:str, direction:str, type_of_day:str):
        """
            Returns the closest ideal arrival time to the given time for the given station, direction, type_of_day.
            It will be useful to calculate delays

            time : [h, m, s]
        """

        # Match the station and direction
        filtered_df = self.ideal_timetable[(self.ideal_timetable['station_name'] == station_name) 
                                           & (self.ideal_timetable['direction'] == direction)
                                           & (self.ideal_timetable['Type_of_day'] == type_of_day)]
        
        assert len(filtered_df) > 0, "No ideal timetable found for the given arguments"
        
        # Sort the results by distance to the given time (convert to seconds)
        filtered_df = filtered_df.copy()
        filtered_df['distance_s'] = abs((filtered_df['hour_departure'] - time[0])*3600 + 
                                       (filtered_df['min_departure'] - time[1])*60 +
                                       time[2])
        filtered_df = filtered_df.sort_values(by=['distance_s'])


        return filtered_df.iloc[0]
    
    def get_delay_s(self, time: Tuple[int, int, int], station_name: str, direction: str, type_of_day: str) -> int:
        """
            Returns the delay in seconds for the given station, direction, type_of_day and time
        """
        closest_train = self.get_closest_train(time, station_name, direction, type_of_day)
        return ((closest_train['hour_departure'] - time[0])*3600 + 
                (closest_train['min_departure'] - time[1])*60
                + time[2])
    
    def get_station_delay(self, station_name: str, direction: str, type_of_day: str, interval : None) -> List[int]:
        
        destination_ids = get_destinations_ids_from_direction(direction)
        station_id = APIHandler().get_id_from_name(station_name)

        trains = self.actual_timetable[(self.actual_timetable['stationId'] == station_id) 
                                       & (self.actual_timetable['destinationId'].isin(destination_ids))]
        
        # Filter to consider the trains in the interval
        if interval is not None:
            start_min = interval[0][0]*60 + interval[0][1]
            end_min = interval[1][0]*60 + interval[1][1]
            trains = trains[(trains['arrival_hour']*60 + trains['arrival_min'] >= start_min) &
                            (trains['arrival_hour']*60 + trains['arrival_min'] <= end_min)]
        delays = []
        for index, train in trains.iterrows():
            delays.append(self.get_delay_s((train['arrival_hour'], train['arrival_min'], train['arrival_sec']),
                                           station_name, direction, type_of_day))
            
        return delays
    
    def density_estimation(self, delays: List[int], bandwidth: float = 30):
        """
            Returns the kernel density estimation for the given delays
        """
        kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth).fit(np.array(delays).reshape(-1, 1))
        return kde

    def plot_delays(self, station_name: str, direction: str, type_of_day: str, plot:str=None, n_bins = 20, interval = None):
        """
            Plots the delays for the given station, direction and type_of_day
            station_name : str, name of the station
            direction : str, direction of the train
            type_of_day : str, type of day (MTT, SAT, SUN)
            plot : Normal | Parzen | None, type of plot to consider
            n_bins : int, number of bins for the histogram
            interval : Tuple[Tuple[int, int], Tuple[int, int]] | None, interval to consider to plot the histogram. If None, consider all the delays
        """
        delays = self.get_station_delay(station_name, direction, type_of_day, interval = interval)

        if plot is not None:
            if plot == 'Parzen':
                # Calculate the kernel density estimation
                kde = self.density_estimation(delays)
                x = np.linspace(min(delays), max(delays), 1000)
                log_dens = kde.score_samples(x.reshape(-1, 1))
                plt.plot(x, np.exp(log_dens), label='Parzen estimation')
            elif plot == 'Normal':
                # Calculate the maximum likelihood for a normal distribution
                mu, std = np.mean(delays), np.std(delays)
                x = np.linspace(min(delays), max(delays), 100)
                y = 1/(std * np.sqrt(2 * np.pi)) * np.exp(- (x - mu)**2 / (2 * std**2))
                plt.plot(x, y, label='Normal distribution')
        plt.hist(delays, bins=n_bins, density=True, alpha=0.6, color='g')
        if interval is not None:
            plt.title(f'Delays for {station_name} in direction {direction} on {type_of_day} between {interval[0]} and {interval[1]}')
        else:
            plt.title(f'Delays for {station_name} in direction {direction} on {type_of_day}')
        plt.xlabel('Delay (s)')
        plt.ylabel('Density')
        plt.show()

    

