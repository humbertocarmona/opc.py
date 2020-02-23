import matplotlib.pyplot as plt
import osmnx as ox
import networkx as nx
from descartes import PolygonPatch
from shapely.geometry import Polygon, MultiPolygon, Point, LineString
import geopandas as gpd
import pandas as pd
ox.config(log_console=False, use_cache=True)
ox.__version__
from directions_google import get_image

def csv_to_gdf(vertices_file, edges_file):
    """
    - reads vertices and esdges files
    - add geometry
    returns 
        GeoDataFrame
    """

    vdf = pd.read_csv(vertices_file)
    edf = pd.read_csv(edges_file)

    geometry = []
    for i, r in edf.iterrows():
        s = r['s']
        t = r['t']
        ps = Point(vdf['lon'][s], vdf['lat'][s])
        pt = Point(vdf['lon'][t], vdf['lat'][t])
        geometry.append(LineString([ps, pt]))

    crs = {'proj': 'latlong', 'ellps': 'WGS84',
           'datum': 'WGS84', 'no_defs': True}
    gdf = gpd.GeoDataFrame(edf, geometry=geometry, crs=crs)
    return gdf


if __name__ == "__main__":
    image, pix, lower, upper = get_image(zoom=12)
    
    place = 'Boston, Massachusetts, USA'
    gdf = ox.gdf_from_place(place) # get contour as geopandas
    G = ox.graph_from_place(place, network_type='drive');  # get map as networkx
    print(G.number_of_nodes())
    print(G.number_of_edges())
    print(G.is_directed())

    pos = {}
    x = nx.get_node_attributes(G, "x")
    y = nx.get_node_attributes(G, "y")
    for n in G.nodes():
        pos[n] = (x[n],y[n])
    # ox.save_graph_shapefile(G, 'bostonshape')
    # ox.save_graphml(G, filename='Bonston.graphml')
    
    # fig, ax = plt.subplots(figsize=(5,5))
    # ax.set_aspect(1)
    
    xlim = upper[1], lower[1]
    ylim = upper[0], lower[0]

    
    
    fig, ax = ox.plot_graph(G, fig_height=15, show=False,
                        close=False, edge_color='#777777',
                        axis_off=False, equal_aspect=True, bgcolor='none', 
                        save=False, filename='teste', file_format='png')

    nx.draw(G, pos=pos, ax=ax)

    # ax.imshow(image, extent=[xlim[0], xlim[1], ylim[0], ylim[1]], zorder=0)
    # ax.set_xlim(xlim)
    # ax.set_ylim(ylim)
    
    # n = gpd.read_file('./data/boston-shape/nodes/nodes.shp')
    # e = gpd.read_file('./data/boston-shape/edges/edges.shp')
    # n.plot(ax=ax, zorder=2, color='gray', markersize=10)
    # e.plot(ax=ax, zorder=2, color='gray')
    
    
    # gdf = csv_to_gdf(vertices_file='./Boston-2-vertices_r.csv',
    #                  edges_file='./Boston-2-edges-4am_r.csv')
    # gdf.plot(ax=ax, zorder=1, color='b',linewidth=2)
    # print(gdf.head())
    # df = pd.read_csv('./Boston-2-vertices_r.csv')
    # ax.scatter(df['lon'], df['lat'], c='b', s=25, zorder=1)


    

    plt.show()
