from flask import Flask, request, jsonify
import os
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_restx import Api, Resource, Namespace, fields
from datetime import datetime
from amqp_lib import publish_message

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
# initialise flask-restx api for documentation
api = Api(app, 
          version='1.0', 
          title='Hub Service API',
          description='API for managing food donation hubs and inventory',
          doc='/swagger')  # This specifies the Swagger UI URL

# create namespace
hub_ns = Namespace('hub', description='Hub operations')
api.add_namespace(hub_ns, path='/hub')

# Initialize Supabase client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
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
    'foodbankID': fields.Integer(required=True, description='ID of the foodbank making the reservation'),
    'foodbankName': fields.String(required=True, description='Name of the foodbank'),
    'foodbankAddress': fields.String(required=True, description='Address of the foodbank')
})

# for hub-food bank validation
hub_foodbank_model = api.model('HubFoodbankRequest', {
    'hubID': fields.Integer(required=True, description='ID of the hub'),
    'foodbankID': fields.Integer(required=True, description='ID of the foodbank')
})

#define rabbitmq variables for publishing messages
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
EXCHANGE_NAME = "foodbridge"
EXCHANGE_TYPE = "topic"
ROUTING_KEY_RESERVE = "hub.reservation.update"

def publish_hub_reservation_event(hub_id, hub_name, foodbank_id, foodbank_name, action):
    """Publish a message when a hub reservation status changes"""
    try:
        # Create message
        message = {
            "hubID": hub_id,
            "hubName": hub_name,
            "foodbankID": foodbank_id,
            "foodbankName": foodbank_name,
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        # Publish message
        publish_message(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT, 
            exchange_name=EXCHANGE_NAME,
            exchange_type=EXCHANGE_TYPE,
            routing_key=ROUTING_KEY_RESERVE,
            message=message
        )
        
        # Log success
        logger.info("MESSAGE PUBLISHED SUCCESSFULLY")
        print("*** MESSAGE PUBLISHED SUCCESSFULLY ***\n\n")
        return True
    except Exception as e:
        # Log failure with detailed error
        error_msg = f"Failed to publish {action} event: {str(e)}"
        print(f"*** ERROR: {error_msg} ***")
        return False

@hub_ns.route('/updateInventory')
class UpdateInventory(Resource):
    @hub_ns.doc('update_inventory')
    @hub_ns.expect(update_inventory_model)
    @hub_ns.response(200, 'Success', success_model)
    @hub_ns.response(400, 'Bad Request')
    @hub_ns.response(404, 'Hub Not Found')
    @hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
            Service to update hub inventory when volunteers drop off items.
            
            This endpoint handles adding both existing items (from the Weight table) and 
            new items that need to be created. For existing items, it looks up their weights
            automatically. For new items, it requires the weight to be provided and adds them
            to the Weight table for future reference.
            
            If an item already exists in a hub's inventory, its quantity will be increased.
            Otherwise, a new inventory entry will be created.
            """
        try:
            data = request.json
            
            if not data or 'hubID' not in data:
                return {"error": "Invalid request data. Required field: hubID"}, 400
            
            hub_id = data['hubID']
            
            # Check if hub exists
            hub_response = supabase.table('hub').select('hubid').eq('hubid', hub_id).execute()
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
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
            
            return {
                "message": "Inventory updated successfully.",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

@hub_ns.route('/existingItems')
class ExistingItems(Resource):
    @hub_ns.doc('get_existing_items')
    @hub_ns.response(200, 'Success', items_response_model)
    @hub_ns.response(500, 'Internal Server Error')
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

@hub_ns.route('/hubsData')
class HubsData(Resource):
    @hub_ns.doc('get_hubs_data')
    @hub_ns.response(200, 'Success', [hub_model])
    @hub_ns.response(500, 'Internal Server Error')
    def get(self):
        """
        Service to retrieve data for all hubs including their complete inventory.
        
        This endpoint returns comprehensive information about all hubs in the system,
        including their basic details (ID, name, address), total weight of stored items,
        and a complete list of all inventory items with their weights and quantities.
        
        Results are ordered by hub name and inventory items are formatted with camelCase
        property names for frontend compatibility.
        """
        try:
            # Get all hubs
            hubs_response = supabase.table('hub').select('*').order('hubname').execute()
            
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

    
@hub_ns.route('/readyHubsData')
class ReadyHubsData(Resource):
    @hub_ns.doc('get_ready_hubs_data', description='Retrieve collection data for hubs that are ready to collect and not reserved')
    @hub_ns.response(200, 'Success', [hub_model])
    @hub_ns.response(500, 'Internal Server Error')
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

@hub_ns.route('/reserveHub')
class ReserveHub(Resource):
    @hub_ns.doc('reserve_hub', description='Food Bank reserves Hub to collect from')
    @hub_ns.expect(reserve_hub_model)
    @hub_ns.response(200, 'Success', success_model)
    @hub_ns.response(400, 'Bad Request')
    @hub_ns.response(404, 'Hub Not Found')
    @hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service for foodbanks to reserve a hub for collection.
        
        This endpoint handles the reservation process when a foodbank wants to collect
        from a hub. It validates that the hub exists and is not already reserved, creates
        a foodbank record if it doesn't exist, and marks the hub as reserved.
        
        Additionally, it publishes a reservation event to RabbitMQ for other services
        (like the routing service) to be notified of the reservation.
        
        The database triggers will automatically mark all inventory items as reserved.
        """
        try:
            data = request.json
            
            if not data or 'hubID' not in data or 'foodbankID' not in data or 'foodbankName' not in data or 'foodbankAddress' not in data:
                return {"error": "Invalid request data. Required fields: hubID, foodbankID, foodbankName, foodbankAddress"}, 400
            
            hub_id = data['hubID']
            foodbank_id = data['foodbankID']
            foodbank_name = data['foodbankName']
            foodbank_address = data['foodbankAddress']
            
            # Check if hub exists and is not already reserved
            hub_response = supabase.table('hub').select('*').eq('hubid', hub_id).execute()
            
            if not hub_response.data:
                return {"error": f"Hub with ID {hub_id} does not exist"}, 404
            
            hub = hub_response.data[0]
            hub_name = hub['hubname']
            
            if hub['reserved']:
                return {"error": f"Hub with ID {hub_id} is already reserved"}, 400
            
            # Check if foodbank exists, create if not
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankid', foodbank_id).execute()
            
            if not foodbank_response.data:
                # Create new foodbank
                supabase.table('foodbank').insert({
                    'foodbankid': foodbank_id,
                    'foodbankname': foodbank_name,
                    'foodbankaddress': foodbank_address
                }).execute()
            
            # Update hub to reserved status
            supabase.table('hub').update({'reserved': True}).eq('hubid', hub_id).execute()
            
            # Create reservation record
            supabase.table('foodbankreservation').insert({
                'foodbankid': foodbank_id,
                'hubid': hub_id
            }).execute()
            
            # Publish reservation event
            publish_hub_reservation_event(
                hub_id=hub_id,
                hub_name=hub_name,
                foodbank_id=foodbank_id,
                foodbank_name=foodbank_name,
                action="reserve"
            )
            
            return {
                "message": "Reserved successfully.",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

# Create a foodbank namespace if you don't have one yet
foodbank_ns = Namespace('foodbank', description='Foodbank operations')
api.add_namespace(foodbank_ns, path='/foodbank')

@foodbank_ns.route('/<int:foodbank_id>/reservedHubs')
@foodbank_ns.param('foodbank_id', 'The ID of the foodbank')
class FoodbankReservedHubs(Resource):
    @foodbank_ns.doc('get_foodbank_reserved_hubs', 
                   description='Retrieve all hubs that have been reserved by a specific foodbank')
    @foodbank_ns.response(200, 'Success', [reserved_hub_model])
    @foodbank_ns.response(404, 'Foodbank Not Found')
    @foodbank_ns.response(500, 'Internal Server Error')
    def get(self, foodbank_id):
        """
        Service to retrieve all hubs reserved by a specific foodbank.
        
        This endpoint returns information about all hubs that have been reserved by
        the specified foodbank and haven't been collected yet. It includes hub details
        and reservation dates.
        
        The implementation first attempts to use a SQL join via RPC for efficiency,
        and falls back to multiple separate queries if that's not available.
        """
        try:
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankid', foodbank_id).execute()
            
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            # Get all reservations for this foodbank
            query = """
            SELECT 
                r.reservationid,
                r.reservationdate,
                h.hubid,
                h.hubname,
                h.hubaddress,
                h.totalweight_kg
            FROM 
                foodbankreservation r
            JOIN 
                hub h ON r.hubid = h.hubid
            WHERE 
                r.foodbankid = {0}
                AND r.collectioncompleted = false
            ORDER BY 
                r.reservationdate DESC
            """.format(foodbank_id)
            
            try:
                reserved_hubs_response = supabase.rpc('postgrest_sql', {"query": query}).execute()
                
                # Transform to camelCase for the response
                result = []
                for hub in reserved_hubs_response.data:
                    result.append({
                        'hubID': hub['hubid'],
                        'hubName': hub['hubname'],
                        'hubAddress': hub['hubaddress'],
                        'totalWeight_kg': hub['totalweight_kg'],
                        'reservationDate': hub['reservationdate']
                    })
                
                return result, 200
                
            except Exception:
                # If RPC fails, fall back to join via Python
                reservations_response = supabase.table('foodbankreservation').select('*').eq('foodbankid', foodbank_id).eq('collectioncompleted', False).execute()
                
                result = []
                for reservation in reservations_response.data:
                    hub_response = supabase.table('hub').select('*').eq('hubid', reservation['hubid']).execute()
                    if hub_response.data:
                        hub = hub_response.data[0]
                        result.append({
                            'hubID': hub['hubid'],
                            'hubName': hub['hubname'],
                            'hubAddress': hub['hubaddress'],
                            'totalWeight_kg': hub['totalweight_kg'],
                            'reservationDate': reservation['reservationdate']
                        })
                
                return result, 200
        
        except Exception as e:
            return {"error": str(e)}, 500
        
@hub_ns.route('/unreserveHub')
class UnreserveHub(Resource):
    @hub_ns.doc('unreserve_hub', description='Food Bank unreserves Hub')
    @hub_ns.expect(hub_foodbank_model)
    @hub_ns.response(200, 'Success', success_model)
    @hub_ns.response(400, 'Bad Request')
    @hub_ns.response(404, 'Not Found')
    @hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service for foodbanks to cancel a hub reservation.
        
        This endpoint handles the process when a foodbank wants to unreserve a previously
        reserved hub. It validates that the hub exists, the foodbank exists, and there
        is an active reservation for this combination.
        
        Upon successful unreservation, it publishes an event to RabbitMQ to notify
        other services of the change in reservation status.
        
        The database triggers will automatically mark all inventory items as unreserved.
        """
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
            
            hub_name = hub_response.data[0]['hubname']
            
            # Check if foodbank exists
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankid', foodbank_id).execute()
            
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            foodbank_name = foodbank_response.data[0]['foodbankname']
            
            # Check if this foodbank has a reservation for this hub
            reservation_response = supabase.table('foodbankreservation').select('*').eq(
                'foodbankid', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            if not reservation_response.data:
                return {"error": f"No active reservation found for Hub ID {hub_id} by Foodbank ID {foodbank_id}"}, 404
            
            # Update hub to unreserved status
            supabase.table('hub').update({'reserved': False}).eq('hubid', hub_id).execute()
            
            # Delete the reservation
            supabase.table('foodbankreservation').delete().eq(
                'foodbankid', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            # Publish unreservation event
            publish_hub_reservation_event(
                hub_id=hub_id,
                hub_name=hub_name,
                foodbank_id=foodbank_id,
                foodbank_name=foodbank_name,
                action="unreserve"
            )
            
            return {
                "message": "Unreserved successfully.",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

@hub_ns.route('/collectionComplete')
class CollectionComplete(Resource):
    @hub_ns.doc('collection_complete', description='Updates inventory on successful pickup by Food Bank')
    @hub_ns.expect(hub_foodbank_model)  # Remove this line if skipping models
    @hub_ns.response(200, 'Success')
    @hub_ns.response(400, 'Bad Request')
    @hub_ns.response(404, 'Not Found')
    @hub_ns.response(500, 'Internal Server Error')
    def post(self):
        """
        Service to mark a hub as collected by a foodbank.
        
        This endpoint handles the completion of the collection process when a foodbank
        has picked up all items from a hub. It:
        1. Marks the reservation as completed in the reservation table
        2. Deletes all inventory items for the hub
        3. Resets the hub's status (unreserved, zero weight, not ready to collect)
        
        This effectively resets the hub to be ready for new donations from volunteers.
        """
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
            foodbank_response = supabase.table('foodbank').select('*').eq('foodbankid', foodbank_id).execute()
            
            if not foodbank_response.data:
                return {"error": f"Foodbank with ID {foodbank_id} does not exist"}, 404
            
            # Check if this foodbank has a reservation for this hub
            reservation_response = supabase.table('foodbankreservation').select('*').eq(
                'foodbankid', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            if not reservation_response.data:
                return {"error": f"No active reservation found for Hub ID {hub_id} by Foodbank ID {foodbank_id}"}, 404
            
            # Begin transaction - unfortunately Supabase Python client doesn't support transactions directly
            # so we'll handle each operation separately
            
            # 1. Mark the reservation as completed
            supabase.table('foodbankreservation').update(
                {'collectioncompleted': True}
            ).eq('foodbankid', foodbank_id).eq('hubid', hub_id).eq('collectioncompleted', False).execute()
            
            # 2. Delete all inventory items for this hub
            supabase.table('inventory').delete().eq('hubid', hub_id).execute()
            
            # 3. Update hub's status
            supabase.table('hub').update({
                'reserved': False,
                'totalweight_kg': 0,
                'readytocollect': False
            }).eq('hubid', hub_id).execute()
            
            return {
                "message": "Collection successful",
                "hubID": str(hub_id)
            }, 200
        
        except Exception as e:
            return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)