import random
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from Data_Processing import Data_Processing
from shapely.wkt import loads
import networkx as nx


def draw_graph(graph, ax, step):
    # Przygotowanie mapy kolorów
    cmap = plt.cm.Reds
    norm = mcolors.Normalize(vmin=0, vmax=30)  # Zakładamy, że maksymalna wartość to 30

    for vertex in graph.vertices.values():
        for edge in vertex.edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]

            # Rysowanie krawędzi
            ax.plot([start_vertex.x, end_vertex.x], [start_vertex.y, end_vertex.y], 'black')

            # Rysowanie wierzchołków z odpowiednim kolorem
            color = cmap(norm(vertex.value))
            ax.plot(start_vertex.x, start_vertex.y, 'o', color=color)

    ax.set_title(f"Symulacja Ruchu Drogowego, krok {step}")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")


class Vertex:
    def __init__(self, vertex_id, x, y):
        self.id = vertex_id
        self.x = x  # Współrzędna X wierzchołka
        self.y = y  # Współrzędna Y wierzchołka
        self.edges = []  # Lista krawędzi wychodzących z tego wierzchołka
        self.value = 0  # Początkowa wartość, np. natężenie ruchu
        self.messages = []
        self.active = False  # Czy wierzchołek jest aktywny

    def __str__(self):
        vertex = f"Vertex({self.id}) "
        for edge in self.edges:
            vertex += str(edge) + ' '
        return vertex

    def add_edge(self, edge):
        self.edges.append(edge)

    def initialize_randomly(self, probability, max_value):
        if random.random() < probability:
            self.value = random.randint(1, max_value)
            self.active = True

    def compute(self, messages):
        if self.id > 20000 and self.id < 20100:
            print(self.id, self.value)
        if messages:
            self.value += sum(messages)  # Dodaj wartości z wiadomości
            self.active = True

    def send_message(self):
        if self.active and self.value > 0:
            total_edges = len(self.edges)
            if total_edges > 0:
                value_per_edge = self.value / total_edges  # Rozdzielenie wartości
                for edge in self.edges:
                    if self.value == 0:
                        break
                    transmit_value = int(random.uniform(0.6, 1.0) * value_per_edge)
                    if transmit_value == 0:
                        transmit_value = self.value
                    target_vertex = graph.vertices[edge.end_vertex]
                    target_vertex.messages.append(transmit_value)
                    # print(f'message sent: {transmit_value}')
                    if self.id > 20000 and self.id < 20100:
                        print("send", self.id, self.value, transmit_value)
                    self.value -= transmit_value  # Zaktualizuj wartość wierzchołka
                    if self.id > 20000 and self.id < 20100:
                        print("send", self.id, self.value, transmit_value)
                self.active = False if self.value < 1 else True


class Edge:
    def __init__(self, start_vertex, end_vertex, cost):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.cost = cost

    def __str__(self):
        return f"Edge(from: {self.start_vertex}, to: {self.end_vertex}, cost: {self.cost:.0f})"


class Graph:
    def __init__(self):
        self.vertices = {}  # Słownik przechowujący wierzchołki

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def add_edge(self, start_point, end_point, start_id, end_id, cost):
        if start_id not in self.vertices:
            self.add_vertex(Vertex(start_id, start_point.x, start_point.y))
        if end_id not in self.vertices:
            self.add_vertex(Vertex(end_id, end_point.x, end_point.y))

        edge = Edge(start_id, end_id, cost)
        self.vertices[start_id].add_edge(edge)

    def initialize_vertices(self, probability, max_value):
        for vertex in self.vertices.values():
            vertex.initialize_randomly(probability, max_value)

    def run_pregel(self, max_supersteps):
        fig, ax = plt.subplots(figsize=(30, 18))
        i = 0

        for step in range(max_supersteps):
            # Zbieranie wiadomości od wierzchołków
            print(f'Iteracja: {i}')
            i += 1
            messages = {vertex_id: [] for vertex_id in self.vertices}
            for vertex in self.vertices.values():
                for message in vertex.messages:
                    messages[vertex.id].append(message)
                vertex.messages.clear()

            # Uruchamianie obliczeń dla aktywnych wierzchołków
            for vertex in self.vertices.values():
                if vertex.active:
                    vertex.compute(messages[vertex.id])

            # Wysyłanie wiadomości po obliczeniach
            for vertex in self.vertices.values():
                if vertex.active:
                    vertex.send_message()

            ax.clear()
            draw_graph(self, ax, step)
            plt.pause(0.5)  # Krótka pauza między iteracjami
        plt.show()


rows = Data_Processing.get_cracow_graph()
graph = Graph()

for row in rows:
    start_point, end_point, source, target, cost = row
    start_point = loads(start_point)
    end_point = loads(end_point)
    graph.add_edge(start_point, end_point, source, target, cost)

# for key in graph.vertices.keys():
#     print(graph.vertices[key])

graph.initialize_vertices(probability=0.5, max_value=500)
graph.run_pregel(max_supersteps=10)
