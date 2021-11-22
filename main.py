import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import math
from constants import AMENITIES, OVERPASS_URL
import matplotlib
import random

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
    os.system(
        'convert out.png -fuzz 20% -fill none -draw "matte 0,0 floodfill" outTransparent.png')


def selectedSeed(matrix, originTransformed):
    idSelected = matrix[int(originTransformed[0])][int(originTransformed[1])]
    print(pointsData[int(idSelected)])


if __name__ == '__main__':
    # set location of script to location of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    meters = 1000
    scale = 2**26
    amenity = AMENITIES[12]
    # amenity = AMENITIES[5]
    # amenity = AMENITIES[17]
    coordinates = getMyCoordinates()
    dataOverpass = getHospitalsQuery(
        meters, amenity, coordinates[0], coordinates[1])
    matrixSeeds, n, originTransformed, pointsData = getMatrixFormatted(
        dataOverpass, coordinates, scale)

    writeNumpyMatrixToFile('./cMultithread/input.txt', matrixSeeds)

    matrix = getMatrixFromCFunction(n, len(pointsData), 3)

    maxRadius = transformMatrix(matrix, matrixSeeds, originTransformed)

    print(selectedSeed(matrix, originTransformed))

    plotHelper(matrix, pointsData, matrixSeeds, originTransformed)
