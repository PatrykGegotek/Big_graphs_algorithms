import random
import pandas as pd
import time

from Data.Graph import Graph, Vertex
from Visualization.Visualization import initialize_dataframe, update_dataframe, process_dataframe, \
    generate_pregel_map, generate_overlayed_pregel_plots

MESSAGES_NUMBER = 0
SENT_MESSAGES = 0
MAX_WEIGHT = 20


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
                # print(edge.weight)
                # print(total_weights)
                # print(total_edges)
                # print(edge.weight / (total_weights / total_edges))
                # print()
                if edge.weight / (total_weights / total_edges) < random.uniform(0, 1.0):
                    continue
                transmit_value = int(random.uniform(0.4, 1.0) * minimal_value * edge.weight)
                if transmit_value == 0 or transmit_value > vertex.value:
                    transmit_value = vertex.value
                target_vertex = graph.vertices[edge.end_vertex]
                target_vertex.messages.append(transmit_value)
                target_vertex.message_received = True
                vertex.value -= transmit_value

                SENT_MESSAGES += 1
    vertex.active = (vertex.value > 0)


def run_pregel(max_supersteps: int, initialization_variant: int = 0, sending_variant: int = 0, initialization_vertices_ids: list[str] = 0, initial_value: int = 90):
    n_received_messages = []
    n_sent_messages = []
    total_movement = []
    total_active_vertices = []
    times = []
    graph = Graph()
    if initialization_variant == 0:
        graph.initialize_traffic(probability=0.75, max_value=initial_value)
    elif initialization_variant == 1:
        graph.initialize_compressed_traffic(initialization_vertices_ids, initial_value)

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

        start_time = time.time()

        for vertex in graph.vertices.values():
            if vertex.message_received:
                compute(vertex)

        for vertex in graph.vertices.values():
            if vertex.active:
                traffic_sum += vertex.value
                sending_function(graph, vertex)
                active_vertices += 1

        end_time = time.time()
        duration = end_time - start_time  # Sekundy

        gdf = update_dataframe(graph, gdf)

        print(f"Ilość otrzymanych wiadomości: {MESSAGES_NUMBER}")
        print(f"Ilość wysłanych wiadomości: {SENT_MESSAGES}")
        print(f"Całkowity ruch: {traffic_sum}")
        print(f"Aktywne wierzchołki: {active_vertices}")

        n_received_messages.append(MESSAGES_NUMBER)
        n_sent_messages.append(SENT_MESSAGES)
        total_movement.append(traffic_sum)
        total_active_vertices.append(active_vertices)
        times.append(duration)
        MESSAGES_NUMBER = 0
        SENT_MESSAGES = 0

    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.max_columns', None)
    data = {
        'Received Messages': n_received_messages,
        'Sent Messages': n_sent_messages,
        'Total Movement': total_movement,
        'Active Vertices': total_active_vertices,
        'Duration': times
    }
    # Tworzenie DataFrame z Pandas
    df = pd.DataFrame(data)
    return gdf, df

def compare_discrete_pregels(max_supersteps: int, n_vertices: int = 10, initial_value: int = 90):
    graph = Graph()
    vertex_ids = []
    for i in range(n_vertices):
        vertex_ids.append(random.choice(list(graph.vertices.keys())))
    maps_data = []
    plots_data = []

    for i in range(0, 2):
        n_received_messages = []
        n_sent_messages = []
        total_movement = []
        total_active_vertices = []
        times = []
        graph = Graph()
        graph.initialize_compressed_traffic(vertex_ids, initial_value)

        sending_function = None
        if i == 0:
            sending_function = send_message_uniform
        elif i == 1:
            sending_function = send_message_weighted

        gdf = initialize_dataframe(graph)
        print(f"Starting {'uniform' if i == 0 else 'weighted'}")

        for step in range(max_supersteps):
            global MESSAGES_NUMBER
            global SENT_MESSAGES
            traffic_sum = 0
            active_vertices = 0
            print(f'Iteracja: {step + 1}')

            start_time = time.time()

            for vertex in graph.vertices.values():
                if vertex.message_received:
                    compute(vertex)

            for vertex in graph.vertices.values():
                if vertex.active:
                    traffic_sum += vertex.value
                    sending_function(graph, vertex)
                    active_vertices += 1

            end_time = time.time()
            duration = end_time - start_time

            gdf = update_dataframe(graph, gdf)

            print(f"Ilość otrzymanych wiadomości: {MESSAGES_NUMBER}")
            print(f"Ilość wysłanych wiadomości: {SENT_MESSAGES}")
            print(f"Całkowity ruch: {traffic_sum}")
            print(f"Aktywne wierzchołki: {active_vertices}")

            n_received_messages.append(MESSAGES_NUMBER)
            n_sent_messages.append(SENT_MESSAGES)
            total_movement.append(traffic_sum)
            total_active_vertices.append(active_vertices)
            times.append(duration)
            MESSAGES_NUMBER = 0
            SENT_MESSAGES = 0

        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.max_columns', None)
        data = {
            'Received Messages': n_received_messages,
            'Sent Messages': n_sent_messages,
            'Total Movement': total_movement,
            'Active Vertices': total_active_vertices,
            'Duration': times
        }

        df = pd.DataFrame(data)

        maps_data.append(gdf)
        plots_data.append(df)

    return maps_data, plots_data


supersteps = 1000
step = 4
# gdf, df = run_pregel(max_supersteps=supersteps, initialization_variant=1, sending_variant=1, initialization_vertices=30, initial_value=20000)

maps_data, plots_data = compare_discrete_pregels(max_supersteps=supersteps, n_vertices=35, initial_value=35000)

generate_overlayed_pregel_plots(plots_data)
for gdf in maps_data:
    gdf = process_dataframe(gdf)

    generate_pregel_map(gdf, "Pregel", supersteps, step)


