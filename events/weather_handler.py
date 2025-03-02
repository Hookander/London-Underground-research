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
    
    def station_weather_influence(self, station, start_date, end_date, threshold = 5, weather_days: Optional[Dict[str, int]] = None):
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
        tuple: A tuple containing two floats:
            - dry_avg (float): The average number of entries on dry days.
            - rainy_avg (float): The average number of entries on rainy days.
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

        dry_avg = 0
        rainy_avg = 0
        got_data = 0
        if len(dry_days) > 0:
            for date in dry_days:
                avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
                if not_missing:
                    dry_avg += avg['entries']
                    got_data += 1
            dry_avg /= got_data
        got_data = 0
        for date in rainy_days:
            avg, not_missing = self.taps.get_entries_exits(station, date, handle_missing=False)
            if not_missing:
                rainy_avg += avg['entries']
                got_data += 1
        rainy_avg /= got_data

        return dry_avg, rainy_avg
    
    def get_best_threshold(self, station, start_date, end_date):
        """
        Find the precipitation threshold that maximizes the coef between the average number of entries on dry and rainy days.
        Parameters:
        station (str): The station for which to find the best threshold.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY'
        Returns:
        float: The best precipitation threshold.
        """
        thresholds = [i/2 for i in range(1, 30, 1)]
        best_threshold = 0
        best_coef = 0
        for threshold in thresholds:
            dry_avg, rainy_avg = self.station_weather_influence(station, start_date, end_date, threshold)
            coef = rainy_avg / dry_avg
            if coef > best_coef:
                best_coef = coef
                best_threshold = threshold
        return best_threshold

    def plot_best_thresholds(self, start_date, end_date):
        stations = get_all_stations()
        best_thresholds = [self.get_best_threshold(station, start_date, end_date) for station in stations]
        plt.plot(stations, best_thresholds)
        plt.xlabel('Station')
        plt.ylabel('Best precipitation threshold (mm)')
        plt.title('Best precipitation threshold for each station')
        plt.show()


    def plot_diff_rainy_days(self, start_date, end_date, threshold = 5, test = False):
        """
        Plot the average number of entries at each station on dry and rainy days within a specified date range.
        Parameters:
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        threshold (int, optional): The precipitation threshold to classify a day as rainy. Defaults to 5.
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
            dry_avg, rainy_avg = self.station_weather_influence(station, start_date, end_date, threshold, {'dry': dry_days, 'rainy': rainy_days})
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
        rainy_avgs = []
        for threshold in thresholds:
            _, rainy_avg = self.station_weather_influence(station, start_date, end_date, threshold)
            rainy_avgs.append(rainy_avg)
        plt.plot(thresholds, rainy_avgs)
        plt.axhline(y=rainy_avgs[0], color='r', linestyle='--', label='total avg')
        plt.legend()
        plt.xlabel('Precipitation threshold (mm)')
        plt.ylabel('Avg entries on rainy days')
        plt.title(f'Influence of the precipitation threshold on the average number of entries at {station}')
        plt.show()


