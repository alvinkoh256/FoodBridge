import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI 

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# schema
reply_schema = {
    "format":{
        "type":"json_object",
        "schema":{
            "type":"object",
            "properties":{
                "result":{
                    "description":"Result after the analysis",
                    "type":"boolean OR string"
                }
            }
        },
        "required": "result",
        "additionalProperties": False
    },
    "strict": True
}

system_content = open('system_message.txt', 'r').read()

# Cause OpenAI api only accept base64 string in utf-8 format
def encode_image(image):
    res = base64.b64encode(image.read()).decode("utf-8")
    return res


def call_openai(image, description):

    base64_image = encode_image(image)

    image_format = "jpeg"

    all_items = ",".join(description)
    print(all_items)

    try:
        response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {
                "role":"user",
                "content":[
                    { "type": "text", "text": f"Check that the image contains ALL of the following: {all_items}" },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":f"data:image/{image_format};base64,{base64_image}"
                        },
                    },
                ]
            },
            {
                "role":"system",
                "content": [
                    {"type":"text", "text":f"ONLY follow the rules here: {system_content}"},
                    {"type":"text", "text":f"Follow the following schema: {reply_schema}"}
                    
                ]
            }
        ],
        temperature = 0.1,
        response_format={"type": "json_object"}
    )
        
                # Validate the response
        
        if not response:
            raise Exception("Invalid or empty response from OpenAI")
        
        return response.choices[0].message.content
    
    except Exception as e:
        # Log the error
        print(f"Error in call_openai: {str(e)}")
        # Return a structured error that can be handled by the calling function
        return json.dumps({"error": f"Failed to process with OpenAI: {str(e)}"})