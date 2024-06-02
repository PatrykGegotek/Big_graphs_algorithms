import random

import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt

from Data.Graph import Graph
from collections import deque
from Visualization.Visualization import generate_wavefront_map, create_wavefront_edge_geodataframe, \
    initialize_wavefront_multi_dataframe, update_wavefront_multi_dataframe, generate_wavefront_map2

INF = float('inf')


def euclidean_distance(vec1, vec2):
    return np.linalg.norm(np.array(vec1) - np.array(vec2))


def gaussian_decay(distance, sigma=500):
    return np.exp(-0.5 * (distance / sigma) ** 2)


def visualize_norms(_gdf, labels, axis_labels):
    num_maps = len(_gdf['distance'].iloc[0])
    vectors = {i: [] for i in range(num_maps)}

    for _, row in _gdf.iterrows():
        for idx, value in enumerate(row['distance']):
            vectors[idx].append(value)

    distance_matrix = np.zeros((num_maps, num_maps))

    for i in range(num_maps):
        for j in range(num_maps):
            distance_matrix[i, j] = euclidean_distance(vectors[i], vectors[j])

    # distance_matrix = distance_matrix.astype(int)
    # sns.heatmap(distance_matrix, annot=True, cmap='Blues', xticklabels=labels, yticklabels=labels, fmt="d")
    plt.figure(figsize=(10, 6))  # Zwiększ tutaj pierwszą wartość dla większej szerokości
    sns.heatmap(distance_matrix, annot=True, cmap='Blues', xticklabels=labels, yticklabels=labels, fmt="0.1f")
    plt.title('Macierz odległości')
    plt.xlabel(axis_labels)
    plt.ylabel(axis_labels)
    plt.show()


def generate_initial_points(graph, num):
    vertices = []
    points = []
    for i in range(num):
        vertex = random.choice(list(graph.vertices.values()))
        vertices.append(vertex.id)
        points.append((vertex.y, vertex.x))
    return vertices, points


def wavefront_single(graph: Graph, vertices, wave_range=100, initial_value=100):
    for i, start_vertex_id in enumerate(vertices):
        vertex = graph.vertices.get(start_vertex_id)
        if vertex is None:
            continue
        vertex.values.append(initial_value)

        queue = deque([(start_vertex_id, 0)])
        for vertex in graph.vertices.values():
            vertex.active = True

        while queue:
            current_id, left_range = queue.popleft()
            current_vertex = graph.vertices[current_id]

            for edge in current_vertex.outcoming_edges:
                neighbor_id = edge.end_vertex
                neighbor_vertex = graph.vertices[neighbor_id]
                left_range += edge.meters
                next_value = gaussian_decay(left_range, wave_range)
                if next_value > 0.01 and neighbor_vertex.active:
                    neighbor_vertex.value += next_value
                    neighbor_vertex.active = False
                    queue.append((neighbor_id, left_range))

    min_val = INF
    max_val = 0
    for vertex in graph.vertices.values():
        new_value = vertex.value
        vertex.value = new_value
        if new_value < min_val:
            min_val = new_value
        if new_value > max_val:
            max_val = new_value

    for vertex in graph.vertices.values():
        vertex.value = (vertex.value - min_val) / (max_val - min_val)
    return max_val, min_val


def run_points_tests(n=100, wave_range=100, increment=10, step=2):
    points = []
    _gdf = initialize_wavefront_multi_dataframe(graph=Graph())
    labels = []
    prev_prev = 0
    prev = n
    for i in range(increment):
        n_points = prev + prev_prev
        prev_prev = prev
        prev = n_points
        print(n_points)
        labels.append(str(n_points//100))
        graph = Graph()
        vertices, starting_points = generate_initial_points(graph, n_points)
        max_value, min_value = wavefront_single(graph, vertices, wave_range=wave_range)
        points.append(starting_points)
        _gdf = update_wavefront_multi_dataframe(graph, _gdf)
    visualize_norms(_gdf, labels=labels, axis_labels='Liczba węzłów (x100)')
    # generate_wavefront_map(_gdf, "WaveFront", 1, labels)
    return _gdf


def run_range_tests(n=100, wave_range=100, increment=10, step=2):
    points = []
    graph = Graph()
    _gdf = initialize_wavefront_multi_dataframe(graph=graph)
    vertices, starting_points = generate_initial_points(graph, n)
    labels = []
    additional_names = []
    prev_prev = 0
    prev = wave_range
    for i in range(increment):
        _wave_range = prev + prev_prev
        prev_prev = prev
        prev = _wave_range
        print(_wave_range)
        points.append(starting_points)
        labels.append(str(_wave_range//1000))
        graph = Graph()
        max_value, min_value = wavefront_single(graph, vertices, wave_range=_wave_range)
        _gdf = update_wavefront_multi_dataframe(graph, _gdf)
    # visualize_norms(_gdf, labels=labels, axis_labels='Zasięg [km]')
    generate_wavefront_map2(_gdf, "WaveFront", 1, points, labels)
    return _gdf


# run_range_tests(n=100, wave_range=1000, increment=4, step=2)
# run_points_tests(n=200, wave_range=1000, increment=10, step=2)

for i in range(5):
    run_range_tests(n=3, wave_range=3500, increment=1)

# graph = Graph()
# points = []
# labels = []
# _gdf = initialize_wavefront_multi_dataframe(graph=graph)
# vertices, starting_points = generate_initial_points(graph, 1)
# points.append(starting_points)
# wavefront_single(graph, vertices, wave_range=5000)
# _gdf = update_wavefront_multi_dataframe(graph, _gdf)
# labels.append(str(1))
# generate_wavefront_map2(_gdf, "WaveFront", 1, points, labels)




























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
