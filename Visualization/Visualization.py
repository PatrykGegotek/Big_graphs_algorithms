import folium
import geopandas as gpd
import matplotlib.colors as mcolors
import webbrowser
from scipy.stats import linregress

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from shapely import LineString

from Data.Graph import Graph

INF = float('inf')
DIRECTORY = "../Generated_Maps"
ABSOLUTE_PATH = "C:\\Users\\patryk\\Desktop\\Inżynierka\\Algorithms implementation\\Generated_Maps"


############################ PREGEL ########################################

def initialize_dataframe(graph):
    rows = []
    for vertex in graph.vertices.values():
        for edge in vertex.outcoming_edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            edge_id = edge.id
            oneway = edge.oneway
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            rows.append({'start': edge.start_vertex,
                         'end': edge.end_vertex,
                         'edge_id': edge_id,
                         'oneway': oneway,
                         'geometry': line,
                         'traffic': []})
    return gpd.GeoDataFrame(rows, columns=['start', 'end', 'edge_id', 'oneway', 'geometry', 'traffic'])


def update_dataframe(graph, gdf):
    for i, row in gdf.iterrows():
        start_vertex_id = row['start']
        end_vertex_id = row['end']
        start_vertex = graph.vertices[start_vertex_id]
        end_vertex = graph.vertices[end_vertex_id]

        edge_traffic = (start_vertex.value + end_vertex.value) / 2
        row['traffic'].append(edge_traffic)
    return gdf


def process_dataframe(df):
    oneway_edges = df[df['oneway']].copy()

    twoway_edges = df[~df['oneway']]
    grouped = twoway_edges.groupby('edge_id').agg({
        'start': 'first',
        'end': 'first',
        'traffic': lambda x: [sum(y) for y in zip(*x)],
        'geometry': 'first'
    }).reset_index(drop=True)

    # Łączenie wyników
    new_df = pd.concat([oneway_edges, grouped], ignore_index=True)
    return gpd.GeoDataFrame(new_df)


def generate_overlayed_pregel_plots(dfs):
    plt.figure(figsize=(14, 4))  # Adjusted for a single row of plots

    colors = ['blue', 'red', 'green', 'orange', 'purple']  # Colors for different lines
    labels = ['1. wersja', '2. wersja']
    trends = ['Trend dla 1. wersji', 'Trend dla 2. wersji']

    # Wykres liczby wysłanych wiadomości
    plt.subplot(1, 3, 1)
    for i, df in enumerate(dfs):
        plt.plot(df['Sent Messages'], color=colors[i % len(colors)], label=labels[i % len(labels)])
    plt.title('Liczba wysłanych wiadomości')
    plt.xlabel('Superkrok')
    plt.ylabel('Wysłane wiadomości')
    plt.legend()

    # Wykres active vertices
    plt.subplot(1, 3, 2)
    for i, df in enumerate(dfs):
        plt.plot(df['Active Vertices'], color=colors[i % len(colors)], label=labels[i % len(labels)])
    plt.title('Liczba aktywnych wierzchołków')
    plt.xlabel('Superkrok')
    plt.ylabel('Aktywne wierzchołki')
    plt.legend()

    # Wykres zależności duration od active vertices
    plt.subplot(1, 3, 3)
    for i, df in enumerate(dfs):
        active_vertices = df['Active Vertices']
        duration = df['Duration']
        plt.scatter(active_vertices, duration, color=colors[i % len(colors)], label=labels[i % len(labels)], alpha=0.5)

    plt.title('Zależność czasu od liczby wierzchołków')
    plt.xlabel('Aktywne wierzchołki')
    plt.ylabel('Czas [s]')
    plt.legend()

    # Wyświetlenie wykresów
    plt.tight_layout()
    plt.show()


def generate_pregel_map(gdf, name, steps, leap=1):
    to_generate = range_between(0, steps-1, leap)
    print(to_generate)
    for i in to_generate:
        print(i)
        mapa = folium.Map(location=[50.050, 19.941], zoom_start=12)

        for _, row in gdf.iterrows():
            if row['traffic'][i] == 0:
                continue
            folium.PolyLine(
                locations=[(y, x) for x, y in row['geometry'].coords],
                color=get_color(row['traffic'][i], 60, get_cmap()),
                weight=2
            ).add_to(mapa)

        mapa.save(f'{DIRECTORY}/{name}_step_{i}.html')
        webbrowser.open(f'{ABSOLUTE_PATH}/{name}_step_{i}.html')


######################## WAVEFRONT ###########################


