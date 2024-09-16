import sys
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtCore import QPointF
from pymongo import MongoClient
from db_management import start_background_fetching
# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_recommendation']
movies_collection = db['movies']

# Class for hover and click interaction
class HoverNode(pg.ScatterPlotItem):
    def __init__(self, pos, size, color, details):
        super().__init__(pos=[pos], size=size, brush=pg.mkBrush(color))
        self.details = details
        self.setAcceptHoverEvents(True)

    def hoverEvent(self, event):
        if event.isExit():
            QToolTip.hideText()
            self.setBrush(pg.mkBrush((255, 255, 255)))  # Reset color when hover exits
        else:
            # Convert screen position to QPoint for QToolTip
            pos = event.screenPos().toPoint()  # Convert QPointF to QPoint
            QToolTip.showText(pos, self.details)
            self.setBrush(pg.mkBrush((255, 0, 0)))  # Highlight color on hover

    def mouseClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            # Show details on click
            QToolTip.showText(event.screenPos().toPoint(), self.details)

class MovieGraphApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MovieGraphApp, self).__init__()
        self.setWindowTitle('Movie Recommendation Mind Map')
        self.setGeometry(100, 100, 800, 600)

        # Create graph widget
        self.view = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.view)
        self.plot = self.view.addPlot()
        self.plot.setAspectLocked()

        # Graph data
        self.node_positions = []
        self.node_colors = []
        self.node_sizes = []
        self.node_labels = []
        self.adjacency_list = []

        # Timer for updates
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_graph)
        self.timer.start(10000)  # Update graph every 10 seconds

        # Initialize the graph with current database entries
        self.init_graph()

    def init_graph(self):
        self.movie_nodes = {}  # Store movies by TMDB ID
        self.node_positions = []  # List of node positions
        self.adjacency_list = []  # Adjacency for edges

        # Fetch movies from the database
        movies = list(movies_collection.find())
        for movie in movies:
            self.add_movie_node(movie)  # Add each movie as a node
            for similar in movie.get('similar_movies', []):
                self.add_movie_edge(movie['tmdb_id'], similar['tmdb_id'])

        # Display the graph
        self.update_graph_display()

    def add_movie_node(self, movie):
        pos = (np.random.random(), np.random.random())
        size = 10
        color = (np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255))
        details = f"Title: {movie['title']}\nOverview: {movie['overview']}\nRating: {movie.get('rating', 'N/A')}\nRuntime: {movie['runtime']} mins"
        
        node_index = len(self.node_positions)
        self.node_positions.append(pos)
        self.node_colors.append(color)
        self.node_sizes.append(size)
        self.node_labels.append(movie['title'])
        
        hover_node = HoverNode(pos, size, color, details)
        self.plot.addItem(hover_node)

    def add_movie_edge(self, source_id, target_id):
        # Add an edge if both source and target nodes exist
        if source_id in self.movie_nodes and target_id in self.movie_nodes:
            source_index = self.movie_nodes[source_id]
            target_index = self.movie_nodes[target_id]
            self.adjacency_list.append((source_index, target_index))

    def update_graph_display(self):
        # Prepare adjacency list and node positions for rendering
        if self.adjacency_list:
            adj_array = np.array(self.adjacency_list, dtype=int)
        else:
            adj_array = np.array([])

        # Convert node positions for pyqtgraph
        pos_array = np.array(self.node_positions)

        # Draw graph edges (edges are white lines)
        edge_pen = pg.mkPen(width=2, color='w')
        self.graph_lines = pg.GraphItem()
        self.graph_lines.setData(pos=pos_array, adj=adj_array, pen=edge_pen, symbolBrush=None)
        self.plot.addItem(self.graph_lines)

    def update_graph(self):
        # Periodically fetch new movies from the database and update the graph
        new_movies = list(movies_collection.find())
        for movie in new_movies:
            if movie['tmdb_id'] not in self.movie_nodes:
                self.add_movie_node(movie)
                for similar in movie.get('similar_movies', []):
                    self.add_movie_edge(movie['tmdb_id'], similar['tmdb_id'])

        # Refresh the graph display
        self.update_graph_display()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MovieGraphApp()
    window.show()
    start_background_fetching()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
