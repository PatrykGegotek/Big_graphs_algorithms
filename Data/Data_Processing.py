import sys

import psycopg2
from shapely.wkt import loads
import matplotlib.pyplot as plt
from shapely.geometry import LineString
from shapely.ops import transform
from pyproj import Transformer

HIGHWAY_TO_WEIGHT = {
    "motorway": 20,
    "trunk": 20,
    "motorway_link": 20,
    "trunk_link": 20,
    "primary": 20,
    "secondary": 18,
    "tertiary": 16,
    "primary_link": 15,
    "secondary_link": 14,
    "tertiary_link": 12,
    "residential": 6,
    "service": 3,
    "living_street": 1
}


def get_weight(highway_type):
    return HIGHWAY_TO_WEIGHT.get(highway_type, 1)


# def draw_edge(ax, start_wkt, end_wkt, source, target, weight):
#     start = loads(start_wkt)
#     end = loads(end_wkt)
#     # print(start.x)
#     # if start.x < 2217500 or end.x < 2217500 or start.x > 2218500 or start.y > 6458400 or end.y > 6459000:
#     #     return
#     ax.plot([start.x, end.x], [start.y, end.y], 'b-', linewidth=(weight/5)+1) # Krawędzie jako niebieskie linie
#     ax.plot(start.x, start.y, 'ro', markersize=2) # Wierzchołki jako czerwone kropki
#     # ax.text(start.x, start.y, f'{source}', color='green', fontsize=6)
#     ax.plot(end.x, end.y, 'ro', markersize=2)
#     # ax.text(end.x, end.y, f'{target}', color='green', fontsize=6)
#
#
# def get_cracow_graph():
#     try:
#         conn = psycopg2.connect(
#             host="localhost",
#             port="5432",
#             dbname="Cracow_Map",
#             user="postgres",
#             password="admin"
#         )
#
#         # Zapytanie SQL do pobrania danych grafu
#         sql = "SELECT ST_AsText(ST_Transform(ST_StartPoint(way), 4326)) AS start_point, " \
#               "ST_AsText(ST_Transform(ST_EndPoint(way), 4326)) AS end_point, " \
#               "source, target, cost, highway " \
#               "FROM planet_osm_line " \
#               "WHERE railway IS NULL " \
#               "AND cost < 1000 " \
#               "AND highway NOT IN ('footway', 'cycleway', 'elevator', 'steps', 'service');"
#
#         # Wykonanie zapytania
#         cur = conn.cursor()
#         cur.execute(sql)
#         rows = cur.fetchall()
#
#         # Zamknięcie połączenia
#         cur.close()
#         conn.close()
#
#         new_rows = []
#
#         for row in rows:
#             weight = get_weight(row[5])
#             new_rows.append(row + (weight,))
#
#         return new_rows
#
#     except psycopg2.Error as e:
#         print(f"Error: Unable to connect to the database - {e}")
#
#
# # get_cracow_graph()
#
# def visualize_graph():
#     rows = get_cracow_graph()
#
#     # Tworzenie wykresu
#     fig, ax = plt.subplots(figsize=(60, 36))  # Ustawienie większego rozmiaru wykresu
#
#     # Rysowanie krawędzi
#     for start, end, source, target, cost, highway, weight in rows:
#         draw_edge(ax, start, end, source, target, weight)
#
#     # Ustawienia wykresu
#     ax.set_title("Graf Drogowy Krakowa")
#     ax.set_xlabel("Długość geograficzna")
#     ax.set_ylabel("Szerokość geograficzna")
#     plt.show()
# #
# #
# # visualize_graph()












def draw_edge(ax, start_wkt, end_wkt, source, target, weight):
    start = start_wkt
    end = end_wkt
    # print(start.x)
    # if start.x < 2217500 or end.x < 2217500 or start.x > 2218500 or start.y > 6458400 or end.y > 6459000:
    #     return
    ax.plot([start[0], end[0]], [start[1], end[1]], 'b-', linewidth=(weight/5)+1) # Krawędzie jako niebieskie linie
    ax.plot(start[0], start[1], 'ro', markersize=2) # Wierzchołki jako czerwone kropki
    # ax.text(start.x, start.y, f'{source}', color='green', fontsize=6)
    ax.plot(end[0], end[1], 'ro', markersize=2)
    # ax.text(end.x, end.y, f'{target}', color='green', fontsize=6)




