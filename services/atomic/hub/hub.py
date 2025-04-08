from flask import Flask, request, jsonify
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_restx import Api, Resource, Namespace, fields
from flask_cors import CORS
import threading
import time
from datetime import datetime
from amqp_lib import publish_message
import json
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
# initialise flask-restx api for documentation
api = Api(app, 
          version='1.0', 
          title='Hub Service API',
          description='API for managing food donation hubs and inventory',
          doc='/swagger')  # This specifies the Swagger UI URL

# Create two separate namespaces
public_hub_ns = Namespace('public/hub', description='Public Hub operations for UI')
internal_hub_ns = Namespace('internal/hub', description='Internal Hub operations for system integration')

# Add both namespaces to the API
api.add_namespace(public_hub_ns, path='/public/hub')
api.add_namespace(internal_hub_ns, path='/internal/hub')

# Initialize Supabase client
url = os.environ.get("HUB_SUPABASE_URL")
key = os.environ.get("HUB_SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Define models for Swagger documentation
# Item model
item_model = api.model('Item', {
    'itemID': fields.Integer(description='ID of the item'),
    'itemName': fields.String(description='Name of the item')
})

# Inventory item model
inventory_item_model = api.model('InventoryItem', {
    'itemName': fields.String(description='Name of the item'),
    'itemWeight_kg': fields.Float(description='Weight of the item in kilograms'),
    'quantity': fields.Integer(description='Quantity of the item')
})

# Hub model
hub_model = api.model('Hub', {
    'hubID': fields.Integer(description='ID of the hub'),
    'hubName': fields.String(description='Name of the hub'),
    'hubAddress': fields.String(description='Address of the hub'),
    'totalWeight_kg': fields.Float(description='Total weight of all items in the hub'),
    'items': fields.List(fields.Nested(inventory_item_model), description='List of items in the hub')
})

# Items response model
items_response_model = api.model('ItemsResponse', {
    'items': fields.List(fields.Nested(item_model), description='List of items')
})

# Success response model
success_model = api.model('SuccessResponse', {
    'message': fields.String(description='Success message'),
    'hubID': fields.String(description='ID of the hub that was updated')
})

# Existing item model for update inventory
existing_item_model = api.model('ExistingItem', {
    'itemName': fields.String(required=True, description='Name of the item'),
    'quantity': fields.Integer(required=True, description='Quantity of the item')
})

# New item model for update inventory
new_item_model = api.model('NewItem', {
    'itemName': fields.String(required=True, description='Name of the item'),
    'itemWeight_kg': fields.Float(required=True, description='Weight of the item in kilograms'),
    'quantity': fields.Integer(required=True, description='Quantity of the item'),
    'description': fields.String(description='Optional description of the item')
})

# Update inventory request model
update_inventory_model = api.model('UpdateInventoryRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub to update'),
    'items': fields.List(fields.Nested(existing_item_model), description='List of existing items to add'),
    'newitems': fields.List(fields.Nested(new_item_model), description='List of new items to add with weights')
})

# Reserved hub model
reserved_hub_model = api.model('ReservedHub', {
    'hubID': fields.Integer(description='ID of the hub'),
    'hubName': fields.String(description='Name of the hub'),
    'hubAddress': fields.String(description='Address of the hub'),
    'totalWeight_kg': fields.Float(description='Total weight of all items in the hub'),
    'reservationDate': fields.DateTime(description='Date and time of the reservation')
})

# Reserve hub request model
reserve_hub_model = api.model('ReserveHubRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub to reserve'),
    'foodbankID': fields.String(required=True, description='ID of the foodbank making the reservation')
})

# for hub-food bank validation
hub_foodbank_model = api.model('HubFoodbankRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub'),
    'foodbankID': fields.String(required=True, description='ID of the foodbank')
})

# to populate foodbank table
user_to_foodbank_model = api.model('UserToFoodbank', {
    'userId': fields.String(required=True, description='ID of the user (will be used as foodbankId)'),
    'userName': fields.String(required=True, description='Name of the user (will be used as foodbankName)'),
    'userEmail': fields.String(required=True, description='Email of the user'),
    'userPhoneNumber': fields.String(required=True, description='Phone number of the user'),
    'userAddress': fields.String(required=True, description='Address of the user (will be used as foodbankAddress)'),
    'userRole': fields.String(required=True, description='Role of the user (F for Foodbank)')
})

#define rabbitmq variables for publishing messages
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
EXCHANGE_NAME = "notificationsS3"
EXCHANGE_TYPE = "direct"

