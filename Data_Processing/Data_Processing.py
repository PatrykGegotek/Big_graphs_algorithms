import psycopg2
from shapely.wkt import loads
import matplotlib.pyplot as plt

HIGHWAY_TO_WEIGHT = {
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


def draw_edge(ax, start_wkt, end_wkt, source, target, weight):
    start = loads(start_wkt)
    end = loads(end_wkt)
    # print(start.x)
    # if start.x < 2217500 or end.x < 2217500 or start.x > 2218500 or start.y > 6458400 or end.y > 6459000:
    #     return
    ax.plot([start.x, end.x], [start.y, end.y], 'b-', linewidth=(weight/5)+1) # Krawędzie jako niebieskie linie
    ax.plot(start.x, start.y, 'ro', markersize=2) # Wierzchołki jako czerwone kropki
    # ax.text(start.x, start.y, f'{source}', color='green', fontsize=6)
    ax.plot(end.x, end.y, 'ro', markersize=2)
    # ax.text(end.x, end.y, f'{target}', color='green', fontsize=6)


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
        sql = "SELECT ST_AsText(ST_StartPoint(way)), ST_AsText(ST_EndPoint(way)), source, target, cost, highway " \
              "FROM planet_osm_line " \
              "WHERE railway IS NULL " \
              "AND cost < 1000 " \
              "AND highway NOT IN ('footway', 'cycleway', 'elevator', 'steps', 'service');"

        # Wykonanie zapytania
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()

        # Zamknięcie połączenia
        cur.close()
        conn.close()

        new_rows = []

        for row in rows:
            weight = get_weight(row[5])
            new_rows.append(row + (weight,))

        return new_rows

    except psycopg2.Error as e:
        print(f"Error: Unable to connect to the database - {e}")


# get_cracow_graph()

def visualize_graph():
    rows = get_cracow_graph()

    # Tworzenie wykresu
    fig, ax = plt.subplots(figsize=(60, 36))  # Ustawienie większego rozmiaru wykresu

    # Rysowanie krawędzi
    for start, end, source, target, cost, highway, weight in rows:
        draw_edge(ax, start, end, source, target, weight)

    # Ustawienia wykresu
    ax.set_title("Graf Drogowy Krakowa")
    ax.set_xlabel("Długość geograficzna")
    ax.set_ylabel("Szerokość geograficzna")
    plt.show()


# visualize_graph()