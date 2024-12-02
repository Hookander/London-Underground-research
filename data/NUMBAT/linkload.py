import pandas as pd
from typing import Dict

class LinkLoadHandler():
    def __init__(self):
        self.dfs = {}
        for type_of_day in ["MTT", "FRI", "SAT", "SUN"]:
            self.dfs[type_of_day] = pd.read_csv(f'./data/NUMBAT/2019/NBT19{type_of_day}_Outputs.csv', encoding='utf-8', on_bad_lines='skip', sep=';', skiprows=2)
            # We only consider the Central line
            self.dfs[type_of_day] = self.dfs[type_of_day][self.dfs[type_of_day]['Line'] == 'Central']

    def get_quaterhour(self, time:int)->str:
        """
        Returns the quaterhour for the given time
        if time = 1714 (17:14), returns '1700-1715'
        if time = 15 (00:15), return '0015-0030'
        """
        s_time = str(time)
        if len(s_time) == 1:
            s_time = '000' + s_time
        elif len(s_time) == 2:
            s_time = '00' + s_time
        elif len(s_time) == 3:
            s_time = '0' + s_time
        mins = int(s_time[-2:])
        if mins < 15:
            return s_time[:2] + '00-0015'
        elif mins < 30:
            return s_time[:2] + '15-0030'
        elif mins < 45:
            return s_time[:2] + '30-0045'
        else:
            end = str(int(s_time[:-2])+1) + '00'
            end = '0' + end if len(end) == 3 else end
            return s_time[:2] + '45-' + end
        
    
    def get_avg_link_load(self, start_station: str, end_station: str, time: int or str, day_of_week:str) -> Dict[str, int]:
        """
        Returns the link load for the given station and time
        time format: hhmm (e.g., '1714' for 17:14)
        """
        match day_of_week:
            case 'Friday':
                df = self.dfs['FRI']
            case 'Saturday':
                df = self.dfs['SAT']
            case 'Sunday':
                df = self.dfs['SUN']
            case _:
                df = self.dfs['MTT']
        time = int(time)
        quaterhour = self.get_quaterhour(time)
        filtered_df = df[(df['From Station'] == start_station) & 
                            (df['To Station'] == end_station)]
        
        if filtered_df.empty:
            raise ValueError(f'get_avg_link_load, Invalid stations: {start_station}, {end_station}')
        
        if quaterhour not in filtered_df.columns:
            raise ValueError(f'get_avg_link_load, Invalid time: {quaterhour}')

        linkload = filtered_df[quaterhour].values[0]

        
        return linkload
    
    def get_inbetween_stations(self, start_station:str, end_station:str) -> list:
        """
        Returns the stations inbetween start_station and end_station
        """
        stations = [start_station]
        current_station = start_station
        i = 0
        # We iterate over all links
        while current_station != end_station and i<100:
            current_station = self.dfs['MTT'][self.dfs['MTT']['From Station'] == current_station]['To Station'].values[0]
            stations.append(current_station)
            i+=1
        
        if i == 100:
            print(stations)
            raise ValueError(f'get_inbetween_stations, Invalid stations: {start_station}, {end_station}')

        return stations
    
#llh = LinkLoadHandler()
#print(llh.get_inbetween_stations("North Acton", "Queensway"))
#print(llh.get_avg_link_load('Buckhurst Hill', 'Loughton', 746, 'Friday'))