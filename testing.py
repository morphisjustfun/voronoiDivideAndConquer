import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import math

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


# get mercator coordinates
def mercator(lat, lon, width, height):
    x = (lon + 180) * (width / 360)
    latRad = lat * math.pi / 180

    mercN = math.log(math.tan((math.pi / 4) + (latRad / 2)))
    y = (height / 2) - (width * mercN / (2 * math.pi))
    return int(x), int(y)


coords = []

print(data['elements'])
for element in data['elements']:
    if element['type'] == 'node':
        lat = element['lat']
        lon = element['lon']
        x, y = mercator(lat, lon, scale, scale)
        coords.append((x, y))
    elif 'center' in element:
        lat = element['center']['lat']
        lon = element['center']['lon']
        x, y = mercator(lat, lon, scale, scale)
        coords.append((x, y))


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


# get max x value from matrix
# get max y value from matrix

plt.plot(matrix[:, 0], matrix[:, 1], 'o')
plt.title('Restaurants near your location')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.axis('equal')
plt.show()

maxXY = max(maxX, maxY)

# find n given that 2^n is greater or equal than maxXY
n = int(math.log(maxXY, 2)) + 1
print(matrix)
print()
print(originTransformed)

def writeNumpyMatrixToFile(filename, matrix):
    with open(filename, 'w') as f:
        for row in matrix:
            for element in row:
                f.write(str(element) + ' ')
            f.write('\n')

# writeNumpyMatrixToFile('./cMultithread/input.txt',matrix)
