import json
import random
import time
from typing import Dict
import plotly.graph_objects as go

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
from Data import Data_Processing
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
            edge_id = edge.id
            oneway = edge.oneway
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            rows.append({'start': edge.start_vertex,
                         'end': edge.end_vertex,
                         'edge_id': edge_id,
                         'oneway': oneway,
                         'geometry': line,
                         'traffic': []})
    return gpd.GeoDataFrame(rows, columns=['start', 'end', 'edge_id', 'oneway', 'geometry', 'traffic'])


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


def process_dataframe(df):
    rows_to_add = []
    matched_ids = set()

    for i in range(len(df)):
        if df.loc[i, 'edge_id'] in matched_ids:
            continue
        if df.loc[i, 'oneway']:
            # rows_to_add.append(df.iloc[i])
            new_row = {
                'start': df.loc[i, 'start'],
                'end': df.loc[i, 'end'],
                'traffic': df.loc[i, 'traffic'],
                'geometry': df.loc[i, 'geometry']
            }

            rows_to_add.append(new_row)
        else:
            edge_id = df.loc[i, 'edge_id']
            duplicate_row = df[(df['edge_id'] == edge_id)]

            if not duplicate_row.empty:
                duplicate_index = duplicate_row.index[0]
                summed_traffic = [sum(x) for x in zip(df.loc[i, 'traffic'], df.loc[duplicate_index, 'traffic'])]

                new_row = {
                    'start': df.loc[i, 'start'],
                    'end': df.loc[i, 'end'],
                    'traffic': summed_traffic,
                    'geometry': df.loc[i, 'geometry']
                }

                rows_to_add.append(new_row)
            matched_ids.add(edge_id)
    new_df = gpd.GeoDataFrame(rows_to_add)
    print(new_df)
    return new_df


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
        if random.random() < (probability * (weight ** 2) / (MAX_WEIGHT ** 2)):
            if weight > 10:
                self.value = random.randint(int(max_value/2), max_value)
            else:
                self.value = random.randint(1, int(max_value / 2))
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
                    target_vertex = graph.vertices[edge.end_vertex]  # DO EDYCJI
                    target_vertex.messages.append(transmit_value)
                    target_vertex.message_received = True
                    self.value -= transmit_value
                    global SENT_MESSAGES
                    SENT_MESSAGES += 1
        self.active = (self.value > 0)


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
        # if start_id not in self.vertices:
        #     self.add_vertex(Vertex(start_id, start_point.x, start_point.y))
        # if end_id not in self.vertices:
        #     self.add_vertex(Vertex(end_id, end_point.x, end_point.y))
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
        return gdf


def get_color(traffic_value, max_traffic, cmap):
    normalized_value = traffic_value / max_traffic
    return mcolors.to_hex(cmap(normalized_value))


def get_color2(traffic_value, max_traffic):
    # Normalizacja wartości 'traffic' do zakresu 0-1
    normalized_value = traffic_value / max_traffic
    # Interpolacja kolorów (zielony -> żółty -> czerwony)
    return mcolors.to_hex(mcolors.rgb_to_hsv(mcolors.to_rgb('green')) * (1 - normalized_value) + mcolors.rgb_to_hsv(
        mcolors.to_rgb('red')) * normalized_value)


colors = ["green", "yellow", "red"]
n_bins = 100  # Liczba kroków w gradiencie
cmap = LinearSegmentedColormap.from_list("traffic_cmap", colors, N=n_bins)

rows = Data_Processing.get_cracow_graph()
graph = Graph()

for row in rows:
    # start_point, end_point, source, target, cost, highway, oneway, weight = row
    # start_point = loads(start_point)
    # end_point = loads(end_point)
    start_point, end_point, source, target, highway, oneway, weight = row
    graph.add_edge(start_point, end_point, source, target, oneway, weight)

print(f"Liczba wierzchołków: {len(graph.vertices)}")
print(f"Liczba krawędzi: {len(graph.edges)}")

steps = 50

graph.initialize_traffic(probability=0.75, max_value=90)
gdf = graph.run_pregel(max_supersteps=steps)
gdf = process_dataframe(gdf)

# gdf = gdf.head(600)

print(gdf)

for i in range(steps):
    mapa = folium.Map(location=[50.074, 19.92], zoom_start=14)

    for _, row in gdf.iterrows():
        folium.PolyLine(
            locations=[(y, x) for x, y in row['geometry'].coords],
            color=get_color(row['traffic'][i], 60, cmap),
            weight=2
        ).add_to(mapa)

    mapa.save(f'Traffic_{i}.html')
    import webbrowser

    webbrowser.open(f'Traffic_{i}.html')

