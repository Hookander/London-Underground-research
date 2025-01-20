import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from data import *



class Model(nn.Module):
    """
    This is the is the simplest model we try, just a bunch of linear layers
    """
    def __init__(self):
        super(Model, self).__init__()
        self.fc = nn.Linear(1, 1)

    def create_data(self):
        """
        Create the csv file for training wioth the following columns:
        - day
        - start_station
        - end_station
        - direction
        - hour
        - min (0, 15, 30 or 45), we are only interested in the quarter of the hour
        - time elapsed since the previous train
        - link_load for the output of the model
        """
        df = pd.DataFrame(columns=['day', 'start_station', 'end_station', 'direction', 'hour', 'min', 'time_elapsed', 'link_load'])
        csv_processor = CSVProcesser()


