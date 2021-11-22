import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:frontend/services/voronoi_service.dart';
import 'package:location/location.dart';

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
    var base2 = useState("");
    var seedResult = useState("");
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
              'You are looking for $amenity within $metersAround meters around',
              style: Theme.of(context).textTheme.bodyText1,
              textAlign: TextAlign.center,
            ),
            ElevatedButton(
              child: const Text('Get results'),
              onPressed: () async {
                var result = await VoronoiService.getVoronoi(
                    locationData, amenity, metersAround);

                base1.value = result.encodedImg;
                base2.value = result.encodedImg2;
                seedResult.value = result.seedResult.toString();
              },
            ),
            if (base1.value != "") ...[
              Text(seedResult.value),
              Image.memory(base64Decode(base1.value), height: 300, width: 300),
            ],
            ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop();
                },
                style: ButtonStyle(
                  backgroundColor: MaterialStateProperty.all(Colors.red),
                ),
                child: const Text("Back"))
          ],
        )));
  }
}
