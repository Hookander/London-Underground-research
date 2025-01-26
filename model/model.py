import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from data import *
from model.model_class import ModelClass
from model.data_handler import CustomUndergroundDataset
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, Dataset
import wandb




class Model(ModelClass):
    """
    This is the is the simplest model we try, just a bunch of linear layers
    """
    def __init__(self, embedding_dim, scale_data = True):
        super().__init__()

        self.embedding_dim = embedding_dim
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.scaler = None
        if scale_data:
            self.scaler = StandardScaler()
        
        train_dataset = CustomUndergroundDataset()
        train_dataset.prep_data(['2019', '2020', '2021'], 'train', self.scaler)
        self.train_dl = DataLoader(train_dataset, batch_size=1, shuffle=True)

        test_dataset = CustomUndergroundDataset()
        test_dataset.prep_data(['2022'], 'test', self.scaler)
        self.test_dl = DataLoader(test_dataset, batch_size=1, shuffle=True)


        # 49 stations
        self.station_embedding = nn.Embedding(49, self.embedding_dim)
        self.tod_embedding = nn.Embedding(4, 4) # 4 types of days, don't need a big embedding
        self.model = nn.Sequential(
            nn.LazyLinear(128),
            nn.ReLU(),
            nn.LazyLinear(64),
            nn.ReLU(),
            nn.LazyLinear(32),
            nn.ReLU(),
            nn.LazyLinear(16),
            nn.ReLU(),
            nn.LazyLinear(1)
        )
        self.to(self.device)
        wandb.init(project='underground_research', entity='underground', name='simple_model')

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
        try: # the df already exists
            df = pd.read_csv(path)
            # get the last date in dd/mm/yyyy format
            last_date = df.iloc[-1][['day', 'month', 'year']].values
            last_date = '/'.join([str(int(x)) for x in last_date])

            # We start the next day
            start_date = get_next_date(last_date)
            df = pd.DataFrame(columns=['day', 'month', 'year', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load', 'output'])
            print(f'Starting from {start_date}')

        except:
            print('Creating new file')
            df = pd.DataFrame(columns=['day', 'month', 'year', 'tod_id', 'start_station_id', 'end_station_id', 'direction_id', 'hour', 'min', 'link_load', 'output'])
            df.to_csv(path, index=False)
            start_date = '01/01' + year
        stations = self.llh.get_all_stations()
        directions = ['EB', 'WB']
        ntods_per_year = nb_days_per_tod(year)
        dates = get_dates_between(start_date, '31/12/'+year)
        for date in dates:
            print(date)
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
                                # Check it has not been done already
                                if len(df[(df['day'] == day) & (df['month'] == month) & (df['year'] == year) & (df['tod_id'] == tod_id) & (df['start_station_id'] == start_id) & (df['end_station_id'] == end_id) & (df['direction_id'] == dir_id) & (df['hour'] == hour) & (df['min'] == minute)]) > 0:
                                    continue
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
    
    def forward(self, continuous_inputs, embedding_inputs):

        #print(continuous_inputs.shape)
        embedded = [self.tod_embedding(embedding_inputs[:, 0]),
                    self.station_embedding(embedding_inputs[:, 1]),
                    self.station_embedding(embedding_inputs[:, 2])]
        embedded = torch.cat(embedded, dim=1)  # Shape : [batch_size, sum(embedding_dims)]


        x = torch.cat([continuous_inputs, embedded], dim=1)  # Shape : [batch_size, continuous_input_size + sum(embedding_dims)]
        
        return self.model(x)

    def train(self, lr, epochs):
        """
        2019 to 2021 for training
        2022 for testing
        """
        self.lr = lr
        self.epochs = epochs
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.parameters(), lr=self.lr)

        for epoch in range(epochs):
            for batch in self.train_dl:
                #print(batch)
                continuous_inputs, embedding_inputs, label = batch

                # De batch to tensor because our batch is of size 365
                continuous_inputs = continuous_inputs[0]
                embedding_inputs = embedding_inputs[0]
                label = label[0]

                continuous_inputs = continuous_inputs.to(self.device)
                embedding_inputs = embedding_inputs.to(self.device)

                label = label.to(self.device)
                self.optimizer.zero_grad()
                output = self.forward(continuous_inputs, embedding_inputs).sum()
                #print(output.shape)
                #print("FORWARD DONE")
                loss = self.criterion(output, label)
                wandb.log({'train_loss': loss.item()})
                loss.backward()
                self.optimizer.step()
            print(f'Epoch {epoch} done, loss: {loss.item()}')
        torch.save(self.state_dict(), "model/models/model.pth")
        print('Model saved')
        
    def test(self):
        for batch in self.train_dl:
            #print(batch)
            continuous_inputs, embedding_inputs, label = batch

            # De batch to tensor because our batch is of size 365
            continuous_inputs = continuous_inputs[0]
            embedding_inputs = embedding_inputs[0]
            label = label[0]

            continuous_inputs = continuous_inputs.to(self.device)
            embedding_inputs = embedding_inputs.to(self.device)

            label = label.to(self.device)
            self.optimizer.zero_grad()
            output = self.forward(continuous_inputs, embedding_inputs).sum()
            loss = self.criterion(output, label)
            wandb.log({'test_loss': loss.item()})
            print(loss.item())







        