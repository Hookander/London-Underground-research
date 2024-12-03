from tools import *
from scraper import *
from data import *
import pandas as pd
import time

csvp = CSVProcesser()
begin = time.time()
print(csvp.get_daily_estimated_link_load('Notting Hill Gate', 'Queensway', '01/01/2019', 'EB'))
print(time.time()-begin)