def get_cracow_graph():
    try:
        # conn = psycopg2.connect(
        #     host="localhost",
        #     port="5432",
        #     dbname="Cracow_Map",
        #     user="postgres",
        #     password="admin"
        # )

        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            dbname="Cracow_Map_Big",
            user="postgres",
            password="admin"
        )

        # 163294

        # Zapytanie SQL do pobrania danych grafu
        sql = "SELECT ST_AsText(ST_Transform(ST_Multi(way), 4326)) AS multiline, " \
              "source, target, highway, oneway " \
              "FROM planet_osm_line " \
              "WHERE railway IS NULL " \
              "AND highway NOT IN " \
              "('footway', 'cycleway', 'elevator', 'steps', 'service', 'path', 'proposed', 'track', " \
              "'pedestrian', 'bridleway', 'corridor', 'planned', 'raceway');"



        # sql = "SELECT ST_AsText(ST_Transform(ST_StartPoint(way), 4326)) AS start_point, " \
        #       "ST_AsText(ST_Transform(ST_EndPoint(way), 4326)) AS end_point, " \
        #       "source, target, cost, highway " \
        #       "FROM planet_osm_line_segmented " \
        #       "WHERE cost < 1000 " \
        #       "AND highway NOT IN ('footway', 'cycleway', 'elevator', 'steps', 'service');"

        # Wykonanie zapytania
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        # Zamknięcie połączenia
        cur.close()
        conn.close()

        # print(rows)
        for row in rows:
            print(row[-2])

        id = 0
        new_rows = []

        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32633", always_xy=True)

        # Funkcja do transformacji punktów
        def transform_point(x, y):
            return transformer.transform(x, y)

        # Transformacja LineString do UTM



        for row in rows:
            multilinestring = row[0]
            source = row[1]
            target = row[2]
            highway = row[3]
            oneway = row[4]
            multi_line = loads(multilinestring)
            print(multi_line)
            for line in multi_line.geoms:
                meters = transform(transform_point, line).length
                line_length = len(line.coords)
                if meters > 200:
                    number_of_segments = int(meters // 100)
                    step = int(line_length//number_of_segments)
                    if step == 0:
                        step = 1
                    # print()
                    # print("values")
                    # print(f"line_length:{line_length}")
                    # print(f"step:{step}")
                    # print()
                    print("\n", "START PROCESSING")
                    for i in range(0, line_length - 1, step):
                        start_point = line.coords[i]
                        last_index = line_length - 1 if step + i >= line_length - 1 else i + step
                        # print(f"i:{i}")
                        # print(f"last_index:{last_index}")
                        end_point = line.coords[last_index]
                        if i == 0:
                            print("PROCESS START NODE: ", source)
                            new_source = str(source)
                        else:
                            new_source = f"custom_{id}"
                            print("Middle: ", new_source)
                            id += 1
                        if last_index == line_length - 1:
                            print("PROCESS END NODE: ", target)
                            new_target = str(target)
                        else:
                            new_target = f"custom_{id}"
                            print("Middle: ", new_target)
                        start_point = [start_point[0], start_point[1]]
                        end_point = [end_point[0], end_point[1]]
                        new_rows.append([start_point, end_point, new_source, new_target, highway, oneway, get_weight(highway)])
                else:
                    print("NO PROCESSING")
                    start_point = line.coords[0]
                    end_point = line.coords[-1]
                    start_point = [start_point[0], start_point[1]]
                    end_point = [end_point[0], end_point[1]]
                    new_rows.append([start_point, end_point, source, target, highway, oneway, get_weight(highway)])

        # for row in new_rows:
        #     print(row)
        # sys.exit()
        return new_rows

    except psycopg2.Error as e:
        print(f"Error: Unable to connect to the database - {e}")


# get_cracow_graph()

def visualize_graph():
    rows = get_cracow_graph()

    # Tworzenie wykresu
    fig, ax = plt.subplots(figsize=(60, 36))  # Ustawienie większego rozmiaru wykresu

    # Rysowanie krawędzi
    for start, end, source, target, highway, weight in rows:
        draw_edge(ax, start, end, source, target, weight)

    # Ustawienia wykresu
    ax.set_title("Graf Drogowy Krakowa")
    ax.set_xlabel("Długość geograficzna")
    ax.set_ylabel("Szerokość geograficzna")
    plt.show()


# visualize_graph()
