from invokes import invoke_http
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import extra_functions

app = FastAPI(
    title="Locating Atomic Microservice",
    description="Service for finding center point and closest volunteers"
)

# CORS so front end can access
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class volunteerInfo(BaseModel):
    userId:str
    userAddress:str

class inputBody(BaseModel):
    productId: str
    productAddress: str
    volunteerList: list[volunteerInfo] = Field(...,description="List of volunteers with their information")

    class Config:
        json_schema_extra = {
            "example": {
                "productId": "prod_789012",
                "productAddress": "B1-67 SMU School of Computing and Information Systems 1, Singapore 178902",
                "volunteerList": [
                    {
                        "userId": "1111-1111-1111",
                        "userAddress": "80 Stamford Rd, Singapore 178902"
                    },
                    {
                        "userId": "2222-2222-2222",
                        "userAddress": "501 Margaret Dr, Singapore 149306"
                    },
                                        {
                        "userId": "3333-3333-3333",
                        "userAddress": "500 Dover Rd, Singapore 139651"
                    }
                ]
            }
        }

class responseBody(BaseModel):
    productId:str
    productClosestCC:str | None
    userList:list[str] = Field(...,description="List of filtered volunteers")
    error: str | None

    class Config:
        json_schema_extra = {
            "example": {
                "productId": "prod_789012",
                "productClosestCC": "Pek Kio Community Centre|21 Gloucester Rd, Singapore 219458",
                "userList": [
                    "1111-1111-1111"
                ]
            }
        }

@app.get("/")
async def my_first_get_api():
    return {"message":"First FastAPI example"}

@app.post("/closest/", response_model=responseBody)
async def find_closest_users(input:inputBody):
    res = None
    product_address = input.productAddress

    product_coord = extra_functions.convertAddress(product_address)
    if product_coord is None:
        return responseBody(
            productId=input.productId,
            productClosestCC=None,
            userList=[],
            error="Not a valid address!"
        )

    closest_cc = extra_functions.find_closest_cc(product_coord)
    if closest_cc is None:
        return responseBody(
            productId=input.productId,
            productClosestCC=None,
            userList=[],
            error="Can't find closest CC!"
        )


    center_point_coord = extra_functions.get_center_point(product_coord,closest_cc["coordinates"])

    volunteer_list = input.volunteerList
    filtered_closest_list = extra_functions.find_closest_users(center_point_coord,volunteer_list)

    res = responseBody(
        productId = input.productId,
        productClosestCC = f"{closest_cc['display_name']}|{closest_cc['address']}",
        userList = filtered_closest_list,
        error = None
    )

    return res

# taskkill /f /im python.exe in powershell to force kill it
# python -m uvicorn locating:app --reload --port 5003