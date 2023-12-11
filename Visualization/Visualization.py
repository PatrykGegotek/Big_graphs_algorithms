import folium
import geopandas as gpd
import matplotlib.colors as mcolors
import webbrowser

from matplotlib.colors import LinearSegmentedColormap
from shapely import LineString

DIRECTORY = "../Generated_Maps"
ABSOLUTE_PATH = "C:\\Users\\patryk\\Desktop\\Inżynierka\\Algorithms implementation\\Generated_Maps"


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

        # Uzyskanie wierzchołków startowego i końcowego na podstawie identyfikatorów
        start_vertex = graph.vertices[start_vertex_id]
        end_vertex = graph.vertices[end_vertex_id]

        edge_traffic = (start_vertex.value + end_vertex.value) / 2
        row['traffic'].append(edge_traffic)
    return gdf


def process_dataframe(df):
    rows_to_add = []
    matched_ids = set()

    for i in range(len(df)):
        if df.loc[i, 'edge_id'] in matched_ids:
            continue
        if df.loc[i, 'oneway']:
            # rows_to_add.append(df.iloc[i])
            new_row = {
                'start': df.loc[i, 'start'],
                'end': df.loc[i, 'end'],
                'traffic': df.loc[i, 'traffic'],
                'geometry': df.loc[i, 'geometry']
            }

            rows_to_add.append(new_row)
        else:
            edge_id = df.loc[i, 'edge_id']
            duplicate_row = df[(df['edge_id'] == edge_id)]

            if not duplicate_row.empty:
                duplicate_index = duplicate_row.index[0]
                summed_traffic = [sum(x) for x in zip(df.loc[i, 'traffic'], df.loc[duplicate_index, 'traffic'])]

                new_row = {
                    'start': df.loc[i, 'start'],
                    'end': df.loc[i, 'end'],
                    'traffic': summed_traffic,
                    'geometry': df.loc[i, 'geometry']
                }

                rows_to_add.append(new_row)
            matched_ids.add(edge_id)
    new_df = gpd.GeoDataFrame(rows_to_add)
    print(new_df)
    return new_df


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


def generate_wavefront_map(gdf, name):
    mapa = folium.Map(location=[50.050, 19.941], zoom_start=12)

    for _, row in gdf.iterrows():
        folium.PolyLine(
            locations=[(y, x) for x, y in row['geometry'].coords],
            color=get_color(row['distance'], 150, get_cmap()),
            weight=2
        ).add_to(mapa)

    mapa.save(f'{DIRECTORY}/{name}.html')
    webbrowser.open(f'{ABSOLUTE_PATH}/{name}.html')

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

def generate_pregel_map(gdf, name, steps, leap=1):
    for i in range(steps):
        mapa = folium.Map(location=[50.074, 19.92], zoom_start=13)

        for _, row in gdf.iterrows():
            folium.PolyLine(
                locations=[(y, x) for x, y in row['geometry'].coords],
                color=get_color(row['traffic'][i], 60, get_cmap()),
                weight=2
            ).add_to(mapa)

        if i%leap == 0:
            mapa.save(f'{DIRECTORY}/{name}_step_{i}.html')
            webbrowser.open(f'{ABSOLUTE_PATH}/{name}_step_{i}.html')

