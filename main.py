from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
from events import *
import time
import requests


print("Starting...")

#wh = WeatherHandler()
#wh.plot_diff_rainy_days('01/01/2019', '31/01/2019', test=True)
#print(wh.station_weather_influence('Queensway', '01/01/2019', '31/12/2019'))
#print(wh.get_best_threshold('Queensway', '01/01/2019', '31/12/2019'))
#wh.plot_best_thresholds('01/01/2019', '31/12/2019')
#wh.plot_threshold_influence('Queensway', '01/01/2019', '31/12/2019')
#wh.plot_best_thresholds('01/01/2019', '31/12/2019', test=True)

fb = FootballData()
#print(fb.get_closest_team('Stratford'))
#print(fb.get_match_influence('Stratford', '01/01/2022', '31/12/2022'))
fb.plot_match_influence('01/01/2019', '31/12/2023')