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
    
    def plot_best_theshold_evolution(self, station):
        """
        Plot the evolution of the best precipitation threshold for a station over a few years.
        Is useful to check the steadiness of the threshold.
        Parameters:
        station (str): The station for which to plot the evolution of the best threshold.
        """
        years = [i for i in range(2019, 2025)]
        best_entry_thresholds = []
        best_exit_thresholds = []
        for year in years:
            start_date = f'01/01/{year}'
            end_date = f'31/12/{year}'
            best_entry_threshold, best_exit_threshold = self.station_best_thresholds(station, start_date, end_date)
            best_entry_thresholds.append(best_entry_threshold)
            best_exit_thresholds.append(best_exit_threshold)
        
        plt.plot(years, best_entry_thresholds, label='Entries', color='b')
        plt.plot(years, best_exit_thresholds, label='Exits', color='r')
        plt.legend()
        plt.xlabel('Precipitation threshold (mm)')
        plt.ylabel('Average number of entries/exits')
        plt.title(f'Evolution of the best precipitation threshold for {station}')
        plt.show()
    
    def station_best_thresholds(self, station, start_date, end_date, coefs = False, precision = 2) -> Tuple[float, float]:
        """
        Find the precipitation threshold that maximizes the coef between the average number of entries on dry and rainy days.
        Parameters:
        station (str): The station for which to find the best threshold.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY'
        Returns:
        tuple: A tuple containing the best precipitation thresholds for entries and exits.
        """
        thresholds = [i for i in range(0, 20, precision)]
        best_entry_threshold = 0
        best_exit_threshold = 0
        best_entry_coef = 0
        best_exit_coef = 0
        for threshold in thresholds:
            entries_dict, exits_dict = self.station_weather_influence(station, start_date, end_date, threshold)

            entry_coef = entries_dict['rainy'] / entries_dict['dry'] if entries_dict['dry'] != 0 else 1
            exit_coef = exits_dict['rainy'] / exits_dict['dry'] if exits_dict['dry'] != 0 else 1
            if entry_coef > best_entry_coef:
                best_entry_coef = entry_coef
                best_entry_threshold = threshold
            if exit_coef > best_exit_coef:
                best_exit_coef = exit_coef
                best_exit_threshold = threshold
        if coefs:
            return (best_entry_threshold, best_entry_coef), (best_exit_threshold, best_exit_coef)
        else:
            return best_entry_threshold, best_exit_threshold

    def plot_best_thresholds(self, start_date, end_date, test = False, all_years = False):
        """
        Plot the best precipitation threshold for each station within a specified date range.
        Parameters:
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY'
        test (bool, optional): If True, only plot the first 5 stations. Defaults to False.
        """
        stations = get_all_stations()
        years = [i for i in range(2019, 2025)]
        if test:
            stations = stations[15:20]
        if all_years:
            for year in years:
                start_date = f'01/01/{year}'
                end_date = f'31/12/{year}'
                best_thresholds = [self.station_best_thresholds(station, start_date, end_date) for station in stations]
                best_entries = [threshold[0] for threshold in best_thresholds]
                best_exits = [threshold[1] for threshold in best_thresholds]
                plt.plot(stations, best_entries, label='Entries')
                plt.plot(stations,best_exits, label='Exits')
                plt.legend()
        else:
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
    
    def get_threshold_influence(self, station, start_date, end_date, relative = False, plot = True, precision = 2):
        """
        Plot the average number of entries/exits at a station on rainy days for different precipitation thresholds.
        Parameters:
        station (str): The station for which to plot the influence of the precipitation threshold.
        start_date (str): The start date of the period in 'dd/mm/YYYY' format.
        end_date (str): The end date of the period in 'dd/mm/YYYY' format.
        relative (bool, optional): If True, plot the relative influence of the threshold, 
                ie the number of entries/exits on rainy days / number on dry days. Defaults to False.
        """
        thresholds = [i for i in range(0, 20, precision)]
        #print(len(thresholds))
        entries_rainy_avgs = []
        exits_rainy_avgs = []
        entris_coefs = []
        exits_coefs = []
        for threshold in thresholds:
            entries_dict, exits_dict = self.station_weather_influence(station, start_date, end_date, threshold)
            entries_rainy_avgs.append(entries_dict['rainy'])
            exits_rainy_avgs.append(exits_dict['rainy'])
            if entries_dict['dry'] != 0:
                entris_coefs.append(entries_dict['rainy'] / entries_dict['dry'])
            else:
                entris_coefs.append(1)
            if exits_dict['dry'] != 0:
                exits_coefs.append(exits_dict['rainy'] / exits_dict['dry'])
            else:
                exits_coefs.append(1)
        if plot:
            if relative:
                plt.plot(thresholds, entris_coefs, label='Entries', color='b')
                plt.plot(thresholds, exits_coefs, label='Exits', color='r')
                plt.axhline(y=1, color='b', linestyle='--', label = 'Dry days avg')
                plt.legend()
                plt.xlabel('Precipitation threshold (mm)')
                plt.ylabel('Relative increase entries/exits (%)')
                #plt.title(f'Influence of the precipitation threshold on the average number of entries at {station}, from {start_date} to {end_date}')
            else:
                plt.plot(thresholds, entries_rainy_avgs, label='Entries', color='b')
                plt.plot(thresholds, exits_rainy_avgs, label='Exits', color='r')
                plt.axhline(y=entries_rainy_avgs[0], color='b', linestyle='--', label='total entries avg')
                plt.axhline(y=exits_rainy_avgs[0], color='r', linestyle='--', label='total exits avg')
                plt.legend()
                plt.xlabel('Precipitation threshold (mm)')
                plt.ylabel('Avg entries/exits on rainy days')
                #plt.title(f'Influence of the precipitation threshold on the average number of entries at {station}, from {start_date} to {end_date}')
            plt.show()
        if relative:
            return {'entries': entris_coefs, 'exits': exits_coefs}
        else:
            return {'entries': entries_rainy_avgs, 'exits': exits_rainy_avgs}
        

    def plot_threshold_influence_evolution(self, station, type = 'entries', precision = 1):
        """
        Plot the average number of entries/exits at a station on rainy days for different precipitation thresholds
        on different years. Helpful to check the evolution of the influence of the thresholds, and to get a sense of
        the steadiness of the thresholds.

        Parameters:
        station (str): The station for which to plot the influence of the precipitation threshold.
        type (str, optional): The type of data to plot. Can be 'entries' or 'exits'. Defaults to 'entries'.
        """
        assert type in ['entries', 'exits'], "plot_threshold_influence_evolution : type must be 'entries' or 'exits'"
        years = [i for i in range(2019, 2025) if i not in [2020, 2021]]
        years = [i for i in range(2019, 2025)]
        thresholds = [i for i in range(0, 20, precision)]

        for year in years:
            start_date = f'01/01/{year}'
            end_date = f'31/12/{year}'
            coefs = self.get_threshold_influence(station, start_date, end_date, relative=True, plot=False, precision = precision)[type]
            plt.plot(thresholds, coefs, label=year)
        plt.axhline(y=1, color='b', linestyle='--')
        plt.legend()
        plt.xlabel('Precipitation (mm)')
        plt.ylabel(f'Relative inscrease (%)')
        #plt.title(f'Influence of the precipitation threshold on the average number of {type} at {station}, from 2019 to 2024')
        plt.show()

    def find_steadiest_thresholh(self, station, precision):
        """
        Find the steadiest threshold for the given station over a range of years.
        The steadiness is measured by the standard deviation of the relative increase of entries/exits on rainy days
        for different precipitation thresholds (ie of the coefficients)

        Parameters:
        station (list): station to consider.
        precision (int): The precision of the thresholds to consider.
        """
        
        # years = [i for i in range(2019, 2025) if i not in [2020, 2021]]
        years = [i for i in range(2019, 2025) if i not in [2020]]
        thresholds = [i for i in range(0, 20, precision)][1:]  # Remove the first threshold (0 mm) as it is not useful

        entries_coefs = []
        exits_coefs = []
        for year in years:
            start_date = f'01/01/{year}'
            end_date = f'31/12/{year}'
            entries_coefs.append(self.get_threshold_influence(station, start_date, end_date, relative=True, plot=False, precision=precision)['entries'])
            exits_coefs.append(self.get_threshold_influence(station, start_date, end_date, relative=True, plot=False, precision=precision)['exits'])
        entries_coefs = np.array(entries_coefs)
        exits_coefs = np.array(exits_coefs)
        # Remove threshold 0 -> useless
        entries_coefs = entries_coefs[:, 1:]
        exits_coefs = exits_coefs[:, 1:]
        entries_std = np.std(entries_coefs, axis=0)
        exits_std = np.std(exits_coefs, axis=0)
        best_entry_threshold = thresholds[np.argmin(entries_std) + 1]  # +1 because we removed the first threshold (0)
        best_exit_threshold = thresholds[np.argmin(exits_std) + 1]
        print(f'Best entry threshold: {best_entry_threshold} mm, std: {np.min(entries_std)}')
        print(f'Best exit threshold: {best_exit_threshold} mm, std: {np.min(exits_std)}')
        return best_entry_threshold, best_exit_threshold, entries_std, exits_std


