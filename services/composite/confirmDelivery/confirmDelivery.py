from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from flask_restx import Api, Resource, Namespace, fields
from amqp_lib import publish_message
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', 
          title='Confirm Delivery Service API',
          description='A microservice for confirming deliveries and forwarding to hub service',
          doc='/swagger')

# Environment variables with Docker-friendly defaults
HUB_SERVICE_URL = os.environ.get("HUB_SERVICE_URL", "http://hub:5010")
ACCOUNT_INFO_API_URL = os.environ.get("ACCOUNT_INFO_API_URL", "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")
PRODUCT_LISTING_URL = os.environ.get("PRODUCT_LISTING_URL", "http://product_listing:5005") # change when YH provides

# AMQP Configuration
AMQP_HOST = os.environ.get("AMQP_HOST", "rabbitmq")
AMQP_PORT = int(os.environ.get("AMQP_PORT", "5672"))
AMQP_EXCHANGE = os.environ.get("AMQP_EXCHANGE", "notificationsS3")
AMQP_EXCHANGE_TYPE = os.environ.get("AMQP_EXCHANGE_TYPE", "direct")
AMQP_ROUTING_KEY = os.environ.get("AMQP_ROUTING_KEY", "dropoff")

# Create namespace
ns = api.namespace('confirmDelivery', description='Confirm Delivery operations')

# Define models for request and response validation
item_model = api.model('Item', {
    'itemName': fields.String(required=True, description='Name of the item'),
    'quantity': fields.Integer(required=True, description='Quantity of the item')
})

new_item_model = api.model('NewItem', {
    'itemName': fields.String(required=True, description='Name of the new item'),
    'itemWeight_kg': fields.Float(required=True, description='Weight of the new item in kg'),
    'quantity': fields.Integer(required=True, description='Quantity of the new item'),
    'description': fields.String(description='Description of the new item')
})

# Updated request model to match expected payload
confirm_delivery_model = api.model('ConfirmDeliveryRequest', {
    'volunteerID': fields.String(required=True, description='ID of the volunteer'),
    'productID': fields.Integer(required=True, description='Product ID for validation'),
    'items': fields.List(fields.Nested(item_model), description='List of existing items being dropped off'),
    'newitems': fields.List(fields.Nested(new_item_model), description='List of new items being dropped off')
})

@ns.route('/drop-off')
class ConfirmDelivery(Resource):
    @ns.expect(confirm_delivery_model)
    def post(self):
        """
        Confirm delivery of items to a hub
        
        Workflow:
        1. Retrieve volunteer phone number from Account Info API
        2. Validate product and get hub information
        3. Send notification via AMQP
        4. Update hub inventory
        """
        try:
            data = request.json
            print(f"Received delivery confirmation request: {json.dumps(data)}")
            
            # Step 1: Retrieve volunteer info
            volunteer_info = self.get_volunteer_info(data['volunteerID'])
            if not volunteer_info:
                return {"error": "Could not retrieve volunteer information"}, 404
            
            # Step 2: Validate product and get hub information
            hub_info = self.validate_product(data['productID'])
            if not hub_info:
                return {"error": "Could not retrieve hub information for the product"}, 404
            
            inventory_payload = {
                'hubID': hub_info.get('hubID'),  # Use .get() to avoid KeyError
                'hubName': hub_info.get('hubName'),
                'hubAddress': hub_info.get('hubAddress'),
                'items': data.get('items', []),
                'newitems': data.get('newitems', [])
            }

            if not inventory_payload['hubID']:
                return {"error": "Hub ID is missing in the response from product listing"}, 404

            
            # Step 3: Send notification via AMQP
            notification_payload = self.create_notification_payload(
                data, volunteer_info, hub_info
            )
            self.send_notification(notification_payload)
            
            # Step 4: Update hub inventory
            self.update_hub_inventory(inventory_payload)
            
            return {"message": "Delivery confirmed successfully"}, 200
        
        except Exception as e:
            return {"error": str(e)}, 500
    
    def get_volunteer_info(self, volunteer_id):
        """Retrieve volunteer information from Account Info API"""
        try:
            url = f"{ACCOUNT_INFO_API_URL}/userPhone/{volunteer_id}"
            response = requests.get(url)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error retrieving volunteer info: {e}")
            return None
    
    def validate_product(self, product_id):
        """Validate product and retrieve hub information"""
        try:
            # Construct the URL using the PRODUCT_LISTING_URL environment variable
            url = f"{PRODUCT_LISTING_URL}/ProductCC/{product_id}"
            
            # Make a GET request to retrieve hub information
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Log the full response for debugging
                product_info = response.json()
                print(f"Product Listing response: {json.dumps(product_info, indent=2)}")  # Pretty-print the response
                
                # Check if 'productCCDetails' is in the response
                hub_info = product_info.get('productCCDetails', {})
                if not hub_info:
                    print("Error: No productCCDetails in the response")
                    return None

                # Access 'hubId' inside 'productCCDetails'
                hub_id = hub_info.get('hubID')
                if not hub_id:
                    print("Error: hubID is missing")
                    return None

                # You can return the whole hub info or just 'hubId' based on your needs
                return hub_info  # Or return {'hubId': hub_id, 'hubName': hub_info.get('hubName'), ...}

            else:
                print(f"Failed to retrieve product info. Status code: {response.status_code}")
                print(f"Response text: {response.text}")
                return None
        
        except requests.RequestException as e:
            print(f"Error validating product: {e}")
            return None

    
    def create_notification_payload(self, delivery_data, volunteer_info, hub_info):
        """Create notification payload for AMQP"""
        return {
            "event": "dropoff",
            "volunteerName": volunteer_info.get('userName', 'Unknown Volunteer'),
            "volunteerMobile": volunteer_info.get('userPhoneNumber', 'N/A')
        }
    
    def send_notification(self, payload):
        """Send notification via AMQP"""
        try:
            publish_message(
                hostname=AMQP_HOST,
                port=AMQP_PORT,
                exchange_name=AMQP_EXCHANGE,
                exchange_type=AMQP_EXCHANGE_TYPE,
                routing_key=AMQP_ROUTING_KEY,
                message=payload
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def update_hub_inventory(self, payload):
        """Update hub inventory via internal hub service"""
        try:
            response = requests.post(
                f"{HUB_SERVICE_URL}/internal/hub/updateInventory",
                json=payload
            )
            
            if response.status_code != 200:
                print(f"Error updating hub inventory: {response.text}")
        except Exception as e:
            print(f"Error updating hub inventory: {e}")

if __name__ == '__main__':
    print(f"Starting Confirm Delivery Service with AMQP integration to {AMQP_HOST}:{AMQP_PORT}")
    app.run(host='0.0.0.0', port=5009, debug=True)