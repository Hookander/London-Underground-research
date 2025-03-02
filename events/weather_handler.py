from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Stations, Daily, Point

class WeatherHandler:
    def __init__(self):
        self.ICL = Point(51.499439, -0.174329) # ICL
        self.taps = tapsHandler()
        self.llh = LinkLoadHandler()
    
    def station_weather_influence(self, station, start_date, end_date, threshold = 5):
        """
        Calculate the average number of entries at a station on dry and rainy days within a specified date range.
        Parameters:
        station (str): The station for which to calculate the weather influence.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        threshold (int, optional): The precipitation threshold to classify a day as rainy. Defaults to 5.
        Returns:
        tuple: A tuple containing two floats:
            - dry_avg (float): The average number of entries on dry days.
            - rainy_avg (float): The average number of entries on rainy days.
        """
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
        if len(dry_days) > 0:
            for date in dry_days:
                dry_avg += self.taps.get_entries_exits(station, date)['entries']
            dry_avg /= len(dry_days)
        for date in rainy_days:
            rainy_avg += self.taps.get_entries_exits(station, date)['entries']
        rainy_avg /= len(rainy_days)

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


    def plot_diff_rainy_days(self, start_date, end_date, threshold = 5):
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
        dry_avg_stations = []
        rainy_avg_stations = []
        for station in all_stations:
            dry_avg = 0
            rainy_avg = 0
            for date in dry_days:
                dry_avg += self.taps.get_entries_exits(station, date)['entries']
            dry_avg /= len(dry_days)
            for date in rainy_days:
                rainy_avg += self.taps.get_entries_exits(station, date)['entries']
            rainy_avg /= len(rainy_days)
            dry_avg_stations.append(dry_avg)
            rainy_avg_stations.append(rainy_avg)
            print(f'{station} : dry avg = {dry_avg}, rainy avg = {rainy_avg}')
        ind_stations = [i for i in range(len(all_stations))]
        plt.bar(all_stations, dry_avg_stations, color='b', label='Dry days')
        plt.bar(all_stations, rainy_avg_stations, color='r', label='Rainy days')
        plt.xlabel('Station')
        plt.ylabel('Avg entries')
        plt.title(f'Avg entries for dry and rainy days with a threshold of {threshold} mm')
        plt.legend()
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


