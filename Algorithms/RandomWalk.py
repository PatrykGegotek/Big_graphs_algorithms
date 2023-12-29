import random
import time

import numpy as np
import pandas as pd
from Data.Graph import Graph
from Visualization.Visualization import generate_random_walk_map, create_sigma_plots, create_samples_plots, \
    create_random_walk_edge_geodataframe


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

    return create_random_walk_edge_geodataframe(graph), duration


def sigma_tests(initial_value, multipliers, n_points, repetitions, variant=0):
    data = {
        "sigma": [], "num": [], "average_value": [], "max_value": [], "n_visited_edges": [], "seconds": []
    }
    gdfs = []
    for multiplier in range(1, multipliers + 1):
        if variant == 0:
            sigma = initial_value * 2 ** (multiplier - 1)
        else:
            sigma = initial_value * multiplier
        print(f"Sigma: {sigma}")
        for i in range(repetitions):
            graph = Graph()
            start_vertices = generate_initial_points(graph, n_points)
            (gdf, average_value, max_value, n_visited_edges), seconds = random_walk_with_decay(graph, start_vertices,
                                                                                               sigma)
            data["sigma"].append(sigma)
            data["num"].append(i)
            data["average_value"].append(average_value)
            data["max_value"].append(max_value)
            data["n_visited_edges"].append(n_visited_edges)
            data["seconds"].append(seconds)
            if i == 0:
                gdfs.append((sigma, average_value, gdf))

    df = pd.DataFrame(data)
    grouped_df = df.groupby('sigma').agg({'average_value': ['mean', 'std'],
                                          'max_value': ['mean', 'std'],
                                          'seconds': ['mean', 'std'],
                                          'n_visited_edges': ['mean', 'std']}).reset_index()
    create_sigma_plots(grouped_df)
    for sigma, mean, gdf in gdfs:
        generate_random_walk_map(gdf, f"Random_Walk_Sigma={sigma}", mean * 2)


def samples_tests(initial_value, multipliers, sigma, repetitions):
    data = {
        "samples": [], "num": [], "average_value": [], "max_value": [], "n_visited_edges": [], "seconds": []
    }
    gdfs = []
    for multiplier in range(1, multipliers + 1):
        samples = initial_value * multiplier
        print(f"Samples: {samples}")
        for i in range(repetitions):
            graph = Graph()
            start_vertices = generate_initial_points(graph, samples)
            (gdf, average_value, max_value, n_visited_edges), seconds = random_walk_with_decay(graph, start_vertices,
                                                                                               sigma)
            data["samples"].append(samples)
            data["num"].append(i)
            data["average_value"].append(average_value)
            data["max_value"].append(max_value)
            data["n_visited_edges"].append(n_visited_edges)
            data["seconds"].append(seconds)
            if i == 0:
                gdfs.append((sigma, average_value, gdf))

    df = pd.DataFrame(data)
    grouped_df = df.groupby('samples').agg({'average_value': ['mean', 'std'],
                                            'max_value': ['mean', 'std'],
                                            'seconds': ['mean', 'std'],
                                            'n_visited_edges': ['mean', 'std']}).reset_index()
    create_samples_plots(grouped_df)
    # for sigma, mean, gdf in gdfs:
    #     generate_random_walk_map(gdf, f"Random_Walk_Sigma={sigma}", mean * 2)


pd.set_option('display.max_columns', None)
# sigma_tests(initial_value=500, multipliers=8, n_points=200, repetitions=20, variant=0)
# sigma_tests(initial_value=5000, multipliers=12, n_points=100, repetitions=20, variant=1)
samples_tests(initial_value=500, multipliers=12, sigma=1000, repetitions=20)

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
