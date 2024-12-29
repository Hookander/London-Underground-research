import matplotlib.pyplot as plt
import networkx as nx

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
            ("White City", "Shepherd's Bush"), ("Shepherd's Bush", "Holland Park"), 
            ("Holland Park", "Notting Hill Gate"), ("Notting Hill Gate", "Queensway"), 
            ("Queensway", "Lancaster Gate"), ("Lancaster Gate", "Marble Arch"), 
            ("Marble Arch", "Bond Street"), ("Bond Street", "Oxford Circus"), 
            ("Oxford Circus", "Tottenham Court Road"), ("Tottenham Court Road", "Holborn"), 
            ("Holborn", "Chancery Lane"), ("Chancery Lane", "St. Paul's"), 
            ("St. Paul's", "Bank"), ("Bank", "Liverpool Street"), 
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
            "Shepherd's Bush", "Holland Park", "Notting Hill Gate", "Queensway", 
            "Lancaster Gate", "Marble Arch", "Bond Street", "Oxford Circus", 
            "Tottenham Court Road", "Holborn", "Chancery Lane", "St. Paul's", 
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

    def get_edge_color(self, value: int) -> str:
        """
        Returns the color of the edge based on the value
        """
        colors = ['red', 'orange', 'yellow', 'green', 'blue']
        return colors[value]
    
    def draw_graph(self) -> None:
        """
        Draw the graph
        """
        self.define_positions()
        G = nx.Graph()
        G.add_edges_from(self.edges)

        edge_values = {edge: i % 5 for i, edge in enumerate(G.edges)}

        edge_colors = [self.get_edge_color(edge_values[edge]) for edge in G.edges]

        plt.figure(figsize=(15, 8))
        nx.draw_networkx_nodes(G, self.pos, node_size=100, node_color='black')
        nx.draw_networkx_edges(G, self.pos, edge_color=edge_colors, width=2)

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
        plt.show()

lg = LineGraphist()
lg.draw_graph()
