from flask import Flask, request, jsonify
import os
import requests
import json
from flask_restx import Api, Resource, Namespace, fields
from amqp_lib import publish_message
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', 
          title='Confirm Delivery Service API',
          description='A microservice for confirming deliveries and forwarding to hub service',
          doc='/swagger')

# Environment variables with Docker-friendly defaults
HUB_SERVICE_URL = os.environ.get("HUB_SERVICE_URL", "http://hub:5000")
ACCOUNT_INFO_API_URL = os.environ.get("ACCOUNT_INFO_API_URL", "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")
PRODUCT_VALIDATION_URL = os.environ.get("PRODUCT_VALIDATION_URL", "http://placeholder/getHubInfo") # change when YH provides

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
    'hubID': fields.Integer(required=False, description='ID of the hub (optional)'),
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
            
            # Step 1: Retrieve volunteer phone number
            volunteer_info = self.get_volunteer_info(data['volunteerID'])
            if not volunteer_info:
                return {"error": "Could not retrieve volunteer information"}, 404
            
            # Step 2: Validate product and get hub information
            hub_info = self.validate_product(data['productID'])
            if not hub_info:
                return {"error": "Could not retrieve hub information for the product"}, 404
            
            # Prepare inventory update payload
            inventory_payload = {
                'hubID': hub_info['hubID'],
                'hubName': hub_info['hubName'],
                'hubAddress': hub_info['hubAddress'],
                'items': data.get('items', []),
                'newitems': data.get('newitems', [])
            }
            
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
            response = requests.post(
                PRODUCT_VALIDATION_URL, 
                json={"productID": product_id}
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error validating product: {e}")
            return None
    
    def create_notification_payload(self, delivery_data, volunteer_info, hub_info):
        """Create notification payload for AMQP"""
        return {
            "eventType": "delivery_confirmation",
            "volunteerName": volunteer_info.get('userName', 'Unknown Volunteer'),
            "volunteerPhone": volunteer_info.get('userPhoneNumber', 'N/A'),
            "hubName": hub_info['hubName'],
            "hubAddress": hub_info['hubAddress'],
            "items": delivery_data.get('items', []),
            "newitems": delivery_data.get('newitems', []),
            "timestamp": datetime.now().isoformat()
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
    app.run(host='0.0.0.0', port=5000, debug=True)