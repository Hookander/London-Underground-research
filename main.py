from tools import *
from scraper import *
from data import *
from model import *
import pandas as pd
import time

print("Starting...")
#csvp = CSVProcesser()
#csvp.plot_dist_to_daily_mean('17/09/2019', 'WB')
#tth = TimetablesHandler()
#tth.plot_delays('Woodford', 'WB', 'SUN', n_bins=50,plot = 'Parzen', interval = None)
#llh = LinkLoadHandler()
#y = [llh.get_avg_link_load('Notting Hill Gate', 'Queensway', t, 'SUN', '2019') for t in range(0, 2345, 15)]
#x = [t for t in range(0, 2345, 15)]
#plt.plot(x, y)
#plt.xlabel('Time of the day')
#plt.ylabel('Link load')
#plt.title('Link load between Notting Hill Gate and Queensway on a Sunday in 2019')
#plt.show()
#day = '17/09/2019'
model = Model(10)
model.train(epochs=50, lr=0.001)
model.test()
#df = model.create_data('2019', 'data/model_data/2019_data_no_taps.csv')
#dataset = CustomUndergroundDataset()
#print(dataset.train_data)
#df = pd.read_csv('data/model_data/2019_data_no_taps.csv') 
#print(df.tail(1))
#csvp = CSVProcesser()
#day = '03/08/2023'
#df = csvp.flow_time_day_csv(day)
#df.to_csv('data/precise_ll/flow_time_day.csv', index=False)
#print(csvp.flow_time_day('Notting Hill Gate', 'Queensway', 'EB', day, '0800'))
#print(day, get_day_of_week(day))
#print(csvp.get_linkload_error_to_daily_mean(day, 'WB'))
#csvp.plot_dist_to_daily_mean(day, 'WB')


#df = pd.read_csv('./data/scraped_timetables.csv', encoding='utf-8', on_bad_lines='skip', sep=',')
#print("Starting...")
#scrapy = Scraper(APIHandler())
#scrapy.continuous_scrap(600, 200, 'central', path='./data/scraped_timetables.csv')
#df = scrapy.scrap_line('central', df)
#df.to_csv('./data/scraped_timetables.csv', index=False)

#scrapy.create_ideal_timetable_df()
#print(scrapy.get_ideal_timetable_from('Woodford', 'MTT', 'WB'))


#handler = TimetablesHandler()
#print(handler.get_delay_s((12, 34, 15), 'Woodford', 'WB', 'MTT'))
# print(handler.get_station_delay('Woodford', 'WB', 'MTT'))
#handler.plot_delays('Woodford', 'EB', 'SUN', n_bins=50,plot = 'Parzen', interval = None)
