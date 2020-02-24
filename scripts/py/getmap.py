import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from descartes import PolygonPatch
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
import geopandas as gpd
import pandas as pd

# %%
ox.config(log_console=False, use_cache=True)
ox.__version__


# %%
# if __name__ == "__main__":
place = 'San Francisco, California, USA'
place = ''
if place is not '':
    print('getting from', place)
    # gdf = ox.gdf_from_place(place) # get contour as geopandas
    G = ox.graph_from_place(place, network_type='drive',
                            simplify=True)  # get map as networkx
    print(G.number_of_nodes())
    print(G.number_of_edges())
    print(G.is_directed())
else:
    location_point = (-3.7327, -38.5270)  # Fortaleza
    # location_point = (37.691331, -122.310746)  # San Francisco Bay
    distance = 15000
    print('getting from', location_point, distance/1000, 'km')
    G = ox.graph_from_point(location_point, network_type='drive',
                            distance=distance, simplify=True)
    print(G.number_of_nodes())
    print(G.number_of_edges())
    print(G.is_directed())

# ox.save_graphml(G, filename="tt.graphml")
# ox.save_graph_shapefile(G, 'cityshape')

# %% get node properties

pos = {}
nDic = {}
x = nx.get_node_attributes(G, "x")
y = nx.get_node_attributes(G, "y")
t = nx.get_node_attributes(G, "highway")
idx = []
lat = []
lon = []
n_idx = []

for i, n in enumerate(G.nodes()):
    idx.append(i+1)
    n_idx.append(n)
    lon.append(x[n])
    lat.append(y[n])
    nDic[n] = i+1
    pos[n] = (x[n], y[n])
    if n in t:
        print(i+1, t[n])

df = pd.DataFrame({'i': idx, 'n': n_idx, 'lat': lat, 'lon': lon})
df.to_csv("data/vertices.csv", index=False)

# %%
src = []
dst = []
i = 0
for e in G.edges():
    s, d = e
    src.append(nDic[s])
    dst.append(nDic[d])

df = pd.DataFrame({'src': src, 'dst': dst})
df.to_csv("data/edges.csv", index=False)


# %%
fig, ax = ox.plot_graph(G, fig_height=15, show=False,
                        close=False, node_color="#000000", edge_color='#777777',
                        axis_off=True, equal_aspect=True, bgcolor='none',
                        save=False, filename='teste', file_format='png')
ax.scatter([location_point[1]],[location_point[0]], s=[500], c='#ff0000')


# %%
ox.save_graph_shapefile(G, 'cityshape')


# %%
