from tools import *
from scraper import *
from data import *
import pandas as pd
import time


csvp = CSVProcesser()
day = '17/09/2019'
print(day, get_day_of_week(day))
print(csvp.get_linkload_error_to_daily_mean(day, 'WB'))
#csvp.plot_dist_to_daily_mean(day, 'WB')