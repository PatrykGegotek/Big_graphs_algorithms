import random

import numpy as np

from Data.Graph import Graph
from collections import deque
from Visualization.Visualization import generate_wavefront_map, create_wavefront_edge_geodataframe, \
    initialize_wavefront_multi_dataframe, update_wavefront_multi_dataframe, generate_wavefront_map2

INF = float('inf')


# def wavefront_single(graph: Graph):
#     start_vertex_id = random.choice(list(graph.vertices.keys()))
#     distances = {vertex_id: INF for vertex_id in graph.vertices}
#     for vertex in graph.vertices.values():
#         vertex.value = INF
#     distances[start_vertex_id] = 0
#     graph.vertices.get(start_vertex_id).value = 0
#
#     queue = deque([start_vertex_id])
#
#     while queue:
#         print("Queue length:", len(queue))
#         current_id = queue.popleft()
#         current_vertex = graph.vertices[current_id]
#
#         for edge in current_vertex.outcoming_edges:
#             neighbor_id = edge.end_vertex
#             if distances[neighbor_id] == INF:
#                 distances[neighbor_id] = distances[current_id] + 1
#                 graph.vertices.get(neighbor_id).value = distances[neighbor_id]
#                 queue.append(neighbor_id)
#
#     for vertex_id, distance in distances.items():
#         print(f"Odległość od wierzchołka {start_vertex_id} do {vertex_id} wynosi: {distance}")
#
#     return distances


# def wavefront_multiple(graph: Graph, n_sources: int):
#     start_indexes = []
#     for n in range(n_sources):
#         start_indexes.append(random.choice(list(graph.vertices.keys())))
#     distances = {vertex_id: INF for vertex_id in graph.vertices}
#     for vertex in graph.vertices.values():
#         vertex.value = INF
#     for start_vertex_id in start_indexes:
#         distances[start_vertex_id] = 0
#         graph.vertices.get(start_vertex_id).value = 0
#
#     queue = deque(start_indexes)
#     # next_queue = None
#
#     while queue:
#         current_id = queue.popleft()
#         current_vertex = graph.vertices[current_id]
#
#         for edge in current_vertex.outcoming_edges:
#             neighbor_id = edge.end_vertex
#             if distances[neighbor_id] > distances[current_id] + 1:
#                 distances[neighbor_id] = distances[current_id] + 1
#                 graph.vertices.get(neighbor_id).value = distances[neighbor_id]
#                 queue.append(neighbor_id)
#
#     return distances

# def wavefront(graph, start_vertex_id, num):
#     print(f"Starting {num}")
#     queue = deque([start_vertex_id])
#     graph.vertices[start_vertex_id].value = 0
#
#     while queue:
#         current_id = queue.popleft()
#         current_value = graph.vertices[current_id].value
#
#         for edge in graph.vertices[current_id].outcoming_edges:
#             neighbor_id = edge.end_vertex
#             if graph.vertices[neighbor_id].active is False:
#                 graph.vertices[neighbor_id].value = current_value + 1
#                 queue.append(neighbor_id)
#                 graph.vertices[neighbor_id].active = True
#             else:
#                 graph.vertices[neighbor_id].value += current_value + 1
#
#     for vertex in graph.vertices.values():
#         vertex.active = False


# def run_wavefront_multiple_sources(graph, start_points):
#
#     for vertex in graph.vertices.values():
#         vertex.value = None
#
#     # Uruchomienie algorytmu dla każdego punktu startowego
#     for i, start_point in enumerate(start_points):
#         wavefront(graph, start_point, i)
#
#     return {vertex_id: vertex.value for vertex_id, vertex in graph.vertices.items()}
#
#
# def calculate_euclidean_distance(vector_a, vector_b):
#     return np.linalg.norm(np.array(vector_a) - np.array(vector_b))
#
#
# def get_random_points(graph: Graph, n):
#     points = []
#     for i in range(n):
#         points.append(random.choice(list(graph.vertices.keys())))
#     return points

def generate_initial_points(graph, num):
    vertices = []
    points = []
    for i in range(num):
        vertex = random.choice(list(graph.vertices.values()))
        vertices.append(vertex.id)
        points.append((vertex.y, vertex.x))
    return vertices, points


