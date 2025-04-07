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
    the product, retrieves volunteers and hubs, filters volunteers based on proximity,
    updates the product details with the closest hub, and sends the filtered list to a queue.
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: The product image file.
      - name: productAddress
        in: formData
        type: string
        required: true
        description: The physical address where the product is located.
        example: "750A Chai Chee Rd, #01-01 ESR BizPark @Chai Chee, Singapore 469001"
      - name: productItemList
        in: formData
        type: string
        required: true
        description: A JSON string containing the list of food items with quantities.
        example: '[{"itemName":"tuna","quantity":10},{"itemName":"luncheon meat","quantity":5},{"itemName":"instant noodle","quantity":5}]'
      - name: productUserId
        in: formData
        type: string
        required: true
        description: The unique identifier of the user who created the product.
        example: "1111-1111-1111"
    responses:
      200:
        description: All steps completed successfully.
        schema:
          type: object
          properties:
            result:
              type: boolean
              example: true
      400:
        description: Bad request due to missing or invalid input.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Product address is required"
      404:
        description: No volunteers or hubs available.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No volunteers available"
      432:
        description: No nearby volunteers found for product.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No nearby volunteers found for product"
      433:
        description: No closest hub identified.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "No closest hub identified"
      510:
        description: Error occurred during product validation.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Product Validation"
            error:
              type: string
            traceback:
              type: string
      520:
        description: Error occurred while adding the product.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Add Product"
            error:
              type: string
            traceback:
              type: string
      530:
        description: Error occurred during volunteer retrieval.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Retrieve Volunteers"
            error:
              type: string
            traceback:
              type: string
      535:
        description: Error occurred during hub retrieval.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Retrieve Hubs"
            error:
              type: string
            traceback:
              type: string
      540:
        description: Error occurred while filtering volunteers.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Filter Nearby Volunteers"
            error:
              type: string
            traceback:
              type: string
      550:
        description: Error occurred while updating product details.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Update Product Details"
            error:
              type: string
            traceback:
              type: string
      560:
        description: Error occurred while sending filtered volunteers to queue.
        schema:
          type: object
          properties:
            step:
              type: string
              example: "Send to Queue"
            error:
              type: string
            traceback:
              type: string
      500:
        description: Internal server error.
        schema:
          type: object
          properties:
            error:
              type: string
            traceback:
              type: string
    """
    try:
        data = request.form
        product_image = request.files.get('image')
        product_address = data.get("productAddress")
        product_item_list = data.get("productItemList")
        product_user_id = data.get("productUserId")
        

        if isinstance(product_item_list, str):
            product_item_list = json.loads(product_item_list)
        
        if not product_image:
            logger.error("No image provided")
            return jsonify({"error": "No image provided"}), 400
        if not product_address:
            logger.error("Product address is required")
            return jsonify({"error": "Product address is required"}), 400
        if not product_item_list:
            logger.error("Product item list is required")
            return jsonify({"error": "Product item list is required"}), 400
        if not product_user_id:
            logger.error("Product user id is required")
            return jsonify({"error": "Product user id is required"}), 400

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
                "productAddress": product_address,
                "productItemList": product_item_list,
                "productUserId": product_user_id
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

        # Step 4: Retrieve list of hubs
        logger.info("Starting Step 4: Getting all hubs")
        hub_list = helper_functions.get_all_hubs()

        # Step 5: Filter Nearby Volunteers
        try:
            logger.info("Starting Step 5: Getting volunteers in 2km radius")
            hub_address = "yuup"
            product_id = product["product_id"]
            logger.info(f"Inserted Address: {hub_address} | Product ID: {product_id}")
            filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id, product_address, hub_address, volunteer_list,hub_list)
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

        # Step 6: Update Product Details with Volunteers
        try:
            logger.info("Starting Step 6: Updating product CC and userList")
            update_body = {
                "productId": product_id,
                "productUserList": filtered_volunteers_list,
                "productCCDetails": filtered_volunteers_result["closest_hub"]
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

        # Step 7: Send Filtered Volunteers to Queue
        try:
            logger.info("Starting Step 7: Sending filtered list into queue")
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