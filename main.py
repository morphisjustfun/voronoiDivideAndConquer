import os
import numpy as np
import requests
import matplotlib.pyplot as plt
import math
from constants import AMENITIES, OVERPASS_URL

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
    os.system(f"rm {filename}")
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
    

if __name__ == '__main__':
    # set location of script to location of this file
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    meters = 1000
    scale = 2**26
    amenity = AMENITIES[17]
    coordinates = getMyCoordinates()
    dataOverpass = getHospitalsQuery(meters, amenity, coordinates[0], coordinates[1])
    matrix, n, originTransformed, pointsData = getMatrixFormatted(dataOverpass, coordinates, scale)

    writeNumpyMatrixToFile('./cMultithread/input.txt',matrix)
    matrix = getMatrixFromCFunction(n, len(pointsData), 3)
    idSelected = matrix[int(originTransformed[0])][int(originTransformed[1])]
    print(f"Nearest {amenity}")
    print(pointsData[int(idSelected)])
