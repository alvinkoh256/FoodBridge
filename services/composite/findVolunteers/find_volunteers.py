import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import helper_functions
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/findVolunteers', methods=["POST"])
def find_volunteers():
    # Take picture and description out
    try:
        data = request.form
        product_image = request.files.get('image')
        product_cc_details = data.get("productCCDetails")
        product_address = data.get("productAddress")
        product_item_list = data.get("productItemList")

        if isinstance(product_cc_details,str):
            product_cc_details = json.loads(product_cc_details)

        if isinstance(product_item_list,str):
            product_item_list = json.loads(product_item_list)
            

        if not product_image:
            logger.error("Error: No image provided")
            return jsonify({"error": "No image provided"}), 400
        if not product_cc_details:
            logger.error("Error: Product CC Details is required")
            return jsonify({"error": "Product CC Details is required"}), 400
        if not product_address:
            logger.error("Error: Product address is required")
            return jsonify({"error": "Product address is required"}), 400
        if not product_item_list:
            logger.error("Error: Product item list is required")
            return jsonify({"error": "Product item list is required"}), 400

        # Run validate image function
        logger.info("Starting Step 1: Product Validation")
        validate_results = helper_functions.validate_image(product_image, product_item_list)["result"]

        if (validate_results!=True):
            logger.warning(f"Image validation rejected: {validate_results}")
            return jsonify({"message": validate_results}), 400
        
        # Run adding of products
        input_body = {
            "productPic":product_image,
            "productCCDetails":product_cc_details,
            "productAddress":product_address,
            "productItemList":product_item_list
        }




        logger.info("Starting Step 2: Adding Products")
        product = helper_functions.add_product(input_body)




        # Run retrieving volunteers
        # HARDCODED FOR NOW
        logger.info("Starting Step 3: Getting all volunteers")
        volunteer_list = helper_functions.get_all_volunteers()
        # volunteer_list = [
        #     {"userId":"1111-1111-1111","userAddress":"39 Siglap Hl, Singapore 456092"},
        #     {"userId":"2222-2222-2222","userAddress":"31 Jurong West Street 41, Singapore 649412"},
        #     {"userId":"3333-3333-3333","userAddress":"73 Jln Tua Kong, Singapore 457264"}
        # ]
        if not volunteer_list:
            logger.error("Error: No volunteers available")
            return jsonify({"error": "No volunteers available"}), 404




        # Run find volunteers in radius
        logger.info("Starting Step 4: Getting volunteers in 2km radius")

        logger.info(f"{type(product_cc_details)}")
        logger.info(f"{type(product)}")

        hub_address = product_cc_details["hubAddress"]
        product_id = product["product_id"]
        
        logger.info(f"Inserted Address: {hub_address} || Inserted Product ID: {product_id}")

        filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id, product_address, hub_address, volunteer_list)
        filtered_volunteers_list = filtered_volunteers_result["user_list"]

        if len(filtered_volunteers_list)==0:
            logger.warning(f"Warning: No nearby volunteers found for product {product_id}")
            return jsonify({"error": "No nearby volunteers found for product"}), 432
            
    

        # Run update product listing CC and userList
        logger.info("Starting Step 5: Updating product CC and userList")
        update_body = {
            "productId":product_id,
            "productUserList":filtered_volunteers_list
        }
        updated_product = helper_functions.update_product_details(update_body)
        logger.info(updated_product)
        if "error" in updated_product:
            return jsonify({"error": f"Failed to update product details: {updated_product['error']}"}), 500

        # retrieve userList
        # send to queue
        logger.info("Starting Step 6: Sending filtered list into queue")
        retrievedUserList = updated_product["productUserList"]
        helper_functions.sendToQueue(retrievedUserList)

        logger.info("All Steps completed successfully!")

        return jsonify({"result":True}), 200
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        logger.error(f"Error in find_volunteers: {str(e)}\n{error_traceback}")
        return jsonify({"error": str(e), "traceback": error_traceback}), 500

@app.route('/testAMQP', methods=["POST"])
def yuup():
    helper_functions.sendToQueue("yuup")
    return "yuup",200

if __name__ == '__main__':
    logger.info("Starting findVolunteers service on port 5001")
    helper_functions.connectAMQP()
    app.run(host='0.0.0.0', port=5001, debug=True)