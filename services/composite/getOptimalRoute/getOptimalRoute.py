from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import redis
import os

app = Flask(__name__)

CORS(app)

# Redis cache setup
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Get absolute path to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
env_path = os.path.join(project_root, '.env')

# Load the .env from project root
load_dotenv(env_path)

# Environment variables
HUB_SERVICE_URL = os.getenv("HUB_SERVICE_URL", "http://hub:5010")
ROUTE_SERVICE_URL = os.getenv("ROUTE_SERVICE_URL", "http://route:5011")

@app.route('/get-optimal-route/<foodbank_id>', methods=['GET'])
def get_optimal_route(foodbank_id):
    try:
        if not foodbank_id:
            return jsonify({"error": "foodbankId is required"}), 400
        
        # Step 1: Retrieve food bank data from Hub microservice
        hub_url = f"{HUB_SERVICE_URL}/internal/hub/foodbank/{foodbank_id}"
        hub_response = requests.get(hub_url)
        
        if hub_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve food bank data"}), 500

        foodbank_data = hub_response.json()
        foodbank_name = foodbank_data.get("foodbankName")
        foodbank_address = foodbank_data.get("foodbankAddress")

        if not all([foodbank_name, foodbank_address]):
            return jsonify({"error": "Invalid data received from Hub service"}), 400

        # Step 2: Store in cache for temporary reference
        redis_client.setex(f"foodbank:{foodbank_id}", 300, str(foodbank_data))  # Expires in 5 min

        # Step 3: Send data to Route service for planning
        route_request_payload = {
            "foodbankName": foodbank_name,
            "foodbankAddress": foodbank_address,
            "reservedHubs": foodbank_data.get("reservedHubs", [])
        }
        route_url = f"{ROUTE_SERVICE_URL}/routing"
        route_response = requests.post(route_url, json=route_request_payload)
        if route_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve route data"}), 500

        route_data = route_response.json()

        # Step 4: Generate Google Maps route link for the UI
        waypoints = "/".join([hub["hubAddress"].replace("#", "") for hub in route_data["route"]])
        google_maps_url = f"https://www.google.com/maps/dir/{format_address(foodbank_address)}/{format_address(waypoints)}/{format_address(foodbank_address)}"

        # Step 5: Return the data to UI
        return jsonify({
            "foodbankName": foodbank_name,
            "foodbankAddress": foodbank_address,
            "route": route_data["route"],
            "googleMapsLink": google_maps_url
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Format addresses correctly for Google Maps URL
def format_address(address):
    return address.replace(" ", "+")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5016)