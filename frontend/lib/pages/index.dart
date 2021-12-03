import 'package:flutter/material.dart';
import 'package:flutter_hooks/flutter_hooks.dart';
import 'package:frontend/services/voronoi_service.dart';
import 'package:location/location.dart';
import 'result.dart';

class Index extends HookWidget {
  final String title;
  const Index({Key? key, required this.title}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    var locationPermission = useState(true);
    var currentLocation = useState<dynamic>(null);
    var metersAround = useState(1000);
    var amenitySelected = useState('school');
    var amenitiesList = useState(['school']);

    useEffect(() {
      void getAmenities() async {
        var amenities = await VoronoiService.getAmenities();
        amenitiesList.value = amenities;
      }

      void getLocation() async {
        var location = Location();
        bool _serviceEnabled;
        PermissionStatus _permissionGranted;

        _serviceEnabled = await location.serviceEnabled();

        if (!_serviceEnabled) {
          await location.requestService();
          if (!_serviceEnabled) {
            return null;
          }
        }

        _permissionGranted = await location.hasPermission();

        if (_permissionGranted == PermissionStatus.denied) {
          _permissionGranted = await location.requestPermission();
          if (_permissionGranted != PermissionStatus.granted) {
            locationPermission.value = false;
            return null;
          }
          locationPermission.value = true;
        }
        currentLocation.value = await location.getLocation();
      }

      getLocation();
      getAmenities();
    }, []);

    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        elevation: 10,
        centerTitle: true,
      ),
      body: Center(
        child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: <Widget>[
              if (!locationPermission.value ||
                  currentLocation.value is LocationData)
                FirstColumn(
                    locationPermission: locationPermission,
                    currentLocation: currentLocation),
              SecondColumn(
                  locationPermission: locationPermission,
                  currentLocation: currentLocation,
                  amenitySelected: amenitySelected,
                  metersAround: metersAround,
                  amenitiesList: amenitiesList),
            ]),
      ),
    );
  }
}

class FirstColumn extends StatelessWidget {
  final ValueNotifier<bool> locationPermission;
  final ValueNotifier<dynamic> currentLocation;

  const FirstColumn({
    Key? key,
    required this.locationPermission,
    required this.currentLocation,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(children: [
      if (!locationPermission.value) ...[
        Text('Location services were denied',
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headline5?.merge(
                  const TextStyle(
                    color: Colors.red,
                  ),
                ))
      ] else if (currentLocation.value is LocationData) ...[
        Row(mainAxisAlignment: MainAxisAlignment.center, children: <Widget>[
          Text(
            'Latitude: ${(currentLocation.value as LocationData).latitude}',
            style: Theme.of(context).textTheme.bodyText1,
          )
        ]),
        Row(mainAxisAlignment: MainAxisAlignment.center, children: <Widget>[
          Text(
            'Longitude: ${(currentLocation.value as LocationData).longitude}',
            style: Theme.of(context).textTheme.bodyText1,
          ),
        ])
      ]
    ]);
  }
}

class SecondColumn extends StatelessWidget {
  final ValueNotifier<bool> locationPermission;
  final ValueNotifier<dynamic> currentLocation;
  final ValueNotifier<String> amenitySelected;
  final ValueNotifier<int> metersAround;
  final ValueNotifier<List<String>> amenitiesList;
  const SecondColumn({
    Key? key,
    required this.locationPermission,
    required this.currentLocation,
    required this.amenitySelected,
    required this.metersAround,
    required this.amenitiesList,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Column(children: <Widget>[
      if (locationPermission.value &&
          currentLocation.value is LocationData) ...[
        Row(mainAxisAlignment: MainAxisAlignment.center, children: <Widget>[
          DropdownButton<String>(
              value: amenitySelected.value,
              items: amenitiesList.value.map((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  child: Text(value),
                );
              }).toList(),
              onChanged: (String? newValue) {
                amenitySelected.value = newValue!;
              })
        ]),
        // input for meters around
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text('Meters around: '),
            Text(metersAround.value.toString()),
            Slider(
              value: metersAround.value.toDouble(),
              min: 100,
              max: 50000,
              divisions: 50,
              onChanged: (double newValue) {
                metersAround.value = newValue.round();
              },
            ),
          ],
        ),
        // button to get the results
        ElevatedButton(
            child: Text('Get results'),
            onPressed: () {
              // alert
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => Result(
                    locationData: currentLocation.value,
                    amenity: amenitySelected.value,
                    metersAround: metersAround.value,
                  ),
                ),
              );
            })
      ] else if (locationPermission.value) ...[
        const CircularProgressIndicator()
      ]
    ]);
  }
}
