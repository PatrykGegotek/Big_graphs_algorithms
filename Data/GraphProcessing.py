import pickle
import random
from collections import deque
from Data.Graph import Graph

GRAPH_PATH = "C:\\Users\\patryk\\Desktop\\Inżynierka\\Algorithms implementation\\Data\\Graph_Data.pkl"


def find_biggest_graph(graph: Graph):
    INF = float('inf')
    # start_vertex_id = random.choice(list(graph.vertices.keys()))
    start_vertex_id = "64218"
    print(f"Chosen: {start_vertex_id}")
    for vertex in graph.vertices.values():
        vertex.value = INF
    graph.vertices.get(start_vertex_id).value = 0

    queue = deque([start_vertex_id])

    while queue:
        current_id = queue.popleft()
        current_vertex = graph.vertices[current_id]

        for edge in current_vertex.outcoming_edges + current_vertex.incoming_edges:
            edge.value = 1
            neighbor_id = edge.end_vertex
            if graph.vertices[neighbor_id].value == INF:
                graph.vertices[neighbor_id].value = 0
                queue.append(neighbor_id)

    return graph


def create_pure_data(graph: Graph):
    graph = find_biggest_graph(graph)
    graph_list = []  # start_point, end_point, source, target, highway, oneway, weight
    for edge in graph.edges:
        if edge.value == 1 and edge.duplicate is False:
            start = graph.vertices[edge.start_vertex]
            end = graph.vertices[edge.end_vertex]
            graph_list.append([[start.x, start.y], [end.x, end.y], start.id, end.id, None, edge.oneway, edge.weight])

    print(f"Result length: {len(graph_list)}")

    with open(GRAPH_PATH, 'wb') as file:
        pickle.dump(graph_list, file)

create_pure_data(graph=Graph())
