from invokes import invoke_http
import os
from pathlib import Path
import grpc
import locate_pb2
import locate_pb2_grpc
from datetime import datetime
import json
import time
import pika 
import amqp_lib
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PRODUCT_VALIDATION_URL = os.environ.get('PRODUCT_VALIDATION_URL', "http://localhost:5004")
PRODUCT_LISTING_URL = os.environ.get('PRODUCT_LISTING_URL', "http://localhost:5005") 
LOCATING_URL = os.environ.get('LOCATING_SERVICE_URL', "localhost:5006")
USER_URL = os.environ.get('ACCOUNT_SERVICE_URL', "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")
HUB_URL = os.environ.get('HUB_SERVICE_URL', "http://localhost:5010")


RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_EXCHANGE = os.environ.get('SCENARIO12_RABBIT_EXCHANGE', 'scenario12Exchange')
EXCHANGE_TYPE = os.environ.get('SCENARIO12_EXCHANGE_TYPE', 'fanout')

def connectAMQP():
    # Use global variables to reduce number of reconnection to RabbitMQ
    # There are better ways but this suffices for our lab
    global connection
    global channel

    print("  Connecting to AMQP broker...")
    try:
        connection, channel = amqp_lib.connect(
                hostname=RABBIT_HOST,
                port=RABBIT_PORT,
                exchange_name=RABBIT_EXCHANGE,
                exchange_type=EXCHANGE_TYPE,
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")
        exit(1)


def sendToQueue(message):
    if connection is None or not amqp_lib.is_connection_open(connection):
        connectAMQP()
    
    # Convert non-string data types (like lists) to JSON strings
    if not isinstance(message, str):
        message = json.dumps(message)
        logger.info(f"Converted message to JSON string: {message}")
    
    # Ensure message is bytes for RabbitMQ
    if isinstance(message, str):
        message = message.encode('utf-8')
    
    channel.basic_publish(exchange=RABBIT_EXCHANGE, routing_key="", body=message, properties=pika.BasicProperties(delivery_mode=2))
    logger.info("Message sent to queue successfully")


# function to call validation service with picture and description as param
def validate_image(image, item_object):
    item_list = [item["itemName"] for item in item_object]
    try:
        image_file = {'file':image}
        
        # Convert the list to a JSON string
        json_str = json.dumps(item_list)
        data = {'productDescription': json_str}

        logger.info(f"Image file: {image_file}")
        logger.info(f"Data being sent: {data}")

        response = invoke_http(
            f"{PRODUCT_VALIDATION_URL}/productValidation",
            method="POST",
            files=image_file,
            data=data
        )
        
        # Log the raw response for debugging
        logger.info(f"Raw validation response: {response}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in validate_image: {str(e)}")
        return {"error": f"Validation service error: {str(e)}", "result": False}


# function to call add product from product_listing service
def add_product(body):
    image = body["productPic"]
    
    # Create a copy of the body data for modification
    body_copy = body.copy()
    
    # Reset the stream pointer to the beginning
    image.stream.seek(0)
    image_file = {'productPic': (image.filename, image.stream, image.mimetype)}
    
    # Remove the image from the body
    del body_copy["productPic"]
    
    # Convert the complex objects to JSON strings
    body_copy["productCCDetails"] = json.dumps(body_copy["productCCDetails"])
    body_copy["productItemList"] = json.dumps(body_copy["productItemList"])
    
    logger.info(f"Sending productCCDetails: {body_copy['productCCDetails']}")
    logger.info(f"Sending productItemList: {body_copy['productItemList']}")
    
    response = invoke_http(
        f"{PRODUCT_LISTING_URL}/product",
        method="POST",
        files=image_file,
        data=body_copy  # Use the modified copy with JSON strings
    )
    
    result = {
        "product_id": response["productId"],
        "product_address": response["productAddress"]
    }
    
    return result
        

# function to retrieve all volunteers id and address with user service
def get_all_volunteers():
    try:
        response = invoke_http(
            f"{USER_URL}/userAddress", 
            method="GET"
        )
        
        return response["volunteerList"]
        
    except Exception as e:
        print(f"Error in get_all_volunteers: {str(e)}")
        return {
            "status": "error", 
            "message": f"User service error: {str(e)}"
        }


def get_all_hubs():
    response = invoke_http(
        url=f"{HUB_URL}/internal/hubs/allHubs",
        method= "GET"
    )
    return response


# function to run locating service with list of volunteer ids and address and id, address
def find_nearby_volunteers(product_id, product_address,product_hub_address, volunteer_list):
    try:
        # Create a gRPC channel
        channel = grpc.insecure_channel(LOCATING_URL)
        
        # Create a stub (client)
        stub = locate_pb2_grpc.locateStub(channel)
        
        # Create volunteer info objects from the list
        volunteer_infos = []
        for volunteer in volunteer_list:
            volunteer_info = locate_pb2.volunteerInfo(
                userId=volunteer['userId'],
                userAddress=volunteer['userAddress']
            )
            volunteer_infos.append(volunteer_info)
        
        # Create the request message
        request = locate_pb2.inputBody(
            productId=product_id,
            productAddress=product_address,
            productHubAddress=product_hub_address,
            volunteerList=volunteer_infos
        )
        
        # Make the gRPC call
        response = stub.getFilteredUsers(request)
        
        # Process the response
        result = {
            "product_id": response.productId,
            "user_list": list(response.userList),  # Convert from repeated field to list
        }
        
        # Check if there's an error
        if response.error:
            result["error"] = response.error
            
        return result
        
    except grpc.RpcError as rpc_error:
        # Handle gRPC specific errors
        status_code = rpc_error.code()
        details = rpc_error.details()
        print(f"gRPC error: {status_code}, {details}")
        return {"error": f"Locating service error: {details}"}
        
    except Exception as e:
        # Handle other errors
        print(f"Error in find_nearby_volunteers: {str(e)}")
        return {"error": f"General error: {str(e)}"}


def update_product_details(input_body):
    try:
        response = invoke_http(
            f"{PRODUCT_LISTING_URL}/product",
            method="PUT",
            json=input_body
        )
        return response
    
    except Exception as e:
        print(f"Error in updating product listing: {str(e)}")
        return {"error": f"Validation service error: {str(e)}"}
    

# TEST FUNCTIONS

def test_validate_image():
    # Path to your test image
    image_path = "sample_pics/tuna.jpg"  # Update this with your actual path
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return
        
    # Description for testing
    description = "This is a can of tuna"
    
    # Open the image file
    with open(image_path, 'rb') as image_file:
        # Call the validation function
        result = validate_image(image_file, description)
        
    # Print the result
    print("Validation result:")
    print(result)

def test_add_product():
    # Path to your test image
    image_path = "D:/SMU/GitRepos/FoodBridge/services/sample_pics/tuna.jpg"
    
    # Open the image file
    with open(image_path, 'rb') as img_file:
        # Create a simple dictionary with the required data
        product_data = {
            'productPic': img_file,
            'productItemList': [{"itemName":"tuna","quantity":10},{"itemName":"beans","quantity":10},{"itemName":"pickled vegetables","quantity":10}],
            'productAddress': "123 Main St, Singapore 123456",
            'productCCDetails':{ "hubId": 1, "hubName": "Bedok Orchard RC", "hubAddress": "10C Bedok South Ave 2 #01-562, S462010"}
        }
        
        # Call the add_product function
        result = add_product(product_data)
    
    # Print the result
    print("Add product result:")
    print(result)

def test_get_all_volunteers():
    # Call the function
    result = get_all_volunteers()
    
    # Print the result
    print("All volunteers information:")
    print(result)

def test_find_nearby_volunteers():
    # Example product details
    product_id = "1111-1111-1111"
    product_address = "750A Chai Chee Rd, #01-01 ESR BizPark @Chai Chee, Singapore 469001"
    productHubAddress = "10C Bedok South Ave 2 #01-562, S462010"

    # Example volunteer list
    volunteer_list = [
        {"userId":"1111-1111-1111","userAddress":"39 Siglap Hl, Singapore 456092"},
        {"userId":"2222-2222-2222","userAddress":"31 Jurong West Street 41, Singapore 649412"},
        {"userId":"3333-3333-3333","userAddress":"73 Jln Tua Kong, Singapore 457264"}
    ]
    
    # Call the function
    result = find_nearby_volunteers(product_id, product_address,productHubAddress, volunteer_list)
    
    # Print the result
    print("Nearby volunteers result:")
    print(result)

def test_update_product_details():
    # Create a mock result from find_nearby_volunteers
    mock_result = {
        "productId": "62a62f2e-d6ec-438d-acc6-90204c5ec7c6",
        "productClosestCC": "ABC Community Centre",
        "productUserList": ["1111-1111-1111","2222-2222-2222", "3333-3333-3333"]
    } 
    
    # Call the update_product_details function
    response = update_product_details(mock_result)
    
    # Print the result
    print("Update product details result:")
    print(response["productId"])

def test_function():
    return {
        "message":"yuup"
    }