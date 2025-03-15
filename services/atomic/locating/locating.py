from invokes import invoke_http
from typing import List, Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import extra_functions

app = FastAPI()

# CORS so front end can access
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class inputBody(BaseModel):
    productId: str
    productAddress: str
    volunteerList: list[dict]


@app.get("/")
async def my_first_get_api():
    return {"message":"First FastAPI example"}

@app.post("/closest/")
async def find_closest_users(input:inputBody):
    res = None
    product_address = input.productAddress
    product_coord = extra_functions.convertAddress(product_address)
    closest_cc = extra_functions.find_closest_cc(product_coord)
    center_point_coord = extra_functions.get_center_point(product_coord,closest_cc["coordinates"])

    volunteer_list = input.volunteerList
    filtered_closest_list = extra_functions.find_closest_users(center_point_coord,volunteer_list)

    res = {
        "productId": input.productId,
        "productClosestCC": closest_cc["display_name"],
        "userList": filtered_closest_list
    }

    return res

# python -m uvicorn locating:app --reload --port 5001