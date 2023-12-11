import random
import geopandas as gpd
from shapely import LineString
from Data.Graph import Graph, Edge, Vertex
from Visualization.Visualization import generate_random_walk_map


def create_edge_geodataframe(graph: Graph):
    data = []

    for vertex_id, vertex in graph.vertices.items():
        for edge in vertex.outcoming_edges:
            if edge.value == 0:
                continue
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            data.append({
                'geometry': line,
                'distance': edge.value,
                'nodes': str(start_vertex.id) + '---' + str(end_vertex.id)
            })

    return gpd.GeoDataFrame(data, columns=['geometry', 'distance', 'nodes'])


def random_walk(graph: Graph, n_steps):
    current_index = random.choice(list(graph.vertices.keys()))
    previous_index = current_index
    max_value = 0

    for i in range(n_steps):
        print(f'{i}')
        vertex = graph.vertices.get(current_index)
        vertex.value += 1
        edges = vertex.outcoming_edges
        if len(edges) == 0:
            print('break')
            break
        chosen_edge = random.choice(edges)
        # while len(edges) > 1 and chosen_edge.end_vertex == previous_index:
        #     print("Poprawka")
        #     chosen_edge = random.choice(edges)
        chosen_edge.value += 1
        if chosen_edge.value > max_value:
            max_value = chosen_edge.value
        previous_index = current_index
        current_index = chosen_edge.end_vertex

    return create_edge_geodataframe(graph), max_value


graph = Graph()
gdf, max_value = random_walk(graph, 500000)
generate_random_walk_map(gdf, "RandomWalk", max_value)
print(gdf)
