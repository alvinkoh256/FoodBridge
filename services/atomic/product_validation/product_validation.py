import json
from flask import Flask, request, jsonify
from jibiti import call_openai
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
        description: Textual description of the product
    responses:
        200:
            description: Successful validation
            schema:
            type: object
            properties:
                isValid:
                type: boolean
                description: Whether the product is valid
                suggestions:
                type: array
                description: List of improvement suggestions if product is invalid
                items:
                    type: string
                confidence:
                type: number
                format: float
                description: Confidence score of the validation (0-1)
        400:
            description: Bad request - missing parameters
            schema:
            type: object
            properties:
                error:
                type: string
        500:
            description: Server error during processing
            schema:
            type: object
            properties:
                error:
                type: string
    """
    try:
        data = request.form
        
        image = request.files.get('file')
        description = data.get("productDescription")

        description = json.loads(description)

        result = call_openai(image, description)

        try:
            result_obj = json.loads(result)
            return result_obj
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return jsonify({"error": "Invalid response format from AI service"}), 500
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004,debug=True)

