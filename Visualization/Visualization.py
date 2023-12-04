from matplotlib.colors import LinearSegmentedColormap
from shapely import LineString
import geopandas as gpd
import matplotlib.colors as mcolors


def initialize_dataframe(graph):
    rows = []
    for vertex in graph.vertices.values():
        for edge in vertex.edges:
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


# def draw_graph(graph, ax, step):
#     colors = [(0, 'green'), (0.25, 'yellow'), (0.75, 'yellow'), (1, 'red')]
#     cmap = LinearSegmentedColormap.from_list('custom_colormap', colors)
#     norm = mcolors.Normalize(vmin=0, vmax=60)  # Zakres wartości ruchu
#
#     for vertex in graph.vertices.values():
#         for edge in vertex.edges:
#             start_vertex = graph.vertices[edge.start_vertex]
#             end_vertex = graph.vertices[edge.end_vertex]
#
#             # Oblicz wartość ruchu dla krawędzi
#             edge_traffic = (start_vertex.value + end_vertex.value) / 2
#
#             # Koloruj krawędź na podstawie wartości ruchu
#             color = cmap(norm(edge_traffic))
#             ax.plot([start_vertex.x, end_vertex.x], [start_vertex.y, end_vertex.y], color=color, linewidth=2)
#         color2 = cmap(norm(vertex.value))
#         ax.plot(vertex.x, vertex.y, 'o', color=color2)
#
#     ax.set_title(f"Symulacja Ruchu Drogowego, krok {step + 1}")
#     ax.set_xlabel("X")
#     ax.set_ylabel("Y")


def get_color(traffic_value, max_traffic, cmap):
    normalized_value = traffic_value / max_traffic
    return mcolors.to_hex(cmap(normalized_value))


def get_color2(traffic_value, max_traffic):
    normalized_value = traffic_value / max_traffic
    return mcolors.to_hex(mcolors.rgb_to_hsv(mcolors.to_rgb('green')) * (1 - normalized_value) + mcolors.rgb_to_hsv(
        mcolors.to_rgb('red')) * normalized_value)


def get_cmap():
    colors = ["green", "yellow", "red"]
    n_bins = 20
    return LinearSegmentedColormap.from_list("traffic_cmap", colors, N=n_bins)














# # Function to extract coordinates from LineStrings
# def linestring_to_coords(linestring):
#     return [[x, y] for x, y in linestring.coords]
#
# # Prepare data for plotting
# gdf['coords'] = gdf['geometry'].apply(linestring_to_coords)
# max_length = gdf['traffic'].apply(len).max()
#
# # Create a Plotly figure
# fig = go.Figure()
#
# # Add streets as lines
# for _, row in gdf.iterrows():
#     fig.add_trace(go.Scattermapbox(
#         lon = [point[0] for point in row['coords']],
#         lat = [point[1] for point in row['coords']],
#         mode = 'lines',
#         line = dict(width = 2, color = 'green'), # Initial color
#         name = '',
#     ))
#
# # Update layout
# fig.update_layout(
#     mapbox_style="open-street-map",
#     mapbox_zoom=13,
#     mapbox_center = {"lat": 50.09151, "lon": 19.93074}
# )
#
# # Create animation frames
# frames = []
# for i in range(max_length):
#     frame_data = []
#     for _, row in gdf.iterrows():
#         traffic_value = row['traffic'][i] if i < len(row['traffic']) else row['traffic'][-1]
#         color = 'red' if traffic_value > 30 else 'green'
#         frame_data.append(go.Scattermapbox(
#             lon = [point[0] for point in row['coords']],
#             lat = [point[1] for point in row['coords']],
#             mode = 'lines',
#             line = dict(width = 2, color = color),
#             name = '',
#         ))
#     frames.append(go.Frame(data=frame_data, name=str(i)))
#
# # Add frames to the figure
# fig.frames = frames
#
# # Add a slider to control animation
# sliders = [{
#     'steps': [{'method': 'animate', 'label': str(k), 'args': [[str(k)], {'frame': {'duration': 1000, 'redraw': True}}]} for k in range(max_length)]
# }]
#
# fig.update_layout(sliders=sliders)
#
# # Show the figure
# fig.show()


#
# # Define the color map
# def traffic_color(value):
#     if value <= 50:
#         return 'green'
#     elif 50 < value <= 100:
#         return 'yellow'
#     else:
#         return 'red'
#
# # Initialize the plot
# fig, ax = plt.subplots()
#
# def animate(i):
#     ax.clear()
#     ax.set_xlim(19.929, 19.932)
#     ax.set_ylim(50.091, 50.092)
#     for index, row in gdf.iterrows():
#         # Determine the color based on the traffic value
#         color = traffic_color(row['traffic'][i])
#         ax.plot(*row['geometry'].xy, color=color, linewidth=2)
#
#     ax.set_title(f"Traffic at second {i+1}")
#
#
# from matplotlib.animation import FuncAnimation
# # Creating the animation
# ani = FuncAnimation(fig, animate, frames=3, interval=1000, repeat=False)
#
# from matplotlib.animation import writers
# print(writers.list())
#
# # Save the animation as a GIF file
# ani.save('traffic_animation.gif', writer='pillow', fps=1)

