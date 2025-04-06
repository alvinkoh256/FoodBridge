from flask import Flask, request, jsonify
import os
from flask_cors import CORS
import requests
import json
from flask_restx import Api, Resource, Namespace, fields

# Initialize Flask app
app = Flask(__name__)

CORS(app)

# Initialize Flask-RESTX API
api = Api(app, version='1.0', 
          title='Reserve Hub Service API',
          description='A composite microservice for coordinating hub reservations by food banks',
          doc='/swagger')

# Environment variables with Docker-friendly defaults
HUB_SERVICE_URL = os.environ.get("HUB_SERVICE_URL", "http://hub:5010")
ACCOUNT_INFO_API_URL = os.environ.get("ACCOUNT_INFO_API_URL", "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")

# Create namespace
ns = api.namespace('reserveHub', description='Reserve Hub operations')

# Define models for request validation
reserve_hub_request_model = api.model('ReserveHubRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub to reserve'),
    'foodbankID': fields.String(required=True, description='ID of the foodbank making the reservation')
})

reserve_hub_response_model = api.model('ReserveHubResponse', {
    'message': fields.String(description='Status message'),
    'hubReserved': fields.Boolean(description='Whether the hub was successfully reserved'),
    'hubServiceError': fields.String(description='Error message from hub service if any'),
    'accountServiceError': fields.String(description='Error message from account service if any')
})

# Common helper methods
def get_foodbank_info(foodbank_id):
    """Retrieve foodbank information from Account Info API"""
    try:
        print(f"Fetching foodbank info for ID: {foodbank_id}")
        
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
        session.mount('https://', adapter)
        
        # Make request to Account Info API user endpoint
        url = f"{ACCOUNT_INFO_API_URL}/user/{foodbank_id}"
        print(f"Calling URL: {url}")
        
        response = session.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Account Info API error: {response.status_code} - {response.text}")
            return None
        
        # Parse the response data
        user_data = response.json()
        print(f"Retrieved user info: {json.dumps(user_data)}")
        
        # Handle both cases - either a single user object or a list of users
        user = None
        if isinstance(user_data, list):
            # If response is a list, get the first user
            if not user_data:
                print(f"No user found for ID {foodbank_id}")
                return None
            user = user_data[0]
        else:
            # If response is a single object, use it directly
            user = user_data
        
        # Check if the user is a foodbank (role F)
        if user.get('userRole') != 'F':
            print(f"User with ID {foodbank_id} is not a foodbank (role: {user.get('userRole')})")
            return None
        
        return user
        
    except Exception as e:
        print(f"Error retrieving foodbank info: {str(e)}")
        return None

def reserve_hub_in_service(reserve_payload):
    """Reserve the hub in the Hub Service"""
    try:
        print(f"Reserving hub: {json.dumps(reserve_payload)}")
        
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
        
        # Make request to Hub Service
        response = session.post(
            f"{HUB_SERVICE_URL}/internal/hub/reserveHub",
            json=reserve_payload,
            timeout=10
        )
        
        print(f"Hub Service response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Hub Service error: {response.text}")
            return {"success": False, "error": response.text}
        
        return {"success": True, "data": response.json()}
        
    except Exception as e:
        print(f"Error reserving hub: {str(e)}")
        return {"success": False, "error": str(e)}

def unreserve_hub_in_service(unreserve_payload):
    """Unreserve the hub in the Hub Service"""
    try:
        print(f"Unreserving hub: {json.dumps(unreserve_payload)}")
        
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
        
        # Make request to Hub Service
        response = session.post(
            f"{HUB_SERVICE_URL}/internal/hub/unreserveHub",
            json=unreserve_payload,
            timeout=10
        )
        
        print(f"Hub Service unreserve response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Hub Service unreserve error: {response.text}")
            return {"success": False, "error": response.text}
        
        return {"success": True, "data": response.json()}
        
    except Exception as e:
        print(f"Error unreserving hub: {str(e)}")
        return {"success": False, "error": str(e)}

