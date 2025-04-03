from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from twilio.rest import Client
from invokes import invoke_http
import os
import threading
import pika
import json


#Twilio Credentials
account_sid = "AC3e0e1ffa3a1cac1ae67dd057498adff4"
auth_token = "03a5396ae124dca507d31cdd993b0c00"    
twilio_number = "+12513254270"  

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notification_queue")


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
### Stopped here 2 April, continue with this to configure the correct phone number and flows

def send_volunteer_notification(message):
    try:
        volunteer_name = message.get("volunteerName")
        volunteer_mobile = message.get("volunteerMobile")
        
        # Send SMS via Twilio
        sms = client.messages.create(
            body=f"Thank you {volunteer_name}! Your delivery has been confirmed.",
            from_=twilio_number,
            to=volunteer_mobile
        )
        print(f"SMS sent to {volunteer_name} at {volunteer_mobile}, SID: {sms.sid}")
    except Exception as e:
        print(f"Error sending volunteer notification: {e}")

def process_hub_broadcast(message):
    try:
        hubs = message.get("hubs", [])
        timestamp = message.get("timestamp", "")
        
        print(f"Processing hub broadcast from {timestamp}")
        for hub in hubs:
            hub_name = hub.get("hubName", "Unknown Hub")
            hub_address = hub.get("hubAddress", "Unknown Address")
            total_weight = hub.get("totalWeight_kg", 0)
            
            print(f"Hub: {hub_name}, Address: {hub_address}, Total Weight: {total_weight}kg")
            
            # Here you would typically notify relevant users about hub status
            # This would require additional logic to determine who should be notified
    except Exception as e:
        print(f"Error processing hub broadcast: {e}")

def process_general_notification(message):
    try:
        print(f"Processing general notification: {message}")
        
        # Extract message details - adapt this based on your actual message structure
        recipient = message.get("recipient")
        message_text = message.get("message", "New notification from FoodBridge")
        phone_number = message.get("phoneNumber")
        
        if phone_number:
            # Send SMS via Twilio
            sms = client.messages.create(
                body=message_text,
                from_=twilio_number,
                to=phone_number
            )
            print(f"General notification SMS sent to {recipient} at {phone_number}, SID: {sms.sid}")
        else:
            print(f"No phone number provided for general notification to {recipient}")
    except Exception as e:
        print(f"Error processing general notification: {e}")
###

def process_message(ch, method, properties, body):
    try:
        message = json.loads(body)
        print(f"Received message: {message}")
        
        # Handle different message types
        if "volunteerName" in message and "volunteerMobile" in message:
            # Handle confirmDelivery messages
            send_volunteer_notification(message)
        elif "event" in message and message["event"] == "ready_hubs_broadcast":
            # Handle hub service broadcasts
            process_hub_broadcast(message)
        else:
            # Handle other notification types
            process_general_notification(message)
            
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f"Error processing message: {e}")
        # Negative acknowledgement to requeue the message
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

def start_rabbitmq_consumer():
    try:
        # Connect to RabbitMQ
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=RABBITMQ_HOST,
                port=RABBITMQ_PORT,
                credentials=credentials
            )
        )
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
        # Set prefetch count
        channel.basic_qos(prefetch_count=1)
        
        # Start consuming
        print(f"Starting to consume from queue: {RABBITMQ_QUEUE}")
        channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_message)
        
        # Start consuming (blocks)
        channel.start_consuming()
    except Exception as e:
        print(f"RabbitMQ consumer error: {e}")
        # Implement reconnection logic here


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

@app.on_event("startup")
async def startup_event():
    """Start the RabbitMQ consumer when the FastAPI app starts"""
    consumer_thread = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    consumer_thread.start()
    print("RabbitMQ consumer started in background thread")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
