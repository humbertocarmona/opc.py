import json
import numpy as np
from numpy import pi
import pandas as pd
from geopy.distance import distance as geodistance
import urllib
import matplotlib.pyplot as plt
from PIL import Image
import io
key = 'insira a chave'


def get_directions(origin, destination, departure_time, key=key):
    """
        get directions using Google Directions API
        input:
        origin: list, tuple or array (lat1,lon1)
        destin: list, tuple or array (lat1,lon1)

        returns:
        jason data from Google API
    """
    origin = 'origin={:},{:}'.format(origin[0], origin[1])
    destination = 'destination={:},{:}'.format(destination[0], destination[1])
    departure_time = 'departure_time={:}'.format(departure_time)
    travel_mode = 'travel_mode=driving'
    units = 'units=metric'
    key = 'key={:}'.format(key)
    querystring = origin + '&' + destination + '&' + \
        departure_time + '&' + travel_mode + '&' + units + '&' + key
    url = 'https://maps.googleapis.com/maps/api/directions/json' + '?' + querystring
    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print(e.reason)
    else:
        if resp.code == 200:  # ok
            resp = resp.read()
            data = json.loads(resp)
        else:
            data = None
        return data


def go_get_directions(vertices, edges, all_data, dep_time,
                      logger, init=True, edge_indexes=[]):
    """
        this will sweep over all edges and get directions
        from source to target using the Google Directions API
        - vertices - lat lon info
        - edges
        - all_data: contains json information already fetched
    """
    if init:
        edge_length = np.full(len(edges), None)
        leg_distance = np.full(len(edges), None)
        leg_duration = np.full(len(edges), None)
        leg_start_loc = np.full(len(edges), None)
        leg_end_loc = np.full(len(edges), None)
        steps_distance = np.full(len(edges), None)
        steps_duration = np.full(len(edges), None)
        google_distance = np.full(len(edges), None)
        n_steps = np.full(len(edges), None)

    if len(edge_indexes) == 0:
        edge_indexes = edges.index.values
    for i in edge_indexes:
        if int(i) % 100 == 0:
            print(i)
        orig = edges['s'][i]
        dest = edges['t'][i]
        origin = vertices['coord'][orig]
        destination = vertices['coord'][dest]
        edge_length[i] = geodistance(origin, destination).m
        logger.info('edge {:} - origin = {:}, destination = {:}'.format(
            i, origin, destination))
        logger.info('edge {:} - length = {:} meters (geopy)'.format(
            i, edge_length[i]))

        key = str(i)
        if key in all_data:
            data = all_data[key]
        else:
            print('feching', key)
            data = get_directions(origin, destination, dep_time)
            all_data[key] = data
        # --- PARSING data ------------------------------------------
        n_routes = len(data['routes'])
        if n_routes == 0:
            logger.warning("# NO ROUTES TO DESTINATION")
        else:
            # legs ---------------------------------
            n_legs = len(data['routes'][0]['legs'])
            assert n_legs > 0
            leg = data['routes'][0]['legs'][0]

            if 'duration_in_traffic' in leg:
                leg_duration[i] = leg['duration_in_traffic']['value']
            elif 'duration' in leg:
                leg_duration[i] = leg['duration']['value']

            if 'distance' in leg:
                leg_distance[i] = leg['distance']['value']

            if 'start_location' in leg:
                leg_start_loc[i] = (leg['start_location']['lat'],
                                    leg['start_location']['lng'])
                leg_end_loc[i] = (leg['end_location']['lat'],
                                  leg['end_location']['lng'])

            logger.info('leg')
            logger.info('\t start loc = {:}, end loc = {:}'.format(
                leg_start_loc[i], leg_end_loc[i]))
            logger.info('\t distance = {:} meters'.format(leg_distance[i]))
            logger.info('\t duration = {:} sec'.format(leg_duration[i]))

            # steps -----------------------------------
            if 'steps' in leg:
                n_steps[i] = len(leg['steps'])
                logger.info('\t number of steps = {:}'.format(n_steps[i]))
                if n_steps[i] > 1:
                    logger.warning('\t more than one step for this edge')
                steps_duration[i] = 0.0
                steps_distance[i] = 0.0
                google_distance[i] = 0.0
                for _, step in enumerate(leg['steps']):
                    duration = step['duration']['value']
                    distance = step['distance']['value']
                    logger.debug(
                        '\t\t step {:}:  duration = {:} sec, distance = {:} meters'
                        .format(i, duration, distance))

                    step_start_loc = (step['start_location']['lat'],
                                      step['start_location']['lng'])
                    step_end_loc = (step['end_location']['lat'],
                                    step['end_location']['lng'])
                    google_distance[i] += geodistance(
                        step_start_loc, step_end_loc).m
                    steps_duration[i] += duration
                    steps_distance[i] += distance

                logger.info('\t total leg duration = {:} sec'.format(
                    steps_duration[i]))
                logger.info('\t total leg distance {:} meters'.format(
                    steps_distance[i]))
                logger.info(
                    '\t total computed distance = {:} meters (geopy)'.format(
                        google_distance[i]))
                logger.info('---------------- end leg')

    dta = {'edge_length': edge_length,
           'leg_distance': leg_distance,
           'leg_duration': leg_duration,
           'leg_start_loc': leg_start_loc,
           'leg_end_loc': leg_end_loc,
           'steps_distance': steps_distance,
           'steps_duration': steps_duration,
           'google_distance': google_distance,
           'n_steps': n_steps}
    df = pd.DataFrame(data=dta)
    print('finished')
    return all_data, df

