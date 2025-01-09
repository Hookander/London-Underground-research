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

#df = pd.read_csv('./data/scraped_timetables.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
#scrapy = Scraper(APIHandler())
#df = scrapy.scrap_line('central', df)
#df.to_csv('./data/scraped_timetables.csv', index=False)

#scrapy.create_ideal_timetable_df()
#print(scrapy.get_ideal_timetable_from('Woodford', 'MTT', 'WB'))


handler = TimetablesHandler()
#print(handler.get_delay_s((12, 34, 15), 'Woodford', 'WB', 'MTT'))
# print(handler.get_station_delay('Woodford', 'WB', 'MTT'))
handler.plot_delays('Woodford', 'EB', 'SUN')
