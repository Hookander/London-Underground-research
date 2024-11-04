from api import APIHandler
from typing import Dict

class scraper():
    def __init__(self, api_handler : APIHandler):
        self.api = api_handler

    def get_arrivals_time(self, line : str, station_id : str) -> Dict[str, str]:
        """
            Uses the api to get the expected arrival time of the trains at the station with their ids
        """
        answer = self.api.send_get_request(f'https://api.tfl.gov.uk/Line/{line}/Arrivals/{station_id}')
        return {answer.json()[_]['vehicleId']: answer.json()[_]['expectedArrival'] for _ in range(len(answer.json()))}
        
    def parse_date(self, date : str):
        """
        Parses for example 2024-11-04T23:29:54Z to 23:29:54
        """
        year, month, day = date.split('T')[0].split('-')
        time = date.split('T')[1].split('Z')[0]

        return {'year': year, 'month': month, 'day': day, 'time': time} 

scrapy = scraper(APIHandler())
print(scrapy.get_arrivals_time('central', '940GZZLUBNK'))
print(scrapy.parse_date('2024-11-04T23:29:54Z'))