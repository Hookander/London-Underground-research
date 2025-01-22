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

    def create_data(self):
        """
        Create the csv file for training wioth the following columns:
        - day
        - month_cos
        - month_sin -> to take into account the cyclical nature of the months (dec is close to jan)
        - tod_id
        - start_station_id
        - end_station_id
        - direction_id
        - hour
        - min (0, 15, 30 or 45), we are only interested in the quarter of the hour

        - taps ? We start without the taps

        - link_load for the output of the model

        2019-2022 : training
        2023 : testing
        """
        df = pd.DataFrame(columns=['day', 'month', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load'])
        df.to_csv(f'data/model_data/data_no_taps.csv', index=False)
        stations = self.llh.get_all_stations()
        directions = ['EB', 'WB']

        ntods_per_year = {}
        for year in range(2019, 2024):
            ntods_per_year[str(year)] = nb_days_per_tod(str(year))
        for iyear in range(2019, 2023):
            ll_dict = {}
            year = str(iyear)
            for date in get_dates_between('01/01/'+year, '31/12/'+year):
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

                                for min in [0, 15, 30, 45]:
                                    quarter_hour = str(hour).zfill(2) + str(min).zfill(2)
                                    avg_link_load = self.llh.get_avg_link_load(start_station, end_station, quarter_hour, type_of_day, year)
                                    output = avg_link_load * ntods_per_year[year][type_of_day]
                                    df = df._append({'day': day, 
                                                        'month' : month,
                                                        'tod_id': tod_id, 
                                                        'start_station_id': start_id, 
                                                        'end_station_id': end_id, 
                                                        'direction_id': dir_id, 
                                                        'hour': hour, 
                                                        'min': min, 
                                                        'output': output}, ignore_index=True)
                        d2 = pd.read_csv(f'data/model_data/data_no_taps.csv')
                        df = pd.concat([d2, df])
                        df.to_csv(f'data/model_data/data_no_taps.csv', index=False)
                        df = pd.DataFrame(columns=['day', 'month', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load'])

                print(f'{date} done, time taken: {time.time() - begin}')

        return df