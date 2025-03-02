import pandas as pd
from typing import Dict, List, Tuple
from tools import *

class tapsHandler():
    def __init__(self):
        self.path = './data/Taps/merged_taps_2019-2024.csv'
        try:
            self.df = pd.read_csv(self.path, encoding='utf-8', on_bad_lines='skip', sep=',')
        except:
            self.merge_csvs()
            print("Merging taps csvs...")
            self.df = pd.read_csv(self.path, encoding='utf-8', on_bad_lines='skip', sep=',')
        
        # To prevent multiple calls to the same data, we store the entries and exits here
        self.entries_exits = {}
    
    def merge_csvs(self):
        """
        Merges the csvs files into 1 big one and filters anything that isn't Tube
        only need to be done if it doens't already exit
        """
        df_full = pd.DataFrame(columns=['TravelDate','Station','EntryExit','TapCount', 'ServedBy'])
        """
        for year in range(2020, 2023):
            df = pd.read_csv(f'./data/Taps/TAPS-daily-rail-station-entryexit-{year}.csv')
            df = df[df['ServedBy'].str.contains('Tube', na=False)]
            df['TapCount'] = df['TapCount'].str.replace(',', '').astype(int)
            df_full = pd.concat([df_full, df], ignore_index=True)
        """
        # Handle the years 2019 and 2023 since it is not fully in the TAPS file (lack of data)
        stations = get_all_stations()

        # 2019-2020
        df_2019 = pd.read_csv(f'./data/Taps/taps_alternate_2019-2020.csv')
        # TravelDate,Station,EntryExit,TapCount,ServedBy
        df_2019 = df_2019.rename(columns={'TravelDateSk': 'TravelDate', 'StationName': 'Station', 'EntryOrExit': 'EntryExit', 'Count': 'TapCount'})
        df_2019['ServedBy'] = 'Tube'
        df_2019['TravelDate'] = pd.to_datetime(df_2019['TravelDate'], format='%Y%m%d').dt.strftime('%d/%m/%Y')
        df_2019 = df_2019[df_2019['ServedBy'].str.contains('Tube', na=False)]
        df_2019['Station'] = df_2019['Station'].str.replace(' LU', '')
        df_full = pd.concat([df_full, df_2019], ignore_index=True)

        # 2021-2022
        df_2021 = pd.read_csv(f'./data/Taps/taps_alternate_2021-2022.csv')
        # TravelDate,Station,EntryExit,TapCount,ServedBy
        df_2021 = df_2021.rename(columns={'TravelDateSk': 'TravelDate', 'StationName': 'Station', 'EntryOrExit': 'EntryExit', 'Count': 'TapCount'})
        df_2021['ServedBy'] = 'Tube'
        df_2021['TravelDate'] = pd.to_datetime(df_2021['TravelDate'], format='%Y%m%d').dt.strftime('%d/%m/%Y')
        df_2021 = df_2021[df_2021['ServedBy'].str.contains('Tube', na=False)]
        df_2021['Station'] = df_2021['Station'].str.replace(' LU', '')
        df_full = pd.concat([df_full, df_2021], ignore_index=True)

        # 2023
        df_2023 = pd.read_csv(f'./data/Taps/taps_alternate_2023-present.csv')
        # TravelDate,Station,EntryExit,TapCount,ServedBy
        df_2023 = df_2023.rename(columns={'TravelDateSk': 'TravelDate', 'StationName': 'Station', 'EntryOrExit': 'EntryExit', 'Count': 'TapCount'})
        df_2023['ServedBy'] = 'Tube'
        df_2023['TravelDate'] = pd.to_datetime(df_2023['TravelDate'], format='%Y%m%d').dt.strftime('%d/%m/%Y')
        df_2023 = df_2023[df_2023['ServedBy'].str.contains('Tube', na=False)]
        df_2023['Station'] = df_2023['Station'].str.replace(' LU', '')
        df_full = pd.concat([df_full, df_2023], ignore_index=True)

        for year in range(2019, 2024):
            df = pd.read_csv(f'./data/Taps/TAPS-daily-rail-station-entryexit-{year}.csv')
            df = df[df['ServedBy'].str.contains('Tube', na=False)]
            df['TapCount'] = df['TapCount'].str.replace(',', '').astype(int)
            df_full = pd.concat([df_full, df], ignore_index=True)
        df_full = df_full.drop_duplicates()
        df_full = df_full[df_full['Station'].isin(stations)]
        df_full.to_csv(self.path, index=False)
    
    def get_entries_exits(self, station:str, date:str, handle_missing = True, print_missing = True) -> Tuple[Dict[str, int], bool]:
        """
            Returns the entries and exits for the given station and date
            date format : dd/mm/yyyy
            args:
                station (str): The station for which to get the entries and exits
                date (str): The date for which to get the entries and exits
                handle_missing (bool): If True, returns the data for 7 days before if there is no data for the given date
                                    If False, returns 0 for entries and exits if there is no data for the given date
                print_missing (bool): If True, prints a message when there is no data for the given date
            returns:
                Tuple(Dict[str, int], bool): The entries and exits for the given station and date, and a boolean indicating if the data was found
        """
        if station not in get_all_stations():
            raise ValueError(f"Station {station} not found")
        if (station, date) in self.entries_exits:
            return {'entries' : self.entries_exits[(station, date)]['entries'], 
                    'exits' : self.entries_exits[(station, date)]['exits']}, True
        else:
            #Station and date
            filtered_df = self.df[(self.df['Station'] == station) & (self.df['TravelDate'] == date)]

            #Entries and Exits
            entries_df = filtered_df[filtered_df['EntryExit'] == 'Entry']
            exits_df = filtered_df[filtered_df['EntryExit'] == 'Exit']
            if len(entries_df['TapCount'].values) == 0 or len(exits_df['TapCount'].values) == 0:
                if not handle_missing:
                    return {'entries' : 0, 'exits' : 0}, False
                if print_missing:
                    print(f"No data for {date}, returning data for 7 days before (to have the same type of day (weekday or weekend)) : {station}")
                # if for some reason there are no data for this day, we return the data
                # for 7 days before (to have the same type of day (weekday or weekend))
                previous_date = pd.to_datetime(date, format='%d/%m/%Y') - pd.DateOffset(days=7)
                previous_date = previous_date.strftime('%d/%m/%Y')
                #print(f"No data for {date}, returning data for {previous_date} : {station}")
                return self.get_entries_exits(station, previous_date, print_missing=False)[0], False
            else:
                
                entries = entries_df['TapCount'].values[0]
                exits = exits_df['TapCount'].values[0]

            self.entries_exits[(station, date)] = {'entries' : entries, 'exits' : exits}

            return {'entries' : entries, 'exits' : exits}, True

    def get_total_output(self, stations: List[str], date:str) -> int:
        """
        Returns the total number of outputs for the given stations and date
        """
        total_outputs = 0
        for station in stations:
            total_outputs += self.get_entries_exits(station, date)['exits'][0]
        return total_outputs
    



