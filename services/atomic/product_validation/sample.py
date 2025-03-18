@app.route('/openai', methods=["POST"])
def generate_response():

    # Initialize Schema
    schema = {
        "name": "get_illness",
        "description": "Retrieves information on various illnesses categorized by their commonality.",
        "parameters": {
            "type": "object",
            "required": [
                "common_illnesses",
                "less_common_illnesses",
                "rare_illnesses"
            ],
            "properties": {
            "common_illnesses": {
                "type": "array",
                "items": {
                "type": "object",
                "required": [
                    "body_part",
                    "description",
                    "brief_description"
                ],
                "properties": {
                    "body_part": {
                    "type": "string",
                    "description": "The part of the body affected by the illness, choose from 5 types: legs, head, abdomen, tail or others."
                    },
                    "description": {
                    "type": "string",
                    "description": "Description of the illness affecting the specified body part."
                    },
                    "brief_description":{
                    "type": "string",
                    "description": "Brief description of the illness affecting the specified body part. Should not be more than 3 words"
                    },
                    "chance_of_occurance":{
                    "type":"float",
                    "decription":"The percentage chance of this being the pet's illness. All illnesses in the categories listed (common_illnesses, less_common_illnesses, and rare_illnesses) must collectively sum to 100."
                    }
                },
                },
                "description": "List of common illnesses, including body part affected and description of the illness."
            },
            "less_common_illnesses": {
                "type": "array",
                "items": {
                "type": "object",
                "required": [
                    "body_part",
                    "description",
                    "brief_description"
                ],
                "properties": {
                    "body_part": {
                    "type": "string",
                    "description": "The part of the body affected by the illness."
                    },
                    "description": {
                    "type": "string",
                    "description": "Description of the less common illness."
                    },
                    "brief_description":{
                    "type": "string",
                    "description": "Brief description of the illness affecting the specified body part. Should not be more than 3 words"
                    },
                    "chance_of_occurance":{
                    "type":"float",
                    "decription":"The percentage chance of this being the pet's illness. All illnesses in the categories listed (common_illnesses, less_common_illnesses, and rare_illnesses) must collectively sum to 100."
                    }
                },
                },
                "description": "List of less common illnesses with details of the affected body part and a description of the illness."
            },
            "rare_illnesses": {
                "type": "array",
                "items": {
                "type": "object",
                "required": [
                    "body_part",
                    "description",
                    "brief_description"
                ],
                "properties": {
                    "body_part": {
                    "type": "string",
                    "description": "The body part affected by the illness."
                    },
                    "description": {
                    "type": "string",
                    "description": "Description of the rare illness"
                    },
                    "brief_description":{
                    "type": "string",
                    "description": "Brief description of the illness affecting the specified body part. Should not be more than 3 words"
                    },
                    "chance_of_occurance":{
                    "type":"float",
                    "decription":"The percentage chance of this being the pet's illness. All illnesses in the categories listed (common_illnesses, less_common_illnesses, and rare_illnesses) must collectively sum to 100."
                    }
                },
                },
                "description": "List of rare illnesses, specifying the affected body part and a description."
            },
            },
        }
    }

    # Get data from post
    data = request.json
    
    animal = data.get("animal")
    gender = data.get("gender")
    age = data.get("age")

    raw_preExisting = data.get("preExistingConditions")
    raw_symptoms = data.get("symptomList")

    # print(f"animal: {animal}")
    # print(f"gender: {gender}")
    # print(f"age: {age}")
    # print(f"raw_preExisting: {raw_preExisting}")
    # print(f"raw_symptoms: {raw_symptoms}")


    processed_symptoms = "; AND ".join(f"{symptom['symptom']}: {symptom['description']}"for symptom in raw_symptoms)

    if len(raw_preExisting)>0:
        processed_preExisitng = ", ".join(raw_preExisting)
    else:
        processed_preExisitng = "none"

    user_message = f"I have a {age} year old {gender} {animal} that has the following pre-existing conditions: {processed_preExisitng}. Recently it has been suffering the following symptoms: {processed_symptoms}. What are the possible illnesses it has?"

    # print(user_message)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format = {"type": "json_object"},
        messages=[
            {"role":"system","content":"You are a medical assistant that provides information on illnesses based on user symptoms and pre-existing conditions. You will categorize illnesses into common, less common, and rare categories, ensuring that each category contains at most 3 unique illnesses, in your explanation of the illness, be sure to explain what the illness is. Use the provided schema format for your response, and ensure to include the word 'json' in your response. DO NOT deviate your response schema"},

            {"role":"assistant", "content":f"Given Schema: {json.dumps(schema)}"},

            {"role":"assistant", "content":f"Ensure the total probability across all categories equals 100%.Ensure that rule is followed"},

            {"role":"user","content":user_message}
        ],
        temperature = 0.1,
    )
    data = completion.choices[0].message.content
    return jsonResponse(200, response=json.loads(data))