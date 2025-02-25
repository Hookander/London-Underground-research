from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Stations, Daily, Point

ICL = Point(51.499439, -0.174329) # ICL
THRESHOLD = 0.5 # rains if precipitations > THRESHOLD

start = datetime(2019, 1, 1)
end = datetime(2019, 12, 31)
precipitations = Daily(ICL, start, end)
precipitations = precipitations.fetch()
rainy_days = precipitations[precipitations['prcp'] >= THRESHOLD].index
rainy_days = [date.strftime('%d/%m/%Y') for date in rainy_days]
dry_days = precipitations[precipitations['prcp'] < THRESHOLD].index
dry_days = [date.strftime('%d/%m/%Y') for date in dry_days]

llh = LinkLoadHandler()
taps = tapsHandler()



# For now we only study the daily correlation with the avg entries
all_stations = llh.get_all_stations()
dry_avg_stations = []
rainy_avg_stations = []
for station in all_stations[15:30]:
    dry_avg = 0
    rainy_avg = 0
    for date in dry_days:
        dry_avg += taps.get_entries_exits(station, date)['entries']
    dry_avg /= len(dry_days)
    for date in rainy_days:
        rainy_avg += taps.get_entries_exits(station, date)['entries']
    rainy_avg /= len(rainy_days)
    dry_avg_stations.append(dry_avg)
    rainy_avg_stations.append(rainy_avg)
    print(f'{station} : dry avg = {dry_avg}, rainy avg = {rainy_avg}')
ind_stations = [i for i in range(len(all_stations))]
plt.bar(all_stations[15:30], dry_avg_stations, color='b', label='Dry days')
plt.bar(all_stations[15:30], rainy_avg_stations, color='r', label='Rainy days')
plt.xlabel('Station')
plt.ylabel('Avg entries')
plt.title('Avg entries for dry and rainy days')
plt.legend()
plt.show()

