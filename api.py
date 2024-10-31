

class APIHandler:
    def __init__(self):
        self.data = []

    def get_data(self):
        return self.data

    def add_data(self, data):
        self.data.append(data)