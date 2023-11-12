import time

import psycopg2
import networkx as nx
from shapely.wkt import loads
import matplotlib.pyplot as plt
from shapely.geometry import LineString
# from shapely.ops import simplify


def draw_edge(ax, start_wkt, end_wkt, source, target):
    start = loads(start_wkt)
    end = loads(end_wkt)
    # print(start.x)
    # if start.x < 2217500 or end.x < 2217500 or start.x > 2218500 or start.y > 6458400 or end.y > 6459000:
    #     return
    ax.plot([start.x, end.x], [start.y, end.y], 'b-', linewidth=1) # Krawędzie jako niebieskie linie
    ax.plot(start.x, start.y, 'ro', markersize=2) # Wierzchołki jako czerwone kropki
    ax.text(start.x, start.y, f'{source}', color='green', fontsize=6)
    ax.plot(end.x, end.y, 'ro', markersize=2)
    ax.text(end.x, end.y, f'{target}', color='green', fontsize=6)


def get_cracow_graph():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            dbname="Cracow_Map",
            user="postgres",
            password="admin"
        )

        # Zapytanie SQL do pobrania danych grafu
        sql = "SELECT ST_AsText(ST_StartPoint(way)), ST_AsText(ST_EndPoint(way)), source, target, cost FROM planet_osm_line " \
              "WHERE railway IS NULL AND cost < 1000 AND highway NOT IN ('footway', 'cycleway', 'elevator');"

        # Wykonanie zapytania
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        # Zamknięcie połączenia
        cur.close()
        conn.close()

        return rows

        # Tworzenie wykresu
        fig, ax = plt.subplots(figsize=(60, 36))  # Ustawienie większego rozmiaru wykresu

        # Rysowanie krawędzi
        for start, end, source, target, cost in rows:
            draw_edge(ax, start, end, source, target)

        # Ustawienia wykresu
        ax.set_title("Graf Drogowy Krakowa")
        ax.set_xlabel("Długość geograficzna")
        ax.set_ylabel("Szerokość geograficzna")
        plt.show()

        # cursor = connection.cursor()
        # graph = nx.Graph()
        #
        # cursor.execute("SELECT osm_id, name, ST_AsText(ST_Transform(way, 4326)) AS geometry FROM planet_osm_roads WHERE railway IS NULL")
        # rows = cursor.fetchall()
        #
        # for row in rows:
        #     osm_id, name, geometry = row
        #     geometry = loads(geometry)
        #     coords = list(geometry.coords)
        #
        #     for i in range(len(coords) - 1):
        #         point1 = coords[i]
        #         point2 = coords[i + 1]
        #         graph.add_node(point1)
        #         graph.add_node(point2)
        #         graph.add_edge(point1, point2, osm_id=osm_id, name=name)
        #
        # cursor.close()
        # connection.close()
        #
        # plt.figure(figsize=(40, 25))
        # pos = {node: node for node in graph.nodes()}
        # nx.draw(graph, pos, with_labels=False, node_size=1)
        # plt.show()
        #
        # return graph

    except psycopg2.Error as e:
        print(f"Error: Unable to connect to the database - {e}")


get_cracow_graph()