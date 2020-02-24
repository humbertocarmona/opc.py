#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import geopandas as gpd
# import geoplot as gplt
import matplotlib.pyplot as plt
from shapely.geometry import Point, LineString


# In[7]:


import osmnx as ox
from descartes import PolygonPatch
from shapely.geometry import Polygon, MultiPolygon
get_ipython().run_line_magic('matplotlib', 'inline')
ox.config(log_console=True, use_cache=True)
ox.__version__


# In[68]:


# get the network for manhattan
# G = ox.graph_from_place('Manhattan Island, New York, New York, USA', network_type='drive')
place='Boston, Massachusetts, USA'
gdf = ox.gdf_from_place(place)
# gdf = ox.project_gdf(gdf)

G = ox.graph_from_place(place, network_type='drive')
# fig, ax = ox.plot_graph(G, fig_height=6, node_size=2, node_alpha=0.5,
#                         edge_linewidth=0.3, save=True, dpi=100, filename='manhattan')


# In[55]:


# G = ox.project_graph(G)


# In[91]:


#fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=150)
fig, ax = ox.plot_graph(G, fig_height=15, show=False,
                        close=False, edge_color='#777777',
                        axis_off=False, equal_aspect=True, bgcolor='none', 
                        save=False, filename='teste', file_format='png')
gdf1.plot(ax=ax, color='r', zorder=10, linewidth=3)
# plt.close()
plt.show()
fig.save('teste.png')


# In[ ]:


def reindex_vertices(vertices_file, edges_file):
    vertices=pd.read_csv(vertices_file, index_col='id')
    vertices['newid'] = np.arange(len(vertices))
    edges=pd.read_csv(edges_file, index_col='id')
#     edges['s_new'] = np.full(len(edges), None)
#     edges['t_new'] = np.full(len(edges), None)
    for i in edges.index.values:
        s = edges['s'][i]
        edges.at[i, 's'] = vertices['newid'][s]
        t = edges['t'][i]
        edges.at[i, 't'] = vertices['newid'][t]
    edges = edges.reset_index(drop=True)
    edges.index.names = ['id']    
    vertices = vertices.reset_index(drop=True)
    vertices = vertices.drop(['newid'], axis=1)
    vertices.index.names = ['id']    
    
    vertices_file = vertices_file.split('/')[-1]
    vertices.to_csv(vertices_file.replace('.csv','_r.csv'))
    edges_file = edges_file.split('/')[-1]
    edges.to_csv(edges_file.replace('.csv','_r.csv'))
    display(vertices.head())
    display(edges.head())
# reindex_vertices('./Aurelio/Boston-2-vertices.csv', './Aurelio/Boston-2-edges-4am.csv')


# In[39]:


# to this matplotlib axis, add the place shape as descartes polygon patches
for geometry in gdf['geometry'].tolist():
    if isinstance(geometry, (Polygon, MultiPolygon)):
        if isinstance(geometry, Polygon):
            geometry = MultiPolygon([geometry])
        for polygon in geometry:
            patch = PolygonPatch(polygon, fc='#cccccc', ec='k', linewidth=3, alpha=0.1, zorder=-1)
            ax.add_patch(patch)


# In[40]:


margin = 0.0
west, south, east, north = gdf.unary_union.bounds
margin_ns = (north - south) * margin
margin_ew = (east - west) * margin
ax.set_ylim((south - margin_ns, north + margin_ns))
ax.set_xlim((west - margin_ew, east + margin_ew))
fig


# In[45]:


vdf = pd.read_csv('Boston-2-vertices_r.csv')
edf = pd.read_csv('Boston-2-edges-4am_r.csv')


# In[53]:


geometry = []
for i, r in edf.iterrows():
    s = r['s']
    t = r['t']
    ps = Point(vdf['lon'][s], vdf['lat'][s])
    pt = Point(vdf['lon'][t], vdf['lat'][t])
    geometry.append(LineString([ps,pt]))

crs = {'proj': 'latlong', 'ellps': 'WGS84', 'datum': 'WGS84', 'no_defs': True}
crs="+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
gdf1 = gpd.GeoDataFrame(edf, geometry=geometry, crs=crs)


# In[48]:


#%matplotlib inline
# fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(8,8), dpi=150)
gdf['color'] = 0.0
ne = 11
gdf.loc[ne,'color'] = 100
gdf.plot(column='color', ax=ax, zorder=1)
epsilon = 0.01
xmin = gdf.loc[ne, 'geometry'].xy[0][0]-epsilon
ymin = gdf.loc[ne, 'geometry'].xy[1][0]-epsilon
xmax = gdf.loc[ne, 'geometry'].xy[0][1]+epsilon
ymax = gdf.loc[ne, 'geometry'].xy[1][1]+epsilon
print(xmin, xmax)
lcl = vdf[vdf['lon'] >= xmin] 
lcl = lcl[lcl['lon'] <= xmax] 
lcl = lcl[lcl['lat'] >= ymin] 
lcl = lcl[lcl['lat'] <= ymax]
print(len(lcl))
# ax.scatter(lcl['lon'], lcl['lat'], s=10, c='r')
# ax.set_xlim(xmin, xmax);
# ax.set_ylim(ymin, ymax);


# In[ ]:





# In[ ]:





# In[ ]:




