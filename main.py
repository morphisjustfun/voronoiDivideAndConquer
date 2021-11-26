import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import math
from constants import AMENITIES, OVERPASS_URL
import matplotlib
import random
from ctypes import *

# filename: written file by c function
# n: 2^n = length of matrix
# seeds: number of random seeds
# threads: number of threads
# threaded: 1 for threaded, 0 for not threaded


def getMatrixFromCFunction(
        n,
        seeds,
        threads,
        threaded=1,
        filename="cMultithread/output.txt"):
    commandLine = f"cd cMultithread && make && ./main.x {threaded} {n} {seeds} {threads} print && cd .."
    os.system(commandLine)
    matrix = np.loadtxt(filename)
    # delete filename
    return matrix


def writeNumpyMatrixToFile(filename, matrix):
    with open(filename, 'w') as f:
        for row in matrix:
            for element in row:
                f.write(str(element) + ' ')
            f.write('\n')


def getHospitalsQuery(meters, amenity, latitude, longitude):
    query = '''[out:json][timeout:25];
    (
    nwr["amenity"="{}"](around:{},{},{});
    );
    out body;
    out center;
    '''.format(amenity, meters, latitude, longitude)
    response = requests.get(OVERPASS_URL, params={'data': query})
    return response.json()


# testing gps will be used
def getMyCoordinates():
    url = 'https://ipinfo.io/json'
    response = requests.get(url)
    data = response.json()
    lat = data['loc'].split(',')[0]
    lon = data['loc'].split(',')[1]
    return lat, lon


def mercator(lat, lon, width, height):
    x = (lon + 180) * (width / 360)
    latRad = lat * math.pi / 180

    mercN = math.log(math.tan((math.pi / 4) + (latRad / 2)))
    y = (height / 2) - (width * mercN / (2 * math.pi))
    return int(x), int(y)


def getMatrixFormatted(data, coordinates, scale):
    coords = []
    pointsData = []
    index = 0
    for element in data['elements']:
        if element['type'] == 'node':
            lat = element['lat']
            lon = element['lon']
            x, y = mercator(lat, lon, scale, scale)
            coords.append((x, y))
            pointsData.append((index, element))
            index += 1
        elif 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
            x, y = mercator(lat, lon, scale, scale)
            coords.append((x, y))
            pointsData.append((index, element))
            index += 1

    xOrigin, yOrigin = mercator(
        float(coordinates[0]),
        float(coordinates[1]),
        scale, scale)
    coords.append((xOrigin, yOrigin))

    matrix = np.array(coords)

    matrix = matrix - matrix.min(axis=0)

    # delete last element from X
    originTransformed = matrix[-1]
    matrix = matrix[:-1]

    maxX = matrix[:, 0].max()
    maxY = matrix[:, 1].max()

    maxXY = max(maxX, maxY)

    # find n given that 2^n is greater or equal than maxXY
    n = int(math.log(maxXY, 2)) + 1

    return matrix, n, originTransformed, pointsData


def transformMatrix(matrix, matrixSeeds, originTransformed):
    maxRadius = 0
    for i in range(len(matrixSeeds)):
        radius = math.sqrt(
            (matrixSeeds[i][0] - originTransformed[0])**2 +
            (matrixSeeds[i][1] - originTransformed[1])**2)
        if radius > maxRadius:
            maxRadius = radius

    # set as -1 all elements inside matrix that are out of maxRadius
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if math.sqrt(
                (i - originTransformed[0])**2 +
                    (j - originTransformed[1])**2) > maxRadius * 23 / 20:
                matrix[i][j] = -1

    return maxRadius


def getRandomColors(n):
    colors = []
    for i in range(n * 30):
        # colors.append(matplotlib.colors.to_hex(matplotlib.colors.hsv_to_rgb([random.random(), 1, 1])))
        if i == 0:
            colors.append(matplotlib.colors.to_hex( # type: ignore
                matplotlib.colors.hsv_to_rgb([0, 0, 1]))) # type: ignore
        else:
            colors.append(matplotlib.colors.to_hex( # type: ignore
                matplotlib.colors.hsv_to_rgb([random.random(), 1, 1]))) # type: ignore
    return colors


def plotHelper(matrix, pointsData, matrixSeeds, originTransformed):
    cmap = matplotlib.colors.ListedColormap( # type: ignore
        getRandomColors(len(pointsData)), name='colors', N=None)
    plt.imshow(matrix, cmap=cmap, interpolation='nearest', origin="lower")
    plt.scatter(
        originTransformed[0],
        originTransformed[1],
        c='white',
        s=100,
        edgecolors=['black'])
    for i in range(len(pointsData)):
        plt.scatter(
            matrixSeeds[i][0],
            matrixSeeds[i][1],
            c='white',
            s=10,
            edgecolors=['black'])
    plt.axis('off')
    plt.savefig(
        'out.png',
        bbox_inches='tight',
        transparent=True,
        pad_inches=0,
        dpi=600)


def selectedSeed(matrix, originTransformed, pointsData):
    idSelected = matrix[int(originTransformed[0])][int(originTransformed[1])]
    print(pointsData[int(idSelected)])

def getMatrixFromData(data):
    coordsX = []
    coordsY = []
    pointsData = []
    i = 0
    for element in data['elements']:
        if element['type'] == 'node':
            lat = element['lat']
            lon = element['lon']
            coordsY.append(lat)
            coordsX.append(lon)
            pointsData.append((i, element))
            i += 1
        elif 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
            coordsY.append(lat)
            coordsX.append(lon)
            pointsData.append((i, element))
            i += 1
    return coordsX, coordsY, pointsData

def set_seeds(X, Y, xOrigin, yOrigin, n_seeds, seeds_x, seeds_y, MATRIX_L): # X and Y are arrays
    xmax = max(X)
    ymax = max(Y)
    xmin = min(X)
    ymin = min(Y)
    REAL_L = max(xmax - xmin, ymax - ymin)
    n_seeds = len(X)
    for i in range(n_seeds):
      seeds_x[i] = c_int(int(MATRIX_L*(X[i]-xmin)/REAL_L))
      seeds_y[i] = c_int(int(MATRIX_L*(Y[i]-ymin)/REAL_L))
    xOriginTransformed = int(MATRIX_L*(xOrigin-xmin)/REAL_L)
    yOriginTransformed = int(MATRIX_L*(yOrigin-ymin)/REAL_L)
    return xOriginTransformed, yOriginTransformed, n_seeds


def getDataFromFunction(X, Y, xOrigin, yOrigin, max_seeds):
    CVoronoi  = CDLL(os.path.abspath("./cMultithread/voronoi_2048.so"))
    voronoi = CVoronoi.voronoi_2048
    voronoi.argtypes = [POINTER(c_uint16), POINTER(c_int), POINTER(c_int), c_int, c_int]

    MATRIX_L = 2048 #Don't change 2048
    MAX_SEEDS = max_seeds #Realistic max (to avoid realloc)

    matrix = (c_uint16*(MATRIX_L*MATRIX_L))()
    seeds_x = (c_int*MAX_SEEDS)()
    seeds_y = (c_int*MAX_SEEDS)()
    n_seeds = 0 #This will be setted with set_seeds, dont change it manually
    threaded = 1 # 1 yes, 0 no, you choose

    xOriginTransformed, yOriginTransformed, n_seeds = set_seeds(X, Y, xOrigin, yOrigin, n_seeds, seeds_x, seeds_y, MATRIX_L)

    voronoi(matrix, seeds_x, seeds_y, n_seeds, threaded)

    seeds_x = np.array(seeds_x)
    seeds_y = np.array(seeds_y)

    seedsCord = np.column_stack((seeds_y, seeds_x))
    
    return matrix, n_seeds, xOriginTransformed, yOriginTransformed, MATRIX_L, seedsCord


if __name__ == '__main__':
    # set location of script to location of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    meters = 2000
    # amenity = AMENITIES[12]
    amenity = 'school'
    coordinates = getMyCoordinates()
    dataOverpass = getHospitalsQuery(
        meters, amenity, coordinates[0], coordinates[1])


    coordsX, coordsY, pointsData = getMatrixFromData(dataOverpass)

    MAX_SEEDS = len(pointsData)

    yOrigin, xOrigin = coordinates
    yOrigin = float(yOrigin)
    xOrigin = float(xOrigin)
    
    matrix, n_seeds, xOriginTransformed, yOriginTransformed, MATRIX_L, coords  = getDataFromFunction(coordsX, coordsY, xOrigin, yOrigin, MAX_SEEDS)

    matrix = np.ctypeslib.as_array(matrix)
    matrix = matrix.reshape(MATRIX_L, MATRIX_L)

    plotHelper(matrix, pointsData, coords, (xOriginTransformed, yOriginTransformed))

    selectedSeedM = matrix[xOriginTransformed][yOriginTransformed]
    print(pointsData[selectedSeedM] )
