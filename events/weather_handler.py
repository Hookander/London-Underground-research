from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Stations, Daily, Point
import numpy as np
from typing import Optional, Dict

class WeatherHandler:
    def __init__(self):
        self.ICL = Point(51.499439, -0.174329) # ICL
        self.taps = tapsHandler()
        self.llh = LinkLoadHandler()
    
    def station_weather_influence(self, station, start_date, end_date, threshold = 5, weather_days: Optional[Dict[str, int]] = None)\
            -> Tuple[Dict, Dict]:
        """
        Calculate the average number of entries at a station on dry and rainy days within a specified date range.
        Parameters:
        station (str): The station for which to calculate the weather influence.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        threshold (int, optional): The precipitation threshold to classify a day as rainy. Defaults to 5.
        weather_days (Dict[str, int], optional): A dictionary containing the rainy days for each date in the period. Defaults to None.
                Useful if the rainy days have already been calculated.
        Returns:
        tuple: A tuple containing two dicts:
            - The first dict contains the average number of entries on dry days and rainy days.
            - The second dict contains the average number of exits on dry days and rainy days.
        """
        if weather_days is not None: # If the rainy/dry days have already been calculated
            rainy_days = weather_days['rainy']
            dry_days = weather_days['dry']
        else:
            start = datetime.strptime(start_date, '%d/%m/%Y')
            end = datetime.strptime(end_date, '%d/%m/%Y')
            precipitations = Daily(self.ICL, start, end)
            precipitations = precipitations.fetch()
            precipitations = precipitations['prcp']
            rainy_days = precipitations[precipitations >= threshold].index
            rainy_days = [date.strftime('%d/%m/%Y') for date in rainy_days]
            dry_days = precipitations[precipitations < threshold].index
            dry_days = [date.strftime('%d/%m/%Y') for date in dry_days]


        entries_avg = {'dry': 0, 'rainy': 0}
        exits_avg = {'dry': 0, 'rainy': 0}
        got_data = 0
        if len(dry_days) > 0:
            for date in dry_days:
                avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
                if not_missing:
                    entries_avg['dry'] += avg['entries']
                    exits_avg['dry'] += avg['exits']
                    got_data += 1
            entries_avg['dry'] /= got_data
            exits_avg['dry'] /= got_data
        got_data = 0
        for date in rainy_days:
            avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
            if not_missing:
                entries_avg['rainy'] += avg['entries']
                exits_avg['rainy'] += avg['exits']
                got_data += 1
        entries_avg['rainy'] /= got_data
        exits_avg['rainy'] /= got_data

        return entries_avg, exits_avg
    
    def station_best_thresholds(self, station, start_date, end_date) -> Tuple[float, float]:
        """
        Find the precipitation threshold that maximizes the coef between the average number of entries on dry and rainy days.
        Parameters:
        station (str): The station for which to find the best threshold.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY'
        Returns:
        tuple: A tuple containing the best precipitation thresholds for entries and exits.
        """
        thresholds = [i/2 for i in range(1, 30, 1)]
        best_entry_threshold = 0
        best_exit_threshold = 0
        best_entry_coef = 0
        best_exit_coef = 0
        for threshold in thresholds:
            entries_dict, exits_dict = self.station_weather_influence(station, start_date, end_date, threshold)
            entry_coef = entries_dict['rainy'] / entries_dict['dry']
            exit_coef = exits_dict['rainy'] / exits_dict['dry']
            if entry_coef > best_entry_coef:
                best_entry_coef = entry_coef
                best_entry_threshold = threshold
            if exit_coef > best_exit_coef:
                best_exit_coef = exit_coef
                best_exit_threshold = threshold
        return best_entry_threshold, best_exit_threshold

    def plot_best_thresholds(self, start_date, end_date, test = False):
        """
        Plot the best precipitation threshold for each station within a specified date range.
        Parameters:
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY'
        test (bool, optional): If True, only plot the first 5 stations. Defaults to False.
        """
        stations = get_all_stations()
        if test:
            stations = stations[15:20]
        best_thresholds = [self.station_best_thresholds(station, start_date, end_date) for station in stations]
        best_entries = [threshold[0] for threshold in best_thresholds]
        best_exits = [threshold[1] for threshold in best_thresholds]
        plt.plot(stations, best_entries, label='Entries')
        plt.plot(stations,best_exits, label='Exits')
        plt.legend()
        plt.xlabel('Station')
        plt.ylabel('Best precipitation threshold (mm)')
        plt.title('Best precipitation threshold for each station')
        plt.show()


    def plot_diff_rainy_days(self, start_date, end_date, threshold = 5, type = 'entries', test = False):
        """
        Plot the average number of entries at each station on dry and rainy days within a specified date range.
        Parameters:
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        threshold (int, optional): The precipitation threshold to classify a day as rainy. Defaults to 5.
        type (str, optional): The type of data to plot. Can be 'entries' or 'exits'. Defaults to 'entries'.        
        test (bool, optional): If True, only plot the first 5 stations. Defaults to False.
        """
        start = datetime.strptime(start_date, '%d/%m/%Y')
        end = datetime.strptime(end_date, '%d/%m/%Y')
        precipitations = Daily(self.ICL, start, end)
        precipitations = precipitations.fetch()
        rainy_days = precipitations[precipitations['prcp'] >= threshold].index
        rainy_days = [date.strftime('%d/%m/%Y') for date in rainy_days]
        dry_days = precipitations[precipitations['prcp'] < threshold].index
        dry_days = [date.strftime('%d/%m/%Y') for date in dry_days]

        # For now we only study the daily correlation with the avg entries
        all_stations = self.llh.get_all_stations()
        if test:
            all_stations = all_stations[15:20]
        dry_avg_stations = []
        rainy_avg_stations = []
        for station in all_stations:
            ent_dict, ex_dict = self.station_weather_influence(station, start_date, end_date, threshold, {'dry': dry_days, 'rainy': rainy_days})
            if type == 'entries':
                dry_avg = ent_dict['dry']
                rainy_avg = ent_dict['rainy']
            else:
                dry_avg = ex_dict['dry']
                rainy_avg = ex_dict['rainy']
            dry_avg_stations.append(dry_avg)
            rainy_avg_stations.append(rainy_avg)
            print(f'{station} : dry avg = {dry_avg}, rainy avg = {rainy_avg}')
        ind_stations = [i for i in range(len(all_stations))]
        ind = np.arange(len(all_stations))  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        bar1 = ax.bar(ind - width/2, dry_avg_stations, width, label='Dry days', color='b')
        bar2 = ax.bar(ind + width/2, rainy_avg_stations, width, label='Rainy days', color='r')

        ax.set_xlabel('Station')
        ax.set_ylabel('Avg entries')
        ax.set_title(f'Avg entries for dry and rainy days with a threshold of {threshold} mm, from {start_date} to {end_date}')
        ax.set_xticks(ind)
        ax.set_xticklabels(all_stations, rotation=45)
        ax.legend()

        fig.tight_layout()
        plt.show()
    
    def plot_threshold_influence(self, station, start_date, end_date):
        """
        Plot the average number of entries at a station on rainy days for different precipitation thresholds.
        Parameters:
        station (str): The station for which to plot the influence of the precipitation threshold.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        """
        thresholds = [i for i in range(0, 20, 2)]
        entries_rainy_avgs = []
        exits_rainy_avgs = []
        for threshold in thresholds:
            entries_dict, exits_dict = self.station_weather_influence(station, start_date, end_date, threshold)
            entries_rainy_avgs.append(entries_dict['rainy'])
            exits_rainy_avgs.append(exits_dict['rainy'])
        plt.plot(thresholds, entries_rainy_avgs, label='Entries', color='b')
        plt.plot(thresholds, exits_rainy_avgs, label='Exits', color='r')
        plt.axhline(y=entries_rainy_avgs[0], color='b', linestyle='--', label='total entries avg')
        plt.axhline(y=exits_rainy_avgs[0], color='r', linestyle='--', label='total exits avg')
        plt.legend()
        plt.xlabel('Precipitation threshold (mm)')
        plt.ylabel('Avg entries/exits on rainy days')
        plt.title(f'Influence of the precipitation threshold on the average number of entries at {station}, from {start_date} to {end_date}')
        plt.show()


