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
import amqp_lib
import sys
from dotenv import load_dotenv


#Twilio Credentials
load_dotenv()
account_sid = os.getenv("TWILIO_ACCOUNT_ID")
auth_token = os.getenv("TWILIO_ACCOUNT_TOKEN")
twilio_number = os.getenv("TWILIO_NUMBER")  

client = Client(account_sid, auth_token)

# class NotifyRequest(BaseModel):
#     userList: List[str]

# class UserNotification(BaseModel):
#     userId: str
#     userPhoneNumber: str
#     message: str

# def send_volunteer_notification(message):
#     try:
#         volunteer_name = message.get("volunteerName")
#         volunteer_mobile = message.get("volunteerMobile")
        
#         # Send SMS via Twilio
#         sms = client.messages.create(
#             body=f"Thank you {volunteer_name}! Your delivery has been confirmed.",
#             from_=twilio_number,
#             to=volunteer_mobile
#         )
#         print(f"SMS sent to {volunteer_name} at {volunteer_mobile}, SID: {sms.sid}")
#     except Exception as e:
#         print(f"Error sending volunteer notification: {e}")

# def process_hub_broadcast(message):
#     try:
#         hubs = message.get("hubs", [])
#         timestamp = message.get("timestamp", "")
        
#         print(f"Processing hub broadcast from {timestamp}")
#         for hub in hubs:
#             hub_name = hub.get("hubName", "Unknown Hub")
#             hub_address = hub.get("hubAddress", "Unknown Address")
#             total_weight = hub.get("totalWeight_kg", 0)
            
#             print(f"Hub: {hub_name}, Address: {hub_address}, Total Weight: {total_weight}kg")
            
#             # Here you would typically notify relevant users about hub status
#             # This would require additional logic to determine who should be notified
#     except Exception as e:
#         print(f"Error processing hub broadcast: {e}")

# def process_general_notification(message):
#     try:
#         print(f"Processing general notification: {message}")
        
#         # Extract message details - adapt this based on your actual message structure
#         recipient = message.get("recipient")
#         message_text = message.get("message", "New notification from FoodBridge")
#         phone_number = message.get("phoneNumber")
        
#         if phone_number:
#             # Send SMS via Twilio
#             sms = client.messages.create(
#                 body=message_text,
#                 from_=twilio_number,
#                 to=phone_number
#             )
#             print(f"General notification SMS sent to {recipient} at {phone_number}, SID: {sms.sid}")
#         else:
#             print(f"No phone number provided for general notification to {recipient}")
#     except Exception as e:
#         print(f"Error processing general notification: {e}")
# ###

# def process_message(ch, method, properties, body):
#     try:
#         message = json.loads(body)
#         print(f"Received message: {message}")
        
#         # Handle different message types
#         if "volunteerName" in message and "volunteerMobile" in message:
#             # Handle confirmDelivery messages
#             send_volunteer_notification(message)
#         elif "event" in message and message["event"] == "ready_hubs_broadcast":
#             # Handle hub service broadcasts
#             process_hub_broadcast(message)
#         else:
#             # Handle other notification types
#             process_general_notification(message)
            
#         # Acknowledge the message
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#     except Exception as e:
#         print(f"Error processing message: {e}")
#         # Negative acknowledgement to requeue the message
#         ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# def start_rabbitmq_consumer():
#     try:
#         # Connect to RabbitMQ
#         credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(
#                 host=RABBITMQ_HOST,
#                 port=RABBITMQ_PORT,
#                 credentials=credentials
#             )
#         )
#         channel = connection.channel()
        
#         # Declare the queue
#         channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
        
#         # Set prefetch count
#         channel.basic_qos(prefetch_count=1)
        
#         # Start consuming
#         print(f"Starting to consume from queue: {RABBITMQ_QUEUE}")
#         channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=process_message)
        
#         # Start consuming (blocks)
#         channel.start_consuming()
#     except Exception as e:
#         print(f"RabbitMQ consumer error: {e}")
#         # Implement reconnection logic here

def gen_message(userObject):
    user_name = userObject.get("volunteerName")
    # unformatted_phone_number = userObject.get("volunteerMobile")
    # temp_format_phone_number = unformatted_phone_number.replace(" ", "")
    ### Currently hardcoded, will get Ferrell's inputs on mobile formatting.
    phone_number = "+6590603108"

    # Send SMS via Twilio
    message = client.messages.create(
        body=f"Hello {user_name}! Dropoff successful! Thank you for delivering.",
        from_=twilio_number,
        to=phone_number
    )
