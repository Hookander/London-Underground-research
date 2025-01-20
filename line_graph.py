import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as mpatches
from typing import List, Tuple
from tools import *
from scraper import *
from data import *

class LineGraphist():
    """
    This class is used to create a graph of the London Underground Central Line
    """
    def __init__(self):
        self.edges = [
            ("West Ruislip", "Ruislip Gardens"), ("Ruislip Gardens", "South Ruislip"), 
            ("South Ruislip", "Northolt"), ("Northolt", "Greenford"), ("Greenford", "Perivale"), 
            ("Perivale", "Hanger Lane"), ("Hanger Lane", "North Acton"), 
            ("North Acton", "East Acton"), ("East Acton", "White City"), 
            ("White City", "Shepherds Bush"), ("Shepherds Bush", "Holland Park"), 
            ("Holland Park", "Notting Hill Gate"), ("Notting Hill Gate", "Queensway"), 
            ("Queensway", "Lancaster Gate"), ("Lancaster Gate", "Marble Arch"), 
            ("Marble Arch", "Bond Street"), ("Bond Street", "Oxford Circus"), 
            ("Oxford Circus", "Tottenham Court Road"), ("Tottenham Court Road", "Holborn"), 
            ("Holborn", "Chancery Lane"), ("Chancery Lane", "St Pauls"), 
            ("St Pauls", "Bank"), ("Bank", "Liverpool Street"), 
            ("Liverpool Street", "Bethnal Green"), ("Bethnal Green", "Mile End"), 
            ("Mile End", "Stratford"), ("Stratford", "Leyton"), ("Leyton", "Leytonstone"), 
            ("Leytonstone", "Wanstead"), ("Wanstead", "Redbridge"), 
            ("Redbridge", "Gants Hill"), ("Gants Hill", "Newbury Park"), 
            ("Newbury Park", "Barkingside"), ("Barkingside", "Fairlop"), 
            ("Fairlop", "Hainault"), ("Hainault", "Grange Hill"), ("Grange Hill", "Chigwell"), 
            ("Chigwell", "Roding Valley"), ("Roding Valley", "Woodford"), 
            ("Woodford", "South Woodford"), ("South Woodford", "Snaresbrook"), 
            ("Snaresbrook", "Leytonstone"), ("Buckhurst Hill", "Loughton"), 
            ("Loughton", "Debden"), ("Debden", "Theydon Bois"), ("Theydon Bois", "Epping"),
            ("Woodford", "Buckhurst Hill"), ("Ealing Broadway", "West Acton"),
            ("West Acton", "North Acton")
        ]


        # Stations of the main line
        self.line_stations = [
            "West Ruislip", "Ruislip Gardens", "South Ruislip", "Northolt", "Greenford", 
            "Perivale", "Hanger Lane", "North Acton", "East Acton", "White City", 
            "Shepherds Bush", "Holland Park", "Notting Hill Gate", "Queensway", 
            "Lancaster Gate", "Marble Arch", "Bond Street", "Oxford Circus", 
            "Tottenham Court Road", "Holborn", "Chancery Lane", "St Pauls", 
            "Bank", "Liverpool Street", "Bethnal Green", "Mile End", "Stratford", 
            "Leyton", "Leytonstone", "Snaresbrook", "South Woodford", "Woodford",
            "Buckhurst Hill", "Loughton", "Debden", "Theydon Bois", "Epping"
        ]
        # East branch
        self.east_branch = ["Wanstead", "Redbridge", "Gants Hill", "Newbury Park", 
            "Barkingside", "Fairlop", "Hainault", "Grange Hill", "Chigwell", "Roding Valley"
            ]
        # West branch
        self.west_branch = ["Ealing Broadway", "West Acton"]

        self.branch_offset = -1  # Vertical offset for branches
        self.branch_spacing = 0.5  # Horizontal spacing for branches

    def define_positions(self) -> None:
        """
        Definepositions for the stations on the graph
        """
        self.pos = {}

        for i, station in enumerate(self.line_stations):
            self.pos[station] = (i, 0)

        for i, station in enumerate(self.east_branch):
            self.pos[station] = (self.line_stations.index("Leytonstone") + 2 * i * self.branch_spacing, self.branch_offset)

        for i, station in enumerate(self.west_branch):
            self.pos[station] = (self.line_stations.index("West Ruislip") + 2 * i * self.branch_spacing, self.branch_offset)

    def color_from_error(self, error: float) -> str:
        """
        Returns the color based on the percentage error
        """
        if error <=10:
            return 'green'
        elif error <= 20:
            return 'yellow'
        elif error <= 50:
            return 'orange'
        elif error <= 100:
            return 'red'
        else:
            return 'black'

    def get_edges_colors(self, date) -> List:
        """
        Returns the color of the edge based on the error betwwen the real data and the model used to predict the link load
        """
        csvp = CSVProcesser()
        errors = csvp.get_linkload_error_to_daily_mean(date, 'EB')
        colors = {edge: self.color_from_error(error) for edge, error in errors.items()}
        return colors
    
    def draw_graph(self, model_evaluation = True, date : str = '17/09/2019') -> None:
        """
        Draw the graph
        If model_evaluation is True, the edges colors will be based on the error between the real data, 
        and the model used to predict the link load on a given day at a given time (see data/csv_processing.py)
        """
        self.define_positions()
        G = nx.Graph()
        G.add_edges_from(self.edges)
        colors = []
        if model_evaluation:
            edge_colors = self.get_edges_colors(date)
            for edge in G.edges:
                if edge in edge_colors:
                    colors.append(edge_colors[edge])
                elif (edge[1], edge[0]) in edge_colors:
                    colors.append(edge_colors[(edge[1], edge[0])])
                else:
                    colors.append('purple')

        plt.figure(figsize=(15, 8))
        nx.draw_networkx_nodes(G, self.pos, node_size=100, node_color='black')
        nx.draw_networkx_edges(G, self.pos, edge_color=colors, width=2)

        # Add labels with specific positions and rotations for branches
        for station, (x, y) in self.pos.items():
            dx, dy = 0.5, 0.1
            rotation = 45

            plt.text(
                x + dx, y + dy,
                station,
                fontsize=8,
                ha='center',
                va='center',
                rotation=rotation,
                rotation_mode='anchor'
            )

        plt.axis("off")
        # Create a legend for the colors
        legend_labels = {
            'green': '0-10% error',
            'yellow': '10-20% error',
            'orange': '20-50% error',
            'red': '50-100% error',
            'black': '>100% error',
            'purple': 'No data'
        }

        patches = [mpatches.Patch(color=color, label=label) for color, label in legend_labels.items()]
        plt.legend(handles=patches)
        plt.show()

        

lg = LineGraphist()
lg.draw_graph(model_evaluation=True)