# # Prepare the data
# def extract_coordinates(linestring):
#     return list(linestring.coords)
#
# gdf['coordinates'] = gdf['geometry'].apply(extract_coordinates)
#
# # Function to get color based on traffic value
# def get_color(traffic_value):
#     if traffic_value > 100:
#         return 'red'
#     else:
#         return 'green'
#
# # Initialize the figure
# fig = go.Figure()
#
# # Add the initial state of the lines (using the first traffic value)
# for idx, row in gdf.iterrows():
#     fig.add_trace(go.Scattermapbox(
#         lon=[p[0] for p in row['coordinates']],
#         lat=[p[1] for p in row['coordinates']],
#         mode='lines',
#         line=dict(color=get_color(row['traffic'][0])),
#         hoverinfo='none'
#     ))
#
# # Set up the map layout
# fig.update_layout(
#     mapbox_style="open-street-map",
#     mapbox_center={"lat": 50.06143, "lon": 19.93658},
#     mapbox_zoom=12,
#     showlegend=False,
# )
#
# # Add animation frames
# frames = []
# for i in range(len(gdf['traffic'].iloc[0])):
#     frame_data = []
#     for idx, row in gdf.iterrows():
#         frame_data.append(go.Scattermapbox(
#             lon=[p[0] for p in row['coordinates']],
#             lat=[p[1] for p in row['coordinates']],
#             mode='lines',
#             line=dict(color=get_color(row['traffic'][i]))
#         ))
#     frames.append(go.Frame(data=frame_data))
#
# fig.frames = frames
#
# # Add a slider to control animation
# fig.update_layout(
#     updatemenus=[dict(
#         type="buttons",
#         buttons=[dict(label="Play",
#                       method="animate",
#                       args=[None, {"frame": {"duration": 1000, "redraw": True}}])])]
# )
#
# # Show the figure
# fig.show()


#
# line_data = []
# for _, row in gdf.iterrows():
#     line = row['geometry'].coords[:]
#     lon, lat = zip(*line)  # Rozpakowanie współrzędnych do osobnych list
#     line_data.append({'type': 'LineString', 'traffic': row['traffic'][0], 'coordinates': list(zip(lon, lat))})
#
# # Tworzymy pusty obiekt figury
# fig = go.Figure()
#
# # Dodajemy ścieżki dla każdego segmentu drogi
# for segment in line_data:
#     fig.add_trace(
#         go.Scattergeo(
#             lon=[coord[0] for coord in segment['coordinates']],
#             lat=[coord[1] for coord in segment['coordinates']],
#             mode='lines',
#             line=dict(width=2, color=get_color(segment['traffic'], 50, cmap)),  # Tutaj możesz dostosować grubość linii
#         )
#     )
#
# # Ustawienie layoutu mapy
# fig.update_layout(
#     title='Mapa korków w Krakowie',
#     geo=dict(
#         resolution=50,
#         showland=True,
#         landcolor="rgb(217, 217, 217)",
#         subunitcolor="rgb(255, 255, 255)",
#         countrycolor="rgb(255, 255, 255)",
#         showlakes=True,
#         lakecolor="rgb(255, 255, 255)",
#         showsubunits=True,
#         showcountries=True,
#         showocean=True,
#         oceancolor="rgb(255, 255, 255)",
#         projection_type="mercator",
#         center=dict(lon=19.9368, lat=50.0619),  # Centrum Krakowa
#         lonaxis_range=[19.8, 20.1],  # Zakres współrzędnych geograficznych
#         lataxis_range=[49.9, 50.1]
#     ),
#     showlegend=False,
#     mapbox_style="carto-positron",
#     mapbox_zoom=14,  # Zwiększ wartość dla większego przybliżenia
#     mapbox_center={"lat": 50.07, "lon": 19.92},  # Ustawienie na centrum Krakowa
#     width=1600,  # Szerokość mapy w pikselach
#     height=600,  # Wysokość mapy w pikselach
# )
#
# fig.show()
#


# # gdf = gpd.GeoDataFrame(df, geometry=gpd.GeoSeries.from_wkt(df['geometry']))
#
# # Ustawienie układu współrzędnych
# gdf.set_crs(epsg=4326, inplace=True)
# # gdf['traffic2'] = gdf['traffic'].get(0)
# gdf['traffic2'] = gdf['traffic'].apply(lambda x: x[0])
# gdf = gdf.head(500)
#
# fig = go.Figure()
#
# # Iterujemy przez każdy wiersz DataFrame
# for _, row in gdf.iterrows():
#     # Parsujemy geometrię linestring do listy współrzędnych
#     line = row['geometry'].coords[:]
#     lat, lon = zip(*line)
#
#     # Dodajemy ślad dla każdego segmentu drogi
#     fig.add_trace(
#         go.Scattermapbox(
#             lat=lat,
#             lon=lon,
#             mode='lines',  # Ustawiamy tryb na linie
#             line=dict(width=2, color='red'),  # Tutaj można dostosować na podstawie 'traffic'
#         )
#     )
#
# # Ustawienie widoku mapy i stylu
# fig.update_layout(
#     mapbox_style="carto-positron",
#     mapbox_zoom=12,
#     mapbox_center={"lat": 50.0619, "lon": 19.9368}
# )
#
# # Wyświetlenie figury
# fig.show()
#
# # Tworzenie mapy
# # fig = px.line_mapbox(gdf, lat=gdf.geometry.centroid.y, lon=gdf.geometry.centroid.x,
# #                      color='traffic2', zoom=12, height=600)
# #
# # # Ustawienie tokena Mapbox (jeśli go masz)
# # # fig.update_layout(mapbox_style="open-street-map") # alternatywa, jeśli nie masz tokena Mapbox
# # fig.update_layout(mapbox_style="carto-positron", mapbox_zoom=12, mapbox_center = {"lat": 50.0619, "lon": 19.9368})
# #
# # fig.show()
# time.sleep(10000)