@internal_hub_ns.route('/allHubs')
class AllHubs(Resource):
    @public_hub_ns.doc('get_all_hubs', description='Retrieve basic information about all hubs')
    @public_hub_ns.response(200, 'Success')
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self):
        """
        Service to retrieve basic information for all hubs.
        
        This endpoint returns a simplified list of all hubs in the system,
        including just their ID, name, and address. This is useful for
        dropdowns and other UI elements that need to display hub options.
        """
        try:
            # Get all hubs
            hubs_response = supabase.table('hub').select('hubid, hubname, hubaddress').order('hubname').execute()
            
            if not hubs_response.data:
                return [], 200  # Return empty list if no hubs
            
            # Transform to camelCase for the response
            result = []
            for hub in hubs_response.data:
                result.append({
                    "hubID": hub['hubid'],
                    "hubName": hub['hubname'],
                    "hubAddress": hub['hubaddress']
                })
            
            return result, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# To populate item dropdown in Volunteer UI
@public_hub_ns.route('/existingItems')
class ExistingItems(Resource):
    @public_hub_ns.doc('get_existing_items')
    @public_hub_ns.response(200, 'Success', items_response_model)
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self):
        """
        Service to retrieve all available food items from the Weight table.
        
        This endpoint returns a list of all items in the Weight table, which can be used
        to populate dropdown menus in the UI. It includes the item ID and name for each item.
        
        The response is formatted with camelCase property names for frontend compatibility.
        """
        try:
            response = supabase.table('weight').select('itemid, itemname').order('itemname').execute()
            
            # Convert to camelCase for the response
            items = []
            for item in response.data:
                items.append({
                    "itemID": item['itemid'],
                    "itemName": item['itemname']
                })
            
            return {
                "items": items
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# To update inventory upon receiving drop-off
update_inventory_model = api.model('UpdateInventoryRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub to update'),
    'hubName': fields.String(required=True, description='Name of the hub'),
    'hubAddress': fields.String(required=True, description='Address of the hub'),
    'items': fields.List(fields.Nested(existing_item_model), description='List of existing items to add'),
    'newitems': fields.List(fields.Nested(new_item_model), description='List of new items to add with weights')
})

