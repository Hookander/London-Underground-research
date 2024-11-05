from api import APIHandler
from typing import Dict, List
import pandas as pd

class scraper():
    def __init__(self, api_handler : APIHandler):
        self.api = api_handler

    def get_arrivals_time(self, line : str, station_id : str) -> List[Dict[str, str]]:
        """
            Uses the api to get the expected arrival time of the trains at the station with their ids
            returns a list of dictionaries with all the info fo reach train
        """
        answer = self.api.send_get_request(f'https://api.tfl.gov.uk/Line/{line}/Arrivals/{station_id}')
        trains = []
        for _ in range(len(answer.json())):
            date = self.parse_date(answer.json()[_]['expectedArrival'])
            trains.append({
                'vehicleId': int(answer.json()[_]['vehicleId']),
                'arrival_year': int(date['year']),
                'arrival_month': int(date['month']),
                'arrival_day': int(date['day']),
                'arrival_hour': int(date['hour']),
                'arrival_min': int(date['min']),
                'arrival_sec': int(date['sec']),
                'direction': answer.json()[_]['direction'],
                'destinationId': answer.json()[_]['destinationNaptanId'],
                'destinationName': answer.json()[_]['destinationName'],
                'timeToStation': answer.json()[_]['timeToStation'],
                'timestamp': answer.json()[_]['timestamp'],
                'stationId': answer.json()[_]['naptanId'],
                'stationName': answer.json()[_]['stationName'],
                'lineName': answer.json()[_]['lineName'],
                'lineId': answer.json()[_]['lineId'],
                'expectedArrival': answer.json()[_]['expectedArrival'],
            })
        
        return trains
    
    def parse_date(self, date : str):
        """
        Parses for example 2024-11-04T23:29:54Z to 23:29:54
        """
        year, month, day = date.split('T')[0].split('-')
        hour, mins, sec = date.split('T')[1].split('Z')[0].split(':')

        return {'year': year, 'month': month, 'day': day, 'hour' : hour, 'min': mins, 'sec': sec} 
    
    def scrap(self, line : str, station_ids: List[str], df : pd.DataFrame) -> None:
        """
        Scrap the data for the given line and stations
        Creates a csv file with the data
        for each line, will contain : the station id and name, line id and name,
        vehicle id, expected arrival time and date, direction, destination id and name, time to station,
        timestanp
        """
 
        for station_id in station_ids:
            incoming_trains = self.get_arrivals_time(line, station_id)
            print(len(incoming_trains))
            for train in incoming_trains:

                #We need to make sure we haven't already added this train
                #So we check the vehicleId and date and time to the hour in the df
                #And if we find it we overwrite it
                #Otherwise we append it
                if len(df[(df['vehicleId'] == train['vehicleId']) & (df['arrival_year'] == train['arrival_year']) & (df['arrival_month'] == train['arrival_month']) & (df['arrival_day'] == train['arrival_day']) & (df['arrival_hour'] == train['arrival_hour'])]) > 0:
                    # We overwrite the line
                    index = df[(df['vehicleId'] == train['vehicleId']) & (df['arrival_year'] == train['arrival_year']) & (df['arrival_month'] == train['arrival_month']) & (df['arrival_day'] == train['arrival_day']) & (df['arrival_hour'] == train['arrival_hour'])].index[0]
                    for key in train:
                        df.at[index, key] = train[key]
                    print(index, train['vehicleId'])
                else:
                    df = df._append(train, ignore_index=True)
        return df


scrapy = scraper(APIHandler())
df = pd.DataFrame(columns=[
            'vehicleId', 'arrival_year', 'arrival_month', 'arrival_day', 'arrival_hour', 'arrival_min', 'arrival_sec',
            'direction', 'destinationId', 'destinationName', 'timeToStation', 'timestamp', 'stationId', 'stationName',
            'lineName', 'lineId', 'expectedArrival'
        ])
df = pd.read_csv('./test_scrap.csv')
df = scrapy.scrap('central', ['940GZZLUNAN'], df)
df.to_csv('./test_scrap.csv', index = False)
