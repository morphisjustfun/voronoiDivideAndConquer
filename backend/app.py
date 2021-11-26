from flask import Flask, request, jsonify, Response
from base64 import encodebytes
from functions import *
import json
import io
from constants import AMENITIES
import os
from PIL import Image

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

        matrix, n_seeds, xOriginTransformed, yOriginTransformed, MATRIX_L, coords  = getDataFromFunction(coordsX, coordsY, xOrigin, yOrigin, MAX_SEEDS)


        matrix = np.ctypeslib.as_array(matrix)
        matrix = matrix.reshape(MATRIX_L, MATRIX_L)

        plotHelper(matrix, pointsData, coords, (xOriginTransformed, yOriginTransformed))

        pil_img = Image.open('out.png', mode='r')
        byte_arr = io.BytesIO()
        pil_img.save(byte_arr, format='PNG')
        encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii').replace('\n', '')

        selectedSeedM = pointsData[matrix[xOriginTransformed][yOriginTransformed]]

        return jsonify(
            {
                "seedResult": selectedSeedM,
                "encoded_img": encoded_img
            }
        )
    return Response(status=400)


if __name__ == '__main__':
    os.system("gcc -shared -o ../cMultithread/voronoi_2048.so -fPIC ../cMultithread/voronoi_2048.c")
    app.run()