@internal_hub_ns.route('/updateInventory')
class UpdateInventory(Resource):
    @internal_hub_ns.doc('update_inventory')
    @internal_hub_ns.expect(update_inventory_model)
    @internal_hub_ns.response(200, 'Success', success_model)
    @internal_hub_ns.response(400, 'Bad Request')
    @internal_hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service to update hub inventory when volunteers drop off items.
        
        This endpoint handles adding both existing items (from the Weight table) and 
        new items that need to be created. For existing items, it looks up their weights
        automatically. For new items, it requires the weight to be provided and adds them
        to the Weight table for future reference.
        
        The endpoint will:
        1. Check if the hub exists, if not, create a new hub with the provided ID
        2. Update the hub name and address if they don't match
        3. Add or update inventory items for the hub
        
        If an item already exists in a hub's inventory, its quantity will be increased.
        Otherwise, a new inventory entry will be created.
        """
        try:
            data = request.json
            
            if not data or 'hubID' not in data or 'hubName' not in data or 'hubAddress' not in data:
                return {"error": "Invalid request data. Required fields: hubID, hubName, hubAddress"}, 400
            
            hub_id = data['hubID']
            hub_name = data['hubName']
            hub_address = data['hubAddress']
            
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                # Hub doesn't exist - create it with the provided ID
                print(f"Creating new hub with ID {hub_id}, name '{hub_name}', and address '{hub_address}'")
                hub_data = {
                    'hubid': hub_id,
                    'hubname': hub_name,
                    'hubaddress': hub_address,
                    'totalweight_kg': 0,  # Start with zero weight
                    'readytocollect': False,  # Not ready to collect initially
                    'reserved': False  # Not reserved initially
                }
                
                # Insert new hub with the provided ID
                hub_insert = supabase.table('hub').insert(hub_data).execute()
                
                if not hub_insert.data:
                    return {"error": f"Failed to create new hub with ID {hub_id}"}, 500
                
                print(f"Successfully created hub with ID {hub_id}")
            else:
                # Hub exists - check if name or address needs to be updated
                existing_hub = hub_response.data[0]
                update_fields = {}
                
                if existing_hub['hubname'] != hub_name:
                    print(f"Updating hub name from '{existing_hub['hubname']}' to '{hub_name}'")
                    update_fields['hubname'] = hub_name
                
                if existing_hub['hubaddress'] != hub_address:
                    print(f"Updating hub address from '{existing_hub['hubaddress']}' to '{hub_address}'")
                    update_fields['hubaddress'] = hub_address
                
                if update_fields:
                    supabase.table('hub').update(update_fields).eq('hubid', hub_id).execute()
            
            # Process existing items
            if 'items' in data and data['items']:
                for item in data['items']:
                    # Validate required fields
                    if 'itemName' not in item or 'quantity' not in item:
                        continue  # Skip invalid items
                    
                    # Find item in Weight table by name
                    weight_response = supabase.table('weight').select('*').ilike(
                        'itemname', item['itemName']).limit(1).execute()
                    
                    if not weight_response.data:
                        continue  # Skip if item not found in Weight table
                    
                    item_id = weight_response.data[0]['itemid']
                    item_weight = weight_response.data[0]['standardweight_kg']
                    
                    # Check if this item is already in inventory for this hub
                    inventory_check = supabase.table('inventory').select('*').eq(
                        'hubid', hub_id).eq('itemid', item_id).execute()
                    
                    if inventory_check.data:
                        # Item exists in inventory - update quantity (add)
                        current_quantity = inventory_check.data[0]['quantity']
                        new_quantity = current_quantity + item['quantity']
                        
                        supabase.table('inventory').update(
                            {'quantity': new_quantity}
                        ).eq('hubid', hub_id).eq('itemid', item_id).execute()
                    else:
                        # Item not in inventory - add it
                        supabase.table('inventory').insert({
                            'hubid': hub_id,
                            'itemid': item_id,
                            'quantity': item['quantity'],
                            'itemname': item['itemName'],
                            'itemweight_kg': item_weight
                        }).execute()
            
            # Process new items
            if 'newitems' in data and data['newitems']:
                for item in data['newitems']:
                    # Validate required fields
                    if 'itemName' not in item or 'quantity' not in item or 'itemWeight_kg' not in item:
                        continue  # Skip invalid items
                    
                    # First check if the item already exists in the Weight table
                    weight_check = supabase.table('weight').select('*').ilike(
                        'itemname', item['itemName']).limit(1).execute()
                    
                    if weight_check.data:
                        # Item already exists in Weight table, use it
                        item_id = weight_check.data[0]['itemid']
                        item_weight = weight_check.data[0]['standardweight_kg']
                    else:
                        # Add new item to Weight table
                        weight_data = {
                            'itemname': item['itemName'],
                            'standardweight_kg': item['itemWeight_kg'],
                            'description': item.get('description', f"Added via inventory update for hub {hub_id}")
                        }
                        weight_insert = supabase.table('weight').insert(weight_data).execute()
                        
                        if not weight_insert.data:
                            continue  # Skip if item creation failed
                        
                        item_id = weight_insert.data[0]['itemid']
                        item_weight = item['itemWeight_kg']
                    
                    # Check if this item is already in inventory for this hub
                    inventory_check = supabase.table('inventory').select('*').eq(
                        'hubid', hub_id).eq('itemid', item_id).execute()
                    
                    if inventory_check.data:
                        # Item exists in inventory - update quantity (add)
                        current_quantity = inventory_check.data[0]['quantity']
                        new_quantity = current_quantity + item['quantity']
                        
                        supabase.table('inventory').update(
                            {'quantity': new_quantity}
                        ).eq('hubid', hub_id).eq('itemid', item_id).execute()
                    else:
                        # Item not in inventory - add it
                        supabase.table('inventory').insert({
                            'hubid': hub_id,
                            'itemid': item_id,
                            'quantity': item['quantity'],
                            'itemname': item['itemName'],
                            'itemweight_kg': item_weight
                        }).execute()
            
            # After adding inventory, check total weight and update readytocollect flag if needed
            # This mimics the database trigger behavior in case it's not implemented in the database
            hub_total_weight = calculate_hub_total_weight(hub_id)
            
            # Update hub's total weight and readytocollect status
            update_data = {'totalweight_kg': hub_total_weight}
            if hub_total_weight >= 50:  # Assuming 50kg is the threshold for collection readiness
                update_data['readytocollect'] = True
            
            supabase.table('hub').update(update_data).eq('hubid', hub_id).execute()
            
            return {
                "message": "Inventory updated successfully.",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

def calculate_hub_total_weight(hub_id):
    """Calculate the total weight of all items in a hub's inventory."""
    try:
        # Get all inventory items for this hub
        inventory_response = supabase.table('inventory').select('quantity, itemweight_kg').eq('hubid', hub_id).execute()
        
        if not inventory_response.data:
            return 0
        
        # Calculate total weight
        total_weight = 0
        for item in inventory_response.data:
            item_weight = item['itemweight_kg']
            quantity = item['quantity']
            total_weight += item_weight * quantity
            
        return total_weight
    except Exception as e:
        print(f"Error calculating hub total weight: {str(e)}")
        return 0
    
