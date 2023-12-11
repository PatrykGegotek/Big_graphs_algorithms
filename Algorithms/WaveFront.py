import folium as folium
import random
import geopandas as gpd

from Data.Graph import Graph, Vertex
from collections import deque
from shapely.geometry import LineString
from Visualization.Visualization import get_color, get_cmap, generate_wavefront_map

INF = float('inf')


def create_edge_geodataframe(graph: Graph, distances):
    data = []

    for vertex_id, vertex in graph.vertices.items():
        for edge in vertex.outcoming_edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            distance = distances[vertex_id]
            if distance != INF:
                data.append({
                    'geometry': line,
                    'distance': distance,
                    'nodes': str(start_vertex.id) + '---' + str(end_vertex.id)
                })

    return gpd.GeoDataFrame(data, columns=['geometry', 'distance', 'nodes'])


def create_path_geodataframe(graph: Graph, verteces: [str]):
    data = []

    for i in range(len(verteces) - 1):
        start_id = verteces[i]
        end_id = verteces[i + 1]
        start_vertex = graph.vertices.get(start_id)
        end_vertex = graph.vertices.get(end_id)
        edges = start_vertex.outcoming_edges
        edge = [edge for edge in edges if edge.end_vertex == end_id][0]
        line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
        data.append({
            'geometry': line,
            'distance': i,
            'nodes': str(start_vertex.id) + '---' + str(end_vertex.id)
        })

    return gpd.GeoDataFrame(data, columns=['geometry', 'distance', 'nodes'])


def wavefront_single(graph: Graph):
    start_vertex_id = random.choice(list(graph.vertices.keys()))
    distances = {vertex_id: INF for vertex_id in graph.vertices}
    for vertex in graph.vertices.values():
        vertex.value = INF
    distances[start_vertex_id] = 0
    graph.vertices.get(start_vertex_id).value = 0

    queue = deque([start_vertex_id])

    while queue:
        print("Queue length:", len(queue))
        current_id = queue.popleft()
        current_vertex = graph.vertices[current_id]

        for edge in current_vertex.outcoming_edges:
            neighbor_id = edge.end_vertex
            if distances[neighbor_id] == INF:
                distances[neighbor_id] = distances[current_id] + 1
                graph.vertices.get(neighbor_id).value = distances[neighbor_id]
                queue.append(neighbor_id)

    for vertex_id, distance in distances.items():
        print(f"Odległość od wierzchołka {start_vertex_id} do {vertex_id} wynosi: {distance}")

    return distances


def wavefront_multiple(graph: Graph, n_sources: int):
    start_indexes = []
    for n in range(n_sources):
        start_indexes.append(random.choice(list(graph.vertices.keys())))
    distances = {vertex_id: INF for vertex_id in graph.vertices}
    for vertex in graph.vertices.values():
        vertex.value = INF
    for start_vertex_id in start_indexes:
        distances[start_vertex_id] = 0
        graph.vertices.get(start_vertex_id).value = 0

    queue = deque(start_indexes)
    # next_queue = None

    while queue:
        current_id = queue.popleft()
        current_vertex = graph.vertices[current_id]

        for edge in current_vertex.outcoming_edges:
            neighbor_id = edge.end_vertex
            if distances[neighbor_id] > distances[current_id] + 1:
                distances[neighbor_id] = distances[current_id] + 1
                graph.vertices.get(neighbor_id).value = distances[neighbor_id]
                queue.append(neighbor_id)

    return distances


def find_shortest_path(graph, start_vertex_id, end_vertex_id):
    distances = {vertex_id: INF for vertex_id in graph.vertices}
    path = {vertex_id: None for vertex_id in graph.vertices}

    distances[start_vertex_id] = 0
    queue = deque([start_vertex_id])

    while queue:
        current_id = queue.popleft()
        current_vertex = graph.vertices[current_id]

        for edge in current_vertex.outcoming_edges:
            neighbor_id = edge.end_vertex
            if distances[neighbor_id] == INF:
                distances[neighbor_id] = distances[current_id] + 1
                path[neighbor_id] = current_id
                queue.append(neighbor_id)

                if neighbor_id == end_vertex_id:
                    return reconstruct_path(path, start_vertex_id, end_vertex_id)

    return None


def reconstruct_path(path, start_vertex_id, end_vertex_id):
    reverse_path = []
    current_id = end_vertex_id
    while current_id is not None:
        reverse_path.append(current_id)
        current_id = path[current_id]

    return reverse_path[::-1]


graph = Graph()

# path = None
# while path is None:
#     start_vertex_id = random.choice(list(graph.vertices.keys()))
#     start_vertex_id2 = random.choice(list(graph.vertices.keys()))
#     path = find_shortest_path(graph, start_vertex_id, start_vertex_id2)
#
# gdf = create_path_geodataframe(graph, path)



# Oblicz odległości

distances = wavefront_single(graph)
# distances = wavefront_multiple(graph, 8)

edge_gdf = create_edge_geodataframe(graph, distances)

generate_wavefront_map(edge_gdf, "WaveFront")
