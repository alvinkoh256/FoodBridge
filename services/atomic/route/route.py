from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import googlemaps
import os

app = Flask(__name__)

CORS(app)

load_dotenv()
ROUTE_GOOGLE_MAPS_API_KEY = os.environ.get('ROUTE_GOOGLE_MAPS_API_KEY')
gmaps = googlemaps.Client(key=ROUTE_GOOGLE_MAPS_API_KEY)

@app.route('/routing', methods=['POST'])
def route():
    data = request.json
    
    if not data or 'foodbankName' not in data or 'foodbankAddress' not in data or 'reservedHubs' not in data:
        return jsonify({"error": "Invalid request data. Required fields: foodbankName, foodbankAddress, hubs"}), 400
           
    food_bank_name = data["foodbankName"]
    food_bank_address = data["foodbankAddress"]
    
    hubs = data["reservedHubs"]
    hub_map = {hub["hubAddress"]: hub["hubName"] for hub in hubs}
    hub_addresses = [hub["hubAddress"] for hub in hubs] 
    waypoints = "|".join(hub_addresses)
    
    try:
        # Planning the route with food bank address and reserved hub addresses using Google Maps
        directions = gmaps.directions(
        origin=food_bank_address,
        destination=food_bank_address,
        waypoints=waypoints,
        optimize_waypoints=True,
        mode="driving"
        )
        
        # No route found
        if not directions:
            return jsonify({"error": "No route found"}), 400
        
        waypoint_order = directions[0]['waypoint_order']
        ordered_hub_addresses = [hub_addresses[i] for i in waypoint_order]
        
        # find hubname given the hub address in ordered hubs, then craft a list with a list of hubnames and hubaddresses
        ordered_hubs = [{"hubName": hub_map[addr], "hubAddress": addr} for addr in ordered_hub_addresses]

        return jsonify({"route": ordered_hubs, 
                        "foodBank": 
                            {"foodbankName": food_bank_name, "foodbankAddress": food_bank_address}
                        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(port=5000)