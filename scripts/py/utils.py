import numpy as np
import pandas as import pd

def displaylog(log_file, i=[0,-1]):
    with open(log_file, 'r') as lf:
        log = lf.read()
        log = log.split('\n')
        for l in log[i[0]:i[1]]:
            print(l)


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
    