# To populate Food Bank UI with non-reserved hubs information
@public_hub_ns.route('/hubsData')
class HubsData(Resource):
    @public_hub_ns.doc('get_hubs_data')
    @public_hub_ns.response(200, 'Success', [hub_model])
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self):
        """
        Service to retrieve data for all non-reserved hubs including their complete inventory.
        
        This endpoint returns comprehensive information about all hubs in the system
        that are NOT currently reserved, including their basic details (ID, name, address), 
        total weight of stored items, and a complete list of all inventory items with 
        their weights and quantities.
        
        Results are ordered by hub name and inventory items are formatted with camelCase
        property names for frontend compatibility.
        """
        try:
            # Get all hubs that are NOT reserved
            hubs_response = supabase.table('hub').select('*').eq('reserved', False).order('hubname').execute()
            
            if not hubs_response.data:
                return [], 200  # Return empty list if no hubs
            
            result = []
            
            for hub in hubs_response.data:
                # Get inventory for this hub
                inventory_response = supabase.table('inventory').select(
                    'itemname, itemweight_kg, quantity'
                ).eq('hubid', hub['hubid']).execute()
                
                # Transform to camelCase for the response
                items = []
                for item in inventory_response.data:
                    items.append({
                        "itemName": item['itemname'],
                        "itemWeight_kg": item['itemweight_kg'],
                        "quantity": item['quantity']
                    })
                
                # Format the response
                hub_data = {
                    'hubID': hub['hubid'],
                    'hubName': hub['hubname'],
                    'hubAddress': hub['hubaddress'],
                    'totalWeight_kg': hub['totalweight_kg'],
                    'items': items
                }
                
                result.append(hub_data)
            
            return result, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

@public_hub_ns.route('/<int:hub_id>/getInfo')
@public_hub_ns.param('hub_id', 'The ID of the hub to get information for')
class GetHubInfo(Resource):
    @public_hub_ns.doc('get_hub_info', description='Get detailed information about a specific hub including inventory')
    @public_hub_ns.response(200, 'Success', hub_model)
    @public_hub_ns.response(404, 'Hub Not Found')
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self, hub_id):
        """
        Service to retrieve detailed information about a specific hub.
        
        This endpoint returns comprehensive information about a specific hub,
        including its basic details (ID, name, address), total weight of stored items,
        and a complete list of all inventory items with their weights and quantities.
        
        Unlike the checkHub endpoint which returns basic status information,
        this endpoint provides the full hub data including inventory details.
        """
        try:
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            hub = hub_response.data[0]
            
            # Get inventory for this hub
            inventory_response = supabase.table('inventory').select(
                'itemname, itemweight_kg, quantity'
            ).eq('hubid', hub_id).execute()
            
            # Transform to camelCase for the response
            items = []
            for item in inventory_response.data:
                items.append({
                    "itemName": item['itemname'],
                    "itemWeight_kg": item['itemweight_kg'],
                    "quantity": item['quantity']
                })
            
            # Format the response
            hub_data = {
                'hubID': hub['hubid'],
                'hubName': hub['hubname'],
                'hubAddress': hub['hubaddress'],
                'totalWeight_kg': hub['totalweight_kg'],
                'isReserved': hub['reserved'],
                'readyToCollect': hub['readytocollect'],
                'items': items
            }
            
            return hub_data, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# Self-invoked by Hub service for broadcasting, >=50kg and not reserved
@internal_hub_ns.route('/readyHubsData')
class ReadyHubsData(Resource):
    @internal_hub_ns.doc('get_ready_hubs_data', description='Retrieve collection data for hubs that are ready to collect and not reserved')
    @internal_hub_ns.response(200, 'Success', [hub_model])
    @internal_hub_ns.response(500, 'Internal Server Error')
    def get(self):
        """
        Service to retrieve hubs that are ready for collection and not reserved.
        
        This endpoint specifically filters for hubs that:
        1. Are marked as readyToCollect = true
        2. Have a total weight >= 50kg (enforced by DB triggers)
        3. Are NOT currently reserved by any foodbank
        
        These are hubs that have enough food to be collected and are available for
        foodbanks to reserve. Returns the same format as hubsData but only for
        eligible hubs.
        """
        try:
            # Get all hubs that are ready for collection and not reserved
            hubs_response = supabase.table('hub').select('*')\
                .eq('readytocollect', True)\
                .eq('reserved', False)\
                .execute()
            
            if not hubs_response.data:
                return [], 200  # Return empty list if no hubs are ready
            
            result = []
            
            for hub in hubs_response.data:
                # Get inventory for this hub
                inventory_response = supabase.table('inventory').select(
                    'itemname, itemweight_kg, quantity'
                ).eq('hubid', hub['hubid']).execute()
                
                # Transform to camelCase for the response
                items = []
                for item in inventory_response.data:
                    items.append({
                        "itemName": item['itemname'],
                        "itemWeight_kg": item['itemweight_kg'],
                        "quantity": item['quantity']
                    })
                
                # Format the response
                hub_data = {
                    'hubID': hub['hubid'],
                    'hubName': hub['hubname'],
                    'hubAddress': hub['hubaddress'],
                    'totalWeight_kg': hub['totalweight_kg'],
                    'items': items
                }
                
                result.append(hub_data)
            
            return result, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# Called by reserveHub to check if hub exists and if its reserved (need to add functionality if unreserve is done)
