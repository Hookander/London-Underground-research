import requests

class APIHandler:
    def __init__(self):
        self.data = []

    def send_get_request(self, url : str):
        x = requests.get(url)
        return x
    