from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from twilio.rest import Client
from invokes import invoke_http
import os


#Twilio Credentials
account_sid = "AC3e0e1ffa3a1cac1ae67dd057498adff4"
auth_token = "03a5396ae124dca507d31cdd993b0c00"    
twilio_number = "+12513254270"  

client = Client(account_sid, auth_token)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage to remember volunteer information
volunteer_info_storage = {}

class NotifyRequest(BaseModel):
    userList: List[str]

class UserNotification(BaseModel):
    userId: str
    userPhoneNumber: str
    message: str

@app.post("/notify/")
async def notify_users(request: dict):
    """Send SMS notifications to selected users"""
    results = []
    
    # Process the userList directly from the request
    for user in request.get("userList", []):
        try:
            # Extract phone number directly from the user object
            user_id = user.get("userId")
            user_name = user.get("userName")
            phone_number = user.get("userPhoneNumber")

            # Store volunteer information for future use
            volunteer_info_storage[user_id] = {
                "userName": user_name,
                "userPhoneNumber": phone_number
            }
            
            # Send SMS via Twilio
            message = client.messages.create(
                body=f"Hello {user_name}! A new food donation is available near you, check FoodBridge for more details",
                from_=twilio_number,
                to=phone_number
            )
            results.append({
                "userId": user_id,
                "status": "sent",
                "message_sid": message.sid
            })
        except Exception as e:
            results.append({
                "userId": user.get("userId", "unknown"),
                "status": "failed",
                "error": str(e)
            })
    
    return {"results": results}

@app.post("/notifyVolunteer/")
async def notify_volunteer(request: dict):
    """Send confirmation SMS to volunteers using stored information"""
    results = []
    
    # Get the list of user IDs from the request
    user_list = request.get("userList", [])
    
    for user_id in user_list:
        try:
            # Retrieve stored user information
            if user_id in volunteer_info_storage:
                user_info = volunteer_info_storage[user_id]
                user_name = user_info["userName"]
                phone_number = user_info["userPhoneNumber"]
                
                # Send SMS via Twilio
                message = client.messages.create(
                    body=f"Thank you {user_name}! Delivery is confirmed. Please check FoodBridge for pickup details.",
                    from_=twilio_number,
                    to=phone_number
                )
                results.append({
                    "userId": user_id,
                    "status": "sent",
                    "message_sid": message.sid
                })
            else:
                # User not found in storage
                results.append({
                    "userId": user_id,
                    "status": "failed",
                    "error": "User information not found. Please notify this user first."
                })
        except Exception as e:
            results.append({
                "userId": user_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {"results": results}

@app.post("/notifyFoodBank/")
async def notify_food_bank(request: dict):
    """Notify food bank personnel about routes after volunteer drop-off"""
    results = []
    
    # Get the list of food bank user IDs from the request
    food_bank_user_list = request.get("foodbankUserList", [])
    
    for user_id in food_bank_user_list:
        try:
            # Check if user info is in storage first
            if user_id in volunteer_info_storage:
                user_info = volunteer_info_storage[user_id]
                user_name = user_info["userName"]
                phone_number = user_info["userPhoneNumber"]
            else:
                # Fall back to Account Info Service
                user_info = invoke_http(
                    f"http://account-info-service:5000/users/{user_id}", 
                    method="GET"
                )
                user_name = user_info.get("userName", "Food Bank Personnel")
                phone_number = user_info["userPhoneNumber"]
                
            message = client.messages.create(
                body=f"Hello {user_name}, a volunteer has dropped off a food donation. A new route has been planned. Please check FoodBridge for collection details.",
                from_=twilio_number,
                to=phone_number
            )
            results.append({
                "userId": user_id,
                "status": "sent",
                "message_sid": message.sid
            })
        except Exception as e:
            results.append({
                "userId": user_id,
                "status": "failed",
                "error": str(e)
            })
    
    return {"results": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
