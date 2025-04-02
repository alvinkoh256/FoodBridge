import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI 
from invokes import invoke_http

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

reply_schema_edited = {
    "format": {
        "type": "json_schema",
        "name":"image_validation",
        "schema": {
            "type": "object",
            "properties":{
                "result":{
                    "description":"Result after the analysis",
                    "type":["boolean", "string"]
                }
            },
            "required": ["result"],
            "additionalProperties": False
        },
        "strict": True
    }
}

system_content = open('system_message.txt', 'r').read()

# Cause OpenAI api only accept base64 string in utf-8 format
def encode_image(image):
    res = base64.b64encode(image.read()).decode("utf-8")
    return res

def encode_image_path(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")




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
                    { "type": "text", "text": f"{all_items}" },
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


def newcall_openai(image, description):
    base64_image = encode_image(image)
    all_items = ",".join(description)
    print(all_items)
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {
                "role": "user",
                "content": [
                    { 
                        "type": "input_text", 
                        "text": f"{all_items}"
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{base64_image}",
                    },
                ],
            },
            {
                "role": "system",
                "content":[
                    {
                        "type":"input_text",
                        "text": system_content
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                    "type": "output_text",
                    "text": "Please ensure all are non-perishable and the picture contains all items stated"
                    }
                ]
            }
        ],
        text = reply_schema_edited,
        reasoning={},
        tools=[],
        temperature=0.3,
        max_output_tokens=2048,
        top_p=1,
        store=True
    )
    result = response.output[0].content[0].text
    # result = json.loads(result)
    return result

