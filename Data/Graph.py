import os
import pickle
import random

from Data import Data_Processing

GRAPH_PATH = "C:\\Users\\patryk\\Desktop\\Inżynierka\\Algorithms implementation\\Data\\Graph_Data.pkl"
MAX_WEIGHT = 20


class Vertex:
    def __init__(self, vertex_id, x, y):
        self.id: str = vertex_id
        self.x = x  # Współrzędna X wierzchołka
        self.y = y  # Współrzędna Y wierzchołka
        self.outcoming_edges = []  # Lista krawędzi wychodzących z tego wierzchołka
        self.incoming_edges = []  # Lista krawędzi wychodzących z tego wierzchołka
        self.value = 0  # Początkowa wartość, np. natężenie ruchu
        self.values = []
        self.messages = []
        self.active = False  # Czy wierzchołek jest aktywny
        self.message_received = False

    def __str__(self):
        vertex = f"Vertex({self.id}) "
        for edge in self.outcoming_edges:
            vertex += str(edge) + ' '
        return vertex

    def add_outcoming_edge(self, edge):
        self.outcoming_edges.append(edge)

    def add_incoming_edge(self, edge):
        self.incoming_edges.append(edge)

    def initialize_traffic(self, probability, max_value, weight):
        if random.random() < (probability * (weight ** 2) / (MAX_WEIGHT ** 2)):
            if weight > 10:
                self.value = random.randint(int(max_value/2), max_value)
            else:
                self.value = random.randint(1, int(max_value / 2))
            self.active = True


class Edge:
    static_edges = []
    edge_id = 0

    def __init__(self, start_vertex, end_vertex, weight, id, oneway, meters, duplicate=False):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.weight = weight
        self.id = id
        self.oneway = oneway
        self.value = 0
        self.meters = meters
        self.duplicate = duplicate
        self.values = []

    def __str__(self):
        return f"Edge(from: {self.start_vertex}, to: {self.end_vertex}, weight: {self.weight:.0f})"


class Graph:
    def __init__(self):
        self.vertices: dict[int, Vertex] = {}
        self.edges: list[Edge] = []

        if os.path.exists(GRAPH_PATH):
            with open(GRAPH_PATH, 'rb') as file:
                rows = pickle.load(file)
        else:
            rows = Data_Processing.get_cracow_graph()

        for row in rows:
            start_point, end_point, source, target, highway, oneway, weight, meters = row
            self.add_edge(start_point, end_point, str(source), str(target), oneway, weight, meters)

        # print(f"Created graph with {len(self.vertices)} vertices and {len(self.edges)} edges.")

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def add_edge(self, start_point, end_point, start_id, end_id, oneway, weight, meters):
        is_oneway = oneway == 'yes'
        if start_id not in self.vertices:
            self.add_vertex(Vertex(start_id, start_point[0], start_point[1]))
        if end_id not in self.vertices:
            self.add_vertex(Vertex(end_id, end_point[0], end_point[1]))

        edge = Edge(start_id, end_id, weight, Edge.edge_id, is_oneway, meters)
        self.edges.append(edge)
        self.vertices[start_id].add_outcoming_edge(edge)
        self.vertices[end_id].add_incoming_edge(edge)
        if not is_oneway:
            edge = Edge(end_id, start_id, weight, Edge.edge_id, is_oneway, meters, duplicate=True)
            self.edges.append(edge)
            self.vertices[end_id].add_outcoming_edge(edge)
            self.vertices[end_id].add_incoming_edge(edge)
        Edge.edge_id += 1

    def initialize_traffic(self, probability, max_value):
        for edge in self.edges:
            vertex = self.vertices.get(edge.start_vertex)
            vertex.initialize_traffic(probability, max_value, edge.weight)

    def initialize_compressed_traffic(self, vertices_ids, initial_value):
        for vertex_id in vertices_ids:
            # vertex = random.choice(list(self.vertices.values()))
            vertex = self.vertices.get(vertex_id)
            vertex.value = initial_value
            vertex.active = True
