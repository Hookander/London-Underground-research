import pandas as pd
from typing import Dict
import numpy as np

class LinkLoadHandler():
    def __init__(self):
        self.dfs = {}
        try :
            for year in range(2019, 2024):
                sy = str(year)
                self.dfs[sy] = {}
                for type_of_day in ["MTT", "FRI", "SAT", "SUN"]:
                    self.dfs[sy][type_of_day] = pd.read_csv(f'./data/NUMBAT/{sy}/NBT{sy[-2:]}{type_of_day}_Outputs_cleaned.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
        except:
            print("Cleaning dataframes...")
            for year in range(2019, 2024):
                self.clean_dfs(year)
                sy = str(year)
                self.dfs[sy] = {}
                for type_of_day in ["MTT", "FRI", "SAT", "SUN"]:
                    self.dfs[sy][type_of_day] = pd.read_csv(f'./data/NUMBAT/{sy}/NBT{sy[-2:]}{type_of_day}_Outputs_cleaned.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
        
    def clean_dfs(self, year: int) -> pd.DataFrame:
        """
        Cleans the dataframes :
            - Removes stations from other lines than the Central Line
            - Convert all stations names to a standard format (mainly removing the "LU" at the end sometimes)
        Then saves the cleaned dataframe to a csv file to gain time
        """
        sy = str(year)
        for type_of_day in ["MTT", "FRI", "SAT", "SUN"]:
            df = pd.read_csv(f'./data/NUMBAT/{sy}/raw/NBT{sy[-2:]}{type_of_day}_Outputs.csv', encoding='utf-8', on_bad_lines='skip', sep=';', skiprows=2)
            df = df[df['Line'] == 'Central']

            # Removes the LU at the end if it exists
            df['From Station'] = df['From Station'].apply(lambda x: x[:-3] if x[-2:] == 'LU' else x)
            df['To Station'] = df['To Station'].apply(lambda x: x[:-3] if x[-2:] == 'LU' else x)

            # Remove aporstrophes and dots
            df['From Station'] = df['From Station'].apply(lambda x: x.replace("'", "").replace(".", ""))
            df['To Station'] = df['To Station'].apply(lambda x: x.replace("'", "").replace(".", ""))

            # "Bank and Monument is actually Bank"
            df['From Station'] = df['From Station'].apply(lambda x: 'Bank' if x == 'Bank and Monument' else x)
            df['To Station'] = df['To Station'].apply(lambda x: 'Bank' if x == 'Bank and Monument' else x)

            df.to_csv(f'./data/NUMBAT/{sy}/NBT{sy[-2:]}{type_of_day}_Outputs_cleaned.csv', index=False)


    def get_quaterhour(self, time:int)->str:
        """
        Returns the quaterhour for the given time
        if time = 1714 (17:14), returns '1700-1715'
        if time = 15 (00:15), return '0015-0030'
        """
        if time == 2345:
            return '2345-0000'
        s_time = str(time)
        if len(s_time) == 1:
            s_time = '000' + s_time
        elif len(s_time) == 2:
            s_time = '00' + s_time
        elif len(s_time) == 3:
            s_time = '0' + s_time
        mins = int(s_time[-2:])
        if mins < 15:
            return s_time[:2] + '00-' + s_time[:2] + '15'
        elif mins < 30:
            return s_time[:2] + '15-' + s_time[:2] + '30'
        elif mins < 45:
            return s_time[:2] + '30-' + s_time[:2] + '45'
        else:
            end = str(int(s_time[:-2])+1) + '00'
            end = '0' + end if len(end) == 3 else end
            return s_time[:2] + '45-' + end
    
    
    def get_avg_link_load(self, start_station: str, end_station: str, time: int or str, type_of_day:str, year: str) -> Dict[str, int]:
        """
        Returns the link load for the given station and time (averaged over a year)
        time format: hhmm (e.g., 1714 or '1714' for 17:14)
        """
        df = self.dfs[year][type_of_day]
        time = int(time)
        quaterhour = self.get_quaterhour(time)
        filtered_df = df[(df['From Station'] == start_station) & 
                            (df['To Station'] == end_station)]
        
        if filtered_df.empty:
            raise ValueError(f'get_avg_link_load, Invalid stations: {start_station}, {end_station}')
        
        if quaterhour not in filtered_df.columns:
            raise ValueError(f'get_avg_link_load, Invalid time: {quaterhour}')

        linkload = filtered_df[quaterhour].values[0]

        # Sometimes the linkload is a string with a weird space in it
        if type(linkload) == str:
            linkload = int(linkload.replace('\u202f', ''))
        
        return linkload
    
    def get_avg_daily_link_load(self, start_station: str, end_station: str, type_of_day: str, year: str) -> int:
        """
        Returns the daily link load for the given station
        Sums over all the quaterhours
        It is an average because each load at a given time is averaged over a year
        """
        df = self.dfs[year][type_of_day]
        filtered_df = df[(df['From Station'] == start_station) &
                            (df['To Station'] == end_station)]
        linkload = 0
        for hour in range(24):
            for mins in range(0, 60, 15):
                time = hour*100 + mins
                l = self.get_avg_link_load(start_station, end_station, time, type_of_day, year)
                linkload += l
        return linkload

    def get_next_station(self, station:str, direction:str) -> str:
        """
        Returns the next station in the given direction
        """
        next_stations = self.dfs['2019']['MTT'][(self.dfs['MTT']['From Station'] == station) 
                                        & (self.dfs['MTT']['Dir'] == direction)
                                        ]['To Station'].values
        if len(next_stations) == 0:
            raise ValueError(f'get_next_station, {station} does not have a successor in direction {direction}')
        return next_stations[0]

    def get_inbetween_stations(self, direction : str, start_station:str = None, end_station:str = None, branching=False) -> list:
        """
        Returns the stations inbetween start_station and end_station
        If either of those two is None, then returns all stations starting/ending at the other station, 
        in the current direction

        If branching is True, then we are checking 2 branches at once so one might not go to end_station

        """
        assert start_station is not None or end_station is not None, "get_inbetween_stations, start_station and end_station cannot be None at the same time"
        stations = [start_station]
        
        # Gets all stations starting from start_station in direction
        if end_station is None:
            
            next_stations = self.dfs['2019']['MTT'][(self.dfs['2019']['MTT']['From Station'] == start_station)
                                            & (self.dfs['2019']['MTT']['Dir'] == direction)
                                            ]['To Station'].values
            
            while len(next_stations) != 0 :           
                # There might be multiple branches because of the Central line
                # We check for those here
                current_station, next_stations = next_stations[0], next_stations[1:]

                #Because of the branches, we might have already added the station
                if not(current_station in stations):
                    stations.append(current_station)
                next = self.dfs['2019']['MTT'][(self.dfs['2019']['MTT']['From Station'] == current_station)
                                       & (self.dfs['2019']['MTT']['Dir'] == direction)
                                        ]['To Station'].values
                next_stations = np.concatenate([next_stations,next])
                
            return stations
        # Gets all stations ending at end_station in direction
        # We can just inverse the result of the previous case (in the other direction)
        if start_station is None:
            if direction == 'EB':
                new_direction = 'WB'
            if direction == 'WB':
                new_direction = 'EB'
            return self.get_inbetween_stations(new_direction, end_station, None)[::-1]

        i = 0
        # We iterate over all links
        # A problem might accur here, for example if the end_station is on a branch
        # Then the path splits and we need to consider both branches
        current_station = start_station
        while current_station != end_station and i<100:

            # Check for the number of next stops for possible branching
            nexts = self.dfs['2019']['MTT'][(self.dfs['2019']['MTT']['From Station'] == current_station)
                                              & (self.dfs['2019']['MTT']['Dir'] == direction)
                                              ]['To Station'].values
            
            if len(nexts)==2: # We are branching at this station
                path1 = stations + self.get_inbetween_stations(direction, nexts[0], end_station, branching = True)
                path2 = stations + self.get_inbetween_stations(direction, nexts[1], end_station, branching = True)
                if end_station in path1:
                    return path1
                else:
                    return path2
            elif len(nexts)==1:
                current_station = nexts[0]
                stations.append(current_station)
            i+=1
        
        if i == 100:
            if branching:
                return []
            else:
                raise ValueError(f'get_inbetween_stations, Invalid stations: {start_station}, {end_station}')

        return stations
    
    def get_next_consecutive_stations(self, station:str, direction:str) -> list:
        """
        Returns the next stations in the given direction, 
        there might be multiple next stations because of the branches
        """
        next_stations = self.dfs['2019']['MTT'][(self.dfs['2019']['MTT']['From Station'] == station) & (self.dfs['2019']['MTT']['Dir'] == direction)
                                        ]['To Station'].values
        return next_stations

    def get_all_stations(self):
        """
        Returns all the stations in the Central line
        """
        return self.dfs['2019']['MTT']['From Station'].unique()
    
#llh = LinkLoadHandler()
#llh.clean_dfs(2023)
#print(llh.get_next_consecutive_stations('Leytonstone', 'EB'))
#print(llh.get_inbetween_stations('EB', 'Leytonstone'))