@internal_hub_ns.route('/checkHub/<int:hub_id>')
@internal_hub_ns.param('hub_id', 'The ID of the hub to check')
class CheckHub(Resource):
    @internal_hub_ns.doc('check_hub', description='Check if a hub exists and whether it is reserved')
    @internal_hub_ns.response(200, 'Success')
    @internal_hub_ns.response(404, 'Hub Not Found')
    @internal_hub_ns.response(500, 'Internal Server Error')
    def get(self, hub_id):
        """
        Service to check if a hub exists and if it's reserved.
        
        This endpoint allows services to check a hub's status before attempting
        reservation. It returns the hub's basic info and reservation status.
        """
        try:
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            hub = hub_response.data[0]
            
            # Return hub information including reservation status
            return {
                "hubName": hub['hubname'],
                "hubAddress": hub['hubaddress'],
                "totalWeight_kg": hub['totalweight_kg'],
                "reserved": hub['reserved'],
                "readyToCollect": hub['readytocollect']
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500
   
@internal_hub_ns.route('/reserveHub')
class ReserveHub(Resource):
    @internal_hub_ns.doc('reserve_hub', description='Food Bank reserves Hub to collect from')
    @internal_hub_ns.expect(reserve_hub_model)
    @internal_hub_ns.response(200, 'Success', success_model)
    @internal_hub_ns.response(400, 'Bad Request')
    @internal_hub_ns.response(404, 'Hub Not Found')
    @internal_hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service for foodbanks to reserve a hub for collection.
        """
        try:
            data = request.json
            print(f"Received reservation request: {json.dumps(data)}")
            
            if not data or 'hubID' not in data or 'foodbankID' not in data:
                return {"error": "Invalid request data. Required fields: hubID, foodbankID"}, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            hub = hub_response.data[0]
            
            # Check if hub is already reserved
            if hub['reserved']:
                return {"error": f"Hub with ID {hub_id} is already reserved"}, 400
            
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', foodbank_id).execute()
            
            # Require foodbank to exist first
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist. Please create it first."}, 404
            
            # Get current inventory
            inventory_response = supabase.table('inventory').select('*').eq('hubid', hub_id).execute()
            
            if not inventory_response.data:
                return {"error": f"Hub with ID {hub_id} has no inventory to reserve"}, 400
            
            try:
                # 1. FIRST important step - Update hub's reserved status
                print(f"Setting hub {hub_id} reserved=TRUE")
                hub_update = supabase.table('hub').update({'reserved': True}).eq('hubid', hub_id).execute()
                print(f"Hub update response: {hub_update}")
                
                # 2. Create reservation record
                reservation_data = {
                    'foodbankId': foodbank_id,
                    'hubid': hub_id,
                    'totalweight_kg': hub['totalweight_kg']
                }
                print(f"Creating reservation with data: {json.dumps(reservation_data)}")
                reservation_response = supabase.table('foodbankreservation').insert(reservation_data).execute()
                
                if not reservation_response.data:
                    raise Exception("Failed to create reservation record")
                    
                reservation_id = reservation_response.data[0]['reservationid']
                print(f"Created reservation ID: {reservation_id}")
                
                # 3. Create snapshot of current inventory
                reserved_inventory = []
                for item in inventory_response.data:
                    reserved_inventory.append({
                        'reservationid': reservation_id,
                        'itemid': item['itemid'],
                        'hubid': hub_id,
                        'itemname': item['itemname'],
                        'quantity': item['quantity'],
                        'itemweight_kg': item['itemweight_kg']
                    })
                
                if reserved_inventory:
                    print(f"Creating {len(reserved_inventory)} reserved inventory items")
                    reserved_response = supabase.table('reservedinventory').insert(reserved_inventory).execute()
                    
                    if not reserved_response.data:
                        raise Exception("Failed to create inventory snapshot")
                
                # Double-check that hub is marked as reserved
                final_check = supabase.table('hub').select('reserved').eq('hubid', hub_id).execute()
                print(f"Final hub reserved status: {final_check.data[0]['reserved']}")
                
                if not final_check.data[0]['reserved']:
                    # One more attempt to set reserved flag
                    supabase.table('hub').update({'reserved': True}).eq('hubid', hub_id).execute()
                
                return {
                    "message": "Reserved successfully.",
                    "hubID": str(hub_id),
                    "reservationID": reservation_id,
                    "reservedWeight_kg": hub['totalweight_kg']
                }, 200
                
            except Exception as e:
                print(f"Error during reservation: {str(e)}")
                
                # Rollback - first delete reservedinventory entries if they exist
                if 'reservation_id' in locals():
                    print(f"Rolling back - deleting reserved inventory for reservation {reservation_id}")
                    supabase.table('reservedinventory').delete().eq('reservationid', reservation_id).execute()
                    
                    # Then delete the reservation
                    print(f"Rolling back - deleting reservation {reservation_id}")
                    supabase.table('foodbankreservation').delete().eq('reservationid', reservation_id).execute()
                
                # Do NOT change hub back to unreserved if reservation failed but hub was marked as reserved
                # This prevents race conditions where multiple requests could try to reserve the same hub
                
                raise e
                
        except Exception as e:
            error_msg = str(e)
            print(f"Reservation failed: {error_msg}")
            return {"error": error_msg}, 500   
# Called by reserveHub service to unreserve hub
@internal_hub_ns.route('/unreserveHub')
class UnreserveHub(Resource):
    def post(self):
        try:
            data = request.json
            
            if not data or 'hubID' not in data or 'foodbankID' not in data:
                return {"error": "Invalid request data. Required fields: hubID, foodbankID"}, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', foodbank_id).execute()

            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            # Check if this foodbank has a reservation for this hub
            reservation_response = supabase.table('foodbankreservation').select('*').eq(
                'foodbankId', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            if not reservation_response.data:
                return {"error": f"No active reservation found for Hub ID {hub_id} by Foodbank ID {foodbank_id}"}, 404
            
            # Get the reservation ID
            reservation_id = reservation_response.data[0]['reservationid']
            
            # FIRST, delete entries in reservedinventory
            supabase.table('reservedinventory').delete().eq('reservationid', reservation_id).execute()
            
            # THEN, update hub to unreserved status
            supabase.table('hub').update({'reserved': False}).eq('hubid', hub_id).execute()
            
            # FINALLY, delete the reservation
            supabase.table('foodbankreservation').delete().eq(
                'foodbankId', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            return {
                "message": "Unreserved successfully.",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# Called by Food Bank UI when collection is made
@public_hub_ns.route('/collectionComplete')
class CollectionComplete(Resource):
    @public_hub_ns.doc('collection_complete', description='Updates inventory on successful pickup by Food Bank')
    @public_hub_ns.expect(hub_foodbank_model)
    @public_hub_ns.response(200, 'Success')
    @public_hub_ns.response(400, 'Bad Request')
    @public_hub_ns.response(404, 'Not Found')
    @public_hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service to mark a hub as collected by a foodbank.
        
        This endpoint:
        1. Marks the reservation as completed
        2. Updates the inventory to remove the collected (reserved) items
        3. Keeps any new donations that came in after the reservation
        """
        try:
            data = request.json
            
            if not data or 'hubID' not in data or 'foodbankID' not in data:
                return {"error": "Invalid request data. Required fields: hubID, foodbankID"}, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            
            # Check for active reservation
            reservation_response = supabase.table('foodbankreservation').select('*').eq(
                'foodbankId', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            if not reservation_response.data:
                return {"error": f"No active reservation found for Hub ID {hub_id} by Foodbank ID {foodbank_id}"}, 404
            
            reservation = reservation_response.data[0]
            reservation_id = reservation['reservationid']
            reserved_weight = reservation['totalweight_kg']
            
            # Get the reserved inventory
            reserved_response = supabase.table('reservedinventory').select('*').eq(
                'reservationid', reservation_id).execute()
            
            # Process inventory changes based on what was collected
            # We need to update the existing inventory, removing the items that were collected
            
            # Start transaction (simulated)
            try:
                # 1. Mark the reservation as completed
                supabase.table('foodbankreservation').update(
                    {'collectioncompleted': True}
                ).eq('reservationid', reservation_id).execute()
                
                # 2. For each reserved item, subtract it from the current inventory
                for reserved_item in reserved_response.data:
                    item_id = reserved_item['itemid']
                    reserved_qty = reserved_item['quantity']
                    
                    # Check current inventory for this item
                    inventory_check = supabase.table('inventory').select('*').eq(
                        'hubid', hub_id).eq('itemid', item_id).execute()
                    
                    if inventory_check.data:
                        current_item = inventory_check.data[0]
                        current_qty = current_item['quantity']
                        
                        if current_qty <= reserved_qty:
                            # Item completely consumed, delete it
                            supabase.table('inventory').delete().eq(
                                'hubid', hub_id).eq('itemid', item_id).execute()
                        else:
                            # Partially consumed, update quantity
                            new_qty = current_qty - reserved_qty
                            supabase.table('inventory').update(
                                {'quantity': new_qty}
                            ).eq('hubid', hub_id).eq('itemid', item_id).execute()
                
                # 3. Delete reserved inventory entries
                supabase.table('reservedinventory').delete().eq('reservationid', reservation_id).execute()
                
                # 4. Update hub's weight and status
                # Recalculate from current inventory
                remaining_weight = calculate_hub_total_weight(hub_id)
                
                update_data = {
                    'reserved': False,
                    'totalweight_kg': remaining_weight
                }
                
                if remaining_weight >= 50:  # Still ready to collect
                    update_data['readytocollect'] = True
                else:
                    update_data['readytocollect'] = False
                
                supabase.table('hub').update(update_data).eq('hubid', hub_id).execute()
                
                return {
                    "message": "Collection completed successfully",
                    "hubID": str(hub_id),
                    "collectedWeight_kg": reserved_weight,
                    "remainingWeight_kg": remaining_weight
                }, 200
                
            except Exception as e:
                print(f"Collection completion failed: {str(e)}")
                return {"error": f"Failed to complete collection: {str(e)}"}, 500
                
        except Exception as e:
            return {"error": str(e)}, 500
        
@public_hub_ns.route('/<int:hub_id>/reservedInventory')
@public_hub_ns.param('hub_id', 'The ID of the hub to get reserved inventory for')
class HubReservedInventory(Resource):
    @public_hub_ns.doc('get_hub_reserved_inventory', description='Get detailed information about a hub\'s reserved inventory')
    @public_hub_ns.response(200, 'Success')
    @public_hub_ns.response(404, 'Hub Not Found or Not Reserved')
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self, hub_id):
        """
        Service to retrieve detailed information about a hub's reserved inventory.
        
        This endpoint returns the snapshot of inventory that was reserved for a hub, 
        including all items with their weights and quantities at the time of reservation.
        This helps foodbanks plan the appropriate vehicle size for collection.
        """
        try:
            # Check if hub exists
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            hub = hub_response.data[0]
            
            # Get active reservation for this hub
            reservation_response = supabase.table('foodbankreservation').select('*')\
                .eq('hubid', hub_id)\
                .eq('collectioncompleted', False)\
                .execute()
            
            if not reservation_response.data:
                return {"error": f"Hub with ID {hub_id} has no active reservation"}, 404
            
            reservation = reservation_response.data[0]
            reservation_id = reservation['reservationid']
            
            # Get the reserved inventory snapshot
            reserved_inventory_response = supabase.table('reservedinventory').select('*')\
                .eq('reservationid', reservation_id)\
                .execute()
            
            # Format the response with reserved inventory items
            reserved_items = []
            total_weight = 0
            
            for item in reserved_inventory_response.data:
                item_total_weight = item['itemweight_kg'] * item['quantity']
                total_weight += item_total_weight
                
                reserved_items.append({
                    "itemName": item['itemname'],
                    "itemWeight_kg": item['itemweight_kg'],
                    "quantity": item['quantity'],
                    "totalItemWeight_kg": item_total_weight
                })
            
            # Prepare response with hub info and reserved inventory
            response = {
                "hubID": hub_id,
                "hubName": hub['hubname'],
                "hubAddress": hub['hubaddress'],
                "foodbankID": reservation['foodbankId'],
                "reservationID": reservation_id,
                "reservationDate": reservation['reservationdate'],
                "totalWeight_kg": reservation['totalweight_kg'] or total_weight,
                "reservedItems": reserved_items
            }
            
            return response, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

@internal_hub_ns.route('/foodbank/<string:foodbank_id>')
@internal_hub_ns.param('foodbank_id', 'The ID of the foodbank to get information for')
class GetFoodbankInfo(Resource):
    @internal_hub_ns.doc('get_foodbank_info', description='Get foodbank information and its reserved hubs')
    @internal_hub_ns.response(200, 'Success')
    @internal_hub_ns.response(404, 'Foodbank Not Found')
    @internal_hub_ns.response(500, 'Internal Server Error')
    def get(self, foodbank_id):
        """
        Service to retrieve foodbank information and its reserved hubs.
        
        This endpoint returns:
        1. Foodbank details (ID, name, address)
        2. A list of hubs that are currently reserved by this foodbank (ID, name, address)
        
        This can be used to display the foodbank profile along with its active reservations.
        """
        try:
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', foodbank_id).execute()
            
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            foodbank = foodbank_response.data[0]
            
            # Get all active reservations for this foodbank
            reservations_response = supabase.table('foodbankreservation').select('*')\
                .eq('foodbankId', foodbank_id)\
                .eq('collectioncompleted', False)\
                .execute()
            
            # Prepare the list of reserved hubs
            reserved_hubs = []
            
            if reservations_response.data:
                # Get hub details for each reservation
                for reservation in reservations_response.data:
                    hub_id = reservation['hubid']
                    
                    # Get hub details
                    hub_response = supabase.table('hub').select('hubid, hubname, hubaddress')\
                        .eq('hubid', hub_id)\
                        .execute()
                    
                    if hub_response.data:
                        hub = hub_response.data[0]
                        
                        # Add to reserved hubs list
                        reserved_hubs.append({
                            "hubID": hub['hubid'],
                            "hubName": hub['hubname'],
                            "hubAddress": hub['hubaddress'],
                            "reservationDate": reservation['reservationdate'],
                            "totalWeight_kg": reservation['totalweight_kg']
                        })
            
            # Format the response with correct camelCase column names
            response = {
                "foodbankID": foodbank['foodbankId'],
                "foodbankName": foodbank['foodbankName'],
                "foodbankAddress": foodbank['foodbankAddress'],
                "reservedHubs": reserved_hubs
            }
            
            return response, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

# Alternative endpoint to get all reservations for a specific foodbank with their reserved inventory
# this is to populate the modal for reserved food banks
@public_hub_ns.route('/reservedInventories/<string:foodbank_id>')
@public_hub_ns.param('foodbank_id', 'The ID of the foodbank')
class FoodbankReservedInventories(Resource):
    @public_hub_ns.doc('get_foodbank_reserved_inventories', 
                    description='Retrieve all reserved inventories for hubs reserved by a specific foodbank')
    @public_hub_ns.response(200, 'Success')
    @public_hub_ns.response(404, 'Foodbank Not Found')
    @public_hub_ns.response(500, 'Internal Server Error')
    def get(self, foodbank_id):
        """
        Service to retrieve all reserved inventories for a specific foodbank.
        
        This endpoint returns comprehensive information about all hubs that have been 
        reserved by the specified foodbank, including their complete reserved inventory.
        This is used to populate the 'My Reservations' page in the foodbank UI.
        """
        try:
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', foodbank_id).execute()
            
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            # Get all active reservations for this foodbank
            reservations_response = supabase.table('foodbankreservation').select('*')\
                .eq('foodbankId', foodbank_id)\
                .eq('collectioncompleted', False)\
                .execute()
            
            if not reservations_response.data:
                return [], 200  # Return empty list if no reservations
            
            # Prepare response with all reserved hubs and their inventories
            reserved_hubs = []
            
            for reservation in reservations_response.data:
                hub_id = reservation['hubid']
                reservation_id = reservation['reservationid']
                
                # Get hub details
                hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
                
                if not hub_response.data:
                    continue  # Skip if hub not found (unlikely scenario)
                
                hub = hub_response.data[0]
                
                # Get reserved inventory for this reservation
                reserved_inventory_response = supabase.table('reservedinventory').select('*')\
                    .eq('reservationid', reservation_id)\
                    .execute()
                
                # Format the reserved inventory items
                reserved_items = []
                
                for item in reserved_inventory_response.data:
                    reserved_items.append({
                        "itemName": item['itemname'],
                        "itemWeight_kg": item['itemweight_kg'],
                        "quantity": item['quantity'],
                        "totalItemWeight_kg": item['itemweight_kg'] * item['quantity']
                    })
                
                # Add this hub and its reserved inventory to the response
                reserved_hubs.append({
                    "hubID": hub_id,
                    "hubName": hub['hubname'],
                    "hubAddress": hub['hubaddress'],
                    "reservationID": reservation_id,
                    "reservationDate": reservation['reservationdate'],
                    "totalWeight_kg": reservation['totalweight_kg'],
                    "reservedItems": reserved_items
                })
            
            return reserved_hubs, 200
            
        except Exception as e:
            return {"error": str(e)}, 500

@public_hub_ns.route('/createFoodbank')
class CreateFoodbank(Resource):
    @public_hub_ns.doc('create_foodbank_from_user', description='Create a foodbank entry from user information')
    @public_hub_ns.expect(user_to_foodbank_model)
    @public_hub_ns.response(201, 'Created Successfully')
    @public_hub_ns.response(400, 'Bad Request')
    @public_hub_ns.response(409, 'Foodbank Already Exists')
    @public_hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service to create a foodbank entry from user information.
        
        This endpoint accepts user information and converts it to the foodbank table format.
        It will:
        1. Check if a foodbank with the given ID already exists
        2. If not, it will create a new foodbank entry with the provided information
        3. If it exists, it will return a conflict response
        """
        try:
            data = request.json
            
            # Validate required fields
            required_fields = ['userId', 'userName', 'userEmail', 'userPhoneNumber', 'userAddress', 'userRole']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            # Check if the userRole is 'F' (Foodbank)
            if data['userRole'] != 'F':
                return {"error": "User role must be 'F' to create a foodbank"}, 400
            
            # Check if foodbank already exists
            foodbank_id = data['userId']
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankId', foodbank_id).execute()
            
            if foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} already exists"}, 409
            
            # Convert user data to foodbank format with camelCase column names
            foodbank_data = {
                'foodbankId': data['userId'],
                'foodbankName': data['userName'],
                'foodbankAddress': data['userAddress'],
                'foodbankEmail': data['userEmail'],
                'foodbankPhoneNumber': data['userPhoneNumber'],
                'foodbankRole': data['userRole']
            }
            
            # Insert foodbank record
            insert_response = supabase.table('foodbank').insert(foodbank_data).execute()
            
            if not insert_response.data:
                return {"error": "Failed to create foodbank record"}, 500
            
            return {
                "message": "Foodbank created successfully",
                "foodbankID": foodbank_id,
                "foodbankName": data['userName']
            }, 201
        
        except Exception as e:
            return {"error": str(e)}, 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)