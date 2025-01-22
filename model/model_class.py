import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from data import *

class ModelClass(nn.Module):
    def __init__(self):
        super().__init__()
        
        self.csvp = CSVProcesser()
        self.llh = LinkLoadHandler()
    
    def type_of_day_to_int(self, type_of_day: str) -> int:
        """
        Returns the type of day as an integer
        """
        match type_of_day:
            case 'MTT':
                return 0
            case 'FRI':
                return 1
            case 'SAT':
                return 2
            case 'SUN':
                return 3
            case _:
                raise ValueError('Invalid type of day')
    
    def station_to_int(self, station: str) -> int:
        """
        Returns the station as an integer
        """
        stations = self.llh.get_all_stations()
        for i, s in enumerate(stations):
            if s == station:
                return i
        raise ValueError('Invalid station')

    def tod_to_int(self, tod: str) -> int:
        """
        Returns the time of day as an integer
        """
        if tod == 'MTT':
            return 0
        elif tod == 'FRI':
            return 1
        elif tod == 'SAT':
            return 2
        elif tod == 'SUN':
            return 3
        raise ValueError('Invalid type of day')
    
    def direction_to_int(self, direction: str) -> int:
        """
        Returns the direction as an integer
        """
        if direction == 'EB':
            return 0
        elif direction == 'WB':
            return 1
        raise ValueError('Invalid direction')