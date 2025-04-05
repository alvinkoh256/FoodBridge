import os
import amqp_lib
import sys
import json
import notification_service
import threading

# RabbitMQ Configuration shifted to Dockerfile.

def start_consumer(host, port, exchange, exchange_type, queue, callback):
    amqp_lib.start_consuming(
        host, port, exchange, 
        exchange_type, queue, 
        callback
    )

def callback(ch, method, properties, body):
    try:
        message = json.loads(body.decode())
        print("\n------------- RECEIVED MESSAGE -------------")
        print(f"Routing Key: {method.routing_key}")
        print(f"Message Content: {json.dumps(message, indent=2)}")
        print("--------------------------------------------\n")
        volunteer_name = message["volunteerName"]
        print(f"Volunteer name is: {volunteer_name}")
        notification_service.gen_message(message)
        volunteer_phone_number = message["volunteerMobile"]
        print(f"Volunteer Phone Number is {volunteer_phone_number}")
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    sys.stdout.flush()  # Force print to log



def callback_notify(ch, method, properties, body):
    try:
        message = json.loads(body.decode())
        print("\n------------- RECEIVED MESSAGE -------------")
        print(f"Message Content: {json.dumps(message, indent=2)}")
        print("--------------------------------------------\n")
        
        # Track phone numbers to avoid duplicates
        phone_number_list = []
        
        # Loop through each user in the userList
        for user in message["userList"]:
            user_id = user["userId"]
            user_name = user["userName"]
            user_phone = user["userPhoneNumber"]
            
            # Check if this phone number has already been processed
            if user_phone in phone_number_list:
                print(f"Duplicate phone number {user_phone} detected, skipping notification")
                continue
            
            phone_number_list.append(user_phone)
            print(f"Volunteer ID is: {user_id}")
            print(f"Volunteer name is: {user_name}")
            print(f"Volunteer Phone Number is {user_phone}")
            
            # Call notification service for each user
            notification_service.send_volunteer_notification({
                "volunteerName": user_name,
                "volunteerMobile": user_phone
            })
            
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    sys.stdout.flush()  # Force print to log


        
if __name__ == "__main__":
    # Create threads for each queue
    t1 = threading.Thread(target=start_consumer,
        args=(os.getenv("RABBITMQ_HOST", "localhost"), int(os.getenv("RABBITMQ_PORT", 5672)), 
            "notificationsS3", "topic", "dropoff", callback))
    t2 = threading.Thread(target=start_consumer,
        args=(os.getenv("RABBITMQ_HOST", "localhost"), int(os.getenv("RABBITMQ_PORT", 5672)), 
            "scenario2NotifyExchange", "fanout", "scenario2Notify", callback_notify))

    
    # Start all threads
    t1.start()
    t2.start()
    
    # Wait for all threads to complete
    t1.join()
    t2.join()