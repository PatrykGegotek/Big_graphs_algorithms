import random

MAX_WEIGHT = 20


class Vertex:
    def __init__(self, vertex_id, x, y):
        self.id = vertex_id
        self.x = x  # Współrzędna X wierzchołka
        self.y = y  # Współrzędna Y wierzchołka
        self.edges = []  # Lista krawędzi wychodzących z tego wierzchołka
        self.value = 0  # Początkowa wartość, np. natężenie ruchu
        self.messages = []
        self.active = False  # Czy wierzchołek jest aktywny
        self.message_received = False

    def __str__(self):
        vertex = f"Vertex({self.id}) "
        for edge in self.edges:
            vertex += str(edge) + ' '
        return vertex

    def add_edge(self, edge):
        self.edges.append(edge)

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

    def __init__(self, start_vertex, end_vertex, weight, id, oneway):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.weight = weight
        self.id = id
        self.oneway = oneway

    def __str__(self):
        return f"Edge(from: {self.start_vertex}, to: {self.end_vertex}, weight: {self.weight:.0f})"


class Graph:
    def __init__(self):
        self.vertices: dict[int, Vertex] = {}
        self.edges: list[Edge] = []

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def add_edge(self, start_point, end_point, start_id, end_id, oneway, weight):
        is_oneway = oneway == 'yes'
        if start_id not in self.vertices:
            self.add_vertex(Vertex(start_id, start_point[0], start_point[1]))
        if end_id not in self.vertices:
            self.add_vertex(Vertex(end_id, end_point[0], end_point[1]))

        edge = Edge(start_id, end_id, weight, Edge.edge_id, is_oneway)
        self.edges.append(edge)
        self.vertices[start_id].add_edge(edge)
        if not is_oneway:
            edge = Edge(end_id, start_id, weight, Edge.edge_id, is_oneway)
            self.edges.append(edge)
            self.vertices[end_id].add_edge(edge)
        Edge.edge_id += 1

    def initialize_traffic(self, probability, max_value):
        for edge in self.edges:
            vertex = self.vertices.get(edge.start_vertex)
            vertex.initialize_traffic(probability, max_value, edge.weight)

