from tools import *
from scraper import *
from data import *
import pandas as pd
import time


#csvp = CSVProcesser()
#day = '17/09/2019'
#print(day, get_day_of_week(day))
#print(csvp.get_linkload_error_to_daily_mean(day, 'WB'))
#csvp.plot_dist_to_daily_mean(day, 'WB')

#scrappy = Scraper(APIHandler())
#scrappy.create_ideal_timetable_df()
#print(scrappy.get_ideal_timetable_from('Woodford', 'MTT', 'WB'))


handler = TimetablesHandler()
#print(handler.get_delay_s((12, 34, 15), 'Woodford', 'WB', 'MTT'))
print(handler.get_station_delay('Woodford', 'WB', 'MTT'))
handler.plot_delays('Notting Hill Gate', 'EB', 'MTT')
