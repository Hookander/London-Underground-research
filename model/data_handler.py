import os
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from data import *
from sklearn.preprocessing import StandardScaler
from model.model_class import ModelClass
from torch.utils.data import DataLoader, Dataset

class CustomUndergroundDataset(Dataset):
    def __init__(self):
        self.inputs = []
        self.embedding_inputs = []
        self.outputs = []
        

    def prep_data(self, years : List[str], mode: str, scaler = None|StandardScaler) -> None:
        """
        # We do the back prop on the sum over the year of the output for each quarter of an hour
        # So we group together the data by the input for 1 output
        # We ll have 365 inputs for 1 output
        + we are using embeddings for the stations (for now the same embedding for the start and end station)
        args:
        - years : list of years to use
        - mode : 'train' or 'test' (useful for the scaler)
        - scaler : if we want to scale the output then StandardScaler object
        """

        for year in years:
            assert year in ['2019', '2020', '2021', '2022'], 'Invalid year'
            df = pd.read_csv(f'data/model_data/{year}_data_no_taps.csv')

            # Feature engineering : ajout des colonnes cos/sin
            df['groupby'] = df['hour'].astype(str) + df['min'].astype(str) + df['start_station_id'].astype(str) + df['end_station_id'].astype(str)
            df['cos_day'] = np.cos(2 * np.pi * df['day'] / 365)
            df['sin_day'] = np.sin(2 * np.pi * df['day'] / 365)
            df['cos_month'] = np.cos(2 * np.pi * df['month'] / 12)
            df['sin_month'] = np.sin(2 * np.pi * df['month'] / 12)
            df['cos_hour'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['sin_hour'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['cos_min'] = np.cos(2 * np.pi * df['min'] / 60)
            df['sin_min'] = np.sin(2 * np.pi * df['min'] / 60)

            # Boucle sur chaque quaterhour
            for groupby, group in df.groupby('groupby'):
                continuous_inputs = group[['cos_day', 
                                           'sin_day', 
                                           'cos_month', 
                                           'sin_month',
                                           'cos_hour',
                                           'sin_hour',
                                           'cos_min',
                                           'sin_min']].values.astype(np.float32)
                

                embedding_inputs = group[['tod_id', 'start_station_id', 'end_station_id']].values.astype(np.int64)
                
                # Output
                output = group['output'].values[0].astype(np.float32)

                # Stockage (as batch of 365)
                self.inputs.append(torch.tensor(continuous_inputs))
                self.embedding_inputs.append(torch.tensor(embedding_inputs))
                self.outputs.append(torch.tensor(output))
        self.outputs = np.array(self.outputs)
        if scaler is not None:
            if mode == 'train':
                print(f'Scaling output for {mode}')
                self.outputs = scaler.fit_transform(self.outputs.reshape(-1, 1)).flatten()
            else:
                print(f'Scaling output for {mode}')
                self.outputs = scaler.transform(self.outputs.reshape(-1, 1)).flatten()

    def __len__(self):
        return len(self.outputs)
    
    def __getitem__(self, idx):
        return self.inputs[idx], self.embedding_inputs[idx], self.outputs[idx]


        

    