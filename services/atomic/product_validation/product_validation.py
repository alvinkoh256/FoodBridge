import json
from flask import Flask, request, jsonify
from jibiti import newcall_openai
from flasgger import Swagger


app = Flask(__name__)

# Initialize flasgger 
app.config['SWAGGER'] = {
    'title': 'Product validation microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'Validates product with image and description'
}
swagger = Swagger(app)



@app.route('/productValidation', methods=['POST'])
def generate_response():
    """
    Validate product with image and description
    ---
    tags:
      - Product Validation
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Image of the product to be validated
      - name: productDescription
        in: formData
        type: string
        required: true
        description: JSON array containing the list of product items to be validated
        example: '["canned beans", "rice", "pasta"]'
    responses:
      200:
        description: Successful validation - all items are non-perishable and present
        schema:
          type: object
          properties:
            result:
              type: boolean
              description: True if all products are non-perishable and present
              example: true
        examples:
          application/json:
            result: true
      400:
        description: Validation failed - items perishable, missing, or unclear image
        schema:
          type: object
          properties:
            result:
              type: string
              description: Error message explaining why validation failed
              example: "Some items shown are perishable. Please ensure all are non-perishable."
        examples:
          application/json:
            result: "The image doesn't contain all items specified. Missing: rice, pasta. Please ensure all items in the description are visible in the image."
      422:
        description: Request processing error - malformed request
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing product image file or product description"
        examples:
          application/json:
            error: "Missing product description"
      500:
        description: Server error during processing
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid response format from AI service"
        examples:
          application/json:
            error: "Failed to process with OpenAI: Rate limit exceeded"
    """
    
    try:
        data = request.form
        
        image = request.files.get('file')
        if not image:
            return jsonify({"error": "Missing product image file"}), 422
            
        description = data.get("productDescription")
        if not description:
            return jsonify({"error": "Missing product description"}), 422

        if isinstance(description, str):
            try:
                description = json.loads(description)
            except json.JSONDecodeError:
                return jsonify({"error": "Invalid JSON format for product description"}), 422

        result = newcall_openai(image, description)

        try:
            result_obj = json.loads(result)
            
            # Check if there's an error from OpenAI
            if "error" in result_obj:
                return jsonify({"error": result_obj["error"]}), 500
                
            # Check if result is not true (boolean) but a string message
            if isinstance(result_obj.get("result"), str):
                return jsonify({"result": result_obj["result"]}), 400
                
            return result_obj, 200
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return jsonify({"error": "Invalid response format from AI service"}), 500
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004,debug=True)