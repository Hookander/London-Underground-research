import pandas as pd
from typing import Dict, List

class tapsHandler():
    def __init__(self, path):
        self.df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip', sep=',')
    
    def merge_csvs(self):
        """
        Merges the csvs files into 1 big one and filters anything that isn't Tube
        only need to be done if it doens't already exit
        """
        df_full = pd.DataFrame(columns=['TravelDate','Station','EntryExit','TapCount', 'ServedBy'])

        for year in range(2019, 2024):
            df = pd.read_csv(f'./data/Taps/TAPS-daily-rail-station-entryexit-{year}.csv')
            df = df[df['ServedBy'] == 'Tube']
            df_full = pd.concat([df_full, df], ignore_index=True)
        df_full.to_csv('./data/Taps/merged_taps_2019-2024.csv', index=False)
    
    def get_entries_exits(self, station:str, date:str) -> Dict[str, int]:
        """
            Returns the entries and exits for the given station and date
            date format : dd/mm/yyyy
        """
        #Station and date
        filtered_df = self.df[(self.df['Station'] == station) & (self.df['TravelDate'] == date)]

        #Entries and Exits
        entries = filtered_df[filtered_df['EntryExit'] == 'Entry']['TapCount'].values[0]
        exits = filtered_df[filtered_df['EntryExit'] == 'Exit']['TapCount'].values[0]

        #we want ints, now they are strings like 1,391
        entries = int(entries.replace(',', ''))
        exits = int(exits.replace(',', ''))

        return {'entries' : entries, 'exits' : exits}




taps = tapsHandler('./data/Taps/merged_taps_2019-2024.csv')
print(taps.get_entries_exits('Notting Hill Gate', '01/01/2019'))