def get_image(center=(42.3601, -71.0589), zoom=11,
              size=[640,640], file='test.png'):
    lower, upper = viewport(center, zoom=zoom, size=size)
    print(lower, upper)
    # url variable store url
    url = "https://maps.googleapis.com/maps/api/staticmap?"

    center_s = 'center={:},{:}&'.format(center[0], center[1])
    zoom_s = 'zoom={:}&'.format(zoom)
    size_s = 'size={:}x{:}&'.format(size[0], size[1])
    maptype_s = 'maptype=roadmap&scale=2&format=png32&'
    sensor_s = 'sensor=false&'
    key_s = 'key={:}'.format(key)

    querystring = center_s+zoom_s+size_s+maptype_s+sensor_s+key_s
    url = url + querystring

    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError as e:
        print(e.reason)
    else:
        print(resp.code)
        if resp.code == 200:  # ok
            buffer = resp.read()
            # image = Image.open(buffer)
            file = 'u_{:}_{:}_l_{:}_{:}.png'.format(
                lower[0], lower[1], upper[0], upper[1])
            with open(file, 'wb') as f:
                f.write(buffer)
            pic = Image.open(io.BytesIO(buffer))
            pix = np.array(pic.getdata()).reshape(pic.size[0], pic.size[1], 4)
            return pic, pix, lower, upper

def to_pixel_coord(coords, zoom):
    lat = coords[0]*pi/180
    lon = coords[1]*pi/180

    F = 128*(2**zoom)/pi
    x = F*(lon + pi)
    y = F*(pi - np.log(np.tan(pi/4+lat/2)))
    return np.array([x, y])

def to_lat_lon(p, zoom):
    F_1 = pi/(128*(2**zoom))

    lon = (F_1*p[0] - pi)

    exp_um = np.exp(pi - F_1*p[1])
    lat = 2*np.arctan(exp_um) - 0.5*pi

    lat *= 180/pi
    lon *= 180/pi
    return (lat, lon)

def viewport(coords, zoom, size=np.array([640, 640])):

    center = to_pixel_coord(coords, zoom)

    x = center[0]+size[1]/2
    y = center[1]-size[1]/2
    lower = [x, y]

    x = center[0]-size[1]/2
    y = center[1]+size[1]/2
    upper = [x, y]

    lower_deg = to_lat_lon(lower, zoom)
    upper_deg = to_lat_lon(upper, zoom)

    return lower_deg, upper_deg
