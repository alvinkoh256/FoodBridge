import os
import amqp_lib
import sys
import json
import notification_service
import threading

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "notification_queue")


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
    except Exception as e:
        print(f"Error processing message: {str(e)}")
    sys.stdout.flush()  # Force print to log



# if __name__ == "__main__":
        
#         # Start consuming data from dropoff
#         amqp_lib.start_consuming(
#             "localhost", 5672, "notificationsS3", 
#             "topic", "dropoff", 
#             callback
#         )
        
if __name__ == "__main__":
    # Create threads for each queue
    t1 = threading.Thread(target=start_consumer, 
                         args=("localhost", 5672, "notificationsS3", "topic", "dropoff", callback))
    
    t2 = threading.Thread(target=start_consumer, 
                         args=("localhost", 5672, "notificationsS3", "topic", "broadcastHubs", callback))
    
    t3 = threading.Thread(target=start_consumer, 
                         args=("localhost", 5672, "scenario2NotifyExchange", "fanout", "scenario2Notify", callback))
    
    # Start all threads
    t1.start()
    t2.start()
    t3.start()
    
    # Wait for all threads to complete
    t1.join()
    t2.join()
    t3.join()