def initialize_wavefront_multi_dataframe(graph):
    rows = []
    for vertex in graph.vertices.values():
        for edge in vertex.outcoming_edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            edge_id = edge.id
            oneway = edge.oneway
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            rows.append({'start': edge.start_vertex,
                         'end': edge.end_vertex,
                         'edge_id': edge_id,
                         'oneway': oneway,
                         'geometry': line,
                         'distance': []})
    return gpd.GeoDataFrame(rows, columns=['start', 'end', 'edge_id', 'oneway', 'geometry', 'distance'])


def update_wavefront_multi_dataframe(graph, gdf):
    for i, row in gdf.iterrows():
        start_vertex_id = row['start']
        start_vertex = graph.vertices[start_vertex_id]
        edge_traffic = start_vertex.value
        row['distance'].append(edge_traffic)
    return gdf


def create_wavefront_edge_geodataframe(graph: Graph):
    data = []

    for vertex_id, vertex in graph.vertices.items():
        for edge in vertex.outcoming_edges:
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            distance = graph.vertices[edge.end_vertex].value
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


def generate_wavefront_map(gdf, name, max_value, start_points):
    mapa = folium.Map(location=[50.050, 19.941], zoom_start=13)

    for _, row in gdf.iterrows():
        if row['distance'] == 0:
            continue
        folium.PolyLine(
            locations=[(y, x) for x, y in row['geometry'].coords],
            color=get_color(row['distance'], max_value, get_cmap()),
            weight=2
        ).add_to(mapa)

    for point in start_points:
        folium.CircleMarker(
            location=point,  # Współrzędne punktu (lat, lon)
            color='purple',
            fill=True,
            fill_color='purple',
            radius=5  # Rozmiar markera
        ).add_to(mapa)

    mapa.save(f'{DIRECTORY}/{name}.html')
    webbrowser.open(f'{ABSOLUTE_PATH}/{name}.html')


def generate_wavefront_map2(gdf, name, max_value, start_points):
    mapa = folium.Map(location=[50.050, 19.941], zoom_start=13)
    print(gdf)

    for i in range(len(gdf['distance'].iloc[0])):
        for _, row in gdf.iterrows():
            if row['distance'][i] == 0:
                continue
            folium.PolyLine(
                locations=[(y, x) for x, y in row['geometry'].coords],
                color=get_color(row['distance'][i], max_value, get_cmap()),
                weight=2
            ).add_to(mapa)

        for point in start_points[i]:
            folium.CircleMarker(
                location=point,  # Współrzędne punktu (lat, lon)
                color='purple',
                fill=True,
                fill_color='purple',
                radius=5  # Rozmiar markera
            ).add_to(mapa)

        mapa.save(f'{DIRECTORY}/{name}_{i}.html')
        webbrowser.open(f'{ABSOLUTE_PATH}/{name}_{i}.html')


###################### RANDOM WALK ###########################

def create_random_walk_edge_geodataframe(graph: Graph):
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
            start_vertex = graph.vertices[edge.start_vertex]
            end_vertex = graph.vertices[edge.end_vertex]
            line = LineString([(start_vertex.x, start_vertex.y), (end_vertex.x, end_vertex.y)])
            data.append({
                'geometry': line,
                'distance': edge.value,
                'nodes': str(start_vertex.id) + '---' + str(end_vertex.id)
            })

    average = sum / i

    return gpd.GeoDataFrame(data, columns=['geometry', 'distance', 'nodes']), average, max_value, i


def generate_random_walk_map(gdf, name, max_value):
    mapa = folium.Map(location=[50.050, 19.941], zoom_start=12)

    for _, row in gdf.iterrows():
        folium.PolyLine(
            locations=[(y, x) for x, y in row['geometry'].coords],
            color=get_color(row['distance'], max_value, get_cmap()),
            weight=3
        ).add_to(mapa)

    mapa.save(f'{DIRECTORY}/{name}.html')
    webbrowser.open(f'{ABSOLUTE_PATH}/{name}.html')


