from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
from events import WeatherHandler
import time

print("Starting...")

wh = WeatherHandler()
#print(wh.station_weather_influence('Queensway', '01/01/2019', '31/12/2019'))
#print(wh.get_best_threshold('Queensway', '01/01/2019', '31/12/2019'))
wh.plot_best_thresholds('01/01/2019', '31/12/2019')
#wh.plot_threshold_influence('Queensway', '01/01/2019', '31/12/2019')
