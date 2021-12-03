from flask import Flask, request, jsonify, Response
from datetime import datetime
from base64 import encodebytes
from functions import *
import json
import io
from constants import AMENITIES
import os
import pyimgur

CLIENT_ID = os.environ['IMGUR_CLIENT_ID']
im = pyimgur.Imgur(CLIENT_ID)

app = Flask(__name__)


@app.route('/amenities', methods=['GET'])
def getAmenities():
    return json.dumps(AMENITIES)


@app.route('/getVoronoi', methods=["POST"])
def getVoronoi():
    data = request.get_json()
    if data is not None:
        meters = data["meters"]
        amenity = data["amenity"]
        lat = data["geolocation"]["lat"]
        lon = data["geolocation"]["lon"]
        coordinates = (lat, lon)

        dataOverpass = getQuery(
            meters, amenity, coordinates[0], coordinates[1])

        coordsX, coordsY, pointsData = getMatrixFromData(dataOverpass)

        MAX_SEEDS = len(pointsData)

        yOrigin, xOrigin = coordinates
        yOrigin = float(yOrigin)
        xOrigin = float(xOrigin)

        matrix, n_seeds, xOriginTransformed, yOriginTransformed, MATRIX_L, coords = getDataFromFunction(
            coordsX, coordsY, xOrigin, yOrigin, MAX_SEEDS)

        matrix = np.ctypeslib.as_array(matrix)
        matrix = matrix.reshape(MATRIX_L, MATRIX_L)

        plotHelper(matrix, pointsData, coords,
                   (xOriginTransformed, yOriginTransformed))

        # current date with title
        uploadedImage = im.upload_image('out.png', title=f'Flutter-Voronoi-{datetime.now()}')

        selectedSeedM = pointsData[matrix[xOriginTransformed]
                                   [yOriginTransformed]]

        jsonMessage = json.dumps({
            "seedResult": selectedSeedM,
            "encoded_img": uploadedImage.link
        })

        return Response(jsonMessage, mimetype='application/json', status=200)
    return Response(status=400)


if __name__ == '__main__':
    # os.system("gcc -shared -o ../cMultithread/voronoi_2048.so -fPIC ../cMultithread/voronoi_2048.c")
    app.run(host='0.0.0.0', port=8000)
