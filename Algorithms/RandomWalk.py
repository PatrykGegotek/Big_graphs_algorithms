import random
import time

import numpy as np
import geopandas as gpd
import pandas as pd
from matplotlib import pyplot as plt
from shapely import LineString
from Data.Graph import Graph, Edge, Vertex
from Visualization.Visualization import generate_random_walk_map


def create_edge_geodataframe(graph: Graph):
    data = []
    max_value = 0
    sum = 0
    i = 0

    for vertex_id, vertex in graph.vertices.items():
        for edge in vertex.outcoming_edges:
            if edge.value == 0:
                continue
            if edge.value > max_value:
                max_value = edge.value
            sum += edge.value
            i += 1
            # print(edge.value)
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            data.append({
                'geometry': line,
                'distance': edge.value,
                'nodes': str(start_vertex.id) + '---' + str(end_vertex.id)
            })

    average = sum/i

    return gpd.GeoDataFrame(data, columns=['geometry', 'distance', 'nodes']), average, max_value, i


def create_plots(grouped_df):
    plt.figure(figsize=(12, 8))

    for val in grouped_df['max_value']['mean']:
        print(val)

    sigmas = [str(sigma) for sigma in grouped_df['sigma']]

    # Średnia wartość i odchylenie standardowe dla "average_value" w zależności od "sigma"
    plt.subplot(2, 2, 1)
    plt.bar(sigmas, grouped_df['average_value']['mean'], yerr=grouped_df['average_value']['std'],
            align='center', alpha=0.5)
    plt.xlabel('Sigma')
    plt.ylabel('Średnia wartość')
    plt.title('Średnia wartość w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "max_value" w zależności od "sigma"
    plt.subplot(2, 2, 2)
    plt.bar(sigmas, grouped_df['max_value']['mean'], yerr=grouped_df['max_value']['std'], align='center',
            alpha=0.5)
    plt.xlabel('Sigma')
    plt.ylabel('Maksymalna wartość')
    plt.title('Maksymalna wartość w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "seconds" w zależności od "sigma"
    plt.subplot(2, 2, 3)
    plt.bar(sigmas, grouped_df['seconds']['mean'], yerr=grouped_df['seconds']['std'], align='center',
            alpha=0.5)
    plt.xlabel('Sigma')
    plt.ylabel('Czas (sekundy)')
    plt.title('Czas w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "n_visited_edges" w zależności od "sigma"
    plt.subplot(2, 2, 4)
    plt.bar(sigmas, grouped_df['n_visited_edges']['mean'], yerr=grouped_df['n_visited_edges']['std'],
            align='center', alpha=0.5)
    plt.xlabel('Sigma')
    plt.ylabel('Liczba odwiedzonych krawędzi')
    plt.title('Liczba odwiedzonych krawędzi w zależności od sigma')

    plt.tight_layout()
    plt.show()

def generate_initial_points(graph, num):
    points = []
    for i in range(num):
        vertex = random.choice(list(graph.vertices.keys()))
        points.append((vertex, 1.0))
    return points


# def random_walk(graph: Graph, n_steps):
    # current_index = random.choice(list(graph.vertices.keys()))
    # previous_index = current_index
    # max_value = 0
    #
    # for i in range(n_steps):
    #     print(f'{i}')
    #     vertex = graph.vertices.get(current_index)
    #     vertex.value += 1
    #     edges = vertex.outcoming_edges
    #     if len(edges) == 0:
    #         print('break')
    #         break
    #     chosen_edge = random.choice(edges)
    #     # while len(edges) > 1 and chosen_edge.end_vertex == previous_index:
    #     #     print("Poprawka")
    #     #     chosen_edge = random.choice(edges)
    #     chosen_edge.value += 1
    #     if chosen_edge.value > max_value:
    #         max_value = chosen_edge.value
    #     previous_index = current_index
    #     current_index = chosen_edge.end_vertex
    #
    # return create_edge_geodataframe(graph), max_value


def gaussian_decay(distance, sigma=500):
    return np.exp(-0.5 * (distance / sigma) ** 2)


def random_walk_with_decay(graph, start_vertices, sigma):
    start_time = time.time()
    for start_vertex_id, start_value in start_vertices:
        current_vertex_id = start_vertex_id
        distance = 0

        while True:
            current_vertex = graph.vertices[current_vertex_id]

            new_value = gaussian_decay(distance, sigma)

            if current_vertex.outcoming_edges:
                edge = random.choice(current_vertex.outcoming_edges + current_vertex.incoming_edges)
                distance += edge.meters
                edge.value += start_value * new_value
                current_vertex_id = edge.end_vertex
            else:
                break

            if new_value < 0.01:  # Próg odcięcia
                break
    end_time = time.time()
    duration = end_time - start_time  # Sekundy

    return create_edge_geodataframe(graph), duration


def sigma_tests(initial_value, multipliers, n_points, repetitions, variant=0):
    data = {
        "sigma": [], "num": [], "average_value": [], "max_value": [], "n_visited_edges": [], "seconds": []
    }
    for multiplier in range(1, multipliers+1):
        if variant == 0:
            sigma = initial_value * 2**multiplier
        else:
            sigma = initial_value * multiplier
        print(f"Sigma: {sigma}")
        for i in range(repetitions):
            graph = Graph()
            start_vertices = generate_initial_points(graph, n_points)
            (gdf, average_value, max_value, n_visited_edges), seconds = random_walk_with_decay(graph, start_vertices, sigma)
            data["sigma"].append(sigma)
            data["num"].append(i)
            data["average_value"].append(average_value)
            data["max_value"].append(max_value)
            data["n_visited_edges"].append(n_visited_edges)
            data["seconds"].append(seconds)

    df = pd.DataFrame(data)
    grouped_df = df.groupby('sigma').agg({'average_value': ['mean', 'std'],
                                          'max_value': ['mean', 'std'],
                                          'seconds': ['mean', 'std'],
                                          'n_visited_edges': ['mean', 'std']}).reset_index()
    print(df)
    print(grouped_df)
    create_plots(grouped_df)


pd.set_option('display.max_columns', None)
# sigma_tests(initial_value=500, multipliers=8, n_points=200, repetitions=20, variant=0)
sigma_tests(initial_value=5000, multipliers=10, n_points=100, repetitions=15, variant=1)

# graph = Graph()
# start_vertices = generate_initial_points(200)
# sigma = 32000  # Parametr funkcji Gaussa
# (gdf, max_value), seconds = random_walk_with_decay(graph, start_vertices, sigma)
# print(seconds)
# generate_random_walk_map(gdf, "RandomWalk", max_value)

#
# gdf, max_value = random_walk(graph, 500000)
# generate_random_walk_map(gdf, "RandomWalk", max_value)
# print(gdf)
