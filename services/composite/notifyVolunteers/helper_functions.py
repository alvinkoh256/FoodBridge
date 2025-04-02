from invokes import invoke_http
import os
import amqp_lib
import logging
import json
import pika
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration - Use environment variables with sensible defaults
USER_URL = os.environ.get('ACCOUNT_SERVICE_URL', "https://personal-tdqpornm.outsystemscloud.com/FoodBridge/rest/AccountInfoAPI")
NOTIFY_URL = os.environ.get('NOTIFICATION_URL', "http://notification:5007")  # Use service name for Docker
RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')  # Default to service name for Docker
RABBIT_PORT = int(os.environ.get('RABBIT_PORT', 5672))
RABBIT_PUBLISHER_EXCHANGE = os.environ.get('SCENARIO2_RABBIT_EXCHANGE', 'scenario2NotifyExchange')
EXCHANGE_TYPE = os.environ.get('SCENARIO12_EXCHANGE_TYPE', 'fanout')

# Global variables for connection and channel
connection = None
channel = None

def connectAMQP(max_retries=5, retry_delay=5):
    """Connect to RabbitMQ with retry logic"""
    global connection
    global channel
    
    logger.info(f"Connecting to AMQP broker at {RABBIT_HOST}:{RABBIT_PORT}...")
    
    for attempt in range(max_retries):
        try:
            connection, channel = amqp_lib.connect(
                hostname=RABBIT_HOST,
                port=RABBIT_PORT,
                exchange_name=RABBIT_PUBLISHER_EXCHANGE,
                exchange_type=EXCHANGE_TYPE,
            )
            logger.info("Successfully connected to RabbitMQ")
            return True
        except Exception as e:
            logger.error(f"Attempt {attempt+1}/{max_retries} failed: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    logger.error(f"Failed to connect to RabbitMQ after {max_retries} attempts")
    return False

def get_user_info(user_id):
    try:
        url = f"{USER_URL}/userPhone/{user_id}"
        response = invoke_http(url, 'GET')
        return response
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        return {
            "userId": user_id,
            "userName": "Unknown",
            "userPhoneNumber": "",
            "error": str(e)
        }

def process_user_list(user_list):
    try:
        if not user_list:
            return {"userList": []}
        
        processed_users = []
        for user_id in user_list:
            user_details = get_user_info(user_id)
            if "error" not in user_details:
                processed_users.append({
                    "userId": user_id,
                    "userName": user_details["userName"],
                    "userPhoneNumber": user_details["userPhoneNumber"]
                })
        
        return {"userList": processed_users}
    except Exception as e:
        logger.error(f"Error processing user list: {str(e)}")
        return {"userList": [], "error": str(e)}

def sendToQueue(message):
    """Send message to RabbitMQ queue with connection handling"""
    global connection, channel
    
    # Ensure we have a connection
    if connection is None or channel is None or not amqp_lib.is_connection_open(connection):
        logger.info("No active connection. Attempting to connect...")
        if not connectAMQP():
            logger.error("Failed to connect to RabbitMQ. Cannot send message.")
            return False
    
    try:
        # Convert message to JSON string if it's not already a string
        if not isinstance(message, str):
            message = json.dumps(message)
            
        # Convert string to bytes for RabbitMQ
        if isinstance(message, str):
            message = message.encode('utf-8')
        
        # Send message with persistence
        properties = pika.BasicProperties(delivery_mode=2)  # Make message persistent
        channel.basic_publish(
            exchange=RABBIT_PUBLISHER_EXCHANGE,
            routing_key="",
            body=message,
            properties=properties
        )
        
        logger.info("Message successfully sent to queue")
        return True
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        # Try to reconnect once
        if connectAMQP(max_retries=1):
            try:
                channel.basic_publish(
                    exchange=RABBIT_PUBLISHER_EXCHANGE,
                    routing_key="",
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                logger.info("Message sent after reconnection")
                return True
            except Exception as e2:
                logger.error(f"Failed to send message after reconnection: {str(e2)}")
        return False