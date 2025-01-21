import torch
import torch.nn as nn
import pandas as pd
import numpy as np

class ModelClass(nn.Module):
    def __init__(self, name):
        super().__init__()
        self.fc = nn.Linear(1, 1)
    
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
    