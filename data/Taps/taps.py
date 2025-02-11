import pandas as pd
from typing import Dict, List

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

        for year in range(2019, 2024):
            df = pd.read_csv(f'./data/Taps/TAPS-daily-rail-station-entryexit-{year}.csv')
            df = df[df['ServedBy'].str.contains('Tube', na=False)]
            df_full = pd.concat([df_full, df], ignore_index=True)
        df_full.to_csv(self.path, index=False)
    
    def get_entries_exits(self, station:str, date:str) -> Dict[str, int]:
        """
            Returns the entries and exits for the given station and date
            date format : dd/mm/yyyy
        """
        if station in self.entries_exits:
            return {'entries' : self.entries_exits[station]['entries'], 
                    'exits' : self.entries_exits[station]['exits']}
        else:
            #Station and date
            filtered_df = self.df[(self.df['Station'] == station) & (self.df['TravelDate'] == date)]

            #Entries and Exits
            entries_df = filtered_df[filtered_df['EntryExit'] == 'Entry']
            exits_df = filtered_df[filtered_df['EntryExit'] == 'Exit']
            if len(entries_df['TapCount'].values) == 0 or len(exits_df['TapCount'].values) == 0:
                # if for some reason there are no data for this day, we return the data
                # for 7 days before (to have the same type of day (weekday or weekend))
                previous_date = pd.to_datetime(date, format='%d/%m/%Y') - pd.DateOffset(days=7)
                previous_date = previous_date.strftime('%d/%m/%Y')
                #print(f"No data for {date}, returning data for {previous_date} : {station}")
                return self.get_entries_exits(station, previous_date)
            else:
                entries = entries_df['TapCount'].values[0]
                exits = exits_df['TapCount'].values[0]

            #we want ints, now they are strings like 1,391
            entries = int(entries.replace(',', ''))
            exits = int(exits.replace(',', ''))

            self.entries_exits[station] = {'entries' : entries, 'exits' : exits}

            return {'entries' : entries, 'exits' : exits}

    def get_total_output(self, stations: List[str], date:str) -> int:
        """
        Returns the total number of outputs for the given stations and date
        """
        total_outputs = 0
        for station in stations:
            total_outputs += self.get_entries_exits(station, date)['exits']
        return total_outputs



#taps = tapsHandler()
#print(taps.get_entries_exits('Notting Hill Gate', '01/01/2019'))

