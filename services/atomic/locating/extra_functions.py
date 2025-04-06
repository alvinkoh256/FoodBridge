from invokes import invoke_http
from pydantic import BaseModel
from dotenv import load_dotenv
from math import radians, cos, sin, asin, sqrt
import os
import urllib.parse

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

# Function to convert product address to coords
# returns product coordinate dict
def convertAddress(address):
    coordinate = None
    encoded_address = urllib.parse.quote(address)
    formatted_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={GOOGLE_MAPS_API_KEY}"
    result = invoke_http(formatted_url)
    coordinate = result["results"][0]["geometry"]["location"]
    return coordinate

# Function to find the closest community center coords w/ prod coords
# returns cc coordinate dict
def find_closest_cc(product_coords):
    headers = {
        "Content-Type":"application/json",
        "X-Goog-Api-Key":GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask":"places.displayName,places.formattedAddress,places.location"
    }
    body = {
        "includedTypes":"community_center",
        "locationRestriction": {
            "circle": {
            "center": {
                "latitude": product_coords["lat"],
                "longitude": product_coords["lng"]},
            "radius": 2000
            }
        }
    }
    url = "https://places.googleapis.com/v1/places:searchNearby"
    places_list = invoke_http(url,'POST',body,headers=headers)

    res = None

    for places in places_list["places"]:
        display_name = places["displayName"]["text"]
        if ("Community Centre" in display_name) or ("Community Club" in display_name):
            formatted_address = places["formattedAddress"]
            coordinates = places["location"]
            res = {
                "display_name": display_name,
                "address": formatted_address,
                "coordinates":coordinates
            }
            return res
    return res

# Function to find the center point with community center coords & product address coords as input
def get_center_point(product_coord,cc_coord):
    product_lat = product_coord["lat"]
    product_long = product_coord["lng"]
    cc_lat = cc_coord["lat"]
    cc_long = cc_coord["lng"]

    center_point_coordinate = {
        "latitude":(product_lat+cc_lat)/2,
        "longitude":(product_long+cc_long)/2
    }
    return center_point_coordinate

# Function to find the closest users in a 2km radius w/ userList and midpoint
def find_closest_users(center_coord, user_list):
    res = []
    for user in user_list:
        user_address = user.userAddress
        user_coords = convertAddress(user_address)
        distance_difference = haversine(center_coord["longitude"],center_coord["latitude"],user_coords["lng"],user_coords["lat"])
        if distance_difference<2:
            res.append(user.userId)
    return res

# Find the hub closest to the product address
def get_closest_hub(hub_list, product_coords):
    closest_hub = {}
    for hub in hub_list:
        hub_address = hub.hubAddress
        hub_coords = convertAddress(hub_address)
        dist_to_product = haversine(hub_coords["lng"],hub_coords["lat"],product_coords["lng"],product_coords["lat"])

        hub_res = {
            "hubID": hub.hubID,
            "hubName": hub.hubName,
            "hubAddress": hub.hubAddress,
            "distToProduct": dist_to_product
        }

        if closest_hub == {} or (dist_to_product < closest_hub["distToProduct"]):
            closest_hub = hub_res
    print(closest_hub)
    return closest_hub

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

# hub_list =     [
#         {
#             "hubID": 6,
#             "hubName": "Bedok Ixora RC",
#             "hubAddress": "51 New Upp Changi Rd #01-1500, S461051"
#         },
#         {
#             "hubID": 1,
#             "hubName": "Bedok Orchard RC",
#             "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"
#         },
#         {
#             "hubID": 12,
#             "hubName": "Bishan East Zone 5 RN",
#             "hubAddress": "145 Bishan St 11 #01-99, S570145"
#         },
#         {
#             "hubID": 3,
#             "hubName": "Eunos Zone 6 RN",
#             "hubAddress": "671 Jalan Damai #01-03, S410671"
#         },
#         {
#             "hubID": 2,
#             "hubName": "Eunos Zone 7 RN",
#             "hubAddress": "114 Bedok Reservoir Rd #01-136, S470114"
#         },
#         {
#             "hubID": 9,
#             "hubName": "Geylang West CC",
#             "hubAddress": "1205 Upper Boon Keng Road, S387311"
#         },
#         {
#             "hubID": 5,
#             "hubName": "Kampong Chai Chee Rainbow Ville RN",
#             "hubAddress": "404 Bedok North Ave 3 #01-225, S460404"
#         },
#         {
#             "hubID": 8,
#             "hubName": "Pine Close RN",
#             "hubAddress": "5 Pine Close #01-141, S391005"
#         },
#         {
#             "hubID": 4,
#             "hubName": "Ping Yi Garden RC",
#             "hubAddress": "50 Chai Chee St #01-841, S461050"
#         },
#         {
#             "hubID": 7,
#             "hubName": "Siglap South CC",
#             "hubAddress": "6 Palm Road, S456441"
#         },
#         {
#             "hubID": 10,
#             "hubName": "Whampoa CC",
#             "hubAddress": "300 Whampoa Drive, S327737"
#         },
#         {
#             "hubID": 11,
#             "hubName": "Whampoa Lorong Limau RN",
#             "hubAddress": "76 Lor Limau #01-07, S320076"
#         }
#     ]
# temp_coords = {
#     "lat":1.323104904706169,
#     "lng":103.9223963418113
# }
# print(get_closest_hub(hub_list,temp_coords))