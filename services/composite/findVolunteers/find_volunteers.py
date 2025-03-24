import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import helper_functions

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
    data = request.form
    image = request.files.get('image')
    description = data.get("productDescription")
    address = data.get("productAddress")

    validate_results = helper_functions.validate_image(image, description)

    if (validate_results["result"]!=True):
        return jsonify(validate_results["result"])
    
    input_body = {
        "product_image":image,
        "product_description":description,
        "product_address":address
    }
    product = helper_functions.add_product(input_body)

    # volunteer_list = helper_functions.get_all_volunteers()
    volunteer_list = [
        {"userId":"1111-1111-1111","userAddress":"20 Siglap Vw, Singapore 455789"},
        {"userId":"2222-2222-2222","userAddress":"30 Eunos Cres, Singapore 409423"},
        {"userId":"3333-3333-3333","userAddress":"81 Lor 25 Geylang, Singapore 388310"}
    ]

    # print(product)
    product_id = product["product_id"]
    filtered_volunteers_result = helper_functions.find_nearby_volunteers(product_id,address,volunteer_list)
    filtered_volunteers_list = filtered_volunteers_result["user_list"]

    print(filtered_volunteers_result)

    update_body = {
        "productId":product_id,
        "productClosestCC":filtered_volunteers_result["product_closest_cc"],
        "productUserList":filtered_volunteers_list
    }
    updated_product = helper_functions.update_product_details(update_body)

    return jsonify(updated_product)


    
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001,debug=True)