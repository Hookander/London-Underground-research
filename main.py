from tools import *
from scraper import *
from data import *
import pandas as pd
import time

csvp = CSVProcesser()
day = '01/04/2019'
print(day, get_day_of_week(day))
stations = csvp.LinkLoadHandler.get_all_stations()
percents = []
for station in stations[:-1]:
    begin = time.time()
    next_s = csvp.LinkLoadHandler.get_inbetween_stations('EB', start_station = station)[1]
    daily_ll = csvp.LinkLoadHandler.get_avg_daily_link_load(station, next_s, 'MTT')
    estimated_flow = csvp.estimate_flow_between_stations(station, next_s, day, 'EB')
    percent = abs(estimated_flow - daily_ll) / daily_ll * 100 
    percents.append(percent)
    print(f"Station: {station}, Next Station: {next_s}, Avg Daily Link Load: {daily_ll}, Estimated Flow: {estimated_flow}, Percent Error: {percent}, Time: {time.time()-begin}")
print(f"Average Percent Error: {sum(percents)/len(percents)}")