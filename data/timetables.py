import pandas as pd
from typing import Tuple


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
        filtered_df['distance_s'] = abs(filtered_df['hour_departure']*3600 + filtered_df['min_departure']*60 
                                      - (3600 * time[0] + 60 * time[1] + time[2]))
        filtered_df = filtered_df.sort_values(by=['distance_s'])

        return filtered_df.iloc[0]
    
    def get_delay_s(self, time, station_name, direction, type_of_day):
        """
            Returns the delay in seconds for the given station, direction, type_of_day and time
        """
        closest_train = self.get_closest_train(time, station_name, direction, type_of_day)
        return (closest_train['hour_departure']*3600 + closest_train['min_departure']*60
                - (3600 * time[0] + 60 * time[1] + time[2]))
    
    
    def get_delays(self):
        """
            Returns the delays for each station and each direction.
            Goes through all the scraped tube arrival times, considers that it was supposed to arrive at the closest
            ideal time and calculates the delay.
        """
        return self.actual_timetable['delay'].value_counts()
    


handler = TimetablesHandler()
print(handler.get_delay_s((12, 34, 15), 'Woodford', 'WB', 'MTT'))