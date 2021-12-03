import 'dart:convert';
import 'dart:math' show cos, pi;

import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:frontend/services/voronoi_service.dart';
import 'package:location/location.dart';
import 'package:flutter_map/flutter_map.dart';
import "package:latlong2/latlong.dart";

class Result extends HookWidget {
  final String amenity;
  final LocationData locationData;
  final int metersAround;

  const Result(
      {Key? key,
      required this.amenity,
      required this.locationData,
      required this.metersAround})
      : super(key: key);

  @override
  Widget build(BuildContext context) {
    var base1 = useState("");
    var seedResult = useState("");
    var latNearest = useState(0.0);
    var lonNearest = useState(0.0);

    return Scaffold(
        appBar: AppBar(
          title: const Text("Result"),
          centerTitle: true,
        ),
        body: Center(
            child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            Text(
              'You are looking for $amenity within $metersAround meters',
              style: Theme.of(context).textTheme.bodyText1,
              textAlign: TextAlign.center,
            ),
            ElevatedButton(
              child: const Text('Get results'),
              onPressed: () async {
                var result = await VoronoiService.getVoronoi(
                    locationData, amenity, metersAround);

                if (result.success) {
                  base1.value = result.encodedImg;

                  seedResult.value =
                      result.seedResult[1]['tags']['name'].toString();
                  /* result.seedResult[1].toString(); */

                  if (result.seedResult[1]['center'] != null) {
                    latNearest.value =
                        result.seedResult[1]['center']['lat'].toDouble();
                    lonNearest.value =
                        result.seedResult[1]['center']['lon'].toDouble();
                  } else {
                    latNearest.value = result.seedResult[1]['lat'].toDouble();
                    lonNearest.value = result.seedResult[1]['lon'].toDouble();
                  }
                } else {
                  base1.value = "error";
                  seedResult.value = "Error 🆘 :(";
                }
              },
            ),
            if (base1.value != "" && base1.value != "error") ...[
              Text(seedResult.value),
              Transform(
                alignment: Alignment.center,
                transform: Matrix4.rotationX(0),
                child: Transform(
                  alignment: Alignment.center,
                  transform: Matrix4.rotationY(0),
                  child: Image.network(base1.value, height: 250, width: 250),
                ),
              )
            ],
            if (base1.value == "error") ...[
              Text(seedResult.value),
            ],
            ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all(Colors.red),
                ),
                child: const Text("Back")),
            SizedBox(
              height: 250,
              width: 250,
              child: FlutterMap(
                options: MapOptions(
                  /* center: */
                  /*     LatLng(locationData.latitude!, locationData.longitude!), */
                  /* zoom: 16.0, */
                  bounds: LatLngBounds(
                      LatLng(
                          locationData.latitude! +
                              metersAround / (110.574 * 1000),
                          locationData.longitude! -
                              // cosine
                              metersAround /
                                  (111.320 *
                                      cos((locationData.latitude! +
                                              metersAround / (110.574 * 1000)) *
                                          0.0174533) *
                                      1000)),
                      LatLng(
                          locationData.latitude! -
                              metersAround / (110.574 * 1000),
                          locationData.longitude! +
                              // cosine
                              metersAround /
                                  (111.320 *
                                      cos((locationData.latitude! -
                                              metersAround / (110.574 * 1000)) *
                                          0.0174533) *
                                      1000))),
                ),
                layers: [
                  TileLayerOptions(
                    urlTemplate:
                        'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    subdomains: ['a', 'b', 'c'],
                  ),
                  MarkerLayerOptions(
                    markers: [
                      Marker(
                        width: 80.0,
                        height: 80.0,
                        point: LatLng(
                            locationData.latitude!, locationData.longitude!),
                        builder: (ctx) => const Icon(
                          Icons.location_on,
                          color: Colors.red,
                        ),
                      ),
                      Marker(
                        width: 80.0,
                        height: 80.0,
                        point: LatLng(latNearest.value, lonNearest.value),
                        builder: (ctx) => const Icon(
                          Icons.location_on,
                          color: Colors.green,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            )
          ],
        )));
  }
}