@ns.route('/reserve')
class ReserveHub(Resource):
    @ns.doc('reserve_hub')
    @ns.expect(reserve_hub_request_model)
    @ns.response(200, 'Success', reserve_hub_response_model)
    @ns.response(400, 'Validation Error')
    @ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Handle hub reservation request from foodbank UI
        
        Workflow:
        1. Validate foodbank ID via Account Info Service
        2. Reserve hub directly with foodbank ID
        """
        try:
            # Get request data
            data = request.json
            print(f"Received hub reservation request: {json.dumps(data)}")
            
            # Validate required fields
            if not data or 'hubID' not in data or 'foodbankID' not in data:
                return {
                    "message": "Invalid request data. Required fields: hubID, foodbankID",
                    "hubReserved": False
                }, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            
            # Step 1: Validate foodbank
            foodbank_info = get_foodbank_info(foodbank_id)
            
            if not foodbank_info:
                return {
                    "message": f"Invalid foodbank ID or account service error",
                    "hubReserved": False,
                    "accountServiceError": "Foodbank not found or validation failed"
                }, 400
            
            # Step 2: Reserve the hub (hub service will handle all validation and reservation logic)
            reserve_payload = {
                "hubID": hub_id,
                "foodbankID": foodbank_id
            }
            
            # Reserve the hub
            reserve_result = reserve_hub_in_service(reserve_payload)
            
            # Process hub service response
            if reserve_result.get('success', False):
                # Extract data from successful response
                response_data = reserve_result.get('data', {})
                reservation_id = response_data.get('reservationID', '')
                reserved_weight = response_data.get('reservedWeight_kg', 0)
                
                return {
                    "message": "Hub reserved successfully",
                    "hubReserved": True,
                    "reservationID": reservation_id,
                    "reservedWeight_kg": reserved_weight
                }, 200
            else:
                # Handle specific error cases from the hub service
                error_msg = reserve_result.get('error', 'Unknown error')
                status_code = 500
                
                # Check for known error conditions
                if "already reserved" in error_msg:
                    status_code = 400
                elif "does not exist" in error_msg:
                    status_code = 404
                
                return {
                    "message": f"Failed to reserve hub: {error_msg}",
                    "hubReserved": False,
                    "hubServiceError": error_msg
                }, status_code
        
        except Exception as e:
            print(f"Error processing hub reservation: {str(e)}")
            return {
                "message": f"Error processing hub reservation: {str(e)}",
                "hubReserved": False
            }, 500

@ns.route('/unreserve')
class UnreserveHub(Resource):
    @ns.doc('unreserve_hub')
    @ns.expect(reserve_hub_request_model)
    @ns.response(200, 'Success', reserve_hub_response_model)
    @ns.response(400, 'Validation Error')
    @ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Handle hub unreservation request from foodbank UI
        
        Workflow:
        1. Validate foodbank ID via Account Info Service
        2. Unreserve hub
        """
        try:
            # Get request data
            data = request.json
            print(f"Received hub unreservation request: {json.dumps(data)}")
            
            # Validate required fields
            if not data or 'hubID' not in data or 'foodbankID' not in data:
                return {
                    "message": "Invalid request data. Required fields: hubID, foodbankID",
                    "hubReserved": True
                }, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            
            # Step 1: Validate foodbank
            foodbank_info = get_foodbank_info(foodbank_id)
            
            if not foodbank_info:
                return {
                    "message": f"Invalid foodbank ID or account service error",
                    "hubReserved": True,
                    "accountServiceError": "Foodbank not found or validation failed"
                }, 400
            
            # Step 2: Unreserve the hub (hub service will handle all validation and unreserve logic)
            unreserve_result = unreserve_hub_in_service({
                "hubID": hub_id,
                "foodbankID": foodbank_id
            })
            
            # Process hub service response
            if unreserve_result.get('success', False):
                return {
                    "message": "Hub unreserved successfully",
                    "hubReserved": False
                }, 200
            else:
                # Handle specific error cases from the hub service
                error_msg = unreserve_result.get('error', 'Unknown error')
                status_code = 500
                
                # Check for known error conditions
                if "does not exist" in error_msg:
                    status_code = 404
                elif "No active reservation found" in error_msg:
                    return {
                        "message": f"No active reservation found for this hub and foodbank",
                        "hubReserved": False,
                        "hubServiceError": error_msg
                    }, 400
                
                return {
                    "message": f"Failed to unreserve hub: {error_msg}",
                    "hubReserved": True,
                    "hubServiceError": error_msg
                }, status_code
        
        except Exception as e:
            print(f"Error processing hub unreservation: {str(e)}")
            return {
                "message": f"Error processing hub unreservation: {str(e)}",
                "hubReserved": True
            }, 500
        
if __name__ == '__main__':
    print(f"Starting Reserve Hub Service")
    app.run(host='0.0.0.0', port=5015, debug=True)