from flask import Flask, jsonify
from flask_cors import CORS
import requests
import redis

app = Flask(__name__)

CORS(app)

# Redis cache setup
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Hub and Route microservices URLs
HUB_SERVICE_URL = "http://localhost:5010/internal/hub/foodbank/123"
ROUTE_SERVICE_URL = "http://localhost:5011/route/routing"

@app.route('/get-optimal-route', methods=['GET'])
def get_optimal_route():
    try:
        # Step 1: Retrieve food bank data from Hub microservice
        hub_response = requests.get(HUB_SERVICE_URL)
        if hub_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve food bank data"}), 500

        foodbank_data = hub_response.json()
        foodbank_id = foodbank_data.get("foodbankID")
        foodbank_name = foodbank_data.get("foodbankName")
        foodbank_address = foodbank_data.get("foodbankAddress")

        if not all([foodbank_id, foodbank_name, foodbank_address]):
            return jsonify({"error": "Invalid data received from Hub service"}), 400

        # Step 2: Store in cache for temporary reference
        redis_client.setex(f"foodbank:{foodbank_id}", 300, str(foodbank_data))  # Expires in 5 min

        # Step 3: Send data to Route service for planning
        route_request_payload = {
            "foodbankName": foodbank_name,
            "foodbankAddress": foodbank_address
        }
        route_response = requests.post(ROUTE_SERVICE_URL, json=route_request_payload)
        if route_response.status_code != 200:
            return jsonify({"error": "Failed to retrieve route data"}), 500

        route_data = route_response.json()

        # Step 4: Generate Google Maps route link for the UI
        waypoints = "/".join([hub["hubAddress"] for hub in route_data["route"]])
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
    app.run(port=5016)