from invokes import invoke_http
from typing import List, Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class volunteerItems(BaseModel):
    userId:str
    userAddress:str

class inputBody(BaseModel):
    productId: str
    productAddress: str
    volunteerList: list[volunteerItems]


# function that convert product address to request
def convertAddress(product_address):
    return None

@app.get("/")
async def my_first_get_api():
    return {"message":"First FastAPI example"}

@app.post("/closest/")
async def find_closest_users(input:inputBody):
    # Retrieve product address from request
    # Function to convert product address to coords
    # Function to find the closest community center coords w/ prod coords
    # Function to find the center point with community center coords & product address coords as input
    # Function to find the closest users in a 4km radius w/ userList and midpoint

    volunteer_list = input.volunteerList
    for volunteer in volunteer_list:
        print(volunteer.userAddress)



    return -1

# python -m uvicorn main:app --reload --port 5001