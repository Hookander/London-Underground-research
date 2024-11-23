import pandas as pd

class TimetablesHandler():
    def __init__(self, path):
        self.df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip', sep=',')

    def get_times(self, arg_dict):
        """
            Returns the times for the given arguments
        """
        filtered_df = self.df
        for key, value in arg_dict.items():
            filtered_df = filtered_df[filtered_df[key] == value]
        # Sort the results by timestamp
        filtered_df = filtered_df.sort_values(by=['arrival_year', 'arrival_month', 'arrival_day', 'arrival_hour', 'arrival_min', 'arrival_sec'])
        return filtered_df[['vehicleId', 'direction', 'stationName', 'arrival_hour', 'arrival_min', 'arrival_sec']]

#handler = TimetablesHandler('./test_scrap.csv')
#print(handler.get_times({'vehicleId': 54, 'arrival_day' : 20, 'direction' : 'inbound'}))