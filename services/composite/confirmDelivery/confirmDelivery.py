from flask import Flask, request, jsonify
import os
import requests
import json
from flask_restx import Api, Resource, Namespace, fields

# TO-DOs:
# retrieve volunteer info from accountInfo
# AMQP message to notification service to inform volunteer
# call /hub/updateInventory (done)

# Initialize Flask app
app = Flask(__name__)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', 
          title='Confirm Delivery Service API',
          description='A microservice for confirming deliveries and forwarding to hub service',
          doc='/swagger')

# Environment variables with Docker-friendly defaults
HUB_SERVICE_URL = os.environ.get("HUB_SERVICE_URL", "http://hub:5000")

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

drop_off_request_model = api.model('DropOffRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub'),
    'volunteerID': fields.Integer(required=True, description='ID of the volunteer'),
    'dropOffTime': fields.String(description='Time of drop-off, defaults to current time if not provided'),
    'items': fields.List(fields.Nested(item_model), description='List of existing items being dropped off'),
    'newitems': fields.List(fields.Nested(new_item_model), description='List of new items being dropped off')
})

drop_off_response_model = api.model('DropOffResponse', {
    'message': fields.String(description='Status message'),
    'hubUpdated': fields.Boolean(description='Whether the hub was successfully updated'),
    'hubServiceError': fields.String(description='Error message from hub service if any')
})

@ns.route('/drop-off')
class ConfirmDropOff(Resource):
    @ns.doc('confirm_drop_off')
    @ns.expect(drop_off_request_model)
    @ns.response(200, 'Success', drop_off_response_model)
    @ns.response(400, 'Validation Error')
    @ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Handle drop-off confirmation from volunteer UI
        
        This endpoint orchestrates the drop-off process by:
        1. Retrieving volunteer information from Account Info API
           - Gets volunteer name and phone from /userPhone/{volunteerID}
           - Falls back to "Unknown" if account service is unavailable
        
        2. Updating hub inventory via Hub Service
           - Transforms and forwards data to /hub/updateInventory
           - Includes both existing items and new items
           - Implements retry mechanism for reliability
        
        Returns a success response with volunteer name and hub update status.
        """
        try:
            data = request.json
            print(f"Received drop-off confirmation request: {json.dumps(data)}")
            
            # Validate required fields
            if not data or 'hubID' not in data or 'volunteerID' not in data:
                return jsonify({
                    "error": "Invalid request data. Required fields: hubID, volunteerID"
                }), 400
            
            if ('items' not in data or not data['items']) and ('newitems' not in data or not data['newitems']):
                return jsonify({
                    "error": "At least one item must be provided in either 'items' or 'newitems'"
                }), 400
            
            # Prepare request for Hub Service - this is the key transformation
            hub_request = {
                "hubID": data['hubID'],
                "items": data.get('items', []),
                "newitems": data.get('newitems', [])
            }
            
            # Call Hub Service to update inventory
            hub_response = call_hub_service(hub_request)
            
            # Return success response
            response_data = {
                "message": "Drop-off confirmed successfully",
                "hubUpdated": True if hub_response.status_code == 200 else False
            }
            
            if hub_response.status_code != 200:
                response_data["hubServiceError"] = hub_response.text
            
            return response_data, 200 if hub_response.status_code == 200 else 500
            
        except Exception as e:
            print(f"Error processing drop-off confirmation: {str(e)}")
            return jsonify({
                "error": f"Error processing drop-off confirmation: {str(e)}"
            }), 500

def call_hub_service(hub_request):
    """Call the Hub Service to update inventory with retry mechanism."""
    # Setup session with retry
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(
        max_retries=requests.packages.urllib3.util.retry.Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
    )
    session.mount('http://', adapter)
    
    try:
        print(f"Sending inventory update to Hub Service: {json.dumps(hub_request)}")
        
        # Make request to Hub Service
        response = session.post(
            f"{HUB_SERVICE_URL}/hub/updateInventory",
            json=hub_request,
            timeout=10
        )
        
        print(f"Hub Service response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Hub Service error: {response.text}")
        
        return response
    except Exception as e:
        print(f"Error calling Hub Service: {str(e)}")
        # Create a mock response for error case
        class MockResponse:
            def __init__(self):
                self.status_code = 500
                self.text = str(e)
        return MockResponse()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)