import 'dart:io';

import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:location/location.dart';

/*
{
    "meters": 500,
    "amenity": "school",
    "geolocation": {
        "lat": -12.0432,
        "lon": -77.0282
    }
}
*/
// get class from json above
class Geolocation {
  final double lat;
  final double lon;

  Geolocation({required this.lat, required this.lon});

  factory Geolocation.fromJson(Map<String, dynamic> json) {
    return Geolocation(
      lat: json['lat'],
      lon: json['lon'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'lat': lat,
      'lon': lon,
    };
  }
}

class VoronoiRequest {
  final int meters;
  final String amenity;
  final Geolocation geolocation;

  VoronoiRequest(
      {required this.meters, required this.amenity, required this.geolocation});

  factory VoronoiRequest.fromJson(Map<String, dynamic> json) {
    return VoronoiRequest(
      meters: json['meters'],
      amenity: json['amenity'],
      geolocation: Geolocation.fromJson(json['geolocation']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'meters': meters,
      'amenity': amenity,
      'geolocation': geolocation.toJson(),
    };
  }
}

/*
   {
   "encoded_img": "9",
   "encoded_img_2": "9",
   "seedResult": [
           5,
           {
               "id": 5593327709,
               "lat": -12.0424849,
               "lon": -77.0271946,
               "tags": {
                   "addr:district": "Rimac",
                   "addr:full": "Jiron Julian Piñeiro 385",
                   "addr:province": "Lima",
                   "addr:subdistrict": "Rimac",
                   "amenity": "school",
                   "ele": "161",
                   "isced:level": "1",
                   "name": "Institución Educativa Manuel Gonzales Prada",
                   "note": "Ubicacion_web_med (local)",
                   "ref": "1672252",
                   "source": "minedu.gob.pe"
               },
               "type": "node"
           }
       ]
   }
*/

class VoronoiResponse {
  final String encodedImg;
  final List<dynamic> seedResult;

  VoronoiResponse(
      {required this.encodedImg,
      required this.seedResult});

  factory VoronoiResponse.fromJson(Map<String, dynamic> json) {
    return VoronoiResponse(
      encodedImg: json['encoded_img'],
      seedResult: json['seedResult'],
    );
  }
}

const String baseURL = "http://192.168.1.4:4999";

class VoronoiService {
  static getAmenities() async {
    final client = http.Client();
    final url = Uri.parse('$baseURL/amenities');
    final response = await client.get(url);
    Iterable amenities = json.decode(response.body);
    return amenities.map((amenity) => amenity.toString()).toList();
  }

  static Future<VoronoiResponse> getVoronoi(
      LocationData location, String amenity, int metersAround) async {
    final client = http.Client();
    final body = json.encode(VoronoiRequest(
      meters: metersAround,
      amenity: amenity,
      geolocation: Geolocation(
        lat: location.latitude!,
        lon: location.longitude!,
      ),
    ));

    final url = Uri.parse('$baseURL/getVoronoi');
    final response = await client.post(url,
        headers: {
          HttpHeaders.contentTypeHeader: 'application/json',
          HttpHeaders.acceptHeader: 'application/json',
          HttpHeaders.connectionHeader: 'keep-alive',
        },
        body: body);

    return VoronoiResponse.fromJson(json.decode(response.body));
  }
}
