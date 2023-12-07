import folium as folium

from Data.Graph import Graph, Vertex
from collections import deque
import random
import geopandas as gpd
from shapely.geometry import LineString

from Visualization.Visualization import get_color, get_cmap

INF = float('inf')



def create_edge_geodataframe(graph :Graph, distances):
    """
    Tworzy GeoDataFrame zawierający krawędzie i odległości od wierzchołka startowego.

    :param graph: Obiekt grafu.
    :param distances: Słownik odległości obliczonych przez algorytm Wavefront.
    :return: GeoDataFrame z krawędziami i odległościami.
    """
    data = []

    for vertex_id, vertex in graph.vertices.items():
        for edge in vertex.outcoming_edges:
            # Odległość wierzchołka początkowego krawędzi
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


def create_path_geodataframe(graph :Graph, verteces: [str]):
    """
    Tworzy GeoDataFrame zawierający krawędzie i odległości od wierzchołka startowego.

    :param graph: Obiekt grafu.
    :param distances: Słownik odległości obliczonych przez algorytm Wavefront.
    :return: GeoDataFrame z krawędziami i odległościami.
    """
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


def wavefront(graph :Graph, start_vertex_id):
    """
    Oblicza odległość od wybranego wierzchołka do wszystkich innych wierzchołków w grafie.

    :param graph: Obiekt grafu.
    :param start_vertex_id: ID wierzchołka startowego.
    :return: Słownik odległości od wierzchołka startowego do każdego innego wierzchołka.
    """
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

        # for edge in current_vertex.incoming_edges:
        #     neighbor_id = edge.start_vertex
        #     if distances[neighbor_id] == INF:
        #         distances[neighbor_id] = distances[current_id] + 1
        #         graph.vertices.get(neighbor_id).value = distances[neighbor_id]
        #         queue.append(neighbor_id)

    return distances

def find_shortest_path(graph, start_vertex_id, end_vertex_id):
    """
    Znajduje najkrótszą ścieżkę pomiędzy dwoma wierzchołkami w grafie.

    :param graph: Obiekt grafu.
    :param start_vertex_id: ID wierzchołka startowego.
    :param end_vertex_id: ID wierzchołka docelowego.
    :return: Lista reprezentująca najkrótszą ścieżkę (wierzchołki od startowego do docelowego), None jeśli ścieżka nie istnieje.
    """
    INF = float('inf')
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
    """
    Odtwarza ścieżkę od wierzchołka startowego do docelowego.

    :param path: Słownik ścieżek.
    :param start_vertex_id: ID wierzchołka startowego.
    :param end_vertex_id: ID wierzchołka docelowego.
    :return: Lista reprezentująca ścieżkę.
    """
    reverse_path = []
    current_id = end_vertex_id
    while current_id is not None:
        reverse_path.append(current_id)
        current_id = path[current_id]

    return reverse_path[::-1]  # Odwrócenie ścieżki

# Przykład użycia
graph = Graph()
# Dodawanie wierzchołków i krawędzi do grafu...

# Wybierz losowy wierzchołek jako startowy
path = None
while path == None:
    start_vertex_id = random.choice(list(graph.vertices.keys()))
    start_vertex_id2 = random.choice(list(graph.vertices.keys()))
    print("Selected_vertex: ", start_vertex_id)
    print("Selected_vertex2: ", start_vertex_id2)
    # start_vertex_id = '21768'
    # start_vertex_id2 = '24217'

    path = find_shortest_path(graph, start_vertex_id, start_vertex_id2)
print(path)
gdf = create_path_geodataframe(graph, path)
print(gdf)

mapa = folium.Map(location=[50.050, 19.941], zoom_start=12)

for _, row in gdf.iterrows():
    folium.PolyLine(
        locations=[(y, x) for x, y in row['geometry'].coords],
        color=get_color(row['distance'], len(path), get_cmap()),
        weight=2
    ).add_to(mapa)

mapa.save(f'Distance.html')
import webbrowser

webbrowser.open(f'Distance.html')

# # Oblicz odległości
# distances = wavefront(graph, start_vertex_id)
#
# # Wyświetl wyniki
# for vertex_id, distance in distances.items():
#     print(f"Odległość od wierzchołka {start_vertex_id} do {vertex_id} wynosi: {distance}")
#
# edge_gdf = create_edge_geodataframe(graph, distances)
#
# print(edge_gdf)
#
#
# mapa = folium.Map(location=[50.050, 19.941], zoom_start=12)
#
# for _, row in edge_gdf.iterrows():
#     folium.PolyLine(
#         locations=[(y, x) for x, y in row['geometry'].coords],
#         color=get_color(row['distance'], 200, get_cmap()),
#         weight=2
#     ).add_to(mapa)
#
# mapa.save(f'Distance.html')
# import webbrowser
#
# webbrowser.open(f'Distance.html')