# # Function to extract coordinates from LineStrings
# def linestring_to_coords(linestring):
#     return [[x, y] for x, y in linestring.coords]
#
# # Prepare data for plotting
# gdf['coords'] = gdf['geometry'].apply(linestring_to_coords)
# max_length = gdf['traffic'].apply(len).max()
#
# # Create a Plotly figure
# fig = go.Figure()
#
# # Add streets as lines
# for _, row in gdf.iterrows():
#     fig.add_trace(go.Scattermapbox(
#         lon = [point[0] for point in row['coords']],
#         lat = [point[1] for point in row['coords']],
#         mode = 'lines',
#         line = dict(width = 2, color = 'green'), # Initial color
#         name = '',
#     ))
#
# # Update layout
# fig.update_layout(
#     mapbox_style="open-street-map",
#     mapbox_zoom=13,
#     mapbox_center = {"lat": 50.09151, "lon": 19.93074}
# )
#
# # Create animation frames
# frames = []
# for i in range(max_length):
#     frame_data = []
#     for _, row in gdf.iterrows():
#         traffic_value = row['traffic'][i] if i < len(row['traffic']) else row['traffic'][-1]
#         color = 'red' if traffic_value > 30 else 'green'
#         frame_data.append(go.Scattermapbox(
#             lon = [point[0] for point in row['coords']],
#             lat = [point[1] for point in row['coords']],
#             mode = 'lines',
#             line = dict(width = 2, color = color),
#             name = '',
#         ))
#     frames.append(go.Frame(data=frame_data, name=str(i)))
#
# # Add frames to the figure
# fig.frames = frames
#
# # Add a slider to control animation
# sliders = [{
#     'steps': [{'method': 'animate', 'label': str(k), 'args': [[str(k)], {'frame': {'duration': 1000, 'redraw': True}}]} for k in range(max_length)]
# }]
#
# fig.update_layout(sliders=sliders)
#
# # Show the figure
# fig.show()


#
# # Define the color map
# def traffic_color(value):
#     if value <= 50:
#         return 'green'
#     elif 50 < value <= 100:
#         return 'yellow'
#     else:
#         return 'red'
#
# # Initialize the plot
# fig, ax = plt.subplots()
#
# def animate(i):
#     ax.clear()
#     ax.set_xlim(19.929, 19.932)
#     ax.set_ylim(50.091, 50.092)
#     for index, row in gdf.iterrows():
#         # Determine the color based on the traffic value
#         color = traffic_color(row['traffic'][i])
#         ax.plot(*row['geometry'].xy, color=color, linewidth=2)
#
#     ax.set_title(f"Traffic at second {i+1}")
#
#
# from matplotlib.animation import FuncAnimation
# # Creating the animation
# ani = FuncAnimation(fig, animate, frames=3, interval=1000, repeat=False)
#
# from matplotlib.animation import writers
# print(writers.list())
#
# # Save the animation as a GIF file
# ani.save('traffic_animation.gif', writer='pillow', fps=1)

# # Prepare the data
# def extract_coordinates(linestring):
#     return list(linestring.coords)
#
# gdf['coordinates'] = gdf['geometry'].apply(extract_coordinates)
#
# # Function to get color based on traffic value
# def get_color(traffic_value):
#     if traffic_value > 100:
#         return 'red'
#     else:
#         return 'green'
#
# # Initialize the figure
# fig = go.Figure()
#
# # Add the initial state of the lines (using the first traffic value)
# for idx, row in gdf.iterrows():
#     fig.add_trace(go.Scattermapbox(
#         lon=[p[0] for p in row['coordinates']],
#         lat=[p[1] for p in row['coordinates']],
#         mode='lines',
#         line=dict(color=get_color(row['traffic'][0])),
#         hoverinfo='none'
#     ))
#
# # Set up the map layout
# fig.update_layout(
#     mapbox_style="open-street-map",
#     mapbox_center={"lat": 50.06143, "lon": 19.93658},
#     mapbox_zoom=12,
#     showlegend=False,
# )
#
# # Add animation frames
# frames = []
# for i in range(len(gdf['traffic'].iloc[0])):
#     frame_data = []
#     for idx, row in gdf.iterrows():
#         frame_data.append(go.Scattermapbox(
#             lon=[p[0] for p in row['coordinates']],
#             lat=[p[1] for p in row['coordinates']],
#             mode='lines',
#             line=dict(color=get_color(row['traffic'][i]))
#         ))
#     frames.append(go.Frame(data=frame_data))
#
# fig.frames = frames
#
# # Add a slider to control animation
# fig.update_layout(
#     updatemenus=[dict(
#         type="buttons",
#         buttons=[dict(label="Play",
#                       method="animate",
#                       args=[None, {"frame": {"duration": 1000, "redraw": True}}])])]
# )
#
# # Show the figure
# fig.show()


