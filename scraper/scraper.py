from tools.api import APIHandler
from data.NUMBAT.linkload import LinkLoadHandler
from typing import Dict, List
import pandas as pd
import time as timee

class Scraper():
    def __init__(self, api_handler : APIHandler):
        self.api = api_handler

    def get_arrivals_time(self, line : str, station_id : str) -> List[Dict[str, str]]:
        """
            Uses the api to get the expected arrival time of the trains at the station with their ids
            returns a list of dictionaries with all the info fo reach train
        """
        answer = self.api.send_get_request(f'https://api.tfl.gov.uk/Line/{line}/Arrivals/{station_id}')
        trains = []
        if len(answer.json()) == 0:
            print(f"No trains found for station {station_id}, line {line}")
            return []
        for _ in range(len(answer.json())):
            date = self.parse_date(answer.json()[_]['expectedArrival'])
            try:
                direction = answer.json()[_]['direction']
            except:
                direction = 'unknown'
                print(f"Direction not found for station {answer.json()[_]['stationName']}, line {line}, destination {answer.json()[_]['destinationName']}")
            trains.append({
                'vehicleId': int(answer.json()[_]['vehicleId']),
                'arrival_year': int(date['year']),
                'arrival_month': int(date['month']),
                'arrival_day': int(date['day']),
                'arrival_hour': int(date['hour']),
                'arrival_min': int(date['min']),
                'arrival_sec': int(date['sec']),
                'direction': direction,
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
    
    def scrap_stations(self, line : str, station_ids: List[str], df : pd.DataFrame) -> None:
        """
        Scrap the data for the given line and stations
        Creates a csv file with the data
        for each line, will contain : the station id and name, line id and name,
        vehicle id, expected arrival time and date, direction, destination id and name, time to station,
        timestanp
        """
 
        for station_id in station_ids:
            try:
                incoming_trains = self.get_arrivals_time(line, station_id)
            except:
                print(f"Error with station {station_id}")
                incoming_trains = []
            for train in incoming_trains:

                #We need to make sure we haven't already added this train
                #So we check the vehicleId and date and time to the hour in the df
                #And if we find it we overwrite it
                #Otherwise we append it
                if len(df[(df['stationId'] == train['stationId']) & (df['vehicleId'] == train['vehicleId']) & (df['arrival_year'] == train['arrival_year']) & (df['arrival_month'] == train['arrival_month']) & (df['arrival_day'] == train['arrival_day']) & (df['arrival_hour'] == train['arrival_hour'])]) > 0:
                    # We overwrite the line
                    index = df[(df['stationId'] == train['stationId']) & (df['vehicleId'] == train['vehicleId']) & (df['arrival_year'] == train['arrival_year']) & (df['arrival_month'] == train['arrival_month']) & (df['arrival_day'] == train['arrival_day']) & (df['arrival_hour'] == train['arrival_hour'])].index[0]
                    for key in train:
                        df.at[index, key] = train[key]
                    print(index, train['vehicleId'])
                else:
                    df = df._append(train, ignore_index=True)
        return df
    
    def scrap_line(self, line: str, df : pd.DataFrame) -> pd.DataFrame:
        """
        Scrap the data for the given line
        Creates a csv file with the data
        for each line, will contain : the station id and name, line id and name,
        vehicle id, expected arrival time and date, direction, destination id and name, time to station,
        timestanp
        """
        stations = self.api.get_ids(line)
        return self.scrap_stations(line, stations, df)

    def continuous_scrap(self, interval_sec, amount, line, path:str = './test_scrap.csv') -> None:
        """
        Scraps continuously for period amount of time
        """
        df = pd.read_csv(path)
        for i in range(amount):
            df = self.scrap_line(line, df)
            df.to_csv(path, index = False)
            print(f"Scrapped {i} times")
            timee.sleep(interval_sec)

    def get_ideal_timetable_from_to(self, from_station_name : str, to_station_name : str, type_of_day:str):
        """
        Returns the ideal timetable for a given station (without delays or anything)
        Theorically, this returns the time of departure for each train, but we can assume 
        that the times of arrival and departure are the same.

        type_of_day : 'MTT', 'SAT', 'SUN', 'FRI'
        """
        from_station_id = self.api.get_id_from_name(from_station_name)
        to_station_id = self.api.get_id_from_name(to_station_name)
        answer = self.api.send_get_request(f'https://api.tfl.gov.uk/Line/central/Timetable/{from_station_id}/to/{to_station_id}').json()
        schedules = answer['timetable']['routes'][0]['schedules']

        # Get the index for the correct day
        if type_of_day == 'SAT':
            day = 'Saturday'
        elif type_of_day == 'SUN':
            day = 'Sunday'
        elif type_of_day == 'FRI':
            day = 'Friday'
        else:
            day = 'Monday'

        for i in range(len(schedules)):
            if day in schedules[i]['name']:
                #print(f"Found the correct day at index {i}")
                break

        #answer['timetable']['routes'][0]['schedules'][i]['name'] is the day (i is the index)
        #answer['timetable']['routes'][0]['schedules'][0]['knownJourneys']

        journeys = schedules[i]['knownJourneys']
        timetables = []
        for journey in journeys:
            timetables.append((int(journey['hour'])%24, int(journey['minute'])))
        timetables.sort()
        return timetables
    
    def get_ideal_timetable_from(self, station_name : str, type_of_day:str, direction:str):
        """
        Returns the ideal timetable for a given station (without delays or anything)
        Theorically, this returns the time of departure for each train, but we can assume 
        that the times of arrival and departure are the same.

        type_of_day : 'MTT', 'SAT', 'SUN', 'FRI'
        """

        station_id = self.api.get_id_from_name(station_name)
        # In case of branching stations, we need all the next consecutive stations
        next_consecutive_stations = LinkLoadHandler().get_next_consecutive_stations(station_name, direction)

        # Lazy way of doing it, we just take the union of all the timetables
        timetable = set()
        for next_station in next_consecutive_stations:
            timetable = timetable.union(set(self.get_ideal_timetable_from_to(station_name, next_station, type_of_day)))
        timetable = list(timetable)
        timetable.sort()
        return timetable
    
    def create_ideal_timetable_df(self, path:str = './ideal_timetable.csv'):
        """
        Creates a dataframe with the ideal timetable for all stations in all directions
        """

        df = pd.DataFrame(columns = ['Type_of_day', 'station_name', 'direction', 'hour_departure', 'min_departure'])
        all_stations = LinkLoadHandler().get_all_stations()
        for station in all_stations:
            for direction in ['EB', 'WB']:
                for type_of_day in ['MTT', 'SAT', 'SUN', 'FRI']:
                    print(f"Scraping {station} {direction} {type_of_day}")
                    n = 50
                    for attempt in range(n):
                        try:
                            timetable = self.get_ideal_timetable_from(station, type_of_day, direction)
                            break
                        except Exception as e:
                            print(f"Attempt {attempt + 1} failed for {station} {direction} {type_of_day}: {e}")
                            timee.sleep(2)
                            
                    for time in timetable:
                        df = df._append({'Type_of_day': type_of_day, 'station_name': station, 'direction': direction, 'hour_departure': time[0], 'min_departure': time[1]}, ignore_index=True)
        df.to_csv(path, index = False)


