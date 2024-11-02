
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data/NUMBAT/2016/NBT16MTT/Outputs.csv', encoding='utf-8', on_bad_lines='skip', sep=';', skiprows=2)


class CSVHandler():
    def __init__(self, path):
        self.df = pd.read_csv(path, encoding='utf-8', on_bad_lines='skip', sep=';', skiprows=2)
    
    def plot_load_between_stations(self, line, from_nlc, to_nlc):
        filtered_df = self.df[(self.df['Line'] == line) & (self.df['From NLC'] == from_nlc) & (self.df['To NLC'] == to_nlc)]
        time_columns = self.df.columns[self.df.columns.get_loc('0500-0515'):]
        filtered_df = filtered_df[time_columns]

        
        plt.plot([_ for _ in range(len(time_columns))], filtered_df.values[0])
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title(f'Load from {from_nlc} to {to_nlc} on line {line}')
        plt.legend([f'Load from {from_nlc} to {to_nlc}'])
        plt.show()
    
    def plot_load_line(self, line : str, time: str, direction : str):
        filtered_df = self.df[(self.df['Line'] == line) & (self.df['Dir'] == direction)]
        time_columns = self.df.columns[self.df.columns.get_loc(time)]
        filtered_df = filtered_df[time_columns]
        
        plt.plot([_ for _ in range(len(filtered_df))], filtered_df)
        plt.xlabel('Time')
        plt.ylabel('Load')
        plt.title(f'Load on line {line} at {time}, direction {direction}')
        plt.legend([f'Load on line {line} at {time}'])
        plt.show()

        

handler = CSVHandler('data/NUMBAT/2016/NBT16MTT/Outputs.csv')
handler.plot_load_line('Bakerloo', '0500-0515', 'NB')