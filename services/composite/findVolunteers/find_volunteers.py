import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import helper_functions
import traceback
import logging
from flasgger import Swagger

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])
Swagger(app)

@app.route('/findVolunteers', methods=["POST"])
def find_volunteers():
    """
    Find Volunteers Endpoint
    This endpoint processes product information, validates the image, adds 
    the product, retrieves volunteers, filters them based on proximity, updates 
    the product details, and sends the filtered list to a queue.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The product image.
      - name: productCCDetails
        in: formData
        type: string
        required: true
        description: A JSON string containing product CC details.
      - name: productAddress
        in: formData
        type: string
        required: true
        description: The product address.
      - name: productItemList
        in: formData
        type: string
        required: true
        description: A JSON string containing the product item list.
    responses:
      200:
        description: All steps completed successfully.
        schema:
          type: object
          properties:
            result:
              type: boolean
      400:
        description: Bad request due to missing or invalid input.
      510:
        description: Error occurred during product validation.
      520:
        description: Error occurred while adding the product.
      530:
        description: Error occurred during volunteer retrieval.
      540:
        description: Error occurred while filtering volunteers.
      550:
        description: Error occurred while updating product details.
      560:
        description: Error occurred while sending filtered volunteers to queue.
      500:
        description: Internal server error.
    """
    try:
        data = request.form
        product_image = request.files.get('image')
        product_cc_details = data.get("productCCDetails")
        product_address = data.get("productAddress")
        product_item_list = data.get("productItemList")
        
        if isinstance(product_cc_details, str):
            product_cc_details = json.loads(product_cc_details)
        if isinstance(product_item_list, str):
            product_item_list = json.loads(product_item_list)
        
        if not product_image:
            logger.error("No image provided")
            return jsonify({"error": "No image provided"}), 400
        if not product_cc_details:
            logger.error("Product CC Details is required")
            return jsonify({"error": "Product CC Details is required"}), 400
        if not product_address:
            logger.error("Product address is required")
            return jsonify({"error": "Product address is required"}), 400
        if not product_item_list:
            logger.error("Product item list is required")
            return jsonify({"error": "Product item list is required"}), 400

        # Step 1: Validate Product
        try:
            logger.info("Starting Step 1: Product Validation")
            validate_results = helper_functions.validate_image(product_image, product_item_list)["result"]
            if validate_results != True:
                logger.warning(f"Image validation rejected: {validate_results}")
                return jsonify({"message": validate_results}), 400
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Product Validation",
                "error": str(e),
                "traceback": tb
            }), 510

        # Step 2: Add Product
        try:
            logger.info("Starting Step 2: Adding Products")
            input_body = {
                "productPic": product_image,
                "productCCDetails": product_cc_details,
                "productAddress": product_address,
                "productItemList": product_item_list
            }
            product = helper_functions.add_product(input_body)
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Add Product",
                "error": str(e),
                "traceback": tb
            }), 520

        # Step 3: Retrieve Volunteers
        try:
            logger.info("Starting Step 3: Getting all volunteers")
            volunteer_list = helper_functions.get_all_volunteers()
            if not volunteer_list:
                logger.error("No volunteers available")
                return jsonify({"error": "No volunteers available"}), 404
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Retrieve Volunteers",
                "error": str(e),
                "traceback": tb
            }), 530

        # Step 4: Filter Nearby Volunteers
        try:
            logger.info("Starting Step 4: Getting volunteers in 2km radius")
            hub_address = product_cc_details["hubAddress"]
            product_id = product["product_id"]
            logger.info(f"Inserted Address: {hub_address} | Product ID: {product_id}")
            filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id, product_address, hub_address, volunteer_list)
            filtered_volunteers_list = filtered_volunteers_result["user_list"]
            if len(filtered_volunteers_list) == 0:
                logger.warning(f"No nearby volunteers found for product {product_id}")
                return jsonify({"error": "No nearby volunteers found for product"}), 432
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Filter Nearby Volunteers",
                "error": str(e),
                "traceback": tb
            }), 540

        # Step 5: Update Product Details with Volunteers
        try:
            logger.info("Starting Step 5: Updating product CC and userList")
            update_body = {
                "productId": product_id,
                "productUserList": filtered_volunteers_list
            }
            updated_product = helper_functions.update_product_details(update_body)
            logger.info(updated_product)
            if "error" in updated_product:
                return jsonify({"error": f"Failed to update product details: {updated_product['error']}"}), 500
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Update Product Details",
                "error": str(e),
                "traceback": tb
            }), 550

        # Step 6: Send Filtered Volunteers to Queue
        try:
            logger.info("Starting Step 6: Sending filtered list into queue")
            retrievedUserList = updated_product["productUserList"]
            helper_functions.sendToQueue(retrievedUserList)
        except Exception as e:
            tb = traceback.format_exc()
            return jsonify({
                "step": "Send to Queue",
                "error": str(e),
                "traceback": tb
            }), 560

        logger.info("All Steps completed successfully!")
        return jsonify({"result": True}), 200

    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Error in find_volunteers: {str(e)}\n{tb}")
        return jsonify({"error": str(e), "traceback": tb}), 500


if __name__ == '__main__':
    logger.info("Starting findVolunteers service on port 5001")
    helper_functions.connectAMQP()
    app.run(host='0.0.0.0', port=5001, debug=True)