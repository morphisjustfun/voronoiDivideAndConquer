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
        scale = 2**26
        coordinates = (lat, lon)

        dataOverpass = getHospitalsQuery(
            meters, amenity, coordinates[0], coordinates[1])

        matrixSeeds, n, originTransformed, pointsData = getMatrixFormatted(
            dataOverpass, coordinates, scale)

        writeNumpyMatrixToFile('../cMultithread/input.txt', matrixSeeds)

        matrix = getMatrixFromCFunction(
            n, len(pointsData), 3, filename="../cMultithread/output.txt")

        maxRadius = transformMatrix(matrix, matrixSeeds, originTransformed)

        seedResult = selectedSeed(matrix, originTransformed, pointsData)

        plotHelper(matrix, pointsData, matrixSeeds, originTransformed)

        pil_img = Image.open('out.png', mode='r')
        byte_arr = io.BytesIO()
        pil_img.save(byte_arr, format='PNG')
        encoded_img = encodebytes(byte_arr.getvalue()).decode('ascii')


        pil_img2 = Image.open('outTransparent.png', mode='r')
        byte_arr2 = io.BytesIO()
        pil_img2.save(byte_arr, format='PNG')
        encoded_img2 = encodebytes(byte_arr.getvalue()).decode('ascii')

        # return json with encoded_img and encoded_img2 and seedResult
        return jsonify(
            {
                "seedResult": seedResult,
                "encoded_img": encoded_img,
                "encoded_img2": encoded_img2
            }
        )
    return Response(status=400)


if __name__ == '__main__':
    app.run()
