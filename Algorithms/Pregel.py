import json
import random
from typing import Dict

import folium as folium
import geopandas as gpd
import pandas as pd
import plotly.express as px
import shapely
from shapely.geometry import LineString
import os
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from Data_Processing import Data_Processing
from shapely.wkt import loads
from matplotlib.colors import LinearSegmentedColormap

MAX_WEIGHT = 20
MESSAGES_NUMBER = 0
SENT_MESSAGES = 0

def initialize_geodataframe(graph):
    rows = []
    for vertex in graph.vertices.values():
        for edge in vertex.edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            rows.append({'start': edge.start_vertex, 'end': edge.end_vertex, 'geometry': line, 'traffic': []})
    print(gpd.GeoDataFrame(rows, columns=['start', 'end', 'geometry', 'traffic']))
    return gpd.GeoDataFrame(rows, columns=['start', 'end', 'geometry', 'traffic'])

def update_geodataframe(graph, gdf):
    for i, row in gdf.iterrows():
        start_vertex_id = row['start']
        end_vertex_id = row['end']

        # Uzyskanie wierzchołków startowego i końcowego na podstawie identyfikatorów
        start_vertex = graph.vertices[start_vertex_id]
        end_vertex = graph.vertices[end_vertex_id]

        edge_traffic = (start_vertex.value + end_vertex.value) / 2
        row['traffic'].append(edge_traffic)
    return gdf


def draw_graph(graph, ax, step):
    colors = [(0, 'green'), (0.25, 'yellow'), (0.75, 'yellow'), (1, 'red')]
    cmap = LinearSegmentedColormap.from_list('custom_colormap', colors)
    # cmap = plt.cm.ScalarMappable(cmap=cmap_)
    norm = mcolors.Normalize(vmin=0, vmax=30)  # Zakres wartości ruchu

    for vertex in graph.vertices.values():
        for edge in vertex.edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]

            # Oblicz wartość ruchu dla krawędzi
            edge_traffic = (start_vertex.value + end_vertex.value) / 2

            # Koloruj krawędź na podstawie wartości ruchu
            color = cmap(norm(edge_traffic))
            ax.plot([start_vertex.x, end_vertex.x], [start_vertex.y, end_vertex.y], color=color, linewidth=2)
        color2 = cmap(norm(vertex.value))
        ax.plot(vertex.x, vertex.y, 'o', color=color2)

    ax.set_title(f"Symulacja Ruchu Drogowego, krok {step + 1}")
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
        self.message_received = False

    def __str__(self):
        vertex = f"Vertex({self.id}) "
        for edge in self.edges:
            vertex += str(edge) + ' '
        return vertex

    def add_edge(self, edge):
        self.edges.append(edge)

    def initialize_traffic(self, probability, max_value, weight):
        if random.random() < (probability * weight / MAX_WEIGHT):
            self.value = random.randint(1, max_value * weight)
            self.active = True

    def compute(self):
        global MESSAGES_NUMBER
        if self.messages:
            MESSAGES_NUMBER += len(self.messages)
            self.value += sum(self.messages)  # Dodaj wartości z wiadomości
            self.messages = []
            self.active = (self.value > 0)
            self.message_received = False

    def send_message(self):
        if self.value > 0:
            total_edges = len(self.edges)
            if total_edges > 0:

                total_weights = 0
                for edge in self.edges:
                    total_weights += edge.weight
                minimal_value = self.value / total_weights

                for edge in self.edges:
                    if self.value == 0:
                        break
                    transmit_value = int(random.uniform(0.4, 1.0) * minimal_value * edge.weight)
                    if transmit_value == 0 or transmit_value > self.value:
                        transmit_value = self.value
                    target_vertex = graph.vertices[edge.end_vertex] # DO EDYCJI
                    target_vertex.messages.append(transmit_value)
                    target_vertex.message_received = True
                    self.value -= transmit_value
                    global SENT_MESSAGES
                    SENT_MESSAGES += 1
        self.active = (self.value > 0)


class Edge:
    static_edges = []

    def __init__(self, start_vertex, end_vertex, weight):
        self.start_vertex = start_vertex
        self.end_vertex = end_vertex
        self.weight = weight

    def __str__(self):
        return f"Edge(from: {self.start_vertex}, to: {self.end_vertex}, weight: {self.weight:.0f})"