#
# line_data = []
# for _, row in gdf.iterrows():
#     line = row['geometry'].coords[:]
#     lon, lat = zip(*line)  # Rozpakowanie współrzędnych do osobnych list
#     line_data.append({'type': 'LineString', 'traffic': row['traffic'][0], 'coordinates': list(zip(lon, lat))})
#
# # Tworzymy pusty obiekt figury
# fig = go.Figure()
#
# # Dodajemy ścieżki dla każdego segmentu drogi
# for segment in line_data:
#     fig.add_trace(
#         go.Scattergeo(
#             lon=[coord[0] for coord in segment['coordinates']],
#             lat=[coord[1] for coord in segment['coordinates']],
#             mode='lines',
#             line=dict(width=2, color=get_color(segment['traffic'], 50, cmap)),  # Tutaj możesz dostosować grubość linii
#         )
#     )
#
# # Ustawienie layoutu mapy
# fig.update_layout(
#     title='Mapa korków w Krakowie',
#     geo=dict(
#         resolution=50,
#         showland=True,
#         landcolor="rgb(217, 217, 217)",
#         subunitcolor="rgb(255, 255, 255)",
#         countrycolor="rgb(255, 255, 255)",
#         showlakes=True,
#         lakecolor="rgb(255, 255, 255)",
#         showsubunits=True,
#         showcountries=True,
#         showocean=True,
#         oceancolor="rgb(255, 255, 255)",
#         projection_type="mercator",
#         center=dict(lon=19.9368, lat=50.0619),  # Centrum Krakowa
#         lonaxis_range=[19.8, 20.1],  # Zakres współrzędnych geograficznych
#         lataxis_range=[49.9, 50.1]
#     ),
#     showlegend=False,
#     mapbox_style="carto-positron",
#     mapbox_zoom=14,  # Zwiększ wartość dla większego przybliżenia
#     mapbox_center={"lat": 50.07, "lon": 19.92},  # Ustawienie na centrum Krakowa
#     width=1600,  # Szerokość mapy w pikselach
#     height=600,  # Wysokość mapy w pikselach
# )
#
# fig.show()
#


# # gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
#
# # Ustawienie układu współrzędnych
# gdf.set_crs(epsg=4326, inplace=True)
# # gdf['traffic2'] = gdf['traffic'].get(0)
# gdf['traffic2'] = gdf['traffic'].apply(lambda x: x[0])
# gdf = gdf.head(500)
#
# fig = go.Figure()
#
# # Iterujemy przez każdy wiersz DataFrame
# for _, row in gdf.iterrows():
#     # Parsujemy geometrię linestring do listy współrzędnych
#     line = row['geometry'].coords[:]
#     lat, lon = zip(*line)
#
#     # Dodajemy ślad dla każdego segmentu drogi
#     fig.add_trace(
#         go.Scattermapbox(
#             lat=lat,
#             lon=lon,
#             mode='lines',  # Ustawiamy tryb na linie
#             line=dict(width=2, color='red'),  # Tutaj można dostosować na podstawie 'traffic'
#         )
#     )
#
# # Ustawienie widoku mapy i stylu
# fig.update_layout(
#     mapbox_style="carto-positron",
#     mapbox_zoom=12,
#     mapbox_center={"lat": 50.0619, "lon": 19.9368}
# )
#
# # Wyświetlenie figury
# fig.show()
#
# # Tworzenie mapy
# # fig = px.line_mapbox(gdf, lat=gdf.geometry.centroid.y, lon=gdf.geometry.centroid.x,
# #                      color='traffic2', zoom=12, height=600)
# #
# # # Ustawienie tokena Mapbox (jeśli go masz)
# # # fig.update_layout(mapbox_style="open-street-map") # alternatywa, jeśli nie masz tokena Mapbox
# # fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=12, mapbox_center = {"lat": 50.0619, "lon": 19.9368})
# #
# # fig.show()
# time.sleep(10000)
