import requests
from typing import List

class APIHandler:
    def __init__(self):
        self.data = []

    def send_get_request(self, url : str):
        x = requests.get(url)
        return x
    
    def get_ids(self, line: str) -> List[str]:
        """
        Get the station ids of the line
        """
        answer = self.send_get_request(f'https://api.tfl.gov.uk/Line/{line}/StopPoints')
        return [station['naptanId'] for station in answer.json()]
    