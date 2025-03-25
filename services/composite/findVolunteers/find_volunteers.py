import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import helper_functions
import traceback

app = Flask(__name__)
CORS(app,origins=["*"])


# function to execute composite microservice
    # take the picture & product description out
    # run the validate_image function
    # check if the !result["check"]
        # return an error
    # make a body with product_image, product_description, product_address
    # send body into add_product function and store in product dict
    # run the get_all_volunteers function and store in volunteer_list
    # run the find_nearby_volunteers to get the response
    # run the update_product_address function with the response body

    # Send filtered_volunteer_list into kafka queue
@app.route('/findVolunteers', methods=["POST"])
def find_volunteers():
    # Take picture and description out
    data = request.form
    image = request.files.get('image')
    description = data.get("productDescription")
    address = data.get("productAddress")

    if not image:
        helper_functions.print_debug("Error: No image provided")
        return jsonify({"error": "No image provided"}), 400
    if not description:
        helper_functions.print_debug("Error: Product description is required")
        return jsonify({"error": "Product description is required"}), 400
    if not address:
        helper_functions.print_debug("Error: Product address is required")
        return jsonify({"error": "Product address is required"}), 400

    # Run validate image function
    try:
        helper_functions.print_debug("Starting Step 1: Product Validation")
        validate_results = helper_functions.validate_image(image, description)["result"]

        if (validate_results!=True):
            helper_functions.print_debug(f"Image validation rejected: {validate_results}")
            return jsonify({"message": validate_results}), 400
        
    except Exception as e:
        helper_functions.print_debug(f"Error during image validation: {str(e)}")
        return jsonify({"error": f"Image validation failed: {str(e)}"}), 500

    # Run adding of products
    input_body = {
        "product_image":image,
        "product_description":description,
        "product_address":address
    }
    try:
        helper_functions.print_debug("Starting Step 2: Adding Products")
        product = helper_functions.add_product(input_body)
    except Exception as e:
        helper_functions.print_debug(f"Error adding product: {str(e)}")
        return jsonify({"error": f"Failed to add product: {str(e)}"}), 500


    # Run retrieving volunteers
    # HARDCODED FOR NOW
    try:
        helper_functions.print_debug("Starting Step 3: Getting all volunteers")
        # volunteer_list = helper_functions.get_all_volunteers()
        volunteer_list = [
            {"userId":"1111-1111-1111","userAddress":"20 Siglap Vw, Singapore 455789"},
            {"userId":"2222-2222-2222","userAddress":"30 Eunos Cres, Singapore 409423"},
            {"userId":"3333-3333-3333","userAddress":"81 Lor 25 Geylang, Singapore 388310"}
        ]
        if not volunteer_list:
            helper_functions.print_debug("Error: No volunteers available")
            return jsonify({"error": "No volunteers available"}), 404

    except Exception as e:
        helper_functions.print_debug(f"Error retrieving volunteers: {str(e)}")
        return jsonify({"error": f"Failed to retrieve volunteers: {str(e)}"}), 500


    # Run find volunteers in radius
    try:
        helper_functions.print_debug("Starting Step 4: Getting volunteers in 2km radius")
        product_id = product["product_id"]
        filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id,address,volunteer_list)
        filtered_volunteers_list = filtered_volunteers_result["user_list"]

        if len(filtered_volunteers_list)==0:
            helper_functions.print_debug(f"Warning: No nearby volunteers found for product {product_id}")
    except Exception as e:
        helper_functions.print_debug(f"Error finding nearby volunteers: {str(e)}")
        return jsonify({"error": f"Failed to find nearby volunteers: {str(e)}"}), 500

    # Run update product listing CC and userList
    try:
        helper_functions.print_debug("Starting Step 5: Updating producc CC and userList")
        update_body = {
            "productId":product_id,
            "productClosestCC":filtered_volunteers_result["product_closest_cc"],
            "productUserList":filtered_volunteers_list
        }
        updated_product = helper_functions.update_product_details(update_body)

    except Exception as e:
        helper_functions.print_debug(f"Error updating product details: {str(e)}")
        return jsonify({"error": f"Failed to update product details: {str(e)}"}), 500

    helper_functions.print_debug("All Steps done!")
    return jsonify(updated_product)


    
@app.route('/testGRPC',methods=['POST'])
def test_grpc():
    volunteer_list = [
        {"userId":"1111-1111-1111","userAddress":"20 Siglap Vw, Singapore 455789"},
        {"userId":"2222-2222-2222","userAddress":"30 Eunos Cres, Singapore 409423"},
        {"userId":"3333-3333-3333","userAddress":"81 Lor 25 Geylang, Singapore 388310"}
    ]
    product_id = "be04b877-cbdc-4a48-a408-9818702686e1"
    address = "11 Maria Ave, Singapore 456743"
    try:
        filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id,address,volunteer_list)
        if "user_list" not in filtered_volunteers_result:
            return jsonify({ "yuup":filtered_volunteers_result}), 500
            raise KeyError("'user_list' key not found in the gRPC response")

        filtered_volunteers_list = filtered_volunteers_result["user_list"]
        return jsonify(filtered_volunteers_list)
    except Exception as error:
        err_trace = traceback.format_exc()
        return jsonify({"error": str(error), "trace": err_trace}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)