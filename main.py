from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
from events import *
import time
import requests


print("Starting...")

wh = WeatherHandler()
#wh.plot_best_theshold_evolution('Queensway')
#wh.plot_diff_rainy_days('01/01/2019', '31/01/2019', test=True)
#print(wh.station_weather_influence('Queensway', '01/01/2019', '31/12/2021'))
#print(wh.get_best_threshold('Queensway', '01/01/2019', '31/12/2019'))
#wh.plot_best_thresholds('01/01/2019', '31/12/2019')
#wh.get_threshold_influence('Holborn', '01/01/2022', '31/12/2022', relative=True, plot=True)
#wh.plot_threshold_influence_evolution('Holborn', 'exits', precision=1)
#wh.plot_best_thresholds('01/01/2019', '31/12/2019', test=True, all_years=True)
llh = LinkLoadHandler()
print(llh.get_avg_link_load('Queensway', 'Lancaster Gate', '0800', 'MTT', '2019'))
#fb = FootballData()

#fb.plot_match_influence('01/01/2019', '31/12/2019')
#print(fb.get_match_influence('Stratford', '01/01/2022', '31/12/2022'))
#fb.plot_match_influence('01/01/2023', '31/12/2023')