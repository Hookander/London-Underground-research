import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from data import *
from model.model_class import ModelClass



class Model(ModelClass):
    """
    This is the is the simplest model we try, just a bunch of linear layers
    """
    def __init__(self):
        super().__init__()
        self.fc = nn.Linear(1, 1)

    def create_data(self, year:str, path: str) -> None:
        """
        Create the csv file for training wioth the following columns:
        - day
        - month
        - year
        - tod_id
        - start_station_id
        - end_station_id
        - direction_id
        - hour
        - min (0, 15, 30 or 45), we are only interested in the quarter of the hour
        - link_load
        - output

        - taps ? We start without the taps

        2019-2022 : training
        2023 : testing
        """
        try:
            df = pd.read_csv(path)
        except:
            print('Creating new file')
            df = pd.DataFrame(columns=['day', 'month', 'year', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load', 'output'])
            df.to_csv(path, index=False)
        stations = self.llh.get_all_stations()
        directions = ['EB', 'WB']

        ntods_per_year = nb_days_per_tod(year)
        dates = get_dates_between('01/01/'+year, '31/12/'+year)
        already_done_dates = (df['day'].astype(str) + '/' + df['month'].astype(str) + '/' + year).tolist()
        print(already_done_dates)
        dates_to_do = [date for date in dates if date not in already_done_dates]
        print(dates_to_do)
        for date in dates_to_do:
            begin = time.time()
            day_of_week = get_day_of_week(date)
            type_of_day = get_type_of_day(day_of_week, include_friday=True)

            tod_id = self.tod_to_int(type_of_day)

            month = int(date.split('/')[1])

            day = int(date.split('/')[0])
            for direction in directions:
                dir_id = self.direction_to_int(direction)
                for start_station in stations:
                    start_id = self.station_to_int(start_station)
                    for end_station in self.llh.get_next_consecutive_stations(start_station, direction):
                        end_id = self.station_to_int(end_station)
                        b = time.time()
                        for hour in range(24):
                            for minute in [0, 15, 30, 45]:
                                quarter_hour = str(hour).zfill(2) + str(minute).zfill(2)
                                avg_link_load = self.llh.get_avg_link_load(start_station, end_station, quarter_hour, type_of_day, year)
                                output = avg_link_load * ntods_per_year[type_of_day]
                                df = df._append({'day': day, 
                                                'month' : month,
                                                'year': year,
                                                'tod_id': tod_id, 
                                                'start_station_id': start_id, 
                                                'end_station_id': end_id, 
                                                'direction_id': dir_id, 
                                                'hour': hour, 
                                                'min': minute,
                                                'link_load': avg_link_load,
                                                'output': output}, ignore_index=True)
                    d2 = pd.read_csv(path)
                    df = pd.concat([d2, df])
                    df.to_csv(path, index=False)
                    df = pd.DataFrame(columns=['day', 'month', 'year', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load', 'output'])

            print(f'{date} done, time taken: {time.time() - begin}')
        
        