class Graph:
    def __init__(self):
        self.vertices: dict[int, Vertex] = {}
        self.edges: list[Edge] = []

    def add_vertex(self, vertex):
        if vertex.id not in self.vertices:
            self.vertices[vertex.id] = vertex

    def add_edge(self, start_point, end_point, start_id, end_id, weight):
        if start_id not in self.vertices:
            self.add_vertex(Vertex(start_id, start_point.x, start_point.y))
        if end_id not in self.vertices:
            self.add_vertex(Vertex(end_id, end_point.x, end_point.y))

        edge = Edge(start_id, end_id, weight)
        self.edges.append(edge)
        self.vertices[start_id].add_edge(edge)

    def initialize_traffic(self, probability, max_value):
        for edge in self.edges:
            vertex = self.vertices.get(edge.start_vertex)
            vertex.initialize_traffic(probability, max_value, weight)

    def save_results(self, all_steps_gdf: gpd.GeoDataFrame):
        results_folder = "Results"
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        all_steps_gdf.to_file(os.path.join(results_folder, "traffic_simulation_results.geojson"), driver='GeoJSON')

    def run_pregel(self, max_supersteps):
        # all_steps_gdf = gpd.GeoDataFrame(columns=['geometry', 'traffic'])
        gdf = initialize_geodataframe(self)

        for step in range(max_supersteps):
            global MESSAGES_NUMBER
            global SENT_MESSAGES
            traffic_sum = 0
            active_vertices = 0
            print(f'Iteracja: {step + 1}')
            # fig, ax = plt.subplots(figsize=(30, 18))

            # Compute incoming messages
            for vertex in self.vertices.values():
                if vertex.message_received:
                    vertex.compute()

            # Send messages to other vertices
            for vertex in self.vertices.values():
                if vertex.active:
                    traffic_sum += vertex.value
                    vertex.send_message()
                    active_vertices += 1

            gdf = update_geodataframe(self, gdf)

            print(f"Ilość otrzymanych wiadomości: {MESSAGES_NUMBER}")
            print(f"Ilość wysłanych wiadomości: {SENT_MESSAGES}")
            print(f"Całkowity ruch: {traffic_sum}")
            print(f"Aktywne wierzchołki: {active_vertices}")
            MESSAGES_NUMBER = 0
            SENT_MESSAGES = 0

            # ax.clear()
            # draw_graph(self, ax, step)
            # plt.show()
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_columns', None)
        print(gdf)
        return gdf

def get_color(traffic_value, max_traffic, cmap):
    normalized_value = traffic_value / max_traffic
    print(mcolors.to_hex(cmap(normalized_value)))
    return mcolors.to_hex(cmap(normalized_value))

def get_color2(traffic_value, max_traffic):
    # Normalizacja wartości 'traffic' do zakresu 0-1
    normalized_value = traffic_value / max_traffic
    # Interpolacja kolorów (zielony -> żółty -> czerwony)
    return mcolors.to_hex(mcolors.rgb_to_hsv(mcolors.to_rgb('green')) * (1 - normalized_value) + mcolors.rgb_to_hsv(mcolors.to_rgb('red')) * normalized_value)

colors = ["green", "yellow", "red"]
n_bins = 100  # Liczba kroków w gradiencie
cmap = LinearSegmentedColormap.from_list("traffic_cmap", colors, N=n_bins)

rows = Data_Processing.get_cracow_graph()
graph = Graph()

for row in rows:
    start_point, end_point, source, target, cost, highway, weight = row
    start_point = loads(start_point)
    end_point = loads(end_point)
    graph.add_edge(start_point, end_point, source, target, weight)

graph.initialize_traffic(probability=0.5, max_value=100)
geo_df = graph.run_pregel(max_supersteps=1)


mapa = folium.Map(location=[50.08, 19.94], zoom_start=12)

# Dodaj linie na mapie
for _, row in geo_df.iterrows():
    # Użyj folium.PolyLine, aby dodać linie na mapie
    # Kolor linii jest zależny od wartości 'traffic'
    # print(get_color2(row['traffic'][0], 200))
    folium.PolyLine(
        locations=[(y, x) for x, y in row['geometry'].coords],
        color=get_color(row['traffic'][0], 20, cmap), # Zmień na odpowiednią funkcję kolorów w zależności od 'traffic'
        weight=2
    ).add_to(mapa)

# Wyświetl mapę
mapa.save('run_map.html')
import webbrowser
webbrowser.open('run_map.html')



