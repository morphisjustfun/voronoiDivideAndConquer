import numpy as np
import requests
import json
import matplotlib.pyplot as plt
import math

# amenity
# https://wiki.openstreetmap.org/wiki/Key:amenity

scale = 2**26

amenities = [
    "grit_bin",
    "parking_entrance",
    "pub",
    "cafe",
    "bar",
    "restaurant",
    "biergarten",
    "fast_food",
    "food_court",
    "ice_cream",
    "college",
    "driving_school",
    "kindergarten",
    "language_school",
    "library",
    "toy_library",
    "music_school",
    "school",
    "university",
    "kick-scooter_rental",
    "bicycle_parking",
    "bicycle_repair_station",
    "bicycle_rental",
    "boat_rental",
    "boat_sharing",
    "bus_station",
    "car_rental",
    "car_sharing",
    "car_wash",
    "vehicle_inspection",
    "charging_station",
    "ferry_terminal",
    "fuel",
    "motorcycle_parking",
    "parking",
    "parking_space",
    "taxi",
    "atm",
    "bank",
    "bureau_de_change",
    "baby_hatch",
    "clinic",
    "dentist",
    "doctors",
    "hospital",
    "nursing_home",
    "social_facility",
    "pharmacy",
    "veterinary",
    "arts_centre",
    "brothel",
    "casino",
    "cinema",
    "community_centre",
    "conference_centre",
    "events_venue",
    "fountain",
    "gambling",
    "love_hotel",
    "nightclub",
    "amenity=stripclub",
    "planetarium",
    "public_bookcase",
    "social_centre",
    "stripclub",
    "studio",
    "swingerclub",
    "theatre",
    "courthouse",
    "embassy",
    "fire_station",
    "police",
    "post_box",
    "post_depot",
    "post_office",
    "prison",
    "ranger_station",
    "townhall",
    "bbq",
    "bench",
    "dog_toilet",
    "drinking_water",
    "give_box",
    "freeshop",
    "shelter",
    "shower",
    "telephone",
    "toilets",
    "water_point",
    "watering_place",
    "sanitary_dump_station",
    "recycling",
    "waste_basket",
    "waste_disposal",
    "waste_transfer_station",
    "animal_boarding",
    "animal_breeding",
    "animal_shelter",
    "baking_oven",
    "childcare",
    "clock",
    "crematorium",
    "dive_centre",
    "funeral_hall",
    "grave_yard",
    "gym",
    "hunting_stand",
    "internet_cafe",
    "kitchen",
    "kneipp_water_cure",
    "lounger",
    "marketplace",
    "monastery",
    "photo_booth",
    "place_of_mourning",
    "place_of_worship",
    "the article",
    "public_bath",
    "public_building",
    "refugee_site",
    "vending_machine",
    "yes"
]

# overpass query to get all hospitals around 10km of radius around the
# given coordinates


def get_hospitals(meters, amenity, latitude, longitude):
    query = '''[out:json][timeout:25];
    (
    nwr["amenity"="{}"](around:{},{},{});
    );
    out body;
    out center;
    '''.format(amenity, meters, latitude, longitude)
    return query

# get my coordinates


def get_my_coordinates():
    url = 'https://ipinfo.io/json'
    response = requests.get(url)
    data = response.json()
    lat = data['loc'].split(',')[0]
    lon = data['loc'].split(',')[1]
    return lat, lon


overpass_url = 'http://overpass-api.de/api/interpreter'
coordinates = get_my_coordinates()

overpass_query = get_hospitals(
    10000,
    'school',
    # amenities[5],
    coordinates[0],
    coordinates[1])
response = requests.get(overpass_url, params={'data': overpass_query})
data = response.json()


# get mercator coordinates
def mercator(lat, lon, width, height):
    x = (lon + 180) * (width / 360)
    latRad = lat * math.pi / 180

    mercN = math.log(math.tan((math.pi / 4) + (latRad / 2)))
    y = (height / 2) - (width * mercN / (2 * math.pi))
    return int(x), int(y)


coords = []
for element in data['elements']:
    if element['type'] == 'node':
        lon = element['lon']
        lat = element['lat']
        x, y = mercator(lat, lon, scale, scale)
        coords.append((x, y))
    elif 'center' in element:
        lon = element['center']['lon']
        lat = element['center']['lat']
        x, y = mercator(lat, lon, scale , scale)
        coords.append((x, y))

X = np.array(coords)

X = X - X.min(axis=0)

plt.plot(X[:, 0], X[:, 1], 'o')
plt.title('Restaurants near your location')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.axis('equal')
plt.show()


"""

# shift elements to match origin
X = X - X.min(axis=0)

# get max x and y
x_max = X[:, 0].max()
y_max = X[:, 1].max()
print(x_max, y_max)

# scale matrix

"""
