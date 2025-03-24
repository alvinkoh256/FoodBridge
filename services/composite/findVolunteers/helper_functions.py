from invokes import invoke_http
import os
from pathlib import Path
import grpc
import locate_pb2
import locate_pb2_grpc

PRODUCT_VALIDATION_URL = "http://localhost:5004"
PRODUCT_LISTING_URL = "http://localhost:5005"
LOCATING_URL = "localhost:5006"
USER_URL = "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI"

# function to call validation service with picture and description as param
def validate_image(image, description):
    try:
        image_file = {'file':image}
        data = {'productDescription': description}

        response = invoke_http(
            f"{PRODUCT_VALIDATION_URL}/productValidation",
            method="POST",
            files=image_file,
            data=data
        )
        
        return response
        
    except Exception as e:
        print(f"Error in validate_image: {str(e)}")
        return {"error": f"Validation service error: {str(e)}"}


# function to call add product from product_listing service
def add_product(body):
    image = body["product_image"]
    description = body["product_description"]
    address = body["product_address"]

    try:
        image_file = {'productPic':image}
        data = {'productAddress':address,
                'productDescription': description
                }

        response = invoke_http(
            f"{PRODUCT_LISTING_URL}/product",
            method="POST",
            files=image_file,
            data=data
        )
        
        result = {
            "product_id":response["productId"],
            "product_address":response["productAddress"]
        }

        return result
        
    except Exception as e:
        print(f"Error in validate_image: {str(e)}")
        return {"error": f"Validation service error: {str(e)}"}


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


# function to run locating service with list of volunteer ids and address and id, address
def find_nearby_volunteers(product_id, product_address, volunteer_list):
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
            volunteerList=volunteer_infos
        )
        
        # Make the gRPC call
        response = stub.getFilteredUsers(request)
        
        # Process the response
        result = {
            "product_id": response.productId,
            "product_closest_cc": response.productClosestCC,
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
            f"{PRODUCT_LISTING_URL}/productCCAndUsers",
            method="PUT",
            json=input_body
        )
        return response
    
    except Exception as e:
        print(f"Error in updating product listing: {str(e)}")
        return {"error": f"Validation service error: {str(e)}"}
    

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
    image_path = "sample_pics/tuna.jpg"
    
    # Open the image file
    with open(image_path, 'rb') as img_file:
        # Create a simple dictionary with the required data
        product_data = {
            'product_image': img_file,
            'product_description': "Canned tuna for donation",
            'product_address': "123 Main St, Singapore 123456"
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
    """
    Test function for find_nearby_volunteers
    """
    # Example product details
    product_id = "1111-1111-1111"
    product_address = "B1-67 SMU School of Computing and Information Systems 1, Singapore 178902"
    
    # Example volunteer list
    volunteer_list = [
        {"userId":"1111-1111-1111","userAddress":"80 Stamford Rd, Singapore 178902"},
        {"userId":"2222-2222-2222","userAddress":"501 Margaret Dr, Singapore 149306"},
        {"userId":"3333-3333-3333","userAddress":"500 Dover Rd, Singapore 139651"}
    ]
    
    # Call the function
    result = find_nearby_volunteers(product_id, product_address, volunteer_list)
    
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


