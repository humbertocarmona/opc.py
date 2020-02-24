import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import re
from datetime import datetime
import time
import logging
import argparse
import json
from directions_google import go_get_directions


def get_net(vertices_file, edges_file):
    """
        simply returns pandas dataframes
        for vertices and edges
    """
    print(edges_file)
    print('vertices_file =', vertices_file)
    vertices = pd.read_csv(vertices_file, index_col='id')
    edges = pd.read_csv(edges_file, index_col='id')
    arr = list(np.vstack([vertices['lat'], vertices['lon']]).transpose())
    vertices['coord'] = arr
    return vertices, edges


def main(vertices_file, edges_file,
         json_file_in=None,
         log_file='temp.log',
         json_file_out=None,
         df_file_out=None):

    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'
    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format=LOG_FORMAT,
                        filemode='w')
    logger = logging.getLogger()

    vertices, edges = get_net(vertices_file, edges_file)

    all_data = {}
    if json_file_in is not None:
        with open(json_file_in, 'r') as f:
            all_data = json.load(f)

    all_data, df = go_get_directions(vertices, edges, all_data, dep_time=dep_time,
                                     logger=logger, edge_indexes=[])
    print(df)

    if json_file_out is not None:
        with open(json_file_out, 'w') as f:
            json.dump(all_data, f)

    if df_file_out is not None:
        df.to_pickle(df_file_out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-')
    parser.add_argument('-vf', help='vertices csv file')
    parser.add_argument('-ef', help='edges csv file')
    parser.add_argument(
        '-js', help='json file with previous google date', default=None)
    parser.add_argument('-t', help='departure time',
                        nargs='?', type=int, default=4)
    parser.add_argument('-wd', help='weekday', nargs='?',
                        type=int, default=2)  # wednesday
    parser.add_argument('--logfile', nargs='?', default='temp.log')

    args = parser.parse_args()

    log_file = args.logfile
    vertices_file = args.vf
    edges_file = args.ef
    dep_time = args.t
    weekday = args.wd
    json_file = args.js
    year, month, day = 2020, 3, 2
    departure = datetime(year, month, day, dep_time)  # future
    wd = departure.weekday()
    while wd != weekday:
        print(day, wd)
        day += (weekday - wd) % 7
        print(day)
        departure = datetime(year, month, day, dep_time)  # future
        wd = departure.weekday()

    departure = int(time.mktime(departure.timetuple()))

    main(vertices_file=vertices_file,
         edges_file=edges_file, json_file_in=json_file)