def create_sigma_plots(grouped_df):
    plt.figure(figsize=(12, 8))

    for val in grouped_df['max_value']['mean']:
        print(val)

    sigmas = [str(sigma / 1000) for sigma in grouped_df['sigma']]

    # Średnia wartość i odchylenie standardowe dla "average_value" w zależności od "sigma"
    plt.subplot(2, 2, 1)
    plt.bar(sigmas, grouped_df['average_value']['mean'], yerr=grouped_df['average_value']['std'],
            align='center', alpha=0.5)
    plt.xlabel('Sigma [km]')
    plt.ylabel('Średnia wartość')
    plt.title('Średnia wartość w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "max_value" w zależności od "sigma"
    plt.subplot(2, 2, 2)
    plt.bar(sigmas, grouped_df['max_value']['mean'], yerr=grouped_df['max_value']['std'], align='center',
            alpha=0.5, color='red')
    plt.xlabel('Sigma [km]')
    plt.ylabel('Maksymalna wartość')
    plt.title('Maksymalna wartość w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "seconds" w zależności od "sigma"
    plt.subplot(2, 2, 3)
    plt.bar(sigmas, grouped_df['seconds']['mean'], yerr=grouped_df['seconds']['std'], align='center',
            alpha=0.5, color='green')
    plt.xlabel('Sigma [km]')
    plt.ylabel('Czas (sekundy)')
    plt.title('Czas w zależności od sigma')

    # Średnia wartość i odchylenie standardowe dla "n_visited_edges" w zależności od "sigma"
    plt.subplot(2, 2, 4)
    plt.bar(sigmas, grouped_df['n_visited_edges']['mean'], yerr=grouped_df['n_visited_edges']['std'],
            align='center', alpha=0.5, color='purple')
    plt.xlabel('Sigma [km]')
    plt.ylabel('Liczba odwiedzonych krawędzi')
    plt.title('Liczba odwiedzonych krawędzi w zależności od sigma')

    plt.tight_layout()
    plt.show()


def create_samples_plots(grouped_df):
    plt.figure(figsize=(12, 8))

    sigmas = [str(sigma / 1000) for sigma in grouped_df['samples']]

    # Średnia wartość i odchylenie standardowe dla "average_value" w zależności od "sigma"
    plt.subplot(2, 2, 1)
    plt.bar(sigmas, grouped_df['average_value']['mean'], yerr=grouped_df['average_value']['std'],
            align='center', alpha=0.5)
    plt.xlabel('Liczba punktów startowych [tys]')
    plt.ylabel('Średnia wartość')
    plt.title('Średnia wartość w zależności od liczby punktów')

    # Średnia wartość i odchylenie standardowe dla "max_value" w zależności od "sigma"
    plt.subplot(2, 2, 2)
    plt.bar(sigmas, grouped_df['max_value']['mean'], yerr=grouped_df['max_value']['std'], align='center',
            alpha=0.5, color='red')
    plt.xlabel('Liczba punktów startowych [tys]')
    plt.ylabel('Maksymalna wartość')
    plt.title('Maksymalna wartość w zależności od liczby punktów')

    # Średnia wartość i odchylenie standardowe dla "seconds" w zależności od "sigma"
    plt.subplot(2, 2, 3)
    plt.bar(sigmas, grouped_df['seconds']['mean'], yerr=grouped_df['seconds']['std'], align='center',
            alpha=0.5, color='green')
    plt.xlabel('Liczba punktów startowych [tys]')
    plt.ylabel('Czas (sekundy)')
    plt.title('Czas w zależności od liczby punktów')

    # Średnia wartość i odchylenie standardowe dla "n_visited_edges" w zależności od "sigma"
    plt.subplot(2, 2, 4)
    plt.bar(sigmas, grouped_df['n_visited_edges']['mean'], yerr=grouped_df['n_visited_edges']['std'],
            align='center', alpha=0.5, color='purple')
    plt.xlabel('Liczba punktów startowych [tys]')
    plt.ylabel('Liczba odwiedzonych krawędzi')
    plt.title('Liczba odwiedzonych krawędzi w zależności od liczby punktów')

    plt.tight_layout()
    plt.show()


###################### OTHER #####################

def get_color(traffic_value, max_traffic, cmap):
    normalized_value = traffic_value / max_traffic
    return mcolors.to_hex(cmap(normalized_value))


def get_color2(traffic_value, max_traffic):
    normalized_value = traffic_value / max_traffic
    return mcolors.to_hex(mcolors.rgb_to_hsv(mcolors.to_rgb('green')) * (1 - normalized_value) + mcolors.rgb_to_hsv(
        mcolors.to_rgb('red')) * normalized_value)


def get_cmap():
    colors = ["green", "orange", "red"]
    n_bins = 20
    return LinearSegmentedColormap.from_list("traffic_cmap", colors, N=n_bins)


def range_between(a, b, x):
    range_width = b - a
    if x == 1:
        step = range_width
    else:
        step = range_width // (x - 1)
    numbers = [a + step * i for i in range(x - 1)]
    numbers.append(b)
    numbers = [int(number) for number in numbers if a <= number <= b][:x]
    return numbers

