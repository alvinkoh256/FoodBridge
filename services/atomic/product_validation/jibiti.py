import os
import base64
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


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Function that accepts picture as input
    # set a user_message

    # function to encode the image to base64

    # start the completion
        # model
        # response format
def call_openai(image, description):
    base64_image = encode_image(image)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages = [
            {
                "role":"user",
                "content":[
                    { "type": "text", "text": description },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url":f"data:image/jpeg;base64,{base64_image}"
                        },
                    },
                ]
            },
            {
                "role":"system",
                "content": [
                    {"type":"text", "text":system_content},
                    {"type":"text", "text":f"Follow the following schema: {reply_schema}"}
                    
                ]
            }
        ],
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

print(call_openai("sample_pics/banana.png","tuna"))