def wavefront_single(graph: Graph, vertices, wave_range=100):
    for i, start_vertex_id in enumerate(vertices):
        vertex = graph.vertices.get(start_vertex_id)
        if vertex is None:
            continue
        vertex.values.append(0)

        queue = deque([start_vertex_id])
        nullify = False

        while queue:
            current_id = queue.popleft()
            current_vertex = graph.vertices[current_id]

            for edge in current_vertex.outcoming_edges:
                neighbor_id = edge.end_vertex
                neighbor_vertex = graph.vertices[neighbor_id]
                if len(neighbor_vertex.values) == i:
                    next_value = current_vertex.values[i] + 1 if nullify is False else 0
                    if next_value >= wave_range:
                        nullify = True
                    neighbor_vertex.values.append(next_value)
                    queue.append(neighbor_id)

    min_val = INF
    max_val = 0
    for vertex in graph.vertices.values():
        new_value = np.sum(vertex.values)
        vertex.value = new_value
        if new_value < min_val:
            min_val = new_value
        if new_value > max_val:
            max_val = new_value

    for vertex in graph.vertices.values():
        vertex.value = (vertex.value - min_val) / (max_val - min_val)
    return max_val, min_val


# def wavefront_single(graph: Graph, vertices, wave_range=100):
#     for i, start_vertex_id in enumerate(vertices):
#         vertex = graph.vertices.get(start_vertex_id)
#         if vertex is None:
#             continue
#         vertex.values.append(wave_range)
#
#         queue = deque([start_vertex_id])
#         nullify = False
#
#         while queue:
#             current_id = queue.popleft()
#             current_vertex = graph.vertices[current_id]
#
#             for edge in current_vertex.outcoming_edges:
#                 neighbor_id = edge.end_vertex
#                 neighbor_vertex = graph.vertices[neighbor_id]
#                 if len(neighbor_vertex.values) == i:
#                     next_value = current_vertex.values[i] - 1 if nullify is False else 0
#                     if next_value <= 0:
#                         nullify = True
#                     neighbor_vertex.values.append(next_value)
#                     queue.append(neighbor_id)
#
#     min_val = INF
#     max_val = 0
#     for vertex in graph.vertices.values():
#         new_value = np.sum(vertex.values)
#         vertex.value = new_value
#         if new_value < min_val:
#             min_val = new_value
#         if new_value > max_val:
#             max_val = new_value
#
#     for vertex in graph.vertices.values():
#         vertex.value = (vertex.value - min_val) / (max_val - min_val)
#     return max_val, min_val


def run_points_tests(n=100, wave_range=100, increment=10):
    # gdfs = []
    points = []
    _gdf = initialize_wavefront_multi_dataframe(graph=Graph())
    for i in range(1, increment+1):
        print(i)
        n_points = n*i
        graph = Graph()
        vertices, starting_points = generate_initial_points(graph, n_points)
        max_value, min_value = wavefront_single(graph, vertices, wave_range=wave_range)
        # edge_gdf = create_wavefront_edge_geodataframe(graph)
        # gdfs.append(edge_gdf)
        points.append(starting_points)
        _gdf = update_wavefront_multi_dataframe(graph, _gdf)
    # for edge_gdf, starting_points in zip(gdfs, points):
    #     generate_wavefront_map(edge_gdf, "WaveFront", 1, starting_points)
    generate_wavefront_map2(_gdf, "WaveFront", 1, points)
    return gdfs


# n_points = 10
# wave_range = 80
# graph = Graph()
# vertices, starting_points = generate_initial_points(graph, n_points)
# max_value, min_value = wavefront_single(graph, vertices, wave_range=wave_range)
# edge_gdf = create_wavefront_edge_geodataframe(graph)
#
# generate_wavefront_map(edge_gdf, "WaveFront", 1, starting_points)

run_points_tests(n=10, wave_range=100, increment=2)





























#
#
# def find_shortest_path(graph, start_vertex_id, end_vertex_id):
#     distances = {vertex_id: INF for vertex_id in graph.vertices}
#     path = {vertex_id: None for vertex_id in graph.vertices}
#
#     distances[start_vertex_id] = 0
#     queue = deque([start_vertex_id])
#
#     while queue:
#         current_id = queue.popleft()
#         current_vertex = graph.vertices[current_id]
#
#         for edge in current_vertex.outcoming_edges:
#             neighbor_id = edge.end_vertex
#             if distances[neighbor_id] == INF:
#                 distances[neighbor_id] = distances[current_id] + 1
#                 path[neighbor_id] = current_id
#                 queue.append(neighbor_id)
#
#                 if neighbor_id == end_vertex_id:
#                     return reconstruct_path(path, start_vertex_id, end_vertex_id)
#
#     return None
#
#
# def reconstruct_path(path, start_vertex_id, end_vertex_id):
#     reverse_path = []
#     current_id = end_vertex_id
#     while current_id is not None:
#         reverse_path.append(current_id)
#         current_id = path[current_id]
#
#     return reverse_path[::-1]
