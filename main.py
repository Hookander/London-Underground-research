from tools import *
from scraper import *
from data import *
import pandas as pd
import time


csvp = CSVProcesser()
day = '17/09/2019'
print(day, get_day_of_week(day))
csvp.plot_dist_to_daily_mean(day, 'WB')