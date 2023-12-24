import folium as folium
import random
import pandas as pd

from Data import Data_Processing
from Data.Graph import Graph, Vertex
from Visualization.Visualization import initialize_dataframe, update_dataframe, process_dataframe, get_color, get_cmap, \
    generate_pregel_map

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


# def add_value_to_end_vertex(target_vertex, transmit_value):


def send_message_uniform(graph: Graph, vertex: Vertex):
    global SENT_MESSAGES
    if vertex.value > 0:
        total_edges = len(vertex.outcoming_edges)
        if total_edges > 0:
            minimal_value = vertex.value / total_edges
            for edge in vertex.outcoming_edges:
                if vertex.value == 0:
                    break
                transmit_value = int(random.uniform(0.4, 1.0) * minimal_value)
                if transmit_value == 0 or transmit_value > vertex.value:
                    transmit_value = vertex.value
                target_vertex = graph.vertices[edge.end_vertex]
                target_vertex.messages.append(transmit_value)
                target_vertex.message_received = True
                vertex.value -= transmit_value

                SENT_MESSAGES += 1
    vertex.active = (vertex.value > 0)


def send_message_weighted(graph: Graph, vertex: Vertex):
    global SENT_MESSAGES
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
                target_vertex = graph.vertices[edge.end_vertex]
                target_vertex.messages.append(transmit_value)
                target_vertex.message_received = True
                vertex.value -= transmit_value

                SENT_MESSAGES += 1
    vertex.active = (vertex.value > 0)


def run_pregel(max_supersteps: int, initialization_variant: int = 0, sending_variant: int = 0, initialization_vertices: int = 0):
    n_received_messages = []
    n_sent_messages = []
    total_movement = []
    active_vertices = []
    time = []
    graph = Graph()
    if initialization_variant == 0:
        graph.initialize_traffic(probability=0.75, max_value=90)
    elif initialization_variant == 1:
        graph.initialize_compressed_traffic(initialization_vertices, 20000)

    sending_function = None
    if sending_variant == 0:
        sending_function = send_message_uniform
    elif sending_variant == 1:
        sending_function = send_message_weighted

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
                sending_function(graph, vertex)
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

supersteps = 20
step = 10
gdf = run_pregel(max_supersteps=supersteps, initialization_variant=1, sending_variant=1, initialization_vertices=30)
gdf = process_dataframe(gdf)

# generate_pregel_map(gdf, "Pregel", supersteps, step)