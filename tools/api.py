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
    
    def get_id_from_name(self, name: str) -> str:
        """
        Get the station id from the station name
        """
        answer = self.send_get_request(f'https://api.tfl.gov.uk/StopPoint/Search/{name}?lines=central&modes=tube&includeHubs=false')
        return answer.json()['matches'][0]['id']

api = APIHandler()
print(api.get_id_from_name("Shepherd's Bush"))