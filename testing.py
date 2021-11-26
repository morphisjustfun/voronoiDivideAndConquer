import numpy as np
import os
import requests
import json
import matplotlib.pyplot as plt
import math
from ctypes import *

# amenity
# https://wiki.openstreetmap.org/wiki/Key:amenity

scale = 2**26


# overpass query to get all hospitals around 10km of radius around the
# given coordinates


def getHospitalsQuery(meters, amenity, latitude, longitude):
    query = '''[out:json][timeout:25];
    (
    nwr["amenity"="{}"](around:{},{},{});
    );
    out body;
    out center;
    '''.format(amenity, meters, latitude, longitude)
    return query

# get my coordinates


def getMyCoordinates():
    url = 'https://ipinfo.io/json'
    response = requests.get(url)
    data = response.json()
    lat = data['loc'].split(',')[0]
    lon = data['loc'].split(',')[1]
    return lat, lon


OVERPASS_URL = 'http://overpass-api.de/api/interpreter'
coordinates = getMyCoordinates()

overpassQuery = getHospitalsQuery(
    1000,
    'school',
    # amenities[5],
    coordinates[0],
    coordinates[1])
response = requests.get(OVERPASS_URL, params={'data': overpassQuery})
data = response.json()


coordsX = []
coordsY = []

print(data['elements'])
for element in data['elements']:
    if element['type'] == 'node':
        lat = element['lat']
        lon = element['lon']
        coordsY.append(lat)
        coordsX.append(lon)
    elif 'center' in element:
        lat = element['center']['lat']
        lon = element['center']['lon']
        coordsY.append(lat)
        coordsX.append(lon)


yOrigin, xOrigin = coordinates
yOrigin = float(yOrigin)
xOrigin = float(xOrigin)

#Global DLL
CVoronoi  = CDLL(os.path.abspath("./cMultithread/voronoi_2048.so"))
voronoi = CVoronoi.voronoi_2048
voronoi.argtypes = [POINTER(c_uint16), POINTER(c_int), POINTER(c_int), c_int, c_int]

#Global Constants
MATRIX_L = 2048 #Don't change 2048
MAX_SEEDS = 2000 #Realistic max (to avoid realloc)

#Global Variables
#   you shouldn't define this inside a function (to avoid realloc)
matrix = (c_uint16*(MATRIX_L*MATRIX_L))()
seeds_x = (c_int*MAX_SEEDS)()
seeds_y = (c_int*MAX_SEEDS)()
n_seeds = 0 #This will be setted with set_seeds, dont change it manually
threaded = 1 # 1 yes, 0 no, you choose

def set_seeds(X, Y, xOrigin, yOrigin): # X and Y are arrays
  xmax = max(X)
  ymax = max(Y)
  xmin = min(X)
  ymin = min(Y)
  REAL_L = max(xmax - xmin, ymax - ymin)
  global n_seeds 
  n_seeds = len(X)
  for i in range(n_seeds):
    seeds_x[i] = c_int(int(MATRIX_L*(X[i]-xmin)/REAL_L))
    seeds_y[i] = c_int(int(MATRIX_L*(Y[i]-ymin)/REAL_L))
  xOriginTransformed = int(MATRIX_L*(xOrigin-xmin)/REAL_L)
  yOriginTransformed = int(MATRIX_L*(yOrigin-ymin)/REAL_L)
  return xOriginTransformed, yOriginTransformed

print("\n")

coordinatesTransformed = set_seeds(coordsX, coordsY, xOrigin, yOrigin)

voronoi(matrix, seeds_x, seeds_y, n_seeds, threaded)

# transform matrix into a 2D numpy array
matrix = np.ctypeslib.as_array(matrix)
matrix = matrix.reshape(MATRIX_L, MATRIX_L)

# plot matrix
plt.imshow(matrix, cmap='gray')
plt.show()
