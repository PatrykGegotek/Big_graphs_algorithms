#TODO:
# samochody chętniej skręcają w ulice o wyższej randze
# dodać długość ulicy do Edge
# ulica może pomieścić daną liczbę samochodów definiowaną przez jej długość
# gdy samochody nie mogą skręcić w daną ulicę to pozostają na obecnej lub przedostaje się tylko ta część poniżej limitu

import folium as folium
import random
import pandas as pd

from Data import Data_Processing
from Data.Graph import Graph, Vertex
from Visualization.Visualization import initialize_dataframe, update_dataframe, process_dataframe, get_color, get_cmap

MESSAGES_NUMBER = 0
SENT_MESSAGES = 0


def compute(vertex: Vertex):
    global MESSAGES_NUMBER
    if vertex.messages:
        MESSAGES_NUMBER += len(vertex.messages)
        vertex.value += sum(vertex.messages)  # Dodaj wartości z wiadomości
        vertex.messages = []
        vertex.active = (vertex.value > 0)
        vertex.message_received = False


def send_message(vertex: Vertex):
    if vertex.value > 0:
        total_edges = len(vertex.outcoming_edges)
        if total_edges > 0:

            total_weights = 0
            for edge in vertex.outcoming_edges:
                total_weights += edge.weight
            minimal_value = vertex.value / total_weights

            for edge in vertex.outcoming_edges:
                if vertex.value == 0:
                    break
                transmit_value = int(random.uniform(0.4, 1.0) * minimal_value * edge.weight)
                if transmit_value == 0 or transmit_value > vertex.value:
                    transmit_value = vertex.value
                target_vertex = graph.vertices[edge.end_vertex]  #TODO: DO EDYCJI
                target_vertex.messages.append(transmit_value)
                target_vertex.message_received = True
                vertex.value -= transmit_value
                global SENT_MESSAGES
                SENT_MESSAGES += 1
    vertex.active = (vertex.value > 0)


def run_pregel(graph: Graph, max_supersteps: int):
    gdf = initialize_dataframe(graph)

    for step in range(max_supersteps):
        global MESSAGES_NUMBER
        global SENT_MESSAGES
        traffic_sum = 0
        active_vertices = 0
        print(f'Iteracja: {step + 1}')

        for vertex in graph.vertices.values():
            if vertex.message_received:
                compute(vertex)

        for vertex in graph.vertices.values():
            if vertex.active:
                traffic_sum += vertex.value
                send_message(vertex)
                active_vertices += 1

        gdf = update_dataframe(graph, gdf)

        print(f"Ilość otrzymanych wiadomości: {MESSAGES_NUMBER}")
        print(f"Ilość wysłanych wiadomości: {SENT_MESSAGES}")
        print(f"Całkowity ruch: {traffic_sum}")
        print(f"Aktywne wierzchołki: {active_vertices}")
        MESSAGES_NUMBER = 0
        SENT_MESSAGES = 0

    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    return gdf


graph = Graph()

print(f"Liczba wierzchołków: {len(graph.vertices)}")
print(f"Liczba krawędzi: {len(graph.edges)}")

steps = 3

graph.initialize_traffic(probability=0.75, max_value=90)
gdf = run_pregel(graph, max_supersteps=steps)
gdf = process_dataframe(gdf)

print(gdf)

for i in range(steps):
    mapa = folium.Map(location=[50.074, 19.92], zoom_start=13)

    for _, row in gdf.iterrows():
        folium.PolyLine(
            locations=[(y, x) for x, y in row['geometry'].coords],
            color=get_color(row['traffic'][i], 60, get_cmap()),
            weight=2
        ).add_to(mapa)

    mapa.save(f'Traffic_{i}.html')
    import webbrowser

    webbrowser.open(f'Traffic_{i}.html')
